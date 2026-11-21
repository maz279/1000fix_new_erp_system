# fix_a05_s3 - A05 ERP remediation, builder stream S3 (20 Nov 2026).
#
# The A05 ERP audit (M18 findings, working/a05/m18/findings.md) found the
# M18 core gaps the owner kept in scope (D5): no certificate-due clock and no
# partner suspension (M18-08), three different diversion figures none of them
# GRI 306-4 (M18-09), a DoE return computed from rounded tonnes across cohorts
# (M18-11) without EPR progress (M18-24), stale ESG figures after a revoke
# (M18-26), a freely editable review date (M18-17), and none of the spec's
# M18 events (M18-19). Built here, imported last:
#
#   * the certificate-due clock: a batch transferred and not certified within
#     the recycler's window raises overdue exceptions, notifies the Quality
#     Manager and, on the recycler's second overdue batch, suspends it
#     (AUT-ESG-11); ewaste.certificate_exception is published;
#   * ONE GRI 306-4 diversion definition (_fix_gri_306_4), used by the ESG
#     metrics and offered to the report packs;
#   * the DoE return computed in kg with a cohort-consistent period mass
#     balance (opening + in - out = closing; treated / recovered / disposed)
#     and EPR target / achievement from the registration;
#   * esg.metrics_published / esg.statutory_return_filed;
#   * the regulatory register's next review: guarded, at most 92 days on.
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from . import ewaste_common as c

# GRI 306-4 "waste diverted from disposal", by recovery operation. The final
# route of an item decides its operation; only these count as diverted.
DIVERTED_ROUTES = ("reuse", "refurbish", "harvest", "recycle", "donation")
GRI_306_4_DEFINITION = (
    "GRI 306-4 diversion rate = weight of the items triaged in the period whose final "
    "route is reuse, refurbishment, parts harvest, certified recycling or donation, "
    "divided by the weight of all items triaged in the period (one cohort: the "
    "period's triage decisions)."
)


# ============================================================ one unit, one item
class FixEwasteCollectionS3(models.Model):
    """A retired rental unit reaches M18 by two roads: rental.asset_retired
    (I1) and the posting of the M49 disposal its retirement opened with
    ewaste_route set. Whichever arrives second links to the first - one
    physical unit is one collection (lead note on S1's report)."""

    _inherit = "fix.ewaste.collection"

    @api.model
    def _fix_unit_collection(self, asset=None, device=None, disposal_id=None):
        """The collection already holding this unit: by its rental asset, the
        rental asset's M49 disposal, or an open item of the same device."""
        Col = self.sudo()
        disposal_ids = {disposal_id} if disposal_id else set()
        if asset and "disposal_id" in asset._fields and asset.disposal_id:
            disposal_ids.add(asset.disposal_id.id)
        clauses = []
        if asset:
            clauses.append(
                ["&", ("source_model", "=", asset._name), ("source_res_id", "=", asset.id)]
            )
        if disposal_ids:
            clauses.append(
                [
                    "&",
                    ("source_model", "=", "fix.asset.disposal"),
                    ("source_res_id", "in", sorted(disposal_ids)),
                ]
            )
        if device:
            clauses.append(
                [
                    "&",
                    ("device_id", "=", device.id),
                    ("state", "in", ("collected", "triaged", "destruction", "recycled", "hazmat")),
                ]
            )
        if not clauses:
            return Col.browse()
        domain = clauses[0]
        for clause in clauses[1:]:
            domain = ["|", *domain, *clause]
        return Col.search(domain, order="id asc", limit=1)

    def _fix_link_rental_source(self, asset, weight=0.0, material=None):
        """The I1 event found the unit already received (via M49): record the
        link and, while it is not yet triaged, what the retirement knows."""
        self.ensure_one()
        col = self.sudo()
        if col.source_model == asset._name and col.source_res_id == asset.id:
            return self.browse(col.id)
        vals = {"channel": "rental_retired"}
        if col.state == "collected":
            if not col.device_id and asset.device_id:
                vals["device_id"] = asset.device_id.id
            if col.weight_pending and weight > 0:
                vals["weight_kg"] = weight
            if material and col.material_type == "other":
                vals["material_type"] = material
        col._guarded().write(vals)
        col.message_post(
            body="Also handed over by M13: retired rental unit %s (rental.asset_retired). "
            "One unit, one collection: no second item was opened." % asset.name
        )
        return self.browse(col.id)

    @api.model
    def _fix_handoff_duplicate(self, vals):
        """For a trusted hand-off create: the collection this unit already has."""
        model = vals.get("source_model")
        if not model:
            return self.browse()
        try:
            res_id = int(vals.get("source_res_id") or 0)
        except (TypeError, ValueError):
            res_id = 0
        asset = None
        if model == "fix.asset.disposal" and res_id and "fix.rental.asset" in self.env:
            asset = (
                self.env["fix.rental.asset"].sudo().search([("disposal_id", "=", res_id)], limit=1)
            ) or None
        device = (
            self.env["fix.device"].sudo().browse(vals["device_id"])
            if vals.get("device_id")
            else (asset.device_id if asset and asset.device_id else None)
        )
        if not asset and not device:
            return self.browse()
        found = self._fix_unit_collection(asset=asset, device=device)
        if found and not (found.source_model == model and found.source_res_id == res_id):
            found.message_post(
                body="Also handed over by %s #%s (%s): the unit already has this collection, "
                "so no second item was opened." % (model, res_id, vals.get("source_ref") or "-")
            )
            return found
        return self.browse()

    @api.model_create_multi
    def create(self, vals_list):
        reuse = {}
        if self._fix_guard_open():
            for n, vals in enumerate(vals_list):
                found = self._fix_handoff_duplicate(vals)
                if found:
                    reuse[n] = found.id
        fresh = [vals for n, vals in enumerate(vals_list) if n not in reuse]
        created = iter(super().create(fresh).ids if fresh else [])
        return self.browse(
            [reuse[n] if n in reuse else next(created) for n in range(len(vals_list))]
        )


# ============================================================ exceptions
class FixEwasteCertificateExceptionS3(models.Model):
    _inherit = "fix.ewaste.certificate.exception"

    kind = fields.Selection(
        selection_add=[("overdue", "Certificate Overdue")],
        ondelete={"overdue": "cascade"},
    )

    @api.model
    def _fix_raise(self, items, certificate, kind="uncovered"):
        out = super()._fix_raise(items, certificate, kind=kind)
        out._fix_publish()
        return out

    @api.model
    def _fix_raise_overdue(self, batch, items):
        """AUT-ESG-11: the items of a transferred batch whose certificate is
        past due. One open exception per item (a re-run adds nothing)."""
        out = self.browse()
        today = c.today(self.env)
        for item in items:
            if self.sudo().search_count([("collection_id", "=", item.id), ("state", "=", "open")]):
                continue
            exc = (
                self.sudo()
                ._guarded()
                .create(
                    {
                        "company_id": item.company_id.id,
                        "batch_id": batch.id,
                        "collection_id": item.id,
                        "kind": "overdue",
                        "raised_on": today,
                    }
                )
            )
            out |= self.browse(exc.id)
        out._fix_publish()
        return out

    def _fix_publish(self):
        today = c.today(self.env)
        for exc in self.sudo():
            batch = exc.batch_id
            publish(
                exc.env,
                "ewaste.certificate_exception",
                "fix.ewaste.certificate.exception",
                exc.id,
                {
                    "batch": batch.name,
                    "batch_id": batch.id,
                    "item": exc.collection_id.name,
                    "item_id": exc.collection_id.id,
                    "partner_id": batch.partner_id.id or None,
                    "kind": exc.kind,
                    "age_days": (today - batch.dispatched_on).days if batch.dispatched_on else 0,
                    "company_id": exc.company_id.id,
                },
            )


# ============================================================ certificate clock
class FixEwasteBatchS3(models.Model):
    _inherit = "fix.ewaste.batch"

    @api.model
    def cron_certificate_due(self):
        """AUT-ESG-11 / M18-08: a batch whose disposal certificate is past its
        due date raises an exception for every uncertified item, notifies the
        Quality Manager, and the recycler is suspended at its second overdue
        batch. Safe to re-run (one exception per item, one flag per batch)."""
        today = c.today(self.env)
        suspend_after = c.param_int(self.env, c.P_SUSPEND_AFTER, c.DEFAULT_SUSPEND_AFTER)
        Exc = self.env["fix.ewaste.certificate.exception"].sudo()
        due = self.sudo().search(
            [
                ("state", "in", ("dispatched", "received", "processed")),
                ("certificate_due_on", "!=", False),
                ("certificate_due_on", "<", today),
            ]
        )
        flagged = self.browse()
        for batch in due:
            pending = batch._fix_uncertified()
            if not pending:
                continue
            Exc._fix_raise_overdue(batch, pending)
            if batch.certificate_overdue:
                continue
            batch._guarded().write({"certificate_overdue": True, "certificate_overdue_on": today})
            flagged |= batch
            c.notify(
                batch,
                "Recycler certificate overdue",
                "Batch %s left for %s on %s; its disposal certificate was due on %s and %d "
                "item(s) are still uncertified (AUT-ESG-11)."
                % (
                    batch.name,
                    batch.partner_id.name,
                    batch.dispatched_on,
                    batch.certificate_due_on,
                    len(pending),
                ),
                c.G_COMPLIANCE,
            )
        for partner in flagged.mapped("partner_id"):
            overdue = self.sudo().search_count(
                [("partner_id", "=", partner.id), ("certificate_overdue", "=", True)]
            )
            if overdue >= suspend_after and partner.state == "active":
                partner._fix_suspend(
                    "performance",
                    "%d batches past their certificate due date" % overdue,
                )
        return len(flagged)


# ============================================================ ESG metrics
class FixEsgMetricS3(models.Model):
    _inherit = "fix.esg.metric"

    metric_type = fields.Selection(
        selection_add=[
            ("waste_diverted", "Waste Diverted from Disposal (kg, GRI 306-4)"),
            ("diversion_rate", "Diversion Rate (%, GRI 306-4)"),
            ("material_recovered", "Material Recovered (kg)"),
        ],
        ondelete={
            "waste_diverted": "cascade",
            "diversion_rate": "cascade",
            "material_recovered": "cascade",
        },
    )

    @api.depends("metric_type")
    def _compute_unit(self):
        super()._compute_unit()
        extra = {"waste_diverted": "kg", "diversion_rate": "%", "material_recovered": "kg"}
        for rec in self:
            if rec.metric_type in extra:
                rec.unit = extra[rec.metric_type]

    # ------------------------------------------------------------ GRI 306-4
    @api.model
    def _fix_final_route(self, col):
        """The recovery operation an item's final route is, or its disposal /
        in-process status."""
        if col.state == "routed":
            return {"reuse": "reuse", "refurbish": "refurbish", "harvest": "harvest"}.get(
                col.triage_grade, "in_process"
            )
        if col.state == "certified":
            return "recycle"
        if col.state == "donated":
            return "donation"
        if col.state == "disposed":
            return "disposal"
        return "in_process"

    @api.model
    def _fix_gri_306_4(self, company, date_from, date_to):
        """THE diversion figure (M18-09): one GRI 306-4 definition for the KPI,
        the ESG metric and every report pack (S5 calls this method).

        Cohort: the items of `company` whose (current) triage decision is
        dated in [date_from, date_to] (Dhaka business days). Denominator: their
        weight. Numerator: the weight of those whose final route is reuse,
        refurbishment, parts harvest, certified recycling or donation.
        Returns a dict with the figures by operation and the definition text."""
        Col = self.env["fix.ewaste.collection"].sudo()
        cohort = Col.search(
            [
                ("company_id", "=", company.id),
                ("triage_id", "!=", False),
                ("triage_id.decided_on", ">=", date_from),
                ("triage_id.decided_on", "<=", date_to),
            ]
        )
        by_operation = dict.fromkeys((*DIVERTED_ROUTES, "disposal", "in_process"), 0.0)
        hazardous = {"diverted": 0.0, "disposal": 0.0}
        for col in cohort:
            route = self._fix_final_route(col)
            by_operation[route] += col.weight_kg or 0.0
            if col.triage_grade == "hazardous" or col.material_type == "battery":
                if route in DIVERTED_ROUTES:
                    hazardous["diverted"] += col.weight_kg or 0.0
                elif route == "disposal":
                    hazardous["disposal"] += col.weight_kg or 0.0
        triaged = round(sum(cohort.mapped("weight_kg")), 3)
        diverted = round(sum(by_operation[r] for r in DIVERTED_ROUTES), 3)
        return {
            "date_from": date_from,
            "date_to": date_to,
            "item_count": len(cohort),
            "triaged_kg": triaged,
            "diverted_kg": diverted,
            "directed_to_disposal_kg": round(by_operation["disposal"], 3),
            "in_process_kg": round(by_operation["in_process"], 3),
            "diversion_rate_pct": round(diverted / triaged * 100.0, 2) if triaged > 0 else 0.0,
            "by_operation": {k: round(v, 3) for k, v in by_operation.items()},
            "hazardous_diverted_kg": round(hazardous["diverted"], 3),
            "hazardous_disposal_kg": round(hazardous["disposal"], 3),
            "definition": GRI_306_4_DEFINITION,
        }

    @api.model
    def _fix_material_recovered(self, company, date_from, date_to):
        """M18-23: the material actually recovered (the recycler's recovery
        lines recorded in the period), by class, in kg."""
        lines = (
            self.env["fix.ewaste.material.recovery"]
            .sudo()
            .search(
                [
                    ("company_id", "=", company.id),
                    ("recorded_on", ">=", date_from),
                    ("recorded_on", "<=", date_to),
                ]
            )
        )
        by_class = {}
        for line in lines:
            by_class[line.material_class] = by_class.get(line.material_class, 0.0) + line.weight_kg
        return {
            "total_kg": round(sum(lines.mapped("weight_kg")), 3),
            "by_class": {k: round(v, 3) for k, v in by_class.items()},
            "line_count": len(lines),
        }

    @api.model
    def _fix_figures(self, company, period):
        figures = super()._fix_figures(company, period)
        start, end = c.period_bounds(period)
        gri = self._fix_gri_306_4(company, start, end)
        rec = self._fix_material_recovered(company, start, end)
        figures["waste_diverted"] = (gri["diverted_kg"], gri["item_count"], False)
        figures["diversion_rate"] = (gri["diversion_rate_pct"], gri["item_count"], False)
        figures["material_recovered"] = (rec["total_kg"], rec["line_count"], False)
        return figures

    @api.model
    def compute_period(self, period, company=None):
        """Refresh, and publish esg.metrics_published when a figure moved
        (or on a restatement)."""
        company = company or self.env.company
        before = {
            r.metric_type: r.value
            for r in self.sudo().search(
                [("company_id", "=", company.id), ("period", "=", period), ("computed", "=", True)]
            )
        }
        rows = super().compute_period(period, company)
        after = {r.metric_type: r.value for r in rows.sudo()}
        moved = any(abs(after[k] - before.get(k, -1e12)) > 1e-9 for k in after)
        if moved or self.env.context.get("fix_esg_restatement"):
            versions = sorted({v for v in rows.sudo().mapped("factor_version") if v})
            publish(
                self.env,
                "esg.metrics_published",
                "fix.esg.metric",
                rows[:1].id or 0,
                {
                    "period": period,
                    "company_id": company.id,
                    "metrics": {k: after[k] for k in sorted(after)},
                    "factor_version": ", ".join(versions) or None,
                    "restatement": bool(self.env.context.get("fix_esg_restatement")),
                    "definition": GRI_306_4_DEFINITION,
                },
            )
        return rows

    @api.model
    def _fix_restate_for_certificate(self, certificate):
        """M18-26: a revoked certificate restates the months it counted in:
        the month it was issued (avoided CO2) and the triage months of the
        items it covered (diversion)."""
        cert = certificate.sudo()
        days = {cert.issued_on} | set(
            (cert.collection_ids | cert.battery_ids.mapped("collection_id")).mapped(
                "triage_id.decided_on"
            )
        )
        for period in sorted({d.strftime("%Y-%m") for d in days if d}):
            self.with_context(fix_esg_restatement=True).compute_period(period, cert.company_id)
        return True

    @api.model
    def cron_recompute(self):
        """M18-26: refresh EVERY month a figure can still move in - from the
        company's first e-waste record to this month - not only this month
        and last (an item certified or revoked late moves an old month)."""
        today = c.today(self.env)
        Col = self.env["fix.ewaste.collection"].sudo()
        for company in self.env["res.company"].sudo().search([]):
            first = Col.search(
                [("company_id", "=", company.id), ("collected_on", "!=", False)],
                order="collected_on asc",
                limit=1,
            ).collected_on
            months = c.months_between(first, today) if first else []
            for period in months or [today.strftime("%Y-%m")]:
                self.compute_period(period, company)
        return True

    def _fix_consume_month(self, event, field_date):
        super()._fix_consume_month(event, field_date)
        # the diversion cohort is the triage month
        rec = self.env["fix.ewaste.collection"].sudo().browse(event.get("aggregate_id")).exists()
        day = rec.triage_id.decided_on if rec else False
        if day:
            self.compute_period(day.strftime("%Y-%m"), rec.company_id)


# ============================================================ DoE return
class FixEwasteReturnS3(models.Model):
    _inherit = "fix.ewaste.return"

    # M18-11: the S.R.O. 187/2021 Form-3 mass balance, in kg, one cohort
    opening_kg = fields.Float(string="Opening Stock (kg)", digits=(12, 3), readonly=True)
    received_kg = fields.Float(string="Received in Period (kg)", digits=(12, 3), readonly=True)
    out_kg = fields.Float(string="Left Custody in Period (kg)", digits=(12, 3), readonly=True)
    closing_kg = fields.Float(string="Closing Stock (kg)", digits=(12, 3), readonly=True)
    prepared_for_reuse_kg = fields.Float(
        string="Left for Reuse / Refurbishment / Donation (kg)", digits=(12, 3), readonly=True
    )
    treated_kg = fields.Float(string="Treated by Recycler (kg)", digits=(12, 3), readonly=True)
    recovered_kg = fields.Float(string="Material Recovered (kg)", digits=(12, 3), readonly=True)
    disposed_kg = fields.Float(string="Residue to Disposal (kg)", digits=(12, 3), readonly=True)
    # M18-24: EPR target in force (from the registration) and achievement
    epr_target_pct = fields.Float(string="EPR Collection Target %", readonly=True)
    epr_base_kg = fields.Float(
        string="EPR Obligation Base (kg)",
        digits=(12, 3),
        help="The quantity the EPR collection target applies to in this period (e.g. the "
        "weight placed on the market), as the DoE registration defines it. Owner to "
        "confirm the base (Q-03).",
    )
    epr_achievement_pct = fields.Float(string="EPR Achievement %", readonly=True)

    _MASS_FIELDS = (
        "opening_kg",
        "received_kg",
        "out_kg",
        "closing_kg",
        "prepared_for_reuse_kg",
        "treated_kg",
        "recovered_kg",
        "disposed_kg",
        "epr_target_pct",
        "epr_achievement_pct",
    )

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | set(self._MASS_FIELDS)

    def _frozen_for(self):
        names = super()._frozen_for()
        if self.state != "draft":
            names.add("epr_base_kg")
        return names

    @api.depends("treated_kg", "recovered_kg", "total_tonnage_collected", "total_tonnage_recycled")
    def _compute_mass_balance(self):
        """Recovery rate = recovered / treated, one cohort (the batches the
        recycler processed in the period), from kg - never above 100%."""
        for rec in self:
            treated = rec.treated_kg or 0.0
            rec.recovery_rate_pct = (
                round(min(rec.recovered_kg or 0.0, treated) / treated * 100.0, 2)
                if treated > 0
                else 0.0
            )

    @api.model
    def _fix_custody_exit(self, col):
        """The day an item left our custody, or None while we hold it."""
        if col.state == "routed":
            return col.routed_on
        if col.state == "donated":
            done = col.donation_ids.filtered(lambda d: d.state == "handed_over")[:1]
            return done.handed_over_on or col.write_date.date()
        batch = col.batch_id
        if batch and batch.state != "draft" and batch.dispatched_on:
            return batch.dispatched_on
        cells = col.battery_ids
        if cells and all(b.batch_id and b.batch_id.dispatched_on for b in cells):
            return max(cells.mapped("batch_id.dispatched_on"))
        return None

    def _fix_mass_balance_kg(self):
        """The period mass balance for this return, in kg (M18-11)."""
        self.ensure_one()
        start, end = c.period_bounds(self.period)
        company = self.company_id
        Col = self.env["fix.ewaste.collection"].sudo()
        items = Col.search([("company_id", "=", company.id), ("collected_on", "<=", end)])
        opening = received = out = closing = reuse = 0.0
        for col in items:
            weight = col.weight_kg or 0.0
            came = col.collected_on
            left = self._fix_custody_exit(col)
            if left and left < came:
                left = came
            if came < start and (not left or left >= start):
                opening += weight
            if start <= came <= end:
                received += weight
            if left and start <= left <= end:
                out += weight
                if col.state in ("routed", "donated"):
                    reuse += weight
            if not left or left > end:
                closing += weight
        batches = (
            self.env["fix.ewaste.batch"]
            .sudo()
            .search(
                [
                    ("company_id", "=", company.id),
                    ("state", "=", "processed"),
                    ("processed_on", ">=", start),
                    ("processed_on", "<=", end),
                ]
            )
        )
        treated = sum(batches.mapped("processed_weight_kg"))
        recovered = min(sum(batches.mapped("recovery_ids.weight_kg")), treated)
        vals = {
            "opening_kg": round(opening, 3),
            "received_kg": round(received, 3),
            "out_kg": round(out, 3),
            "closing_kg": round(closing, 3),
            "prepared_for_reuse_kg": round(reuse, 3),
            "treated_kg": round(treated, 3),
            "recovered_kg": round(recovered, 3),
            "disposed_kg": round(treated - recovered, 3),
            # kept for the filed form and its readers: tonnes from the kg
            "total_tonnage_collected": round(received / 1000.0, 3),
            "total_tonnage_recycled": round(treated / 1000.0, 3),
        }
        if abs(vals["opening_kg"] + vals["received_kg"] - vals["out_kg"] - vals["closing_kg"]) > (
            0.01
        ):
            raise UserError(
                "Return %s: the mass balance does not close (opening %.3f + in %.3f - out "
                "%.3f != closing %.3f)." % (self.name, opening, received, out, closing)
            )
        registration = (
            self.env["fix.ewaste.registration"].sudo()._fix_active_for(company, self.authority)
        )
        target = registration.epr_target_pct if registration else 0.0
        vals["epr_target_pct"] = target
        vals["epr_achievement_pct"] = (
            round(received / self.epr_base_kg * 100.0, 2) if self.epr_base_kg > 0 else 0.0
        )
        return vals

    def _fix_mass_balance(self):
        """(collected t, recycled t): the kg balance, kept for old callers."""
        vals = self._fix_mass_balance_kg()
        return vals["total_tonnage_collected"], vals["total_tonnage_recycled"]

    def action_calculate_mass_balance(self):
        c.require_group(self.env, c.G_COMPLIANCE, "E-Waste Compliance Officer", "compute a return")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Return %s is %s: its figures are filed." % (rec.name, rec.state))
            rec._guarded().write(rec._fix_mass_balance_kg())
        return True

    def action_submit_return(self):
        """Submit on fresh figures (kg balance), then publish the filing."""
        c.require_group(self.env, c.G_COMPLIANCE, "E-Waste Compliance Officer", "submit a return")
        for rec in self.filtered(lambda r: r.state == "draft"):
            rec._guarded().write(rec._fix_mass_balance_kg())
        res = super().action_submit_return()
        for rec in self:
            if rec.state != "submitted":
                continue
            publish(
                rec.env,
                "esg.statutory_return_filed",
                "fix.ewaste.return",
                rec.id,
                {
                    "authority": rec.authority,
                    "period": rec.period,
                    "form": rec.form_type,
                    "reference": rec.reference,
                    "volumes_kg": {n: rec[n] for n in rec._MASS_FIELDS if n.endswith("_kg")},
                    "recovery_rate_pct": rec.recovery_rate_pct,
                    "epr_target_pct": rec.epr_target_pct,
                    "epr_achievement_pct": rec.epr_achievement_pct,
                    "company_id": rec.company_id.id,
                },
            )
        return res


# ============================================================ register
class FixEwasteObligationS3(models.Model):
    _inherit = "fix.ewaste.obligation"

    def _fix_guarded_fields(self) -> set:
        # M18-17 (BRU-ESG-16): the review clock is set by activation and by
        # each review, never typed
        return set(super()._fix_guarded_fields()) | {"next_review"}

    @api.constrains("next_review", "last_reviewed", "state")
    def _check_review_cap(self):
        """At most a quarter (92 days) ahead of the last review, or of
        today for one never reviewed."""
        today = c.today(self.env)
        for rec in self:
            if not rec.next_review or rec.state == "retired":
                continue
            base = rec.last_reviewed or today
            if rec.next_review > base + timedelta(days=92):
                raise ValidationError(
                    "%s: the next review %s is more than a quarter after %s (BRU-ESG-16)."
                    % (rec.name, rec.next_review, base)
                )
