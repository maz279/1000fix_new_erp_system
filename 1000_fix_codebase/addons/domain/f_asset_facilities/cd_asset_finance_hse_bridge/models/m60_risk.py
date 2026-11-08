# m60_risk — A07 P1 (2026-11-04), report §6 P1: compliance lapses reach M60.
#
# A site operating on a lapsed licence, a driver on an expired licence and a
# vehicle on an expired statutory document were each an M47/M46 alert that the
# risk register never held, so the board's risk view showed none of them.
# Each lapse now raises or updates ONE open fix.risk.register entry per
# SUBJECT (the site, the driver, the vehicle): a second lapse on the same
# subject adds to the open entry instead of a duplicate, and once the risk
# owner closes the entry a new lapse opens a new one. The entry is raised at
# the register's default scoring and with no owner: scoring and the owner are
# the risk function's decision, not the bridge's.
from odoo import api, fields, models
from odoo.exceptions import UserError

from .fix_bridge_exception import event_source

# A07 operability (2026-11-07): the site incidents the risk register holds.
INCIDENT_RISK_TYPES = ("fire", "theft", "trespass", "injury")


class FixRiskRegisterBridge(models.Model):
    _inherit = "fix.risk.register"

    bridge_subject_key = fields.Char(string="Subject Key", readonly=True, copy=False, index=True)
    bridge_subject_ref = fields.Char(string="Subject", readonly=True, copy=False)
    bridge_trigger_count = fields.Integer(string="Lapses Recorded", readonly=True, copy=False)
    bridge_last_trigger = fields.Char(string="Last Lapse", readonly=True, copy=False)
    bridge_last_trigger_on = fields.Date(string="Last Lapse On", readonly=True, copy=False)
    bridge_lapse_log = fields.Text(
        string="Lapses Recorded (Bridge)",
        readonly=True,
        copy=False,
        help="Each lapse and decision the source modules reported on this subject",
    )

    _bridge_open_unique = models.UniqueIndex(
        "(bridge_subject_key) WHERE bridge_subject_key IS NOT NULL AND state != 'closed'",
        "One open risk entry per subject.",
    )

    def write(self, vals):
        if not self.env.su and any(k.startswith("bridge_") for k in vals):
            raise UserError("The bridge fields of a risk entry are set by the hand-off only.")
        return super().write(vals)

    @api.model
    def _bridge_open_entry(self, subject):
        key = "m60:%s:%s" % (subject._name, subject.id)
        return self.sudo().search(
            [("bridge_subject_key", "=", key), ("state", "!=", "closed")], limit=1
        )

    def _bridge_log(self, trigger, trigger_key):
        """Add a line to this open entry without counting it as a lapse (a
        warning, a recovery). Idempotent on `trigger_key`."""
        self.ensure_one()
        seen = "[%s]" % trigger_key
        if seen in (self.bridge_lapse_log or ""):
            return self
        self.sudo().write(
            {
                "bridge_lapse_log": "%s\n%s %s %s"
                % (self.bridge_lapse_log or "", fields.Date.context_today(self), seen, trigger)
            }
        )
        self.message_post(body="Reported by the source: %s" % trigger)
        return self

    @api.model
    def _bridge_raise(
        self,
        subject,
        label,
        company,
        operating_unit,
        trigger,
        trigger_key,
        category="compliance",
        likelihood=None,
        impact=None,
    ):
        """Raise or update the subject's ONE open entry. `trigger_key` makes a
        redelivered event a no-op. Returns the entry. `category`, `likelihood`
        and `impact` apply to a new entry only: an open entry keeps the risk
        function's scoring."""
        key = "m60:%s:%s" % (subject._name, subject.id)
        Risk = self.sudo()
        risk = self._bridge_open_entry(subject)
        seen = "[%s]" % trigger_key
        today = fields.Date.context_today(self)
        if risk:
            if seen in (risk.bridge_lapse_log or ""):
                return risk  # this lapse is already on the entry
            risk.write(
                {
                    "bridge_trigger_count": risk.bridge_trigger_count + 1,
                    "bridge_last_trigger": trigger,
                    "bridge_last_trigger_on": today,
                    "bridge_lapse_log": "%s\n%s %s %s"
                    % (risk.bridge_lapse_log or "", today, seen, trigger),
                }
            )
            risk.message_post(body="Another lapse on %s: %s" % (label, trigger))
            return risk
        scoring = {k: v for k, v in (("likelihood", likelihood), ("impact", impact)) if v}
        risk = Risk.create(
            {
                **scoring,
                "name": "%s: %s" % (label, trigger),
                "category": category,
                "company_id": company.id,
                "operating_unit_id": operating_unit.id,
                "bridge_subject_key": key,
                "bridge_subject_ref": label,
                "bridge_trigger_count": 1,
                "bridge_last_trigger": trigger,
                "bridge_last_trigger_on": today,
                "bridge_lapse_log": "%s %s %s" % (today, seen, trigger),
            }
        )
        risk.message_post(
            body="Raised from %s. Scored %s and with no owner: the risk function assigns the "
            "owner and scores it."
            % (label, "low (2 x 2)" if scoring else "at the register default")
        )
        return risk

    @api.model
    def _bridge_site(self, site):
        return (
            site,
            "Site %s" % site.name,
            site.company_id or self.env.company,
            site.operating_unit_id,
        )

    @api.model
    def consume_site_risk_exception_raised(self, event):
        """site.risk_exception_raised (a site operating on a lapsed licence)."""
        exc = event_source(self.env, event, "fix.site.risk.exception")
        if not exc:
            return False
        payload = event.get("payload") or {}
        subject, label, company, ou = self._bridge_site(exc.site_id)
        trigger = (
            "operating-risk exception %s: %s (%s) lapsed %s, %s severity, decision "
            "required"
            % (
                exc.name,
                payload.get("licence") or exc.licence_id.name or "-",
                payload.get("licence_type") or "-",
                payload.get("expiry") or "-",
                payload.get("severity") or exc.severity,
            )
        )
        return self._bridge_raise(subject, label, company, ou, trigger, "exc:%s" % exc.id)

    @api.model
    def consume_site_incident(self, event):
        """site.incident (M47: a fire, a theft, a trespass or an injury) -> the
        site's ONE open entry, each incident logged on it."""
        incident = event_source(self.env, event, "fix.site.incident")
        if not incident or not (
            incident.incident_type in INCIDENT_RISK_TYPES or incident.injuries_flag
        ):
            return False
        subject, label, company, ou = self._bridge_site(incident.site_id)
        kind = dict(incident._fields["incident_type"].selection)[incident.incident_type]
        trigger = "%s incident %s on %s, %s severity" % (
            kind,
            incident.name,
            incident.occurred_on or "-",
            incident.severity or "-",
        )
        return self._bridge_raise(
            subject,
            label,
            company,
            ou,
            trigger,
            "inc:%s:%s" % (incident.id, incident.incident_type),
            category="operational",
        )

    @api.model
    def consume_site_compliance_expired(self, event):
        """site.compliance_expired (a site licence passed its expiry)."""
        licence = event_source(self.env, event, "fix.site.licence")
        if not licence:
            return False
        payload = event.get("payload") or {}
        subject, label, company, ou = self._bridge_site(licence.site_id)
        trigger = "licence %s (%s) expired %s" % (
            payload.get("licence") or licence.name,
            payload.get("licence_type") or "-",
            payload.get("expiry") or "-",
        )
        return self._bridge_raise(
            subject,
            label,
            company,
            ou,
            trigger,
            "lic:%s:%s" % (licence.id, payload.get("expiry") or ""),
        )

    @api.model
    def consume_site_risk_decision_recorded(self, event):
        """site.risk_decision_recorded: the continue/suspend decision goes on the
        site's open entry (it never closes the entry: the risk owner does)."""
        exc = event_source(self.env, event, "fix.site.risk.exception")
        if not exc:
            return False
        payload = event.get("payload") or {}
        key = "m60:fix.site:%s" % exc.site_id.id
        risk = self.sudo().search(
            [("bridge_subject_key", "=", key), ("state", "!=", "closed")], limit=1
        )
        if not risk:
            return False
        seen = "[dec:%s:%s]" % (exc.id, payload.get("decision") or "")
        if seen in (risk.bridge_lapse_log or ""):
            return risk
        risk.write(
            {
                "bridge_lapse_log": "%s\n%s %s decision on %s: %s by %s, review %s"
                % (
                    risk.bridge_lapse_log or "",
                    fields.Date.context_today(self),
                    seen,
                    exc.name,
                    payload.get("decision") or "-",
                    payload.get("decided_by") or "-",
                    payload.get("review_due_on") or "-",
                )
            }
        )
        return risk

    @api.model
    def consume_driver_licence_expired(self, event):
        """driver.licence_expired (M46): a driver on an expired licence."""
        driver = event_source(self.env, event, "fix.driver")
        if not driver:
            return False
        payload = event.get("payload") or {}
        employee = driver.employee_id
        trigger = "driving licence (%s) expired %s" % (
            payload.get("licence_class") or "-",
            payload.get("expiry_date") or driver.license_expiry or "-",
        )
        return self._bridge_raise(
            driver,
            "Driver %s" % driver.name,
            employee.company_id or self.env.company,
            self.env["operating.unit"],
            trigger,
            "drv:%s:%s" % (driver.id, payload.get("expiry_date") or ""),
        )

    @api.model
    def consume_vehicle_document_expired(self, event):
        """vehicle.document_expired (M46): a vehicle on an expired statutory document."""
        doc = event_source(self.env, event, "fix.vehicle.document")
        if not doc:
            return False
        payload = event.get("payload") or {}
        vehicle = doc.vehicle_id
        trigger = "%s %s expired %s" % (
            payload.get("doc_type") or "-",
            payload.get("document") or doc.display_name,
            payload.get("expiry_date") or "-",
        )
        return self._bridge_raise(
            vehicle,
            "Vehicle %s" % (vehicle.license_plate or vehicle.name),
            vehicle.company_id or self.env.company,
            vehicle.operating_unit_id or vehicle.branch_id.operating_unit_id,
            trigger,
            "doc:%s:%s" % (doc.id, payload.get("expiry_date") or ""),
        )

    # ---- A07 P1 wiring (2026-11-04): M45 losses, M47 lease continuity ----------
    @api.model
    def _bridge_equipment(self, equipment):
        eq = equipment.sudo()
        return (
            eq,
            "Equipment %s" % (eq.code or eq.name),
            eq.company_id or self.env.company,
            eq.operating_unit_id or eq.branch_id.operating_unit_id,
        )

    @api.model
    def consume_equipment_lost(self, event):
        """equipment.lost (M45: not found at a physical verification) -> ONE
        open operational risk entry per item (a lost test instrument is a loss
        and a custody failure until the risk owner closes it)."""
        verification = event_source(self.env, event, "fix.equipment.verification")
        if not verification:
            return False
        payload = event.get("payload") or {}
        subject, label, company, ou = self._bridge_equipment(verification.equipment_id)
        trigger = "missing at verification %s (campaign %s), last custodian %s, value %.2f" % (
            verification.name,
            payload.get("campaign") or verification.campaign_ref or "-",
            payload.get("custodian") or "-",
            float(payload.get("value") or 0.0),
        )
        return self._bridge_raise(
            subject,
            label,
            company,
            ou,
            trigger,
            "lost:%s" % verification.id,
            category="operational",
        )

    @api.model
    def consume_equipment_recovered(self, event):
        """equipment.recovered -> the recovery goes on the item's open entry.
        It never closes the entry: how the item went missing is the risk
        owner's to review."""
        verification = event_source(self.env, event, "fix.equipment.verification")
        if not verification:
            return False
        risk = self._bridge_open_entry(verification.equipment_id)
        if not risk:
            return False
        payload = event.get("payload") or {}
        return risk._bridge_log(
            "found at verification %s (missing since %s): the entry stays open for the risk "
            "owner" % (verification.name, payload.get("missing_since") or "-"),
            "rec:%s" % verification.id,
        )

    @api.model
    def _bridge_lease(self, site_lease):
        site = site_lease.sudo().site_id
        return (
            site_lease.sudo(),
            "Lease %s (%s)" % (site_lease.name, site.name or "-"),
            site.company_id or self.env.company,
            site.operating_unit_id,
        )

    @api.model
    def consume_lease_renewal_decision_required(self, event):
        """lease.renewal_decision_required (M47, daily inside 30 days of the
        notice deadline) -> ONE open operational entry per lease: the branch's
        premises are at risk until the CFO decides. Each reminder is logged."""
        site_lease = event_source(self.env, event, "fix.site.lease")
        if not site_lease:
            return False
        payload = event.get("payload") or {}
        subject, label, company, ou = self._bridge_lease(site_lease)
        days = payload.get("days_left")
        trigger = "renewal decision required by %s (%s day(s) left, %s)" % (
            payload.get("deadline") or "-",
            "-" if days is None else days,
            payload.get("responsible_role") or "CFO",
        )
        return self._bridge_raise(
            subject,
            label,
            company,
            ou,
            trigger,
            "ren:%s:%s:%s" % (site_lease.id, payload.get("deadline"), days),
            category="operational",
        )

    @api.model
    def consume_lease_critical_date_due(self, event):
        """lease.critical_date_due (M47 expiry horizons) -> the same entry per
        lease, each alert logged on it."""
        site_lease = event_source(self.env, event, "fix.site.lease")
        if not site_lease:
            return False
        payload = event.get("payload") or {}
        subject, label, company, ou = self._bridge_lease(site_lease)
        days = payload.get("days_left")
        kind = payload.get("event_type") or "critical date"
        trigger = "lease %s due %s (%s day(s) left)" % (
            kind,
            payload.get("due_on") or "-",
            "-" if days is None else days,
        )
        return self._bridge_raise(
            subject,
            label,
            company,
            ou,
            trigger,
            "crit:%s:%s:%s:%s" % (site_lease.id, kind, payload.get("due_on"), days),
            category="operational",
        )

    @api.model
    def consume_site_compliance_expiring(self, event):
        """site.compliance_expiring (M47 licence alert at 90/60/30/15/7 days)
        -> logged on the site's open entry; with none open, ONE is opened at
        low scoring (2 x 2), as site.compliance_expired opens one per site."""
        licence = event_source(self.env, event, "fix.site.licence")
        if not licence:
            return False
        payload = event.get("payload") or {}
        subject, label, company, ou = self._bridge_site(licence.site_id)
        days = payload.get("days_remaining")
        trigger = "licence %s (%s) expires %s, %s day(s) left" % (
            payload.get("licence") or licence.name,
            payload.get("licence_type") or "-",
            payload.get("expiry") or "-",
            "-" if days is None else days,
        )
        trigger_key = "exp:%s:%s:%s" % (licence.id, payload.get("expiry") or "", days)
        risk = self._bridge_open_entry(subject)
        if risk:
            return risk._bridge_log(trigger, trigger_key)
        return self._bridge_raise(
            subject, label, company, ou, trigger, trigger_key, likelihood="2", impact="2"
        )
