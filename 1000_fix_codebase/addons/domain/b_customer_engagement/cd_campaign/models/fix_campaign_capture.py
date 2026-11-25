# M35 capture audit (2026-11-14): the records the sub-module pages capture.
#
# Spec: 03_Modules/B_.../M35_Marketing_Campaigns_and_Demand_Generation.md
#   §5.2 FR-MKT-009..014, §5.5 FR-MKT-031..037, §9 BRU-MKT-02/03/11/12/14,
#   §10.1 fix.audience.definition, fix.campaign.budget, fix.attribution.model,
#   fix.ab.test, fix.ad.placement, §6 T-03/T-05/T-06.
#
# What the pages could not capture before:
#   * Audience from Segments offered "+ New Campaign", and a campaign's
#     audience was a typed res.partner domain or a hard-coded audience type:
#     no campaign could name an M33 segment (BRU-MKT-02), nobody saw the
#     post-suppression reach before approval (BRU-MKT-03), and there was no
#     holdout group (FR-MKT-014, BRU-MKT-14).
#   * Budget & Attribution had no capture at all. Spend booked outside the
#     estate (media, print, agency) could not be recorded, so "actual spend"
#     counted message cost and offer discounts only, and nothing stopped spend
#     passing the approved budget (BRU-MKT-11). The attribution model was a
#     method argument, not a versioned record (BRU-MKT-12, T-06).
#   * Experimentation let anyone type the experiment's state; there was no
#     start, no conclusion, no winner.
#   * Portal Advertising had no advertiser and no run window.
import hashlib

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

# fix_campaign_ops defines the experiment and the ad placement extended below:
# imported here so it is defined first whatever order __init__ lists them in.
from . import fix_campaign_ops  # noqa: F401
from .fix_attribution import ATTRIBUTION_MODELS, DEFAULT_LOOKBACK_DAYS
from .fix_campaign import CHANNEL_CONSENTS

MARKETING_MANAGER = "cd_campaign.group_marketing_manager"

# Holdout is a measurement control, not a way to shrink an audience: above
# half the audience a "holdout" is the campaign.
HOLDOUT_MAX_PCT = 50

AUDIENCE_FIELDS = frozenset(
    {
        "target_audience_type",
        "audience_domain",
        "segment_ids",
        "exclude_segment_ids",
        "holdout_pct",
        "holdout_key",
        "channel",
    }
)


def holdout_bucket(key, partner_id):
    """0..99, stable for a (key, party) pair (spec T-05).

    A stable hash, not random(): the same party lands in the same bucket every
    time, so campaigns sharing a holdout key share one holdout group."""
    digest = hashlib.sha256(("%s:%s" % (key, partner_id)).encode()).hexdigest()
    return int(digest[:8], 16) % 100


class FixCampaignAudience(models.Model):
    """The campaign's audience composed from governed M33 segments."""

    _inherit = "fix.campaign"

    target_audience_type = fields.Selection(
        selection_add=[("segments", "Governed M33 Segments")],
        ondelete={"segments": "set default"},
    )
    segment_ids = fields.Many2many(
        "fix.segment",
        "fix_campaign_segment_include_rel",
        "campaign_id",
        "segment_id",
        string="Include Segments",
        help="The audience is every current member of these M33 segments "
        "(BRU-MKT-02: audiences come from governed segments).",
    )
    exclude_segment_ids = fields.Many2many(
        "fix.segment",
        "fix_campaign_segment_exclude_rel",
        "campaign_id",
        "segment_id",
        string="Exclude Segments",
        help="Current members of these segments are left out, whatever the audience.",
    )
    holdout_pct = fields.Integer(
        string="Holdout (%)",
        default=0,
        help="Share of the reachable audience kept back to measure what the "
        "campaign caused (FR-MKT-014). Held-out parties receive nothing.",
    )
    holdout_key = fields.Char(
        string="Holdout Key",
        help="Campaigns with the same key share one holdout group (a party "
        "held out of one is held out of all). Empty: this campaign alone.",
    )
    holdout_partner_ids = fields.Many2many(
        "res.partner",
        "fix_campaign_holdout_rel",
        "campaign_id",
        "partner_id",
        string="Holdout Group",
        readonly=True,
        copy=False,
        help="Set at launch: the reachable parties kept back for measurement.",
    )
    holdout_count = fields.Integer(string="Held Out", compute="_compute_holdout_count")
    # list columns: the workspace grid prints a many2many as its ids
    segment_names = fields.Char(string="Segments Included", compute="_compute_audience_names")
    exclude_segment_names = fields.Char(
        string="Segments Excluded", compute="_compute_audience_names"
    )
    comarketing_partner_names = fields.Char(
        string="Co-Marketing Partners (names)", compute="_compute_comarketing_partner_names"
    )
    estimated_reach = fields.Integer(
        string="Estimated Reach (after suppression)",
        readonly=True,
        copy=False,
        help="Parties the campaign would reach after consent, DND and the "
        "holdout are applied (BRU-MKT-03). Cleared when the audience changes.",
    )
    estimated_at = fields.Datetime(string="Estimated At", readonly=True, copy=False)
    estimate_breakdown = fields.Char(
        string="How The Estimate Was Reached", readonly=True, copy=False
    )

    spend_ids = fields.One2many("fix.campaign.spend", "campaign_id", string="Recorded Spend")
    attribution_model_id = fields.Many2one(
        "fix.attribution.model",
        string="Attribution Model (pinned)",
        readonly=True,
        copy=False,
        help="The model in force when the campaign completed. A later model "
        "does not restate a closed campaign (BRU-MKT-12).",
    )

    @api.constrains("holdout_pct")
    def _check_holdout_pct(self):
        for rec in self:
            if not 0 <= (rec.holdout_pct or 0) <= HOLDOUT_MAX_PCT:
                raise ValidationError(
                    "The holdout is between 0 and %d%% of the audience." % HOLDOUT_MAX_PCT
                )

    @api.constrains("target_audience_type", "segment_ids")
    def _check_segment_audience(self):
        for rec in self:
            if rec.target_audience_type == "segments" and not rec.segment_ids:
                raise ValidationError(
                    "A segment audience names at least one M33 segment to include."
                )

    @api.depends("segment_ids", "exclude_segment_ids")
    def _compute_audience_names(self):
        for rec in self:
            rec.segment_names = ", ".join(rec.segment_ids.mapped("name"))
            rec.exclude_segment_names = ", ".join(rec.exclude_segment_ids.mapped("name"))

    def _compute_comarketing_partner_names(self):
        # partner_ids comes from the M40 partner module when it is installed
        for rec in self:
            partners = rec["partner_ids"] if "partner_ids" in rec._fields else []
            rec.comarketing_partner_names = ", ".join(p.name for p in partners)

    @api.depends("holdout_partner_ids")
    def _compute_holdout_count(self):
        for rec in self:
            rec.holdout_count = len(rec.holdout_partner_ids)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "holdout_partner_ids",
            "estimated_reach",
            "estimated_at",
            "estimate_breakdown",
            "attribution_model_id",
        }

    def write(self, vals):
        touched = AUDIENCE_FIELDS & set(vals)
        if touched and not self._fix_guard_open():
            for rec in self:
                changed = [n for n in touched if rec._fix_guard_differs(n, vals[n], rec[n])]
                if not changed:
                    continue
                if rec.state != "draft":
                    raise UserError(
                        "The audience of %s is fixed once it has launched: it is %s."
                        % (rec.name, dict(rec._fields["state"].selection)[rec.state])
                    )
        res = super().write(vals)
        if touched:
            # an estimate describes the audience it was made for
            stale = self.filtered(lambda r: r.state == "draft" and r.estimated_at)
            if stale:
                stale._guarded().write(
                    {"estimated_reach": 0, "estimated_at": False, "estimate_breakdown": False}
                )
        return res

    # ------------------------------------------------------------------
    # Audience resolution
    # ------------------------------------------------------------------
    def _segment_members(self, segments):
        if not segments:
            return set()
        rows = (
            self.env["fix.segment.membership"]
            .sudo()
            .search([("segment_id", "in", segments.ids), ("exited_at", "=", False)])
        )
        return set(rows.mapped("partner_id").ids)

    def _audience_domain(self):
        """Segments are the governed audience; exclusions apply to any audience."""
        self.ensure_one()
        if self.target_audience_type == "segments":
            if not self.segment_ids:
                raise UserError("Name at least one M33 segment to include.")
            ids = self._segment_members(self.segment_ids)
            domain = [("id", "in", sorted(ids) or [0])]
        else:
            domain = super()._audience_domain()
        excluded = self._segment_members(self.exclude_segment_ids)
        if excluded:
            domain = [*domain, ("id", "not in", sorted(excluded))]
        return domain

    def _holdout_of(self, partners):
        """The parties of ``partners`` kept back for measurement (T-05)."""
        self.ensure_one()
        pct = self.holdout_pct or 0
        if pct <= 0 or not partners:
            return partners.browse()
        key = self.holdout_key or "campaign-%s" % self.id
        return partners.filtered(lambda p: holdout_bucket(key, p.id) < pct)

    def action_estimate_audience(self):
        """Post-suppression reach for the approver (BRU-MKT-03, FR-MKT-012)."""
        for rec in self:
            if rec.state != "draft":
                raise UserError("Estimate the audience of a draft campaign.")
            domain = rec._audience_domain()
            Partner = self.env["res.partner"]
            audience = Partner.search(domain)
            if rec.channel in CHANNEL_CONSENTS:
                consented = rec._consented(domain)
                reachable = rec._dnd_reachable(consented)
                held = rec._holdout_of(reachable)
                reach = len(reachable) - len(held)
                breakdown = (
                    "%d in the audience, %d without marketing consent, %d on the DND "
                    "registry, %d held out: %d reachable"
                    % (
                        len(audience),
                        len(audience) - len(consented),
                        len(consented) - len(reachable),
                        len(held),
                        reach,
                    )
                )
            else:
                held = rec._holdout_of(audience)
                reach = len(audience) - len(held)
                breakdown = (
                    "%d in the audience, %d held out: %d (this channel addresses no "
                    "individual, so consent and DND do not apply)"
                    % (len(audience), len(held), reach)
                )
            rec._guarded().write(
                {
                    "estimated_reach": reach,
                    "estimated_at": fields.Datetime.now(),
                    "estimate_breakdown": breakdown,
                }
            )
            rec.message_post(body="Audience estimated: %s." % breakdown)
        return True

    def action_request_approval(self, *args, **kwargs):
        # AUT-MKT-01: the approver sees the post-suppression reach, so the
        # estimate is refreshed when approval is requested. An audience that
        # cannot be resolved yet does not stop the request: the approver then
        # sees no estimate, which is what is true.
        for rec in self.filtered(lambda r: r.state == "draft"):
            try:
                with self.env.cr.savepoint():
                    rec.action_estimate_audience()
            except (UserError, ValidationError):
                continue
        return super().action_request_approval(*args, **kwargs)

    def action_complete(self):
        res = super().action_complete()
        model = self.env["fix.attribution.model"].sudo()._current()
        if model:
            self.filtered(lambda r: not r.attribution_model_id)._guarded().write(
                {"attribution_model_id": model.id}
            )
        return res

    def _recorded_spend(self) -> float:
        spend = super()._recorded_spend()
        if not self.id:
            return spend
        lines = (
            self.env["fix.campaign.spend"]
            .sudo()
            .search([("campaign_id", "=", self.id), ("state", "=", "recorded")])
        )
        return spend + sum(lines.mapped("amount"))


SPEND_CATEGORIES = [
    ("media", "Media buy (TV, radio, digital ads)"),
    ("print", "Print and outdoor"),
    ("event", "Event and activation"),
    ("agency", "Agency and production fees"),
    ("influencer", "Influencer and content partner"),
    ("bulk_message", "Bulk messaging outside the estate"),
    ("other", "Other"),
]


class FixCampaignSpend(models.Model):
    """Spend on a campaign booked outside the estate (FR-MKT-033).

    Message cost and offer discounts are already counted from the estate's own
    records; this is the media buy, the printing, the agency invoice."""

    _name = "fix.campaign.spend"
    _description = "Campaign Spend"
    _inherit = ["fix.guarded.mixin"]
    _order = "spend_date desc, id desc"

    campaign_id = fields.Many2one(
        "fix.campaign", string="Campaign", required=True, ondelete="restrict", index=True
    )
    company_id = fields.Many2one(related="campaign_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(related="campaign_id.operating_unit_id", store=True)
    currency_id = fields.Many2one(related="campaign_id.currency_id")
    name = fields.Char(string="What Was Bought", required=True)
    category = fields.Selection(SPEND_CATEGORIES, required=True, default="media")
    spend_date = fields.Date(string="Spend Date", required=True, default=fields.Date.context_today)
    amount = fields.Monetary(string="Amount", currency_field="currency_id", required=True)
    vendor_partner_id = fields.Many2one("res.partner", string="Supplier", ondelete="restrict")
    reference = fields.Char(string="Invoice / PO Reference")
    state = fields.Selection(
        [("recorded", "Recorded"), ("void", "Void")],
        default="recorded",
        required=True,
        readonly=True,
    )
    void_reason = fields.Char(string="Why It Was Voided", readonly=True)
    voided_by_id = fields.Many2one("res.users", string="Voided By", readonly=True)
    voided_at = fields.Datetime(string="Voided At", readonly=True)

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self:
            # a recorded spend is voided and recorded again, never edited
            locked |= {
                "campaign_id",
                "name",
                "category",
                "spend_date",
                "amount",
                "vendor_partner_id",
                "reference",
            }
        return locked

    @api.constrains("amount")
    def _check_amount(self):
        for rec in self:
            if (rec.amount or 0.0) <= 0:
                raise ValidationError("A spend is a positive amount.")

    def _assert_within_budget(self):
        """BRU-MKT-11: no spend past the approved budget without re-approval."""
        for rec in self:
            campaign = rec.campaign_id
            total = campaign._recorded_spend()
            if total > (campaign.budget or 0.0) + 0.005:
                raise UserError(
                    "Recording BDT %.2f takes %s to BDT %.2f against a budget of BDT %.2f. "
                    "Raise the budget and have it approved again first (BRU-MKT-11)."
                    % (rec.amount, campaign.name, total, campaign.budget or 0.0)
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not self.env.su and vals.get("state", "recorded") != "recorded":
                raise UserError("A spend is recorded first and voided later.")
        recs = super().create(vals_list)
        recs._assert_within_budget()
        for rec in recs:
            rec.campaign_id.message_post(
                body="Spend recorded: %s, BDT %.2f (%s)."
                % (rec.name, rec.amount, rec.reference or "no reference")
            )
        return recs

    def write(self, vals):
        if not self._fix_guard_open():
            # the P03 form posts every field it shows on save: an unchanged
            # value is not a change
            # workflow-owned fields (state, the void stamps) are refused by the
            # guard mixin with its own message, as on every guarded model; the
            # spend's own rule covers the figures it was recorded with
            guarded = self._fix_guarded_fields()
            changed = {
                n
                for n in vals
                for rec in self
                if n in rec._fields
                and n not in guarded
                and rec._fix_guard_differs(n, vals[n], rec[n])
            }
            if changed:
                raise UserError(
                    "A recorded spend is not edited. Void it with a reason and record "
                    "the correct one."
                )
        return super().write(vals)

    def unlink(self):
        raise UserError("A recorded spend is voided, never deleted.")

    def action_void(self, reason=None):
        reason = (reason or "").strip()
        if not reason:
            raise UserError("Say why the spend is voided.")
        for rec in self:
            if rec.state != "recorded":
                raise UserError("%s is already void." % rec.name)
        self._guarded().write(
            {
                "state": "void",
                "void_reason": reason,
                "voided_by_id": self.env.user.id,
                "voided_at": fields.Datetime.now(),
            }
        )
        for rec in self:
            rec.campaign_id.message_post(
                body="Spend voided: %s, BDT %.2f. Reason: %s" % (rec.name, rec.amount, reason)
            )
        return True


class FixAttributionModel(models.Model):
    """The versioned attribution model (BRU-MKT-12, spec T-06)."""

    _name = "fix.attribution.model"
    _description = "Attribution Model"
    _inherit = ["fix.guarded.mixin"]
    _order = "code, version desc"
    _rec_name = "display_label"

    code = fields.Char(required=True, help="Stable name; each change is a new version of it.")
    name = fields.Char(required=True)
    method = fields.Selection(ATTRIBUTION_MODELS, required=True, default="position")
    lookback_days = fields.Integer(
        string="Lookback (days)",
        required=True,
        default=DEFAULT_LOOKBACK_DAYS,
        help="How far before a conversion a touch may be and still be credited.",
    )
    version = fields.Integer(readonly=True, copy=False, default=1)
    effective_from = fields.Date(readonly=True, copy=False)
    state = fields.Selection(
        [("draft", "Draft"), ("active", "In Force"), ("superseded", "Superseded")],
        default="draft",
        required=True,
        readonly=True,
        copy=False,
    )
    rationale = fields.Text(help="Why this model, and what changed from the last version.")
    activated_by_id = fields.Many2one(
        "res.users", string="Put In Force By", readonly=True, copy=False
    )
    activated_at = fields.Datetime(string="Put In Force At", readonly=True, copy=False)
    display_label = fields.Char(compute="_compute_display_label", store=True)

    _code_version_unique = models.Constraint(
        "UNIQUE (code, version)", "That version of the model already exists."
    )

    @api.depends("code", "version", "method")
    def _compute_display_label(self):
        labels = dict(ATTRIBUTION_MODELS)
        for rec in self:
            rec.display_label = "%s v%s · %s" % (
                rec.code or "?",
                rec.version or 1,
                (labels.get(rec.method) or "").split(" — ")[0],
            )

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= {"code", "name", "method", "lookback_days", "rationale"}
        return locked

    @api.constrains("lookback_days")
    def _check_lookback(self):
        for rec in self:
            if not 1 <= (rec.lookback_days or 0) <= 365:
                raise ValidationError("The lookback is between 1 and 365 days.")

    @api.model
    def _current(self):
        return self.search([("state", "=", "active")], order="activated_at desc, id desc", limit=1)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            code = (vals.get("code") or "").strip()
            if code:
                vals["code"] = code
                last = self.sudo().search([("code", "=", code)], order="version desc", limit=1)
                vals["version"] = (last.version or 0) + 1
            if not self.env.su:
                for name in ("state", "effective_from", "activated_by_id", "activated_at"):
                    vals.pop(name, None)
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_open():
            frozen = self.filtered(lambda r: r.state != "draft")
            if frozen:
                raise UserError(
                    "%s is or was in force and is not changed: create a new version "
                    "(BRU-MKT-12)." % ", ".join(frozen.mapped("display_label"))
                )
            if {"state", "version", "effective_from", "activated_by_id", "activated_at"} & set(
                vals
            ):
                raise UserError("A model is put in force through Put In Force.")
        return super().write(vals)

    def unlink(self):
        if self.filtered(lambda r: r.state != "draft"):
            raise UserError("A model that was in force is kept: closed campaigns name it.")
        return super().unlink()

    def action_activate(self):
        self.ensure_one()
        if self.state != "draft":
            raise UserError("Only a draft model is put in force.")
        current = self.search([("state", "=", "active"), ("id", "!=", self.id)])
        current._guarded().write({"state": "superseded"})
        self._guarded().write(
            {
                "state": "active",
                "effective_from": fields.Date.context_today(self),
                "activated_by_id": self.env.user.id,
                "activated_at": fields.Datetime.now(),
            }
        )
        return True


EXPERIMENT_VARIABLES = [
    ("content", "Content / creative"),
    ("offer", "Offer"),
    ("channel", "Channel"),
    ("timing", "Send timing"),
]


class FixCampaignExperimentLifecycle(models.Model):
    """FR-MKT-031: an experiment is started and concluded, with a winner."""

    _name = "fix.campaign.experiment"
    _inherit = ["fix.campaign.experiment", "fix.guarded.mixin"]

    variable = fields.Selection(EXPERIMENT_VARIABLES, string="What Is Tested", default="content")
    variant_a_label = fields.Char(string="Variant A")
    variant_b_label = fields.Char(string="Variant B")
    winner = fields.Selection(
        [("a", "Variant A"), ("b", "Variant B"), ("none", "No significant difference")],
        string="Winner",
        copy=False,
    )
    started_at = fields.Datetime(readonly=True, copy=False)
    concluded_at = fields.Datetime(readonly=True, copy=False)
    concluded_by_id = fields.Many2one("res.users", string="Concluded By", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "winner",
            "started_at",
            "concluded_at",
            "concluded_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= {
                "variable",
                "variant_a_pct",
                "variant_a_label",
                "variant_b_label",
                "metric",
                "campaign_id",
            }
        return locked

    @api.constrains("variant_a_pct")
    def _check_split(self):
        for rec in self:
            if not 1 <= (rec.variant_a_pct or 0) <= 99:
                raise ValidationError("Variant A takes between 1% and 99% of the audience.")

    def write(self, vals):
        design = {
            "variable",
            "variant_a_pct",
            "variant_a_label",
            "variant_b_label",
            "metric",
            "campaign_id",
        }
        if design & set(vals) and not self._fix_guard_open():
            for rec in self.filtered(lambda r: r.state != "draft"):
                if any(rec._fix_guard_differs(n, vals[n], rec[n]) for n in design & set(vals)):
                    raise UserError("The design of a started experiment is fixed: %s." % rec.name)
        return super().write(vals)

    def action_start(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Start a draft experiment.")
            if rec.campaign_id.state == "completed":
                raise UserError("%s has completed: nothing is left to test." % rec.campaign_id.name)
            rec._guarded().write({"state": "running", "started_at": fields.Datetime.now()})
        return True

    def action_conclude(self, winner=None, note=None):
        if winner not in ("a", "b", "none"):
            raise UserError("Name the winner: Variant A, Variant B, or no significant difference.")
        note = (note or "").strip()
        if not note:
            raise UserError("Record the finding: the figures the winner was judged on.")
        for rec in self:
            if rec.state != "running":
                raise UserError("Conclude a running experiment.")
            rec._guarded().write(
                {
                    "state": "concluded",
                    "winner": winner,
                    "result_note": note,
                    "concluded_at": fields.Datetime.now(),
                    "concluded_by_id": self.env.user.id,
                }
            )
        return True


class FixCampaignAdPlacement(models.Model):
    """FR-MKT-030: who advertises where, and when."""

    _inherit = "fix.campaign.ad"

    advertiser_partner_id = fields.Many2one(
        "res.partner",
        string="Advertiser",
        ondelete="restrict",
        help="The brand partner or seller paying for the placement; empty for "
        "the Company's own promotion.",
    )
    active_from = fields.Date(string="Runs From")
    active_to = fields.Date(string="Runs Until")

    @api.constrains("active_from", "active_to")
    def _check_window(self):
        for rec in self:
            if rec.active_from and rec.active_to and rec.active_to < rec.active_from:
                raise ValidationError("A placement ends after it starts.")
