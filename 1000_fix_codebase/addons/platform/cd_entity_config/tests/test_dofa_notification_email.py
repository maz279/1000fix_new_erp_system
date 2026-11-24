# cd_entity_config — DOFA ruling notification emails (source-level, 2026-11-24).
#
# The Mailpit inbox showed one-line notifications with technical model names,
# no bands and no action. These checks pin the content contract of the email
# the proposer/countersigner receives.
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1]
SRC = (MODULE / "models" / "fix_dofa_threshold.py").read_text(encoding="utf-8")
CRONS = (MODULE / "data" / "fix_a12_crons.xml").read_text(encoding="utf-8")


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
        self.assertIn("html_sanitize(body)", SRC)

    def test_proposal_is_queued_as_a_note_not_emailed_per_ladder(self):
        self.assertIn("def _post_ruling_note(self, subject, intro_html)", SRC)
        self.assertIn('subtype_xmlid="mail.mt_note"', SRC)
        self.assertIn("rec._post_ruling_note(", SRC)
        self.assertIn('"notice_queued_at": fields.Datetime.now()', SRC)
        self.assertIn('"notice_sent_at": False', SRC)

    def test_digest_sends_one_mail_per_countersigner(self):
        self.assertIn("def cron_send_dofa_digest(self)", SRC)
        self.assertIn("pending.grouped(", SRC)
        self.assertIn("countersigned_by", SRC)
        self.assertIn("def _send_digest(self, counter, ladders)", SRC)
        self.assertIn('["mail.mail"]', SRC)
        self.assertIn('"email_to"', SRC)
        self.assertIn("counter.partner_id.email", SRC)
        self.assertIn("ladders.sudo().write(", SRC)

    def test_digest_lists_every_queued_ladder_with_a_link(self):
        self.assertIn("def _digest_body_html(self, ladders, counter)", SRC)
        self.assertIn("await your countersignature", SRC)
        self.assertIn("for ladder in ladders.sorted(", SRC)
        self.assertIn('"notice_queued_at"', SRC)
        self.assertIn('"notice_sent_at"', SRC)

    def test_digest_has_a_five_minute_cron(self):
        self.assertIn('id="ir_cron_dofa_ruling_digest"', CRONS)
        self.assertIn("model.cron_send_dofa_digest()", CRONS)
        self.assertIn('<field name="interval_number">5</field>', CRONS)
        self.assertIn('<field name="interval_type">minutes</field>', CRONS)

    def test_single_ruling_keeps_the_detailed_email(self):
        self.assertIn("def _send_single(self, counter, ladder)", SRC)
        self.assertIn("if len(ladders) == 1:", SRC)
        self.assertIn("self._send_single(counter, ladders)", SRC)

    def test_recipient_is_the_named_countersigner_only(self):
        self.assertIn('"email_to"', SRC)
        self.assertNotIn("recipient_ids", SRC)
        self.assertNotIn("partner_ids=counter.partner_id.ids", SRC)

    def test_sender_is_the_company_identity(self):
        self.assertIn("company = self.env.company", SRC)
        self.assertIn("email_from=sender", SRC)
        self.assertIn("company.email", SRC)


if __name__ == "__main__":
    unittest.main()
