# cd_cx_feedback — M34 Customer Experience + M42 Supplier Performance
# (P07-M06, CD-M34-nn/CD-M42-nn).
#
# M34: feedback/survey/rating capture, the complaint lifecycle with
# escalation, and survey triggering FROM service_order.closed events (AS-08 —
# no synchronous call into M01). T03/T07: the M23 NCR/CAPA linkages are
# REGISTERED STUBS with expiry dates (AR-006 §5.4 STUB + GV-005).
#
# M42: a READ-AND-SCORE consumer of M16 events (AR-006 §4.1 pair 10 — the
# asymmetric interface designed in Phase 6, implemented here): scorecards
# computed from goods.received / po.issued events, never a reach into M16.
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish  # FF-28


class FixSurvey(models.Model):
    """T04: the post-service survey, triggered by consuming
    service_order.closed (NT-024's deferred send — never at completion)."""

    _name = "fix.survey"
    _description = "Service Survey"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc, id desc"
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _order_unique = models.Constraint('UNIQUE (service_order_id)', 'One survey per service order')

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    service_order_id = fields.Many2one("fix.service.order", string="Service Order",
                                       required=True, ondelete="cascade", index=True)
    customer_id = fields.Many2one(related="service_order_id.customer_id",
                                  store=True, index=True)
    state = fields.Selection(
        [("pending", "Pending"), ("sent", "Sent"), ("responded", "Responded"),
         ("expired", "Expired")], default="pending", required=True, tracking=True)
    rating = fields.Selection(
        [("1", "খুব খারাপ / Very Poor"), ("2", "খারাপ / Poor"),
         ("3", "মোটামুটি / Fair"), ("4", "ভালো / Good"),
         ("5", "খুব ভালো / Excellent")],
        string="Overall Rating (NPS-style)")
    nps_score = fields.Integer(compute="_compute_nps", store=True,
                               help="-100..+100 — detractors(1-3) vs promoters(5)")
    comment = fields.Text()
    source_event_id = fields.Char(readonly=True, index=True,
                                  help="The service_order.closed event — replay key")

    @api.depends("rating")
    def _compute_nps(self):
        for survey in self:
            if not survey.rating:
                survey.nps_score = 0
            elif int(survey.rating) >= 5:
                survey.nps_score = 100
            elif int(survey.rating) <= 3:
                survey.nps_score = -100
            else:
                survey.nps_score = 0

    @api.model
    def consume_order_closed(self, event: dict) -> "FixSurvey | None":
        """T04: journey 1 ends here — the closed event triggers the survey
        (deferred per NT-024, never at completion time). Idempotent on the
        order."""
        order_id = event.get("aggregate_id")
        existing = self.search([("service_order_id", "=", order_id)])
        if existing:
            return existing
        return self.create({
            "service_order_id": order_id,
            "source_event_id": event.get("event_id", ""),
            "state": "sent",
        })


class FixComplaint(models.Model):
    """T02: the complaint lifecycle — complaint -> non-conformance -> root
    cause -> CAPA -> verification -> closure (journey 14)."""

    _name = "fix.complaint"
    _description = "Complaint"
    # P03 workspace data-entry form (discovered by cd_p03_portal).
    _p03_capture = {
        "module": "M34",
        "form": "Complaint",
        "fields": ["name", "customer_id", "category", "severity", "description",
                   "service_order_id"],
    }
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc, id desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    name = fields.Char(required=True)
    customer_id = fields.Many2one("res.partner", string="Customer", required=True,
                                  index=True, ondelete="restrict")
    service_order_id = fields.Many2one("fix.service.order", string="Service Order",
                                       index=True, ondelete="set null")
    category = fields.Selection(
        [("service_quality", "Service Quality"), ("delay", "Delay / SLA"),
         ("billing", "Billing"), ("staff_conduct", "Staff Conduct"),
         ("device_damage", "Device Damage"), ("other", "Other")],
        required=True, default="service_quality")
    severity = fields.Selection(
        [("minor", "Minor"), ("major", "Major"), ("critical", "Critical")],
        default="minor", required=True, tracking=True)
    state = fields.Selection(
        [("new", "New"), ("investigating", "Investigating"),
         ("ncr_raised", "NCR Raised"), ("root_cause", "Root Cause Identified"),
         ("capa_open", "CAPA Open"), ("verification", "Verification"),
         ("closed", "Closed"), ("rejected", "Rejected")],
        default="new", required=True, tracking=True)
    description = fields.Text(required=True)
    resolution = fields.Text()
    # T03: the M23 NCR/CAPA linkage stubs (registered, with expiry)
    ncr_stub_ref = fields.Char(readonly=True,
                               help="AR-006 §5.4 STUB: M23 lands W5 — the NCR "
                                    "reference links then; stub expiry 2027-03-31")
    capa_stub_ref = fields.Char(readonly=True,
                                help="STUB: the CAPA reference links when M23 lands")

    def action_raise_ncr(self):
        """Journey 14: complaint -> NCR. Until M23 (W5), the stub records
        the linkage intent with an expiry — the GV-005 registration."""
        for complaint in self:
            if complaint.state != "investigating":
                raise UserError("Investigate before raising the NCR")
            complaint.write({
                "state": "ncr_raised",
                "ncr_stub_ref": "NCR-STUB/%s" % complaint.id,
            })
            publish(self.env, "complaint.ncr_raised", "fix.complaint",
                    complaint.id, {"complaint": complaint.name,
                                   "stub": True})

    def action_close(self, resolution: str):
        for complaint in self:
            if complaint.severity == "critical" and not complaint.capa_stub_ref:
                raise UserError(
                    "A CRITICAL complaint closes only through CAPA verification "
                    "(journey 14) — no shortcut")
            complaint.write({"state": "closed", "resolution": resolution})


class FixSupplierScorecard(models.Model):
    """M42 (T05/T06): the vendor scorecard — computed FROM consumed M16
    events (goods.received, po.issued), the asymmetric interface. M42 never
    reads M16 tables and M16 never knows M42 exists."""

    _name = "fix.supplier.scorecard"
    _description = "Supplier Scorecard"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _vendor_period_unique = models.Constraint('UNIQUE (vendor_id, period)', 'One scorecard per vendor and period')

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    vendor_id = fields.Many2one("res.partner", string="Vendor", required=True,
                                index=True, ondelete="cascade")
    period = fields.Char(required=True, size=7, index=True,
                         help="YYYY-MM")
    po_count = fields.Integer(default=0, readonly=True)
    lines_on_time = fields.Integer(default=0, readonly=True)
    lines_late = fields.Integer(default=0, readonly=True)
    on_time_pct = fields.Float(compute="_compute_scores", store=True)
    rejection_count = fields.Integer(default=0, readonly=True,
                                     help="From the M52 matcher's blocked invoices")
    score = fields.Float(compute="_compute_scores", store=True,
                         help="0-100: 60% on-time, 40% quality (100 - rejections)")

    @api.depends("lines_on_time", "lines_late", "rejection_count", "po_count")
    def _compute_scores(self):
        for card in self:
            total_lines = card.lines_on_time + card.lines_late
            on_time = (100.0 * card.lines_on_time / total_lines) if total_lines else 100.0
            quality = max(0.0, 100.0 - 10.0 * card.rejection_count)
            card.on_time_pct = round(on_time, 2)
            card.score = round(0.6 * on_time + 0.4 * quality, 2)

    @api.model
    def consume_goods_received(self, event: dict) -> None:
        """Pair 10's consuming half: one goods.received line event scores
        on-time vs late (receipt within the PO's scheduled window)."""
        payload = event.get("payload", {})
        vendor = payload.get("vendor_id")
        if not vendor:
            return
        period = str(payload.get("po_date", fields.Date.today()))[:7]
        card = self.search([("vendor_id", "=", vendor), ("period", "=", period)])
        if not card:
            card = self.create({"vendor_id": vendor, "period": period,
                                "po_count": 0})
        late = bool(payload.get("late", False))
        if late:
            card.lines_late += 1
        else:
            card.lines_on_time += 1

    @api.model
    def publish_all_scorecards(self):
        """T06: scorecards publish through events — the P05 vendor portal
        reads them via the API, never from M42 tables."""
        for card in self.search([]):
            publish(self.env, "supplier.scorecard", "fix.supplier.scorecard",
                    card.id, {
                        "vendor_id": card.vendor_id.id,
                        "period": card.period,
                        "score": card.score,
                        "on_time_pct": card.on_time_pct,
                    })
