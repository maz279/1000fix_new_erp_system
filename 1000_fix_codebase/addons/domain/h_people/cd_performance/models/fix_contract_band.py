# cd_performance — I7 of the A09 build brief: the contract salary is checked
# against the compensation band of the employee's grade.
#
# A09 audit M57-40 / M57-F9: bands were linked to nothing; an HR Officer
# created a 500,000 contract for a grade whose band maximum is 30,000. The
# band is M57's (fix.compensation.band); this inherit lives here so core HR
# needs no dependency on performance.
#
# The band form defines a band as MONTHLY GROSS compensation, so the check
# compares the contract's gross (basic plus the monthly allowances). A draft is
# not checked: the check binds when the contract leaves draft.
from odoo import api, models

GROSS_FIELDS = (
    "basic_monthly",
    "house_rent",
    "medical_allowance",
    "conveyance_allowance",
    "technical_allowance",
    "other_allowance",
    "dearness_allowance",
    "adhoc_allowance",
)


class FixEmploymentContractBand(models.Model):
    _inherit = "fix.employment.contract"

    def _fix_contract_grade(self):
        self.ensure_one()
        position = self["position_id"] if "position_id" in self._fields else False
        position = position or self.employee_id.sudo().position_id
        return position.sudo().grade if position else False

    def _fix_contract_gross(self):
        self.ensure_one()
        return sum(float(self[f] or 0.0) for f in GROSS_FIELDS if f in self._fields)

    @api.constrains("employee_id", "company_id", "state", *GROSS_FIELDS)
    def _check_salary_within_band(self):
        """A DRAFT contract may carry any salary (M58's hire drafts one from
        the offer, I6); the band binds from the moment the contract is not a
        draft, so activation (and any later change) is where it is refused."""
        Band = self.env["fix.compensation.band"]
        for rec in self:
            if rec.state == "draft":
                continue
            grade = rec._fix_contract_grade()
            if not grade:
                continue
            gross = rec._fix_contract_gross()
            exception = (
                self.env["fix.band.exception"]
                .sudo()
                ._fix_covering(rec.employee_id, grade, gross, contract=rec)
            )
            Band._fix_check_amount(
                grade,
                gross,
                company=rec.company_id,
                what="The contract's monthly gross",
                exception=exception,
            )
