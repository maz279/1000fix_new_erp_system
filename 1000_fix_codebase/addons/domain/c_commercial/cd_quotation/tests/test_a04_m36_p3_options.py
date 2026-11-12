# ruff: noqa: F811  (the c fixture is imported from the M36 suite)
# Quote-to-cash P3 (13 Nov 2026): good / better / best options the customer
# chooses between, quotation templates per segment, the document language.
import pytest
from odoo.addons.cd_quotation.tests.test_a04_m36_controls import (  # noqa: F401
    _approved_quote,
    _estimate,
    _quote,
    _sent_quote,
    c,
)
from odoo.addons.cd_service_order.models import fix_otp_util
from odoo.exceptions import UserError


def _options(c, **kw):
    return _quote(
        c,
        line_ids=[
            (0, 0, {"description": "Call-out", "line_type": "callout", "unit_price": 1000.0}),
            (
                0,
                0,
                {
                    "description": "OEM panel",
                    "line_type": "part",
                    "unit_price": 3000.0,
                    "alternative_group": "Panel",
                    "is_selected": True,
                },
            ),
            (
                0,
                0,
                {
                    "description": "Compatible panel",
                    "line_type": "part",
                    "unit_price": 2000.0,
                    "alternative_group": "Panel",
                    "is_selected": False,
                },
            ),
            (
                0,
                0,
                {
                    "description": "Refurbished panel",
                    "line_type": "part",
                    "unit_price": 1500.0,
                    "alternative_group": "Panel",
                    "is_selected": False,
                },
            ),
        ],
        **kw,
    )


def test_only_the_chosen_option_is_priced(c):
    q = _options(c)
    assert q.value == 4000.0 and q.has_options
    q.with_user(c.author).action_choose_option(choice="Compatible panel")
    assert q.value == 3000.0
    assert q.line_ids.filtered("is_selected").mapped("description") == [
        "Call-out",
        "Compatible panel",
    ]
    with pytest.raises(UserError, match="Options:"), c.env.cr.savepoint():
        q.with_user(c.author).action_choose_option(choice="Gold panel")


def test_the_customer_switches_between_approved_options_up_to_acceptance(c, monkeypatch):
    q = _options(c)
    # the approval covers the dearest choice
    assert q._dofa_amount() == 4000.0
    q = _sent_quote(
        c,
        line_ids=[
            (0, 0, vals)
            for vals in [
                {"description": "Call-out", "line_type": "callout", "unit_price": 1000.0},
                {
                    "description": "OEM panel",
                    "line_type": "part",
                    "unit_price": 3000.0,
                    "alternative_group": "Panel",
                    "is_selected": True,
                },
                {
                    "description": "Refurbished panel",
                    "line_type": "part",
                    "unit_price": 1500.0,
                    "alternative_group": "Panel",
                    "is_selected": False,
                },
            ]
        ],
    )
    approved_by = q.dofa_approved_by
    q.with_user(c.author).action_choose_option(choice="Refurbished panel")
    assert (q.state, q.value, q.dofa_approved_by) == ("sent", 2500.0, approved_by)
    sent = []
    monkeypatch.setattr(
        fix_otp_util, "dispatch_otp", lambda phone, code, ttl, language="bn": sent.append(code)
    )
    q.with_user(c.author).action_send_acceptance_otp()
    q.with_user(c.author).action_verify_acceptance_otp(otp=sent[-1])
    assert (q.state, q.accepted_value) == ("accepted", 2500.0)
    with pytest.raises(UserError, match="final"), c.env.cr.savepoint():
        q.with_user(c.author).action_choose_option(choice="OEM panel")


def test_option_groups_must_be_a_real_single_choice(c):
    q = _options(c)
    q.line_ids.filtered(lambda r: r.description == "Compatible panel").with_context(
        fix_quote_option_choice=True
    ).write({"is_selected": True})
    with pytest.raises(UserError, match="exactly one chosen"), c.env.cr.savepoint():
        q.with_user(c.author).action_submit(justification="test")
    lonely = _quote(
        c,
        line_ids=[
            (0, 0, {"description": "Only one", "unit_price": 10.0, "alternative_group": "Solo"})
        ],
    )
    with pytest.raises(UserError, match="not a choice"), c.env.cr.savepoint():
        lonely.with_user(c.author).action_submit(justification="test")


def test_options_are_not_offered_on_an_estimate_quotation(c):
    est = _estimate(c)
    est.action_send()
    est.action_approve()
    q = (
        c.env["fix.quotation"]
        .with_user(c.author)
        .create(
            {
                "estimate_id": est.id,
                "cost_amount": 100.0,
                "payment_term_id": c.env.ref("account.account_payment_term_immediate").id,
            }
        )
    )
    q.line_ids[:1].with_user(c.author).write({"alternative_group": "X"})
    assert "prices the estimate" in " ".join(q._readiness_problems())


def test_a_template_gives_the_lines_terms_and_billing_plan(c):
    tpl = c.env.ref("cd_quotation.quote_template_corporate_project")
    acme = c.env["res.partner"].create({"name": "M36P3 Acme", "is_company": True})
    q = (
        c.env["fix.quotation"]
        .with_user(c.author)
        .create(
            {
                "customer_id": acme.id,
                "template_id": tpl.id,
                "cost_amount": 100.0,
                "operating_unit_id": c.ou.id,
            }
        )
    )
    assert (q.segment, q.quote_type, q.advance_pct) == ("corporate", "project", 50.0)
    assert q.payment_term_id == c.env.ref("cd_billing_engine.payment_term_bd_50_advance")
    assert "Installation and configuration" in q.line_ids.mapped("description")
    assert [(b.kind, b.pct) for b in q.billing_line_ids] == [
        ("on_delivery", 70.0),
        ("on_completion", 30.0),
    ]
    assert q.valid_until
    consumer = c.env.ref("cd_quotation.quote_template_consumer_onsite")
    q2 = _quote(c, quote_type="project")
    q2.with_user(c.author).write({"template_id": consumer.id})
    q2.with_user(c.author).action_apply_template()
    assert len(q2._option_groups()["part"]) == 3
    approved = _approved_quote(c)
    approved.with_user(c.author).write({"template_id": consumer.id})
    with pytest.raises(UserError, match="draft"), c.env.cr.savepoint():
        approved.with_user(c.author).action_apply_template()


def test_the_document_language_follows_the_customer(c):
    bn = c.env["res.lang"].with_context(active_test=False).search([("code", "=", "bn_BD")])
    if not bn.active:
        pytest.skip("Bangla is not installed in this database")
    customer = c.env["res.partner"].create({"name": "M36P3 Rahim", "lang": "bn_BD"})
    q = _quote(c, customer_id=customer.id)
    assert q.document_lang == "bn_BD"
    assert _quote(c).document_lang == "en_US"
    report = c.env.ref("cd_doc_suite.action_report_quotation", raise_if_not_found=False)
    if report:
        html = (
            c.env["ir.actions.report"]
            .sudo()
            ._render_qweb_html(report.report_name, q.ids)[0]
            .decode()
        )
        assert "মোট প্রদেয় (ভ্যাটসহ)" in html and "Total Payable (incl. VAT)" not in html
