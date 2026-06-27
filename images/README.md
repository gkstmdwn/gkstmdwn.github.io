# Blog image publisher

`publish_images.py` converts local images referenced by a Markdown post to WebP,
uploads only new images to Cloudflare R2 through the existing Wrangler login, and
replaces the local image paths with the public Worker URL.

## Local layout

Place source images under `images/source/`. This directory is ignored by Git.

```text
images/
  source/
    model-memory.png
```

Reference the local file from a post using standard Markdown or an HTML `img` tag.

```markdown
![모델 크기와 GPU 메모리](../images/source/model-memory.png)
```

Every local image needs unique, meaningful alt text. The generated WebP filename is
the alt text with characters invalid on Windows replaced by `-`.

## Install

Use Python 3.11 or newer.

```powershell
python -m pip install -r images/requirements.txt
```

Wrangler must already be authenticated in the Worker project.

```powershell
cd E:\Projects\gkstmdwn-image-worker
npx wrangler login
```

## Run

Validate without changing anything:

```powershell
python images/publish_images.py `
  "_posts/2026-06-26-EfficientML 1강.md" `
  --prefix "efficientml/lec01" `
  --dry-run
```

Convert, upload, verify, and update the Markdown file:

```powershell
python images/publish_images.py `
  "_posts/2026-06-26-EfficientML 1강.md" `
  --prefix "efficientml/lec01"
```

Already uploaded images are recorded in `manifest.json` and reused on later runs.
External HTTP images are reported and left unchanged. If an image changes, use new
alt text because the published Worker response is cached as immutable.

The deployed image base URL configured for this project is:

```text
https://gkstmdwn-image-worker.gkstmdwn-blog-images.workers.dev
```
