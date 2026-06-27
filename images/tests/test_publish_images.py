from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from PIL import Image


MODULE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MODULE_DIR))
import publish_images  # noqa: E402


class FindImageReferencesTests(unittest.TestCase):
    def test_finds_markdown_and_html_but_skips_fenced_code(self) -> None:
        text = """![그림 1](../images/source/a.png)

```markdown
![예제](../images/source/ignored.png)
```

<img src="../images/source/b.jpg" alt="그림 2">
"""
        references = publish_images.find_image_references(text)
        self.assertEqual([item.alt for item in references], ["그림 1", "그림 2"])
        self.assertEqual(
            [item.source for item in references],
            ["../images/source/a.png", "../images/source/b.jpg"],
        )

    def test_supports_markdown_title_and_angle_brackets(self) -> None:
        text = '![슬라이드](<../images/source/my slide.png> "설명")'
        reference = publish_images.find_image_references(text)[0]
        self.assertEqual(reference.alt, "슬라이드")
        self.assertEqual(reference.source, "../images/source/my slide.png")


class FilenameTests(unittest.TestCase):
    def test_uses_alt_text_and_replaces_invalid_characters(self) -> None:
        self.assertEqual(
            publish_images.filename_from_alt('GPU: "메모리" 비교.png'),
            "GPU- -메모리- 비교.webp",
        )

    def test_rejects_empty_alt_text(self) -> None:
        with self.assertRaises(publish_images.PublishError):
            publish_images.filename_from_alt("")


class ConversionTests(unittest.TestCase):
    def test_converts_and_resizes_to_webp(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "source.png"
            destination = root / "result.webp"
            Image.new("RGB", (2000, 1000), "red").save(source)

            width, height, size = publish_images.convert_to_webp(
                source, destination, max_width=1400, quality=82
            )

            self.assertEqual((width, height), (1400, 700))
            self.assertGreater(size, 0)
            with Image.open(destination) as converted:
                self.assertEqual(converted.format, "WEBP")
                self.assertEqual(converted.size, (1400, 700))


class ReplacementTests(unittest.TestCase):
    def test_replaces_targets_from_right_to_left(self) -> None:
        text = "![a](one.png) and ![b](two.png)"
        references = publish_images.find_image_references(text)
        replacements = [
            (references[0].target_start, references[0].target_end, "https://x/a.webp"),
            (references[1].target_start, references[1].target_end, "https://x/b.webp"),
        ]
        self.assertEqual(
            publish_images.replace_targets(text, replacements),
            "![a](https://x/a.webp) and ![b](https://x/b.webp)",
        )


class PipelineTests(unittest.TestCase):
    def test_processes_once_then_skips_worker_url(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            script_dir = root / "images"
            source_dir = script_dir / "source"
            generated_dir = script_dir / ".generated"
            worker_dir = root / "worker"
            post_dir = root / "_posts"
            source_dir.mkdir(parents=True)
            worker_dir.mkdir()
            post_dir.mkdir()

            source = source_dir / "original.png"
            post = post_dir / "post.md"
            manifest_file = script_dir / "manifest.json"
            Image.new("RGB", (1600, 800), "blue").save(source)
            post.write_text(
                "![파이프라인 테스트](../images/source/original.png)\n",
                encoding="utf-8",
            )

            settings = publish_images.Settings(
                script_dir=script_dir,
                repo_root=root,
                base_url="https://images.example.workers.dev",
                bucket="test-bucket",
                worker_project_dir=worker_dir,
                default_prefix="blog",
                source_dir=source_dir,
                generated_dir=generated_dir,
                manifest_file=manifest_file,
                max_width=1400,
                webp_quality=82,
                cache_control="public, max-age=31536000, immutable",
            )

            with (
                mock.patch.object(
                    publish_images, "upload_with_wrangler", return_value="uploaded"
                ) as upload,
                mock.patch.object(publish_images, "verify_public_url") as verify,
            ):
                result = publish_images.process_post(
                    post,
                    "course/lesson-01",
                    settings,
                    dry_run=False,
                    verify=True,
                )
                second_result = publish_images.process_post(
                    post,
                    "course/lesson-01",
                    settings,
                    dry_run=False,
                    verify=True,
                )

            self.assertEqual((result, second_result), (0, 0))
            upload.assert_called_once()
            verify.assert_called_once()
            self.assertIn(
                "https://images.example.workers.dev/course/lesson-01/"
                "%ED%8C%8C%EC%9D%B4%ED%94%84%EB%9D%BC%EC%9D%B8%20"
                "%ED%85%8C%EC%8A%A4%ED%8A%B8.webp",
                post.read_text(encoding="utf-8"),
            )
            self.assertTrue(
                (generated_dir / "course/lesson-01/파이프라인 테스트.webp").is_file()
            )
            manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
            self.assertIn(
                "course/lesson-01/파이프라인 테스트.webp", manifest["items"]
            )


if __name__ == "__main__":
    unittest.main()
