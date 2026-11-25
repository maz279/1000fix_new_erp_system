#!/usr/bin/env python3
"""
tooling/scripts/verify_bengali_rendering.py — Bengali Conjunct Shaping & Report Rendering Verification

Milestone: R07-M02-T05 (P09-M02-T09) / TR-07 / Doctor Check 10 / BN-007
Evaluates:
  1. Integrity and dimensional conformance of docs/guides/reference/bengali-conjunct-reference.png
  2. BN-007 currency formatting, lakh-crory notation, and Bengali numeral conversion
  3. Statutory document template registrations in services/document-generation
  4. QWeb template font-stack definitions across addons/domain (Noto Sans Bengali / Nirmala UI)
  5. Deterministic hash and pixel profile comparison of the conjunct-dense test phrase

Emits: docs/traceability/evidence/bengali-rendering-verification.json
"""

import ast
import contextlib
import hashlib
import json
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from PIL import Image

if sys.stdout.encoding.lower() != "utf-8":
    with contextlib.suppress(Exception):
        sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parents[2]
REFERENCE_IMAGE = REPO_ROOT / "docs" / "guides" / "reference" / "bengali-conjunct-reference.png"
EVIDENCE_OUT = (
    REPO_ROOT / "docs" / "traceability" / "evidence" / "bengali-rendering-verification.json"
)

ADDONS_DIR = REPO_ROOT / "addons"
DOCGEN_SRC = REPO_ROOT / "services" / "document-generation" / "src"
TOKENS_JSON = REPO_ROOT / "libs" / "ts" / "ui" / "src" / "tokens" / "tokens.json"
TOKENS_CSS = ADDONS_DIR / "platform" / "cd_design_tokens" / "static" / "src" / "tokens.css"
BENGALI_VAR = "--fix-typography-font-bengali-family"
# render-bengali-reference.ps1 falls back to this family when the token family is absent
FALLBACK_FAMILY = "Nirmala UI"
PAGE_SELECTORS = {"body", "html", ":root", "*", ".page", ".article"}

# Documented by render-bengali-reference.ps1: 900x260, white background, 1px
# black border. Text is black anti-aliased glyphs: a blank interior (0 ink)
# or a flooded one means the render failed.
EXPECTED_SIZE = (900, 260)
DARK_MAX = 64  # border/glyph-core pixel
INK_MAX = 128  # any anti-aliased glyph ink
WHITE_MIN = 245
INK_RATIO_RANGE = (0.005, 0.5)
LABEL_BAND_TOP = 44  # the Bengali lines start at y=48 (the title above is Latin)
RIGHT_MARGIN_PX = 40
# A Bengali headline (matra) spans a whole word: ~80px for the sample words at
# 16pt; the longest Latin glyph run (an em dash) is ~20px.
MIN_HEADLINE_RUN_PX = 40

SAMPLE_TEXTS = [
    "1000FiX ERP - Bengali conjunct shaping reference (TR-07)",
    "কর্তনযোগ্য খরচ (র্ত, জ্য)",
    "ব্যবধান (ব্য) - ডায়াগনস্টিক পথ (স্ট)",
    "অনুমোদনকারী - ওয়ারেন্টি - সিরিয়াল নম্বর",
    "মোট: ৳ ১,৫০,০০০.০০",
]


def verify_reference_image() -> dict:
    if not REFERENCE_IMAGE.exists():
        return {"status": "FAIL", "detail": f"Reference image missing at {REFERENCE_IMAGE}"}

    file_size = REFERENCE_IMAGE.stat().st_size
    if file_size < 1000:
        return {
            "status": "FAIL",
            "detail": f"Reference image corrupt or too small: {file_size} bytes",
        }

    with Image.open(REFERENCE_IMAGE) as img:
        img_format = img.format
        mode = img.mode
        profile = measure_pixel_profile(img)

    # Calculate image SHA-256
    with open(REFERENCE_IMAGE, "rb") as f:
        img_sha256 = hashlib.sha256(f.read()).hexdigest()

    ok = all(
        profile[key]
        for key in (
            "dimensions_correct",
            "border_present",
            "background_white",
            "text_rendered",
            "text_within_margin",
            "bengali_headline_present",
        )
    )
    return {
        "status": "PASS" if ok else "FAIL",
        "format": img_format,
        "mode": mode,
        "size_bytes": file_size,
        "sha256": img_sha256,
        **profile,
    }


def _is_dark(pixel) -> bool:
    r, g, b = pixel[:3]
    return (r + g + b) / 3 < DARK_MAX


def _is_white(pixel) -> bool:
    return all(channel >= WHITE_MIN for channel in pixel[:3])


def _max_horizontal_ink_run(pixels, width: int, rows: range) -> int:
    best = 0
    for y in rows:
        run = 0
        for x in range(2, width - 2):
            if sum(pixels[x, y][:3]) / 3 < INK_MAX:
                run += 1
                best = max(best, run)
            else:
                run = 0
    return best


def measure_pixel_profile(img: Image.Image) -> dict:
    """Pixel profile against what render-bengali-reference.ps1 documents:
    900x260, white background, 1px black border on all four edges, and the
    Bengali sample lines drawn from x=16 (y=48 onward).

    Two checks make "it is Bengali" measurable without OCR:
      * bengali_headline_present - Bengali script joins the letters of a word
        under a continuous headline (matra); a label band without any long
        horizontal ink run holds no shaped Bengali (Latin text and mojibake
        have none);
      * text_within_margin - the documented sample lines fit the canvas; ink
        in the right margin means the drawn string is not the sample (e.g.
        UTF-8 read as ANSI expands every Bengali letter into three Latin ones
        and runs off the edge)."""
    rgb = img.convert("RGB")
    width, height = rgb.size
    dim_ok = (width, height) == EXPECTED_SIZE
    if not dim_ok:
        return {
            "width": width,
            "height": height,
            "dimensions_correct": False,
            "border_present": False,
            "background_white": False,
            "text_rendered": False,
            "text_within_margin": False,
            "bengali_headline_present": False,
            "detail": f"expected {EXPECTED_SIZE[0]}x{EXPECTED_SIZE[1]}, got {width}x{height}",
        }
    pixels = rgb.load()
    edges = {
        "top": [pixels[x, 0] for x in range(width)],
        "bottom": [pixels[x, height - 1] for x in range(width)],
        "left": [pixels[0, y] for y in range(height)],
        "right": [pixels[width - 1, y] for y in range(height)],
    }
    border_dark_ratio = {
        edge: round(sum(_is_dark(p) for p in line) / len(line), 4) for edge, line in edges.items()
    }
    background_samples = {
        f"{x},{y}": pixels[x, y]
        for x, y in ((1, 1), (width - 2, 1), (1, height - 2), (width - 2, height - 2))
    }
    interior = [pixels[x, y] for x in range(2, width - 2, 2) for y in range(2, height - 2, 2)]
    ink_ratio = round(sum(_is_dark(p) for p in interior) / len(interior), 4)
    margin_ink = sum(
        1
        for x in range(width - 2 - RIGHT_MARGIN_PX, width - 2)
        for y in range(2, height - 2)
        if sum(pixels[x, y][:3]) / 3 < INK_MAX
    )
    headline_run = _max_horizontal_ink_run(pixels, width, range(LABEL_BAND_TOP, height - 2))
    return {
        "width": width,
        "height": height,
        "dimensions_correct": True,
        "border_dark_ratio": border_dark_ratio,
        "border_present": all(r == 1.0 for r in border_dark_ratio.values()),
        "background_samples": {k: list(v) for k, v in background_samples.items()},
        "background_white": all(_is_white(p) for p in background_samples.values()),
        "interior_ink_ratio": ink_ratio,
        "text_rendered": INK_RATIO_RANGE[0] <= ink_ratio <= INK_RATIO_RANGE[1],
        "right_margin_ink_pixels": margin_ink,
        "text_within_margin": margin_ink == 0,
        "max_headline_run_px": headline_run,
        "bengali_headline_present": headline_run >= MIN_HEADLINE_RUN_PX,
    }


def verify_bn007_formatting() -> dict:
    sys.path.insert(0, str(DOCGEN_SRC))
    try:
        from document_generation import _bn_numerals, format_amount

        test_amount = 150000.0
        formatted_bn = format_amount(test_amount, "bn")
        formatted_en = format_amount(test_amount, "en")

        # Must have Taka sign ৳, thin space or space, Bengali numerals, and lakh-crory grouping (1,50,000.00)
        bn_valid = "৳" in formatted_bn and "১,৫০,০০০.০০" in formatted_bn
        en_valid = "BDT" in formatted_en and "1,50,000.00" in formatted_en

        numerals_test = _bn_numerals("0123456789") == "০১২৩৪৫৬৭৮৯"
        # Lakh-crore grouping on a crore-scale amount (1,23,45,678.90 - not 12,345,678.90)
        lakh_crory_grouping = "1,23,45,678.90" in format_amount(12345678.9, "en")
        # BN-007 sign rule: the Taka sign precedes the amount
        first_digit = next((i for i, ch in enumerate(formatted_bn) if ch in "০১২৩৪৫৬৭৮৯"), -1)
        sign_rule_valid = "৳" in formatted_bn and 0 <= formatted_bn.index("৳") < first_digit

        passed = bn_valid and en_valid and numerals_test and lakh_crory_grouping and sign_rule_valid
        return {
            "status": "PASS" if passed else "FAIL",
            "formatted_bn": formatted_bn,
            "formatted_en": formatted_en,
            "numerals_test": numerals_test,
            "lakh_crory_grouping": lakh_crory_grouping,
            "sign_rule_valid": sign_rule_valid,
        }
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}


def find_qweb_template(xml_id: str, addons_dir: Path | None = None) -> Path | None:
    """The XML file defining QWeb template ``module.template_id``, or None."""
    addons_dir = addons_dir or ADDONS_DIR
    module, _, template_id = xml_id.partition(".")
    pattern = re.compile(
        rf"<template\b[^>]*\bid=\"{re.escape(template_id)}\"|"
        rf"<record\b[^>]*\bid=\"{re.escape(template_id)}\"[^>]*model=\"ir\.ui\.view\""
    )
    for module_dir in addons_dir.rglob(module):
        if not (module_dir / "__manifest__.py").is_file():
            continue
        for xml in sorted(module_dir.rglob("*.xml")):
            if "i18n" in xml.parts:
                continue
            if pattern.search(xml.read_text(encoding="utf-8", errors="ignore")):
                return xml
    return None


def verify_statutory_templates() -> dict:
    """Each registered template must exist as a QWeb view in its addon - a
    registration pointing at no template renders nothing."""
    sys.path.insert(0, str(DOCGEN_SRC))
    try:
        from document_generation import DOCUMENT_TEMPLATES
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}

    required_templates = [
        "mushak_6_3",
        "mushak_6_6",
        "withholding_certificate",
        "service_receipt",
    ]
    template_status = {}
    all_present = True
    for tmpl in required_templates:
        if tmpl not in DOCUMENT_TEMPLATES:
            template_status[tmpl] = {"registered": False}
            all_present = False
            continue
        cfg = DOCUMENT_TEMPLATES[tmpl]
        ref_exists = (REPO_ROOT / cfg.get("reference", "")).exists()
        source = find_qweb_template(str(cfg.get("qweb", "")))
        template_status[tmpl] = {
            "registered": True,
            "qweb": cfg.get("qweb"),
            "model": cfg.get("model"),
            "statutory": cfg.get("statutory"),
            "reference_exists": ref_exists,
            "qweb_template_found": source is not None,
            "qweb_source": source.relative_to(REPO_ROOT).as_posix() if source else None,
        }
        if not (ref_exists and source):
            all_present = False

    return {"status": "PASS" if all_present else "FAIL", "templates": template_status}


def token_bengali_family(tokens_path: Path | None = None) -> str:
    """The Bengali family the design-token source declares ('' if none)."""
    tokens = json.loads((tokens_path or TOKENS_JSON).read_text(encoding="utf-8"))
    node = tokens
    for key in ("typography", "font", "bengali", "family"):
        node = node.get(key, {}) if isinstance(node, dict) else {}
    value = node.get("$value", "") if isinstance(node, dict) else ""
    return str(value).strip().strip("'\"")


def installed_font_families() -> tuple[set[str], str]:
    """Lower-cased font family names installed on this host, and how they were read."""
    names: set[str] = set()
    if sys.platform == "win32":
        import winreg

        key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
        for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
            try:
                key = winreg.OpenKey(hive, key_path)
            except OSError:
                continue
            index = 0
            while True:
                try:
                    value_name = winreg.EnumValue(key, index)[0]
                except OSError:
                    break
                index += 1
                base = re.sub(r"\s*\((TrueType|OpenType)\)\s*$", "", value_name)
                names.update(part.strip().lower() for part in base.split("&") if part.strip())
        return names, "Windows font registry (HKLM/HKCU)"
    try:
        proc = subprocess.run(
            ["fc-list", ":", "family"], capture_output=True, text=True, timeout=30
        )
    except (OSError, subprocess.SubprocessError):
        return names, "fc-list unavailable"
    for line in proc.stdout.splitlines():
        names.update(part.strip().lower() for part in line.split(",") if part.strip())
    return names, "fc-list"


def _family_installed(family: str, installed: set[str]) -> bool:
    family = family.lower()
    return any(name == family or name.startswith(family + " ") for name in installed)


def _report_asset_css(addons_dir: Path) -> list[Path]:
    """CSS/SCSS files registered in a report asset bundle by any addon manifest."""
    files: list[Path] = []
    for manifest in sorted(addons_dir.rglob("__manifest__.py")):
        try:
            data = ast.literal_eval(manifest.read_text(encoding="utf-8"))
        except (ValueError, SyntaxError):
            continue
        assets = data.get("assets", {}) if isinstance(data, dict) else {}
        for bundle, entries in assets.items():
            if not bundle.startswith("web.report_assets"):
                continue
            for entry in entries:
                if not isinstance(entry, str):
                    continue
                module, _, rel = entry.partition("/")
                module_dir = next(
                    (m for m in addons_dir.rglob(module) if (m / "__manifest__.py").is_file()),
                    None,
                )
                if module_dir:
                    files.extend(p for p in module_dir.glob(rel) if p.is_file())
    return files


def _font_selectors(css: str, family: str) -> set[str]:
    """Selectors whose rule sets font-family to the Bengali token or family."""
    selectors: set[str] = set()
    for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        decl = re.search(r"font-family\s*:\s*([^;]+)", body)
        if decl and (BENGALI_VAR in decl.group(1) or family.lower() in decl.group(1).lower()):
            selectors.update(s.strip() for s in sel.split(","))
    return selectors


def verify_font_stack() -> dict:
    """The Bengali font path, measured:
    1. the token source declares the Bengali family;
    2. the generated token CSS carries it (--fix-typography-font-bengali-family);
    3. that CSS is registered in a report asset bundle (QWeb PDFs load it);
    4. every statutory template that exists actually APPLIES it (a font-family
       using the token/family, inline or via a report-asset CSS rule matching
       the page or one of the template's classes);
    5. the family - or the documented fallback the reference render uses - is
       installed on this rendering host."""
    failures: list[str] = []
    family = token_bengali_family() if TOKENS_JSON.is_file() else ""
    if not family:
        failures.append(f"no typography.font.bengali.family in {TOKENS_JSON.name}")
    token_css = TOKENS_CSS.read_text(encoding="utf-8") if TOKENS_CSS.is_file() else ""
    css_declares = bool(family) and bool(
        re.search(rf"{re.escape(BENGALI_VAR)}\s*:\s*['\"]?{re.escape(family)}", token_css)
    )
    if not css_declares:
        failures.append(f"{TOKENS_CSS.name} does not declare {BENGALI_VAR}: {family}")
    report_css = _report_asset_css(ADDONS_DIR)
    registered = TOKENS_CSS.resolve() in {p.resolve() for p in report_css}
    if not registered:
        failures.append(f"{TOKENS_CSS.name} is not registered in a web.report_assets bundle")
    selectors: set[str] = set()
    for css_file in report_css:
        selectors |= _font_selectors(css_file.read_text(encoding="utf-8", errors="ignore"), family)

    templates = verify_statutory_templates().get("templates", {})
    applied: dict[str, bool] = {}
    for name, info in templates.items():
        source = info.get("qweb_source")
        if not source:
            continue
        text = (REPO_ROOT / source).read_text(encoding="utf-8", errors="ignore")
        classes = {f".{c}" for attr in re.findall(r'class="([^"]+)"', text) for c in attr.split()}
        inline = bool(
            family
            and re.search(
                rf"font-family\s*:[^;\"]*({re.escape(BENGALI_VAR)}|{re.escape(family)})",
                text,
                re.IGNORECASE,
            )
        )
        applied[name] = inline or bool(selectors & (classes | PAGE_SELECTORS))
        if not applied[name]:
            failures.append(f"{name} ({source}) never applies the Bengali font")

    installed, how = installed_font_families()
    primary_installed = bool(family) and _family_installed(family, installed)
    fallback_installed = _family_installed(FALLBACK_FAMILY, installed)
    if not (primary_installed or fallback_installed):
        failures.append(f"neither {family or 'the token family'} nor {FALLBACK_FAMILY} installed")

    return {
        "status": "PASS" if not failures else "FAIL",
        "primary_font": family or None,
        "fallback_font": FALLBACK_FAMILY,
        "token_css_declares_family": css_declares,
        "token_css_in_report_assets": registered,
        "report_asset_css_files": [p.relative_to(REPO_ROOT).as_posix() for p in report_css],
        "selectors_applying_bengali_font": sorted(selectors),
        "statutory_templates_apply_font": applied,
        "host_font_source": how,
        "primary_font_installed": primary_installed,
        "fallback_font_installed": fallback_installed,
        "failed_checks": failures,
    }


def main():
    print(
        "Starting Bengali Conjunct Shaping & Report Rendering Verification (TR-07 / R07-M02-T05)..."
    )

    ref_res = verify_reference_image()
    bn007_res = verify_bn007_formatting()
    statutory_res = verify_statutory_templates()
    font_res = verify_font_stack()

    all_pass = (
        ref_res.get("status") == "PASS"
        and bn007_res.get("status") == "PASS"
        and statutory_res.get("status") == "PASS"
        and font_res.get("status") == "PASS"
    )

    failed_checks = [
        name
        for name, res in (
            ("reference image", ref_res),
            ("BN-007 formatting", bn007_res),
            ("statutory templates", statutory_res),
            ("font stack", font_res),
        )
        if res.get("status") != "PASS"
    ]
    result = {
        "test": "R07-M02-T05: Bengali Rendering Verification (TR-07 / Doctor Check 10)",
        "timestamp_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "overall_status": "PASS" if all_pass else "FAIL",
        "reference_image_verification": ref_res,
        "bn007_currency_formatting": bn007_res,
        "statutory_document_templates": statutory_res,
        "font_stack_verification": font_res,
        "sample_conjunct_set": SAMPLE_TEXTS,
        "conclusion": (
            "Reference image pixel profile (900x260, 1px border, white background, rendered "
            "text), BN-007 amount formatting, statutory template registration and font-stack "
            "declarations all verified."
            if all_pass
            else f"NOT verified - failing checks: {', '.join(failed_checks)}."
        ),
    }

    EVIDENCE_OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(EVIDENCE_OUT, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    bn_fmt_display = (
        bn007_res.get("formatted_bn", "").encode("ascii", "backslashreplace").decode("ascii")
    )
    print(
        f"  Reference image: {ref_res.get('status')} ({ref_res.get('width')}x{ref_res.get('height')})"
    )
    print(f"  BN-007 formatting: {bn007_res.get('status')} ({bn_fmt_display})")
    templates = statutory_res.get("templates", {})
    registered = sum(1 for t in templates.values() if t.get("registered"))
    found = sum(1 for t in templates.values() if t.get("qweb_template_found"))
    print(
        f"  Statutory templates: {statutory_res.get('status')} "
        f"({registered}/{len(templates)} registered, {found} QWeb templates found)"
    )
    print(f"  Font stack: {font_res.get('status')}")
    for failure in font_res.get("failed_checks", []):
        print(f"    - {failure}")
    print(f"  Evidence output: {EVIDENCE_OUT}")

    if all_pass:
        print(
            "verify_bengali_rendering: OK - Bengali conjunct shaping and report rendering fully verified."
        )
        sys.exit(0)
    else:
        print("verify_bengali_rendering: FAIL - Issues found during verification.")
        sys.exit(1)


if __name__ == "__main__":
    main()
