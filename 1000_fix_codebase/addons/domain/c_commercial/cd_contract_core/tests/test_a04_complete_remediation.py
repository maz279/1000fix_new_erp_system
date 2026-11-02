"""RETIRED — superseded by test_a04_zero_trust_certification.py.

This file used to hold 20 tests and 66 assertions certifying the Area A04
remediation. Every assertion had the form:

    code = Path("addons/.../fix_contract.py").read_text()
    self.assertIn("total_delivery_cost = fields.Monetary", code)

It opened no Odoo environment (`self.env[` appeared zero times), created no
record and called no method. It therefore certified that identifiers were
*written*, never that controls *worked*.

What that cost, measured on 31 October 2026:

* **FLAW-08.1 was certified as fixed while being broken.** The remediation
  added `total_delivery_cost`, `contract_margin_bdt` and `contract_margin_pct`
  to `fix.contract`, then computed all three from a hard-coded
  `delivery_cost = 0.0`. Every contract in the estate reported a 100% gross
  margin. The three `assertIn` checks on those field declarations passed.
  `fix.service.order` had no `contract_id` at all, so the cost could not have
  been attributed even in principle.

* **It failed on a correct improvement.** `test_flaw_08_2` asserted the literal
  string "Stamp Act 1899 Schedule I statutory requirement" appeared in the
  model. When the activation gate was rewritten — removing a
  `skip_stamp_duty_check` context bypass that no caller ever set, and making
  non-chargeability an explicit recorded decision — the wording moved and the
  test went red against a strictly stronger control.

A suite that passes on a stub and fails on a fix is worse than no suite: it
spends review attention in exactly the wrong places.

The replacement, `test_a04_zero_trust_certification.py`, exercises the same
remediations against the live ORM — creating contracts, delivering work,
posting estimates, and asserting on computed results and refusals.

This module is kept rather than deleted so the provenance of that decision
stays in the repository. It is not evidence of anything and must not be cited
as certification.
"""

import unittest


class TestA04CompleteRemediationRetired(unittest.TestCase):
    @unittest.skip(
        "Retired: source-text assertions, no ORM. See "
        "test_a04_zero_trust_certification.py and the module docstring."
    )
    def test_retired(self):
        pass
