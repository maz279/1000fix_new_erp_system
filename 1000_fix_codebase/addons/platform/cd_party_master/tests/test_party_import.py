# M33 real-customer cut-over loader — behavioural tests on the live ORM
# (`odoo_env`, rolled back per test). The full pipeline runs against a
# purpose-built workbook that reproduces every quality issue measured in the
# real file: year-prefixed names, comma-concatenated parent+branch, 880
# phones, landlines, Outlook-format emails, invalid emails, district states,
# placeholder numbers and a pre-existing party to match.
from __future__ import annotations

import base64
import io
import uuid

import pytest

# unique per run: the trial cut-over commits the REAL names into the test
# database, so unit-test rows must never collide with live parties
U = uuid.uuid4().hex[:6].upper()

from odoo.addons.cd_party_master.models.fix_party_import import (
    _norm_email,
    _norm_name,
    _norm_phone,
    _split_parent_branch,
)

BD_MOBILE = "01712345678"


def _workbook() -> bytes:
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = "Corp"
    ws.append(["Complete Name", "Mobile", "E-mail", "Street", "State", "Country", "Tags"])
    ws.append(
        [
            "23-(BIGM-%s)BANGLADESH INSTITUTE" % U,
            "01711111001",
            "info@bigm.edu.bd",
            "E-33, Agargaon",
            "Dhaka (BD)",
            "Bangladesh",
            "Corporate",
        ]
    )
    # 880-prefix normalises; district state maps to a division
    ws.append(
        [
            "23-(CEGIS-%s)Center For Environment" % U,
            "88018111111002",
            "Rajesh Gupta <rajesh@cegisbd.com>",
            "CEGIS Bhaban",
            "Cumilla (BD)",
            "Bangladesh",
            "Corporate",
        ]
    )
    # parent + comma-concatenated branch (the World Vision shape)
    ws.append(
        [
            "23-%s WORLD VISION BANGLADESH" % U,
            "01711111003",
            "motiur@wvi.org",
            "Shanta Western Tower",
            "Dhaka (BD)",
            "Bangladesh",
            "Corporate",
        ]
    )
    ws.append(
        [
            "23-%s WORLD VISION BANGLADESH, 23-%s WORLD VISION BANGLADESH (KHULNA)" % (U, U),
            "01711111004",
            "",
            "Shanta Western Tower",
            "Dhaka (BD)",
            "Bangladesh",
            "Corporate",
        ]
    )
    # landline kept; state blank; invalid email quarantined
    ws.append(
        [
            "ACME %s OFFICE" % U,
            "02821111",
            "bad-email-no-tld",
            "Banani",
            "",
            "Bangladesh",
            "Corporate",
        ]
    )
    # placeholder phone → quarantined
    ws.append(
        [
            "PLACEHOLDER %s CO" % U,
            "880 1749-0000000",
            "ok@example.com",
            "Gulshan",
            "Dhaka (BD)",
            "Bangladesh",
            "Corporate",
        ]
    )
    # duplicate of the first row's org (same normalised name) → intra-batch dup
    ws.append(
        [
            "23-(BIGM-%s)BANGLADESH INSTITUTE" % U,
            "01711111001",
            "info@bigm.edu.bd",
            "E-33, Agargaon",
            "Dhaka (BD)",
            "Bangladesh",
            "Corporate",
        ]
    )
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


@pytest.fixture()
def batch(odoo_env):
    Batch = odoo_env["fix.party.import.batch"]
    return Batch.create(
        {
            "sheet_kind": "corp",
            "source_file": base64.b64encode(_workbook()).decode(),
            "source_filename": "unit_workbook.xlsx",
            "import_ref": "TEST",
        }
    )


class TestCleansingHelpers:
    def test_name_normalisation_strips_year_prefix(self):
        assert _norm_name("23-(BIGM)BANGLADESH") == "BIGM BANGLADESH"

    def test_phone_bd_formats(self):
        assert _norm_phone("+880 1812-345678")[0] == "01812345678"
        assert _norm_phone("01711111001")[0] == "01711111001"
        landline = _norm_phone("02-8413571")
        assert landline[0].startswith("02") and "landline" in landline[1]
        short = _norm_phone("171234567")
        assert "truncated" in short[1]

    def test_email_display_format_and_invalid(self):
        assert _norm_email("Rajesh Gupta <rajesh@x.com>")[0] == "rajesh@x.com"
        clean, note = _norm_email("no-tld@company")
        assert clean == "" and "dropped" in note

    def test_parent_branch_split(self):
        code, full, parent, branch = _split_parent_branch(
            "23-WORLD VISION BANGLADESH, 23-WORLD VISION BANGLADESH (KHULNA)"
        )
        assert code == "23"
        assert full == "WORLD VISION BANGLADESH — KHULNA"
        assert parent == "WORLD VISION BANGLADESH"
        assert branch.upper().startswith("KHULNA")
        # a comma that is just part of the name NEVER decomposes (the
        # 2026-11-08 audit: 125 records named after bare fragments)
        code2, full2, parent2, branch2 = _split_parent_branch(
            "23-Aga Khan Education Service , Bangladesh"
        )
        assert full2 == "Aga Khan Education Service, Bangladesh"
        assert parent2 == "" and branch2 == ""
        code3, full3, parent3, branch3 = _split_parent_branch("23-icddr,b")
        assert full3 == "icddr,b" and parent3 == "" and branch3 == ""


@pytest.mark.financial
class TestLoaderPipeline:
    def test_full_pipeline(self, odoo_env, batch):
        # stage: 7 data rows
        batch.action_stage()
        assert batch.state == "staged" and batch.line_count == 7

        # validate: divisions, phones, emails, intra-batch dup, quarantine
        batch.action_validate()
        assert batch.state == "validated"
        bigm = [ln for ln in batch.line_ids if "BIGM" in (ln.clean_name or "")]
        assert len(bigm) == 2
        assert bigm[0].division_id.name == "Dhaka"
        assert bigm[0].phone_norm == "01711111001"
        dup = [ln for ln in bigm if ln.dup_of_line_id]
        assert len(dup) == 1 and "duplicate within batch" in dup[0].notes
        cegis = next(ln for ln in batch.line_ids if "CEGIS" in (ln.raw_name or ""))
        assert cegis.email_norm == "rajesh@cegisbd.com"
        assert cegis.division_id.name == "Chattogram"  # district Cumilla mapped
        assert "display-format" in cegis.notes
        wv = next(ln for ln in batch.line_ids if "KHULNA" in (ln.raw_name or ""))
        assert wv.parent_name.endswith("WORLD VISION BANGLADESH")
        ph = next(ln for ln in batch.line_ids if "PLACEHOLDER" in (ln.raw_name or ""))
        assert ph.line_state == "quarantined"
        landline = next(ln for ln in batch.line_ids if "ACME" in (ln.raw_name or ""))
        assert "landline" in (landline.notes or "")
        assert landline.email_norm == ""  # invalid email quarantined

        # import: draft parties, hierarchy for the branch, PDPA stamp
        batch.action_import()
        assert batch.state == "imported"
        created = batch.line_ids.filtered(lambda ln: ln.created_partner_id)
        assert len(created) == 5  # 7 rows - 1 quarantined - 1 intra-batch dup
        for line in created:
            p = line.created_partner_id
            assert p.party_status in ("draft", "pending_approval")
            assert p.is_company and p.party_class == "corporate"
            assert p.legacy_reference and p.legacy_reference.startswith("TEST-")
        wv_line = next(ln for ln in created if "KHULNA" in (ln.clean_name or "").upper())
        assert wv_line.parent_partner_id.name.endswith("WORLD VISION BANGLADESH")
        # the duplicate row linked to the same party, no second record
        assert dup[0].line_state == "linked"
        assert (
            dup[0].matched_partner_id == bigm[0].created_partner_id
            or dup[0].matched_partner_id == dup[0].dup_of_line_id.created_partner_id
        )

        # registrations: the auto-opened approvals get decided, parties active
        batch.action_decide_registrations()
        assert batch.state == "approved"
        for line in created:
            partner = line.created_partner_id
            assert partner.party_status == "active", partner.name
            approval = odoo_env["fix.registration.approval"].search(
                [("partner_id", "=", partner.id)], limit=1
            )
            assert approval.lm_state == "approved" and approval.admin_state == "approved"

        # reconcile: counts add up to the source
        summary = batch.action_reconcile()
        assert summary["source_rows"] == 7
        assert summary["created"] == 5
        assert summary["by_state"].get("quarantined") == 1

    def test_matched_line_gets_legacy_key_not_a_duplicate(self, odoo_env, batch):
        batch.action_stage()
        batch.action_validate()
        batch.action_import()
        # second run over the same workbook: every row now matches
        batch2 = odoo_env["fix.party.import.batch"].create(
            {
                "sheet_kind": "corp",
                "source_file": base64.b64encode(_workbook()).decode(),
                "source_filename": "unit_workbook.xlsx",
                "import_ref": "TEST",
            }
        )
        batch2.action_stage()
        batch2.action_validate()
        batch2.action_import()
        fresh = batch2.line_ids.filtered(lambda ln: ln.created_partner_id)
        linked = batch2.line_ids.filtered(lambda ln: ln.line_state == "linked")
        assert not fresh, "a re-run must not duplicate parties"
        assert linked, "matched lines get the legacy key attached"
        for line in linked:
            assert line.matched_partner_id.legacy_reference

    def test_state_guards(self, odoo_env, batch):
        from odoo.exceptions import UserError

        with pytest.raises(UserError):
            batch.action_validate()  # not staged yet
        with pytest.raises(UserError):
            batch.action_import()
        with pytest.raises(UserError):
            batch.action_decide_registrations()

    def test_stbl_salesperson_mapping(self, odoo_env):
        from openpyxl import Workbook

        user = odoo_env["res.users"].search([("share", "=", False)], limit=1)
        wb = Workbook()
        ws = wb.active
        ws.title = "STBL and Principal"
        ws.append(
            [
                "Complete Name",
                "Phone",
                "Email",
                "Salesperson",
                "Activities",
                "City",
                "Country",
                "Tag",
            ]
        )
        ws.append(
            [
                "ACER %s INDIA PVT LTD. (SERVICE)" % U,
                "888471111111",
                "RaoCK.Rao@acer.com",
                user.name,
                "",
                "Pondicherry",
                "India",
                "Principal",
            ]
        )
        buf = io.BytesIO()
        wb.save(buf)
        batch = odoo_env["fix.party.import.batch"].create(
            {
                "sheet_kind": "stbl",
                "source_file": base64.b64encode(buf.getvalue()).decode(),
                "source_filename": "stbl.xlsx",
                "import_ref": "STBL",
            }
        )
        batch.action_stage()
        batch.action_validate()
        batch.action_import()
        line = batch.line_ids[0]
        assert line.user_id.id == user.id
        assert line.created_partner_id.party_class == "dealer"
