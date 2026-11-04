# M37 decisions routed through the M63 approval engine, and the M11 floor on
# every sale (A04 audit, 2026-11-04, C4/C8/C9).
#
# The catalogue item's activation and the brand authorisation are M37
# decisions, but cd_catalogue loads BEFORE cd_workflow_engine (a platform
# kernel the engine does not depend on), and a new dependency would change
# that load order. cd_rate_card is the first module that loads after both, so
# it carries the routing: cd_catalogue declares the lifecycle with no-op route
# hooks (the DOFA mixin's own pattern), and this file plugs the engine in.
from odoo import models
from odoo.exceptions import UserError

ROLE_CATALOGUE_PUBLISHER = "cd_catalogue.group_catalogue_publisher"


class FixCatalogueItemApproval(models.Model):
    _name = "fix.catalogue.item"
    # the approvable mixin FIRST: it sits in front of the guard mixin the item
    # already carries; after it, Python finds no consistent method order
    _inherit = ["fix.approvable.mixin", "fix.catalogue.item"]

    _approval_domain = "catalogue_item"
    _approval_apply_method = "action_approve"
    _approval_group = ROLE_CATALOGUE_PUBLISHER
    _approval_routed = True

    def action_request_approval(self, justification=None):
        """Draft -> In Review (submit), routed to a Catalogue Publisher."""
        drafts = self.filtered(lambda r: r.state == "draft")
        if drafts:
            drafts.action_submit()
        rest = self - drafts
        if rest:
            rest._catalogue_route(justification)
        return True

    def _catalogue_route(self, justification=None):
        for rec in self:
            if rec.state != "in_review":
                raise UserError("Submit %s for review first." % rec.display_name)
        return super().action_request_approval(justification=justification)

    def _catalogue_route_submit(self):
        return self._catalogue_route()

    def _catalogue_route_guard(self):
        self._approval_assert_routed()

    def _catalogue_authority_user(self):
        return self._approval_authority_user()

    def _catalogue_acting_users(self):
        return self._approval_acting_users()

    def _approval_on_rejected(self, comment):
        self._catalogue_return_to_draft(comment)
        return super()._approval_on_rejected(comment)

    def action_recall_approval(self):
        result = super().action_recall_approval()
        self._catalogue_return_to_draft("recalled by the requester")
        return result


class FixBrandApproval(models.Model):
    _name = "fix.brand"
    _inherit = ["fix.approvable.mixin", "fix.brand"]

    _approval_domain = "catalogue_brand_authorisation"
    _approval_apply_method = "action_approve_authorisation"
    _approval_group = ROLE_CATALOGUE_PUBLISHER
    _approval_routed = True

    def action_request_approval(self, justification=None):
        fresh = self.filtered(lambda r: not r.authorisation_requested_by)
        if fresh:
            fresh.action_request_authorisation()
        rest = self - fresh
        if rest:
            rest._brand_route(justification)
        return True

    def _brand_route(self, justification=None):
        return super().action_request_approval(justification=justification)

    def _brand_route_request(self):
        return self._brand_route()

    def _brand_route_guard(self):
        self._approval_assert_routed()

    def _brand_authority_user(self):
        return self._approval_authority_user()

    def _brand_acting_users(self):
        return self._approval_acting_users()

    def _approval_on_rejected(self, comment):
        self._brand_clear_request(comment)
        return super()._approval_on_rejected(comment)

    def action_recall_approval(self):
        result = super().action_recall_approval()
        self._brand_clear_request("recalled by the requester")
        return result


class ProductProductFloor(models.Model):
    _inherit = "product.product"

    def _fix_check_sale(self, unit_price=None, channel=None):
        """BRU-PRC-04 on every selling document: a price below an active M11
        floor needs an approved DOFA override that covers that price
        (A04 audit M11-4, pf_10: the floor was read by no sale)."""
        result = super()._fix_check_sale(unit_price=unit_price, channel=channel)
        if unit_price is None:
            return result
        Floor = self.env["fix.price.floor"].sudo()
        for product in self:
            for floor in Floor._floors_for(product):
                floor.validate_price_against_floor(unit_price)
        return result
