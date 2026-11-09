# Behavioural tests for the M33 party kernel on the live ORM (`odoo_env`,
# rolled back after every test). The Z4 residency service is replaced by an
# in-memory fake: tests run offline and assert the classified value NEVER
# reaches the regional store.
import contextlib
import json
import logging

import pytest
from odoo.exceptions import ValidationError

import libs.py.fix_residency as fix_residency


class FakeZ4:
    """In-memory stand-in for the residency service (put/get by key)."""

    def __init__(self):
        self.store: dict[str, str] = {}
        self.fail_get = False

    def put(self, key, value):
        self.store[key] = value
        return {"ok": True}

    def get(self, key):
        if self.fail_get:
            raise fix_residency.ResidencyError("residency service unreachable")
        return self.store.get(key, "")


@pytest.fixture
def z4(monkeypatch):
    fake = FakeZ4()
    monkeypatch.setattr(fix_residency, "get_client", lambda: fake)
    return fake


@contextlib.contextmanager
def _rejects(env, exc, match):
    with pytest.raises(exc, match=match) as info, env.cr.savepoint():
        yield info


def _partner(env, name="Karim Ahmed", **vals):
    return env["res.partner"].create({"name": name, **vals})


def _events(env, event_type, aggregate, aggregate_id):
    return env["fix.event.outbox"].search(
        [
            ("event_type", "=", event_type),
            ("aggregate", "=", aggregate),
            ("aggregate_id", "=", aggregate_id),
        ]
    )


def _regional_column(env, doc):
    env.flush_all()
    env.cr.execute("SELECT document_number FROM fix_identity_document WHERE id = %s", [doc.id])
    return env.cr.fetchone()[0]


def _identity(env, number=None, document_type="nid_10", partner=None):
    vals = {"partner_id": (partner or _partner(env)).id, "document_type": document_type}
    if number is not None:
        vals["document_number"] = number
    return env["fix.identity.document"].create(vals)


# --- fix.identity.document + residency.mixin -------------------------------------


def test_classified_number_goes_to_z4_never_the_regional_store(odoo_env, z4):
    doc = _identity(odoo_env, "1234567890")
    assert doc.residency_ref
    assert z4.store == {f"party identity:{doc.residency_ref}": "1234567890"}
    assert _regional_column(odoo_env, doc) is None

    events = _events(odoo_env, "party.identity_added", "fix.identity.document", doc.id)
    payload = json.loads(events.payload)
    assert payload == {"partner_id": doc.partner_id.id, "document_type": "nid_10"}
    assert "1234567890" not in events.payload


def test_read_of_classified_field_is_served_from_z4(odoo_env, z4):
    doc = _identity(odoo_env, "1234567890")
    assert doc.read(["document_number", "document_type"])[0]["document_number"] == "1234567890"
    # an unclassified read never calls Z4 and never sees the value
    assert "document_number" not in doc.read(["document_type"])[0]


def test_read_of_several_records_resolves_each_own_reference(odoo_env, z4):
    """Regression: read() dereferenced residency_ref on the whole recordset
    (singleton crash) and only ever filled the first row."""
    first = _identity(odoo_env, "1111111111")
    second = _identity(odoo_env, "22222222222222222", document_type="nid_17")
    unnumbered = _identity(odoo_env)
    rows = {r["id"]: r for r in (first | second | unnumbered).read(["document_number"])}
    assert rows[first.id]["document_number"] == "1111111111"
    assert rows[second.id]["document_number"] == "22222222222222222"
    assert rows[unnumbered.id]["document_number"] is False


def test_read_failure_degrades_to_empty_value(odoo_env, z4, caplog):
    doc = _identity(odoo_env, "1234567890")
    z4.fail_get = True
    with caplog.at_level(logging.WARNING):
        row = doc.read(["document_number"])[0]
    assert row["document_number"] == ""
    assert "residency read failed for document_number" in caplog.text


def test_write_reuses_the_existing_residency_reference(odoo_env, z4):
    doc = _identity(odoo_env, "1234567890")
    ref = doc.residency_ref
    doc.write({"document_number": "0987654321"})
    assert doc.residency_ref == ref
    assert z4.store[f"party identity:{ref}"] == "0987654321"
    assert _regional_column(odoo_env, doc) is None


def test_write_of_unclassified_fields_bypasses_z4(odoo_env, z4):
    doc = _identity(odoo_env)
    doc.write({"verification_status": "pending"})
    assert not doc.residency_ref
    assert z4.store == {}


def test_batch_write_routes_each_record_through_its_own_reference(odoo_env, z4):
    """Regression: a classified write on several records crashed reading the
    singleton residency_ref."""
    first, second = _identity(odoo_env, "1111111111"), _identity(odoo_env)
    (first | second).write({"document_number": "5555555555", "is_primary": False})
    assert first.residency_ref and second.residency_ref
    assert first.residency_ref != second.residency_ref
    assert z4.store[f"party identity:{first.residency_ref}"] == "5555555555"
    assert z4.store[f"party identity:{second.residency_ref}"] == "5555555555"
    assert not first.is_primary and not second.is_primary


@pytest.mark.parametrize(
    ("document_type", "number", "valid"),
    [
        ("nid_10", "1234567890", True),
        ("nid_17", "12345678901234567", True),
        ("nid_10", "SYNTHETIC-NID-0001", True),
        ("nid_10", "12345", False),
        ("nid_17", "12345678ABCDEFGHI", False),
        ("passport", "1234567890", False),  # not an NID: never checksum-valid
    ],
)
def test_checksum_validity_is_computed_from_the_z4_value(
    odoo_env, z4, document_type, number, valid
):
    doc = _identity(odoo_env, number, document_type=document_type)
    assert doc.checksum_valid is valid


def test_checksum_fails_closed_without_reference_or_service(odoo_env, z4):
    assert _identity(odoo_env).checksum_valid is False
    doc = _identity(odoo_env, "1234567890")
    odoo_env.invalidate_all()
    z4.fail_get = True
    assert odoo_env["fix.identity.document"].browse(doc.id).checksum_valid is False


# --- fix.party.role -------------------------------------------------------------------


def test_role_lifecycle_emits_added_changed_removed(odoo_env):
    partner = _partner(odoo_env)
    role = odoo_env["fix.party.role"].create({"partner_id": partner.id, "role_type": "customer"})
    added = _events(odoo_env, "party.role_added", "res.partner", partner.id)
    assert json.loads(added.payload) == {
        "partner_id": partner.id,
        "role_type": "customer",
        "role_status": "prospect",
    }

    role.write({"operating_unit_ids": [(6, 0, [])]})
    assert not _events(odoo_env, "party.role_changed", "res.partner", partner.id)
    role.write({"role_status": "active"})
    changed = _events(odoo_env, "party.role_changed", "res.partner", partner.id)
    assert json.loads(changed.payload)["role_status"] == "active"

    role.unlink()
    removed = _events(odoo_env, "party.role_removed", "res.partner", partner.id)
    assert json.loads(removed.payload)["role_type"] == "customer"


def test_one_partner_holds_many_roles(odoo_env):
    partner = _partner(odoo_env)
    Role = odoo_env["fix.party.role"]
    for role_type in ("customer", "vendor", "seller"):
        Role.create({"partner_id": partner.id, "role_type": role_type})
    assert sorted(partner.role_ids.mapped("role_type")) == ["customer", "seller", "vendor"]


def test_shared_vat_is_flagged_as_potential_duplicate_master(odoo_env, caplog):
    partner = _partner(odoo_env, "Dup One", vat="BIN-778899")
    _partner(odoo_env, "Dup Two", vat="BIN-778899")
    with caplog.at_level(logging.WARNING):
        odoo_env["fix.party.role"].create({"partner_id": partner.id, "role_type": "vendor"})
    assert "shares VAT with 1 other record(s)" in caplog.text


@pytest.mark.parametrize("vat", [False, "BIN-UNIQUE-1"])
def test_no_duplicate_warning_without_shared_vat(odoo_env, caplog, vat):
    partner = _partner(odoo_env, vat=vat)
    with caplog.at_level(logging.WARNING):
        odoo_env["fix.party.role"].create({"partner_id": partner.id, "role_type": "customer"})
    assert "potential duplicate master" not in caplog.text


# --- fix.party.hierarchy / fix.consent / res.partner -------------------------------------


def test_party_cannot_relate_to_itself(odoo_env):
    partner, spouse = _partner(odoo_env), _partner(odoo_env, "Spouse")
    Hierarchy = odoo_env["fix.party.hierarchy"]
    with _rejects(odoo_env, ValidationError, match="cannot relate to itself"):
        Hierarchy.create({"parent_id": partner.id, "child_id": partner.id})
    link = Hierarchy.create({"parent_id": partner.id, "child_id": spouse.id})
    assert partner.hierarchy_child_ids == link
    assert spouse.hierarchy_parent_ids == link


def test_granted_consent_needs_proof_and_notice(odoo_env):
    partner = _partner(odoo_env)
    Consent = odoo_env["fix.consent"]
    with _rejects(odoo_env, ValidationError, match="needs its proof reference"):
        Consent.create({"partner_id": partner.id, "channel": "sms"})
    withdrawn = Consent.create({"partner_id": partner.id, "channel": "email", "state": "withdrawn"})
    assert not withdrawn.proof
    # BRU-CPM-08: a grant with proof but no notice version is not valid consent
    with _rejects(odoo_env, ValidationError, match="BRU-CPM-08"):
        Consent.create({"partner_id": partner.id, "channel": "sms", "proof": "OTP-1"})


def test_withdrawal_is_append_only_and_keeps_the_grant(odoo_env):
    """T-09: a withdrawal is a NEW record — the granted row is never
    rewritten to look withdrawn (it is marked superseded by link)."""
    partner = _partner(odoo_env)
    notice = odoo_env["fix.transparency.notice"].create(
        {"version": "1.0", "text_en": "Notice EN", "text_bn": "বিজ্ঞপ্তি"}
    )
    Consent = odoo_env["fix.consent"]
    grant = Consent.create(
        {
            "partner_id": partner.id,
            "purpose": "marketing",
            "channel": "marketing",
            "proof": "OTP-123",
            "notice_version_id": notice.id,
        }
    )
    assert grant.action_withdraw() is True

    grant.invalidate_recordset()
    assert grant.state == "superseded"
    assert grant.proof == "OTP-123"  # the grant keeps its captured state
    assert grant.date_granted  # never rewritten

    withdrawal = Consent.search([("supersedes_id", "=", grant.id)])
    assert len(withdrawal) == 1
    assert withdrawal.state == "withdrawn"
    assert withdrawal.purpose == grant.purpose
    assert withdrawal.date_withdrawn
    assert grant.superseded_by_id.id == withdrawal.id


def test_notification_language_defaults_to_english(odoo_env):
    # user directive 2026-11-08: English is the business default; Bengali
    # is a per-party choice (MD-013 notification language)
    partner = _partner(odoo_env)
    assert partner.preferred_language == "en"
    assert partner._get_notification_language() == "en"
    partner.preferred_language = "bn"
    assert partner._get_notification_language() == "bn"
    unsaved = odoo_env["res.partner"].new({"name": "Draft", "preferred_language": False})
    assert unsaved._get_notification_language() == "en"
    with pytest.raises(ValueError, match="Expected singleton"):
        (partner | _partner(odoo_env, "Other"))._get_notification_language()


def test_dedup_rule_defaults_to_the_partner_model(odoo_env):
    rule = odoo_env["fix.dedup.rule"].create({"name": "Phone match", "match_fields": "phone"})
    assert rule.model_id == odoo_env.ref("base.model_res_partner")
    assert (rule.scope, rule.action, rule.threshold) == ("exact", "flag", 2)
