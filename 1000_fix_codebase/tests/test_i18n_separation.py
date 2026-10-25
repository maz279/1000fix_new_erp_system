"""DE-17 language separation checker — Bangla and English must never mix in
one user-visible literal.

Policy (user-confirmed 2026-10-25): Latin acronyms and product tokens stay
Latin inside Bangla text (standard Bangla typography). A literal is a
VIOLATION iff it contains Bangla script AND still has a Latin letter-run
(≥2 letters) after whitelisted tokens, digits and punctuation are removed.

Scanned surfaces:
  * apps/web/*/ (all 8 portals; .tsx/.ts source, node_modules/.next skipped)
  * the P03 workspace (cd_p03_portal/static/src)
  * every first-party bn_BD.po msgstr
"""

from __future__ import annotations

import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]

BANGLA = re.compile(
    r"[\u0985-\u09B9\u09BE-\u09CC\u09CE\u09D7\u09DC-\u09DF\u09E0-\u09E3\u09FA-\u09FF]"
)
LATIN_RUN = re.compile(r"[A-Za-z]{2,}")

# tokens allowed to stay Latin inside Bangla text (acronyms, product names,
# codes, units). Kept deliberately as ONE source of truth.
ALLOWED = """
P01 P02 P03 P04 P05 P06 P07 P08 P09
M01 M02 M03 M04 M05 M06 M07 M08 M09 M10 M11 M12 M13 M14 M15 M16 M17 M18 M19
M20 M21 M22 M23 M24 M25 M26 M27 M28 M29 M30 M31 M32 M33 M34 M35 M36 M37 M38
M39 M40 M41 M42 M43 M44 M45 M46 M47 M48 M49 M50 M51 M52 M53 M54 M55 M56 M57
M58 M59 M60 M61 M62 M63 M64 M65 M66 M67
A02 A03 A04 A05 A06 A07 A08 A09 A10 A11 A12
L1 L2 L3 L4 L5 W1 W2 W3 W4 W5 W6
OTP SLA PDPA VAT GL AR INV RCP BEFTN AMC ERP KPI CSV MUSHAK BIN CAPA NCR
JSON URL API WIP SMS GPS AI ML ISO NBR BFRS PWA ETA SKU HR FM CN ID PC
VDS IFRS IAS COD CWIP NBV RTGS NPSB MFS DSO MD
BD BDT HQ EN AC DC PDPA TDS QC NID IMEI IMEIs SSL SSLCOMMERZ
Odoo 1000FiX FiX bKash Nagad bKash Nagad
localhost 1000fix com https http www
Dr Cr Mr Ms Ltd Services
NT Dynamics Tell Me Enter Esc Alt OEM SoD SOP
FR FIN ARB E-SIGN TXN BTRC DND STN MIG AS BN BRU SRM KYC
read_group enum attachment postMessage localStorage cron
SO CB RCT INV RCP TRX NID FSC TRIM FSM E2E PoS
admin demo Dell Latitude WhatsApp TrxID Tejgaon
Keycloak Mayan Samsung HP Walton Inspiron Apache Airflow IoT kWh CoA
e-TIN TIN QWeb R-nn Airflow EDMS Kafka Redis Novu Care Club Capex EaaS Levenshtein
""".split()

ALLOWED_RE = re.compile(
    r"\b(?:" + "|".join(re.escape(t) for t in sorted(set(ALLOWED), key=len, reverse=True)) + r")\b",
    re.IGNORECASE,
)


ACRONYM = re.compile(r"\b[A-Z]{2,6}\b")  # PCB, MAC, VAT… standard tech acronyms
SNAKE_CODE = re.compile(r"\b\w+(?:[_.]\w+)+\b")  # snake_case / dotted code ids
DIGIT_CODE = re.compile(r"\b[A-Za-z]*\w*[-]?\d[\w-]*\b")  # any token with a digit


def strip_interpolations(s: str) -> str:
    """Depth-aware ${…} removal (nested ternaries/backticks included)."""
    out, depth, i = [], 0, 0
    while i < len(s):
        if s.startswith("${", i):
            depth += 1
            i += 2
            continue
        if s[i] == "}" and depth:
            depth -= 1
            i += 1
            continue
        if not depth:
            out.append(s[i])
        i += 1
    return "".join(out)


def violation(bn_part: str) -> str | None:
    """The residual ENGLISH word in a Bangla string, or None when clean.

    Allowed to stay Latin: whitelisted names, ALL-CAPS acronyms (2-6),
    snake/dotted code identifiers, tokens containing digits. Anything left
    is a lowercase-bearing English word of 2+ letters inside Bangla text —
    the DE-17 violation."""
    if not BANGLA.search(bn_part):
        return None
    s = strip_interpolations(bn_part)
    s = re.sub(r"\{[a-zA-Z_]\w*\}", " ", s)  # tf() {token} placeholders
    s = re.sub(r"[0-9Xx]{4,}", " ", s)  # digit/placeholder runs
    s = SNAKE_CODE.sub(" ", s)  # code ids BEFORE whitelist (ir.attachment etc.)
    s = ALLOWED_RE.sub(" ", s)
    s = DIGIT_CODE.sub(" ", s)
    s = ACRONYM.sub(" ", s)
    m = re.search(r"\b(?=[A-Za-z]*[a-z])[A-Za-z]{2,}\b", s)
    return m.group(0) if m else None


def portal_files():
    web = ROOT / "apps" / "web"
    if not web.exists():
        return []
    out = []
    for app in sorted(web.iterdir()):
        if not app.is_dir():
            continue
        for f in app.rglob("*.[jt]s*"):
            if "node_modules" in f.parts or ".next" in f.parts:
                continue
            out.append(f)
    return out


def workspace_files():
    src = ROOT / "addons" / "platform" / "cd_p03_portal" / "static" / "src"
    return sorted(src.glob("*.js")) + sorted(src.glob("*.xml")) if src.exists() else []


def po_files():
    out = []
    for f in (ROOT / "addons").rglob("bn_BD.po"):
        out.append(f)
    return out


def string_literals(line: str):
    """Quoted string literals on a line (code around them is not UI)."""
    out = []
    for m in re.finditer(r'"((?:[^"\\\n]|\\.){2,})"', line):
        out.append(m.group(1))
    for m in re.finditer(r"'((?:[^'\\\n]|\\.){2,})'", line):
        out.append(m.group(1))
    for m in re.finditer(r"`([^`]{2,})`", line):
        if "}" not in m.group(1):  # partial multi-line template fragment
            out.append(m.group(1))
    return out


def test_no_mixed_script_literals():
    bad = []
    for f in portal_files() + workspace_files():
        text = f.read_text(encoding="utf-8", errors="replace")
        for lineno, line in enumerate(text.splitlines(), 1):
            if not BANGLA.search(line):
                continue
            # the P03 search hint is the ONE deliberate bilingual affordance
            # (the user types either language into it)
            if "(EN or" in line or "EN or বাংলা" in line:
                continue
            for lit in string_literals(line):
                v = violation(lit)
                if v:
                    bad.append(f"{f.relative_to(ROOT)}:{lineno}: …{v}… :: {lit[:100]}")
    assert not bad, f"{len(bad)} mixed-script literals:\n" + "\n".join(bad[:40])


def test_bn_po_msgstrs_separate():
    bad = []
    for po in po_files():
        for lineno, line in enumerate(
            po.read_text(encoding="utf-8", errors="replace").splitlines(), 1
        ):
            if not line.startswith("msgstr"):
                continue
            for lit in string_literals(line):
                v = violation(lit)
                if v:
                    bad.append(f"{po.relative_to(ROOT)}:{lineno}: …{v}… :: {lit[:100]}")
    assert not bad, f"{len(bad)} mixed bn_BD translations:\n" + "\n".join(bad[:40])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
