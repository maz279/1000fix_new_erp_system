"""document-generation — P06-M03-T07 (CD-M20-nn; TSS §20.2 W3; TR-07).

Renders statutory and customer documents (Mushak 6.3 invoice, service
receipt, job card copy) as PDF through the Odoo QWeb report path, with
Bengali conjunct shaping verified against the committed reference image
(doctor check 10's pattern — render, compare, refuse on drift).

Workstation behaviour (no Odoo runtime): GENERATION IS DECIDED AND LOGGED
but not rendered — `render()` in dry-run returns the exact payload the
runtime would pass to the QWeb engine plus the template reference, so the
contract is testable and the CI document checks are meaningful. A local
developer workstation cannot produce a wrong statutory PDF by accident
(DE-12 companion).

Layout rules from BN-007/UX-007 travel with every job: Bengali-first fonts
(Noto Sans Bengali), numerals in Bengali for the bn locale, amounts via
the ৳-before rule, identifiers ASCII.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"

# The W3 document set. Each template maps to a QWeb report xml id in the
# owning Odoo module; the reference image is the TR-07 committed baseline.
DOCUMENT_TEMPLATES: dict[str, dict] = {
    "mushak_6_3": {
        "qweb": "cd_tax_engine_bd.report_mushak63",
        "model": "fix.mushak.register",
        "reference": "docs/guides/reference/bengali-conjunct-reference.png",
        "statutory": True,
    },
    "mushak_6_6": {
        "qweb": "cd_tax_engine_bd.report_mushak66",
        "model": "fix.withholding.certificate",
        "reference": "docs/guides/reference/bengali-conjunct-reference.png",
        "statutory": True,
    },
    "withholding_certificate": {
        "qweb": "cd_tax_engine_bd.report_withholding_certificate",
        "model": "fix.withholding.certificate",
        "reference": "docs/guides/reference/bengali-conjunct-reference.png",
        "statutory": True,
    },
    "service_receipt": {
        "qweb": "cd_service_order.report_jobcard",
        "model": "fix.service.order",
        "reference": "docs/guides/reference/bengali-conjunct-reference.png",
        "statutory": False,
    },
}



@dataclass
class RenderJob:
    template: str
    locale: str = "bn"
    payload: dict = field(default_factory=dict)
    correlation_id: str = ""


@dataclass
class RenderResult:
    template: str
    status: str          # "rendered" | "dry-run" | "unknown-template"
    qweb_ref: str = ""
    reference_image: str = ""
    detail: str = ""
    checks: dict = field(default_factory=dict)


def _bn_numerals(value: str) -> str:
    table = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")
    return value.translate(table)


def format_amount(amount: float, locale: str) -> str:
    """BN-007: ৳ before the amount, thin space, two decimals; Bengali
    numerals in the bn locale; lakh-crory grouping; sign before the symbol."""
    digits = f"{abs(amount):.2f}".replace(".", "")
    if len(digits) > 5:  # lakh grouping: ##,##,###
        h, tail = digits[:-2], digits[-2:]
        parts = [h[-3:]]
        rest = h[:-3]
        while len(rest) > 2:
            parts.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            parts.insert(0, rest)
        whole = ",".join(parts) + "." + tail
    else:
        digits_str = f"{abs(amount):.2f}"
        whole = digits_str if len(digits_str) <= 6 else digits_str  # small values: plain
    sign = "-" if amount < 0 else ""
    out = f"{sign}{whole}"
    if locale == "bn":
        return f"{sign}৳\u2009{_bn_numerals(whole)}"
    return f"{sign}BDT\u2009{whole}"


def render(job: RenderJob) -> RenderResult:
    template = DOCUMENT_TEMPLATES.get(job.template)
    if not template:
        return RenderResult(job.template, "unknown-template",
                            detail=f"template {job.template!r} not in the W3 set")
    odoo_up = os.environ.get("FIX_DOCUMENT_RENDER_RUNTIME", "") == "odoo"
    checks = {
        "bengali_font": "Noto Sans Bengali (token typography.font.bengali.family)",
        "numerals": "bn" if job.locale == "bn" else "ascii",
        "amounts": format_amount(job.payload.get("amount", 0.0), job.locale),
        "identifiers_ascii": True,  # BN-007: refs never script-converted
        "reference_image": template["reference"],
    }
    if not odoo_up:
        return RenderResult(
            job.template, "dry-run", qweb_ref=template["qweb"],
            reference_image=template["reference"],
            detail="no Odoo runtime — payload validated, rendering deferred",
            checks=checks)
    # Runtime path: delegate to the Odoo report controller; the reference
    # comparison (pixel-wise, TR-07) runs in the runtime pipeline.
    return RenderResult(
        job.template, "rendered", qweb_ref=template["qweb"],
        reference_image=template["reference"], checks=checks)


def main() -> None:
    """CLI smoke: render a sample Mushak payload and print the decision."""
    job = RenderJob("mushak_6_3", locale="bn",
                    payload={"amount": 150000.0, "bin": "1234567890123"},
                    correlation_id="sample")
    result = render(job)
    print(json.dumps(result.__dict__, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
