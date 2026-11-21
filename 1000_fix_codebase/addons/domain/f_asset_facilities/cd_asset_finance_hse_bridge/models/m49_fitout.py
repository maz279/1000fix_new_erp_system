# m49_fitout — A07 ERP audit (2026-11-20) M47-11 / FIN-13 / LEAD-03 (A07 side):
# a branch fit-out is capital work in progress, not a typed budget.
#
# When an approved site project (opening or relocation) starts, the bridge
# raises a capex request for its budget on the site's branch and the fit-out
# category (FIT; parameter fitout_category_code), which finance approves in M49
# (its own DOFA). Bills on that capex's purchase orders debit the project's
# CWIP account (m49_capex_bill: the capex bill alone books Dr CWIP / Cr AP,
# no GRNI, agreed with A06). When the project is done, the CWIP is capitalised
# as leasehold improvement over the SHORTER of the category life and the
# remaining lease term (IFRS 16 / IAS 16.56). A step that cannot complete
# becomes a visible bridge exception, never a silent gap.
#
# R2a (2026-11-21): M47 states a fit-out's actual cost line by line
# (fix.site.project.cost -> cost entry facility_work_order.fit_out, role ->
# CWIP 100608). When that cost posts (the vendor's bill), its CWIP item is
# booked to the project's CWIP entry (opened from the approved capex), and the
# project carries the CWIP reference M47 needs to complete. On completion M47
# sets capitalisation_requested_on and states the facts
# (`_m47_capitalisation_facts`: branch, life = the shorter of the useful life
# and the remaining lease, in-service date); the bridge capitalises from them.
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError

from .fix_bridge_exception import dhaka_today, param_str, run_hook

FITOUT_CATEGORY_PARAM = "fitout_category_code"
FITOUT_TYPES = ("open", "relocate")


class FixSiteProjectCwip(models.Model):
    _inherit = "fix.site.project"

    capex_request_id = fields.Many2one(
        "fix.capex.request", string="M49 Capex (CWIP)", readonly=True, copy=False, index=True
    )

    def write(self, vals):
        if "capex_request_id" in vals and not self.env.su:
            from odoo.exceptions import UserError

            raise UserError("The capex of a site project is raised by the asset bridge only.")
        return super().write(vals)

    def action_start(self):
        result = super().action_start()
        Capex = self.env["fix.capex.request"].sudo()
        run_hook(self.env, "m49_fitout_capex", Capex._bridge_from_site_project, self)
        return result

    def action_done(self):
        result = super().action_done()
        Capex = self.env["fix.capex.request"].sudo()
        run_hook(self.env, "m49_fitout_capitalise", Capex._bridge_capitalise_site_project, self)
        return result


class FixCapexRequestSite(models.Model):
    _inherit = "fix.capex.request"

    site_project_id = fields.Many2one(
        "fix.site.project", string="M47 Site Project", readonly=True, copy=False, index=True
    )

    @api.model
    def _bridge_fitout_category(self, company):
        code = param_str(self.env, FITOUT_CATEGORY_PARAM, "FIT")
        return (
            self.env["fix.asset.category"]
            .sudo()
            .search([("company_id", "=", company.id), ("code", "=", code)], limit=1)
        )

    @api.model
    def _bridge_from_site_project(self, projects):
        made = self.browse()
        for project in projects.sudo():
            capital = (
                project.capitalise
                if "capitalise" in project._fields
                else project.project_type in FITOUT_TYPES
            )
            if not capital or (project.budget or 0.0) <= 0:
                continue
            if project.capex_request_id:
                continue
            site = project.site_id
            company = site.company_id or self.env.company
            ou = site.operating_unit_id or site.branch_id.operating_unit_id
            category = self._bridge_fitout_category(company)
            req = self.sudo().create(
                {
                    "company_id": company.id,
                    "operating_unit_id": ou.id,
                    "title": "Fit-out: %s (%s)" % (site.name, project.name),
                    "justification": "Raised from M47 site project %s, approved budget %.2f. "
                    "Bills on its purchase orders accumulate in CWIP; the project's completion "
                    "capitalises it." % (project.name, project.budget),
                    "amount": project.budget,
                    "category_id": category.id,
                    "site_project_id": project.id,
                }
            )
            project.with_context(fix_bridge=True).sudo().write({"capex_request_id": req.id})
            project.message_post(
                body="Capex %s raised in M49 for the fit-out (CWIP). Finance approves it."
                % req.name
            )
            made |= req
        return made

    @api.model
    def _bridge_lease_months_left(self, site):
        lease = (
            self.env["fix.site.lease"]
            .sudo()
            .search(
                [("site_id", "=", site.id), ("state", "=", "active")],
                order="end_date desc",
                limit=1,
            )
        )
        if not lease or not lease.end_date:
            return 0
        delta = relativedelta(lease.end_date, dhaka_today(self.env))
        return max(delta.years * 12 + delta.months + (1 if delta.days else 0), 1)

    @api.model
    def _bridge_capitalise_site_project(self, projects):
        """The completed project's CWIP becomes the fit-out asset, on M47's
        facts when M47 asked for capitalisation (capitalisation_requested_on):
        its branch, its life (the shorter of the useful life and the remaining
        lease, IAS 16.56). A project M47 did not ask to capitalise (nothing
        spent, a closure) is left alone."""
        assets = self.env["fix.fixed.asset"]
        for project in projects.sudo().filtered("capex_request_id"):
            if "capitalisation_requested_on" in project._fields and not (
                project.capitalisation_requested_on
            ):
                continue
            facts_fn = getattr(project, "_m47_capitalisation_facts", None)
            facts = facts_fn() if facts_fn else {}
            req = project.capex_request_id
            cwip = req.cwip_ids.filtered(lambda w: w.state == "open" and w.amount > 0)
            if not cwip:
                project.message_post(
                    body="Project done; capex %s has no posted CWIP cost to capitalise yet."
                    % req.name
                )
                continue
            category = req.category_id or self._bridge_fitout_category(req.company_id)
            life = facts.get("life_months") or category.useful_life_months
            if not facts.get("life_months"):
                left = self._bridge_lease_months_left(project.site_id)
                if left:
                    life = min(life, left)
            ou = facts.get("operating_unit_id")
            made = self.env["fix.fixed.asset"]
            for entry in cwip:
                if ou and not entry.operating_unit_id:
                    entry._guarded().write({"operating_unit_id": ou})
                made |= entry.action_capitalise(category=category, life_months=life)
            assets |= made
            project.message_post(
                body="Fit-out capitalised from CWIP: %s (life %s months)."
                % (", ".join(made.mapped("display_name")), life)
            )
        return assets


class FixAssetCostEntryFitout(models.Model):
    _inherit = "fix.asset.cost.entry"

    def _m52_after_posted(self, paid_on, ref):
        result = super()._m52_after_posted(paid_on, ref)
        fitout = self.filtered(
            lambda e: e.cost_type == "facility_work_order"
            and e.subtype == "fit_out"
            and e.source_model == "fix.site.project.cost"
            and e.move_id
        )
        for entry in fitout:
            run_hook(self.env, "m49_fitout_book", entry._bridge_book_fitout_cost)
        return result

    def _bridge_book_fitout_cost(self):
        """Book this posted fit-out cost's CWIP item to the project's CWIP
        entry (opened from the approved capex when it is not open yet)."""
        self.ensure_one()
        entry = self.sudo()
        cost = entry._m52_source()
        project = cost.project_id if cost else None
        if not project:
            raise UserError("%s: its site project is gone." % entry.name)
        req = project.capex_request_id
        if not req:
            raise UserError(
                "Fit-out cost %s of %s is in CWIP, but the project has no M49 capex: start the "
                "project (the bridge raises it) and have finance approve it."
                % (entry.name, project.name)
            )
        cwip = req.cwip_ids.filtered(lambda w: w.state == "open")[:1]
        if not cwip:
            if req.state != "approved":
                raise UserError(
                    "Fit-out cost %s is in CWIP, but capex %s of %s is not approved yet: "
                    "finance approves it, then Retry." % (entry.name, req.name, project.name)
                )
            cwip = (
                self.env["fix.cwip.entry"]
                .sudo()
                .browse(req.sudo().action_create_cwip()["cwip_ids"])
            )
        candidates = entry.move_id.line_ids.filtered(
            lambda ln: ln.account_id == entry.account_id and ln.debit > 0
        )
        booked = (
            self.env["fix.cwip.entry"]
            .sudo()
            .search([("cost_line_ids", "in", candidates.ids)])
            .mapped("cost_line_ids")
        )
        lines = candidates - booked
        exact = lines.filtered(lambda ln: abs(ln.debit - entry.amount) <= 0.005)[:1]
        lines = exact or lines
        if not lines:
            if entry.move_id.line_ids & cwip.cost_line_ids:
                return cwip  # booked already (a redelivery)
            raise UserError(
                "%s: %s has no unbooked CWIP item on %s."
                % (entry.name, entry.move_id.name, entry.account_id.code)
            )
        cwip._fix_book_cost(lines)
        vals = {}
        if not project.cwip_res_id:
            vals["cwip_res_id"] = cwip.id
        if "cwip_ref" in project._fields and not project.cwip_ref:
            vals["cwip_ref"] = cwip.name
        if vals:
            project._guarded().write(vals)
        project.message_post(
            body="Cost %s (%.2f) booked to CWIP %s." % (entry.name, entry.amount, cwip.name)
        )
        return cwip
