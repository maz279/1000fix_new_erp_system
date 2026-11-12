# D-11 (E2E rehearsal on a fix_real copy, 11 Nov 2026): billed estimate parts
# never left stock. Two orders billed a RAM on their approved estimates, were
# delivered, closed and invoiced; nobody recorded a work-order part line and
# the close checked nothing, so on-hand was unchanged by the sale.
#
# The close is the estate's commercial point: the billing engine invoices a
# CLOSED order (service_order.closed -> billable event -> invoice). So the
# close gate now refuses an order whose approved estimate bills a stocked part
# that no M15 issue for this order covers, naming each part with the quantity
# billed and the quantity issued.
#
# Why refuse (option a) and not issue the shortfall automatically (option b):
# an M15 issue needs facts only the person fitting the part has — WHICH
# serial (a serialized part issues one received serial, in stock at that
# location, BRU-INV-14), WHERE it came from (a van issues only by its
# custodian, FR-INV-028; the store vs the van vs the workshop bench), and
# WHICH class (brand consignment only on that brand's warranty job,
# BRU-INV-01; customer-supplied only on that customer's job, BRU-INV-04). A
# system issue at close, run by a front-desk agent, would either fail on
# exactly those parts or have to bypass the rules as superuser, and it would
# hide who took the part. Refusing keeps every M15 control: the technician
# records the part fitted (work-order, workshop or field part line, or an M15
# issue against the job) and the issue runs through the one consumption path.
#
# Exempt: a part line with no product, a service product, a product with no
# M15 spare-part record (the same mapping every issue path uses), and a line
# of zero quantity. Matching is per order, per spare part, by quantity: the
# sum of CONSUMED issues (a returned issue no longer counts) whose job is this
# order, its workshop job or its field order. Superuser code (imports, data
# repair) is trusted, as by the money gate beside it.
#
# G12 (owner decision 12 Nov 2026): a billed part that was genuinely never
# fitted left a delivered order that could never close. An APPROVED "billed
# part not fitted" exemption (fix.so.part.exemption, decided by a branch
# manager from the M63 inbox) now counts as covered, beside the issues.
from __future__ import annotations

from collections import defaultdict

from odoo import models
from odoo.addons.cd_inventory.models.fix_stock_consumption import JOB_MODELS
from odoo.exceptions import UserError

ORDER_MODEL = "fix.service.order"
_EPS = 1e-6


def _qty(value: float) -> str:
    return ("%.4f" % value).rstrip("0").rstrip(".")


class FixServiceOrderPartsGate(models.Model):
    _inherit = "fix.service.order"

    def _fix_billed_stock_parts(self) -> dict:
        """{fix.spare.part: quantity} the approved estimate bills as stocked
        parts. Empty when there is no approved estimate."""
        self.ensure_one()
        estimate = self._fix_governing_estimate()
        if not estimate or estimate.state != "approved":
            return {}
        billed = defaultdict(float)
        for line in estimate.sudo().line_ids:
            if line.line_type != "part" or (line.quantity or 0.0) <= _EPS:
                continue
            part = self._fix_stock_part_for(line.product_id)
            if part:
                billed[part] += line.quantity
        return dict(billed)

    def _fix_stock_part_for(self, product):
        """The M15 spare part a billed product is, or an empty recordset when
        it is not stocked (no product, a service, no spare-part record)."""
        self.ensure_one()
        Part = self.env["fix.spare.part"].sudo()
        if not product or product.type == "service":
            return Part
        company = self.sudo().company_id
        return Part.search(
            [("product_id", "=", product.id), ("company_id", "in", [company.id, False])],
            limit=1,
        )

    def _fix_exempted_stock_parts(self) -> dict:
        """G12: {fix.spare.part: quantity} that APPROVED billed-part-not-fitted
        exemptions on the governing estimate cover."""
        self.ensure_one()
        exempted = defaultdict(float)
        for ex in self._fix_part_exemptions():
            if ex.part_id:
                exempted[ex.part_id] += ex.quantity
        return dict(exempted)

    def _fix_issued_stock_parts(self) -> dict:
        """{fix.spare.part: quantity} issued from M15 to this order's jobs and
        still consumed (a returned issue is back in stock)."""
        self.ensure_one()
        domain = []
        for model in JOB_MODELS:
            if model not in self.env:
                continue
            if model == ORDER_MODEL:
                ids = self.ids
            elif "order_id" in self.env[model]._fields:
                ids = (
                    self.env[model]
                    .sudo()
                    .with_context(active_test=False)
                    .search([("order_id", "=", self.id)])
                    .ids
                )
            else:
                continue
            if ids:
                clause = ["&", ("job_model", "=", model), ("job_res_id", "in", ids)]
                domain = ["|", *domain, *clause] if domain else clause
        issued = defaultdict(float)
        if not domain:
            return {}
        issues = (
            self.env["fix.stock.consumption"].sudo().search([("state", "=", "consumed"), *domain])
        )
        for issue in issues:
            issued[issue.product_id] += issue.quantity
        return dict(issued)

    def _fix_unissued_billed_parts(self) -> list:
        """The billed stocked parts that neither M15 issued to this order nor
        an approved exemption (G12) covers: [{"part", "billed", "issued",
        "exempted"}], in part-number order."""
        self.ensure_one()
        billed = self._fix_billed_stock_parts()
        if not billed:
            return []
        issued = self._fix_issued_stock_parts()
        exempted = self._fix_exempted_stock_parts()
        gaps = [
            {
                "part": part,
                "billed": qty,
                "issued": issued.get(part, 0.0),
                "exempted": exempted.get(part, 0.0),
            }
            for part, qty in billed.items()
            if qty - issued.get(part, 0.0) - exempted.get(part, 0.0) > _EPS
        ]
        return sorted(gaps, key=lambda g: g["part"].part_number or "")

    def _check_close_gate(self) -> None:
        super()._check_close_gate()
        self._check_billed_parts_issued()

    def _check_billed_parts_issued(self) -> None:
        """D-11: a billed stocked part has left stock before the order closes."""
        self.ensure_one()
        if self.env.su:
            return
        gaps = self._fix_unissued_billed_parts()
        if not gaps:
            return
        listed = "; ".join(
            "%s %s: billed %s, issued %s%s"
            % (
                g["part"].part_number,
                g["part"].name,
                _qty(g["billed"]),
                _qty(g["issued"]),
                ", exempted %s" % _qty(g["exempted"]) if g["exempted"] > _EPS else "",
            )
            for g in gaps
        )
        raise UserError(
            "Order %s cannot be closed: its approved estimate bills parts that have not left "
            "stock (%s). Record each part fitted on the work order (or the workshop or field "
            "job), which issues it from M15, then close. A part that was never fitted is "
            "exempted instead: request a billed-part-not-fitted exemption, which a branch "
            "manager approves (G12)." % (self.name, listed)
        )
