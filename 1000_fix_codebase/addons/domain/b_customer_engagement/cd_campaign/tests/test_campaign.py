# cd_campaign tests — P08-M04-T08, R06-M01-T05 (CD-M35-01).
import inspect
import unittest

from odoo.addons.cd_campaign.models.fix_campaign import FixCampaign, FixCampaignResponse


class TestCampaign(unittest.TestCase):
    def test_launch_requires_window(self):
        src = inspect.getsource(FixCampaign.action_launch)
        self.assertIn("runs between dates", src)
        self.assertIn("inverted", src)

    def test_pause_resume_discipline(self):
        self.assertIn("RUNNING", inspect.getsource(FixCampaign.action_pause))
        self.assertIn("PAUSED", inspect.getsource(FixCampaign.action_resume))

    def test_attribution_ledger_events(self):
        self.assertIn("campaign.response", inspect.getsource(FixCampaignResponse))

    def test_cost_per_response_measurable(self):
        src = inspect.getsource(FixCampaign._compute_response_count)
        self.assertIn("cost_per_response", src)

    def test_m10_loyalty_hook_consumption(self):
        src = inspect.getsource(FixCampaign.action_trigger_loyalty_hook)
        self.assertIn("fix.loyalty.campaign.hook", src)
        self.assertIn("campaign.loyalty_rewards_disbursed", src)
        self.assertIn("enrolled_loyalty", src)

    def test_audience_segmentation_and_pdpa_consent(self):
        for field_name in ("target_audience_type", "pdpa_consent_verified", "utm_campaign"):
            self.assertTrue(
                hasattr(FixCampaign, field_name)
                or field_name in getattr(FixCampaign, "_fields", {}),
                f"Field {field_name} missing on FixCampaign",
            )


if __name__ == "__main__":
    unittest.main()
