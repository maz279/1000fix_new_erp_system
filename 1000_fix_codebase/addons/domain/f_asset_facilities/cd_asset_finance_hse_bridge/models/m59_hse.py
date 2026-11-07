# m59_hse — A07 P1 (2026-11-04), report §6 P1: injuries and unfit safety
# equipment reach M59.
#
# M47 set the BLA 2006 s.80 clock on an injury incident (hse_notice_due_on)
# and M46 flagged an accident with injuries, and the HSE officer heard of
# neither: no case, no Form 27 deadline, no statutory accident register, and
# the incident could close with `hse_case_ref` empty. Now an injury opens ONE
# fix.hse.incident (state Reported: the HSE officer investigates and closes it
# under M59's own DIFE-notice gate). M59 computes its s.80 deadline in
# Bangladesh working days from the accident date; the M47 date stays the
# earlier, calendar-day reminder. The case reference is written back to the
# M47 incident (and the M46 accident). Unfit safety equipment raises ONE open
# hazard per item.
#
# The statutory register M59 opens for a medium/high injury names the worker
# involved. The bridge uses the person who reported the source (their
# employee record); when there is none it does not guess: the hand-off waits
# as a bridge exception until the HSE officer names the worker and retries.
from datetime import datetime, time

from odoo import api, fields, models
from odoo.exceptions import UserError

from .fix_bridge_exception import HSE_OFFICER, PARAM_PREFIX, event_source, run_hook

# BUSINESS SWITCH (B2): M46 records "injuries yes/no" on an accident, not a
# severity. The case opens at this M59 severity until the HSE officer rates
# it. "medium" (the default) is the fail-safe one: it starts the Form 27
# deadline AND the statutory accident register; "low" would start only the
# Form 27(b) minor-injury notice.
VEHICLE_SEVERITY_PARAM = "vehicle_injury_severity"
SEVERITIES = ("low", "medium", "high")
# A07 operability (2026-11-07): what a site incident puts on the M59 hazard
# register. An injury has its own route (the HSE case).
INCIDENT_HAZARD_TYPES = ("fire", "theft", "trespass")
INCIDENT_HAZARD_SEVERITY = {"low": 2, "medium": 3, "high": 4}


def _employee_of(env, user, company):
    if not user:
        return env["hr.employee"]
    return (
        env["hr.employee"]
        .sudo()
        .with_context(active_test=False)
        .search(
            [("user_id", "=", user.id), ("company_id", "in", [company.id, False])],
            order="active desc, id",
            limit=1,
        )
    )


class FixHseIncidentBridge(models.Model):
    _inherit = "fix.hse.incident"

    bridge_source_key = fields.Char(
        string="Raised From",
        readonly=True,
        copy=False,
        index=True,
        help="The M47 incident or M46 accident this case was opened for",
    )
    site_incident_id = fields.Many2one(
        "fix.site.incident", string="Site Incident (M47)", readonly=True, copy=False
    )
    vehicle_accident_id = fields.Many2one(
        "fix.vehicle.accident", string="Vehicle Accident (M46)", readonly=True, copy=False
    )
    source_notice_due_on = fields.Date(
        string="M47 Notice Reminder",
        readonly=True,
        copy=False,
        help="The calendar-day s.80 date M47 set on the incident (never later than the "
        "working-day deadline M59 computes)",
    )

    _bridge_source_unique = models.Constraint(
        "UNIQUE (bridge_source_key)", "One HSE case per source incident or accident."
    )

    def write(self, vals):
        if not self.env.su and {
            "bridge_source_key",
            "site_incident_id",
            "vehicle_accident_id",
            "source_notice_due_on",
        } & set(vals):
            raise UserError(
                "The bridge link of %s is set by the hand-off only." % self._description
            )
        return super().write(vals)

    @api.model
    def _bridge_open_case(self, source, key, vals, event, method):
        """Open the case once for `source`; write its reference back. Returns it."""
        case = self.sudo().search([("bridge_source_key", "=", key)], limit=1)
        if not case:
            company = vals["company_id"]
            hint = self.env["fix.bridge.exception"].hint(key)
            employee = hint.employee_id or _employee_of(
                self.env, source.create_uid, self.env["res.company"].browse(company)
            )
            if vals["severity"] in ("medium", "high") and not employee:
                self.env["fix.bridge.exception"].sudo().record(
                    route="m59_case",
                    key=key,
                    message="%s involves an injury (%s severity): the M59 case opens the "
                    "statutory accident register, which names the worker involved. Nobody "
                    "with an employee record reported it: name the worker (Worker Involved) "
                    "and Retry." % (source.display_name, vals["severity"]),
                    event=event,
                    source=source,
                    consumer=("fix.hse.incident", method),
                    role=HSE_OFFICER,
                    company=self.env["res.company"].browse(company),
                )
                return self.browse()
            vals = dict(vals, bridge_source_key=key, employee_id=employee.id or False)
            case = self.sudo().create(vals)
            case.message_post(
                body="Opened by the A07 bridge from %s. The HSE officer investigates; the "
                "case closes under M59's DIFE-notice gate." % source.display_name
            )
            self.env["fix.bridge.exception"].sudo().resolve(key, "HSE case %s opened" % case.name)
        if "hse_case_ref" in source._fields and source.hse_case_ref != case.name:
            source.sudo()._guarded().write({"hse_case_ref": case.name})
        return case

    @api.model
    def _bridge_case_for_site_incident(self, incidents, event=None):
        cases = self.browse()
        for incident in incidents.sudo().filtered("injuries_flag"):
            site = incident.site_id
            occurred = incident.occurred_on or fields.Date.context_today(self)
            cases |= self._bridge_open_case(
                incident,
                "m59:fix.site.incident:%s" % incident.id,
                {
                    "company_id": (site.company_id or self.env.company).id,
                    "operating_unit_id": site.operating_unit_id.id,
                    "branch_id": site.branch_id.id,
                    "incident_type": "injury",
                    "severity": incident.severity if incident.severity in SEVERITIES else "medium",
                    # the accident date, at its start: the deadline is never later
                    "accident_datetime": datetime.combine(occurred, time.min),
                    "description": "Site incident %s at %s (%s): %s"
                    % (incident.name, site.name, incident.incident_type, incident.description),
                    "site_incident_id": incident.id,
                    "source_notice_due_on": incident.hse_notice_due_on,
                },
                event
                or {
                    "event_type": "site.incident",
                    "aggregate": incident._name,
                    "aggregate_id": incident.id,
                    "payload": {"injuries_flag": True},
                },
                "consume_site_incident",
            )
        return cases

    @api.model
    def consume_site_incident(self, event):
        """site.incident with injuries (M47) -> the HSE case + hse_case_ref back."""
        if not (event.get("payload") or {}).get("injuries_flag"):
            return False
        incident = event_source(self.env, event, "fix.site.incident")
        if not incident:
            return False
        return self._bridge_case_for_site_incident(incident, event)

    @api.model
    def _bridge_case_for_vehicle_accident(self, accidents, event=None):
        cases = self.browse()
        severity = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(PARAM_PREFIX + VEHICLE_SEVERITY_PARAM, "medium")
        )
        if severity not in SEVERITIES:
            severity = "medium"
        for accident in accidents.sudo().filtered("injury"):
            vehicle = accident.vehicle_id
            occurred = accident.occurred_on or fields.Date.context_today(self)
            cases |= self._bridge_open_case(
                accident,
                "m59:fix.vehicle.accident:%s" % accident.id,
                {
                    "company_id": (vehicle.company_id or self.env.company).id,
                    "operating_unit_id": (
                        vehicle.operating_unit_id or vehicle.branch_id.operating_unit_id
                    ).id,
                    "branch_id": vehicle.branch_id.id,
                    "incident_type": "injury",
                    "severity": severity,
                    "accident_datetime": datetime.combine(occurred, time.min),
                    "description": "Vehicle accident %s, %s (driver %s): %s"
                    % (
                        accident.name,
                        vehicle.license_plate or vehicle.name,
                        accident.driver_id.name or "-",
                        accident.description,
                    ),
                    "vehicle_accident_id": accident.id,
                },
                event
                or {
                    "event_type": "vehicle.incident",
                    "aggregate": accident._name,
                    "aggregate_id": accident.id,
                    "payload": {"injuries": True},
                },
                "consume_vehicle_incident",
            )
        return cases

    @api.model
    def consume_vehicle_incident(self, event):
        """vehicle.incident with injuries (M46) -> the HSE case + hse_case_ref back."""
        if not (event.get("payload") or {}).get("injuries"):
            return False
        accident = event_source(self.env, event, "fix.vehicle.accident")
        if not accident:
            return False
        return self._bridge_case_for_vehicle_accident(accident, event)


class FixHseHazardBridge(models.Model):
    _inherit = "fix.hse.hazard"

    bridge_source_key = fields.Char(string="Raised From", readonly=True, copy=False, index=True)
    site_safety_id = fields.Many2one(
        "fix.site.safety", string="Site Safety Equipment (M47)", readonly=True, copy=False
    )
    site_incident_id = fields.Many2one(
        "fix.site.incident", string="Site Incident (M47)", readonly=True, copy=False
    )

    # one OPEN hazard per safety item; a closed one stays the record of the lapse
    _bridge_open_unique = models.UniqueIndex(
        "(bridge_source_key) WHERE bridge_source_key IS NOT NULL AND state != 'closed'",
        "One open hazard per safety equipment item.",
    )

    def write(self, vals):
        if not self.env.su and {"bridge_source_key", "site_safety_id", "site_incident_id"} & set(
            vals
        ):
            raise UserError(
                "The bridge link of %s is set by the hand-off only." % self._description
            )
        return super().write(vals)

    @api.model
    def consume_site_safety_equipment_unfit(self, event):
        """site.safety_equipment_unfit (M47 daily job) -> ONE open hazard per item."""
        item = event_source(self.env, event, "fix.site.safety")
        if not item:
            return False
        payload = event.get("payload") or {}
        key = "m59:fix.site.safety:%s" % item.id
        hazard = self.sudo().search(
            [("bridge_source_key", "=", key), ("state", "!=", "closed")], limit=1
        )
        due = payload.get("due_date") or str(item.next_check or "")
        if hazard:
            if due and due not in (hazard.controls or ""):
                hazard.write(
                    {
                        "controls": "%s\nStill unfit: inspection due %s not recorded."
                        % (hazard.controls or "", due)
                    }
                )
            return hazard
        return self._bridge_safety_hazard(
            item,
            key,
            "Inspection due %s not recorded in M47: the item is unfit until "
            "its check is recorded. The HSE officer rates likelihood and severity." % due,
        )

    @api.model
    def _bridge_safety_hazard(self, item, key, controls):
        site = item.site_id
        label = dict(item._fields["equipment_type"].selection).get(item.equipment_type, "")
        return self.sudo().create(
            {
                "name": "Unfit safety equipment: %s (%s%s) at %s"
                % (item.name, label, ", " + item.ref if item.ref else "", site.name),
                "company_id": (site.company_id or self.env.company).id,
                "operating_unit_id": site.operating_unit_id.id,
                "branch_id": site.branch_id.id,
                "hazard_type": "other",
                "controls": controls,
                "bridge_source_key": key,
                "site_safety_id": item.id,
            }
        )

    @api.model
    def consume_site_safety_check_failed(self, event):
        """site.safety_check_failed (M47) -> ONE open hazard per item, or the
        finding added to the one already open."""
        item = event_source(self.env, event, "fix.site.safety")
        if not item:
            return False
        payload = event.get("payload") or {}
        key = "m59:fix.site.safety:%s" % item.id
        text = "Failed its check on %s: %s." % (
            payload.get("checked_on") or "-",
            payload.get("finding") or "-",
        )
        hazard = self.sudo().search(
            [("bridge_source_key", "=", key), ("state", "!=", "closed")], limit=1
        )
        if hazard:
            if text not in (hazard.controls or ""):
                hazard.write({"controls": "%s\n%s" % (hazard.controls or "", text)})
            return hazard
        return self._bridge_safety_hazard(
            item,
            key,
            "%s The item is unfit until a check passes. The HSE officer rates likelihood and "
            "severity." % text,
        )

    @api.model
    def consume_site_incident(self, event):
        """site.incident (M47: a fire, a theft or a trespass) -> ONE hazard per
        incident for the HSE officer to assess. An injury opens its HSE case."""
        incident = event_source(self.env, event, "fix.site.incident")
        if not incident or incident.incident_type not in INCIDENT_HAZARD_TYPES:
            return False
        key = "m59:fix.site.incident:%s" % incident.id
        hazard = (
            self.sudo()
            .with_context(active_test=False)
            .search([("bridge_source_key", "=", key)], limit=1)
        )
        if hazard:
            return hazard
        site = incident.site_id
        label = dict(incident._fields["incident_type"].selection)[incident.incident_type]
        return self.sudo().create(
            {
                "name": "%s at %s: incident %s" % (label, site.name, incident.name),
                "company_id": (site.company_id or self.env.company).id,
                "operating_unit_id": site.operating_unit_id.id,
                "branch_id": site.branch_id.id,
                "hazard_type": "other",
                "severity": INCIDENT_HAZARD_SEVERITY.get(incident.severity, 3),
                "controls": "Reported in M47 on %s: %s. The HSE officer assesses it and records "
                "the controls." % (incident.occurred_on, incident.description),
                "bridge_source_key": key,
                "site_incident_id": incident.id,
            }
        )


class FixSiteIncidentBridge(models.Model):
    _inherit = "fix.site.incident"

    def write(self, vals):
        """An injury ticked after the incident was reported: M47 publishes
        site.incident on create only, so the case is opened from here."""
        injured = vals.get("injuries_flag") or vals.get("incident_type") == "injury"
        newly = self.filtered(lambda r: not r.injuries_flag) if injured else None
        result = super().write(vals)
        if newly:
            Case = self.env["fix.hse.incident"].sudo()
            run_hook(self.env, "m59_site_incident", Case._bridge_case_for_site_incident, newly)
        if "occurred_on" in vals:
            run_hook(self.env, "m59_site_incident_date", self._bridge_case_redate)
        return result

    def _bridge_case_redate(self):
        """The accident date moved: the case's reminder follows M47's new date.
        Its own working-day deadline stays M59's to correct."""
        Case = self.env["fix.hse.incident"].sudo()
        for incident in self.sudo():
            case = Case.search([("site_incident_id", "=", incident.id)], limit=1)
            if case and case.source_notice_due_on != incident.hse_notice_due_on:
                case.write({"source_notice_due_on": incident.hse_notice_due_on})
                case.message_post(
                    body="M47 corrected the accident date of %s to %s: check the accident date "
                    "here." % (incident.name, incident.occurred_on)
                )


class FixVehicleAccidentBridge(models.Model):
    _inherit = "fix.vehicle.accident"

    hse_case_ref = fields.Char(string="HSE Case (M59)", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"hse_case_ref"}

    def write(self, vals):
        """An injury recorded after the accident was reported (M46 publishes
        vehicle.incident on create only)."""
        newly = self.filtered(lambda r: not r.injury) if vals.get("injury") else None
        result = super().write(vals)
        if newly:
            Case = self.env["fix.hse.incident"].sudo()
            run_hook(
                self.env, "m59_vehicle_accident", Case._bridge_case_for_vehicle_accident, newly
            )
        return result
