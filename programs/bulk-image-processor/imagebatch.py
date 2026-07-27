#!/usr/bin/env python3
"""Bulk image processor: resize, convert, watermark and optimise whole folders.

Built for the job that keeps coming back - "here are 4,000 photos, I need them
web-sized, watermarked, renamed and under 300 KB each". Runs in parallel, never
overwrites the originals, and writes a CSV manifest of exactly what it did.

Requires Pillow (`pip install -r requirements.txt`).
Run `python3 imagebatch.py --help` for usage.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import fnmatch
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

try:
    from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps
except ImportError:  # pragma: no cover - dependency check
    sys.exit("Pillow is required:  pip install -r requirements.txt")

IMAGE_SUFFIXES = {
    ".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff",
    ".gif", ".ppm", ".jfif", ".avif",
}
FORMAT_ALIASES = {"jpg": "JPEG", "jpeg": "JPEG", "png": "PNG", "webp": "WEBP",
                  "tiff": "TIFF", "tif": "TIFF", "avif": "AVIF", "bmp": "BMP"}
EXTENSIONS = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp", "TIFF": ".tif",
              "AVIF": ".avif", "BMP": ".bmp", "GIF": ".gif"}
POSITIONS = ("top-left", "top-right", "bottom-left", "bottom-right", "center",
             "top-center", "bottom-center")

PRESETS: dict[str, dict[str, Any]] = {
    # name: flags applied before the user's own flags
    "web": {"max": 1600, "format": "webp", "quality": 82},
    "thumbs": {"sizes": "320", "format": "jpeg", "quality": 80, "mode": "cover"},
    "email": {"max": 1024, "format": "jpeg", "quality": 78},
    "social-square": {"width": 1080, "height": 1080, "mode": "cover", "format": "jpeg", "quality": 88},
    "archive": {"format": "png", "keep_metadata": True},
}


# --------------------------------------------------------------------------
# plan
# --------------------------------------------------------------------------

@dataclass
class Plan:
    out_dir: Path
    fmt: str | None = None                 # target Pillow format, None = keep
    quality: int = 85
    mode: str = "fit"                      # fit | cover | exact
    width: int | None = None
    height: int | None = None
    max_side: int | None = None
    sizes: list[int] = field(default_factory=list)  # widths for responsive sets
    upscale: bool = False
    sharpen: bool = False
    keep_metadata: bool = False
    background: str = "#ffffff"            # used when flattening alpha to JPEG
    name_template: str = "{stem}{suffix}.{ext}"
    flatten_tree: bool = False
    skip_existing: bool = False
    watermark_text: str = ""
    watermark_image: Path | None = None
    watermark_position: str = "bottom-right"
    watermark_opacity: float = 0.45
    watermark_scale: float = 0.18          # fraction of the target image width
    watermark_margin: float = 0.025
    dry_run: bool = False


@dataclass
class Record:
    source: Path
    output: Path | None
    status: str                # ok | skipped | error
    source_bytes: int = 0
    output_bytes: int = 0
    source_size: str = ""
    output_size: str = ""
    note: str = ""

    @property
    def saved_pct(self) -> float:
        if self.status != "ok" or not self.source_bytes or not self.output_bytes:
            return 0.0
        return round(100 * (1 - self.output_bytes / self.source_bytes), 1)


# --------------------------------------------------------------------------
# discovery
# --------------------------------------------------------------------------

def discover(inputs: Iterable[str], recursive: bool, include: list[str], exclude: list[str]) -> list[Path]:
    found: list[Path] = []
    for raw in inputs:
        path = Path(raw)
        if path.is_file():
            found.append(path)
        elif path.is_dir():
            pattern = "**/*" if recursive else "*"
            found.extend(p for p in sorted(path.glob(pattern)) if p.is_file())
        else:
            found.extend(sorted(Path().glob(raw)))  # treat as a glob

    def keep(path: Path) -> bool:
        if path.suffix.lower() not in IMAGE_SUFFIXES:
            return False
        name = path.as_posix()
        if include and not any(fnmatch.fnmatch(name, pat) for pat in include):
            return False
        if exclude and any(fnmatch.fnmatch(name, pat) for pat in exclude):
            return False
        return True

    seen: dict[str, Path] = {}
    for path in found:
        if keep(path):
            seen.setdefault(str(path.resolve()), path)
    return list(seen.values())


# --------------------------------------------------------------------------
# image operations
# --------------------------------------------------------------------------

def target_size(size: tuple[int, int], plan: Plan, width_override: int | None = None) -> tuple[int, int]:
    """Work out the output pixel size for one image."""
    source_w, source_h = size
    width = width_override or plan.width
    height = plan.height

    if plan.max_side and not width and not height:
        longest = max(source_w, source_h)
        if longest <= plan.max_side and not plan.upscale:
            return source_w, source_h
        ratio = plan.max_side / longest
        return max(1, round(source_w * ratio)), max(1, round(source_h * ratio))

    if width and height:
        return width, height
    if width:
        ratio = width / source_w
        return width, max(1, round(source_h * ratio))
    if height:
        ratio = height / source_h
        return max(1, round(source_w * ratio)), height
    return source_w, source_h


def resize_image(image: Image.Image, plan: Plan, width_override: int | None = None) -> Image.Image:
    want = target_size(image.size, plan, width_override)
    if want == image.size:
        return image
    if not plan.upscale and want[0] >= image.width and want[1] >= image.height:
        return image

    if plan.mode == "cover":
        return ImageOps.fit(image, want, method=Image.LANCZOS, centering=(0.5, 0.5))
    if plan.mode == "exact":
        return image.resize(want, Image.LANCZOS)
    # fit: preserve aspect ratio inside the box
    copy = image.copy()
    copy.thumbnail(want, Image.LANCZOS)
    return copy


def load_font(size: int) -> Any:
    for name in ("DejaVuSans-Bold.ttf", "DejaVuSans.ttf", "Arial.ttf", "Helvetica.ttc"):
        try:
            return ImageFont.truetype(name, size)
        except (OSError, IOError):
            continue
    try:
        return ImageFont.load_default(size)  # Pillow >= 10.1
    except TypeError:
        return ImageFont.load_default()


def anchor_box(image_size: tuple[int, int], mark_size: tuple[int, int],
               position: str, margin: float) -> tuple[int, int]:
    width, height = image_size
    mark_w, mark_h = mark_size
    pad_x = int(width * margin)
    pad_y = int(height * margin)
    left, right = pad_x, max(pad_x, width - mark_w - pad_x)
    top, bottom = pad_y, max(pad_y, height - mark_h - pad_y)
    center_x = max(0, (width - mark_w) // 2)
    center_y = max(0, (height - mark_h) // 2)
    return {
        "top-left": (left, top),
        "top-right": (right, top),
        "bottom-left": (left, bottom),
        "bottom-right": (right, bottom),
        "center": (center_x, center_y),
        "top-center": (center_x, top),
        "bottom-center": (center_x, bottom),
    }.get(position, (right, bottom))


def apply_watermark(image: Image.Image, plan: Plan, logo: Image.Image | None = None) -> Image.Image:
    if not plan.watermark_text and logo is None:
        return image

    base = image.convert("RGBA")
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))

    if logo is not None:
        mark = logo.copy()
        want_w = max(1, int(base.width * plan.watermark_scale))
        ratio = want_w / mark.width
        mark = mark.resize((want_w, max(1, round(mark.height * ratio))), Image.LANCZOS)
        alpha = mark.getchannel("A").point(lambda value: int(value * plan.watermark_opacity))
        mark.putalpha(alpha)
        layer.paste(mark, anchor_box(base.size, mark.size, plan.watermark_position, plan.watermark_margin), mark)
    else:
        font_size = max(12, int(base.width * plan.watermark_scale * 0.28))
        font = load_font(font_size)
        draw = ImageDraw.Draw(layer)
        box = draw.textbbox((0, 0), plan.watermark_text, font=font)
        mark_size = (box[2] - box[0], box[3] - box[1])
        x, y = anchor_box(base.size, mark_size, plan.watermark_position, plan.watermark_margin)
        opacity = int(255 * plan.watermark_opacity)
        # shadow first so the text stays readable on light and dark images
        draw.text((x + 2 - box[0], y + 2 - box[1]), plan.watermark_text,
                  font=font, fill=(0, 0, 0, int(opacity * 0.6)))
        draw.text((x - box[0], y - box[1]), plan.watermark_text,
                  font=font, fill=(255, 255, 255, opacity))

    return Image.alpha_composite(base, layer)


def prepare_for_save(image: Image.Image, fmt: str, background: str) -> Image.Image:
    """Flatten or convert modes that the target format cannot represent."""
    if fmt in ("JPEG", "BMP"):
        if image.mode in ("RGBA", "LA", "P"):
            rgba = image.convert("RGBA")
            canvas = Image.new("RGB", rgba.size, background)
            canvas.paste(rgba, mask=rgba.getchannel("A"))
            return canvas
        if image.mode != "RGB":
            return image.convert("RGB")
    elif image.mode == "P":
        return image.convert("RGBA")
    return image


def save_kwargs(fmt: str, plan: Plan, source: Image.Image) -> dict[str, Any]:
    options: dict[str, Any] = {}
    if fmt == "JPEG":
        options.update(quality=plan.quality, optimize=True, progressive=True, subsampling="4:2:0")
    elif fmt == "WEBP":
        options.update(quality=plan.quality, method=6)
    elif fmt == "PNG":
        options.update(optimize=True, compress_level=9)
    elif fmt == "AVIF":
        options.update(quality=plan.quality)
    if plan.keep_metadata:
        exif = source.info.get("exif")
        icc = source.info.get("icc_profile")
        if exif:
            options["exif"] = exif
        if icc:
            options["icc_profile"] = icc
    return options


# --------------------------------------------------------------------------
# naming
# --------------------------------------------------------------------------

def output_path(source: Path, plan: Plan, root: Path | None, fmt: str,
                index: int, size: tuple[int, int], suffix: str) -> Path:
    extension = EXTENSIONS.get(fmt, source.suffix).lstrip(".")
    name = plan.name_template.format(
        stem=source.stem,
        name=source.name,
        ext=extension,
        suffix=suffix,
        width=size[0],
        height=size[1],
        index=index,
        parent=source.parent.name,
    )
    if plan.flatten_tree or root is None:
        return plan.out_dir / name
    try:
        relative = source.resolve().parent.relative_to(root.resolve())
    except ValueError:
        relative = Path()
    return plan.out_dir / relative / name


# --------------------------------------------------------------------------
# processing
# --------------------------------------------------------------------------

def process_one(source: Path, plan: Plan, root: Path | None, logo: Image.Image | None) -> list[Record]:
    records: list[Record] = []
    try:
        source_bytes = source.stat().st_size
        with Image.open(source) as opened:
            opened.load()
            image = ImageOps.exif_transpose(opened) or opened
            original_size = image.size
            fmt = plan.fmt or FORMAT_ALIASES.get(source.suffix.lower().lstrip("."), image.format or "PNG")

            widths: list[int | None] = list(plan.sizes) if plan.sizes else [None]
            for index, width in enumerate(widths, start=1):
                suffix = f"-{width}w" if plan.sizes else ""
                resized = resize_image(image, plan, width)
                marked = apply_watermark(resized, plan, logo)
                final = prepare_for_save(marked, fmt, plan.background)
                if plan.sharpen and final.size != original_size:
                    final = ImageEnhance.Sharpness(final).enhance(1.15)

                destination = output_path(source, plan, root, fmt, index, final.size, suffix)
                if plan.dry_run:
                    records.append(Record(source, destination, "ok", source_bytes, 0,
                                          f"{original_size[0]}x{original_size[1]}",
                                          f"{final.size[0]}x{final.size[1]}", "dry-run"))
                    continue
                if plan.skip_existing and destination.exists():
                    records.append(Record(source, destination, "skipped", source_bytes,
                                          destination.stat().st_size,
                                          f"{original_size[0]}x{original_size[1]}", "", "exists"))
                    continue

                destination.parent.mkdir(parents=True, exist_ok=True)
                final.save(destination, fmt, **save_kwargs(fmt, plan, opened))
                records.append(Record(source, destination, "ok", source_bytes,
                                      destination.stat().st_size,
                                      f"{original_size[0]}x{original_size[1]}",
                                      f"{final.size[0]}x{final.size[1]}"))
    except Exception as exc:  # one bad file must not kill a 4,000 file batch
        records.append(Record(source, None, "error", note=f"{type(exc).__name__}: {exc}"))
    return records


def run_batch(sources: list[Path], plan: Plan, root: Path | None, workers: int,
              progress: bool = True) -> list[Record]:
    logo = None
    if plan.watermark_image:
        with Image.open(plan.watermark_image) as opened:
            logo = opened.convert("RGBA")

    records: list[Record] = []
    done = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(process_one, path, plan, root, logo): path for path in sources}
        for future in concurrent.futures.as_completed(futures):
            records.extend(future.result())
            done += 1
            if progress and (done % 25 == 0 or done == len(sources)):
                print(f"\r  {done}/{len(sources)} files", end="", file=sys.stderr, flush=True)
    if progress and sources:
        print(file=sys.stderr)
    return sorted(records, key=lambda r: (str(r.source), str(r.output)))


def write_manifest(records: list[Record], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["source", "output", "status", "source_size", "output_size",
                         "source_bytes", "output_bytes", "saved_pct", "note"])
        for record in records:
            writer.writerow([
                record.source, record.output or "", record.status,
                record.source_size, record.output_size,
                record.source_bytes, record.output_bytes, record.saved_pct, record.note,
            ])


def human_bytes(count: int) -> str:
    value = float(count)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return f"{value:,.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{value:.1f} GB"


# --------------------------------------------------------------------------
# commands
# --------------------------------------------------------------------------

def plan_from_args(args: argparse.Namespace) -> Plan:
    settings: dict[str, Any] = dict(PRESETS.get(args.preset, {})) if args.preset else {}
    # explicit flags win over the preset
    for key in ("max", "format", "quality", "mode", "width", "height", "sizes", "keep_metadata"):
        value = getattr(args, key, None)
        if value not in (None, False):
            settings[key] = value

    fmt_name = settings.get("format")
    sizes = settings.get("sizes")
    return Plan(
        out_dir=Path(args.out),
        fmt=FORMAT_ALIASES.get(str(fmt_name).lower()) if fmt_name else None,
        quality=int(settings.get("quality", 85)),
        mode=str(settings.get("mode", "fit")),
        width=settings.get("width"),
        height=settings.get("height"),
        max_side=settings.get("max"),
        sizes=[int(s) for s in str(sizes).split(",") if s] if sizes else [],
        upscale=args.upscale,
        sharpen=args.sharpen,
        keep_metadata=bool(settings.get("keep_metadata", False)),
        background=args.background,
        name_template=args.name,
        flatten_tree=args.flatten_tree,
        skip_existing=args.skip_existing,
        watermark_text=args.watermark_text or "",
        watermark_image=Path(args.watermark_image) if args.watermark_image else None,
        watermark_position=args.watermark_position,
        watermark_opacity=args.watermark_opacity,
        watermark_scale=args.watermark_scale,
        watermark_margin=args.watermark_margin,
        dry_run=args.dry_run,
    )


def cmd_process(args: argparse.Namespace) -> int:
    sources = discover(args.inputs, not args.no_recursive, args.include, args.exclude)
    if not sources:
        print("no images matched", file=sys.stderr)
        return 2

    plan = plan_from_args(args)
    root = Path(args.inputs[0]) if len(args.inputs) == 1 and Path(args.inputs[0]).is_dir() else None
    if not args.quiet:
        print(f"{len(sources)} image(s) -> {plan.out_dir}" + ("  [dry run]" if plan.dry_run else ""),
              file=sys.stderr)

    started = time.time()
    records = run_batch(sources, plan, root, args.workers, progress=not args.quiet)

    ok = [r for r in records if r.status == "ok"]
    errors = [r for r in records if r.status == "error"]
    skipped = [r for r in records if r.status == "skipped"]
    bytes_in = sum(r.source_bytes for r in ok)
    bytes_out = sum(r.output_bytes for r in ok)

    if plan.dry_run:
        for record in records[:40]:
            print(f"  {record.source}  {record.source_size} -> {record.output_size}  {record.output}")
        if len(records) > 40:
            print(f"  ... and {len(records) - 40} more")

    if not args.quiet:
        print(
            f"done in {time.time() - started:.1f}s | written {len(ok)} | "
            f"skipped {len(skipped)} | errors {len(errors)}", file=sys.stderr
        )
        if bytes_out and not plan.dry_run:
            change = 100 * (1 - bytes_out / bytes_in) if bytes_in else 0
            direction = "smaller" if change >= 0 else "larger"
            print(f"size {human_bytes(bytes_in)} -> {human_bytes(bytes_out)} "
                  f"({abs(change):.1f}% {direction})", file=sys.stderr)
    for record in errors[:10]:
        print(f"  error: {record.source}: {record.note}", file=sys.stderr)

    if args.manifest:
        write_manifest(records, Path(args.manifest))
        print(f"manifest -> {args.manifest}", file=sys.stderr)

    return 1 if errors and not ok else 0


def cmd_inspect(args: argparse.Namespace) -> int:
    sources = discover(args.inputs, not args.no_recursive, args.include, args.exclude)
    if not sources:
        print("no images matched", file=sys.stderr)
        return 2

    total_bytes = 0
    by_format: dict[str, int] = {}
    widest = (0, None)
    rows = []
    for path in sources:
        try:
            with Image.open(path) as image:
                size = path.stat().st_size
                total_bytes += size
                by_format[image.format or "?"] = by_format.get(image.format or "?", 0) + 1
                if image.width > widest[0]:
                    widest = (image.width, path)
                rows.append((path, image.size, image.mode, size))
        except Exception as exc:
            rows.append((path, (0, 0), f"unreadable: {exc}", 0))

    for path, size, mode, byte_count in rows[: args.limit]:
        print(f"{str(path)[:70]:<70} {size[0]:>5}x{size[1]:<5} {mode:<6} {human_bytes(byte_count):>10}")
    if len(rows) > args.limit:
        print(f"... and {len(rows) - args.limit} more")

    print(f"\n{len(sources)} images, {human_bytes(total_bytes)} total, "
          f"avg {human_bytes(total_bytes // max(1, len(sources)))}")
    print("formats: " + ", ".join(f"{k} x{v}" for k, v in sorted(by_format.items())))
    if widest[1]:
        print(f"widest: {widest[1]} ({widest[0]}px)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="imagebatch.py",
        description="Batch resize / convert / watermark / optimise images.",
        epilog="presets: " + ", ".join(PRESETS),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("process", help="process a folder or file list")
    run.add_argument("inputs", nargs="+", help="files, folders or globs")
    run.add_argument("--out", required=True, help="output directory (never written in place)")
    run.add_argument("--preset", choices=sorted(PRESETS), help="starting point; explicit flags win")

    size = run.add_argument_group("sizing")
    size.add_argument("--max", type=int, help="longest side, preserving aspect ratio")
    size.add_argument("--width", type=int)
    size.add_argument("--height", type=int)
    size.add_argument("--sizes", help="comma-separated widths, e.g. 320,800,1600")
    size.add_argument("--mode", choices=["fit", "cover", "exact"], help="default: fit")
    size.add_argument("--upscale", action="store_true", help="allow enlarging small images")
    size.add_argument("--sharpen", action="store_true", help="light sharpen after resizing")

    out = run.add_argument_group("output")
    out.add_argument("--format", choices=sorted(FORMAT_ALIASES), help="default: keep source format")
    out.add_argument("--quality", type=int, help="JPEG/WEBP quality, default 85")
    out.add_argument("--name", default="{stem}{suffix}.{ext}",
                     help="filename template: {stem} {name} {ext} {suffix} {width} {height} {index} {parent}")
    out.add_argument("--flatten-tree", action="store_true", help="ignore the input folder structure")
    out.add_argument("--skip-existing", action="store_true")
    out.add_argument("--keep-metadata", action="store_true", help="preserve EXIF and ICC (stripped by default)")
    out.add_argument("--background", default="#ffffff", help="fill colour when flattening alpha to JPEG")
    out.add_argument("--manifest", help="write a CSV report of every file")

    mark = run.add_argument_group("watermark")
    mark.add_argument("--watermark-text")
    mark.add_argument("--watermark-image")
    mark.add_argument("--watermark-position", choices=POSITIONS, default="bottom-right")
    mark.add_argument("--watermark-opacity", type=float, default=0.45)
    mark.add_argument("--watermark-scale", type=float, default=0.18,
                      help="mark width as a fraction of the image width")
    mark.add_argument("--watermark-margin", type=float, default=0.025)

    run.add_argument("--include", action="append", default=[], help="glob to keep, repeatable")
    run.add_argument("--exclude", action="append", default=[], help="glob to drop, repeatable")
    run.add_argument("--no-recursive", action="store_true")
    run.add_argument("--workers", type=int, default=8)
    run.add_argument("--dry-run", action="store_true", help="report what would happen, write nothing")
    run.add_argument("-q", "--quiet", action="store_true")
    run.set_defaults(func=cmd_process)

    inspect = sub.add_parser("inspect", help="report sizes, formats and total weight")
    inspect.add_argument("inputs", nargs="+")
    inspect.add_argument("--include", action="append", default=[])
    inspect.add_argument("--exclude", action="append", default=[])
    inspect.add_argument("--no-recursive", action="store_true")
    inspect.add_argument("--limit", type=int, default=25)
    inspect.set_defaults(func=cmd_inspect)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
