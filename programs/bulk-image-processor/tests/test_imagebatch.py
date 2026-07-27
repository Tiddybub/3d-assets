"""Tests for the bulk image processor. Run: python3 -m unittest discover -s tests"""

import csv
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PIL import Image  # noqa: E402

import imagebatch as ib  # noqa: E402


def make_image(path: Path, size=(1200, 800), color=(200, 40, 40), mode="RGB", fmt=None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new(mode, size, color if mode != "RGBA" else (*color, 128))
    image.save(path, fmt)
    return path


class BaseCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.src = self.root / "src"
        self.out = self.root / "out"

    def run_cli(self, *args):
        return ib.main([str(a) for a in args])


class DiscoveryTests(BaseCase):
    def setUp(self):
        super().setUp()
        make_image(self.src / "a.jpg")
        make_image(self.src / "nested" / "b.png")
        make_image(self.src / "nested" / "deep" / "c.webp")
        (self.src / "notes.txt").write_text("not an image")

    def test_finds_images_recursively_and_ignores_other_files(self):
        found = ib.discover([str(self.src)], True, [], [])
        self.assertEqual({p.name for p in found}, {"a.jpg", "b.png", "c.webp"})

    def test_no_recursive_stays_at_the_top_level(self):
        found = ib.discover([str(self.src)], False, [], [])
        self.assertEqual({p.name for p in found}, {"a.jpg"})

    def test_include_and_exclude_globs(self):
        self.assertEqual(len(ib.discover([str(self.src)], True, ["*.png"], [])), 1)
        self.assertEqual(len(ib.discover([str(self.src)], True, [], ["*deep*"])), 2)

    def test_duplicate_inputs_are_processed_once(self):
        found = ib.discover([str(self.src), str(self.src / "a.jpg")], True, [], [])
        self.assertEqual(len(found), 3)


class SizingTests(unittest.TestCase):
    def plan(self, **kwargs):
        return ib.Plan(out_dir=Path("."), **kwargs)

    def test_max_side_scales_the_longest_edge(self):
        self.assertEqual(ib.target_size((1200, 800), self.plan(max_side=600)), (600, 400))
        self.assertEqual(ib.target_size((800, 1200), self.plan(max_side=600)), (400, 600))

    def test_max_side_does_not_upscale_by_default(self):
        self.assertEqual(ib.target_size((300, 200), self.plan(max_side=1000)), (300, 200))
        self.assertEqual(ib.target_size((300, 200), self.plan(max_side=1000, upscale=True)), (1000, 667))

    def test_width_only_preserves_aspect(self):
        self.assertEqual(ib.target_size((1200, 800), self.plan(width=600)), (600, 400))

    def test_width_and_height_are_taken_literally(self):
        self.assertEqual(ib.target_size((1200, 800), self.plan(width=500, height=500)), (500, 500))

    def test_fit_keeps_aspect_cover_crops(self):
        image = Image.new("RGB", (1200, 800), "blue")
        fitted = ib.resize_image(image, self.plan(width=600, height=600, mode="fit"))
        covered = ib.resize_image(image, self.plan(width=600, height=600, mode="cover"))
        self.assertEqual(fitted.size, (600, 400))   # fits inside the box
        self.assertEqual(covered.size, (600, 600))  # fills the box, centre-cropped


class ProcessingTests(BaseCase):
    def setUp(self):
        super().setUp()
        make_image(self.src / "photo.jpg", (1600, 1200))
        make_image(self.src / "logo.png", (800, 800), mode="RGBA")

    def test_resize_and_convert_to_webp(self):
        code = self.run_cli("process", self.src, "--out", self.out, "--max", 400, "--format", "webp", "-q")
        self.assertEqual(code, 0)
        outputs = sorted(p.name for p in self.out.rglob("*.webp"))
        self.assertEqual(outputs, ["logo.webp", "photo.webp"])
        with Image.open(self.out / "photo.webp") as image:
            self.assertEqual(image.size, (400, 300))
            self.assertEqual(image.format, "WEBP")

    def test_originals_are_never_modified(self):
        before = (self.src / "photo.jpg").read_bytes()
        self.run_cli("process", self.src, "--out", self.out, "--max", 200, "-q")
        self.assertEqual((self.src / "photo.jpg").read_bytes(), before)

    def test_alpha_is_flattened_for_jpeg(self):
        self.run_cli("process", self.src / "logo.png", "--out", self.out,
                     "--format", "jpeg", "--background", "#000000", "-q")
        with Image.open(self.out / "logo.jpg") as image:
            self.assertEqual(image.mode, "RGB")

    def test_responsive_sizes_produce_one_file_each(self):
        self.run_cli("process", self.src / "photo.jpg", "--out", self.out,
                     "--sizes", "200,400,800", "--format", "jpeg", "-q")
        names = sorted(p.name for p in self.out.glob("*.jpg"))
        self.assertEqual(names, ["photo-200w.jpg", "photo-400w.jpg", "photo-800w.jpg"])
        with Image.open(self.out / "photo-400w.jpg") as image:
            self.assertEqual(image.width, 400)

    def test_folder_structure_is_mirrored_unless_flattened(self):
        make_image(self.src / "sub" / "deep.jpg", (600, 600))
        self.run_cli("process", self.src, "--out", self.out, "--max", 100, "-q")
        self.assertTrue((self.out / "sub" / "deep.jpg").exists())

        flat = self.root / "flat"
        self.run_cli("process", self.src, "--out", flat, "--max", 100, "--flatten-tree", "-q")
        self.assertTrue((flat / "deep.jpg").exists())

    def test_name_template(self):
        self.run_cli("process", self.src / "photo.jpg", "--out", self.out,
                     "--max", 300, "--name", "{stem}_{width}x{height}.{ext}", "-q")
        self.assertTrue((self.out / "photo_300x225.jpg").exists())

    def test_metadata_is_stripped_by_default(self):
        source = self.src / "exif.jpg"
        image = Image.new("RGB", (500, 500), "green")
        exif = image.getexif()
        exif[271] = "TestCamera"
        image.save(source, exif=exif)

        self.run_cli("process", source, "--out", self.out, "--max", 200, "-q")
        with Image.open(self.out / "exif.jpg") as out_image:
            self.assertNotIn(271, out_image.getexif())

        kept = self.root / "kept"
        self.run_cli("process", source, "--out", kept, "--max", 200, "--keep-metadata", "-q")
        with Image.open(kept / "exif.jpg") as out_image:
            self.assertEqual(out_image.getexif().get(271), "TestCamera")

    def test_dry_run_writes_nothing(self):
        self.run_cli("process", self.src, "--out", self.out, "--max", 200, "--dry-run", "-q")
        self.assertFalse(self.out.exists() and any(self.out.rglob("*")))

    def test_skip_existing_leaves_the_first_output_alone(self):
        self.run_cli("process", self.src / "photo.jpg", "--out", self.out, "--max", 800, "-q")
        first = (self.out / "photo.jpg").stat().st_size
        self.run_cli("process", self.src / "photo.jpg", "--out", self.out,
                     "--max", 100, "--skip-existing", "-q")
        self.assertEqual((self.out / "photo.jpg").stat().st_size, first)

    def test_corrupt_file_is_reported_not_fatal(self):
        broken = self.src / "broken.jpg"
        broken.write_bytes(b"this is not a JPEG")
        code = self.run_cli("process", self.src, "--out", self.out, "--max", 200,
                            "--manifest", self.root / "m.csv", "-q")
        self.assertEqual(code, 0)  # the good files still went through
        with (self.root / "m.csv").open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        statuses = {Path(r["source"]).name: r["status"] for r in rows}
        self.assertEqual(statuses["broken.jpg"], "error")
        self.assertEqual(statuses["photo.jpg"], "ok")

    def test_manifest_records_sizes_and_savings(self):
        manifest = self.root / "manifest.csv"
        self.run_cli("process", self.src / "photo.jpg", "--out", self.out,
                     "--max", 400, "--format", "jpeg", "--manifest", manifest, "-q")
        with manifest.open(encoding="utf-8") as handle:
            row = next(iter(csv.DictReader(handle)))
        self.assertEqual(row["source_size"], "1600x1200")
        self.assertEqual(row["output_size"], "400x300")
        self.assertEqual(row["status"], "ok")
        self.assertGreater(int(row["output_bytes"]), 0)


class WatermarkTests(BaseCase):
    def setUp(self):
        super().setUp()
        self.photo = make_image(self.src / "photo.jpg", (900, 600), color=(20, 20, 20))

    def corner_pixels(self, path, box=(0.75, 0.75, 1.0, 1.0)):
        with Image.open(path) as image:
            width, height = image.size
            region = image.crop((int(width * box[0]), int(height * box[1]),
                                 int(width * box[2]), int(height * box[3])))
            raw = region.convert("RGB").tobytes()
        return [tuple(raw[i:i + 3]) for i in range(0, len(raw), 3)]

    def test_text_watermark_changes_the_chosen_corner(self):
        self.run_cli("process", self.photo, "--out", self.out,
                     "--watermark-text", "(c) Studio", "--watermark-position", "bottom-right", "-q")
        pixels = self.corner_pixels(self.out / "photo.jpg")
        self.assertTrue(any(sum(p) > 200 for p in pixels), "expected light watermark pixels")

    def test_watermark_position_is_respected(self):
        self.run_cli("process", self.photo, "--out", self.out,
                     "--watermark-text", "MARK", "--watermark-position", "top-left", "-q")
        top_left = self.corner_pixels(self.out / "photo.jpg", (0.0, 0.0, 0.35, 0.35))
        bottom_right = self.corner_pixels(self.out / "photo.jpg", (0.75, 0.75, 1.0, 1.0))
        self.assertTrue(any(sum(p) > 200 for p in top_left))
        self.assertFalse(any(sum(p) > 200 for p in bottom_right))

    def test_image_watermark_is_scaled_to_the_target(self):
        logo = make_image(self.src / "mark.png", (400, 400), mode="RGBA")
        plain = self.root / "plain"
        self.run_cli("process", self.photo, "--out", plain, "--exclude", "*mark.png", "-q")
        self.run_cli("process", self.photo, "--out", self.out,
                     "--watermark-image", logo, "--watermark-scale", "0.25",
                     "--exclude", "*mark.png", "-q")

        with Image.open(self.out / "photo.jpg") as image:
            self.assertEqual(image.size, (900, 600))  # watermarking must not resize
        marked = self.corner_pixels(self.out / "photo.jpg")
        untouched = self.corner_pixels(plain / "photo.jpg")
        changed = sum(1 for a, b in zip(marked, untouched) if a != b)
        self.assertGreater(changed, len(marked) // 10, "watermark did not reach the corner")

    def test_watermark_applies_to_every_responsive_size(self):
        self.run_cli("process", self.photo, "--out", self.out, "--sizes", "300,600",
                     "--watermark-text", "X", "-q")
        for name in ("photo-300w.jpg", "photo-600w.jpg"):
            self.assertTrue(any(sum(p) > 200 for p in self.corner_pixels(self.out / name)))


class PresetTests(BaseCase):
    def setUp(self):
        super().setUp()
        make_image(self.src / "photo.jpg", (2400, 1600))

    def test_web_preset_resizes_and_converts(self):
        self.run_cli("process", self.src, "--out", self.out, "--preset", "web", "-q")
        with Image.open(self.out / "photo.webp") as image:
            self.assertEqual(image.format, "WEBP")
            self.assertEqual(max(image.size), 1600)

    def test_explicit_flags_beat_the_preset(self):
        self.run_cli("process", self.src, "--out", self.out, "--preset", "web", "--max", 400, "-q")
        with Image.open(self.out / "photo.webp") as image:
            self.assertEqual(max(image.size), 400)

    def test_social_square_crops_to_a_square(self):
        self.run_cli("process", self.src, "--out", self.out, "--preset", "social-square", "-q")
        with Image.open(self.out / "photo.jpg") as image:
            self.assertEqual(image.size, (1080, 1080))


class InspectTests(BaseCase):
    def test_inspect_reports_without_writing(self):
        make_image(self.src / "a.jpg", (100, 100))
        make_image(self.src / "b.png", (200, 300))
        self.assertEqual(self.run_cli("inspect", self.src), 0)
        self.assertFalse(self.out.exists())

    def test_inspect_on_empty_folder_returns_error_code(self):
        (self.root / "empty").mkdir()
        self.assertEqual(self.run_cli("inspect", self.root / "empty"), 2)


if __name__ == "__main__":
    unittest.main()
