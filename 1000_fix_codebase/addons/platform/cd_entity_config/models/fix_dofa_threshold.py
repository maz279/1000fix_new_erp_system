# fix.dofa.threshold — the DOFA ladders as governed CONFIGURATION.
#
# WHY. Two A03 ladders have an unresolved conflict between the specification's
# prose and its DOFA matrix (M10 loyalty points, M34 service-recovery
# concessions). In both, the code implements the REQ text and says so in a
# comment, so neither is a defect — but both are unresolved policy, and the
# re-audit recorded them as "decisions, not code".
#
# That framing hid an engineering blocker, which is the trap the area-audit
# playbook warns about: every "business, not engineering" item in A04 had one
# underneath. Here it was that the ladders are PYTHON LISTS. Ruling on them
# meant a code change, a review, a release and a deployment — so "the business
# must decide" really meant "the business must decide and then wait for an
# engineer". That is a bad place to leave a financial-authority policy.
#
# The ladders become data. A ruling is now a configuration act with an audit
# trail, applied by the people who own the authority, and the conflict is
# VISIBLE on the record rather than buried in a source comment: each basis is
# loadable, exactly one is in force, and the alternative stays beside it.
#
# The code keeps its Python list as the fallback, so behaviour is unchanged
# until somebody actually rules. Removing the fallback would have made this a
# behaviour change disguised as a refactor.
#
# A12 workflow audit (2026-11-04) X3 / M30-1, M30-2, M30-5, M30-14: the
# ruling step was forgeable. One Tier-4 user switched off every DOFA approval
# on a model alone (bands all at tier 0, authority "x"); `in_force` was a
# plain Boolean; two ladders could be in force at once; bands of an in-force
# ladder changed with no re-ruling; `ruled_by` could be retyped. Now:
#   * in_force / ruled_by / ruled_at / ruling_reference are SYSTEM-SET
#     (fix.guarded.mixin) — only action_put_in_force writes them;
#   * a ruling needs TWO DIFFERENT authority holders, one Tier 4 and one
#     Tier 5, and records both;
#   * a partial UNIQUE index allows at most one ladder in force per
#     (target_model, company_id) — the DB, not a search-then-unset race;
#   * bands are LOCKED once the ladder is in force (a change is a new
#     version, ruled again) — which also ends the stale stored-tier drift;
#   * the target must exist and inherit fix.dofa.mixin.
#
# A12 finish audit (2026-11-07) E1-E4, E23: that "two people" was one person
# and a typed name. The T4 named a T5 who never acted, then ruled alone. A ruling
# is now TWO ACTS BY TWO SESSIONS: a Tier 4 holder PROPOSES (reference, named
# Tier 5 countersigner), and that Tier 5 holder COUNTERSIGNS by restating the
# reference. Only the countersignature puts the ladder in force. The workflow
# engine depends on this module, so this is a dedicated step, not the M63 inbox.
# Superseding clears the sibling's reference and countersigner (history stays in
# chatter), so an old stamp can never be reused; a ruled ladder is never deleted
# or re-pointed; an amended ruling is a new version.
import logging
from xml.sax.saxutils import escape as xml_escape

from markupsafe import Markup
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_dofa import DOFA_TIERS, TIER_GROUP

_logger = logging.getLogger(__name__)

TIER4_GROUP = TIER_GROUP["tier_4"]
TIER5_GROUP = TIER_GROUP["tier_5"]

# Who may countersign (A12 finish E1). Default and conservative: a Tier 5 holder.
# Set to "tier_4" to let any Tier 4 holder countersign a Tier 5 holder's proposal;
# the pair must still contain a Tier 5 holder.
COUNTERSIGN_TIER_PARAM = "fix_dofa.countersign_min_tier"
RULED_LOCKED_FIELDS = {"target_model", "basis", "company_id"}


def _target_is_dofa_governed(env, target) -> bool:
    """True when `target` names a model that actually carries the DOFA mixin.

    A ladder for anything else governs nothing: it would sit "in force" in the
    Open DOFA Rulings report while the 18 real DOFA models kept their coded
    defaults (A12 M30-5). Checked with issubclass on the registry classes, so
    an inherited mixin anywhere in the MRO counts.
    """
    target = (target or "").strip()
    if not target or target not in env:
        return False
    return issubclass(type(env[target]), type(env["fix.dofa.mixin"]))


class FixDofaThreshold(models.Model):
    """One band of one named DOFA ladder."""

    _name = "fix.dofa.threshold"
    _description = "DOFA Threshold Band"
    _order = "ladder_id, upper_bound"

    ladder_id = fields.Many2one("fix.dofa.ladder", required=True, ondelete="cascade", index=True)
    upper_bound = fields.Float(
        required=True,
        help="Inclusive upper bound of this band. The highest band should be a "
        "very large number — it is the ceiling tier applied above every bound.",
    )
    tier = fields.Selection(DOFA_TIERS, required=True)
    note = fields.Char()

    _bound_unique = models.Constraint(
        "UNIQUE (ladder_id, upper_bound)",
        "Two bands of one ladder cannot share an upper bound — which applies "
        "would depend on evaluation order.",
    )

    @api.depends("ladder_id.name", "upper_bound", "tier")
    def _compute_display_name(self):
        """Without this a band renders as "fix.dofa.threshold,13".

        That is the label a Tier-4 approver reads on the ladder form's own
        band grid before ruling on it, so an opaque one is not cosmetic. The
        highest band carries a sentinel bound (the help calls it "a very large
        number"); printing it literally reads "<= 1,000,000,000" where the
        meaning is "everything above the band below". Resolve the ceiling
        against the ladder rather than hard-coding the sentinel, so a ladder
        loaded with a different sentinel still describes itself correctly.
        """
        labels = dict(DOFA_TIERS)
        for rec in self:
            bounds = rec.ladder_id.threshold_ids.mapped("upper_bound")
            is_ceiling = bool(bounds) and len(bounds) > 1 and rec.upper_bound >= max(bounds)
            bound = (
                "above every bound"
                if is_ceiling
                else "≤ %s" % format(rec.upper_bound or 0.0, ",.0f")
            )
            rec.display_name = "%s · %s · %s" % (
                rec.ladder_id.name or "—",
                bound,
                labels.get(rec.tier, rec.tier or "—"),
            )

    # ---- band lock (A12 M30-2 / M30-14) ----------------------------------
    # The bands of a ladder in force ARE the ruling: a second Tier-4 used to
    # lower the in-force band with no re-ruling, and the stored tier on
    # existing records went stale with it. Locked bands make both impossible:
    # a change is a new ladder (a new version), ruled again by two people.
    # A12 finish E1: a PROPOSED ladder is locked too, or the bands could move
    # between the proposal and the countersignature. A superseded ladder is
    # history: re-ruling it re-rules the bands it was ruled with.
    def _assert_bands_editable(self, extra_ladder_ids=()):
        Ladder = self.env["fix.dofa.ladder"]
        ladders = self.mapped("ladder_id") | Ladder.browse([int(i) for i in extra_ladder_ids if i])
        locked = ladders.filtered(lambda lad: lad.ruling_state != "draft")
        if locked and not self.env.su:
            raise UserError(
                "The bands of a proposed or ruled DOFA ladder are the ruling itself "
                "(%s). They cannot be edited; create a NEW ladder for %s with "
                "the amended bands and rule that instead."
                % (" ,".join(locked.mapped("name")), " ,".join(locked.mapped("target_model")))
            )

    @api.model_create_multi
    def create(self, vals_list):
        self._assert_bands_editable(v.get("ladder_id") for v in vals_list)
        return super().create(vals_list)

    def _write_changes_nothing(self, vals):
        # The ladder form posts every band row on save. An unchanged echo must pass,
        # or a superseded ladder could never be given a new countersigner.
        for rec in self:
            for name, value in vals.items():
                current = rec[name]
                current = current.id if name == "ladder_id" else current
                if rec._fields[name].type == "float":
                    if abs(float(value or 0.0) - float(current or 0.0)) > 1e-6:
                        return False
                elif (current or False) != (value or False):
                    return False
        return True

    def write(self, vals):
        if self._write_changes_nothing(vals):
            return True
        # A band moved to another ladder may not leave (or enter) a ruling.
        self._assert_bands_editable([vals.get("ladder_id")] if "ladder_id" in vals else ())
        return super().write(vals)

    def unlink(self):
        self._assert_bands_editable()
        return super().unlink()


class FixDofaLadder(models.Model):
    """A named, versioned threshold ladder for one model's authority field.

    Several bases may exist for the same target (the REQ text and the DOFA
    matrix, say). Exactly one may be in force, which is what makes this a
    ruling rather than an opinion.
    """

    _name = "fix.dofa.ladder"
    _description = "DOFA Threshold Ladder"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "target_model, basis"

    name = fields.Char(required=True)
    target_model = fields.Char(
        required=True,
        index=True,
        help="The model whose authority this ladder governs, e.g. "
        "fix.loyalty.ledger or fix.complaint. It must carry fix.dofa.mixin — "
        "a ladder for anything else governs nothing.",
    )
    basis = fields.Selection(
        [
            ("req_text", "Specification prose (REQ text)"),
            ("dofa_matrix", "DOFA authority matrix"),
            ("ruling", "Authoritative ruling (supersedes both)"),
        ],
        required=True,
        help="Which source this ladder transcribes. Recording it is the point: "
        "the conflict between the prose and the matrix is a fact about the "
        "specification, and it should be visible here rather than buried in a "
        "source comment.",
    )
    in_force = fields.Boolean(
        default=False,
        tracking=True,
        help="Exactly one ladder per target model may be in force. Switching "
        "which one is the RULING, and it is tracked on this record. "
        "System-set: only action_put_in_force may change it.",
    )
    matches_implementation = fields.Boolean(
        string="Matches Current Code",
        compute="_compute_matches_implementation",
        help="True when this ladder's bands equal the target model's own "
        "coded default. A statement of FACT about the code, not a ruling: "
        "with nothing in force the coded default applies, so the ladder "
        "marked here is how the estate behaves today. It tells a "
        "decision-maker which option is 'keep what we do' and which is "
        "'change the bands'. COMPUTED, never stored, so it cannot drift "
        "from the code it claims to describe.",
    )
    ruling_state = fields.Selection(
        [
            ("draft", "Draft"),
            ("proposed", "Awaiting Countersignature"),
            ("in_force", "In Force"),
            ("superseded", "Superseded"),
        ],
        string="Ruling Status",
        compute="_compute_ruling_state",
        store=True,
        index=True,
        help="Computed from the stamps, so it cannot disagree with them.",
    )
    version = fields.Integer(
        default=1,
        required=True,
        readonly=True,
        copy=False,
        help="An amended ruling is a new version of the same basis. Numbered on create.",
    )
    ruled_by = fields.Many2one("res.users", readonly=True, string="Ruled By", copy=False)
    proposed_by = fields.Many2one("res.users", readonly=True, string="Proposed By", copy=False)
    proposed_at = fields.Datetime(readonly=True, string="Proposed At", copy=False)
    proposed_reference = fields.Char(
        string="Proposed Authority",
        readonly=True,
        copy=False,
        help="The minute or memo the proposer cited. The countersigner restates it.",
    )
    countersigned_by = fields.Many2one(
        "res.users",
        string="Countersigned By",
        copy=False,
        tracking=True,
        help="The Tier 5 holder who must countersign: a different, active "
        "person from the proposer. Naming them does not count as their act: "
        "'Countersigned At' is stamped only when they countersign themselves.",
    )
    countersigned_at = fields.Datetime(string="Countersigned At", readonly=True, copy=False)
    countersigner_choice = fields.Selection(
        selection="_countersigner_selection",
        string="Countersigning Authority",
        compute="_compute_countersigner_choice",
        inverse="_inverse_countersigner_choice",
        help="Active Tier 5 holders only (the workspace form's picker).",
    )
    ruled_at = fields.Datetime(readonly=True, copy=False)
    ruling_reference = fields.Char(
        copy=False,
        help="The minute, memo or approval that authorises this ladder. A "
        "financial-authority change with no stated authority is not a ruling.",
    )
    superseded_at = fields.Datetime(readonly=True, string="Superseded At", copy=False)
    superseded_by_id = fields.Many2one(
        "fix.dofa.ladder", readonly=True, string="Superseded By", copy=False, ondelete="set null"
    )
    threshold_ids = fields.One2many("fix.dofa.threshold", "ladder_id", string="Bands", copy=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )

    # A12 finish E23: the unique key used to stop at the basis, so a model could
    # have at most three ladders ever and "create a NEW ladder" was impossible.
    _name_unique = models.Constraint(
        "UNIQUE (target_model, basis, company_id, version)",
        "One ladder per target model, basis, company and version.",
    )

    # A12 M30-2 / d06: two ladders were left in force for one model and the
    # UNRULED one won on basis order. A partial unique index makes "exactly
    # one in force" a database fact instead of a search-then-unset race.
    _in_force_unique = models.UniqueIndex(
        "(target_model, company_id) WHERE in_force",
        "Only one DOFA ladder per target model and company may be in force — "
        "which one applies is a ruling, not a race.",
    )

    def _fix_guarded_fields(self) -> set:
        # The ruling stamp is evidence. Only action_put_in_force — with its
        # two-authority check — may write it (A12 M30-2 / d05, d08).
        return super()._fix_guarded_fields() | {
            "in_force",
            "ruled_by",
            "ruled_at",
            "ruling_reference",
            "proposed_by",
            "proposed_at",
            "proposed_reference",
            "countersigned_at",
            "superseded_at",
            "superseded_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        # Once proposed or ruled, what was ruled on is frozen. A superseded
        # ladder may name a new countersigner: re-ruling it needs a fresh one.
        locked = super()._fix_form_locked_fields()
        state = self[:1].ruling_state if self else "draft"
        if state != "draft":
            locked = locked | RULED_LOCKED_FIELDS
        if state in ("proposed", "in_force"):
            locked = locked | {"countersigned_by", "countersigner_choice"}
        return locked

    @api.depends("in_force", "proposed_by", "superseded_at")
    def _compute_ruling_state(self):
        for rec in self:
            if rec.in_force:
                rec.ruling_state = "in_force"
            elif rec.proposed_by:
                rec.ruling_state = "proposed"
            elif rec.superseded_at:
                rec.ruling_state = "superseded"
            else:
                rec.ruling_state = "draft"

    @api.model
    def _countersign_group(self) -> str:
        param = self.env["ir.config_parameter"].sudo().get_param(COUNTERSIGN_TIER_PARAM, "tier_5")
        return TIER4_GROUP if param == "tier_4" else TIER5_GROUP

    def _countersigner_selection(self):
        # /p03/model/form lists every user for a many2one, so the picker is a
        # dynamic selection of the people who can actually countersign.
        group = self.env.ref(self._countersign_group(), raise_if_not_found=False)
        if not group:
            return []
        holders = group.sudo().all_user_ids.filtered(lambda u: u.active and not u.share)
        return [(str(u.id), u.name) for u in holders.sorted("name")]

    @api.depends("countersigned_by")
    def _compute_countersigner_choice(self):
        allowed = {key for key, _label in self._countersigner_selection()}
        for rec in self:
            key = str(rec.countersigned_by.id) if rec.countersigned_by else False
            rec.countersigner_choice = key if key in allowed else False

    def _inverse_countersigner_choice(self):
        for rec in self:
            rec.countersigned_by = (
                int(rec.countersigner_choice) if rec.countersigner_choice else False
            )

    @api.depends("target_model", "threshold_ids.upper_bound", "threshold_ids.tier")
    def _compute_matches_implementation(self):
        """Compare this ladder's bands with the target model's coded default.

        Computed, not stored, and deliberately so: a flag seeded in data
        would be an assertion that goes stale the moment somebody edits a
        Python threshold list, and this field's entire worth is being true of
        the code right now.

        Reads the model's OWN _dofa_thresholds(). The ladder override sits on
        _dofa_tier_for_amount, so this cannot become self-referential.
        """
        for rec in self:
            rec.matches_implementation = False
            target = (rec.target_model or "").strip()
            if not target or target not in self.env:
                continue
            coded = getattr(self.env[target], "_dofa_thresholds", None)
            if coded is None:
                continue
            try:
                default = list(coded())
            except Exception:
                # matches_implementation stays False (honest), but say why.
                _logger.warning(
                    "DOFA ladder %s: %s._dofa_thresholds() raised; cannot compare",
                    rec.id,
                    target,
                    exc_info=True,
                )
                continue
            bands = [
                (band.upper_bound, band.tier) for band in rec.threshold_ids.sorted("upper_bound")
            ]
            if not bands or not default:
                continue

            def norm(pairs):
                # The coded lists end in float("inf"); a stored band must hold
                # a real number, so any very large bound is the same ceiling.
                return [
                    ("inf" if b == float("inf") or b >= 1e9 else round(float(b), 2), t)
                    for b, t in pairs
                ]

            rec.matches_implementation = norm(bands) == norm(default)

    @api.constrains("threshold_ids")
    def _check_bands_are_ascending_and_present(self):
        for rec in self:
            if not rec.threshold_ids:
                continue
            bounds = rec.threshold_ids.sorted("upper_bound").mapped("upper_bound")
            if len(set(bounds)) != len(bounds):
                raise ValidationError("Ladder '%s' has duplicate bounds." % rec.name)

    @api.constrains("target_model")
    def _check_target_model(self):
        """A ladder may only govern a model that actually reads it (M30-5).

        `fix.access.request` and a non-existent model were both accepted and
        shown "in force" while governing nothing. Models not in THIS registry
        are skipped here: the ladder data loads with the T0 config module, before
        the domain models that depend on it exist (the same partial-registry reason
        _compute_matches_implementation skips). Constraints run as superuser, so a
        person's ghost target is refused in create and write (A12 finish E23). The
        ruling gate refuses an unknown target absolutely — nothing that is not
        real can ever be ruled.
        """
        for rec in self:
            target = (rec.target_model or "").strip()
            if not target or target not in self.env:
                continue
            if not _target_is_dofa_governed(self.env, target):
                raise ValidationError(
                    "'%s' does not carry fix.dofa.mixin, so a DOFA ladder "
                    "cannot govern it. Ladders rule the models that actually "
                    "read them." % target
                )

    def _refuse_ghost_target(self, target):
        if not self.env.su and (target or "").strip() not in self.env:
            raise ValidationError(
                "No model named '%s' exists, so a DOFA ladder cannot govern it." % target
            )

    @api.model_create_multi
    def create(self, vals_list):
        # An amendment is a new version of its basis (E23); the number is
        # the server's, never typed.
        for vals in vals_list:
            self._refuse_ghost_target(vals.get("target_model"))
            if vals.get("target_model") and vals.get("basis"):
                company_id = vals.get("company_id") or self.env.company.id
                latest = self.sudo().search(
                    [
                        ("target_model", "=", vals["target_model"]),
                        ("basis", "=", vals["basis"]),
                        ("company_id", "=", company_id),
                    ],
                    order="version desc",
                    limit=1,
                )
                if latest:
                    vals["version"] = latest.version + 1
                else:
                    vals.pop("version", None)
        return super().create(vals_list)

    def write(self, vals):
        # What was ruled on is evidence. The form lock is not enough: an ORM
        # write re-pointed an in-force ruling at another model (A12 finish E3).
        if "target_model" in vals:
            self._refuse_ghost_target(vals["target_model"])
        if not self._fix_guard_open():
            if "version" in vals and any(r.version != vals["version"] for r in self):
                self._fix_guard_refuse(["version"])
            ruled = self.filtered(lambda r: r.ruling_state != "draft")
            for name in RULED_LOCKED_FIELDS & set(vals):
                if any(r._fix_guard_differs(name, vals[name], r[name]) for r in ruled):
                    raise UserError(
                        "%s of a proposed or ruled DOFA ladder cannot change: it "
                        "would move the ruling without a new one. Create a new "
                        "ladder and rule that." % self._fields[name].string
                    )
            if "countersigned_by" in vals and any(
                r._fix_guard_differs(
                    "countersigned_by", vals["countersigned_by"], r.countersigned_by
                )
                for r in ruled.filtered(lambda r: r.ruling_state in ("proposed", "in_force"))
            ):
                self._fix_guard_refuse(["countersigned_by"])
        return super().write(vals)

    def unlink(self):
        # A ruling on record is superseded, never erased: deleting a ladder
        # that was ever proposed or ruled would destroy its chatter, the only
        # record of who changed the authority (A12 finish E23). The bands
        # cascade with a draft ladder at the DB level, which is fine — a draft
        # governs nothing.
        locked = self.filtered(lambda r: r.ruling_state != "draft")
        if locked and not self.env.su:
            raise UserError(
                "A ladder proposed or ruled is on record for %s. It cannot be "
                "deleted; rule a new ladder to supersede it."
                % ", ".join(locked.mapped("target_model"))
            )
        return super().unlink()

    def _ruling_countersigner(self, countersigned_by=None):
        """Resolve the named countersigner: an explicit argument (the workspace
        action's kwargs), else the record's countersigned_by field."""
        counter = countersigned_by or self.countersigned_by
        if counter:
            return self.env["res.users"].browse(int(counter)).exists()
        return self.env["res.users"]

    def _ruling_preconditions(self, reference):
        """What any ruling needs, whoever makes it."""
        self.ensure_one()
        if self.in_force:
            raise UserError(
                "'%s' is already in force. A ruling is not re-run: rule a new "
                "version to change it." % self.name
            )
        if not (reference or "").strip():
            raise UserError(
                "Putting a DOFA ladder in force changes who may approve "
                "what, so it requires a ruling reference — the minute, "
                "memo or approval that authorises it."
            )
        if not self.threshold_ids:
            raise UserError(
                "Ladder '%s' defines no bands, so it would grant no authority at all." % self.name
            )
        if not _target_is_dofa_governed(self.env, self.target_model):
            raise UserError(
                "'%s' is not a model governed by DOFA (it does not exist "
                "or does not carry fix.dofa.mixin), so this ladder can "
                "never apply. Ladders rule the models that read them." % (self.target_model or "—")
            )

    @staticmethod
    def _check_reference_cites_something(reference):
        """'x' is not an authorising minute (A12 finish, 'DOFA cites its authority')."""
        text = (reference or "").strip()
        if len(text) < 4 or not any(ch.isdigit() for ch in text):
            raise UserError(
                "'%s' does not cite an authority. Give the number of the minute, "
                "memo or approval, for example 'Board minute 2026-11'." % text
            )

    def _display_target(self):
        """The human model label, not the technical name in the subject line."""
        self.ensure_one()
        model = self.env["ir.model"].sudo().search([("model", "=", self.target_model)], limit=1)
        return model.name if model else (self.target_model or "DOFA")

    def _ruling_bands_html(self):
        """The bands the ruling actually sets, as an email-safe table."""
        self.ensure_one()
        if not self.threshold_ids:
            return '<p style="margin:12px 0">No bands are defined on this ladder.</p>'
        bounds = self.threshold_ids.mapped("upper_bound")
        labels = dict(DOFA_TIERS)
        rows = []
        for band in self.threshold_ids.sorted(lambda b: b.upper_bound):
            ceiling = len(bounds) > 1 and band.upper_bound >= max(bounds)
            bound = (
                "Above every bound"
                if ceiling
                else "Up to %s" % format(band.upper_bound or 0.0, ",.0f")
            )
            rows.append(
                "<tr>"
                '<td style="padding:6px 10px;border:1px solid #d8dde6">%s</td>'
                '<td style="padding:6px 10px;border:1px solid #d8dde6">%s</td>'
                '<td style="padding:6px 10px;border:1px solid #d8dde6">%s</td>'
                "</tr>"
                % (
                    bound,
                    xml_escape(labels.get(band.tier, band.tier or "—")),
                    xml_escape(band.note or ""),
                )
            )
        return (
            '<table style="border-collapse:collapse;width:100%%;font-size:13px;margin:12px 0">'
            '<thead><tr style="background:#f3f5f8">'
            '<th style="padding:6px 10px;border:1px solid #d8dde6;text-align:left">Amount (BDT)</th>'
            '<th style="padding:6px 10px;border:1px solid #d8dde6;text-align:left">Authority</th>'
            '<th style="padding:6px 10px;border:1px solid #d8dde6;text-align:left">Note</th>'
            "</tr></thead><tbody>%s</tbody></table>" % "".join(rows)
        )

    def _post_ruling_email(self, subject, intro_html, partner_ids=None):
        """Post a branded, actionable ruling notification.

        The stock message_post body rendered as one sentence with the technical
        model name in the subject, no bands and no call to action — the Mailpit
        inbox showed 78 of those for one countersigner. This keeps the chatter
        post (the record of the act) and gives the email the facts the
        countersigner needs: what is ruled, on what authority, against which
        bands, and where to act.
        """
        self.ensure_one()
        base = (self.env["ir.config_parameter"].sudo().get_param("web.base.url") or "").rstrip("/")
        link = "%s/mail/view?model=fix.dofa.ladder&res_id=%s" % (base, self.id)
        body = (
            '<div style="font-family:Arial,Helvetica,sans-serif;font-size:14px;'
            'color:#1f2933;line-height:1.5;max-width:720px">'
            '<p style="margin:0 0 4px;font-size:12px;letter-spacing:.08em;'
            'text-transform:uppercase;color:#5b6776">1000 FiX · DOFA authority</p>'
            '<h2 style="margin:0 0 12px;font-size:19px">%s</h2>'
            "%s"
            "%s"
            '<p style="margin:16px 0"><a href="%s" '
            'style="display:inline-block;padding:10px 18px;background:#1f4e79;'
            'color:#ffffff;text-decoration:none;border-radius:4px;font-weight:600">'
            "Open the ladder</a></p>"
            '<p style="margin:16px 0 0;font-size:12px;color:#5b6776">'
            "Automated internal notification from the 1000 FiX ERP. The ladder record "
            "holds the full band table and the ruling trail.</p>"
            "</div>"
            % (
                xml_escape(self.name or "DOFA ladder"),
                intro_html,
                self._ruling_bands_html(),
                xml_escape(link),
            )
        )
        company = self.env.company
        sender = "%s <%s>" % (company.name, company.email) if company.email else None
        self.message_post(
            # Safe: this is a static HTML template; every interpolated value
            # (name, authority, model label, link, band text) is xml_escape'd.
            body=Markup(body),
            subject=subject,
            email_from=sender,
            partner_ids=partner_ids or [],
            subtype_xmlid="mail.mt_comment",
        )

    def action_propose_ruling(self, reference="", countersigned_by=None):
        """Step 1 of a ruling: a Tier 4 holder proposes it and names the Tier 5
        holder who must countersign. Nothing changes until they do."""
        for rec in self:
            rec._ruling_preconditions(reference)
            if rec.ruling_state == "proposed":
                raise UserError(
                    "'%s' is already awaiting %s's countersignature. Withdraw "
                    "the proposal to change it." % (rec.name, rec.countersigned_by.name)
                )
            acting = self.env.user
            if not self.env.su and not acting.has_group(TIER4_GROUP):
                raise UserError(
                    "A DOFA ruling is Tier 4 / Tier 5 authority. You do "
                    "not hold that approval authority."
                )
            counter = rec._ruling_countersigner(countersigned_by)
            if not counter:
                raise UserError(
                    "A DOFA ruling needs TWO authority holders: name the "
                    "countersigning Tier 5 user (a different person) in "
                    "'Countersigning Authority' before proposing it."
                )
            if counter == acting:
                raise UserError(
                    "A DOFA ruling needs two DIFFERENT people: the "
                    "countersigner must not be the user who proposes it."
                )
            if not counter.active:
                raise UserError(
                    "%s is archived, so they cannot countersign a ruling." % counter.name
                )
            if not counter.has_group(TIER4_GROUP):
                raise UserError(
                    "%s does not hold DOFA Tier 4 / Tier 5 authority, so "
                    "they cannot countersign a ruling." % counter.name
                )
            if not counter.has_group(rec._countersign_group()):
                raise UserError(
                    "%s does not hold Tier 5, and the countersigner of a DOFA "
                    "ruling must (ir.config_parameter %s)." % (counter.name, COUNTERSIGN_TIER_PARAM)
                )
            if not (acting.has_group(TIER5_GROUP) or counter.has_group(TIER5_GROUP)):
                raise UserError(
                    "A DOFA ruling needs one Tier 4 holder AND one Tier 5 "
                    "holder — two different people. Neither of you holds Tier 5."
                )
            if not self.env.su:
                rec._check_reference_cites_something(reference)
            rec._guarded().write(
                {
                    "proposed_by": acting.id,
                    "proposed_at": fields.Datetime.now(),
                    "proposed_reference": reference.strip(),
                    "countersigned_by": counter.id,
                    "countersigned_at": False,
                }
            )
            rec._post_ruling_email(
                subject="Countersign required — %s DOFA ruling" % rec._display_target(),
                intro_html=(
                    '<p style="margin:0 0 10px">%s proposed a ruling on the '
                    "<strong>%s</strong> basis (version %s) for <strong>%s</strong>.</p>"
                    '<p style="margin:0 0 10px">Authority cited: <strong>%s</strong></p>'
                    '<p style="margin:0 0 10px;padding:10px 12px;background:#fff4e5;'
                    'border-left:4px solid #b26a00"><strong>This is not in force until '
                    "%s countersigns.</strong></p>"
                    % (
                        xml_escape(acting.name or "A Tier 4 holder"),
                        xml_escape(dict(rec._fields["basis"].selection)[rec.basis]),
                        rec.version,
                        xml_escape(rec._display_target()),
                        xml_escape(reference.strip()),
                        xml_escape(counter.name or "the named countersigner"),
                    )
                ),
                partner_ids=counter.partner_id.ids,
            )
        return True

    def action_countersign(self, reference=""):
        """Step 2 of a ruling: the named Tier 5 holder acts, in their own
        session, and restates the authority. THIS puts the ladder in force."""
        for rec in self:
            if rec.ruling_state != "proposed":
                raise UserError(
                    "'%s' is not awaiting a countersignature (it is %s)."
                    % (rec.name, dict(rec._fields["ruling_state"].selection)[rec.ruling_state])
                )
            acting = self.env.user
            if not self.env.su:
                if acting != rec.countersigned_by:
                    raise UserError(
                        "Only %s, the named countersigner, can countersign this ruling."
                        % rec.countersigned_by.name
                    )
                if acting == rec.proposed_by:
                    raise UserError(
                        "A DOFA ruling needs two DIFFERENT people: you proposed this one."
                    )
                if not acting.has_group(rec._countersign_group()):
                    raise UserError(
                        "Countersigning a DOFA ruling needs Tier 5 authority, which "
                        "%s no longer holds." % acting.name
                    )
                proposer = rec.proposed_by
                if not (proposer.active and proposer.has_group(TIER4_GROUP)):
                    raise UserError(
                        "%s no longer holds Tier 4 authority, so their proposal "
                        "cannot be ruled. Withdraw it." % proposer.name
                    )
            typed = (reference or "").strip()
            if typed.casefold() != (rec.proposed_reference or "").strip().casefold():
                raise UserError(
                    "Restate the authority you are countersigning: it must read "
                    "exactly '%s'." % rec.proposed_reference
                )
            # Through action_put_in_force so every override of the ruling
            # (cd_grc's DoA register resync) runs. The token is an object:
            # JSON-RPC cannot supply it, so only this path reaches the ruling.
            rec._guarded().action_put_in_force(
                reference=rec.proposed_reference, countersigned_by=acting.id
            )
        return True

    def action_withdraw_ruling(self, reason=""):
        """The proposer withdraws, or the named countersigner declines."""
        for rec in self:
            if rec.ruling_state != "proposed":
                raise UserError("Only a proposed ruling can be withdrawn.")
            acting = self.env.user
            if not self.env.su and acting not in (rec.proposed_by | rec.countersigned_by):
                raise UserError(
                    "Only the proposer or the named countersigner can withdraw this ruling."
                )
            if not (reason or "").strip():
                raise UserError("Say why this proposal is being withdrawn.")
            rec.message_post(
                body="Proposal on authority '%s' withdrawn by %s: %s"
                % (rec.proposed_reference, acting.name, reason.strip())
            )
            rec._guarded().write(
                {
                    "proposed_by": False,
                    "proposed_at": False,
                    "proposed_reference": False,
                    "countersigned_by": False,
                }
            )
        return True

    def action_put_in_force(self, reference="", countersigned_by=None):
        """Make this ladder the one in force. THIS is the ruling.

        A12 finish E1 (M30-1): one Tier 4 session named a Tier 5 user who never
        acted, and ruled alone. For a person this method is now only the
        PROPOSAL: the countersigner's action_countersign is what reaches the
        ruling below, through an in-process token that JSON-RPC cannot supply.

        The superuser rules directly, as with every guard in this codebase
        (fix.guarded.mixin._fix_guard_open): the workspace and the ORM never
        rule as su, and whoever holds the database can rewrite the table anyway.
        """
        if not self._fix_guard_open():
            return self.action_propose_ruling(
                reference=reference, countersigned_by=countersigned_by
            )
        for rec in self:
            rec._ruling_preconditions(reference)
            proposer = rec.proposed_by
            counter = rec._ruling_countersigner(countersigned_by)
            # Retire the ruling sibling FIRST, then rule: the unique index on
            # (target_model, company_id) WHERE in_force is satisfied at every
            # statement, and a concurrent ruling loses to the database.
            siblings = self.sudo().search(
                [
                    ("target_model", "=", rec.target_model),
                    ("company_id", "=", rec.company_id.id),
                    ("in_force", "=", True),
                    ("id", "!=", rec.id),
                ]
            )
            for sibling in siblings:
                # E4: the reference and countersigner go, so a stale stamp can
                # never be re-used; chatter keeps what they were.
                sibling.message_post(
                    body="Superseded by '%s' (authority '%s'). This ruling had been made "
                    "by %s, countersigned by %s, on authority '%s'."
                    % (
                        rec.name,
                        reference.strip(),
                        sibling.ruled_by.name or "—",
                        sibling.countersigned_by.name or "—",
                        sibling.ruling_reference or "—",
                    )
                )
                sibling._guarded().write(
                    {
                        "in_force": False,
                        "ruling_reference": False,
                        "countersigned_by": False,
                        "countersigned_at": False,
                        "superseded_at": fields.Datetime.now(),
                        "superseded_by_id": rec.id,
                    }
                )
            # E2 (M30-2): flush NOW. The ORM defers writes and orders the batch
            # by id and dirty fields; when someone else last wrote the old ladder
            # it sent the new ladder's in_force=True first, and the partial
            # unique index raised UniqueViolation on the ordinary supersede.
            siblings.flush_recordset()
            rec._guarded().write(
                {
                    "in_force": True,
                    "ruled_by": (proposer or self.env.user).id,
                    "ruled_at": fields.Datetime.now(),
                    "ruling_reference": reference.strip(),
                    "countersigned_by": counter.id or False,
                    "countersigned_at": fields.Datetime.now() if counter else False,
                    "proposed_by": False,
                    "proposed_at": False,
                    "proposed_reference": False,
                    "superseded_at": False,
                    "superseded_by_id": False,
                }
            )
            rec._post_ruling_email(
                subject="DOFA ruling in force — %s" % rec._display_target(),
                intro_html=(
                    '<p style="margin:0 0 10px">The ladder is <strong>in force</strong> on the '
                    "%s basis for <strong>%s</strong>.</p>"
                    '<p style="margin:0 0 10px">Proposed by %s · countersigned by %s · '
                    "authority <strong>%s</strong>.</p>"
                    '<p style="margin:0 0 10px">Superseded: %s.</p>'
                    % (
                        xml_escape(dict(rec._fields["basis"].selection)[rec.basis]),
                        xml_escape(rec._display_target()),
                        xml_escape((proposer or self.env.user).name or "—"),
                        xml_escape(counter.name or "—"),
                        xml_escape(rec.ruling_reference or "—"),
                        xml_escape(", ".join(siblings.mapped("name")) or "none"),
                    )
                ),
            )
            rec._recompute_target_tiers()
        return True

    def _recompute_target_tiers(self):
        """A ruling must move the tier of records that already exist.

        dofa_tier_required depends only on the amount field, so without this
        a BDT 700 complaint raised before the ruling kept its old tier while
        an identical one raised after it got the new one (A03 audit). The
        gates now read the live tier anyway; this keeps the stored column —
        what lists, filters and dashboards show — telling the same story.
        """
        for rec in self:
            if rec.target_model not in self.env:
                continue
            target = self.env[rec.target_model]
            field = target._fields.get("dofa_tier_required")
            if not field:
                continue
            records = target.sudo().with_context(active_test=False).search([])
            self.env.add_to_compute(field, records)
            records.flush_recordset(["dofa_tier_required"])

    @api.model
    def thresholds_for(self, model_name, company=None):
        """The ladder in force for a model, as the mixin's list, or None.

        None means "nothing has been ruled", and the calling model keeps its
        own Python default. That is deliberate: making this table authoritative
        before anyone has populated it would silently change every approval
        threshold in the estate to nothing.
        """
        company_id = getattr(company, "id", company) or self.env.company.id
        ladder = self.sudo().search(
            [
                ("target_model", "=", model_name),
                ("in_force", "=", True),
                ("company_id", "in", [company_id, False]),
            ],
            limit=1,
        )
        if not ladder or not ladder.threshold_ids:
            return None
        bands = ladder.threshold_ids.sorted("upper_bound")
        return [(band.upper_bound, band.tier) for band in bands]

    @api.model
    def conflicts(self):
        """Every target model that has more than one basis on file.

        The reporting surface for the two open A03 rulings: it names the
        target, which basis is in force, and which alternatives exist, so the
        decision is visible to whoever has to take it.
        """
        rows = {}
        for ladder in self.sudo().search([]):
            bucket = rows.setdefault(
                ladder.target_model,
                {
                    "target_model": ladder.target_model,
                    "bases": [],
                    "in_force": None,
                    "implemented_basis": None,
                },
            )
            bucket["bases"].append(ladder.basis)
            if ladder.in_force:
                bucket["in_force"] = ladder.basis
            if ladder.matches_implementation:
                bucket["implemented_basis"] = ladder.basis
        return [
            dict(
                row,
                unresolved=row["in_force"] is None or len(row["bases"]) > 1,
                note=(
                    "No ruling has been taken. The model's own coded default "
                    "applies, which is the '%s' basis — so choosing it changes "
                    "nothing and choosing the other changes the bands."
                    % (row["implemented_basis"] or "unmarked")
                    if row["in_force"] is None
                    else "%d basis/bases on file, '%s' in force."
                    % (len(row["bases"]), row["in_force"])
                ),
            )
            for row in rows.values()
            if len(row["bases"]) > 1 or row["in_force"] is None
        ]


class FixDofaMixinConfigurable(models.AbstractModel):
    """Teach the DOFA mixin to consult the ladder table first."""

    _inherit = "fix.dofa.mixin"

    def _dofa_tier_for_amount(self, amount: float) -> str:
        """Derive the tier from the RULED ladder if one is in force.

        Hooked here, not on _dofa_thresholds(), and that distinction is the
        whole reason this works: eight concrete models override
        _dofa_thresholds() themselves, and a concrete method shadows an
        inherited one — so an override on the mixin's _dofa_thresholds never
        ran for any of them. It looked right and did nothing, and the test
        that asserts a ruling actually moves a derived tier is what found it.

        _dofa_tier_for_amount() is overridden by nobody, so it is the single
        chokepoint every tier derivation passes through.

        The fallback matters: until somebody actually rules, behaviour is
        exactly what it was. A refactor that changed approval thresholds as a
        side effect would be far worse than the hard-coded lists it replaces.
        """
        if "fix.dofa.ladder" in self.env:
            company = self.env.company
            if self:
                company = getattr(self[:1], "company_id", False) or company
            try:
                ruled = self.env["fix.dofa.ladder"].thresholds_for(self._name, company=company)
            except Exception:
                # dofa_tier_required is a STORED compute, so it runs during
                # module installation -- including the very upgrade that
                # creates this table. The model is in the registry before its
                # relation exists, so a lookup here can hit a missing table.
                # Falling back to the model default is the safe answer: it is
                # what the estate did before the ladder existed.
                ruled = None
            if ruled:
                for bound, tier in ruled:
                    if amount <= bound:
                        return tier
                return ruled[-1][1]
        return super()._dofa_tier_for_amount(amount)
