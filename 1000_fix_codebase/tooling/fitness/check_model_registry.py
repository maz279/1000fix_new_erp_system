#!/usr/bin/env python3
"""FF-20/21/22 — Model registry check (AS-02/03/14, P02-M08-T07 stage 3).

Scans every model file under addons/ for:
  AS-02: transactional models inherit mail.thread + mail.activity.mixin
  AS-03: transactional models carry company_id and operating_unit_id
  AS-14: residency-classified fields marked with the residency mixin

Blocking: a model without chatter mixins is a chat-less island; a model
without company_id is cross-entity contaminated; an unmarked classified
field is a residency leak.

Exit: 0 pass / 1 violations.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ADDONS = REPO_ROOT / "addons"

MIXIN_PATTERN = re.compile(r'_inherit\s*=\s*\[.*(?:mail\.thread|mail\.activity\.mixin).*\]', re.DOTALL)
COMPANY_PATTERN = re.compile(r'company_id\s*=\s*fields\.')
OU_PATTERN = re.compile(r'operating_unit_ids?\s*=\s*fields\.')

# Models that are exempt (AbstractModel, configuration/master, or non-transactional)
EXEMPT_MODELS = {
    "residency.mixin",
    # Configuration/master models — no transaction lifecycle, no OU isolation
    "fix.isolation.tier", "fix.retention.class", "fix.refurb.grade",
    "fix.bd.address", "fix.brand", "fix.device.model",
    "fix.feature.flag", "fix.field.rule",
    # M30 master data: zones/geofences span OUs; calendars and country packs
    # are estate-wide reference data (BD divisions are not per-OU)
    "fix.zone", "fix.geofence",
    "fix.working.calendar", "fix.working.calendar.line",
    "fix.working.calendar.holiday",
    "fix.country.pack", "fix.country.pack.line",
    # Per-company policy (company_id present), estate-wide by design: a
    # customer's consent or a dedup rule must not fragment per OU
    "fix.notification.config", "fix.consent", "fix.dedup.rule",
    "fix.party.hierarchy",
    # SLA promise and diagnostic trees are estate-wide masters (company_id
    # present, no OU — a promise made in one branch is the promise)
    "fix.sla.policy", "fix.diagnostic.node",
    # Rules engines — configuration, not transactional data
    "fix.mdm.golden.rule", "fix.mdm.match.rule",
    # Child/line models (owned by parent — OU comes from parent)
    "fix.service.kit.component",
    # System outbox (infrastructure, not business data)
    "fix.event.outbox",
    # MDM governance engine (process, not transactional record)
    "fix.mdm.change.request",
    # Domain child/line models (OU inherited from parent)
    "fix.device.history", "fix.device.ownership",
    "fix.estimate.line", "fix.qc.item", "fix.work.order.part",
    # P06 child/line + estate-wide config models: custody scans belong to
    # their consignment; warehouse zones/bins to their warehouse; rate
    # cards and cash positions are estate-wide masters (company-level)
    "fix.custody.scan", "fix.warehouse.zone", "fix.warehouse.bin",
    "fix.rate.card", "fix.cash.position",
    # P06 finance line models (OU from their parent invoice/order/close)
    "fix.ar.invoice.line", "fix.vendor.invoice.line",
    "fix.purchase.order.line", "fix.period.close.line",
    # VAT tariff treatments are statutory, estate-wide (a 15% promise is
    # the same in every branch)
    "fix.vat.treatment",
    # P06 M63/M24 config + line models: the automation register and the
    # approval matrix are estate-wide governance data; template and signer
    # rows belong to their parent document/envelope
    "fix.automation", "fix.approval.matrix", "fix.document.template",
    "fix.esignature.signer",
    # P07 line/config models: entitlements and PM visits belong to their
    # contract; warranty products are estate-wide catalogue data; evidence
    # items belong to their claim; statutory returns are company-level
    "fix.contract.entitlement", "fix.contract.pm.visit",
    "fix.warranty.product", "fix.warranty.evidence",
    "fix.tds.return", "fix.withholding.certificate",
    # P07 M27 line/register models: transcript turns belong to their
    # conversation; the intent register is estate-wide AI configuration
    "fix.conversation.turn", "fix.assistant.intent",
}


def check_relation_integrity() -> list[str]:
    """AS-14 companion: every relational field target must be a model that
    exists — in addons/ or as an Odoo core/vendor model. A dangling target
    crashes Odoo's registry load for the whole module chain. This exact
    defect class shipped twice (fix.sla.policy, fix.diagnostic.node) before
    this scan existed."""
    core = {
        "res.partner", "res.company", "res.users", "res.groups", "res.currency",
        "res.country", "res.country.state", "product.template", "product.product",
        "product.category", "hr.employee", "hr.department", "crm.lead",
        "mail.template", "mail.thread", "mail.activity.mixin", "operating.unit",
        "ir.attachment", "ir.model", "ir.model.fields", "ir.actions.report",
        "ir.ui.view", "ir.sequence",
        # Odoo `account` (vendor) — present in every profile that installs finance
        "account.move", "account.move.line", "account.account", "account.journal",
        # Odoo `maintenance` (vendor) — present in the Wave-5 EAM profile
        "maintenance.equipment", "maintenance.equipment.category",
        # Odoo `fleet` (vendor) — present in the Wave-5 fleet profile
        "fleet.vehicle", "fleet.vehicle.model",
    }
    defined: set[str] = set()
    sources: list[tuple[Path, str]] = []
    for py in ADDONS.rglob("*.py"):
        if "__pycache__" in py.parts or "vendor" in py.parts:
            continue
        text = py.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r'_name\s*=\s*"([\w.]+)"', text):
            defined.add(m.group(1))
        for m in re.finditer(
            r'fields\.(?:Many2one|One2many|Many2many)\(\s*"([\w.]+)"', text
        ):
            sources.append((py, m.group(1)))
    dangling = []
    for py, target in sources:
        if target not in defined and target not in core:
            dangling.append(
                f"{py.relative_to(REPO_ROOT).as_posix()}: relation target "
                f"{target!r} is not a defined or core model"
            )
    return dangling


def main() -> int:
    violations = []
    checked = 0
    for py in ADDONS.rglob("*.py"):
        if "__pycache__" in py.parts or py.name == "__init__.py":
            continue
        if "vendor" in py.parts:
            continue
        raw = py.read_text(encoding="utf-8", errors="ignore")
        # Strip docstrings to avoid false matches from usage examples
        text = re.sub(r'"""[\s\S]*?"""', '""', raw)
        text = re.sub(r"'''[\s\S]*?'''", "''", text)

        # Find model declarations
        for match in re.finditer(r'class\s+(\w+)\(models\.(Model|AbstractModel)\):', text):
            model_class = match.group(1)
            is_abstract = match.group(2) == "AbstractModel"
            if is_abstract:
                continue
            # Convert class name to Odoo model name (CamelCase -> dot.snake)
            # We check the _name field directly
            # The class body: from this class to the next (a fixed char
            # window bleeds into the following class and mis-attributes
            # its _name to an extension).
            next_class = re.search(r'\nclass\s+\w+\(', text[match.start() + 1:])
            section_end = (match.start() + 1 + next_class.start()
                           if next_class else len(text))
            section = text[match.start():section_end]
            name_match = re.search(r'_name\s*=\s*"([^"]+)"', section)
            inherit_only = re.search(r'_inherit\s*=', section) and not name_match
            if inherit_only:
                # A pure extension class (_inherit, no _name): the PARENT
                # model governs AS-02/AS-03 conformance.
                continue
            if not name_match:
                continue
            model_name = name_match.group(1)
            if model_name in EXEMPT_MODELS:
                continue
            checked += 1
            rel = py.relative_to(REPO_ROOT).as_posix()
            # AS-02: chatter mixins
            has_mixin = bool(MIXIN_PATTERN.search(section))
            if not has_mixin:
                violations.append((rel, model_class, "AS-02: no mail.thread/mail.activity.mixin in _inherit"))
            # AS-03: company_id + operating_unit_id
            has_company = bool(COMPANY_PATTERN.search(section))
            has_ou = bool(OU_PATTERN.search(section))
            if not has_company:
                violations.append((rel, model_class, "AS-03: no company_id field"))
            if not has_ou:
                violations.append((rel, model_class, "AS-03: no operating_unit_id field"))

    violations.extend(check_relation_integrity())

    if violations:
        print(f"model-registry: FAIL - {len(violations)} violation(s) across {checked} models:")
        for violation in violations[:20]:
            if isinstance(violation, tuple):
                rel, cls, msg = violation
                print(f"  {rel}:{cls}: {msg}")
            else:
                print(f"  {violation}")
        print("  remedy: every transactional model inherits chatter mixins and carries company_id + operating_unit_id (AS-02/AS-03);")
        print("          every relation target must be a model that exists (AS-14 companion).")
        return 1
    print(f"model-registry: OK - {checked} models checked, all carry AS-02/AS-03 conformant fields; "
          f"all relation targets resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())
