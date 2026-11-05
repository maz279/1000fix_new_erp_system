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
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_dofa import DOFA_TIERS, TIER_GROUP

_logger = logging.getLogger(__name__)

TIER4_GROUP = TIER_GROUP["tier_4"]
TIER5_GROUP = TIER_GROUP["tier_5"]


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
    def _assert_bands_editable(self, extra_ladder_ids=()):
        Ladder = self.env["fix.dofa.ladder"]
        ladders = self.mapped("ladder_id") | Ladder.browse([int(i) for i in extra_ladder_ids if i])
        locked = ladders.filtered(lambda lad: lad.in_force)
        if locked and not self.env.su:
            raise UserError(
                "The bands of a DOFA ladder in force are the ruling itself "
                "(%s). They cannot be edited; create a NEW ladder for %s with "
                "the amended bands and rule that instead."
                % (" ,".join(locked.mapped("name")), " ,".join(locked.mapped("target_model")))
            )

    @api.model_create_multi
    def create(self, vals_list):
        self._assert_bands_editable(v.get("ladder_id") for v in vals_list)
        return super().create(vals_list)

    def write(self, vals):
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
    ruled_by = fields.Many2one("res.users", readonly=True, string="Ruled By")
    countersigned_by = fields.Many2one(
        "res.users",
        string="Countersigned By",
        copy=False,
        tracking=True,
        help="The SECOND authority holder who countersigned the ruling: the "
        "other of a Tier 4 / Tier 5 pair, a different person from whoever "
        "rules. Choose them here, then run 'Put In Force' with the ruling "
        "reference.",
    )
    ruled_at = fields.Datetime(readonly=True)
    ruling_reference = fields.Char(
        help="The minute, memo or approval that authorises this ladder. A "
        "financial-authority change with no stated authority is not a ruling."
    )
    threshold_ids = fields.One2many("fix.dofa.threshold", "ladder_id", string="Bands", copy=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )

    _name_unique = models.Constraint(
        "UNIQUE (target_model, basis, company_id)",
        "One ladder per target model, basis and company.",
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
        }

    def _fix_form_locked_fields(self) -> set:
        # A ladder in force is the ruling: its target and basis are frozen too.
        locked = super()._fix_form_locked_fields()
        if self and self[:1].in_force:
            return locked | {"target_model", "basis", "countersigned_by"}
        return locked

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
        are skipped rather than refused: the ladder data loads with the T0
        config module, before the domain models that depend on it exist (the
        same partial-registry reason _compute_matches_implementation skips).
        The ruling gate (action_put_in_force) refuses an unknown target
        absolutely — nothing that is not real can ever be ruled.
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

    def write(self, vals):
        # countersigned_by is chosen while the ladder is a DRAFT; once in
        # force it is evidence of who the second signatory was, and stays.
        if (
            "countersigned_by" in vals
            and not self._fix_guard_open()
            and any(rec.in_force for rec in self)
        ):
            self._fix_guard_refuse(["countersigned_by"])
        return super().write(vals)

    def unlink(self):
        # A ruling on record is superseded, never erased: deleting the
        # in-force ladder would silently return the model to its coded
        # default with no trace of who changed the authority. (The bands
        # cascade with a draft ladder at the DB level, which is fine — a
        # draft governs nothing.)
        locked = self.filtered("in_force")
        if locked and not self.env.su:
            raise UserError(
                "A ladder in force is the ruling on record for %s. It cannot "
                "be deleted; rule a new ladder to supersede it."
                % ", ".join(locked.mapped("target_model"))
            )
        return super().unlink()

    def _ruling_countersigner(self, countersigned_by=None):
        """Resolve the second signatory: an explicit argument (the workspace
        action's kwargs), else the record's countersigned_by field."""
        counter = countersigned_by or self.countersigned_by
        if counter:
            return self.env["res.users"].browse(int(counter)).exists()
        return self.env["res.users"]

    def action_put_in_force(self, reference="", countersigned_by=None):
        """Make this ladder the one in force. THIS is the ruling.

        Deliberately requires a reference: a change to who may approve what,
        with nothing recorded about who authorised the change, is not an
        improvement on a hard-coded list.

        A12 X3 / M30-1: it also requires TWO DIFFERENT authority holders —
        one Tier 4 and one Tier 5. One unsupervised Tier-4 user could switch
        off every DOFA approval on a model alone; now the acting user holds
        Tier 4 (Tier 5 implies it), a DIFFERENT user countersigns, and at
        least one of the pair holds Tier 5. Both are recorded on the record.

        The superuser is exempt from the two-person check, as it is by every
        guard in this codebase (fix.guardedMixin._fix_guard_open): the
        workspace and the ORM never rule as su, and whoever holds the
        database can rewrite the table directly anyway.
        """
        for rec in self:
            if not (reference or rec.ruling_reference or "").strip():
                raise UserError(
                    "Putting a DOFA ladder in force changes who may approve "
                    "what, so it requires a ruling reference — the minute, "
                    "memo or approval that authorises it."
                )
            if not rec.threshold_ids:
                raise UserError(
                    "Ladder '%s' defines no bands, so it would grant no "
                    "authority at all." % rec.name
                )
            if not _target_is_dofa_governed(self.env, rec.target_model):
                raise UserError(
                    "'%s' is not a model governed by DOFA (it does not exist "
                    "or does not carry fix.dofa.mixin), so this ladder can "
                    "never apply. Ladders rule the models that read them."
                    % (rec.target_model or "—")
                )
            counter = rec._ruling_countersigner(countersigned_by)
            if not self.env.su:
                acting = self.env.user
                if not acting.has_group(TIER4_GROUP):
                    raise UserError(
                        "A DOFA ruling is Tier 4 / Tier 5 authority. You do "
                        "not hold that approval authority."
                    )
                if not counter:
                    raise UserError(
                        "A DOFA ruling needs TWO authority holders: name the "
                        "countersigning Tier 4 / Tier 5 user (a different "
                        "person) in 'Countersigned By' before putting the "
                        "ladder in force."
                    )
                if counter == acting:
                    raise UserError(
                        "A DOFA ruling needs two DIFFERENT people: the "
                        "countersigner must not be the user who rules."
                    )
                if not counter.has_group(TIER4_GROUP):
                    raise UserError(
                        "%s does not hold DOFA Tier 4 / Tier 5 authority, so "
                        "they cannot countersign a ruling." % counter.name
                    )
                if not (acting.has_group(TIER5_GROUP) or counter.has_group(TIER5_GROUP)):
                    raise UserError(
                        "A DOFA ruling needs one Tier 4 holder AND one Tier 5 "
                        "holder — two different people. Neither of you holds "
                        "Tier 5."
                    )
            # Retire the ruling sibling FIRST, then rule: the unique index on
            # (target_model, company_id) WHERE in_force is satisfied at every
            # statement, and a concurrent ruling loses to the database rather
            # than to whichever search ran last.
            siblings = self.sudo().search(
                [
                    ("target_model", "=", rec.target_model),
                    ("company_id", "=", rec.company_id.id),
                    ("in_force", "=", True),
                    ("id", "!=", rec.id),
                ]
            )
            siblings._guarded().write({"in_force": False})
            rec._guarded().write(
                {
                    "in_force": True,
                    "ruled_by": self.env.user.id,
                    "ruled_at": fields.Datetime.now(),
                    "ruling_reference": reference or rec.ruling_reference,
                    "countersigned_by": counter.id or False,
                }
            )
            rec.message_post(
                body="DOFA ladder for %s put in force on the %s basis by %s, "
                "countersigned by %s. Authority: %s. Superseded: %s."
                % (
                    rec.target_model,
                    dict(rec._fields["basis"].selection)[rec.basis],
                    self.env.user.name,
                    counter.name or "—",
                    rec.ruling_reference,
                    ", ".join(siblings.mapped("name")) or "none",
                )
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
