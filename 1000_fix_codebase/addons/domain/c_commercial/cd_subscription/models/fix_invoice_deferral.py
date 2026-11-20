# An invoice that credits the contract liability gets its recognition schedule.
#
# E2E3 rehearsal on a fix_real copy (11 Nov 2026, E3-03): contract billing
# periods and subscription charges are issued to deferred revenue
# (fix.ar.invoice.DEFERRED_SOURCES), and M53's recognition cron moves deferred
# revenue to revenue - but only along a fix.revenue.schedule, and nothing ever
# created one: create_from_deferral() had no production caller. An AMC fee
# billed in arrears (the walker bills a period once it has ended) stayed in
# 200401 Deferred income for ever.
#
# Now the issue posting creates the schedule for exactly the amount it put on
# the liability, over the billed period, named against the contract or
# subscription that is its basis (M53-6). The daily recognition cron
# (_cron_recognize) then releases it straight-line: a period already ended is
# recognised in full on the next run.
from datetime import timedelta

from odoo import models

# the source document of a deferred invoice -> (its period fields, its basis)
_DEFERRAL_BASIS = {
    "fix.contract.billing.period": "contract_id",
    "fix.subscription.charge": "subscription_id",
}


class FixArInvoiceDeferral(models.Model):
    _inherit = "fix.ar.invoice"

    def _post_issue_gl(self):
        result = super()._post_issue_gl()
        for inv in self:
            if inv.posted_move_id and inv._revenue_role() == "deferred_revenue":
                inv._fix_schedule_deferral()
        return result

    def _fix_deferred_amount(self) -> float:
        """What the issue posting credited to the liability (same split as
        _post_issue_gl: total less VAT, never negative)."""
        self.ensure_one()
        return round(max(self.total_payable - self.vat_amount, 0.0), 2)

    def _fix_schedule_deferral(self):
        """Create this invoice's recognition schedule once. Returns it, or an
        empty recordset when the invoice has nothing to defer or no basis."""
        self.ensure_one()
        Schedule = self.env["fix.revenue.schedule"].sudo()
        existing = Schedule.search(
            [("source_model", "=", self._name), ("source_id", "=", self.id)], limit=1
        )
        if existing:
            return existing
        amount = self._fix_deferred_amount()
        if amount <= 0.0 or self.source_model not in self.env:
            return Schedule
        source = self.env[self.source_model].sudo().browse(self.source_id).exists()
        if not source:
            return Schedule
        basis_field = _DEFERRAL_BASIS.get(self.source_model)
        basis = {}
        if basis_field:
            start, end = source.period_start, source.period_end
            basis = {basis_field: source[basis_field].id}
            unit = self.operating_unit_id or source[basis_field].operating_unit_id
        elif hasattr(source, "_fix_deferral_period"):
            # A04 ERP M09-F2: a protection premium defers over its cover term
            start, end = source._fix_deferral_period()
            unit = self.operating_unit_id
        else:
            return Schedule
        if self.source_model == "fix.subscription.charge":
            sub = source.subscription_id
            # A04 ERP M39-F1: one basis per subscription. Its scheduled
            # contract obligations already recognise this period's revenue.
            if sub._fix_recognition_basis() == "contract":
                return Schedule
        if not start or not end:
            return Schedule
        if end <= start:  # a one-day period still needs a positive term
            end = start + timedelta(days=1)
        return Schedule.create(
            {
                "company_id": self.company_id.id,
                "operating_unit_id": unit.id,
                "source_model": self._name,
                "source_id": self.id,
                "description": "Invoice %s - %s" % (self.name, source.display_name),
                "currency_id": self.currency_id.id,
                "total_amount": amount,
                "start_date": start,
                "end_date": end,
                **basis,
            }
        )
