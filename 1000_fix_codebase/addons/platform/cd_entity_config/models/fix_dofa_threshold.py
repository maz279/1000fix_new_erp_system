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
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_dofa import DOFA_TIERS

_logger = logging.getLogger(__name__)


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


class FixDofaLadder(models.Model):
    """A named, versioned threshold ladder for one model's authority field.

    Several bases may exist for the same target (the REQ text and the DOFA
    matrix, say). Exactly one may be in force, which is what makes this a
    ruling rather than an opinion.
    """

    _name = "fix.dofa.ladder"
    _description = "DOFA Threshold Ladder"
    _inherit = ["mail.thread"]
    _order = "target_model, basis"

    name = fields.Char(required=True)
    target_model = fields.Char(
        required=True,
        index=True,
        help="The model whose authority this ladder governs, e.g. "
        "fix.loyalty.ledger or fix.complaint.",
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
        "which one is the RULING, and it is tracked on this record.",
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

    def action_put_in_force(self, reference=""):
        """Make this ladder the one in force. THIS is the ruling.

        Deliberately requires a reference: a change to who may approve what,
        with nothing recorded about who authorised the change, is not an
        improvement on a hard-coded list.
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
            siblings = self.sudo().search(
                [
                    ("target_model", "=", rec.target_model),
                    ("company_id", "=", rec.company_id.id),
                    ("in_force", "=", True),
                    ("id", "!=", rec.id),
                ]
            )
            siblings.write({"in_force": False})
            rec.write(
                {
                    "in_force": True,
                    "ruled_by": self.env.user.id,
                    "ruled_at": fields.Datetime.now(),
                    "ruling_reference": reference or rec.ruling_reference,
                }
            )
            rec.message_post(
                body="DOFA ladder for %s put in force on the %s basis by %s. "
                "Authority: %s. Superseded: %s."
                % (
                    rec.target_model,
                    dict(rec._fields["basis"].selection)[rec.basis],
                    self.env.user.name,
                    rec.ruling_reference,
                    ", ".join(siblings.mapped("name")) or "none",
                )
            )
        return True

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
