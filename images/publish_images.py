from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
    import tomli as tomllib  # type: ignore[no-redef]

from PIL import Image, ImageOps


MARKDOWN_IMAGE_RE = re.compile(
    r"!\[(?P<alt>(?:\\.|[^\]])*)\]\((?P<body>[^\n]*?)\)",
    re.MULTILINE,
)
HTML_IMAGE_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE | re.DOTALL)
HTML_ALT_RE = re.compile(
    r"\balt\s*=\s*(?P<quote>['\"])(?P<value>.*?)\1",
    re.IGNORECASE | re.DOTALL,
)
HTML_SRC_RE = re.compile(
    r"\bsrc\s*=\s*(?P<quote>['\"])(?P<value>.*?)\1",
    re.IGNORECASE | re.DOTALL,
)
TRAILING_TITLE_RE = re.compile(
    r"^(?P<target>.*?)(?P<title>\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))\s*$",
    re.DOTALL,
)
FENCE_RE = re.compile(r"^[ \t]{0,3}(?P<fence>`{3,}|~{3,})")
INVALID_FILENAME_RE = re.compile(r"[<>:\"/\\|?*\x00-\x1f]")
SUPPORTED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".tif",
    ".tiff",
    ".webp",
}


class PublishError(RuntimeError):
    pass


@dataclass(frozen=True)
class Settings:
    script_dir: Path
    repo_root: Path
    base_url: str
    bucket: str
    worker_project_dir: Path
    default_prefix: str
    source_dir: Path
    generated_dir: Path
    manifest_file: Path
    max_width: int
    webp_quality: int
    cache_control: str


@dataclass(frozen=True)
class ImageReference:
    kind: str
    alt: str
    source: str
    target_start: int
    target_end: int


@dataclass(frozen=True)
class PlannedImage:
    reference: ImageReference
    source_path: Path
    source_relative: str
    source_sha256: str
    filename: str
    object_key: str
    public_url: str
    generated_path: Path
    already_uploaded: bool


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Convert local images referenced by a Markdown post to WebP, upload "
            "them to Cloudflare R2 through Wrangler, and replace the links."
        )
    )
    parser.add_argument("post", type=Path, help="Markdown post to process")
    parser.add_argument(
        "--prefix",
        help="R2 path below the Worker URL, for example efficientml/lec01",
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="TOML config path (defaults to images/config.toml)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and print actions without converting, uploading, or editing",
    )
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="Do not verify uploaded URLs with an HTTP HEAD request",
    )
    return parser.parse_args(argv)


def load_settings(config_path: Path | None = None) -> Settings:
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    path = (config_path or script_dir / "config.toml").resolve()

    if not path.is_file():
        raise PublishError(f"Config file not found: {path}")

    with path.open("rb") as config_file:
        raw = tomllib.load(config_file)

    def required_string(name: str) -> str:
        value = raw.get(name)
        if not isinstance(value, str) or not value.strip():
            raise PublishError(f"config.toml requires a non-empty '{name}'")
        return value.strip()

    def relative_to_script(name: str) -> Path:
        value = Path(required_string(name))
        return (script_dir / value).resolve() if not value.is_absolute() else value.resolve()

    max_width = int(raw.get("max_width", 1400))
    quality = int(raw.get("webp_quality", 82))
    if max_width <= 0:
        raise PublishError("max_width must be greater than zero")
    if quality < 1 or quality > 100:
        raise PublishError("webp_quality must be between 1 and 100")

    return Settings(
        script_dir=script_dir,
        repo_root=repo_root,
        base_url=required_string("base_url").rstrip("/"),
        bucket=required_string("bucket"),
        worker_project_dir=relative_to_script("worker_project_dir"),
        default_prefix=required_string("default_prefix"),
        source_dir=relative_to_script("source_dir"),
        generated_dir=relative_to_script("generated_dir"),
        manifest_file=relative_to_script("manifest_file"),
        max_width=max_width,
        webp_quality=quality,
        cache_control=str(
            raw.get("cache_control", "public, max-age=31536000, immutable")
        ),
    )


def normalize_prefix(value: str) -> str:
    prefix = value.strip().replace("\\", "/").strip("/")
    parts = prefix.split("/") if prefix else []
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise PublishError(f"Invalid R2 prefix: {value!r}")
    return "/".join(parts)


def fenced_code_spans(text: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    offset = 0
    open_start: int | None = None
    open_character = ""
    open_length = 0

    for line in text.splitlines(keepends=True):
        match = FENCE_RE.match(line)
        if match:
            fence = match.group("fence")
            if open_start is None:
                open_start = offset
                open_character = fence[0]
                open_length = len(fence)
            elif fence[0] == open_character and len(fence) >= open_length:
                spans.append((open_start, offset + len(line)))
                open_start = None
                open_character = ""
                open_length = 0
        offset += len(line)

    if open_start is not None:
        spans.append((open_start, len(text)))
    return spans


def is_protected(position: int, spans: Iterable[tuple[int, int]]) -> bool:
    return any(start <= position < end for start, end in spans)


def markdown_unescape(value: str) -> str:
    return re.sub(r"\\([\\`*{}\[\]()#+\-.!_>])", r"\1", value)


def split_markdown_destination(body: str) -> tuple[str, int, int] | None:
    leading = len(body) - len(body.lstrip())
    stripped = body.lstrip()
    if not stripped:
        return None

    if stripped.startswith("<"):
        closing = stripped.find(">")
        if closing == -1:
            return None
        return stripped[1:closing], leading + 1, leading + closing

    title_match = TRAILING_TITLE_RE.match(stripped)
    target_text = title_match.group("target") if title_match else stripped
    target_text = target_text.rstrip()
    if not target_text:
        return None
    return target_text, leading, leading + len(target_text)


def find_image_references(text: str) -> list[ImageReference]:
    protected = fenced_code_spans(text)
    references: list[ImageReference] = []

    for match in MARKDOWN_IMAGE_RE.finditer(text):
        if is_protected(match.start(), protected):
            continue
        destination = split_markdown_destination(match.group("body"))
        if destination is None:
            continue
        source, relative_start, relative_end = destination
        body_start = match.start("body")
        references.append(
            ImageReference(
                kind="markdown",
                alt=html.unescape(markdown_unescape(match.group("alt"))).strip(),
                source=html.unescape(source).strip(),
                target_start=body_start + relative_start,
                target_end=body_start + relative_end,
            )
        )

    for match in HTML_IMAGE_RE.finditer(text):
        if is_protected(match.start(), protected):
            continue
        tag = match.group(0)
        src_match = HTML_SRC_RE.search(tag)
        if src_match is None:
            continue
        alt_match = HTML_ALT_RE.search(tag)
        references.append(
            ImageReference(
                kind="html",
                alt=html.unescape(alt_match.group("value")).strip()
                if alt_match
                else "",
                source=html.unescape(src_match.group("value")).strip(),
                target_start=match.start() + src_match.start("value"),
                target_end=match.start() + src_match.end("value"),
            )
        )

    return sorted(references, key=lambda item: item.target_start)


def filename_from_alt(alt: str) -> str:
    normalized = unicodedata.normalize("NFC", alt).strip()
    if not normalized:
        raise PublishError("Every local image must have non-empty alt text")

    suffix = Path(normalized).suffix.lower()
    if suffix in SUPPORTED_EXTENSIONS:
        normalized = normalized[: -len(suffix)].rstrip()

    safe = INVALID_FILENAME_RE.sub("-", normalized)
    safe = re.sub(r"\s+", " ", safe).strip(" .")
    if not safe:
        raise PublishError(f"Alt text does not produce a valid filename: {alt!r}")
    if len(safe) > 150:
        raise PublishError(
            f"Alt text is too long for an image filename ({len(safe)} characters)"
        )
    return f"{safe}.webp"


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def resolve_local_source(
    source: str,
    post_path: Path,
    settings: Settings,
) -> Path | None:
    parsed = urllib.parse.urlsplit(source)
    if parsed.scheme.lower() in {"http", "https", "data"} or source.startswith("//"):
        return None
    if parsed.scheme and parsed.scheme.lower() != "file":
        return None

    decoded_path = urllib.parse.unquote(parsed.path)
    if parsed.scheme.lower() == "file":
        if os.name == "nt" and re.match(r"^/[A-Za-z]:/", decoded_path):
            decoded_path = decoded_path[1:]
        candidates = [Path(decoded_path)]
    else:
        normalized = decoded_path.replace("/", os.sep)
        local = Path(normalized)
        if local.is_absolute():
            candidates = [settings.repo_root / normalized.lstrip("/\\")]
        else:
            candidates = [post_path.parent / local, settings.source_dir / local]
            if len(local.parts) == 1:
                candidates.insert(0, settings.source_dir / local.name)

    existing = next((candidate.resolve() for candidate in candidates if candidate.is_file()), None)
    if existing is None:
        attempted = ", ".join(str(candidate.resolve()) for candidate in candidates)
        raise PublishError(f"Local image not found for {source!r}; tried: {attempted}")
    if not is_within(existing, settings.source_dir):
        raise PublishError(
            f"Local image must be inside {settings.source_dir}, got: {existing}"
        )
    if existing.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise PublishError(f"Unsupported image format: {existing.suffix} ({existing})")
    return existing


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source_file:
        for chunk in iter(lambda: source_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def encode_public_url(base_url: str, object_key: str) -> str:
    return f"{base_url}/{urllib.parse.quote(object_key, safe='/-._~')}"


def load_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": 1, "items": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as error:
        raise PublishError(f"Unable to read manifest {path}: {error}") from error
    if data.get("version") != 1 or not isinstance(data.get("items"), dict):
        raise PublishError(f"Unsupported manifest format: {path}")
    return data


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as temporary_file:
            temporary_file.write(content)
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def save_manifest(path: Path, manifest: dict[str, Any]) -> None:
    serialized = json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    atomic_write_text(path, serialized)


def inspect_image(path: Path) -> tuple[int, int]:
    with Image.open(path) as image:
        if getattr(image, "n_frames", 1) > 1:
            raise PublishError(f"Animated images are not supported: {path}")
        image = ImageOps.exif_transpose(image)
        width, height = image.size
        if width <= 0 or height <= 0:
            raise PublishError(f"Invalid image dimensions: {path}")
        return width, height


def convert_to_webp(
    source: Path,
    destination: Path,
    max_width: int,
    quality: int,
) -> tuple[int, int, int]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        if getattr(image, "n_frames", 1) > 1:
            raise PublishError(f"Animated images are not supported: {source}")
        image = ImageOps.exif_transpose(image)
        if image.width > max_width:
            target_height = max(1, round(image.height * max_width / image.width))
            image = image.resize(
                (max_width, target_height), Image.Resampling.LANCZOS
            )

        has_alpha = "A" in image.getbands() or "transparency" in image.info
        image = image.convert("RGBA" if has_alpha else "RGB")
        image.save(destination, "WEBP", quality=quality, method=6)
        width, height = image.size
    return width, height, destination.stat().st_size


def find_npx() -> str:
    executable = shutil.which("npx.cmd") or shutil.which("npx")
    if executable is None:
        raise PublishError("npx was not found in PATH")
    return executable


def upload_with_wrangler(
    image: PlannedImage,
    settings: Settings,
) -> str:
    if not settings.worker_project_dir.is_dir():
        raise PublishError(
            f"Worker project directory not found: {settings.worker_project_dir}"
        )
    command = [
        find_npx(),
        "wrangler",
        "r2",
        "object",
        "put",
        f"{settings.bucket}/{image.object_key}",
        "--file",
        str(image.generated_path),
        "--content-type",
        "image/webp",
        "--cache-control",
        settings.cache_control,
        "--remote",
        "--force",
    ]
    completed = subprocess.run(
        command,
        cwd=settings.worker_project_dir,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()
        raise PublishError(f"Wrangler upload failed for {image.object_key}: {detail}")
    return (completed.stdout or completed.stderr).strip()


def verify_public_url(url: str) -> None:
    request = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            if response.status != 200:
                raise PublishError(f"URL verification returned {response.status}: {url}")
            content_type = response.headers.get_content_type()
            if content_type != "image/webp":
                raise PublishError(
                    f"URL verification returned {content_type}, expected image/webp: {url}"
                )
    except (urllib.error.URLError, TimeoutError) as error:
        raise PublishError(f"Unable to verify uploaded image {url}: {error}") from error


def make_plan(
    references: list[ImageReference],
    post_path: Path,
    prefix: str,
    settings: Settings,
    manifest: dict[str, Any],
) -> tuple[list[PlannedImage], list[ImageReference]]:
    planned: list[PlannedImage] = []
    skipped_external: list[ImageReference] = []
    key_to_source: dict[str, Path] = {}
    manifest_items: dict[str, Any] = manifest["items"]

    for reference in references:
        if reference.source.startswith(f"{settings.base_url}/"):
            continue
        source_path = resolve_local_source(reference.source, post_path, settings)
        if source_path is None:
            skipped_external.append(reference)
            continue

        filename = filename_from_alt(reference.alt)
        object_key = f"{prefix}/{filename}"
        previous_source = key_to_source.get(object_key)
        if previous_source is not None and previous_source != source_path:
            raise PublishError(
                f"Duplicate alt text maps different files to {object_key!r}: "
                f"{previous_source} and {source_path}"
            )
        key_to_source[object_key] = source_path

        digest = sha256_file(source_path)
        existing = manifest_items.get(object_key)
        if existing and existing.get("sha256") != digest:
            raise PublishError(
                f"{object_key!r} already exists with different content. "
                "Use a new alt text because Worker responses are cached as immutable."
            )

        source_relative = source_path.relative_to(settings.source_dir).as_posix()
        public_url = encode_public_url(settings.base_url, object_key)
        planned.append(
            PlannedImage(
                reference=reference,
                source_path=source_path,
                source_relative=source_relative,
                source_sha256=digest,
                filename=filename,
                object_key=object_key,
                public_url=public_url,
                generated_path=settings.generated_dir / prefix / filename,
                already_uploaded=bool(existing),
            )
        )
    return planned, skipped_external


def replace_targets(text: str, replacements: list[tuple[int, int, str]]) -> str:
    updated = text
    for start, end, value in sorted(replacements, reverse=True):
        updated = f"{updated[:start]}{value}{updated[end:]}"
    return updated


def process_post(
    post_path: Path,
    prefix: str,
    settings: Settings,
    *,
    dry_run: bool,
    verify: bool,
) -> int:
    post_path = post_path.resolve()
    if not post_path.is_file():
        raise PublishError(f"Post not found: {post_path}")
    if not dry_run:
        settings.source_dir.mkdir(parents=True, exist_ok=True)

    original = post_path.read_text(encoding="utf-8")
    references = find_image_references(original)
    manifest = load_manifest(settings.manifest_file)
    planned, external = make_plan(
        references, post_path, prefix, settings, manifest
    )

    print(f"Post: {post_path}")
    print(f"Prefix: {prefix}")
    print(f"Images found: {len(references)}")
    print(f"Local images: {len(planned)}")
    print(f"External images skipped: {len(external)}")
    for reference in external:
        print(f"  SKIP external: {reference.source}")

    if not planned:
        print("No local images to process.")
        return 0

    for image in planned:
        width, height = inspect_image(image.source_path)
        action = "SKIP uploaded" if image.already_uploaded else "UPLOAD"
        print(
            f"  {action}: {image.source_relative} ({width}x{height}) "
            f"-> {image.object_key}"
        )

    if dry_run:
        print("Dry run complete; no files or remote objects were changed.")
        return 0

    replacements: list[tuple[int, int, str]] = []
    manifest_items: dict[str, Any] = manifest["items"]
    processed_keys: set[str] = set()
    uploaded_keys: set[str] = set()
    reused_keys: set[str] = set()

    for image in planned:
        replacements.append(
            (
                image.reference.target_start,
                image.reference.target_end,
                image.public_url,
            )
        )
        if image.object_key in processed_keys:
            continue
        processed_keys.add(image.object_key)

        if image.already_uploaded:
            reused_keys.add(image.object_key)
            continue

        width, height, output_size = convert_to_webp(
            image.source_path,
            image.generated_path,
            settings.max_width,
            settings.webp_quality,
        )
        print(
            f"  Converted: {image.generated_path} "
            f"({width}x{height}, {output_size / 1024:.1f} KiB)"
        )
        upload_output = upload_with_wrangler(image, settings)
        if upload_output:
            print(f"  Wrangler: {upload_output.splitlines()[-1]}")
        if verify:
            verify_public_url(image.public_url)
            print(f"  Verified: {image.public_url}")

        manifest_items[image.object_key] = {
            "source": image.source_relative,
            "sha256": image.source_sha256,
            "url": image.public_url,
            "width": width,
            "height": height,
            "size_bytes": output_size,
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
        }
        save_manifest(settings.manifest_file, manifest)
        uploaded_keys.add(image.object_key)

    updated = replace_targets(original, replacements)
    if updated != original:
        atomic_write_text(post_path, updated)
        print(f"Updated Markdown: {post_path}")
    else:
        print("Markdown already contains the expected Worker URLs.")
    print(
        f"Complete: {len(uploaded_keys)} uploaded, {len(reused_keys)} reused."
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        settings = load_settings(args.config)
        prefix = normalize_prefix(args.prefix or settings.default_prefix)
        return process_post(
            args.post,
            prefix,
            settings,
            dry_run=args.dry_run,
            verify=not args.no_verify,
        )
    except PublishError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Cancelled.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
