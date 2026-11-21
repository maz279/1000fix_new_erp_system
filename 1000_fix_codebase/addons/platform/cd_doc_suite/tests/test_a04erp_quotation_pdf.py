# ruff: noqa: F811  (the c fixture is imported from the M36 suite)
# A04 ERP audit (21 Nov 2026) M36-F13: the quotation PDF printed the day the
# draft was created and none of the recorded terms and exclusions - the
# customer accepted a document that did not show what they were accepting.
import datetime

from odoo.addons.cd_quotation.tests.test_a04_m36_controls import (  # noqa: F401
    _quote,
    c,
)


def _meta(payload):
    return dict(payload["meta"])


def test_the_quotation_prints_its_issue_day_in_dhaka(c):
    q = _quote(c)
    assert "Date" in _meta(q._fix_print_payload())  # an unsent draft: its creation day
    # sent at 20:30 UTC on 20 Nov = 02:30 on 21 Nov in Dhaka
    q.sudo().write({"sent_at": datetime.datetime(2026, 11, 20, 20, 30)})
    meta = _meta(q._fix_print_payload())
    assert meta["Issue Date"] == "21-Nov-2026"
    assert "Date" not in meta


def test_the_quotation_prints_its_terms_but_not_an_unapproved_deviation(c):
    env = c.env
    q = _quote(c)
    std = (
        env["fix.quotation.standard.term"]
        .sudo()
        .create(
            {
                "code": "A04ERP-EXCL-1",
                "name": "Liquid damage",
                "term_type": "exclusion",
                "text_en": "Liquid and physical damage are excluded.",
                "text_bn": "তরল ও শারীরিক ক্ষতি অন্তর্ভুক্ত নয়।",
            }
        )
    )
    Term = env["fix.quotation.term"].sudo()
    Term.create(
        {
            "quotation_id": q.id,
            "standard_term_id": std.id,
            "term_type": "exclusion",
            "text_en": std.text_en,
            "text_bn": std.text_bn,
        }
    )
    Term.create(
        {
            "quotation_id": q.id,
            "term_type": "term",
            "text_en": "Payment within 90 days.",
            "deviation_reason": "large account",
        }
    )
    notes = q._fix_print_payload()["notes"]
    assert notes == ["Exclusion: Liquid and physical damage are excluded."]
    q.sudo().write({"document_lang": "bn_BD"})
    assert q._fix_print_payload()["notes"] == ["Exclusion: তরল ও শারীরিক ক্ষতি অন্তর্ভুক্ত নয়।"]
