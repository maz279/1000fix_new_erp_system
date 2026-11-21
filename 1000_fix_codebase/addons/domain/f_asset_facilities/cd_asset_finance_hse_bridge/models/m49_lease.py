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

from .fix_bridge_exception import (
    ACCOUNTANT,
    ACCOUNTING_MANAGER,
    dhaka_today,
    event_source,
    param_float,
    param_str,
    require_role,
    role_account,
    run_hook,
)

# D5(e): exemptions (IFRS 16.5-8). The owner set the figures; finance confirms
# the BDT one. Both are parameters.
SHORT_TERM_PARAM = "ifrs16_short_term_max_months"
SHORT_TERM_DEFAULT = 12.0
LOW_VALUE_PARAM = "ifrs16_low_value_max_bdt"
LOW_VALUE_DEFAULT = 500000.0
FREQUENCY = {"monthly": "1", "quarterly": "3", "half_yearly": "6", "yearly": "12"}


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
        help="From the M47 lease; measured in the liability as the contract's fixed annual "
        "escalation (D5b).",
    )
    vehicle_id = fields.Many2one(
        "fleet.vehicle",
        string="M46 Leased Vehicle",
        readonly=True,
        copy=False,
        index=True,
        help="FIN-09 / D5(d): the leased van or motorbike this contract was drafted from",
    )
    remeasurement_ids = fields.One2many(
        "fix.lease.remeasurement", "lease_id", string="Remeasurements"
    )
    site_deposit = fields.Monetary(string="M47 Security Deposit", readonly=True, copy=False)
    modification_item_ids = fields.One2many(
        "fix.lease.modification.item", "lease_id", string="Modification Items"
    )

    _site_lease_unique = models.Constraint(
        "UNIQUE (site_lease_id)", "One IFRS 16 contract per M47 lease."
    )

    def write(self, vals):
        if not self.env.su and {"site_lease_id", "site_extract_version", "vehicle_id"} & set(vals):
            raise UserError("The M47 / M46 link of a lease is set by the bridge only.")
        return super().write(vals)

    @api.model
    def _bridge_defaults(self, company):
        """D2: the IFRS 16 accounts and the right-of-use category a drafted
        contract starts with (account roles ifrs16_liability / ifrs16_interest /
        ifrs16_clearing, category code ROU). Finance can still change them
        before commencing; unset roles stay empty (activation fails closed)."""
        vals = {}
        for field, key in (
            ("liability_account_id", "ifrs16_liability"),
            ("interest_account_id", "ifrs16_interest"),
            ("payment_account_id", "ifrs16_clearing"),
        ):
            account = role_account(self.env, company, key)
            if account:
                vals[field] = account.id
        code = param_str(self.env, "rou_category_code", "ROU")
        category = (
            self.env["fix.asset.category"]
            .sudo()
            .search([("company_id", "=", company.id), ("code", "=", code)], limit=1)
        )
        if category:
            vals["category_id"] = category.id
        return vals

    @api.model
    def _bridge_exemption(self, term_months, new_value=0.0):
        """D5(e): a lease of 12 months or less, or of an asset worth BDT 500,000
        or less new, is expensed (IFRS 16.5); otherwise it is on the book."""
        if term_months and term_months <= param_float(
            self.env, SHORT_TERM_PARAM, SHORT_TERM_DEFAULT
        ):
            return "short_term"
        if new_value and new_value <= param_float(self.env, LOW_VALUE_PARAM, LOW_VALUE_DEFAULT):
            return "low_value"
        return "none"

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
            if rec.vehicle_id and not rec.ibr_percent:
                raise UserError(
                    "%s was drafted from leased vehicle %s: enter the incremental borrowing "
                    "rate before commencing it." % (rec.name, rec.vehicle_id.display_name)
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
            frequency = extract.get("payment_frequency") or getattr(
                site_lease, "payment_frequency", None
            )
            return {
                "commencement_date": start,
                "term_months": int(extract.get("term_months") or _term_months(start, end)),
                "payment_amount": float(extract.get("monthly_rent") or 0.0),
                "payment_frequency": FREQUENCY.get(frequency or "monthly", "1"),
                "escalation_percent": float(extract.get("escalation_pct") or 0.0),
                "site_escalation_pct": float(extract.get("escalation_pct") or 0.0),
                "site_deposit": float(extract.get("deposit") or 0.0),
            }
        return {
            "commencement_date": site_lease.start_date,
            "term_months": _term_months(site_lease.start_date, site_lease.end_date),
            "payment_amount": float(site_lease.monthly_rent or 0.0),
            "payment_frequency": FREQUENCY.get(
                getattr(site_lease, "payment_frequency", None) or "monthly", "1"
            ),
            "escalation_percent": float(site_lease.escalation_pct or 0.0),
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
    def _bridge_awaiting_approval(self, site_lease):
        """R2a (D6): a lease a person recorded is a draft until its total
        commitment is approved; it reaches IFRS 16 on activation (M47 publishes
        lease.recorded again then), never before. A stale or early event for it
        drafts nothing."""
        return "state" in site_lease._fields and site_lease.state == "draft"

    @api.model
    def _bridge_draft(self, site_lease, terms, version, event, method):
        if self._bridge_awaiting_approval(site_lease):
            return self.browse()
        problem = self._bridge_terms_problem(terms)
        if problem:
            return self._bridge_hold(site_lease, problem, event, method)
        site = site_lease.site_id
        lease = self.sudo().create(
            dict(
                terms,
                company_id=(site.company_id or self.env.company).id,
                # M47-02: the site's OU, else its branch's: never left to the first OU
                operating_unit_id=(site.operating_unit_id or site.branch_id.operating_unit_id).id,
                name="%s — %s" % (site_lease.name, site.name),
                partner_id=site_lease.lessor_id.id,
                site_lease_id=site_lease.id,
                site_extract_version=version,
                ibr_percent=0.0,
                exemption=self._bridge_exemption(terms["term_months"]),
                **self._bridge_defaults(site.company_id or self.env.company),
            )
        )
        advance = float(getattr(site_lease, "advance_rent_amount", 0.0) or 0.0)
        lease.message_post(
            body="Drafted from M47 lease %s (extract v%s): %s, %.2f%% fixed escalation measured "
            "in the liability. Finance completes the incremental borrowing rate, the "
            "right-of-use category and the accounts, then commences it. The %.2f deposit is "
            "refundable and is not part of the right-of-use asset%s."
            % (
                site_lease.name,
                version,
                dict(self._fields["exemption"].selection)[lease.exemption],
                terms["site_escalation_pct"],
                terms["site_deposit"],
                "; the %.2f advance rent is adjusted against the rent the schedule pays" % advance
                if advance
                else "",
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
            terms = dict(terms, exemption=self._bridge_exemption(terms["term_months"]))
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
    def consume_lease_terminated(self, event):
        """lease.terminated (M47, an approved early end) -> the IFRS 16 book
        derecognises the ROU asset and the liability (D5c, FIN-07/12). A
        draft contract is only told; one whose earlier months are not posted
        waits as an exception for finance (post them, then Retry)."""
        site_lease = event_source(self.env, event, "fix.site.lease")
        if not site_lease:
            return False
        lease = self.sudo().search([("site_lease_id", "=", site_lease.id)], limit=1)
        payload = event.get("payload") or {}
        reason = payload.get("reason") or site_lease.terminated_reason or "terminated in M47"
        if not lease or lease.state == "ended":
            return lease
        if lease.state == "draft" or lease.exemption != "none":
            text = "M47 lease %s was terminated (%s): nothing is on the IFRS 16 book." % (
                site_lease.name,
                reason,
            )
            lease.message_post(body=text)
            return lease
        on_date = (
            fields.Date.to_date(getattr(site_lease, "termination_effective_date", None))
            or fields.Date.to_date(payload.get("end_date"))
            or dhaka_today(self.env)
        )
        on_date = min(on_date, dhaka_today(self.env))
        try:
            with self.env.cr.savepoint():
                move = lease._fix_terminate(on_date, reason)
        except UserError as exc:
            self.env["fix.bridge.exception"].sudo().record(
                route="m49_lease",
                key="m49_lease_end:%s" % site_lease.id,
                message="IFRS 16 lease %s cannot be derecognised yet: %s" % (lease.name, exc),
                event=event,
                source=site_lease,
                consumer=("fix.lease", "consume_lease_terminated"),
                role=ACCOUNTANT,
                company=lease.company_id,
            )
            return lease
        self.env["fix.bridge.exception"].sudo().resolve(
            "m49_lease_end:%s" % site_lease.id, "derecognised by %s" % move.name
        )
        return lease

    @api.model
    def _bridge_vehicle_terms(self, vehicle):
        v = vehicle.sudo()
        start = getattr(v, "fix_contract_start", None) or v.acquisition_date
        end = v.fix_contract_end
        payment = float(
            getattr(v, "fix_lease_monthly_rent", 0.0) or getattr(v, "fix_lease_payment", 0.0) or 0.0
        )
        return {
            "commencement_date": start,
            "term_months": _term_months(start, end),
            "payment_amount": payment,
        }

    @api.model
    def _bridge_draft_vehicle_lease(self, vehicles):
        """FIN-09 / D5(d): a leased van or motorbike is drafted on the IFRS 16
        book like a branch lease (exempt when 12 months or less, or worth BDT
        500,000 or less new). What the fleet register lacks is an exception."""
        for v in vehicles.sudo():
            if getattr(v, "fix_ownership_basis", None) != "leased":
                continue
            lease = self.sudo().search([("vehicle_id", "=", v.id)], limit=1)
            terms = self._bridge_vehicle_terms(v)
            problem = self._bridge_terms_problem(terms)
            key = "m49_vehicle_lease:%s" % v.id
            if problem:
                self.env["fix.bridge.exception"].sudo().record(
                    route="m49_lease",
                    key=key,
                    message="Leased vehicle %s cannot be drafted under IFRS 16: %s. Record the "
                    "contract start, end and monthly rent in M46."
                    % (v.license_plate or v.name, problem),
                    source=v,
                    role=ACCOUNTANT,
                    company=v.company_id,
                )
                continue
            new_value = float(getattr(v, "fix_new_value", 0.0) or v.net_car_value or 0.0)
            terms["exemption"] = self._bridge_exemption(terms["term_months"], new_value)
            if lease:
                if lease.state == "draft":
                    lease.write(terms)
                continue
            lessor = getattr(v, "fix_lessor_id", None)
            lease = self.sudo().create(
                dict(
                    terms,
                    company_id=(v.company_id or self.env.company).id,
                    operating_unit_id=(v.operating_unit_id or v.branch_id.operating_unit_id).id,
                    name="Vehicle lease — %s" % (v.license_plate or v.name),
                    partner_id=lessor.id if lessor else False,
                    vehicle_id=v.id,
                    ibr_percent=0.0,
                    **self._bridge_defaults(v.company_id or self.env.company),
                )
            )
            lease.message_post(
                body="Drafted from leased vehicle %s (contract %s): %s. Finance completes the "
                "borrowing rate, the right-of-use category and the accounts, then commences it."
                % (
                    v.license_plate or v.name,
                    v.fix_contract_ref or "-",
                    dict(self._fields["exemption"].selection)[lease.exemption],
                )
            )
            self.env["fix.bridge.exception"].sudo().resolve(key, "drafted %s" % lease.reference)

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
            "remeasurement_id",
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
        extract = payload.get("extract") or {}
        if payload.get("reason") == "terminated":
            changes.insert(0, "Terminated in M47: %s" % (extract.get("terminated_reason") or "-"))
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

    remeasurement_id = fields.Many2one(
        "fix.lease.remeasurement", string="Remeasurement", readonly=True, copy=False
    )

    def action_mark_remeasured(self, note=None):
        """Finance remeasured the liability and the ROU asset for this version:
        only with a POSTED remeasurement of this item (FIN-07: never a tick)."""
        for rec in self:
            if not rec.remeasurement_id or rec.remeasurement_id.state != "posted":
                raise UserError(
                    "%s: post the remeasurement of this version first (New Remeasurement)."
                    % rec.name
                )
        return self._decide("remeasured", note)

    def action_new_remeasurement(self):
        """A draft remeasurement prefilled with this version's terms."""
        require_role(self.env, [ACCOUNTANT, ACCOUNTING_MANAGER], "Remeasuring a lease")
        self.ensure_one()
        if self.state != "open":
            raise UserError("%s is already decided." % self.name)
        if self.remeasurement_id and self.remeasurement_id.state == "draft":
            return self.remeasurement_id
        extract = json.loads(self.extract or "{}")
        terms = self.env["fix.lease"]._bridge_terms(self.site_lease_id, extract)
        effective = fields.Date.to_date(extract.get("effective_date")) or dhaka_today(self.env)
        doc = self.env["fix.lease.remeasurement"].create(
            {
                "lease_id": self.lease_id.id,
                "modification_item_id": self.id,
                "effective_date": effective.replace(day=1),
                "payment_amount": terms["payment_amount"],
                # the revised TOTAL term, counted from the original commencement
                "term_months": _term_months(
                    self.lease_id.commencement_date,
                    fields.Date.to_date(extract.get("end_date")) or self.lease_id.end_date,
                )
                or terms["term_months"],
                "escalation_percent": terms["escalation_percent"],
                "payment_frequency": terms["payment_frequency"],
                "ibr_percent": self.lease_id.ibr_percent,
                "reason": self.reason or "modification v%s" % self.version,
            }
        )
        self.sudo()._guarded().write({"remeasurement_id": doc.id})
        return doc

    def action_mark_no_change(self, note=None):
        """The version changes nothing IFRS 16 measures (e.g. a notice period)."""
        return self._decide("no_change", note)


class FixLeaseRemeasurement(models.Model):
    """A07 D5(c), FIN-07: the IFRS 16 remeasurement of a commenced lease (a
    rent change, a term change, a revised rate): prepared by one accountant,
    posted by ANOTHER, which revises the liability at the revised rate,
    adjusts the right-of-use asset and rebuilds the remaining schedule."""

    _name = "fix.lease.remeasurement"
    _description = "IFRS 16 Lease Remeasurement"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "effective_date desc, id desc"

    name = fields.Char(readonly=True, default="New", copy=False)
    lease_id = fields.Many2one("fix.lease", required=True, index=True, ondelete="restrict")
    company_id = fields.Many2one(related="lease_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="lease_id.operating_unit_id", store=True, index=True
    )
    currency_id = fields.Many2one(related="lease_id.currency_id")
    modification_item_id = fields.Many2one(
        "fix.lease.modification.item", string="Modification Item", readonly=True
    )
    effective_date = fields.Date(required=True, help="The first unposted month it applies from")
    payment_amount = fields.Monetary(string="Revised Monthly Rent", required=True)
    term_months = fields.Integer(string="Revised Total Term (Months)", required=True)
    escalation_percent = fields.Float(string="Revised Fixed Escalation %", digits=(6, 3))
    payment_frequency = fields.Selection(
        [("1", "Monthly"), ("3", "Quarterly"), ("6", "Half-Yearly"), ("12", "Yearly")],
        default="1",
        required=True,
    )
    ibr_percent = fields.Float(string="Revised Borrowing Rate %", required=True, digits=(6, 3))
    reason = fields.Char(required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("posted", "Posted"), ("cancelled", "Cancelled")],
        default="draft",
        required=True,
        tracking=True,
    )
    move_id = fields.Many2one("account.move", string="Adjustment Entry", readonly=True, copy=False)
    posted_by_id = fields.Many2one("res.users", readonly=True, copy=False)

    _TERMS = (
        "lease_id",
        "effective_date",
        "payment_amount",
        "term_months",
        "escalation_percent",
        "payment_frequency",
        "ibr_percent",
    )

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields() | {
            "name",
            "state",
            "move_id",
            "posted_by_id",
            "modification_item_id",
        }
        if any(rec.state != "draft" for rec in self):
            guarded |= set(self._TERMS) | {"reason"}
        return guarded

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, [ACCOUNTANT, ACCOUNTING_MANAGER], "Preparing a remeasurement")
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.lease.remeasurement")
                    or "REM/New"
                )
        return super(FixLeaseRemeasurement, self._guarded()).create(vals_list)

    def unlink(self):
        if any(rec.state == "posted" for rec in self) and not self.env.su:
            raise UserError("A posted remeasurement is part of the record.")
        return super().unlink()

    def action_post(self):
        require_role(self.env, [ACCOUNTANT, ACCOUNTING_MANAGER], "Posting a remeasurement")
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s is not a draft." % rec.name)
            if not self.env.su and rec.create_uid == self.env.user:
                raise UserError(
                    "Segregation of duties: you prepared %s; another accountant posts it."
                    % rec.name
                )
            lease = rec.lease_id
            terms = {
                "payment_amount": rec.payment_amount,
                "term_months": rec.term_months,
                "escalation_percent": rec.escalation_percent,
                "payment_frequency": rec.payment_frequency,
                "ibr_percent": rec.ibr_percent,
            }
            move = lease.sudo()._fix_remeasure(rec.effective_date, terms, rec.reason)
            rec.sudo()._guarded().write(
                {"state": "posted", "move_id": move.id or False, "posted_by_id": self.env.uid}
            )
            rec.message_post(body="Posted%s." % (": %s" % move.name if move else " (no change)"))
        return True

    def action_cancel(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft remeasurement is cancelled.")
            rec.sudo()._guarded().write({"state": "cancelled"})
        return True


class FleetVehicleIfrs16(models.Model):
    _inherit = "fleet.vehicle"

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        Lease = self.env["fix.lease"].sudo()
        run_hook(self.env, "m49_vehicle_lease", Lease._bridge_draft_vehicle_lease, records)
        return records

    def write(self, vals):
        result = super().write(vals)
        watched = {
            "fix_ownership_basis",
            "fix_contract_end",
            "fix_contract_start",
            "fix_lease_monthly_rent",
            "fix_lease_payment",
            "acquisition_date",
            "net_car_value",
        }
        if watched & set(vals):
            Lease = self.env["fix.lease"].sudo()
            run_hook(self.env, "m49_vehicle_lease", Lease._bridge_draft_vehicle_lease, self)
        return result
