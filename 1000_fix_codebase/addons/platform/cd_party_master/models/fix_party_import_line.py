# cd_party_master — party import line (M33 cut-over): one staged source row
# with its raw values, every cleansing note, and the match/create outcome.
from __future__ import annotations

from odoo import fields, models


class FixPartyImportLine(models.Model):
    _name = "fix.party.import.line"
    _description = "Party Import Line"
    _order = "batch_id, row_no"

    batch_id = fields.Many2one(
        "fix.party.import.batch", required=True, ondelete="cascade", index=True
    )
    row_no = fields.Integer(string="Source Row", readonly=True)

    # raw values exactly as staged
    raw_name = fields.Char()
    raw_phone = fields.Char()
    raw_email = fields.Char()
    raw_street = fields.Char()
    raw_state = fields.Char()
    raw_country = fields.Char()
    raw_tag = fields.Char()
    raw_salesperson = fields.Char()
    raw_city = fields.Char()
    # vendor-ledger sheet only (readiness report 2026-11-08 §2.1)
    raw_area = fields.Char(string="Customer Area (raw)")
    raw_pan = fields.Char(string="PAN (raw)")
    raw_cin = fields.Char(string="CIN (raw)")

    # cleansed values + audit notes
    legacy_reference = fields.Char(index=True)
    clean_name = fields.Char()
    parent_name = fields.Char(string="Parent (decomposed)")
    phone_norm = fields.Char()
    email_norm = fields.Char()
    # the e-TIN classified from the PAN column (12-digit) — the only
    # identifier the fix.vendor.tax.profile constraint accepts at load
    tax_tin = fields.Char(string="e-TIN (classified)")
    district_raw = fields.Char()
    division_id = fields.Many2one("res.country.state")
    user_id = fields.Many2one("res.users", string="Salesperson (mapped)")
    notes = fields.Char(string="Cleansing Notes")

    line_state = fields.Selection(
        [
            ("staged", "Staged (raw)"),
            ("validated", "Validated"),
            ("quarantined", "Quarantined"),
            ("error", "Error"),
            ("matched", "Matched existing party"),
            ("linked", "Matched — legacy key attached"),
            ("created", "Created"),
        ],
        default="staged",
        required=True,
        index=True,
    )
    matched_partner_id = fields.Many2one("res.partner", readonly=True)
    created_partner_id = fields.Many2one("res.partner", readonly=True)
    dup_of_line_id = fields.Many2one(
        "fix.party.import.line", string="Duplicate Of (batch line)", readonly=True
    )
    parent_partner_id = fields.Many2one(
        "res.partner", string="Parent Party (hierarchy)", readonly=True
    )
