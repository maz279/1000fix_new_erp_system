# cd_competency tests — P08-M05 (CD-M22-01).
#
# A09 B6: six of the seven tests that stood here were inspect.getsource greps
# that passed with the controls deleted. The controls are proved
# behaviourally: the register and FR-LMS-039 in test_competency_orm.py, and
# the A09 controls as non-admin users in test_a09_m22_controls.py.
import unittest

from odoo.addons.cd_competency.models import fix_competency


class TestExpiryLeadTime(unittest.TestCase):
    def test_default_lead_time_is_the_value_the_code_used(self):
        # FR-LMS-011: configurable (ir.config_parameter
        # cd_competency.expiry_lead_days); 30 days until someone rules otherwise.
        self.assertEqual(fix_competency.EXPIRING_WINDOW_DAYS, 30)
        self.assertEqual(fix_competency.LEAD_DAYS_PARAM, "cd_competency.expiry_lead_days")


if __name__ == "__main__":
    unittest.main()
