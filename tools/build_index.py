#!/usr/bin/env python3
"""Generate index/ - machine-readable manifests for agents consuming this repo.

Walks every pack listed in catalog.json and records what is actually inside it:
file inventory, preview image, sprite sheets paired with their atlas, and audio
durations. Re-runnable; overwrites index/ from the current working tree.
"""
import json
import os
import re
import struct
import subprocess
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "index")

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".svg"}
AUDIO_EXT = {".ogg", ".wav", ".mp3"}
MODEL_EXT = {".glb", ".gltf", ".obj", ".dae", ".fbx", ".blend"}
FONT_EXT = {".ttf", ".otf"}
PREVIEW_NAMES = ("preview.png", "preview-part-1.png", "sample.png", "Preview.png",
                 "Sample.png", "Preview (Variation A).png")


def png_size(path):
    """Read width/height straight out of the IHDR chunk."""
    try:
        with open(path, "rb") as fh:
            head = fh.read(24)
        if head[:8] != b"\x89PNG\r\n\x1a\n":
            return None
        return struct.unpack(">II", head[16:24])
    except Exception:
        return None


def rel(path):
    return os.path.relpath(path, REPO).replace(os.sep, "/")


def find_sheets(pack_dir):
    """Pair sprite sheets with their atlas. Kenney ships TextureAtlas XML next to
    the sheet; Superpowers ships a combined 0-*.png with no atlas."""
    sheets, claimed = [], set()

    for cur, _, files in os.walk(pack_dir):
        for name in files:
            if not name.lower().endswith(".xml"):
                continue
            xml_path = os.path.join(cur, name)
            try:
                root = ET.parse(xml_path).getroot()
            except ET.ParseError:
                continue
            if root.tag != "TextureAtlas":
                continue
            # TexturePacker leaves imagePath as a placeholder ("sheet.png") in
            # most Kenney packs; the real sheet is named after the XML instead.
            candidates = [os.path.splitext(name)[0] + ".png", root.get("imagePath")]
            sheet = next((os.path.join(cur, c) for c in candidates
                          if c and os.path.isfile(os.path.join(cur, c))), None)
            if sheet is None:
                continue
            claimed.add(os.path.normpath(sheet))
            size = png_size(sheet)
            sheets.append({
                "sheet": rel(sheet), "atlas": rel(xml_path), "atlas_format": "texture-atlas-xml",
                "frames": len(root.findall("SubTexture")),
                "width": size[0] if size else None, "height": size[1] if size else None,
            })

    for cur, _, files in os.walk(pack_dir):
        in_sheet_dir = os.path.basename(cur).lower().startswith("spritesheet")
        for name in files:
            if not name.lower().endswith(".png"):
                continue
            path = os.path.join(cur, name)
            if os.path.normpath(path) in claimed:
                continue
            low = name.lower()
            if not (in_sheet_dir or "spritesheet" in low or re.match(r"^0-.*\.png$", low)):
                continue
            size = png_size(path)
            sheets.append({
                "sheet": rel(path), "atlas": None, "atlas_format": None, "frames": None,
                "width": size[0] if size else None, "height": size[1] if size else None,
            })

    sheets.sort(key=lambda s: s["sheet"])
    return sheets


def audio_duration(path):
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", path],
            capture_output=True, text=True, timeout=30)
        return round(float(r.stdout.strip()), 2)
    except Exception:
        return None


def main():
    with open(os.path.join(REPO, "catalog.json")) as fh:
        catalog = json.load(fh)

    packs, all_sheets, audio_jobs = [], [], []

    for asset in catalog["assets"]:
        pack_dir = os.path.join(REPO, asset["path"])
        by_ext, total_bytes, files = {}, 0, []
        for cur, _, names in os.walk(pack_dir):
            for name in names:
                if name == "SOURCE.md":
                    continue
                path = os.path.join(cur, name)
                ext = os.path.splitext(name)[1].lower()
                by_ext[ext] = by_ext.get(ext, 0) + 1
                total_bytes += os.path.getsize(path)
                files.append(path)

        preview = next(
            (rel(os.path.join(pack_dir, n)) for n in PREVIEW_NAMES
             if os.path.isfile(os.path.join(pack_dir, n))), None)
        if preview is None:
            for cur, _, names in os.walk(pack_dir):
                hit = next((n for n in sorted(names) if n in PREVIEW_NAMES), None)
                if hit:
                    preview = rel(os.path.join(cur, hit))
                    break

        sheets = find_sheets(pack_dir)
        all_sheets.extend(sheets)

        audio_files = sorted(f for f in files if os.path.splitext(f)[1].lower() in AUDIO_EXT)
        audio_jobs.extend((asset["id"], f) for f in audio_files)

        entry = dict(asset)
        entry.update({
            "files": sum(by_ext.values()),
            "bytes": total_bytes,
            "by_extension": dict(sorted(by_ext.items())),
            "counts": {
                "images": sum(n for e, n in by_ext.items() if e in IMAGE_EXT),
                "audio": len(audio_files),
                "models": sum(n for e, n in by_ext.items() if e in MODEL_EXT),
                "fonts": sum(n for e, n in by_ext.items() if e in FONT_EXT),
            },
            "preview": preview,
            "sprite_sheets": sheets,
            "source_md": asset["path"] + "/SOURCE.md",
        })
        packs.append(entry)

    with ThreadPoolExecutor(max_workers=8) as pool:
        durations = list(pool.map(lambda j: audio_duration(j[1]), audio_jobs))

    audio_index = []
    per_pack_seconds = {}
    for (pack_id, path), secs in zip(audio_jobs, durations):
        audio_index.append({"pack": pack_id, "file": rel(path), "seconds": secs})
        if secs:
            per_pack_seconds[pack_id] = round(per_pack_seconds.get(pack_id, 0) + secs, 2)
    for entry in packs:
        if entry["id"] in per_pack_seconds:
            entry["audio_seconds"] = per_pack_seconds[entry["id"]]

    by_genre, by_type = {}, {}
    for entry in packs:
        for g in entry["genres"]:
            by_genre.setdefault(g, []).append(entry["id"])
        by_type.setdefault(entry.get("type", "3d"), []).append(entry["id"])
    by_genre = {g: sorted(v) for g, v in sorted(by_genre.items())}
    by_type = {t: sorted(v) for t, v in sorted(by_type.items())}

    os.makedirs(OUT, exist_ok=True)
    manifests = {
        "packs.json": {
            "generated_from": "catalog.json + working tree",
            "license": "CC0-1.0 (every pack)",
            "packs": len(packs),
            "assets": packs,
        },
        "spritesheets.json": {
            "note": "Every packed sprite sheet in the repo. 'atlas' is a Kenney-style "
                    "TextureAtlas XML (SubTexture name/x/y/width/height) when present; "
                    "null means the sheet is a uniform grid you slice yourself.",
            "count": len(all_sheets),
            "sheets": sorted(all_sheets, key=lambda s: s["sheet"]),
        },
        "by-genre.json": {
            "note": "genre -> pack ids. `genres` is the theme axis (what a pack "
                    "depicts) and is the field to filter on; `type` is the format "
                    "axis. A pack appears under every genre it matches.",
            "genres": by_genre,
            "types": by_type,
        },
        "audio.json": {
            "note": "Every sound effect and music file, with duration in seconds.",
            "count": len(audio_index),
            "files": audio_index,
        },
    }
    for name, data in manifests.items():
        with open(os.path.join(OUT, name), "w", newline="\r\n") as fh:
            json.dump(data, fh, indent=1)
            fh.write("\n")

    with_atlas = sum(1 for s in all_sheets if s["atlas"])
    print("packs {} | sheets {} ({} with atlas) | audio files {} ({:.0f} min)".format(
        len(packs), len(all_sheets), with_atlas, len(audio_index),
        sum(d for d in durations if d) / 60))


if __name__ == "__main__":
    main()
