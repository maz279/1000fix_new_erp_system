# m49_lease — A07 P1 (2026-11-04), report §6 P1: the M47 lease reaches IFRS 16.
#
# M47 records the lease and publishes versioned data extracts; it never
# computes the right-of-use asset or the liability (BRU-FAC-13). M49 had no
# lease until finance keyed one by hand, so the branch rents on the estate
# register and the IFRS 16 book were two unlinked truths. Now:
#   lease.recorded / lease.extract_published -> ONE draft fix.lease per M47
#   lease, kept in step with each new extract version while it is a draft;
#   finance completes it (IBR, accounts, category) and commences it with
#   M49's own Activate. After commencement a new version changes nothing in
#   the book: it raises a modification item finance remeasures (IFRS 16.44-46).
import json

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError

from .fix_bridge_exception import ACCOUNTANT, ACCOUNTING_MANAGER, event_source, require_role


def _term_months(start, end):
    if not start or not end:
        return 0
    term = relativedelta(end, start)
    return term.years * 12 + term.months + (1 if term.days else 0)


class FixLeaseBridge(models.Model):
    _inherit = "fix.lease"

    site_lease_id = fields.Many2one(
        "fix.site.lease",
        string="M47 Lease",
        readonly=True,
        copy=False,
        index=True,
        help="The estate lease this IFRS 16 contract was drafted from",
    )
    site_extract_version = fields.Integer(
        string="M47 Extract Version Applied", readonly=True, copy=False
    )
    site_escalation_pct = fields.Float(
        string="M47 Escalation % a Year",
        readonly=True,
        copy=False,
        help="From the M47 lease. This contract carries a flat payment: finance decides how "
        "the escalation enters the measurement before commencing.",
    )
    site_deposit = fields.Monetary(string="M47 Security Deposit", readonly=True, copy=False)
    modification_item_ids = fields.One2many(
        "fix.lease.modification.item", "lease_id", string="Modification Items"
    )

    _site_lease_unique = models.Constraint(
        "UNIQUE (site_lease_id)", "One IFRS 16 contract per M47 lease."
    )

    def write(self, vals):
        if not self.env.su and {"site_lease_id", "site_extract_version"} & set(vals):
            raise UserError("The M47 link of a lease is set by the bridge only.")
        return super().write(vals)

    def action_activate(self):
        """A07 P1: a contract drafted from M47 has no incremental borrowing rate
        (M47 does not hold one). Commencing it at 0% would recognise the
        undiscounted rent as the liability, so it is refused until finance
        enters the rate."""
        for rec in self:
            if rec.site_lease_id and not rec.ibr_percent:
                raise UserError(
                    "%s was drafted from M47 lease %s: enter the incremental borrowing rate "
                    "before commencing it." % (rec.name, rec.site_lease_id.name)
                )
        return super().action_activate()

    # ---- the consumers ---------------------------------------------------------
    @api.model
    def _bridge_terms(self, site_lease, extract=None):
        """The contract terms from the extract (the published version) or, for
        lease.recorded, from the M47 lease itself."""
        if extract:
            start = fields.Date.to_date(extract.get("commencement")) or site_lease.start_date
            end = fields.Date.to_date(extract.get("end_date")) or site_lease.end_date
            return {
                "commencement_date": start,
                "term_months": int(extract.get("term_months") or _term_months(start, end)),
                "payment_amount": float(extract.get("monthly_rent") or 0.0),
                "site_escalation_pct": float(extract.get("escalation_pct") or 0.0),
                "site_deposit": float(extract.get("deposit") or 0.0),
            }
        return {
            "commencement_date": site_lease.start_date,
            "term_months": _term_months(site_lease.start_date, site_lease.end_date),
            "payment_amount": float(site_lease.monthly_rent or 0.0),
            "site_escalation_pct": float(site_lease.escalation_pct or 0.0),
            "site_deposit": float(site_lease.deposit or 0.0),
        }

    @api.model
    def _bridge_terms_problem(self, terms):
        if not terms["commencement_date"] or terms["term_months"] <= 0:
            return "it has no start and end date"
        if terms["payment_amount"] <= 0:
            return "it has no monthly rent"
        return ""

    @api.model
    def _bridge_hold(self, site_lease, problem, event, method):
        site = site_lease.site_id
        self.env["fix.bridge.exception"].sudo().record(
            route="m49_lease",
            key="m49_lease:%s" % site_lease.id,
            message="M47 lease %s cannot be drafted under IFRS 16: %s. Correct the lease in "
            "M47 (Open Modification), then Retry." % (site_lease.name, problem),
            event=event,
            source=site_lease,
            consumer=("fix.lease", method),
            role=ACCOUNTANT,
            company=site.company_id,
        )
        return self.browse()

    @api.model
    def _bridge_draft(self, site_lease, terms, version, event, method):
        problem = self._bridge_terms_problem(terms)
        if problem:
            return self._bridge_hold(site_lease, problem, event, method)
        site = site_lease.site_id
        lease = self.sudo().create(
            dict(
                terms,
                company_id=(site.company_id or self.env.company).id,
                operating_unit_id=site.operating_unit_id.id,
                name="%s — %s" % (site_lease.name, site.name),
                partner_id=site_lease.lessor_id.id,
                site_lease_id=site_lease.id,
                site_extract_version=version,
                ibr_percent=0.0,
            )
        )
        lease.message_post(
            body="Drafted from M47 lease %s (extract v%s). Finance completes the incremental "
            "borrowing rate, the right-of-use category and the accounts, decides the "
            "short-term / low-value exemption and how the %.2f%% escalation enters the "
            "measurement, then commences it. The %.2f deposit is refundable and is not part "
            "of the right-of-use asset."
            % (
                site_lease.name,
                version,
                terms["site_escalation_pct"],
                terms["site_deposit"],
            )
        )
        self.env["fix.bridge.exception"].sudo().resolve(
            "m49_lease:%s" % site_lease.id, "draft lease %s created" % lease.reference
        )
        return lease

    @api.model
    def consume_lease_recorded(self, event):
        """lease.recorded -> the draft contract, once per M47 lease."""
        site_lease = event_source(self.env, event, "fix.site.lease")
        if not site_lease:
            return False
        lease = self.sudo().search([("site_lease_id", "=", site_lease.id)], limit=1)
        if lease:
            return lease
        return self._bridge_draft(
            site_lease, self._bridge_terms(site_lease), 0, event, "consume_lease_recorded"
        )

    @api.model
    def consume_lease_extract_published(self, event):
        """lease.extract_published -> update the draft to the new version, or,
        once commenced, a modification item. Idempotent per (lease, version)."""
        site_lease = event_source(self.env, event, "fix.site.lease")
        if not site_lease:
            return False
        payload = event.get("payload") or {}
        version = int(payload.get("version") or 0)
        extract = payload.get("extract") or {}
        terms = self._bridge_terms(site_lease, extract)
        lease = self.sudo().search([("site_lease_id", "=", site_lease.id)], limit=1)
        if not lease:
            lease = self._bridge_draft(
                site_lease, terms, version, event, "consume_lease_extract_published"
            )
        elif version <= lease.site_extract_version:
            return lease  # this version is already applied (redelivery)
        elif lease.state == "draft":
            problem = self._bridge_terms_problem(terms)
            if problem:
                return self._bridge_hold(
                    site_lease, problem, event, "consume_lease_extract_published"
                )
            before = {k: lease[k] for k in terms}
            lease.write(dict(terms, site_extract_version=version))
            changed = ", ".join(
                "%s %s -> %s" % (lease._fields[k].string, before[k], terms[k])
                for k in terms
                if before[k] != terms[k]
            )
            lease.message_post(
                body="M47 extract v%s (%s) applied to the draft: %s."
                % (version, payload.get("reason") or "-", changed or "no term changed")
            )
        else:
            self.env["fix.lease.modification.item"].sudo()._bridge_raise(
                lease, site_lease, version, payload
            )
            lease.sudo().write({"site_extract_version": version})
        if lease:
            extract_row = (
                self.env["fix.site.lease.extract"]
                .sudo()
                .search([("lease_id", "=", site_lease.id), ("version", "=", version)], limit=1)
            )
            if extract_row and not extract_row.consumed_by_m19_at:
                extract_row._guarded().write({"consumed_by_m19_at": fields.Datetime.now()})
        return lease

    @api.model
    def _bridge_modified_extract(self, site_lease, after):
        """The 'modified' extract version a lease.modified event produced: the
        earliest whose terms are the event's `after` terms. M47 publishes it
        in the same transaction as the event (action_apply_modification)."""

        def same(extract):
            try:
                data = json.loads(extract.payload or "{}")
            except ValueError:
                return False
            return (
                str(data.get("end_date")) == str(after.get("end_date"))
                and abs(
                    float(data.get("monthly_rent") or 0.0) - float(after.get("monthly_rent") or 0.0)
                )
                < 0.005
                and abs(
                    float(data.get("escalation_pct") or 0.0)
                    - float(after.get("escalation_pct") or 0.0)
                )
                < 0.0001
            )

        extracts = site_lease.sudo().extract_ids.filtered(
            lambda e: e.reason == "modified" and same(e)
        )
        return extracts.sorted("version")

    @api.model
    def consume_lease_modified(self, event):
        """lease.modified (M47 applied an approved renewal / modification:
        BRU-FAC-14, an IFRS 16 remeasurement trigger) -> treated as the new
        extract version it published: the draft contract follows it, a
        commenced contract gets a fix.lease.modification.item for finance.
        Idempotent with lease.extract_published: one version is applied once,
        whichever of the two events arrives first."""
        site_lease = event_source(self.env, event, "fix.site.lease")
        if not site_lease:
            return False
        payload = event.get("payload") or {}
        after = payload.get("after") or {}
        lease = self.sudo().search([("site_lease_id", "=", site_lease.id)], limit=1)
        applied = lease.site_extract_version if lease else 0
        candidates = self._bridge_modified_extract(site_lease, after)
        pending = candidates.filtered(lambda e: e.version > applied)
        if not pending:
            if candidates:
                return lease  # its version is already applied (redelivery)
            return self._bridge_hold(
                site_lease,
                "the modification (%s) has no published extract with its terms"
                % (payload.get("reason") or "-"),
                event,
                "consume_lease_modified",
            )
        extract = pending[0]
        return self.consume_lease_extract_published(
            dict(
                event,
                payload={
                    "lease": site_lease.name,
                    "version": extract.version,
                    "reason": extract.reason,
                    "extract": json.loads(extract.payload or "{}"),
                },
            )
        )


class FixLeaseModificationItem(models.Model):
    """An M47 change after commencement: finance remeasures (IFRS 16.44-46)."""

    _name = "fix.lease.modification.item"
    _description = "IFRS 16 Lease Modification Item"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "state, create_date desc, id desc"

    _version_unique = models.Constraint(
        "UNIQUE (site_lease_id, version)", "One modification item per M47 lease version."
    )

    name = fields.Char(required=True, readonly=True)
    lease_id = fields.Many2one("fix.lease", required=True, readonly=True, index=True)
    site_lease_id = fields.Many2one("fix.site.lease", required=True, readonly=True, index=True)
    company_id = fields.Many2one(related="lease_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="lease_id.operating_unit_id", store=True, index=True
    )
    version = fields.Integer(required=True, readonly=True)
    reason = fields.Char(readonly=True)
    extract = fields.Text(readonly=True, help="The M47 extract of this version")
    changes = fields.Text(readonly=True, help="Terms that differ from the commenced contract")
    state = fields.Selection(
        [
            ("open", "Open: Remeasure"),
            ("remeasured", "Remeasured"),
            ("no_change", "No Accounting Change"),
        ],
        default="open",
        required=True,
        index=True,
        tracking=True,
    )
    decided_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    decided_on = fields.Datetime(readonly=True, copy=False)
    decision_note = fields.Text()

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields() | {
            "name",
            "lease_id",
            "site_lease_id",
            "version",
            "reason",
            "extract",
            "changes",
            "state",
            "decided_by_id",
            "decided_on",
        }
        if any(rec.state != "open" for rec in self):
            guarded.add("decision_note")
        return guarded

    def unlink(self):
        if not self.env.su:
            raise UserError("A lease modification item is part of the record.")
        return super().unlink()

    @api.model
    def _bridge_raise(self, lease, site_lease, version, payload):
        existing = self.sudo().search(
            [("site_lease_id", "=", site_lease.id), ("version", "=", version)], limit=1
        )
        if existing:
            return existing
        terms = self.env["fix.lease"]._bridge_terms(site_lease, payload.get("extract") or {})
        changes = [
            "%s: %s -> %s" % (lease._fields[k].string, lease[k], v)
            for k, v in terms.items()
            if lease[k] != v
        ]
        item = (
            self.sudo()
            ._guarded()
            .create(
                {
                    "name": "%s v%s" % (site_lease.name, version),
                    "lease_id": lease.id,
                    "site_lease_id": site_lease.id,
                    "version": version,
                    "reason": payload.get("reason") or False,
                    "extract": json.dumps(payload.get("extract") or {}, sort_keys=True),
                    "changes": "\n".join(changes) or "No contract term differs.",
                }
            )
        )
        lease.message_post(
            body="M47 published extract v%s after commencement: modification item %s raised "
            "for remeasurement. Nothing was changed in the book." % (version, item.name)
        )
        return item

    def _decide(self, state, note):
        require_role(
            self.env, [ACCOUNTANT, ACCOUNTING_MANAGER], "Deciding a lease modification item"
        )
        for rec in self:
            if rec.state != "open":
                raise UserError("%s is already decided." % rec.name)
            text = (note or rec.decision_note or "").strip()
            if not text:
                raise UserError("Record how %s was dealt with (Decision Note)." % rec.name)
            rec.sudo()._guarded().write(
                {
                    "state": state,
                    "decision_note": text,
                    "decided_by_id": self.env.uid,
                    "decided_on": fields.Datetime.now(),
                }
            )
            rec.lease_id.message_post(body="%s: %s (%s)." % (rec.name, text, state))
        return True

    def action_mark_remeasured(self, note=None):
        """Finance remeasured the liability and the ROU asset for this version."""
        return self._decide("remeasured", note)

    def action_mark_no_change(self, note=None):
        """The version changes nothing IFRS 16 measures (e.g. a notice period)."""
        return self._decide("no_change", note)
