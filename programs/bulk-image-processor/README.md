# Bulk Image Processor

Resize, convert, watermark and optimise whole folders of images in one pass —
in parallel, never touching the originals, with a CSV manifest of exactly what
was written.

This is the "here are 4,000 photos, I need them web-sized, watermarked, renamed
and under 300 KB each" job — one of the most repeated freelance automation
requests, and the one clients most often have to redo because a script
overwrote their originals or silently died on one corrupt file. This one writes
to a separate output tree and reports failures per file instead of aborting.

**Requires Pillow:** `pip install -r requirements.txt`

---

## Quick start

```bash
cd programs/bulk-image-processor

# what am I even dealing with?
python3 imagebatch.py inspect ~/client-photos

# see the plan without writing anything
python3 imagebatch.py process ~/client-photos --out ./web --preset web --dry-run

# do it
python3 imagebatch.py process ~/client-photos --out ./web --preset web --manifest report.csv
```

## Common jobs

```bash
# web-ready: longest side 1600px, WebP, metadata stripped
python3 imagebatch.py process input --out web --max 1600 --format webp --quality 82

# responsive set: three widths per source image
python3 imagebatch.py process input --out dist --sizes 320,800,1600 --format webp

# watermark a proof gallery
python3 imagebatch.py process input --out proofs \
  --max 1200 --watermark-text "© Northline Studio 2026" \
  --watermark-position bottom-right --watermark-opacity 0.4

# logo watermark, centred, 30% of the image width
python3 imagebatch.py process input --out proofs \
  --watermark-image logo.png --watermark-position center --watermark-scale 0.3

# square social crops, renamed sequentially
python3 imagebatch.py process input --out social \
  --preset social-square --name "{parent}-{index}.{ext}" --flatten-tree
```

## Presets

| Preset | Equivalent flags |
|---|---|
| `web` | `--max 1600 --format webp --quality 82` |
| `thumbs` | `--sizes 320 --format jpeg --quality 80 --mode cover` |
| `email` | `--max 1024 --format jpeg --quality 78` |
| `social-square` | `--width 1080 --height 1080 --mode cover --format jpeg --quality 88` |
| `archive` | `--format png --keep-metadata` |

Any explicit flag overrides the preset, so `--preset web --max 800` is 800px WebP.

## Behaviour worth knowing

- **Originals are never written to.** `--out` is required and always a separate
  tree; the input folder structure is mirrored unless you pass `--flatten-tree`.
- **EXIF is stripped by default** (location data included) and orientation is
  baked in first, so photos don't come out rotated. `--keep-metadata` preserves
  EXIF and the ICC profile.
- **No upscaling** unless you ask for `--upscale`; a 400px source stays 400px
  under `--max 1600` instead of being blown up into mush.
- **Transparency → JPEG** is flattened onto `--background` (white by default)
  rather than turning black.
- **One bad file doesn't kill the batch.** Unreadable images are recorded as
  `error` rows in the manifest and the run continues.
- **`--skip-existing`** makes a re-run cheap after adding new source files.

**Sizing modes:** `fit` (default, whole image inside the box), `cover` (fill the
box, centre-crop the overflow), `exact` (stretch — rarely what you want).

**Name template fields:** `{stem} {name} {ext} {suffix} {width} {height} {index} {parent}`.
`{suffix}` is `-800w` style when `--sizes` is used and empty otherwise.

## Tests

```bash
python3 -m unittest discover -s tests -v   # 29 tests, images generated on the fly
```

---

## For the next agent

**Layout**
```
imagebatch.py       Plan/Record dataclasses, ops, CLI, parallel runner
requirements.txt    Pillow
tests/              29 unittest cases; fixtures are generated, none committed
```

**How it fits together**
- `Plan` is the single source of truth for a run — every operation reads it and
  nothing else. New options go on `Plan` plus a flag in `build_parser()`.
- `process_one()` handles exactly one source file and returns `Record` rows; it
  swallows exceptions on purpose so a batch of thousands can't be killed by one
  corrupt JPEG. Keep that guarantee.
- `run_batch()` uses threads, which is right here because Pillow releases the
  GIL during encode/decode. Switch to processes only if you add heavy pure-Python
  pixel work.
- Order inside `process_one()` is deliberate: exif-transpose → resize →
  watermark → flatten → sharpen → save. Watermarking after resize keeps the mark
  the same relative size at every output width.

**Good next steps**
- `--target-kb N`: binary-search quality per image to hit a size budget (clients
  ask for this constantly for e-commerce and email).
- A `--config job.json` file so a repeat client's settings live in version
  control instead of shell history.
- Smart cropping for `cover` mode — entropy or face detection instead of the
  centre.
- A contact-sheet / proof-grid output mode.
- `--watch` to process files as they land in a dropbox folder.
- Note it also works well on this repo's own texture folders — `--max 1024
  --format webp` over `materials/` produces preview-sized copies without
  touching the source PBR maps.
