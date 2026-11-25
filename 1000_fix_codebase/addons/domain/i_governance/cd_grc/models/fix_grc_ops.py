# fix_grc_ops — M60: control testing, SoD rules, delegated authority, licence
# register, policy governance, legal matters, PDPA requests and whistleblowing.
# Risk register, controls, compliance frameworks/obligations and audit
# findings live in fix_grc.py.
import contextlib
import datetime

from odoo import api, fields, models
from odoo.addons.cd_entity_config.models.fix_dofa import DOFA_TIERS
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from .fix_grc import OFFICER_GROUP, _require_group

DOA_ADMIN_GROUP = "cd_grc.group_grc_dofa_admin"


class FixGrcControlTest(models.Model):
    """A10 P1-5 (M60-9): a control test is the tester's record of ONE test.
    The tester is stamped from the session and may not be the control's
    owner; the result stamps the control (last_tested / test_result — typed
    writes of those fields are refused); and a FAILED test raises the
    deficiency (an NCR) and drives it to a CAPA owned by the control owner,
    so a failing control can never sit quietly under an accepted residual."""

    _name = "fix.grc.control.test"
    _description = "Control Test"
    _inherit = ["fix.guarded.mixin"]
    _order = "tested_on desc, id desc"

    # a result short of 'effective' is a failed test
    FAILED_RESULTS = ("partially_effective", "ineffective")

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    control_id = fields.Many2one("fix.control", required=True, ondelete="cascade", index=True)
    tested_on = fields.Date(required=True, default=fields.Date.context_today)
    tester_id = fields.Many2one("hr.employee", string="Tester")
    sample_size = fields.Integer(string="Sample Size")
    exceptions = fields.Integer(string="Exceptions Found")
    result = fields.Selection(
        [
            ("effective", "Effective"),
            ("partially_effective", "Partially Effective"),
            ("ineffective", "Ineffective"),
        ],
        required=True,
        default="effective",
    )
    notes = fields.Text()

    @api.constrains("tester_id", "control_id")
    def _check_tester_is_not_the_owner(self):
        for rec in self:
            owner = rec.control_id.owner_id
            if rec.tester_id and owner and rec.tester_id == owner:
                raise ValidationError(
                    "The tester of a control may not be its owner (A10 P1-5, "
                    "M60-9): %s both owns and tests '%s'." % (owner.name, rec.control_id.name)
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.grc.control.test") or "CTST/New"
                )
            # the tester is the session's employee unless the record names the
            # (third-party) tester explicitly
            if not vals.get("tester_id"):
                vals["tester_id"] = self.env.user.employee_id.id or False
        tests = super().create(vals_list)
        tests._stamp_control()
        tests.filtered(lambda t: t.result in self.FAILED_RESULTS)._raise_deficiency()
        return tests

    def write(self, vals):
        res = super().write(vals)
        if {"result", "tested_on"} & set(vals):
            self._stamp_control()
            self.filtered(lambda t: t.result in self.FAILED_RESULTS)._raise_deficiency()
        return res

    def _stamp_control(self):
        """The control's assessment record is the test's conclusion, stamped —
        never typed (fix.control guards last_tested and test_result). The
        control's selection says 'partially' where the test's says
        'partially_effective'."""
        to_control = {
            "effective": "effective",
            "partially_effective": "partially",
            "ineffective": "ineffective",
        }
        for rec in self:
            rec.control_id._guarded().write(
                {
                    "last_tested": rec.tested_on,
                    "test_result": to_control.get(rec.result, rec.result),
                }
            )

    def _raise_deficiency(self):
        """A failed test raises a deficiency (an NCR linked to this test) and
        drives the QMS journey to a CAPA owned by the control owner (or the
        risk owner). Idempotent: one deficiency per test."""
        Ncr = self.env["fix.ncr"].sudo()
        for rec in self:
            control = rec.control_id
            if Ncr.search_count([("control_test_id", "=", rec.id)]):
                continue
            owner = control.owner_id or control.risk_id.owner_id
            if not owner:
                raise UserError(
                    "The control '%s' has no owner and its risk names none either: "
                    "a failed test must raise a deficiency someone is accountable "
                    "for. Name the control's owner first (A10 P1-5, M60-9)." % control.name
                )
            label = dict(rec._fields["result"].selection).get(rec.result, rec.result)
            sample = rec.sample_size or "—"
            ncr = Ncr.create(
                {
                    "source": "control_test",
                    "control_test_id": rec.id,
                    "severity": "major" if rec.result == "ineffective" else "minor",
                    "description": (
                        "Control test %s (%s) found the control '%s' %s: %d "
                        "exception(s) in a sample of %s. The control no longer "
                        "grounds the residual assessment of '%s'."
                        % (
                            rec.name,
                            rec.tested_on,
                            control.name,
                            label.lower(),
                            rec.exceptions or 0,
                            sample,
                            control.risk_id.name or "—",
                        )
                    ),
                }
            )
            # the QMS journey requires the root cause before the CAPA; the
            # test's factual finding is the record, the owner investigates
            ncr.action_set_root_cause(
                "Control test %s found the control %s (%d exception(s) in a "
                "sample of %s) — root cause under investigation by the control "
                "owner (%s)." % (rec.name, label.lower(), rec.exceptions or 0, sample, owner.name)
            )
            ncr.action_open_capa(
                corrective_action=(
                    "Remediate the control '%s' (found %s by test %s on %s) and "
                    "re-test it until the result is effective."
                    % (control.name, label.lower(), rec.name, rec.tested_on)
                ),
                owner_id=owner.id,
            )
            rec.control_id.message_post(
                body=(
                    "Deficiency raised: %s found this control %s — the CAPA on NCR "
                    "%s is owned by %s (A10 P1-5, M60-9)."
                    % (rec.name, label.lower(), ncr.name, owner.name)
                )
            )


class FixNcrControlDeficiency(models.Model):
    """A10 P1-5 (M60-9): the NCR a failed control test raises."""

    _inherit = "fix.ncr"

    source = fields.Selection(
        selection_add=[("control_test", "Control Test (M60)")],
        ondelete={"control_test": "cascade"},
    )
    control_test_id = fields.Many2one(
        "fix.grc.control.test",
        string="Control Test",
        ondelete="set null",
        index=True,
    )


class FixApprovalMatrixRiskAcceptance(models.Model):
    """A10 P1-5 (M60-7): lets a DoA matrix row target the routed above-appetite
    residual acceptance (narrowing the coded CFO-group authority per A11 E3)."""

    _inherit = "fix.approval.matrix"

    decision_domain = fields.Selection(
        selection_add=[("risk_acceptance", "Risk Residual Acceptance")],
        ondelete={"risk_acceptance": "cascade"},
    )


class FixGrcSodRule(models.Model):
    _name = "fix.grc.sod.rule"
    _description = "Segregation of Duties Rule"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    # A10 P1-3 (M60-4): a rule that names roles the access engine has never
    # heard of guards nothing. Both ends now reference the reconciled
    # register (fix.role) that M29's grant paths check against.
    role_a = fields.Many2one("fix.role", string="First Role", required=True, index=True)
    role_b = fields.Many2one("fix.role", string="Incompatible Role", required=True, index=True)
    conflict_area = fields.Char(string="Process Area")
    severity = fields.Selection(
        [("high", "High"), ("medium", "Medium"), ("low", "Low")],
        required=True,
        default="high",
    )
    compensating_control = fields.Char(string="Compensating Control")
    state = fields.Selection(
        [("active", "Active"), ("waived", "Waived")], required=True, default="active"
    )
    waived_by_id = fields.Many2one("res.users", string="Waived By", readonly=True)
    waived_on = fields.Date(string="Waived On", readonly=True)

    def _fix_guarded_fields(self) -> set:
        # A10 R1 (M60-4): the waiver state and its record change only through
        # action_waive — a conflicted user typing 'waived' was the finding.
        return super()._fix_guarded_fields() | {"state", "waived_by_id", "waived_on"}

    def action_waive(self, reason=""):
        """A waiver is a Compliance Officer's recorded decision (M60-4); the
        conflicted-user waiver register is P1-3's to build on top."""
        _require_group(
            self.env,
            OFFICER_GROUP,
            "Only a Compliance Officer waives a segregation-of-duties rule " "(A10 R1, M60-4).",
        )
        if not (reason or "").strip():
            raise UserError(
                "State why the rule is waived — the compensating control is part "
                "of the record (A10 R1, M60-4)."
            )
        for rec in self:
            if rec.state == "waived":
                raise UserError("%s is already waived." % rec.name)
            rec._guarded().write(
                {
                    "state": "waived",
                    "waived_by_id": self.env.user.id,
                    "waived_on": fields.Date.context_today(rec),
                }
            )
            rec.message_post(body="Waived by %s: %s" % (self.env.user.name, reason.strip()))
        return True

    # ------------------------------------------------------------------
    # A10 deep audit (2026-11-22, A3-F01): the governance register was empty
    # on every estate while the controls M29 actually enforces (fix.sod.control,
    # 61 role-pair controls on live) were invisible to M60. The register is
    # now DERIVED from the enforced controls, DoA-register style: an upsert
    # by source control that never touches the waiver record — a waived rule
    # keeps its waiver across rebuilds, because the waiver is an officer's
    # decision, not a projection of the control.
    source_control_id = fields.Many2one(
        "fix.sod.control",
        string="Enforced Control (M29)",
        index=True,
        ondelete="set null",
        help="The M29 control this governance row is derived from; empty on a "
        "manually-authored rule.",
    )
    derived_synced_at = fields.Datetime(readonly=True)

    SEVERITY_FROM_ACTION = {"block": "high", "warn": "medium", "log": "low"}

    @api.model
    def _sod_rows_from_controls(self):
        """One register row per ACTIVE role-pair control. Group-pair controls
        (fix.sod.control with group ends instead of role ends) have no role
        ends to mirror and stay governed on the M29 side only — counted and
        reported, never silently dropped."""
        rows, skipped = [], 0
        for ctl in self.env["fix.sod.control"].sudo().search([("active", "=", True)]):
            if not (ctl.role_a_id and ctl.role_b_id):
                skipped += 1
                continue
            rows.append(
                {
                    "name": "%s: %s" % (ctl.code, ctl.name),
                    "company_id": ctl.company_id.id,
                    "role_a": ctl.role_a_id.id,
                    "role_b": ctl.role_b_id.id,
                    "conflict_area": ctl.operating_unit_id.name or "",
                    "severity": self.SEVERITY_FROM_ACTION.get(ctl.conflict_action, "medium"),
                    "compensating_control": ctl.rationale or "",
                    "source_control_id": ctl.id,
                    "derived_synced_at": fields.Datetime.now(),
                }
            )
        return rows, skipped

    def action_rebuild_from_controls(self):
        """Regenerate the derived rows from the enforced controls (the M60 action)."""
        _require_group(
            self.env,
            OFFICER_GROUP,
            "Rebuilding the SoD governance register is a Compliance Officer's "
            "act — it re-reads the controls M29 enforces.",
        )
        res = self._sod_rebuild()
        res["note"] = (
            "SoD register rebuilt: %d derived row(s) created, %d updated, "
            "%d group-pair control(s) left to M29."
            % (res["created"], res["updated"], res["skipped_group_pair"])
        )
        return res

    @api.model
    def cron_rebuild_sod(self):
        """Daily convergence: a control edited between rebuilds cannot leave
        the register describing conflicts nothing enforces (or hiding ones
        that are)."""
        return self._sod_rebuild()

    @api.model
    def _sod_rebuild(self) -> dict:
        Register = self.sudo()
        rows, skipped = Register._sod_rows_from_controls()
        by_source = {row["source_control_id"]: row for row in rows}
        updated = 0
        for rule in Register.search([("source_control_id", "!=", False)]):
            row = by_source.pop(rule.source_control_id.id, None)
            if row is None:
                # the control was retired or deactivated: the rule stays as
                # history (its waiver record is evidence); the officer retires
                # it explicitly
                continue
            # state/waived_* deliberately absent: the waiver survives rebuilds
            rule.write(row)
            updated += 1
        created = len(by_source)
        if by_source:
            Register.create(list(by_source.values()))
        return {"created": created, "updated": updated, "skipped_group_pair": skipped}


# A10 P1-4 (M60-6): the single delegated-authority register. The audit found
# two authority books that never read each other: this table — typed by hand,
# writable by every internal user, consulted by nothing — and the machinery
# that actually enforces authority (the DOFA ladders every tier derivation
# reads through _dofa_tier_for_amount, and the M63 approval matrix the engine
# routes by). A register that documents limits nothing enforces answers the
# auditor's question with fiction, so the table is retired as a SOURCE and
# kept as the read-only VIEW: rows exist only as a rebuild from the enforced
# machinery, a typed row is refused, and the rebuild is the Delegated
# Authority Owner's (CFO) act.
DOA_REBUILD_KEY = "a10_doa_rebuild"
DOA_REBUILD_TOKEN = object()


class FixGrcAuthority(models.Model):
    _name = "fix.grc.authority"
    _description = "Delegated Authority Register (derived)"
    _inherit = ["fix.guarded.mixin"]
    _order = "amount_limit desc"

    name = fields.Char(required=True, readonly=True)
    company_id = fields.Many2one(
        "res.company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
        readonly=True,
    )
    role_title = fields.Char(string="Role / Position", required=True, readonly=True)
    amount_limit = fields.Monetary(
        currency_field="currency_id", string="Authority Limit", readonly=True
    )
    currency_id = fields.Many2one(
        "res.currency",
        required=True,
        default=lambda self: self.env.ref("base.BDT"),
        readonly=True,
    )
    authority_scope = fields.Char(string="Scope", readonly=True)
    delegate_to = fields.Char(string="May Delegate To", readonly=True)
    effective_from = fields.Date(required=True, default=fields.Date.context_today, readonly=True)
    source = fields.Selection(
        [("dofa", "DOFA ladder in force"), ("matrix", "M63 approval matrix")],
        string="Enforced Source",
        readonly=True,
    )
    source_ref = fields.Char(string="Source Record", readonly=True)
    synced_at = fields.Datetime(string="Rebuilt At", readonly=True)

    # -------------------------------------------------- the only write path
    def _doa_sync(self):
        """This model, allowed to rebuild the register. The context token is
        an object, not a flag: an RPC caller can put any key it likes in the
        context but cannot put this object there (the guard-mixin pattern)."""
        return self.with_context(**{DOA_REBUILD_KEY: DOA_REBUILD_TOKEN})

    def _doa_sync_open(self) -> bool:
        return self.env.su or self.env.context.get(DOA_REBUILD_KEY) is DOA_REBUILD_TOKEN

    @staticmethod
    def _doa_refuse() -> str:
        return (
            "The delegated-authority register is a VIEW over the machinery that "
            "enforces authority — the DOFA ladders in force and the M63 approval "
            "matrix (A10 P1-4). A typed row here would describe a limit nothing "
            "enforces. Change the ladder (M30) or the matrix (M63), then rebuild "
            "the register from M60."
        )

    @api.model_create_multi
    def create(self, vals_list):
        if not self._doa_sync_open():
            raise ValidationError(self._doa_refuse())
        return super().create(vals_list)

    def write(self, vals):
        if not self._doa_sync_open():
            raise ValidationError(self._doa_refuse())
        return super().write(vals)

    def unlink(self):
        if not self._doa_sync_open():
            raise ValidationError(self._doa_refuse())
        return super().unlink()

    # --------------------------------------------------------- the rebuild
    def action_rebuild(self):
        """Regenerate every row from the enforced sources (the M60 action)."""
        _require_group(
            self.env,
            DOA_ADMIN_GROUP,
            "Rebuilding the delegated-authority register is the Delegated "
            "Authority Owner's (CFO) act — it re-reads the DOFA ladders in "
            "force and the M63 approval matrix.",
        )
        res = self._doa_rebuild()
        res["note"] = "Register rebuilt: %d derived row(s), %d stale row(s) removed." % (
            res["created"],
            res["removed"],
        )
        return res

    @api.model
    def cron_rebuild_doa(self):
        """Daily convergence: a matrix edit made between rebuilds cannot leave
        the register describing authority that no longer exists."""
        return self._doa_rebuild()

    @api.model
    def _doa_rebuild(self) -> dict:
        Register = self.sudo()
        existing = Register.search([])
        removed = len(existing)
        if existing:
            existing._doa_sync().unlink()
        vals_list = Register._doa_rows_from_enforced()
        if vals_list:
            Register._doa_sync().create(vals_list)
        return {"removed": removed, "created": len(vals_list)}

    @api.model
    def _doa_rows_from_enforced(self) -> list:
        """One register row per enforced authority limit, read from the two
        places the estate actually obeys. The M63 matrix is read through
        env.get: cd_grc does not depend on the workflow engine, and a register
        that crashed where the engine is absent would protect nothing."""
        now = fields.Datetime.now()
        today = fields.Date.context_today(self)
        rows = []
        ladders = self.env["fix.dofa.ladder"].sudo().search([("in_force", "=", True)])
        tiers = dict(DOFA_TIERS)
        bases = dict(self.env["fix.dofa.ladder"]._fields["basis"].selection)
        for ladder in ladders:
            currency = (ladder.company_id.currency_id or self.env.ref("base.BDT")).id
            for band in ladder.threshold_ids.sorted("upper_bound"):
                rows.append(
                    {
                        "name": band.display_name or ladder.name,
                        "company_id": ladder.company_id.id,
                        "currency_id": currency,
                        "role_title": tiers.get(band.tier, band.tier or "—"),
                        "amount_limit": band.upper_bound,
                        "authority_scope": "DOFA ladder in force · %s (%s basis)"
                        % (ladder.target_model, bases.get(ladder.basis, ladder.basis or "—")),
                        "effective_from": (ladder.ruled_at and fields.Date.to_date(ladder.ruled_at))
                        or today,
                        "source": "dofa",
                        "source_ref": "fix.dofa.ladder:%d" % ladder.id,
                        "synced_at": now,
                    }
                )
        Matrix = self.env.get("fix.approval.matrix")
        if Matrix is not None:
            domains = dict(Matrix._fields["decision_domain"].selection)
            for rule in Matrix.sudo().search([("active", "=", True)]):
                rows.append(
                    {
                        "name": rule.name
                        or "%s · %s"
                        % (
                            domains.get(rule.decision_domain, rule.decision_domain),
                            rule.res_model or "every model",
                        ),
                        "company_id": rule.company_id.id,
                        "currency_id": (rule.currency_id or self.env.ref("base.BDT")).id,
                        "role_title": rule.approver_role
                        or (
                            rule.approver_group_id.name
                            if rule.approver_group_id
                            else "Approver per matrix"
                        ),
                        "amount_limit": rule.threshold or 0.0,
                        "authority_scope": "M63 approval matrix · %s%s"
                        % (
                            rule.res_model or "every model",
                            " · %s" % domains.get(rule.decision_domain, rule.decision_domain)
                            if rule.decision_domain
                            else "",
                        ),
                        "effective_from": rule.date_from or today,
                        "source": "matrix",
                        "source_ref": "fix.approval.matrix:%d" % rule.id,
                        "synced_at": now,
                    }
                )
        return rows


class FixDofaLadderRegisterSync(models.Model):
    """A ruling resyncs the register (A10 P1-4): the view must never keep
    describing the authority of a ladder a ruling just retired."""

    _inherit = "fix.dofa.ladder"

    def action_put_in_force(self, reference="", countersigned_by=None):
        # countersigned_by is the A12 X3 two-person ruling kwarg — the
        # override must carry the parent's signature or every ruled ladder
        # from the A03/A12 suites raises TypeError before the resync.
        res = super().action_put_in_force(reference=reference, countersigned_by=countersigned_by)
        self.env["fix.grc.authority"].sudo()._doa_rebuild()
        return res


class FixGrcLicence(models.Model):
    _name = "fix.grc.licence"
    _description = "Corporate Licence Register"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "valid_to"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    licence_type = fields.Selection(
        [
            ("trade", "Trade Licence"),
            ("bin", "BIN / VAT Registration"),
            ("tin", "TIN"),
            ("fire", "Fire Safety"),
            ("environment", "Environment"),
            ("other", "Other"),
        ],
        required=True,
        default="trade",
    )
    number = fields.Char(string="Licence Number")
    authority = fields.Char(string="Issuing Authority")
    issued_on = fields.Date()
    valid_to = fields.Date()
    responsible_id = fields.Many2one("hr.employee", string="Responsible")
    state = fields.Selection(
        [
            ("valid", "Valid"),
            ("expiring", "Expiring Soon"),
            ("expired", "Expired"),
            ("suspended", "Suspended"),
        ],
        required=True,
        default="valid",
    )

    def _fix_guarded_fields(self) -> set:
        # A10 R1: the licence state is the register's own clock and decision
        # record — expiry moves by the retention-style cron (P1-2), suspension
        # by the Compliance Officer's action, never by a typed value.
        return super()._fix_guarded_fields() | {"state"}

    def action_suspend(self, reason=""):
        _require_group(
            self.env,
            OFFICER_GROUP,
            "Only a Compliance Officer suspends a licence (A10 R1).",
        )
        if not (reason or "").strip():
            raise UserError("State why the licence is suspended — the reason is the record.")
        for rec in self:
            if rec.state == "suspended":
                raise UserError("%s is already suspended." % rec.name)
            rec._guarded().write({"state": "suspended"})
            rec.message_post(body="Suspended by %s: %s" % (self.env.user.name, reason.strip()))
        return True

    def action_reinstate(self):
        _require_group(
            self.env,
            OFFICER_GROUP,
            "Only a Compliance Officer reinstates a licence (A10 R1).",
        )
        for rec in self:
            if rec.state != "suspended":
                raise UserError("%s is not suspended." % rec.name)
            rec._guarded().write({"state": "valid"})
            rec.message_post(body="Reinstated by %s." % self.env.user.name)
        return True

    # ------------------------------------------------------------- the clock
    @api.model
    def cron_licence_expiry(self):
        """The daily licence clock (A10 P1-2, M60-10). Expiry is computed by
        the system, never typed: a licence past its validity date becomes
        EXPIRED, one approaching it (30 days) becomes EXPIRING — both
        announced on the outbox. A SUSPENDED licence is a human decision and
        is left alone."""
        today = fields.Date.today()
        horizon = today + datetime.timedelta(days=30)
        expired = self.search(
            [
                ("state", "in", ("valid", "expiring")),
                ("valid_to", "!=", False),
                ("valid_to", "<", today),
            ]
        )
        expiring = self.search(
            [
                ("state", "=", "valid"),
                ("valid_to", ">=", today),
                ("valid_to", "<=", horizon),
            ]
        )
        for rec in expired:
            rec._guarded().write({"state": "expired"})
            self._publish_licence_event("grc.licence.expired", rec)
            rec.message_post(
                body="Expired on %s — renewal or retirement is now due." % rec.valid_to
            )
        for rec in expiring:
            rec._guarded().write({"state": "expiring"})
            self._publish_licence_event("grc.licence.expiring", rec)
            rec.message_post(
                body="Expiring on %s — %d day(s) left."
                % (rec.valid_to, (rec.valid_to - today).days)
            )
        return len(expired) + len(expiring)

    def _publish_licence_event(self, event_type, rec):
        publish(
            self.env,
            event_type,
            "fix.grc.licence",
            rec.id,
            {
                "licence": rec.name,
                "type": rec.licence_type,
                "number": rec.number or "",
                "authority": rec.authority or "",
                "valid_to": str(rec.valid_to or ""),
            },
        )

    def consume_licence_clock(self, env_from_relay):
        """In-Odoo consumer for grc.licence.expired / grc.licence.expiring
        (relay-only): keeps the register's own thread as the audit trail."""
        if not self.env.su:
            raise UserError("The licence clock consumer runs from the event relay only.")
        lic = self.browse(int(env_from_relay.get("aggregate_id") or 0)).exists()
        if lic:
            lic.message_post(body="Licence clock announcement relayed to the register.")
        return True


class FixGrcPolicy(models.Model):
    _name = "fix.grc.policy"
    _description = "Corporate Policy"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "code"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    policy_type = fields.Selection(
        [
            ("hr", "HR"),
            ("quality", "Quality"),
            ("security", "Information Security"),
            ("finance", "Finance"),
            ("hse", "HSE"),
            ("other", "Other"),
        ],
        required=True,
        default="quality",
    )
    version = fields.Char(default="1.0")
    owner_id = fields.Many2one("hr.employee", string="Policy Owner")
    approved_on = fields.Date()
    review_due = fields.Date()
    attestation_required = fields.Boolean(string="Attestation Required", default=True)
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"), ("retired", "Retired")],
        required=True,
        default="draft",
    )

    _code_unique = models.Constraint(
        "UNIQUE (code, company_id)", "A policy code is unique per company"
    )

    def _fix_guarded_fields(self) -> set:
        # A10 R1 (M60-11): approval and its date change only through
        # action_approve — the typed 'approved' with no approver was the
        # decorative approval the audit found.
        return super()._fix_guarded_fields() | {"state", "approved_on"}

    def action_approve(self):
        """A policy is approved by someone other than its owner (M60-11); the
        date is stamped, never typed. (Routing this through the M63 approval
        inbox with read-and-understood attestations is P1-1/P1-6.)"""
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s is not a draft policy." % rec.name)
            if (
                not self.env.su
                and rec.owner_id
                and rec.owner_id.user_id
                and rec.owner_id.user_id == self.env.user
            ):
                raise UserError(
                    "%s's owner does not approve their own policy (A10 R1, M60-11)." % rec.code
                )
            rec._guarded().write(
                {"state": "approved", "approved_on": fields.Date.context_today(rec)}
            )
            rec.message_post(body="Policy approved by %s." % self.env.user.name)

    def action_retire(self):
        _require_group(
            self.env, OFFICER_GROUP, "Only a Compliance Officer retires a policy (A10 R1)."
        )
        for rec in self:
            if rec.state != "approved":
                raise UserError(
                    "Only an approved policy is retired — %s is %s." % (rec.code, rec.state)
                )
            rec._guarded().write({"state": "retired"})
            rec.message_post(body="Policy retired by %s." % self.env.user.name)
        return True


class FixGrcLegal(models.Model):
    _name = "fix.grc.legal"
    _description = "Legal Matter"
    _order = "opened_on desc, id desc"
    _inherit = ["fix.guarded.mixin"]

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    matter_type = fields.Selection(
        [
            ("litigation", "Litigation"),
            ("contract", "Contract Dispute"),
            ("labour", "Labour / Employment"),
            ("ip", "IP / Trademark"),
            ("regulatory", "Regulatory Notice"),
            ("other", "Other"),
        ],
        required=True,
        default="litigation",
    )
    counterparty = fields.Char()
    opened_on = fields.Date(required=True, default=fields.Date.context_today)
    counsel = fields.Char(string="External Counsel")
    exposure = fields.Monetary(currency_field="currency_id", string="Exposure")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    state = fields.Selection(
        [
            ("open", "Open"),
            ("negotiation", "Negotiation"),
            ("closed", "Closed"),
            ("judgment", "Judgment"),
        ],
        required=True,
        default="open",
    )
    # A10 W2 (M60-2): closure needs the recorded outcome
    outcome = fields.Selection(
        [
            ("settled", "Settled"),
            ("withdrawn", "Withdrawn"),
            ("dismissed", "Dismissed"),
            ("won", "Won"),
            ("lost", "Lost"),
        ],
        string="Outcome",
        help="How the matter ended. Required before a matter can be closed (W2).",
    )
    close_note = fields.Text(
        string="Closing Note", help="The resolution terms or judgment reference."
    )
    closed_on = fields.Date(string="Closed On")

    _outcome_required = "A10 W2: record the outcome and the closing note of %s before closing it."

    def _fix_guarded_fields(self) -> set:
        """A matter's lifecycle and its closure record change only through
        action_close (W2): a plain write must not close a matter."""
        return {"state", "outcome", "closed_on"}

    def _fix_form_locked_fields(self) -> set:
        locked = set(self._fix_guarded_fields())
        if set(self.mapped("state")) == {"closed"}:
            # closed: the closure record itself freezes too
            locked |= {"close_note"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.grc.legal") or "LEG/New"
        return super().create(vals_list)

    def action_close(self, outcome=None, close_note=None):
        """A10 W2 (M60-2): only Legal Counsel (ACL group_grc_legal) closes a
        matter, and only with the recorded outcome and closing note. The
        workspace Close action prompts for both; values already on the
        matter (set earlier through its form) are accepted as-is."""
        for rec in self:
            if rec.state == "closed":
                raise UserError("%s is already closed." % rec.name)
            outcome = outcome or rec.outcome
            if outcome not in dict(self._fields["outcome"].selection):
                raise UserError(self._outcome_required % rec.name)
            close_note = (close_note or "").strip() or rec.close_note
            if not (close_note or "").strip():
                raise UserError(
                    "A10 W2: write the closing note of %s (the settlement terms or "
                    "judgment reference) before closing it." % rec.name
                )
            rec._guarded().write(
                {
                    "state": "closed",
                    "outcome": outcome,
                    "close_note": close_note,
                    "closed_on": fields.Date.context_today(rec),
                }
            )


class FixGrcPdpa(models.Model):
    _name = "fix.grc.pdpa"
    _description = "PDPA Data Subject Request"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "received_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    request_type = fields.Selection(
        [
            ("access", "Access"),
            ("erasure", "Erasure"),
            ("correction", "Correction"),
            ("portability", "Portability"),
            ("objection", "Objection"),
        ],
        required=True,
        default="access",
    )
    subject_name = fields.Char(string="Data Subject", required=True)
    received_on = fields.Date(required=True, default=fields.Date.context_today)
    # A10 P1-2 (M60-10): the DSR deadline is DERIVED from the request date —
    # the PDPA's 30-day response window — never typed. A typed due_on could
    # quietly move a statutory deadline.
    due_on = fields.Date(
        string="SLA Due (received + 30 days)",
        compute="_compute_due_on",
        store=True,
        help="Derived: received_on + the 30-day PDPA response window.",
    )

    @api.depends("received_on")
    def _compute_due_on(self):
        for rec in self:
            rec.due_on = rec.received_on + datetime.timedelta(days=30) if rec.received_on else False

    handled_by_id = fields.Many2one("hr.employee", string="Handled By")
    outcome = fields.Selection(
        [
            ("pending", "Pending"),
            ("fulfilled", "Fulfilled"),
            ("refused", "Refused"),
            ("partially", "Partially Fulfilled"),
        ],
        required=True,
        default="pending",
    )
    notes = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.grc.pdpa") or "DSR/New"
        return super().create(vals_list)

    def _fix_guarded_fields(self) -> set:
        # A10 R1: the outcome of a data-subject request is the DSR's decision
        # record — fulfilled/refused is an officer's act, not a typed value.
        # overdue_notified_on joins it: the statutory clock's evidence is the
        # system's, not a typed value (A10 deep audit 2026-11-22, A3-F04).
        return super()._fix_guarded_fields() | {"outcome", "overdue_notified_on"}

    # A10 deep audit (2026-11-22, A3-F04): the 30-day SLA due date was derived
    # but nothing watched it. The clock's escalation flag.
    overdue_notified_on = fields.Date(
        readonly=True,
        help="The day the Compliance Officers were told this request went past "
        "its PDPA response window (set once, by the daily clock).",
    )

    @api.model
    def cron_dsr_overdue(self):
        """Daily PDPA clock: an unanswered request past its 30-day window
        tells the Compliance Officers ONCE (the DSR list keeps showing it
        overdue; re-notification would be noise, silence would be the
        original finding)."""
        today = fields.Date.context_today(self)
        overdue = (
            self.sudo()
            .search([("outcome", "in", ("pending", "partially")), ("due_on", "<", today)])
            .filtered(lambda r: not r.overdue_notified_on)
        )
        if not overdue:
            return True
        group = self.env.ref("cd_grc.group_grc_officer", raise_if_not_found=False)
        officers = (group.sudo().user_ids if group else self.env["res.users"]).filtered(
            lambda u: u.active and not u.share
        )
        for rec in overdue:
            rec._guarded().write({"overdue_notified_on": today})
            rec.message_post(
                body=(
                    "PDPA response window OVERDUE: %s was received on %s and its "
                    "30-day window closed %s. Record the outcome (fulfil/refuse) "
                    "and answer the data subject." % (rec.name, rec.received_on, rec.due_on)
                ),
                partner_ids=officers.mapped("partner_id").ids,
                subtype_xmlid="mail.mt_comment",
            )
        return True

    def action_fulfil(self):
        _require_group(
            self.env,
            OFFICER_GROUP,
            "Only a Compliance Officer records a PDPA request outcome (A10 R1).",
        )
        for rec in self:
            if rec.outcome != "pending":
                raise UserError("%s was already handled (%s)." % (rec.name, rec.outcome))
            rec._guarded().write({"outcome": "fulfilled"})
            rec.message_post(body="Request fulfilled by %s." % self.env.user.name)
        return True

    def action_refuse(self, reason=""):
        _require_group(
            self.env,
            OFFICER_GROUP,
            "Only a Compliance Officer refuses a PDPA request (A10 R1).",
        )
        if not (reason or "").strip():
            raise UserError("State the refusal ground — PDPA refusals answer to the law.")
        for rec in self:
            if rec.outcome != "pending":
                raise UserError("%s was already handled (%s)." % (rec.name, rec.outcome))
            rec._guarded().write({"outcome": "refused"})
            rec.message_post(body="Refused by %s: %s" % (self.env.user.name, reason.strip()))
        return True


class FixGrcWhistle(models.Model):
    """A whistleblowing report (A10 W1).

    Confidentiality model: the read ACL carries only the Intake (Audit
    Committee) and Investigator groups; investigators additionally see only
    the reports assigned to them (record rule). The reporter's identity is
    stamped by the system at intake, is never part of any event payload,
    and a investigator reads it only through action_reveal_reporter, which
    records the access in fix.pii.access.log. The intake facts (summary,
    channel, category, reported_on, anonymous) are guarded: immutable after
    filing — the report is kept as received.
    """

    _name = "fix.grc.whistle"
    _description = "Whistleblowing Report"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "reported_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    channel = fields.Selection(
        [
            ("hotline", "Hotline"),
            ("email", "Email"),
            ("web", "Web Form"),
            ("letter", "Letter"),
            ("in_person", "In Person"),
        ],
        required=True,
        default="hotline",
    )
    category = fields.Selection(
        [
            ("fraud", "Fraud / Bribery"),
            ("harassment", "Harassment"),
            ("safety", "Safety Breach"),
            ("data", "Data Privacy"),
            ("other", "Other"),
        ],
        required=True,
        default="fraud",
    )
    reported_on = fields.Date(required=True, default=fields.Date.context_today)
    anonymous = fields.Boolean(string="Anonymous", default=True)
    summary = fields.Text(required=True)
    investigator_id = fields.Many2one("hr.employee", string="Investigator")
    state = fields.Selection(
        [
            ("received", "Received"),
            ("investigating", "Investigating"),
            ("substantiated", "Substantiated"),
            ("unsubstantiated", "Unsubstantiated"),
            ("closed", "Closed"),
        ],
        required=True,
        default="received",
    )
    # A10 W1 fields ---------------------------------------------------------
    reporter_user_id = fields.Many2one(
        "res.users",
        string="Reporter (system-recorded)",
        readonly=True,
        index=True,
        groups="base.group_system",
        help="Stamped from the session at intake. Even the assigned "
        "investigator reads it only through action_reveal_reporter, which "
        "logs the access; never part of an event payload.",
    )
    investigation_notes = fields.Text(string="Investigation Notes")
    finding = fields.Selection(
        [
            ("substantiated", "Substantiated"),
            ("unsubstantiated", "Unsubstantiated"),
            ("unfounded", "Unfounded"),
            ("policy_gap", "Policy Gap Identified"),
        ],
        string="Finding",
        help="The conclusion of the investigation. Required at closure (W1).",
    )
    follow_up = fields.Char(
        string="Follow-up Action", help="What happens next because of this report."
    )
    reviewer_id = fields.Many2one(
        "res.users",
        string="Second Reviewer",
        help="A second reviewer, never the investigator, confirms the closure (W1).",
    )
    revealed_count = fields.Integer(
        string="Identity Reveals",
        help="How many times the reporter's identity was revealed (each reveal is logged).",
    )

    def _fix_guarded_fields(self) -> set:
        """The intake facts are immutable after filing; the workflow fields
        change only through the actions below."""
        return {
            "state",
            "summary",
            "channel",
            "category",
            "reported_on",
            "anonymous",
            "investigator_id",
            "finding",
            "reviewer_id",
        }

    def _fix_form_locked_fields(self) -> set:
        """At filing (a new record) the intake facts ARE the filing — they
        must reach create(); the workflow fields are never typed. Once
        filed, the report is kept as received: everything it was filed
        with locks, and a closed report freezes the notes too."""
        if not self.ids:
            return {"state", "investigator_id", "finding", "reviewer_id"}
        locked = set(self._fix_guarded_fields())
        if set(self.mapped("state")) == {"closed"}:
            locked |= {"investigation_notes", "follow_up"}
        return locked

    # ------------------------------------------------------------------ W1 --
    def _w1_require_intake(self):
        if self.env.su:
            return
        if not self.env.user.has_group("cd_grc.group_grc_whistle_intake"):
            raise UserError(
                "Only the Whistleblowing Intake (Audit Committee) may do this. "
                "Reports are filed through the intake channel, never edited."
            )

    def _w1_require_investigator(self, rec):
        if self.env.su:
            return
        if not rec.investigator_id or rec.investigator_id.user_id != self.env.user:
            raise UserError("Only the investigator assigned to %s may do this (W1)." % rec.name)

    @api.model_create_multi
    def create(self, vals_list):
        self._w1_require_intake()
        # The reporter identity is stamped by the system, never typed: an
        # authenticated filing records the session user (the intake clerk
        # for a hotline/letter report). The field is system-only, so the
        # stamp lands through sudo after creation.
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.grc.whistle") or "WBL/New"
            vals.pop("reporter_user_id", None)
            vals.pop("revealed_count", None)
            # a filing is born received: the workflow fields are never
            # typed (the token below is for the intake facts only)
            born = [
                n
                for n in ("state", "investigator_id", "finding", "reviewer_id")
                if n in vals and vals[n] not in (False, None, "", 0, "received")
            ]
            if born and not self._fix_guard_open():
                self._fix_guard_refuse(born)
        # Filing is the transition that sets the intake facts: create runs
        # with the guard token so the immutable-after-filing fields can be
        # born (write() stays guarded — only the actions below may change
        # them). super(FixGrcWhistle, …) skips this override, so no loop.
        # The born records are re-homed on the caller's env IMMEDIATELY:
        # records inherit the env they were created in, and one carrying
        # the token would accept guarded writes forever (found by the W1
        # control tests).
        recs = super(FixGrcWhistle, self._guarded()).create(vals_list).with_env(self.env)
        if not self.env.su:
            recs.sudo().write({"reporter_user_id": self.env.user.id})
        for rec in recs:
            self._w1_log_access(rec, "summary", "whistle report filed")
            rec.message_post(body="Report filed through the %s channel." % rec.channel)
        return recs

    def read(self, fields=None, load=None):
        # A10 W1: every read of a report is recorded (who read which report).
        # Superuser/relay reads are service traffic and are not logged.
        if not self.env.su and self.ids:
            for rec in self:
                self._w1_log_access(rec, "summary", "whistle report read")
        return super().read(fields=fields, load=load)

    def _w1_log_access(self, rec, field_name, reason):
        # record_access() itself creates with sudo and stamps the REAL
        # session user — the caller here — into user_id. Never let the
        # audit trail break the work it audits.
        with contextlib.suppress(Exception):
            self.env["fix.pii.access.log"].record_access(
                "fix.grc.whistle", rec.id, field_name, reason=reason
            )

    def action_assign_investigator(self, investigator_id):
        """Intake assigns the investigator — never themself (W1)."""
        self._w1_require_intake()
        investigator = self.env["hr.employee"].browse(investigator_id)
        for rec in self:
            if rec.investigator_id or rec.state != "received":
                raise UserError(
                    "%s already has an investigator (assigned when received)." % rec.name
                )
            if not investigator.user_id:
                raise UserError(
                    "The investigator of %s must be an employee with a login "
                    "(they act from their own session)." % rec.name
                )
            if investigator.user_id == self.env.user and not self.env.su:
                raise UserError(
                    "The Audit Committee member who files %s may not investigate "
                    "it themself (W1 segregation of duties)." % rec.name
                )
            rec._guarded().write({"investigator_id": investigator.id})
            rec.message_post(body="Investigator assigned by %s." % self.env.user.name)
        return True

    def action_investigate(self):
        """The assigned investigator takes the report up."""
        for rec in self:
            self._w1_require_investigator(rec)
            if rec.state != "received":
                raise UserError("%s is not in the received state." % rec.name)
            rec._guarded().write({"state": "investigating"})
        return True

    def action_close(self, finding=None, follow_up=None, reviewer_id=None):
        """W1 closure: the assigned investigator records the finding; a second
        reviewer — named, or the first other Audit Committee member, stamped
        by the system and never the investigator — confirms the closure.
        The published event carries no reporter identity."""
        for rec in self:
            self._w1_require_investigator(rec)
            if rec.state != "investigating":
                raise UserError("Investigate %s before closing it." % rec.name)
            finding = finding or rec.finding
            if finding not in dict(self._fields["finding"].selection):
                raise UserError(
                    "Record the finding of %s (substantiated, unsubstantiated, "
                    "unfounded or policy gap)." % rec.name
                )
            reviewer = self._w1_pick_reviewer(rec, reviewer_id)
            rec._guarded().write(
                {
                    "state": "closed",
                    "finding": finding,
                    "follow_up": (follow_up or "").strip() or rec.follow_up or "",
                    "reviewer_id": reviewer.id,
                }
            )
            publish(
                self.env,
                "grc.whistle.closed",
                "fix.grc.whistle",
                rec.id,
                {
                    "report": rec.name,
                    "category": rec.category,
                    "finding": finding,
                    "follow_up": (follow_up or "").strip(),
                },
            )
        return True

    def _w1_pick_reviewer(self, rec, reviewer_id):
        """The second reviewer: the named one, else the first other member of
        the Audit Committee. Never the investigator, never the closer."""
        if reviewer_id:
            reviewer = self.env["res.users"].browse(reviewer_id)
            if not reviewer.exists():
                raise UserError("The named second reviewer of %s does not exist." % rec.name)
        else:
            intake = self.env.ref("cd_grc.group_grc_whistle_intake")
            investigator_user = rec.investigator_id.user_id
            candidates = intake.all_user_ids.filtered(
                lambda u: u.active and u != investigator_user and u != self.env.user
            )
            if not candidates:
                raise UserError(
                    "%s needs a second reviewer: appoint another member of the "
                    "Audit Committee (the investigator cannot review their own "
                    "closure, W1)." % rec.name
                )
            reviewer = candidates[:1]
        if reviewer == rec.investigator_id.user_id:
            raise UserError(
                "The second reviewer of %s may not be its investigator (W1)." % rec.name
            )
        return reviewer

    def action_reveal_reporter(self, reason=None):
        """The logged step-up: an investigator reads the reporter's identity.

        Requires a stated reason; the access lands in fix.pii.access.log and
        the reveal count rises. The field itself is system-only — this
        action (through sudo, after logging) is the one way in. Anonymous
        reports have nothing to reveal."""
        self.ensure_one()
        self._w1_require_investigator(self)
        reporter = self.sudo().reporter_user_id
        if self.anonymous or not reporter:
            return {
                "revealed": False,
                "note": "This report was filed anonymously through the intake channel; "
                "the reporter's identity is not recorded.",
            }
        if not (reason or "").strip():
            raise UserError(
                "State why the reporter's identity of %s must be revealed — the "
                "access is logged (W1)." % self.name
            )
        self._w1_log_access(self, "reporter_user_id", "identity revealed: %s" % reason.strip())
        self.write({"revealed_count": (self.revealed_count or 0) + 1})
        return {"revealed": True, "reporter": reporter.name}

    @api.model
    def consume_grc_whistle_closed(self, event):
        """grc.whistle.closed -> the closure note on the report's own thread.

        Relay-only (superuser) and idempotent: one closure note per finding
        value (a re-delivered event does not duplicate it). The external
        consumers (the audit-committee digest, BI) read the outbox; this
        in-Odoo consumer keeps the closure in the record's own history —
        without the reporter's identity, which is never in the payload."""
        if not self.env.su:
            raise UserError("consume_grc_whistle_closed runs only from the event relay.")
        payload = (event or {}).get("payload") or {}
        rec = self.browse(int(event.get("aggregate_id") or payload.get("id") or 0))
        if not rec.exists() or rec.state != "closed":
            return True
        marker = "Closed — finding: %s." % (payload.get("finding") or rec.finding)
        if any(marker in (m.body or "") for m in rec.message_ids):
            return True
        rec.message_post(body=marker)
        return True


REPORTS = {}
