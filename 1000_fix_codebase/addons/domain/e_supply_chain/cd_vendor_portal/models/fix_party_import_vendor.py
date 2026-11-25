# cd_vendor_portal — vendor-ledger satellites for the M33 party import
# (readiness report 2026-11-08 §7A steps 2–4).
#
# The cd_party_master loader creates the PARTIES (vendor role, legacy keys,
# PDPA stamps). This extension registers them as suppliers: a fix.supplier
# row per party (born prospect, moved to qualified through the sanctioned
# _a06_set_status transition — the M42 activation gate with its documents,
# screening and second-person approval is deliberately NOT bypassed; legacy
# mass activates later by spend waves) and a fix.vendor.tax.profile wherever
# the loader classified a 12-digit e-TIN from the PAN column. Rollback
# removes exactly the rows this batch created.
from __future__ import annotations

import datetime

from odoo import models
from odoo.exceptions import UserError


class FixPartyImportBatch(models.Model):
    _inherit = "fix.party.import.batch"

    def _vendor_satellite_note(self) -> str:
        self.ensure_one()
        return "M33 vendor-ledger cut-over batch #%d" % self.id

    # -------------------------------------------------- supplier registration
    def action_register_suppliers(self):
        """Register every vendor-ledger party in the M42 supplier register:
        prospect → qualified (transactional segment), tax profile where an
        e-TIN was classified. Idempotent per partner. Runs only on vendor
        batches whose registrations are already decided (active parties)."""
        self.ensure_one()
        # same authority as the loader steps it follows (registration
        # administrator or the trusted cut-over script): with chunked commits
        # a 500+ party batch would otherwise register rows before the batch
        # ACL stops a non-administrator at the closing log write
        self._fix_import_check_authority()
        if self.sheet_kind != "vendor":
            raise UserError("Supplier registration runs on vendor-ledger batches only.")
        if self.state not in ("approved", "reconciled"):
            raise UserError("Decide the registrations first — a supplier needs an active party.")
        Supplier = self.env["fix.supplier"]
        TaxProfile = self.env["fix.vendor.tax.profile"]
        note = self._vendor_satellite_note()
        lines = self.line_ids
        # created parties + matched (dual-role) parties, ordered, de-duped
        partners = lines.mapped(lambda ln: ln.created_partner_id or ln.matched_partner_id).filtered(
            lambda p: p and p.party_status == "active"
        )
        registered = {
            row["partner_id"][0]
            for row in Supplier.read_group(
                [("partner_id", "in", partners.ids)], ["partner_id"], ["partner_id"]
            )
        }
        tins = {}
        for line in lines:
            partner = line.created_partner_id or line.matched_partner_id
            if partner and line.tax_tin and partner.id not in tins:
                tins[partner.id] = line.tax_tin
        created = profiles = skipped = 0
        chunked = self.env.context.get("import_chunk_commits")
        for reg_index, partner in enumerate(partners, start=1):
            if partner.id in registered:
                skipped += 1
                continue
            supplier = Supplier.create(
                {
                    "name": partner.name,
                    "partner_id": partner.id,
                    "company_id": self.company_id.id,
                    "segment": "transactional",
                    "onboarded_on": datetime.date.today(),
                    "notes": note,
                }
            )
            # A06 P35: a legacy vendor arrives as a PROSPECT. It used to be
            # labelled "qualified" with no qualification record behind it; the
            # status now says what is true until a qualification is approved.
            supplier.message_post(
                body="Vendor-ledger cut-over: legacy mass import. Qualification, documents and "
                "screening are recorded before the supplier is activated."
            )
            created += 1
            tin = tins.get(partner.id)
            if tin and not TaxProfile.search_count(
                [
                    ("partner_id", "=", partner.id),
                    ("company_id", "=", self.company_id.id),
                ]
            ):
                TaxProfile.create(
                    {
                        "partner_id": partner.id,
                        "company_id": self.company_id.id,
                        "tin": tin,
                    }
                )
                profiles += 1
            if chunked and reg_index % 500 == 0:
                self.env.cr.commit()
        self._log(
            "supplier register: %d created (qualified/transactional), %d tax "
            "profiles, %d already registered" % (created, profiles, skipped)
        )
        return True

    # ---------------------------------------------------------------- rollback
    def action_rollback(self):
        """Vendor batches roll back their satellites first — a supplier
        register row pins its partner (ondelete=restrict), so the base
        rollback's party unlink would fail otherwise. Tax profiles cascade
        with the party; supplier rows and vendor roles on matched (dual-role)
        parties are removed here, exactly the ones this batch created."""
        for batch in self:
            batch._fix_import_check_authority()
        for batch in self:
            if batch.sheet_kind != "vendor":
                continue
            Supplier = self.env["fix.supplier"]
            Role = self.env["fix.party.role"]
            note = batch._vendor_satellite_note()
            partners = batch.line_ids.mapped(
                lambda ln: ln.created_partner_id or ln.matched_partner_id
            )
            satellites = Supplier.search([("partner_id", "in", partners.ids), ("notes", "=", note)])
            satellites.unlink()
            roles = Role.search(
                [
                    ("partner_id", "in", partners.ids),
                    ("role_type", "=", "vendor"),
                    ("role_status", "=", "active"),
                ]
            ).filtered(
                # only roles this batch could have assigned: created after the
                # batch was, with no other vendor context (no bills) — a
                # pre-existing vendor role on a dual-role party survives
                lambda r, since=batch.create_date: r.create_date >= since
                and not self.env["fix.vendor.invoice"].search_count(
                    [("vendor_id", "=", r.partner_id.id)]
                )
            )
            roles.unlink()
            batch._log(
                "vendor satellites removed: %d supplier rows, %d vendor roles"
                % (len(satellites), len(roles))
            )
        return super().action_rollback()
