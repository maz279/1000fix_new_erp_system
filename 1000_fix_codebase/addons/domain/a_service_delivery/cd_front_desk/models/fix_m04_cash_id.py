# M04 capture audit (18 Nov 2026): the high-value cash identity check
# (FR-FRD-019 P0, BRU-FRD-04 / -13 / -14, AUT-FRD-06).
#
# A counter sale never becomes an M20 receipt (cd_front_desk_finance posts it
# straight to the books, and without that bridge it posts nowhere), so the M20
# rule "cash above the threshold needs the customer's NID"
# (fix.ar.receipt.action_confirm) never ran at the counter: a BDT 60,000 cash
# sale confirmed with no NID and no consent, and Payment Capture had nothing
# to record them with.
#
# Now a cash sale above the high-value threshold is refused until a
# High-Value Cash ID Check is recorded for it. Recording the check
#   1. records the customer's consent against the PDPA transparency notice
#      version shown, FIRST (BRU-FRD-13), then
#   2. writes the NID to the Bangladesh-resident store as an M33 identity
#      document (BRU-FRD-14: the check keeps only the last 4 digits), or uses
#      an NID document already on file for the customer.
# A check is evidence: it is never changed or deleted. cd_front_desk_finance
# extends it to the multi-item basket (one check for the basket's one payment).
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

CASHIER_GROUPS = ("cd_front_desk.group_fd_cashier", "cd_front_desk.group_fd_branch_manager")
NID_TYPES = ("nid_10", "nid_17")
# BRU-FRD-04 names BDT 50,000. The figure in force is M51 statutory master
# data read through M20 (fix.ar.receipt._nid_threshold); this is used only
# where the billing engine is not installed.
STATUTORY_THRESHOLD = 50000.0


class FixConsentHighValueCash(models.Model):
    _inherit = "fix.consent"

    purpose = fields.Selection(
        selection_add=[("high_value_cash_id", "High-Value Cash Identity Check (statutory)")],
        ondelete={"high_value_cash_id": "cascade"},
    )
    channel = fields.Selection(
        selection_add=[("counter", "In Person at the Counter")],
        ondelete={"counter": "cascade"},
    )


class FixProcessingRecordHighValueCash(models.Model):
    """The consent and the NID capture are processing activities (PDPA record)."""

    _inherit = "fix.processing.record"

    purpose = fields.Selection(
        selection_add=[("high_value_cash_id", "High-Value Cash Identity Check (statutory)")],
        ondelete={"high_value_cash_id": "cascade"},
    )
    source = fields.Selection(
        selection_add=[("counter_id_check", "High-value cash ID check at the counter")],
        ondelete={"counter_id_check": "cascade"},
    )


class FixCashIdCheck(models.Model):
    """The customer's NID and consent behind a high-value cash receipt."""

    _name = "fix.cash.id.check"
    _description = "High-Value Cash ID Check"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    _sale_unique = models.Constraint("UNIQUE (sale_id)", "A counter sale has one ID check.")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "name",
            "amount",
            "threshold",
            "consent_id",
            "nid_last4",
            "recorded_by_id",
            "recorded_at",
        }

    name = fields.Char(string="Check No.", readonly=True, copy=False, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)
    sale_id = fields.Many2one(
        "fix.counter.sale", string="Counter Sale", index=True, ondelete="restrict"
    )
    branch_id = fields.Many2one("fix.branch", string="Branch", index=True)
    partner_id = fields.Many2one("res.partner", string="Customer", required=True, index=True)
    amount = fields.Float(string="Cash Received (BDT)", readonly=True)
    threshold = fields.Float(string="Threshold in Force (BDT)", readonly=True)
    notice_version_id = fields.Many2one(
        "fix.transparency.notice",
        string="Transparency Notice Presented",
        required=True,
        help="The PDPA notice version shown to the customer before the NID is taken.",
    )
    notice_presented = fields.Boolean(
        string="Notice Shown and Customer Agreed",
        help="Tick only after the customer has seen the notice and agreed.",
    )
    identity_document_id = fields.Many2one(
        "fix.identity.document",
        string="NID on File",
        help="An NID already recorded for the customer. Leave empty to record a new one.",
    )
    nid_number = fields.Char(
        string="Customer NID (10 or 17 digits)",
        compute="_compute_nid_number",
        inverse="_inverse_nid_number",
        help="Written to the Bangladesh-resident store only; never kept on this check.",
    )
    nid_last4 = fields.Char(string="NID (last 4 digits)", readonly=True)
    consent_id = fields.Many2one("fix.consent", string="Consent Recorded", readonly=True)
    recorded_by_id = fields.Many2one("res.users", string="Checked By", readonly=True)
    recorded_at = fields.Datetime(string="Checked At", readonly=True)

    def _compute_nid_number(self):
        # never read back: the number lives in the resident store only
        for rec in self:
            rec.nid_number = False

    def _inverse_nid_number(self):
        # taken in create(); a check is never edited afterwards
        return

    # ------------------------------------------------------------- the rule
    @api.model
    def _hv_threshold(self, company):
        if "fix.ar.receipt" in self.env:
            return self.env["fix.ar.receipt"].with_company(company)._nid_threshold()
        return STATUTORY_THRESHOLD

    @api.model
    def _hv_target(self, sale):
        """(record, cash amount, is_cash) a check on this sale covers."""
        return sale, sale.total, sale.payment_method == "cash"

    @api.model
    def _hv_target_from_vals(self, vals):
        """The draft record a new check is for, or an empty recordset."""
        sale = self.env["fix.counter.sale"].browse(vals.get("sale_id")).exists()
        if not sale:
            return None
        return self._hv_target(sale)

    @api.model
    def _hv_check_for(self, record):
        return self.sudo().search([("sale_id", "=", record.id)], limit=1)

    @api.model
    def _hv_link_vals(self, record):
        return {"sale_id": record.id}

    @api.model
    def _hv_require(self, record, amount, cash):
        """Refuse a cash receipt above the threshold that has no ID check."""
        if not cash or amount <= 0:
            return
        threshold = self._hv_threshold(record.company_id)
        if amount > threshold and not self._hv_check_for(record):
            raise UserError(
                "%s takes BDT %.2f in cash, above the BDT %s high-value threshold: record the "
                "customer's NID with a High-Value Cash ID Check (Payment Capture) before "
                "confirming (BRU-FRD-04)." % (record.name, amount, threshold)
            )

    @api.model
    def _hv_parse_nid(self, raw):
        nid = (raw or "").strip().replace(" ", "").replace("-", "")
        if not (nid.isdigit() and len(nid) in (10, 17)):
            raise UserError("A National ID is 10 (smart card) or 17 digits.")
        return nid, ("nid_10" if len(nid) == 10 else "nid_17")

    @api.model_create_multi
    def create(self, vals_list):
        user = self.env.user
        if not self.env.su and not any(user.has_group(g) for g in CASHIER_GROUPS):
            raise AccessError("Only a Front Desk Cashier or Branch Manager records an ID check.")
        Notice = self.env["fix.transparency.notice"]
        Doc = self.env["fix.identity.document"]
        records = self.browse()
        for vals in vals_list:
            target = self._hv_target_from_vals(vals)
            if not target:
                raise UserError("Choose the counter sale (or basket) being paid in cash.")
            record, amount, cash = target
            if record.state != "draft":
                raise UserError("%s is already confirmed." % record.name)
            if not cash:
                raise UserError("%s is not paid in cash: no NID is taken." % record.name)
            threshold = self._hv_threshold(record.company_id)
            if amount <= threshold:
                # PDPA data minimisation: no NID where the law does not ask for one
                raise UserError(
                    "%s is BDT %.2f, not above the BDT %s threshold: no NID is needed."
                    % (record.name, amount, threshold)
                )
            if self._hv_check_for(record):
                raise UserError("%s already has its ID check." % record.name)
            partner = self.env["res.partner"].browse(vals.get("partner_id")).exists()
            if not partner:
                raise UserError("Choose the customer paying the cash.")
            if record.customer_id and record.customer_id != partner:
                raise UserError(
                    "%s is for %s; the ID check must be for the same customer."
                    % (record.name, record.customer_id.display_name)
                )
            notice = Notice.browse(vals.get("notice_version_id")).exists()
            if not notice or not notice.active or notice.retired_at:
                raise UserError("Choose the transparency notice in force that was shown.")
            if not vals.get("notice_presented"):
                raise UserError(
                    "Show the customer the transparency notice and record their agreement "
                    "before the NID is taken (BRU-FRD-13)."
                )
            raw = vals.pop("nid_number", False)
            doc = Doc.browse(vals.get("identity_document_id")).exists()
            if doc and raw:
                raise UserError("Use the NID on file or type a new one, not both.")
            if doc and (
                doc.partner_id != partner or doc.document_type not in NID_TYPES or not doc.active
            ):
                raise UserError("The NID on file must be the customer's own active National ID.")
            if not doc and not raw:
                raise UserError("Type the customer's NID, or choose the NID already on file.")
            nid = doc_type = None
            if raw:
                nid, doc_type = self._hv_parse_nid(raw)
            now = fields.Datetime.now()
            seq = self.env["ir.sequence"].sudo().next_by_code("fix.cash.id.check") or "New"
            # 1. consent against the notice version shown (BRU-FRD-13) ...
            consent = (
                self.env["fix.consent"]
                .sudo()
                .create(
                    {
                        "partner_id": partner.id,
                        "purpose": "high_value_cash_id",
                        "channel": "counter",
                        "state": "granted",
                        "date_granted": now,
                        "notice_version_id": notice.id,
                        "proof": "%s: notice %s shown at the counter by %s"
                        % (seq, notice.version, user.name),
                        "company_id": record.company_id.id,
                    }
                )
            )
            # 2. ... then the NID, to the resident store (BRU-FRD-14)
            if not doc:
                doc = Doc.sudo().create(
                    {
                        "partner_id": partner.id,
                        "document_type": doc_type,
                        "document_number": nid,
                        "company_id": record.company_id.id,
                    }
                )
            # the NID (new or on file) is used under the statute, not the consent
            self.env["fix.processing.record"].sudo().create(
                {
                    "party_id": partner.id,
                    "purpose": "high_value_cash_id",
                    "lawful_basis": "legal_obligation",
                    "consent_id": consent.id,
                    "categories": "national ID number (BRU-FRD-04)",
                    "occurred_at": now,
                    "source": "counter_id_check",
                    "note": "%s: cash of BDT %.2f on %s" % (seq, amount, record.name),
                    "company_id": record.company_id.id,
                }
            )
            if not record.customer_id:
                record.sudo().write({"customer_id": partner.id})
            vals.update(self._hv_link_vals(record))
            vals.update(
                {
                    "name": seq,
                    "company_id": record.company_id.id,
                    "operating_unit_id": record.operating_unit_id.id or False,
                    "branch_id": record.branch_id.id or False,
                    "amount": amount,
                    "threshold": threshold,
                    "identity_document_id": doc.id,
                    "consent_id": consent.id,
                    "nid_last4": nid[-4:] if nid else False,
                    "recorded_by_id": user.id,
                    "recorded_at": now,
                }
            )
            records |= super(FixCashIdCheck, self._guarded()).create([vals])
        return records

    def write(self, vals):
        if not self.env.su and not self._fix_guard_has_token():
            if set(vals) & self._fix_guarded_fields():
                return super().write(vals)  # the guard refuses its own fields
            raise UserError("A high-value cash ID check is evidence: it is not changed.")
        return super().write(vals)

    def unlink(self):
        raise UserError("A high-value cash ID check is evidence: it is never deleted.")


class FixCounterSaleHighValue(models.Model):
    _inherit = "fix.counter.sale"

    def action_confirm(self):
        Check = self.env["fix.cash.id.check"]
        for sale in self:
            if sale.state == "draft":
                Check._hv_require(*Check._hv_target(sale))
        return super().action_confirm()
