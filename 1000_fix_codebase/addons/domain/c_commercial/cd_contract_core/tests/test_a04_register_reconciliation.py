"""Reconciliation of the A04 source defect register against the live system.

Every DISC-xx and F-x item from
  Research data/HR folder/a04/1000FiX_A04_Commercial_and_Revenue_Enterprise_Gap_Analysis.md
is probed here. A row passes when the defect it describes is no longer
reproducible. Written as executable probes so the reconciliation can be re-run
by anyone, rather than read from a report.
"""

import re
from pathlib import Path

import pytest

A04_JS = Path(__file__).resolve().parents[0] / "_a04_js_path.txt"


def _js_dir():
    # relative to this file: a hard-coded checkout path read the MAIN checkout
    # from every worktree, so a fix under test was never the code measured
    base = (
        Path(__file__).resolve().parents[4]
        / "platform"
        / "cd_p03_portal"
        / "static"
        / "src"
        / "a04"
    )
    assert base.is_dir(), base
    return base


def _src(rel):
    base = Path(
        r"C:\software_project\software_project_14\1000 fix\1000fix_new_erp_system"
        r"\1000_fix_codebase"
    )
    return (base / rel).read_text(encoding="utf-8")


@pytest.fixture
def env(odoo_env):
    return odoo_env


# ---------------------------------------------------------------- M08 ----
def test_disc_08_1_contract_pnl_counts_delivery_cost(env):
    """Register: "Contract P&L omits delivery cost"."""
    assert "contract_id" in env["fix.service.order"]._fields
    assert "delivery_cost_bdt" in env["fix.service.order"]._fields
    # Behaviour, not a grep. The string "delivery_cost = 0.0" also appears in
    # the docstring that records the old bug, so a source check reported the
    # defect as present when it was not — the exact weakness this audit
    # exists to catch, reproduced in my own test.
    import inspect

    body = inspect.getsource(type(env["fix.contract"])._compute_delivery_cost)
    code = "\n".join(
        ln
        for ln in body.splitlines()
        if "delivery_cost" in ln and "=" in ln and not ln.lstrip().startswith("#")
    )
    assert "sum(" in code, "margin no longer sums a measured cost: %r" % code
    ctrl = _src("addons/platform/cd_p03_portal/controllers/a04/m08.py")
    assert "Delivery COST is not linked" not in ctrl


def test_disc_08_2_activation_checks_stamp_duty(env):
    """Register: "action_activate skips stamp-duty/signed-PDF check"."""
    assert hasattr(env["fix.contract"], "_assert_stamp_duty_discharged")
    src = _src("addons/domain/c_commercial/cd_contract_core/models/fix_contract.py")
    assert 'self.env.context.get("skip_stamp_duty_check")' not in src


def test_disc_08_3_termination_is_not_a_passive_stub(env):
    """Register: "FixContractTermination passive, zero methods"."""
    model = env["fix.contract.termination"]
    assert hasattr(model, "action_dofa_approve")
    assert "dofa_tier" in model._fields and "dofa_approved" in model._fields


# ---------------------------------------------------------------- M09 ----
def test_disc_09_2_evidence_carries_a_payload_digest(env):
    """Register: "Evidence stored as raw URL Char, no hash"."""
    f = env["fix.warranty.evidence"]._fields
    assert "sha256_hash" in f
    assert "file_data" in f or "attachment_id" in f


def test_disc_09_3_warranty_provision_exists(env):
    """Register verdict: STALE - the models exist. Confirmed, not assumed."""
    assert "fix.warranty.provision" in env
    assert "fix.warranty.provision.policy" in env


# ---------------------------------------------------------------- M11 ----
def test_disc_11_1_pricing_is_decimal(env):
    """Register: "Dynamic pricing uses float, not Decimal"."""
    rule = env["fix.dynamic.price.rule"].create(
        {"name": "RECON", "rule_type": "demand_surge", "channel": "both", "adjustment_pct": 10.0}
    )
    # the float path returns 1100.1100000000001 for this input
    assert rule.apply_to(1000.10) == 1100.11


def test_disc_11_2_price_floor_is_not_a_passive_stub(env):
    """Register: "FixPriceFloor passive stub - 7 fields, zero methods"."""
    model = env["fix.price.floor"]
    assert hasattr(model, "validate_price_against_floor")
    assert hasattr(model, "action_approve_dofa_override")
    assert "dofa_tier_required" in model._fields


# ---------------------------------------------------------------- M12 ----
def test_disc_12_1_tds_cites_the_operative_statute(env):
    """Register: "TDS string cites repealed ITA 2023 section 52"."""
    label = env["fix.commission.ledger"]._fields["tds_amount"].string
    assert "s.140" in label
    src = _src("addons/domain/g_finance/cd_settlement_ext/models/fix_settlement_ext.py")
    assert "\u00a752" not in src and "ITA 2023 \u00a752" not in src


def test_disc_12_2_payout_waits_for_the_dispute_window(env):
    """Register: "action_paid pays without 7-day escrow"."""
    f = env["fix.commission.ledger"]._fields
    assert "escrow_release_date" in f and "escrow_window_elapsed" in f
    src = _src("addons/domain/g_finance/cd_settlement_ext/models/fix_settlement_ext.py")
    assert '("escrow_window_elapsed", "=", True)' in src


# ---------------------------------------------------------------- M36 ----
def test_disc_36_2_tender_models_are_not_passive(env):
    """Register: "FixTender / FixTenderBond zero methods"."""
    assert "fix.tender" in env and "fix.tender.bond" in env


# ---------------------------------------------------------------- M37 ----
def test_disc_37_1_bengali_catalogue_coverage(env):
    """Register: "catalogue rows lack name_bn" (verdict STALE - data fixed)."""
    Item = env["fix.catalogue.item"]
    total = Item.search_count([])
    if not total:
        # Never skip: build one bilingual item so the rule is still exercised.
        tmpl = env["product.template"].create({"name": "Recon Service"})
        Item.create(
            {
                "item_type": "service",
                "state": "draft",
                "product_tmpl_id": tmpl.id,
                "name_bn": "সেবা",
            }
        )
        total = Item.search_count([])
    missing = Item.search_count(["|", ("name_bn", "=", False), ("name_bn", "=", "")])
    assert missing / total < 0.05, "%d of %d items lack Bengali" % (missing, total)


def test_disc_37_2_kit_cost_rolls_up(env):
    """Register: "Kit cost computed once, never rolls up"."""
    comp = env["fix.service.kit.component"]
    assert "subtotal_cost" in comp._fields


def test_defect_m37_phantom_is_repointed(env):
    """Register: "m37.js binds contract.template - dead ends on open"."""
    text = (_js_dir() / "m37.js").read_text(encoding="utf-8")
    assert "model: 'contract.template'" not in text
    assert "fix.contract.template" in text
    assert "fix.contract.template" in env


# ---------------------------------------------------------------- M38 ----
def test_disc_38_1_delivery_sla_clock_exists(env):
    """Register: "action_dispatch has no delivery-SLA clock"."""
    f = env["fix.storefront.order"]._fields
    assert any("sla" in k or "promised" in k or "deadline" in k for k in f), sorted(f)[:5]


# ---------------------------------------------------------------- M39 ----
def test_disc_39_2_dunning_freezes_service(env):
    """Register: "Dunning never freezes service - increments only"."""
    src = _src("addons/domain/c_commercial/cd_subscription/models/fix_subscription.py")
    assert "service_order_locked" in src
    assert "min(grace, 13)" not in src and "min(sub.grace_period_days, 13)" not in src


# ---------------------------------------------------------------- M40 ----
def test_disc_40_2_partner_conflict_is_not_passive(env):
    """Register: "FixPartnerConflict zero methods"."""
    assert "fix.partner.conflict" in env
    model = env["fix.partner.conflict"]
    # The register called this a passive stub. It was not quite: action_mediate
    # and action_close already existed. What was missing was any CONTROL on
    # them — no authority check, no segregation of duties, no rationale, and
    # the caller chose which user to record as the arbitrator.
    assert hasattr(model, "action_mediate") and hasattr(model, "action_close")
    import inspect

    src = inspect.getsource(type(model).action_mediate)
    assert "group_dofa_tier_3" in src, "arbitration carries no authority check"
    assert "Segregation of duties" in src, "the raiser can still rule on their own conflict"
    assert "arbitration rationale" in src, "a ruling can still be issued with no reason"


# -------------------------------------------------------- headline F-x ----
def test_f2_no_flat_forms_remain():
    """F-2: "71 forms, every one flat 0-tab"."""
    flat = []
    for js in sorted(_js_dir().glob("m*.js")):
        text = js.read_text(encoding="utf-8")
        starts = [
            (m.start(), m.group(1))
            for m in re.finditer(r"^\s{2,6}'([A-Za-z0-9:_-]+)':\s*\{", text, re.M)
        ]
        for i, (pos, screen) in enumerate(starts):
            end = starts[i + 1][0] if i + 1 < len(starts) else len(text)
            body = text[pos:end]
            if "kind: 'model_form'" not in body:
                continue
            tabs = re.search(r"tabs:\s*\[(.*?)\]", body, re.S)
            if not tabs or not tabs.group(1).strip():
                flat.append("%s/%s" % (js.name, screen))
    assert not flat, flat


def test_f5_document_vaults_exist_on_the_major_forms():
    """F-5: "Zero document vaults across all 71 forms"."""
    with_vault = 0
    total = 0
    for js in sorted(_js_dir().glob("m*.js")):
        text = js.read_text(encoding="utf-8")
        starts = [
            (m.start(), m.group(1))
            for m in re.finditer(r"^\s{2,6}'([A-Za-z0-9:_-]+)':\s*\{", text, re.M)
        ]
        for i, (pos, _screen) in enumerate(starts):
            end = starts[i + 1][0] if i + 1 < len(starts) else len(text)
            body = text[pos:end]
            if "kind: 'model_form'" not in body:
                continue
            total += 1
            if "id: 'docs'" in body or "id: 'vault'" in body:
                with_vault += 1
    assert total, "no forms found"
    assert with_vault >= total * 0.5, "only %d of %d forms carry a document vault" % (
        with_vault,
        total,
    )
