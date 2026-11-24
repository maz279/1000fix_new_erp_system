# cd_entity_config — DOFA ruling notification emails (source-level, 2026-11-24).
#
# The Mailpit inbox showed one-line notifications with technical model names,
# no bands and no action. These checks pin the content contract of the email
# the proposer/countersigner receives.
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1]
SRC = (MODULE / "models" / "fix_dofa_threshold.py").read_text(encoding="utf-8")


class TestEmailSurface(unittest.TestCase):
    def test_there_is_one_ruling_email_helper(self):
        self.assertIn("def _post_ruling_email(self, subject, intro_html, partner_ids=None)", SRC)
        self.assertIn('subtype_xmlid="mail.mt_comment"', SRC)
        self.assertIn("partner_ids=partner_ids or []", SRC)

    def test_subject_uses_the_human_model_label(self):
        self.assertIn("def _display_target(self)", SRC)
        self.assertIn("fix.dofa.ladder", SRC)
        self.assertIn("ir.model", SRC)
        self.assertIn('"Countersign required — %s DOFA ruling"', SRC)
        self.assertIn('"DOFA ruling in force — %s"', SRC)

    def test_bands_are_in_the_email(self):
        self.assertIn("def _ruling_bands_html(self)", SRC)
        self.assertIn("Amount (BDT)", SRC)
        self.assertIn("Authority</th>", SRC)
        self.assertIn("Above every bound", SRC)

    def test_email_has_a_deep_link_to_the_record(self):
        self.assertIn('get_param("web.base.url")', SRC)
        self.assertIn("/mail/view?model=fix.dofa.ladder&res_id=%s", SRC)
        self.assertIn("Open the ladder", SRC)

    def test_the_proposal_says_it_is_not_in_force(self):
        self.assertIn("This is not in force until", SRC)
        self.assertIn("countersigns", SRC)

    def test_user_supplied_text_is_escaped(self):
        self.assertIn("from xml.sax.saxutils import escape as xml_escape", SRC)
        self.assertIn("xml_escape(reference.strip())", SRC)
        self.assertIn("xml_escape(counter.name", SRC)

    def test_recipient_is_the_named_countersigner_only(self):
        self.assertIn("partner_ids=counter.partner_id.ids", SRC)

    def test_sender_is_the_company_identity(self):
        self.assertIn("company = self.env.company", SRC)
        self.assertIn("email_from=sender", SRC)
        self.assertIn("company.email", SRC)


if __name__ == "__main__":
    unittest.main()
