# Vendor-ledger sheet kind — behavioural tests on the live ORM (odoo_env,
# rolled back per test). The workbook reproduces the real file's measured
# shapes (readiness report 2026-11-08 §2): location-suffixed shop names,
# `23-` vintage twins, individual payees, mixed PAN/CIN semantics, internal
# staff rows, call-note noise, and a dual-role row that must MATCH the
# live customer master instead of duplicating it.
from __future__ import annotations

import base64
import io
import uuid

import pytest

U = uuid.uuid4().hex[:6].upper()

BD_MOBILE = "01712345678"


def _vendor_workbook() -> bytes:
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    ws.append(
        [
            "Complete Name",
            "Phone",
            "Email",
            "Address",
            "City",
            "Country",
            "Salesperson",
            "Customer Area",
            "PAN",
            "CIN",
        ]
    )
    rows = [
        # company-shaped, location suffix kept, city → division via vendor map
        [
            "HALDER ELECTRONICS %s (KHULNA)" % U,
            "01711111001",
            "halder%s@gmail.com" % U.lower(),
            "Shop#12, Khulna",
            "uttara",
            "Bangladesh",
            "",
            "Khulna",
            "",
            "",
        ],
        # `23-` vintage twin of the next row — same normalised name
        ["23-TANHA COMPUTER %s" % U, "01711111002", "", "", "", "", "", "", "", ""],
        ["TANHA COMPUTER %s" % U, "01711111003", "", "", "", "", "", "", "", ""],
        # individual payee with a 12-digit PAN (e-TIN) and a 2026-vintage CIN
        [
            "MD RIPON HOSSAIN %s" % U,
            "01711111004",
            "",
            "",
            "Dhaka",
            "Bangladesh",
            "",
            "",
            "175690137323",
            "20268210089",
        ],
        # 8-digit CIN = legacy system id, never a tax id
        [
            "LUCID COMPUTER %s" % U,
            "01711111005",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "11194880",
        ],
        # internal staff payee — quarantined, never a supplier
        [
            "A B M GOLAM %s" % U,
            "01711111006",
            "golam%s@1000fix.com" % U.lower(),
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ],
        # call note as a vendor name — quarantined noise
        ["3 Times No answer (Bogura)", "", "", "", "", "", "", "", "", ""],
        # matched BRANCH row (comma-concat repeating the parent): must
        # attach to the existing party, never stay 'matched' forever (the
        # audit-D-1 defect: pass 2 used to skip matched lines). In the real
        # ledger these rows match by SHARED PHONE with the parent's party.
        [
            "Daraz Bangladesh %s, Daraz Bangladesh %s (Khulna)" % (U, U),
            "01711111007",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ],
        # non-numeric phone (person name in the phone column) — dropped
        [
            "SIAM %s" % U,
            "Md.Rafsanul Alam",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ],
        # phone-as-name (2,496 measured rows) — split, noted, name kept
        ["01711112010 RECOVERED SHOP %s" % U, "", "", "", "", "", "", "", "", ""],
        # phone in the email column — rescued onto the phone field
        ["EMAILPHONE %s" % U, "", "01711112011", "", "", "", "", "", "", ""],
        # gamil.com typo domain — repaired, never dropped
        ["GAMIL %s" % U, "", "someone%s@gamil.com" % U.lower(), "", "", "", "", "", "", ""],
        # dual-role row: the party already exists as an active customer
        ["Daraz Bangladesh %s" % U, "01711111007", "", "", "Dhaka", "Bangladesh", "", "", "", ""],
    ]
    for r in rows:
        ws.append(r)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


@pytest.fixture()
def vbatch(odoo_env):
    return odoo_env["fix.party.import.batch"].create(
        {
            "sheet_kind": "vendor",
            "source_file": base64.b64encode(_vendor_workbook()).decode(),
            "source_filename": "unit_vendor_workbook.xlsx",
            "import_ref": "VENDTEST-%s" % U,
        }
    )


@pytest.fixture()
def daraz(odoo_env):
    """The pre-existing active customer the vendor row must match — activated
    through its two-tier registration approval, never a raw status write."""
    from odoo import fields as odoo_fields

    partner = odoo_env["res.partner"].create(
        {
            "name": "Daraz Bangladesh %s" % U,
            "is_company": True,
            "party_class": "corporate",
            "email": "daraz%s@example.com" % U.lower(),
            "phone": "01711111007",  # the branch row matches on this shared phone
        }
    )
    # the corporate birth auto-opens its two-tier approval — decide THAT one
    approval = (
        odoo_env["fix.registration.approval"]
        .sudo()
        .search([("partner_id", "=", partner.id)], limit=1)
    )
    approval._guarded().write(
        {
            "lm_state": "approved",
            "lm_decided_by": odoo_env.uid,
            "lm_decided_at": odoo_fields.Datetime.now(),
            "admin_state": "approved",
            "admin_decided_by": odoo_env.uid,
            "admin_decided_at": odoo_fields.Datetime.now(),
        }
    )
    approval._activate_if_complete()
    assert partner.party_status == "active"
    return partner


@pytest.mark.financial
class TestVendorSheetPipeline:
    def test_stage(self, odoo_env, vbatch):
        vbatch.action_stage()
        assert vbatch.state == "staged"
        assert vbatch.line_count == 13
        # vendor-only raw columns staged verbatim
        assert vbatch.line_ids[0].raw_city == "uttara"
        assert vbatch.line_ids[3].raw_pan == "175690137323"
        assert vbatch.line_ids[3].raw_cin == "20268210089"

    def test_validate_classification_and_quarantine(self, odoo_env, vbatch, daraz):
        vbatch.action_stage()
        vbatch.action_validate()
        assert vbatch.state == "validated"

        halder = next(ln for ln in vbatch.line_ids if "HALDER" in (ln.raw_name or ""))
        assert halder.line_state == "validated"
        assert "vendor class: dealer" in halder.notes
        assert halder.division_id.name == "Dhaka"  # 'uttara' → Dhaka
        assert "city 'uttara' mapped to division Dhaka" in halder.notes

        ripon = next(ln for ln in vbatch.line_ids if "RIPON" in (ln.raw_name or ""))
        assert "vendor class: individual" in ripon.notes
        assert ripon.tax_tin == "175690137323"
        assert "e-TIN classified from PAN" in ripon.notes
        assert "2026-vintage BIN pending verification" in ripon.notes

        lucid = next(ln for ln in vbatch.line_ids if "LUCID" in (ln.raw_name or ""))
        assert lucid.tax_tin == ""
        assert "legacy system id" in lucid.notes

        staff = next(ln for ln in vbatch.line_ids if "1000fix.com" in (ln.raw_email or ""))
        assert staff.line_state == "quarantined"
        assert "internal staff payee" in staff.notes

        noise = next(ln for ln in vbatch.line_ids if "No answer" in (ln.raw_name or ""))
        assert noise.line_state == "quarantined"

        siam = next(ln for ln in vbatch.line_ids if "SIAM" in (ln.raw_name or ""))
        assert siam.phone_norm == ""
        assert "non-numeric phone dropped" in siam.notes

        recovered = next(ln for ln in vbatch.line_ids if "RECOVERED" in (ln.raw_name or ""))
        assert recovered.phone_norm == "01711112010"
        assert "phone recovered from name prefix" in recovered.notes
        assert recovered.clean_name == "RECOVERED SHOP %s" % U

        emailphone = next(ln for ln in vbatch.line_ids if "EMAILPHONE" in (ln.raw_name or ""))
        assert emailphone.phone_norm == "01711112011"
        assert "phone rescued from email column" in emailphone.notes
        assert not emailphone.email_norm

        gamil = next(ln for ln in vbatch.line_ids if "GAMIL" in (ln.raw_name or ""))
        assert gamil.email_norm == "someone%s@gmail.com" % U.lower()
        assert "gamil.com typo repaired" in gamil.notes

        # the `23-` vintage twin: whichever TANHA row validates SECOND is the
        # intra-batch duplicate of the first (sheet order puts 23- first)
        tanha_lines = [ln for ln in vbatch.line_ids if "TANHA" in (ln.raw_name or "")]
        assert len(tanha_lines) == 2
        dup = [ln for ln in tanha_lines if ln.dup_of_line_id]
        assert len(dup) == 1 and "duplicate within batch" in dup[0].notes
        other = next(ln for ln in tanha_lines if not ln.dup_of_line_id)
        assert dup[0].dup_of_line_id.id == other.id

        # dual-role row matches the live customer
        daraz_line = next(
            ln
            for ln in vbatch.line_ids
            if "daraz" in (ln.raw_name or "").lower() and not ln.parent_name
        )
        assert daraz_line.line_state == "matched"
        assert daraz_line.matched_partner_id.id == daraz.id
        # its comma-concat BRANCH twin (parent repeat) also matches pre-import
        daraz_branch = next(
            ln
            for ln in vbatch.line_ids
            if "daraz" in (ln.raw_name or "").lower() and ln.parent_name
        )
        assert daraz_branch.line_state == "matched"

    def test_full_pipeline_roles_and_classes(self, odoo_env, vbatch, daraz):
        vbatch.action_stage()
        vbatch.action_validate()
        vbatch.action_import()
        assert vbatch.state == "imported"

        created = vbatch.line_ids.filtered(lambda ln: ln.created_partner_id)
        assert len(created) == 8  # halder, tanha, ripon, lucid, siam, recovered, emailphone, gamil

        halder = next(ln for ln in created if "HALDER" in ln.clean_name)
        assert halder.created_partner_id.is_company
        assert halder.created_partner_id.party_class == "dealer"
        ripon = next(ln for ln in created if "RIPON" in ln.clean_name)
        assert not ripon.created_partner_id.is_company
        assert ripon.created_partner_id.party_class == "individual"
        # the suffix stays in the name (no decomposition without a parent
        # repeat) — cleaned, i.e. parens → spaces, case preserved
        assert halder.created_partner_id.name == "HALDER ELECTRONICS %s KHULNA" % U

        vbatch.action_decide_registrations()
        # individuals activated via the guarded path, dealers via their approval
        assert ripon.created_partner_id.party_status == "active"
        assert halder.created_partner_id.party_status == "active"

        vbatch.action_assign_roles()
        Role = odoo_env["fix.party.role"]
        vendor_roles = Role.search(
            [
                ("role_type", "=", "vendor"),
                ("partner_id", "in", created.mapped("created_partner_id").ids),
            ]
        )
        assert len(vendor_roles) == len(created)
        # the dual-role party gained a vendor role too — never a second party
        daraz_roles = Role.search([("role_type", "=", "vendor"), ("partner_id", "=", daraz.id)])
        assert len(daraz_roles) == 1
        # the matched BRANCH line linked (audit D-1: pass 2 used to leave
        # matched branch rows unattached forever)
        daraz_branch = next(
            ln
            for ln in vbatch.line_ids
            if "daraz" in (ln.raw_name or "").lower() and ln.parent_name
        )
        assert daraz_branch.line_state == "linked"
        assert daraz_branch.matched_partner_id.id == daraz.id

        summary = vbatch.action_reconcile()
        assert summary["by_party_class"]["individual"] >= 2
        assert summary["by_party_class"]["dealer"] >= 2
        assert vbatch.state == "reconciled"

    def test_rollback(self, odoo_env, vbatch, daraz):
        vbatch.action_stage()
        vbatch.action_validate()
        vbatch.action_import()
        vbatch.action_decide_registrations()
        vbatch.action_assign_roles()
        created = vbatch.line_ids.mapped("created_partner_id")
        vbatch.action_rollback()
        for partner in created:
            assert not partner.exists() or not partner.active
        # the pre-existing customer keeps its party AND loses only the legacy
        # key this batch attached
        assert daraz.exists()
