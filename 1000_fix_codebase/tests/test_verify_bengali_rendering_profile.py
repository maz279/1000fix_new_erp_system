"""R01-AUDIT: verify_bengali_rendering asserts the sampled pixels against the
layout render-bengali-reference.ps1 documents (900x260, 1px black border,
white background, Bengali text that fits the canvas)."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "scripts" / "verify_bengali_rendering.py"


def _load():
    spec = importlib.util.spec_from_file_location("verify_bengali_rendering_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _canvas(border: bool = True) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGBA", (900, 260), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    if border:
        draw.rectangle((0, 0, 899, 259), outline=(0, 0, 0, 255), width=1)
    return img, draw


def _bengali_like(draw: ImageDraw.ImageDraw) -> None:
    """Words hanging from a continuous headline (matra), as Bengali shapes."""
    for y in (52, 90, 128, 172):
        x = 16
        for width in (90, 60, 110):
            draw.line((x, y, x + width, y), fill=(0, 0, 0, 255), width=2)
            for stem in range(x + 6, x + width, 14):
                draw.line((stem, y, stem, y + 18), fill=(0, 0, 0, 255), width=2)
            x += width + 18


def _latin_like(draw: ImageDraw.ImageDraw, run_to_edge: bool) -> None:
    """Short, separate glyph strokes - no headline; optionally clipped at the edge."""
    end = 899 if run_to_edge else 600
    for y in (52, 90, 128):
        for x in range(16, end, 9):
            draw.line((x, y, x, y + 16), fill=(0, 0, 0, 255), width=2)
            draw.line((x, y + 16, x + 5, y + 16), fill=(0, 0, 0, 255), width=1)


class TestPixelProfile(unittest.TestCase):
    def setUp(self):
        self.vbr = _load()

    def test_documented_layout_passes(self):
        img, draw = _canvas()
        _bengali_like(draw)
        profile = self.vbr.measure_pixel_profile(img)
        self.assertTrue(profile["dimensions_correct"])
        self.assertTrue(profile["border_present"])
        self.assertTrue(profile["background_white"])
        self.assertTrue(profile["text_rendered"])
        self.assertTrue(profile["text_within_margin"])
        self.assertTrue(profile["bengali_headline_present"], profile["max_headline_run_px"])

    def test_missing_border_fails(self):
        img, draw = _canvas(border=False)
        _bengali_like(draw)
        self.assertFalse(self.vbr.measure_pixel_profile(img)["border_present"])

    def test_blank_reference_fails(self):
        img, _ = _canvas()
        profile = self.vbr.measure_pixel_profile(img)
        self.assertFalse(profile["text_rendered"])
        self.assertFalse(profile["bengali_headline_present"])

    def test_mojibake_like_render_fails(self):
        """UTF-8 read as ANSI: Latin glyphs, no headline, text runs off the edge."""
        img, draw = _canvas()
        _latin_like(draw, run_to_edge=True)
        profile = self.vbr.measure_pixel_profile(img)
        self.assertFalse(profile["bengali_headline_present"])
        self.assertFalse(profile["text_within_margin"])

    def test_wrong_size_fails(self):
        profile = self.vbr.measure_pixel_profile(Image.new("RGB", (800, 260), "white"))
        self.assertFalse(profile["dimensions_correct"])
        self.assertFalse(profile["border_present"])

    def test_non_white_background_fails(self):
        img = Image.new("RGB", (900, 260), (200, 200, 200))
        draw = ImageDraw.Draw(img)
        draw.rectangle((0, 0, 899, 259), outline=(0, 0, 0), width=1)
        self.assertFalse(self.vbr.measure_pixel_profile(img)["background_white"])


TOKENS_JSON = '{"typography": {"font": {"bengali": {"family": {"$value": "Noto Sans Bengali"}}}}}'
TOKENS_CSS = ":root {\n  --fix-typography-font-bengali-family: Noto Sans Bengali;\n}\n"
APPLY_RULE = ".page { font-family: var(--fix-typography-font-bengali-family), sans-serif; }\n"
REPORT_XML = (
    '<odoo><template id="report_mushak63"><div class="page mushak63">' "মুশক</div></template></odoo>"
)


class TestFontStack(unittest.TestCase):
    """verify_font_stack measures registrations and installed fonts - a file
    that merely mentions "Bengali" proves nothing."""

    def setUp(self):
        self.vbr = _load()
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        addons = root / "addons"
        tokens_mod = addons / "platform" / "cd_design_tokens"
        (tokens_mod / "static" / "src").mkdir(parents=True)
        (tokens_mod / "__manifest__.py").write_text(
            "{'name': 't', 'assets': {'web.report_assets_common': "
            "['cd_design_tokens/static/src/tokens.css']}}",
            encoding="utf-8",
        )
        self.tokens_css = tokens_mod / "static" / "src" / "tokens.css"
        self.tokens_css.write_text(TOKENS_CSS + APPLY_RULE, encoding="utf-8")
        tax = addons / "domain" / "cd_tax_engine_bd"
        (tax / "report").mkdir(parents=True)
        (tax / "__manifest__.py").write_text("{'name': 'tax'}", encoding="utf-8")
        (tax / "report" / "report_mushak63.xml").write_text(REPORT_XML, encoding="utf-8")
        tokens_json = root / "tokens.json"
        tokens_json.write_text(TOKENS_JSON, encoding="utf-8")
        reference = root / "docs" / "guides" / "reference"
        reference.mkdir(parents=True)
        (reference / "bengali-conjunct-reference.png").write_bytes(b"png")
        self.vbr.REPO_ROOT = root
        self.vbr.ADDONS_DIR = addons
        self.vbr.TOKENS_JSON = tokens_json
        self.vbr.TOKENS_CSS = self.tokens_css
        self.installed = {"nirmala ui"}
        self.vbr.installed_font_families = lambda: (self.installed, "test")

    def tearDown(self):
        self.tmp.cleanup()

    def test_applied_and_installed_passes(self):
        res = self.vbr.verify_font_stack()
        self.assertEqual(res["status"], "PASS", res["failed_checks"])
        self.assertEqual(res["primary_font"], "Noto Sans Bengali")
        self.assertTrue(res["statutory_templates_apply_font"]["mushak_6_3"])
        self.assertTrue(res["fallback_font_installed"])
        self.assertFalse(res["primary_font_installed"])

    def test_declared_but_never_applied_fails(self):
        self.tokens_css.write_text(TOKENS_CSS, encoding="utf-8")
        res = self.vbr.verify_font_stack()
        self.assertEqual(res["status"], "FAIL")
        self.assertFalse(res["statutory_templates_apply_font"]["mushak_6_3"])

    def test_no_bengali_font_installed_fails(self):
        self.installed.clear()
        self.installed.add("arial")
        res = self.vbr.verify_font_stack()
        self.assertEqual(res["status"], "FAIL")
        self.assertTrue(any("installed" in f for f in res["failed_checks"]))

    def test_unregistered_token_css_fails(self):
        manifest = self.vbr.ADDONS_DIR / "platform" / "cd_design_tokens" / "__manifest__.py"
        manifest.write_text("{'name': 't'}", encoding="utf-8")
        res = self.vbr.verify_font_stack()
        self.assertEqual(res["status"], "FAIL")
        self.assertFalse(res["token_css_in_report_assets"])

    def test_registered_template_must_exist(self):
        res = self.vbr.verify_statutory_templates()
        self.assertEqual(res["status"], "FAIL")  # only mushak63 exists in the fixture
        self.assertTrue(res["templates"]["mushak_6_3"]["qweb_template_found"])
        self.assertFalse(res["templates"]["mushak_6_6"]["qweb_template_found"])


if __name__ == "__main__":
    unittest.main()
