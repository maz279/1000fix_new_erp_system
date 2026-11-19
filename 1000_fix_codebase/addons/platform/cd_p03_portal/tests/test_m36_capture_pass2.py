# M36 Quotations & Tenders, capture audit second pass (2026-11-19).
#
# After the first pass every page had a "+ New", but read against the spec
# (§5 FR-QTE-001..048, §9 BRU-QTE-01..18, §10.1) these records had nowhere to
# be captured (HEAD 742e46bc, evaluated with the engine's own fregPanels):
#   p1  the technical review / second opinion of an estimate      FR-QTE-009
#   p2  the terms of a quotation from a governed library          FR-QTE-018
#       a renewal quotation from an expiring contract             FR-QTE-024
#   p4  the CCO + CFO decision on a non-standard term             FR-QTE-027
#       Finance's override of the credit gate                     FR-QTE-028
#   p5/7 acceptance on a recorded phone call                      FR-QTE-042
#   p7  the legal hold on a disputed quotation                    BRU-QTE-17
#   p9  the tender document checklist                             FR-QTE-046
#       the outcome of a lost tender with a governed reason       FR-QTE-048
#   p10 the standard terms library itself                         FR-QTE-018
# This guard reuses the first pass's node evaluation of the real registry.
from __future__ import annotations

import ast
import importlib.util
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
QUOTATION = HERE.parents[2] / "domain" / "c_commercial" / "cd_quotation"

_spec = importlib.util.spec_from_file_location("_m36_pass1", HERE / "test_m36_capture_buttons.py")
_p1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_p1)

m36 = _p1.m36  # the module-scoped fixture: node runs fregCreate / fregPanels

# What each page must now ALSO capture (by form screen).
PASS2 = {
    "1": ["M36-form-est-review", "M36-form-est-review-decide"],
    "2": ["M36-form-term", "M36-form-renewal"],
    "4": ["M36-form-term-decide", "M36-form-credit-override"],
    "5": ["M36-form-phone"],
    "7": ["M36-form-phone", "M36-form-legal-hold", "M36-form-hold-release"],
    "9": ["M36-form-tender-doc", "M36-form-tender-outcome"],
    "10": ["M36-form-std-term"],
}

# The spec entity each new capture writes.
MODELS = {
    "M36-form-est-review": "fix.estimate.review",
    "M36-form-est-review-decide": "fix.estimate.review",
    "M36-form-term": "fix.quotation.term",
    "M36-form-renewal": "fix.quotation",
    "M36-form-term-decide": "fix.quotation.term",
    "M36-form-credit-override": "fix.quotation.credit.override",
    "M36-form-phone": "fix.quotation",
    "M36-form-legal-hold": "fix.quotation.legal.hold",
    "M36-form-hold-release": "fix.quotation.legal.hold",
    "M36-form-tender-doc": "fix.tender.document",
    "M36-form-tender-outcome": "fix.tender.outcome",
    "M36-form-std-term": "fix.quotation.standard.term",
}

# Decisions on an existing record run their workflow method, never a write.
PICK_ACTIONS = {
    "M36-form-est-review-decide": (
        "action_decide",
        {"decision_choice", "findings_entry"},
        ["state", "=", "requested"],
    ),
    "M36-form-term-decide": (
        "action_decide_deviation",
        {"decision_choice", "decision_note"},
        ["deviation_state", "=", "pending"],
    ),
    "M36-form-phone": (
        "action_record_phone_acceptance",
        {"phone_consent_ref", "phone_called_number"},
        ["state", "=", "sent"],
    ),
    "M36-form-hold-release": ("action_release", {"release_note"}, ["state", "=", "active"]),
}

NEW_MODELS = (
    "fix.quotation.standard.term",
    "fix.quotation.term",
    "fix.quotation.credit.override",
    "fix.quotation.legal.hold",
    "fix.estimate.review",
    "fix.tender.document",
    "fix.tender.outcome",
)

# Who records what; nobody types an approval, a stamp or a decision.
STAMPS = {
    "fix.quotation.term": {
        "is_standard",
        "deviation_state",
        "recorded_by_id",
        "commercial_approver_id",
        "commercial_approved_at",
        "finance_approver_id",
        "finance_approved_at",
        "rejected_by_id",
        "rejection_note",
    },
    "fix.quotation.credit.override": {
        "version",
        "amount_total",
        "block_reason",
        "granted_by_id",
        "granted_at",
        "revoked",
    },
    "fix.quotation.legal.hold": {
        "state",
        "version",
        "placed_by_id",
        "placed_at",
        "released_by_id",
        "released_at",
        "release_reason",
    },
    "fix.estimate.review": {"state", "requested_by_id", "findings", "decided_at"},
    "fix.tender.document": {"state", "version", "checksum", "prepared_by_id"},
    "fix.tender.outcome": {"our_value", "price_gap_pct", "recorded_by_id"},
    "fix.tender": {"loss_reason_code", "submission_pack_hash", "awarded_to", "winning_value"},
    "fix.quotation": {"acceptance_method", "legal_hold", "credit_block_reason"},
}


@pytest.mark.parametrize("no", sorted(PASS2, key=int))
def test_each_page_captures_the_spec_records_it_is_about(m36, no):
    sub = _p1._sub(m36, no)
    chips = {f["id"] for f in sub["forms"] if f["opens"]}
    missing = [form for form in PASS2[no] if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)


def test_each_new_capture_writes_its_spec_entity(m36):
    for sid, model in MODELS.items():
        assert m36["screens"][sid]["model"] == model, sid


def test_each_new_record_is_listed_on_the_page_that_captures_it(m36):
    for no, forms in PASS2.items():
        sub = _p1._sub(m36, no)
        listed = {m36["screens"][s]["model"] for s in sub["screens"] if s in m36["screens"]}
        for sid in forms:
            assert MODELS[sid] in listed, "page %s captures %s but lists none" % (no, sid)


@pytest.mark.parametrize("sid", sorted(PICK_ACTIONS))
def test_decisions_run_the_workflow_not_a_write(m36, sid):
    cfg = m36["screens"][sid]
    method, inputs, clause = PICK_ACTIONS[sid]
    assert cfg["kind"] == "model_form" and cfg["pick"], sid
    assert clause in cfg["pick"]["domain"], sid
    assert cfg["save"] and cfg["save"]["method"] == method, sid
    assert method in _p1._surfaces()[cfg["model"]], "%s is not served" % method
    assert set(cfg["save"]["kwargs"].values()) == inputs, sid
    typed = {f["name"] for f in cfg["fields"] if not f["readonly"]}
    assert not typed, "%s lets %s be written directly" % (sid, sorted(typed))


def test_new_records_are_served_with_their_actions():
    served = _p1._surfaces()
    for model in NEW_MODELS:
        assert model in served, model
    assert "action_decide_deviation" in served["fix.quotation.term"]
    assert "action_revoke" in served["fix.quotation.credit.override"]
    assert "action_release" in served["fix.quotation.legal.hold"]
    assert "action_decide" in served["fix.estimate.review"]
    assert {"action_apply_standard_terms", "action_record_phone_acceptance"} <= served[
        "fix.quotation"
    ]


def test_a_lost_tender_is_recorded_only_with_a_governed_reason(m36):
    """BRU-QTE-16: the free-text Record Loss is neither offered nor served."""
    assert "action_record_loss" not in _p1._surfaces()["fix.tender"]
    acts = {a["m"] for a in m36["screens"]["M36-tenders"]["actions"]}
    assert "action_record_loss" not in acts
    outcome = {f["name"]: f for f in m36["screens"]["M36-form-tender-outcome"]["fields"]}
    assert outcome["loss_reason_code"]["required"] and outcome["notes"]["required"]


def test_stamps_and_decisions_are_never_typed():
    writable = _p1._writable()
    for model, names in STAMPS.items():
        leak = names & writable.get(model, set())
        assert not leak, (model, leak)


def test_the_renewal_form_names_its_contract(m36):
    fields = {f["name"]: f for f in m36["screens"]["M36-form-renewal"]["fields"]}
    assert fields["renewal_of_contract_id"]["required"]
    assert not {"customer_id", "contract_start", "value", "state"} & {
        n for n, f in fields.items() if not f["readonly"]
    }


def test_new_registers_are_secured_and_fenced():
    acl = (QUOTATION / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
    rows = [line.split(",") for line in acl.splitlines()[1:] if line.strip()]

    def perms(model, group):
        ref = "model_" + model.replace(".", "_")
        return [r[4:8] for r in rows if r[2] == ref and r[3] == group]

    for model in NEW_MODELS:
        assert perms(model, "base.group_user"), model  # every member of staff reads
        assert perms(model, "base.group_user")[0][0] == "1", model
    # only the steward keeps the library; only Finance overrides; nobody deletes
    # a credit override, a hold or an outcome
    assert perms("fix.quotation.standard.term", "base.group_user") == [["1", "0", "0", "0"]]
    assert perms("fix.quotation.credit.override", "account.group_account_manager") == [
        ["1", "0", "1", "0"]
    ]
    for model in (
        "fix.quotation.credit.override",
        "fix.quotation.legal.hold",
        "fix.tender.outcome",
    ):
        assert all(
            p[3] == "0"
            for r in rows
            if r[2] == "model_" + model.replace(".", "_")
            for p in [r[4:8]]
        ), model
    rules = (QUOTATION / "security" / "fix_isolation_rules.xml").read_text(encoding="utf-8")
    for model in NEW_MODELS:
        assert 'ref="model_%s"' % model.replace(".", "_") in rules, model


def test_the_new_model_file_loads_after_the_models_it_extends():
    """Ruff re-sorts models/__init__.py: an extension loaded before its base
    makes every DB test skip (the first pass's trap)."""
    init = (QUOTATION / "models" / "__init__.py").read_text(encoding="utf-8")
    tree = ast.parse(init)
    order = [a.name for node in tree.body if isinstance(node, ast.ImportFrom) for a in node.names]
    assert order[-1] == "fix_quote_capture2", order
