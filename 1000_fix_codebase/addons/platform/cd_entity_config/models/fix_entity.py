# fix.entity — legal entity model on res.company (P03-M04-T01).
# One fix.entity per legal entity; branches reference it for isolation.
import logging

from odoo import api, fields, models
from odoo.exceptions import AccessError, ValidationError

_logger = logging.getLogger(__name__)

# A12 audit (2026-11-04) X4: the statutory register — entity, branch, zone,
# working calendar (+ lines/holidays), notification config and feature flags —
# was writable by every internal user. The ACLs now lock these models to
# Platform Admin; this check is the second layer for any path that reaches the
# ORM without an ACL verdict (a relaxed CSV row, a future endpoint). It binds
# the CALLER, not the recordset: sudo() service code is trusted, exactly as
# fix.guarded.mixin trusts it.
PLATFORM_ADMIN_GROUP = "cd_entity_config.group_platform_admin"
SYSTEM_GROUP = "base.group_system"


def require_platform_admin(env, what):
    """Refuse a statutory/platform master-data change by a non-admin caller.

    `what` names the register for the refusal message. Superuser code (crons,
    data loads, seeds, the country-pack loader) passes: env.su is the
    codebase-wide trust boundary, and the guards exist for the people, not for
    the server.
    """
    if env.su:
        return
    user = env.user
    if user.has_group(PLATFORM_ADMIN_GROUP) or user.has_group(SYSTEM_GROUP):
        return
    raise AccessError(
        "%s is statutory platform master data. Only a Platform Admin "
        "(cd_entity_config.group_platform_admin) may change it." % what
    )


class FixEntity(models.Model):
    """A legal entity within the 1000FiX group (M65 multi-entity/multi-country)."""

    _name = "fix.entity"
    _rec_name = "legal_name"
    _description = "Legal Entity"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "code"
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _code_unique = models.Constraint("UNIQUE (code)", "Entity code must be unique")

    # AS-02: chatter mixins mandatory
    # AS-03: company_id + operating_unit_id on transactional models
    # (fix.entity is a master, not transactional, but carries company_id for OU)

    code = fields.Char(
        string="Entity Code",
        required=True,
        size=10,
        tracking=True,
        help="Short unique code, e.g. 1000FIX-BD",
    )
    legal_name = fields.Char(string="Legal Name", required=True, tracking=True)
    legal_name_bn = fields.Char(
        string="Legal Name (Bengali)", help="Bengali legal name — DE-17 Bengali-first"
    )
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, ondelete="restrict"
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Primary Operating Unit",
        help="The OU for this entity's headquarters operations (AS-03)",
    )
    country_id = fields.Many2one(
        "res.country", string="Country", required=True, default=lambda self: self.env.ref("base.bd")
    )
    currency_id = fields.Many2one(
        "res.currency", string="Currency", default=lambda self: self.env.ref("base.BDT")
    )
    active = fields.Boolean(default=True, tracking=True)
    branch_ids = fields.One2many("fix.branch", "entity_id", string="Branches")
    branch_count = fields.Integer(compute="_compute_branch_count", store=True)

    _company_unique = models.Constraint(
        "UNIQUE (company_id)", "Each res.company maps to exactly one fix.entity"
    )

    @api.depends("branch_ids")
    def _compute_branch_count(self):
        for rec in self:
            rec.branch_count = len(rec.branch_ids)

    @api.constrains("code")
    def _check_code(self):
        for rec in self:
            if not rec.code.isupper():
                raise ValidationError("Entity code must be uppercase.")

    # A12 X4 / M30-12: the legal-entity register is statutory data. A clerk
    # renamed the entity, changed its code and moved it to India; now only a
    # Platform Admin may create, edit or delete an entity (branch.company_id,
    # M65 localisation and multi-entity reporting all hang off this row).
    @api.model_create_multi
    def create(self, vals_list):
        require_platform_admin(self.env, "The legal-entity register")
        return super().create(vals_list)

    def write(self, vals):
        require_platform_admin(self.env, "The legal-entity register")
        return super().write(vals)

    def unlink(self):
        require_platform_admin(self.env, "The legal-entity register")
        return super().unlink()

    # Odoo's install leaves base.main_company as "My Company" in USD/US; the
    # 1000FiX estate books in BDT under Bangladesh law. Runs on every module
    # install/upgrade (data/main_company_bd.xml) and only touches a company
    # that still carries an Odoo default name, so a configured company is
    # never overwritten.
    _ODOO_DEFAULT_COMPANY_NAMES = ("My Company", "My Company (San Francisco)", "YourCompany")

    @api.model
    def _bootstrap_main_company(self):
        bdt = self.env.ref("base.BDT", raise_if_not_found=False)
        bd = self.env.ref("base.bd", raise_if_not_found=False)
        if bdt and not bdt.active:
            bdt.active = True
        company = self.env.ref("base.main_company", raise_if_not_found=False)
        if not company or company.name not in self._ODOO_DEFAULT_COMPANY_NAMES:
            return
        company.write({"name": "1000 FiX Services Ltd."})
        if bd:
            company.partner_id.write({"country_id": bd.id})
        if not bdt or company.currency_id == bdt:
            return
        # Odoo forbids a company currency change once journal items exist.
        aml = self.env.get("account.move.line")
        if aml is not None and aml.sudo().search_count([("company_id", "=", company.id)], limit=1):
            _logger.warning(
                "cd_entity_config: %s already has journal items in %s; currency left "
                "unchanged — rebuild this database to book in BDT",
                company.name,
                company.currency_id.name,
            )
            return
        company.currency_id = bdt
