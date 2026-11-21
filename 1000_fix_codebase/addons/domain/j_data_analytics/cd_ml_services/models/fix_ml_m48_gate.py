# fix_ml_m48_gate — A07 ERP audit (2026-11-20) M48-02 / M48-10: what makes an
# M48 failure prediction one that may drive work, and the monthly precision.
#
# The "published M26 model" gate checked a catalogue code: the only production
# predictive-maintenance entry was the aggregator of the predictions themselves,
# so an operator typed a 0.9 "failure predicted", named that code, and the gate
# passed. A prediction now drives work (an approved action, a preventive work
# order) only when:
#   - the M26 inference path recorded it (score_source = engine, M48 side), and
#   - it carries the model version that scored it, DEPLOYED (not demoted or
#     retired), with an accuracy evaluation gate and every gate passed by a
#     reviewer (fix.ml.evaluation.gate), and
#   - its model is not past its governance review date (BRU-AIM-26).
# The seeded aggregator version was grandfathered as deployed with no gate, so it
# no longer qualifies: nothing it "scores" drives work.
#
# BRU-IOT-22 / AUT-IOT-17: each month the precision of every model version is
# computed (confirmed + prevented over confirmed + prevented + false alarm;
# unknown excluded). Below cd_stream_registry.precision_threshold_pct for two
# consecutive months suspends the model's customer-facing use (spec Q-08: the
# threshold is the owner's; unset, precision is recorded and nothing suspends).
import json
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

from libs.py.fix_events import publish

from .fix_ml_governance import MODEL_OWNER_GROUP

PRECISION_THRESHOLD_PARAM = "cd_stream_registry.precision_threshold_pct"
DHAKA = "Asia/Dhaka"


def _dhaka_today(env):
    return fields.Date.context_today(env["res.users"].with_context(tz=DHAKA))


class FixMlModelM48(models.Model):
    _inherit = "fix.ml.model"

    m48_customer_suspended = fields.Boolean(
        string="Customer-Facing Use Suspended (M48)",
        readonly=True,
        copy=False,
        help="BRU-IOT-22: precision below the published threshold for two consecutive "
        "months. Its predictions no longer raise customer work until reinstated.",
    )
    m48_suspended_on = fields.Date(string="Suspended On", readonly=True, copy=False)
    m48_suspension_note = fields.Text(string="Suspension Record", readonly=True, copy=False)

    def write(self, vals):
        if not self.env.su and {
            "m48_customer_suspended",
            "m48_suspended_on",
            "m48_suspension_note",
        } & set(vals):
            raise UserError(
                "A model's customer-facing suspension changes only through the monthly "
                "precision run or Reinstate (Model Owner)."
            )
        return super().write(vals)

    def action_m48_reinstate(self, reason=None):
        """M26 review lifts a BRU-IOT-22 suspension (Model Owner, with a reason)."""
        if not (self.env.su or self.env.user.has_group(MODEL_OWNER_GROUP)):
            raise AccessError("Reinstating a suspended model is a Model Owner act (M26).")
        why = (reason or "").strip()
        if not why:
            raise UserError("Give the reason the model is reinstated (the M26 review).")
        for rec in self.sudo():
            if not rec.m48_customer_suspended:
                raise UserError("Model %s is not suspended." % rec.code)
            rec.write(
                {
                    "m48_customer_suspended": False,
                    "m48_suspension_note": "%s\nReinstated %s by %s: %s"
                    % (
                        rec.m48_suspension_note or "",
                        _dhaka_today(self.env),
                        self.env.user.name,
                        why,
                    ),
                }
            )
        return True


class FixPredictiveMaintenanceM26(models.Model):
    _inherit = "fix.predictive.maintenance"

    _OUTPUT_FIELDS = {
        "equipment_id",
        "prediction",
        "confidence",
        "estimated_days_to_failure",
        "model_name",
        "feature_window_from",
        "feature_window_to",
        "last_evaluated",
        "failure_mode",
        "rul_low_days",
        "rul_high_days",
        "model_version_id",
        "input_snapshot_ref",
    }

    # BRU-IOT-11: the version that scored it and the input it scored.
    model_version_id = fields.Many2one(
        "fix.ml.model.version",
        string="Model Version (M26)",
        ondelete="restrict",
        index=True,
        help="The deployed M26 model version that produced this score.",
    )
    input_snapshot_ref = fields.Char(
        string="Input Snapshot",
        help="Where the feature values the score was computed on are kept, so it can be "
        "reproduced (BRU-IOT-11).",
    )

    @api.model_create_multi
    def create(self, vals_list):
        engine = self.env.su or bool(self.env.context.get("fix_m26_inference"))
        if engine:
            Model = self.env["fix.ml.model"].sudo()
            for vals in vals_list:
                if vals.get("model_version_id") or not (vals.get("model_name") or "").strip():
                    continue
                model = Model.search(
                    [
                        ("code", "=", vals["model_name"].strip()),
                        ("kind", "=", "predictive_maintenance"),
                    ],
                    limit=1,
                )
                serving = model._serving_version() if model else False
                if serving:
                    vals["model_version_id"] = serving.id
        elif any(v.get("model_version_id") for v in vals_list):
            raise UserError(
                "The model version of a score is recorded by the M26 inference path, not typed."
            )
        return super().create(vals_list)

    def _fix_publication_problem(self):
        problem = super()._fix_publication_problem()
        if problem:
            return problem
        model = self._fix_catalog_model()
        version = self.sudo().model_version_id
        if not version:
            return "carries no M26 model version: nothing records which model scored it"
        if version.model_id != model:
            return "carries version %s of another model than %s" % (
                version.display_name,
                model.code,
            )
        if version.state != "deployed":
            return "was scored by version %s, which is %s, not deployed" % (
                version.display_name,
                version.state,
            )
        gates = version.sudo().gate_ids
        if not gates.filtered(lambda g: g.gate == "accuracy" and g.result == "passed"):
            return (
                "was scored by version %s, which has no passed accuracy evaluation gate: its "
                "accuracy was never measured against the model's target" % version.display_name
            )
        if gates.filtered(lambda g: g.result != "passed"):
            return "was scored by version %s, which has a gate not passed" % version.display_name
        if model.review_date and model.review_date < _dhaka_today(self.env):
            return "names model %s, whose governance review was due %s" % (
                model.code,
                model.review_date,
            )
        return ""

    def _fix_customer_use_problem(self):
        """BRU-IOT-22: customer-facing work is refused while the model is
        suspended. "" when it may raise customer work."""
        self.ensure_one()
        model = self._fix_catalog_model()
        if model and model.m48_customer_suspended:
            return (
                "model %s is suspended from customer-facing use (precision below the "
                "threshold for two months, BRU-IOT-22)" % model.code
            )
        return ""

    @api.model
    def m26_record_prediction(self, model_code, vals, input_snapshot_ref=None):
        """The M26 inference path's one way to record an M48 score: the serving
        (deployed) version of `model_code` is pinned on it. Engine code only."""
        if not self.env.su:
            raise AccessError("Only the M26 inference service records an engine score.")
        model = (
            self.env["fix.ml.model"]
            .sudo()
            .search([("code", "=", model_code), ("kind", "=", "predictive_maintenance")], limit=1)
        )
        serving = model._serving_version() if model else False
        if not serving:
            raise UserError("Model %s has no deployed version: it scores nothing." % model_code)
        return self.with_context(fix_m26_inference=True).create(
            dict(
                vals,
                model_name=model.code,
                model_version_id=serving.id,
                input_snapshot_ref=input_snapshot_ref or vals.get("input_snapshot_ref"),
            )
        )


class FixMlM48Precision(models.Model):
    """AUT-IOT-17: the measured precision of one model version in one month."""

    _name = "fix.ml.m48.precision"
    _description = "M48 Prediction Precision (monthly)"
    _order = "period_start desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    model_id = fields.Many2one("fix.ml.model", required=True, index=True, ondelete="restrict")
    version_id = fields.Many2one("fix.ml.model.version", index=True, ondelete="restrict")
    period_start = fields.Date(required=True)
    period_end = fields.Date(required=True)
    true_positive = fields.Integer(string="Confirmed + Prevented")
    false_positive = fields.Integer(string="False Alarms")
    unknown = fields.Integer(string="Unknown (excluded)")
    precision_pct = fields.Float(string="Precision %", digits=(6, 1))
    threshold_pct = fields.Float(string="Threshold %", digits=(6, 1))
    below_threshold = fields.Boolean()
    detail = fields.Text()

    _period_once = models.Constraint(
        "UNIQUE (model_id, version_id, period_start)", "One precision record per month."
    )

    def write(self, vals):
        if not self.env.su:
            raise UserError("A precision record is measured, never edited.")
        return super().write(vals)

    @api.model
    def _month_bounds(self, day):
        first = day.replace(day=1)
        prev_end = first - timedelta(days=1)
        return prev_end.replace(day=1), prev_end

    @api.model
    def cron_m48_precision(self, today=None):
        """Monthly: the previous Dhaka month's precision per model version; a
        model below the threshold this month and the month before is suspended
        from customer-facing use (BRU-IOT-22) and telemetry.model_suspended told."""
        today = today or _dhaka_today(self.env)
        start, end = self._month_bounds(today)
        raw = self.env["ir.config_parameter"].sudo().get_param(PRECISION_THRESHOLD_PARAM)
        try:
            threshold = float(raw) if raw not in (None, False, "") else None
        except ValueError:
            threshold = None
        Pred = self.env["fix.predictive.maintenance"].sudo()
        begin = fields.Datetime.to_datetime(start) - timedelta(hours=6)
        finish = fields.Datetime.to_datetime(end + timedelta(days=1)) - timedelta(hours=6)
        preds = Pred.search(
            [
                ("outcome", "in", ("confirmed", "prevented", "false_alarm", "unknown")),
                ("outcome_recorded_on", ">=", begin),
                ("outcome_recorded_on", "<", finish),
                ("model_name", "!=", False),
            ]
        )
        groups = {}
        for pred in preds:
            model = pred._fix_catalog_model()
            if model:
                groups.setdefault((model, pred.model_version_id), Pred.browse())
                groups[(model, pred.model_version_id)] |= pred
        written = self.browse()
        for (model, version), rows in groups.items():
            if self.sudo().search_count(
                [
                    ("model_id", "=", model.id),
                    ("version_id", "=", version.id or False),
                    ("period_start", "=", start),
                ]
            ):
                continue
            tp = len(rows.filtered(lambda p: p.outcome in ("confirmed", "prevented")))
            fp = len(rows.filtered(lambda p: p.outcome == "false_alarm"))
            unknown = len(rows.filtered(lambda p: p.outcome == "unknown"))
            precision = round(tp / (tp + fp) * 100, 1) if (tp + fp) else None
            below = threshold is not None and precision is not None and precision < threshold
            rec = self.sudo().create(
                {
                    "company_id": model.company_id.id or self.env.company.id,
                    "model_id": model.id,
                    "version_id": version.id or False,
                    "period_start": start,
                    "period_end": end,
                    "true_positive": tp,
                    "false_positive": fp,
                    "unknown": unknown,
                    "precision_pct": precision or 0.0,
                    "threshold_pct": threshold or 0.0,
                    "below_threshold": below,
                    "detail": json.dumps(
                        {"predictions": rows.mapped("name"), "threshold_set": threshold is not None}
                    ),
                }
            )
            written |= rec
            if below:
                prev_start, _prev_end = self._month_bounds(start)
                before = self.sudo().search(
                    [
                        ("model_id", "=", model.id),
                        ("period_start", "=", prev_start),
                        ("below_threshold", "=", True),
                    ],
                    limit=1,
                )
                if before and not model.m48_customer_suspended:
                    note = "Precision %.1f%% (%s) and %.1f%% (%s), below %.1f%%." % (
                        before.precision_pct,
                        prev_start.strftime("%Y-%m"),
                        precision,
                        start.strftime("%Y-%m"),
                        threshold,
                    )
                    model.sudo().write(
                        {
                            "m48_customer_suspended": True,
                            "m48_suspended_on": today,
                            "m48_suspension_note": note,
                        }
                    )
                    publish(
                        self.env,
                        "telemetry.model_suspended",
                        "fix.ml.model",
                        model.id,
                        {
                            "model": model.code,
                            "version": version.version or "",
                            "precision": precision,
                            "threshold": threshold,
                            "period": start.strftime("%Y-%m"),
                        },
                    )
        return written
