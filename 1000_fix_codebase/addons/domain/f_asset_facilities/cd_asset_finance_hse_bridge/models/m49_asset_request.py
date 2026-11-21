# m49_asset_request — A07 P1 (2026-11-04), report §6 P1 "Event consumers":
# M45 equipment, M46 vehicles and M47 site assets reach the M49 register.
#
# Before: an item was registered with its cost, written off under DOFA, and
# M49 never heard of either: no depreciation, no derecognition, and a
# fixed-asset register that disagreed with the operational one. Now each
# acquisition and each write-off/retirement raises ONE pending request (per
# source and kind) that finance decides. Accepting creates what M49 already
# treats as a draft: a registered (draft) fix.fixed.asset, which the
# accountant puts into service with M49's own Activate, or a draft
# fix.asset.disposal, which M49 approves (SoD) and posts. Nothing here posts
# a journal entry.
from odoo import api, fields, models
from odoo.exceptions import UserError

from .fix_bridge_exception import (
    ACCOUNTANT,
    ACCOUNTING_MANAGER,
    dhaka_today,
    event_source,
    noted,
    param_float,
    require_role,
    role_account,
    run_hook,
    source_key,
)

# BUSINESS SWITCH (B2): the capitalisation threshold is company policy the
# spec does not give. 0 (the default) queues every costed item, and finance
# rejects the ones below its policy, so nothing is silently left out.
CAP_MIN_PARAM = "capitalisation_min_bdt"

DISPOSAL_KINDS = [("sale", "Sale"), ("scrap", "Scrap"), ("write_off", "Write-Off (Lost / Missing)")]


def lost_subject(env, event):
    """(equipment, where, day) of an equipment.lost / equipment.recovered
    event, whichever M45 record published it: a physical verification or a
    loss-register report (A07 FIN-04). None when the record is gone, or when
    the payload names another item than the record does."""
    aggregate = event.get("aggregate") or "fix.equipment.verification"
    if aggregate == "fix.equipment.loss":
        loss = event_source(env, event, "fix.equipment.loss")
        if not loss:
            return None
        equipment = loss.equipment_id.sudo()
        where = "loss report %s (%s)" % (loss.name, loss.kind)
        day = loss.reported_on and fields.Date.context_today(
            loss.with_context(tz="Asia/Dhaka"), loss.reported_on
        )
    elif aggregate == "fix.equipment.verification":
        verification = event_source(env, event, "fix.equipment.verification")
        if not verification:
            return None
        payload = event.get("payload") or {}
        equipment = verification.equipment_id.sudo()
        where = "verification %s, campaign %s" % (
            verification.name,
            payload.get("campaign") or verification.campaign_ref or "-",
        )
        day = verification.verified_on
    else:
        return None
    code = (event.get("payload") or {}).get("equipment")
    if not equipment or (code and code != equipment.code):
        return None
    return equipment, where, day


class FixAssetFinanceRequest(models.Model):
    _name = "fix.asset.finance.request"
    _description = "M49 Capitalisation / Disposal Request"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "state, create_date desc, id desc"

    _key_unique = models.Constraint(
        "UNIQUE (key)", "One M49 request per source item and kind (idempotent hand-off)."
    )

    name = fields.Char(required=True, readonly=True, default="New", copy=False)
    key = fields.Char(required=True, readonly=True, index=True, copy=False)
    kind = fields.Selection(
        [("capitalise", "Capitalise"), ("dispose", "Dispose / Derecognise")],
        required=True,
        readonly=True,
    )
    company_id = fields.Many2one("res.company", required=True, index=True, readonly=True)
    operating_unit_id = fields.Many2one("operating.unit", string="Branch", index=True)
    source_model = fields.Char(required=True, readonly=True)
    source_res_id = fields.Integer(required=True, readonly=True, index=True)
    source_ref = fields.Char(string="Source Item", readonly=True)
    source_label = fields.Char(string="Source", readonly=True, help="Which register raised it")
    event_type = fields.Char(readonly=True, help="The event or action that raised the request")
    currency_id = fields.Many2one(
        "res.currency", required=True, readonly=True, default=lambda self: self.env.ref("base.BDT")
    )
    source_amount = fields.Monetary(
        string="Amount in the Source Register",
        readonly=True,
        help="Acquisition cost (capitalise) or the value written off (dispose), as the "
        "operational register holds it",
    )
    amount = fields.Monetary(
        string="Amount to Capitalise",
        help="Finance's figure; starts at the source amount (freight, duty and installation "
        "may be added before accepting)",
    )
    acquisition_date = fields.Date()
    basis = fields.Text(string="Basis", readonly=True, help="Why the source raised it")
    category_id = fields.Many2one(
        "fix.asset.category",
        string="Asset Category",
        help="Finance chooses the M49 category (life, accounts) before accepting",
    )
    custodian_id = fields.Many2one("hr.employee", string="Custodian", readonly=True)
    fixed_asset_id = fields.Many2one(
        "fix.fixed.asset",
        string="M49 Asset",
        help="Dispose: the M49 asset this derecognises. Capitalise: the draft asset created",
    )
    acquisition_line_id = fields.Many2one(
        "account.move.line",
        string="Acquisition Journal Item",
        help="Capitalise: the POSTED journal item that carries the cost on the category's "
        "asset account (the bill, or M19's re-class of an expensed bill). It becomes the "
        "M19 capitalisation seam that puts the asset into service (A08 BRU-FXA-01).",
    )
    disposal_kind = fields.Selection(DISPOSAL_KINDS, string="Disposal Type")
    # A07 D10 (FIN-12, M45-06): a sale's proceeds and buyer, from the source
    sale_proceeds = fields.Monetary(string="Sale Proceeds", readonly=True)
    buyer_id = fields.Many2one("res.partner", string="Buyer", readonly=True)
    disposal_ref = fields.Char(string="Sale / Disposal Reference", readonly=True)
    disposal_id = fields.Many2one("fix.asset.disposal", string="Draft Disposal", readonly=True)
    state = fields.Selection(
        [
            ("pending", "Pending Finance"),
            ("accepted", "Accepted"),
            ("rejected", "Rejected"),
            # A07 P1 (2026-11-04): the source took the trigger back before
            # finance decided (a lost item found again). Raised again, it
            # returns to pending: one request per item and kind.
            ("withdrawn", "Withdrawn by the Source"),
        ],
        default="pending",
        required=True,
        index=True,
        tracking=True,
    )
    decided_by_id = fields.Many2one("res.users", string="Decided By", readonly=True, copy=False)
    decided_on = fields.Datetime(string="Decided On", readonly=True, copy=False)
    decision_note = fields.Text(string="Decision Note")

    _GUARDED = {
        "name",
        "key",
        "kind",
        "company_id",
        "source_model",
        "source_res_id",
        "source_ref",
        "source_label",
        "event_type",
        "currency_id",
        "source_amount",
        "basis",
        "custodian_id",
        "disposal_id",
        "sale_proceeds",
        "buyer_id",
        "disposal_ref",
        "state",
        "decided_by_id",
        "decided_on",
    }

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields() | self._GUARDED
        if any(rec.state != "pending" for rec in self):
            # a decided request is the record of the decision
            guarded |= {
                "amount",
                "acquisition_date",
                "category_id",
                "fixed_asset_id",
                "acquisition_line_id",
                "disposal_kind",
                "operating_unit_id",
                "decision_note",
            }
        return guarded

    def unlink(self):
        if not self.env.su:
            raise UserError("An M49 request is part of the record: reject it instead.")
        return super().unlink()

    # ---- raising (the bridge, as superuser) -----------------------------------
    @api.model
    def _m49_queue(self, kind, record, vals):
        """Raise the request for `record` once; refresh a pending one. Returns it."""
        key = source_key("m49:%s" % kind, record)
        Req = self.sudo()._guarded()
        existing = Req.search([("key", "=", key)], limit=1)
        if existing:
            if existing.state == "withdrawn":
                reopen = {
                    k: v
                    for k, v in vals.items()
                    if k
                    in (
                        "source_amount",
                        "basis",
                        "acquisition_date",
                        "event_type",
                        "disposal_kind",
                        "operating_unit_id",
                        "sale_proceeds",
                        "buyer_id",
                        "disposal_ref",
                    )
                }
                reopen.update(
                    state="pending", decided_by_id=False, decided_on=False, decision_note=False
                )
                if "source_amount" in reopen:
                    reopen["amount"] = reopen["source_amount"]
                existing.write(reopen)
                existing.message_post(
                    body="Raised again by the source (%s): back to pending finance."
                    % (vals.get("event_type") or "-")
                )
                return existing
            if existing.state == "pending":
                update = {
                    k: v
                    for k, v in vals.items()
                    if k
                    in (
                        "source_amount",
                        "basis",
                        "acquisition_date",
                        "event_type",
                        "disposal_kind",
                        "sale_proceeds",
                        "buyer_id",
                        "disposal_ref",
                    )
                }
                if "source_amount" in update and (
                    not existing.amount or existing.amount == existing.source_amount
                ):
                    update["amount"] = update["source_amount"]

                def _differs(k, v):
                    cur = existing[k]
                    if existing._fields[k].type == "many2one":
                        return (cur.id or False) != (v or False)
                    return (cur or False) != (v or False)

                if any(_differs(k, v) for k, v in update.items() if k in existing._fields):
                    existing.write(update)
                    existing.message_post(body="The source register changed: request refreshed.")
            elif vals.get("source_amount") not in (None, existing.source_amount):
                existing.message_post(
                    body="After the decision the source amount changed to %.2f (was %.2f): "
                    "finance reviews it." % (vals["source_amount"], existing.source_amount)
                )
            return existing
        vals = dict(vals)
        vals.update(
            {
                "name": self.env["ir.sequence"].sudo().next_by_code("fix.asset.finance.request")
                or "M49REQ/New",
                "key": key,
                "kind": kind,
                "source_model": record._name,
                "source_res_id": record.id,
                "source_ref": record.display_name,
            }
        )
        vals.setdefault("amount", vals.get("source_amount") or 0.0)
        req = Req.create(vals)
        req.message_post(
            body="Raised from %s %s (%s). Finance decides: accept into M49 or reject with a "
            "reason." % (vals.get("source_label") or record._description, record.display_name, kind)
        )
        return req

    @api.model
    def _m49_min(self):
        return param_float(self.env, CAP_MIN_PARAM, 0.0)

    # ---- the source registers -------------------------------------------------
    @api.model
    def _m49_equipment_vals(self, equipment):
        eq = equipment.sudo()
        return {
            "company_id": eq.company_id.id,
            "operating_unit_id": (eq.operating_unit_id or eq.branch_id.operating_unit_id).id,
            "source_label": "M45 Equipment",
            "custodian_id": eq.custodian_id.id,
            "fixed_asset_id": eq.fixed_asset_id.id,
        }

    @api.model
    def _m49_capitalise_equipment(self, equipment):
        for eq in equipment.sudo():
            if (eq.acquisition_cost or 0.0) <= max(self._m49_min(), 0.0):
                continue
            if eq.fixed_asset_id:
                continue
            # a cost entered to write an item off is the write-off's basis, not an
            # acquisition: the approved write-off reaches M49 as a disposal
            if (
                eq.operational_status == "retired"
                or (eq.retirement_reason or "").strip()
                or eq.approval_state in ("pending", "approved")
            ):
                continue
            vals = self._m49_equipment_vals(eq)
            vals.update(
                {
                    "event_type": "equipment.registered",
                    "source_amount": eq.acquisition_cost,
                    # FIN-23 / M45-12: the date it was acquired, else the Dhaka
                    # day it was registered (never the UTC create date)
                    "acquisition_date": getattr(eq, "acquired_on", False)
                    or (
                        fields.Date.context_today(
                            self.with_context(tz="Asia/Dhaka"), eq.create_date
                        )
                        if eq.create_date
                        else dhaka_today(self.env)
                    ),
                    "basis": "Equipment %s registered with an acquisition cost." % eq.code,
                }
            )
            self._m49_queue("capitalise", eq, vals)

    @api.model
    def consume_equipment_written_off(self, event):
        """equipment.written_off (M45, approved under DOFA) -> a disposal request.
        Idempotent: one disposal request per item."""
        equipment = event_source(self.env, event, "fix.equipment")
        if not equipment:
            return False
        payload = event.get("payload") or {}
        vals = self._m49_equipment_vals(equipment)
        vals.update(
            {
                "event_type": event.get("event_type") or "equipment.written_off",
                "source_amount": float(payload.get("value") or equipment.acquisition_cost or 0.0),
                "basis": "Written off in M45, approved by %s: %s"
                % (payload.get("approver") or "-", payload.get("basis") or "-"),
                "disposal_kind": "write_off" if payload.get("was_missing") else "scrap",
                "acquisition_date": equipment.retired_on or fields.Date.context_today(self),
            }
        )
        return self._m49_queue("dispose", equipment, vals)

    @api.model
    def consume_equipment_lost(self, event):
        """equipment.lost (M45: not found at a physical verification, or a loss
        reported in the loss register) -> a pending write-off request for a
        CAPITALISED item (spec §10.2: M49 derecognises a lost asset). An item
        never accepted into M49 has nothing to derecognise: its pending
        capitalisation is told instead. Idempotent: one disposal request per
        item (shared with the write-off, so a later DOFA write-off refreshes
        the same request). A07 FIN-04: the event's own aggregate says which
        record it is about."""
        found = lost_subject(self.env, event)
        if not found:
            return False
        equipment, where, day = found
        payload = event.get("payload") or {}
        if not equipment.fixed_asset_id:
            pending = self.sudo().search(
                [("key", "=", source_key("m49:capitalise", equipment)), ("state", "=", "pending")],
                limit=1,
            )
            note = "%s was reported missing (%s)." % (equipment.code, where)
            if pending and not noted(pending, note):
                pending.message_post(body=note)
            return pending
        vals = self._m49_equipment_vals(equipment)
        vals.update(
            {
                "event_type": event.get("event_type") or "equipment.lost",
                "source_amount": float(payload.get("value") or equipment.acquisition_cost or 0.0),
                "basis": "Reported missing (%s); last custodian %s. Withdrawn automatically if "
                "the item is found before finance decides."
                % (where, payload.get("custodian") or "-"),
                "disposal_kind": "write_off",
                "acquisition_date": day or dhaka_today(self.env),
            }
        )
        return self._m49_queue("dispose", equipment, vals)

    @api.model
    def consume_equipment_recovered(self, event):
        """equipment.recovered (M45: a count or the loss register found the
        missing item) -> the disposal request the loss raised is withdrawn
        while still pending. A request finance already decided, or one a DOFA
        write-off raised, is left alone and told."""
        found = lost_subject(self.env, event)
        if not found:
            return False
        equipment, where, _day = found
        req = self.sudo().search([("key", "=", source_key("m49:dispose", equipment))], limit=1)
        if not req or req.state == "withdrawn":
            return req
        payload = event.get("payload") or {}
        text = "%s found (%s, missing since %s)" % (
            equipment.code,
            where,
            payload.get("missing_since") or "-",
        )
        if req.state == "pending" and req.event_type == "equipment.lost":
            req._guarded().write(
                {
                    "state": "withdrawn",
                    "decision_note": "Withdrawn: %s." % text,
                    "decided_on": fields.Datetime.now(),
                }
            )
            req.message_post(body="Withdrawn: %s. Nothing to derecognise." % text)
        elif not noted(req, text):
            req.message_post(body="%s: finance reviews this request (%s)." % (text, req.state))
        return req

    @api.model
    def consume_equipment_disposed(self, event):
        """equipment.disposed (M45 retirement disposed: resale, scrap, e-waste)
        -> the item's disposal request carries the route, and for a resale the
        sale proceeds and buyer (D10, M45-06): a request still pending is
        updated, a draft M49 disposal already raised takes the sale terms."""
        retirement = event_source(self.env, event, "fix.equipment.retirement")
        if not retirement:
            return False
        equipment = retirement.equipment_id.sudo()
        payload = event.get("payload") or {}
        route = getattr(retirement, "disposal_route", None) or payload.get("route")
        proceeds = float(getattr(retirement, "sale_amount", 0.0) or 0.0)
        buyer = getattr(retirement, "buyer_partner_id", None)
        sale = route == "resale" and proceeds > 0
        vals = self._m49_equipment_vals(equipment)
        vals.update(
            {
                "event_type": "equipment.disposed",
                "source_amount": float(equipment.acquisition_cost or 0.0),
                "basis": "Disposed in M45 by %s (reference %s)."
                % (route or "-", payload.get("reference") or "-"),
                "disposal_kind": "sale" if sale else "scrap",
                "sale_proceeds": proceeds if sale else 0.0,
                "buyer_id": buyer.id if sale and buyer else False,
                "disposal_ref": payload.get("reference") or False,
                "acquisition_date": getattr(retirement, "disposed_on", False)
                or dhaka_today(self.env),
            }
        )
        req = self._m49_queue("dispose", equipment, vals)
        if req.state == "accepted" and req.disposal_id.state == "draft":
            req._m49_disposal_terms(req.disposal_id)
        elif req.state != "pending":
            text = "M45 disposed of %s by %s (proceeds %.2f)." % (equipment.code, route, proceeds)
            if not noted(req, text):
                req.message_post(body=text)
        return req

    @api.model
    def _m49_vehicle_vals(self, vehicle):
        v = vehicle.sudo()
        return {
            "company_id": (v.company_id or self.env.company).id,
            "operating_unit_id": (v.operating_unit_id or v.branch_id.operating_unit_id).id,
            "source_label": "M46 Vehicle",
            "custodian_id": v.fix_driver_id.employee_id.id,
            "fixed_asset_id": v.fixed_asset_id.id,
        }

    @api.model
    def _m49_capitalise_vehicle(self, vehicles):
        for v in vehicles.sudo():
            if (v.net_car_value or 0.0) <= max(self._m49_min(), 0.0) or v.fixed_asset_id:
                continue
            # M46 capture audit (FR-FLT-003): a leased, hired or employee-owned
            # vehicle is not the company's asset; only an owned one capitalises.
            if (getattr(v, "fix_ownership_basis", None) or "owned") != "owned":
                continue
            vals = self._m49_vehicle_vals(v)
            vals.update(
                {
                    "event_type": "vehicle.acquired",
                    "source_amount": v.net_car_value,
                    "acquisition_date": v.acquisition_date or fields.Date.context_today(self),
                    "basis": "Vehicle %s acquired (purchase value in the fleet register)."
                    % (v.license_plate or v.name),
                }
            )
            self._m49_queue("capitalise", v, vals)

    @api.model
    def _m49_dispose_vehicle_from_m46(self, vehicles):
        reqs = self.browse()
        for v in vehicles.sudo().with_context(active_test=False):
            disposal = getattr(v, "fix_disposal_id", None)
            facts = getattr(disposal, "_m49_disposal_facts", None) if disposal else None
            if not facts:
                continue
            f = facts()
            if not v.fixed_asset_id or f.get("kind") == "lease_return":
                continue  # M46-26: only a capitalised vehicle concerns M49
            kind = {"sale": "sale", "scrap": "scrap", "write_off": "write_off"}.get(
                f.get("kind"), "scrap"
            )
            reqs |= self._m49_dispose_vehicle(
                v,
                "%s %s" % (f.get("route") or "disposed", f.get("disposal_ref") or ""),
                proceeds=float(f.get("proceeds") or 0.0) if kind == "sale" else 0.0,
                buyer_id=f.get("buyer_id") or False,
                reference=f.get("disposal_ref") or False,
                kind=kind,
                on_date=f.get("disposal_date") or False,
            )
        return reqs

    @api.model
    def _m49_dispose_vehicle(
        self,
        vehicles,
        how,
        proceeds=0.0,
        buyer_id=False,
        reference=False,
        kind=False,
        on_date=False,
    ):
        floor = max(self._m49_min(), 0.0)
        reqs = self.browse()
        for v in vehicles.sudo().with_context(active_test=False):
            if not (v.fixed_asset_id or (v.net_car_value or 0.0) > floor):
                continue  # never costed nor capitalised: nothing for M49 to derecognise
            vals = self._m49_vehicle_vals(v)
            vals.update(
                {
                    "event_type": "vehicle.disposed",
                    "source_amount": v.net_car_value or 0.0,
                    "acquisition_date": on_date or v.write_off_date or dhaka_today(self.env),
                    "basis": "Vehicle %s left the fleet (%s)." % (v.license_plate or v.name, how),
                }
            )
            if kind:
                vals["disposal_kind"] = kind
            if proceeds:
                vals.update(
                    disposal_kind="sale",
                    sale_proceeds=proceeds,
                    buyer_id=buyer_id,
                    disposal_ref=reference,
                )
            reqs |= self._m49_queue("dispose", v, vals)
        return reqs

    @api.model
    def _m49_site_asset_vals(self, asset):
        a = asset.sudo()
        return {
            "company_id": (a.site_id.company_id or self.env.company).id,
            "operating_unit_id": a.site_id.operating_unit_id.id,
            "source_label": "M47 Site Asset",
            "fixed_asset_id": a.fixed_asset_id.id,
        }

    @api.model
    def _m49_capitalise_site_asset(self, assets):
        for a in assets.sudo():
            if (a.value or 0.0) <= max(self._m49_min(), 0.0) or a.fixed_asset_id:
                continue
            if a.state == "retired":
                continue
            vals = self._m49_site_asset_vals(a)
            vals.update(
                {
                    "event_type": "site.asset_registered",
                    "source_amount": a.value,
                    "acquisition_date": a.installed_on or fields.Date.context_today(self),
                    "basis": "Site asset %s (%s) registered at %s with a value."
                    % (a.name, a.asset_type, a.site_id.name),
                }
            )
            self._m49_queue("capitalise", a, vals)

    @api.model
    def _m49_dispose_site_asset(self, assets):
        floor = max(self._m49_min(), 0.0)
        for a in assets.sudo().filtered(lambda r: r.state == "retired"):
            if not (a.fixed_asset_id or (a.value or 0.0) > floor):
                continue
            vals = self._m49_site_asset_vals(a)
            vals.update(
                {
                    "event_type": "site.asset_retired",
                    "source_amount": a.value or 0.0,
                    "acquisition_date": a.retired_on or fields.Date.context_today(self),
                    "basis": "Site asset %s retired: %s" % (a.name, a.retire_reason or "-"),
                    "disposal_kind": "scrap",
                }
            )
            self._m49_queue("dispose", a, vals)

    # ---- finance's decision ---------------------------------------------------
    def _m49_source(self):
        self.ensure_one()
        if self.source_model not in self.env:
            return None
        return (
            self.env[self.source_model]
            .sudo()
            .with_context(active_test=False)
            .browse(self.source_res_id)
            .exists()
        )

    def action_accept(self):
        """Accept into M49: a draft (registered) asset for a capitalisation, a
        draft disposal for a derecognition. M49's own steps (Activate; Approve
        and Post with SoD) follow, by M49's roles."""
        require_role(self.env, [ACCOUNTANT, ACCOUNTING_MANAGER], "Accepting an M49 request")
        for rec in self:
            if rec.state != "pending":
                raise UserError("%s is already decided." % rec.name)
            if rec.kind == "capitalise":
                rec._m49_accept_capitalise()
            else:
                rec._m49_accept_dispose()
            rec.sudo()._guarded().write(
                {
                    "state": "accepted",
                    "decided_by_id": self.env.uid,
                    "decided_on": fields.Datetime.now(),
                }
            )
        return True

    def _m49_accept_capitalise(self):
        self.ensure_one()
        source = self._m49_source()
        if source and "fixed_asset_id" in source._fields and source.fixed_asset_id:
            raise UserError(
                "%s is already in the M49 register as %s: reject this request."
                % (self.source_ref, source.fixed_asset_id.display_name)
            )
        if not self.category_id:
            raise UserError("Choose the M49 asset category of %s first." % self.name)
        if self.category_id.company_id != self.company_id:
            raise UserError("The asset category belongs to another company.")
        if not (self.amount or 0.0) > 0.0:
            raise UserError("The amount to capitalise must be above zero.")
        if not self.operating_unit_id:
            # FIN-16: never the company's first operating unit
            raise UserError(
                "Choose the branch (operating unit) %s belongs to before accepting: the "
                "asset is booked and depreciated on its own branch."
                % (self.source_ref or self.name)
            )
        seam = self._m49_acquisition_seam()
        asset = self.env["fix.fixed.asset"].create(
            {
                "company_id": self.company_id.id,
                "operating_unit_id": self.operating_unit_id.id,
                "name": self.source_ref or self.name,
                "category_id": self.category_id.id,
                "custodian_id": self.custodian_id.id,
                "gross": self.amount,
                "purchase_date": self.acquisition_date or fields.Date.context_today(self),
                "seam_id": seam.id,
            }
        )
        self.write({"fixed_asset_id": asset.id})
        if source and "fixed_asset_id" in source._fields:
            source._bridge_link_fixed_asset(asset)
        self.message_post(
            body="Accepted: draft asset %s registered in M49 (not in service; M49 Activate "
            "starts its depreciation)." % asset.display_name
        )

    def _m49_acquisition_seam(self):
        """A08 (BRU-FXA-01 / BRU-FXA-02): an asset enters the register with its
        ledger consequence. The chosen journal item must be posted, on the
        category's asset account, for the amount capitalised, and not already
        a seam; it becomes the M19 capitalisation seam M49's Activate needs."""
        self.ensure_one()
        line = self.acquisition_line_id.sudo()
        if not line:
            raise UserError(
                "Choose the posted journal item that carries the cost of %s on the asset "
                "account (the bill, or an M19 re-class of an expensed bill) before accepting."
                % self.name
            )
        account = self.category_id.asset_account_id
        if not account:
            raise UserError(
                "Configure the asset account of category %s first." % self.category_id.name
            )
        if line.parent_state != "posted" or line.account_id != account:
            raise UserError(
                "%s is not a posted item on %s, the asset account of %s."
                % (line.display_name, account.display_name, self.category_id.name)
            )
        if abs((line.balance or 0.0) - (self.amount or 0.0)) > 0.005:
            raise UserError(
                "The journal item carries %.2f; the amount to capitalise is %.2f."
                % (line.balance, self.amount)
            )
        Seam = self.env["fix.fixed.asset.seam"].sudo()
        if Seam.search_count([("move_line_id", "=", line.id)]):
            raise UserError("%s is already the source of another asset." % line.display_name)
        # FIN-06: one ledger debit, one asset. A line of another company, or of
        # an entry that already put an asset in service (a CWIP capitalisation,
        # an IFRS 16 recognition, an earlier acquisition) is not a new cost.
        if line.company_id != self.company_id:
            raise UserError("%s belongs to another company." % line.display_name)
        move = line.move_id
        Asset = self.env["fix.fixed.asset"].sudo().with_context(active_test=False)
        taken = Asset.search([("acquisition_move_id", "=", move.id)], limit=1)
        if not taken and "fix.cwip.entry" in self.env:
            cwip = self.env["fix.cwip.entry"].sudo().search([("move_id", "=", move.id)], limit=1)
            taken = cwip.asset_id or cwip
        if not taken:
            taken = self.env["fix.lease"].sudo().search([("move_id", "=", move.id)], limit=1)
        if taken:
            raise UserError(
                "%s already brought %s into the register: it cannot capitalise %s again."
                % (move.display_name, taken.display_name, self.source_ref or self.name)
            )
        ou = self.operating_unit_id
        if not ou:
            raise UserError("Choose the branch of %s first." % self.name)
        return Seam.create(
            {
                "company_id": self.company_id.id,
                "operating_unit_id": ou.id,
                "name": ("%s %s" % (self.name, self.source_ref or "")).strip(),
                "move_line_id": line.id,
                "amount": self.amount,
                "currency_id": self.currency_id.id,
                "asset_category": self.category_id.code,
            }
        )

    def _m49_accept_dispose(self):
        self.ensure_one()
        source = self._m49_source()
        linked = source.fixed_asset_id if source and "fixed_asset_id" in source._fields else None
        asset = self.fixed_asset_id or linked
        if not asset:
            raise UserError(
                "Choose the M49 asset %s derecognises. If it was never capitalised in M49, "
                "reject the request and say so." % self.name
            )
        # FIN-17: the source's own asset, of this company, nobody else's
        if linked and asset != linked:
            raise UserError(
                "%s is registered in M49 as %s: the request derecognises that asset, not %s."
                % (self.source_ref, linked.display_name, asset.display_name)
            )
        if asset.company_id != self.company_id:
            raise UserError("%s belongs to another company." % asset.display_name)
        if not linked:
            for model in ("fix.equipment", "fleet.vehicle", "fix.site.asset"):
                other = (
                    self.env[model]
                    .sudo()
                    .with_context(active_test=False)
                    .search([("fixed_asset_id", "=", asset.id)], limit=1)
                )
                if other and (other._name, other.id) != (self.source_model, self.source_res_id):
                    raise UserError(
                        "%s is the M49 asset of %s, not of %s."
                        % (asset.display_name, other.display_name, self.source_ref)
                    )
        if not self.disposal_kind:
            raise UserError("Choose the disposal type (sale, scrap or write-off) first.")
        if asset.state != "active":
            raise UserError(
                "%s is %s in M49: only an active asset is disposed of."
                % (asset.display_name, asset.state)
            )
        result = asset.action_dispose()
        disposal = self.env["fix.asset.disposal"].browse(result.get("disposal_ids") or [])[:1]
        if disposal.state == "draft":
            self._m49_disposal_terms(disposal)
        self.sudo()._guarded().write({"disposal_id": disposal.id, "fixed_asset_id": asset.id})
        self.message_post(
            body="Accepted: draft disposal %s on %s. M49 approves (another person) and posts it."
            % (disposal.display_name, asset.display_name)
        )

    def _m49_disposal_terms(self, disposal):
        """D10: the disposal carries the source's route, and for a sale the
        proceeds, the buyer and the proceeds clearing account (the M20 sale
        invoice credits it with output VAT per M51; the M49 posting debits it
        against the gain 400116 / loss 500901 of the category)."""
        self.ensure_one()
        vals = {
            "kind": self.disposal_kind,
            "reason": "%s (%s): %s" % (self.source_ref, self.name, self.basis or "-"),
        }
        if self.disposal_kind == "sale" and self.sale_proceeds:
            account = role_account(
                self.env,
                self.company_id,
                "disposal_proceeds",
                required_for="The sale of %s" % self.source_ref,
            )
            vals.update(
                proceeds=self.sale_proceeds,
                partner_id=self.buyer_id.id,
                proceeds_account_id=account.id,
            )
        disposal.write(vals)

    def action_reject(self, reason=None):
        require_role(self.env, [ACCOUNTANT, ACCOUNTING_MANAGER], "Rejecting an M49 request")
        text = (reason or "").strip()
        for rec in self:
            if rec.state != "pending":
                raise UserError("%s is already decided." % rec.name)
            note = text or (rec.decision_note or "").strip()
            if not note:
                raise UserError("Say why %s is rejected (Decision Note)." % rec.name)
            rec.sudo()._guarded().write(
                {
                    "state": "rejected",
                    "decision_note": note,
                    "decided_by_id": self.env.uid,
                    "decided_on": fields.Datetime.now(),
                }
            )
            rec.message_post(body="Rejected: %s" % note)
        return True


def _fixed_asset_link_field():
    return fields.Many2one(
        "fix.fixed.asset", string="M49 Fixed Asset", readonly=True, copy=False, index=True
    )


class _BridgeFixedAssetLink:
    """The M49 asset an operational item became; set only by an accepted request.

    A07 P1 (2026-11-04) FF-20/21: a plain Python mixin, not an abstract model.
    Odoo 19 names a class with a LIST _inherit and no _name after the class,
    so the extensions below inherit their one model by string (a pure
    extension) and take the link field from _fixed_asset_link_field().
    No instance layout of its own (`__slots__`), so the ORM can rebase it."""

    __slots__ = ()

    def _bridge_link_fixed_asset(self, asset):
        self.sudo().with_context(bridge_fixed_asset_link=True).write({"fixed_asset_id": asset.id})

    def _bridge_refuse_link_write(self, vals):
        if (
            "fixed_asset_id" in vals
            and not self.env.su
            and any(
                (rec.fixed_asset_id.id or False) != (vals["fixed_asset_id"] or False)
                for rec in self
            )
        ):
            raise UserError(
                "The M49 asset link is set when finance accepts the capitalisation request."
            )


class FixEquipmentM49(_BridgeFixedAssetLink, models.Model):
    _inherit = "fix.equipment"

    fixed_asset_id = _fixed_asset_link_field()

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        Req = self.env["fix.asset.finance.request"].sudo()
        run_hook(self.env, "m49_capitalise_equipment", Req._m49_capitalise_equipment, records)
        return records

    def write(self, vals):
        self._bridge_refuse_link_write(vals)
        result = super().write(vals)
        if "acquisition_cost" in vals:
            Req = self.env["fix.asset.finance.request"].sudo()
            run_hook(self.env, "m49_capitalise_equipment", Req._m49_capitalise_equipment, self)
        return result


class FleetVehicleM49(_BridgeFixedAssetLink, models.Model):
    _inherit = "fleet.vehicle"

    fixed_asset_id = _fixed_asset_link_field()

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        Req = self.env["fix.asset.finance.request"].sudo()
        run_hook(self.env, "m49_capitalise_vehicle", Req._m49_capitalise_vehicle, records)
        return records

    def write(self, vals):
        self._bridge_refuse_link_write(vals)
        result = super().write(vals)
        Req = self.env["fix.asset.finance.request"].sudo()
        # an owned basis reached later capitalises then (M46 FR-FLT-003)
        if "net_car_value" in vals or "fix_ownership_basis" in vals:
            run_hook(self.env, "m49_capitalise_vehicle", Req._m49_capitalise_vehicle, self)
        if vals.get("fix_disposal_id"):
            # D10 / M46-10/26: a vehicle leaves M49 only through a completed M46
            # Vehicle Disposal (route, proceeds, buyer, CFO approval); archiving
            # or a cancelled plate raises nothing
            run_hook(self.env, "m49_dispose_vehicle", Req._m49_dispose_vehicle_from_m46, self)
        return result


class FixSiteAssetM49(_BridgeFixedAssetLink, models.Model):
    _inherit = "fix.site.asset"

    fixed_asset_id = _fixed_asset_link_field()

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        Req = self.env["fix.asset.finance.request"].sudo()
        run_hook(self.env, "m49_capitalise_site_asset", Req._m49_capitalise_site_asset, records)
        return records

    def write(self, vals):
        self._bridge_refuse_link_write(vals)
        result = super().write(vals)
        if "value" in vals:
            Req = self.env["fix.asset.finance.request"].sudo()
            run_hook(self.env, "m49_capitalise_site_asset", Req._m49_capitalise_site_asset, self)
        return result

    def action_retire(self, reason=None):
        result = super().action_retire(reason=reason)
        Req = self.env["fix.asset.finance.request"].sudo()
        run_hook(self.env, "m49_dispose_site_asset", Req._m49_dispose_site_asset, self)
        return result
