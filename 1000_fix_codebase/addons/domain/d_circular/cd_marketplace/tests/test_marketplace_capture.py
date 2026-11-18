"""M12 capture audit, second pass (19 Nov 2026): the records four pages lacked.

Exercised as the people who use them (operator, a second operator, a plain
user, the seller's own portal account):

  * Job Broadcast: no seller quotes on a service job until the customer's
    consent to an external seller is recorded (FR-MKP-037, BRU-MKP-07);
  * Execution Oversight: a job completes only with the evidence an owned job
    needs (FR-MKP-040/042, BRU-MKP-02), captured while it is in progress;
  * Ratings: the customer's review of a signed-off job, moderated by another
    operator, with one seller response; a published review's rating is the
    job's rating in the measured score (FR-MKP-049/050);
  * Trust & Safety: a counterfeit-part report suspends the listing at once;
    a substantiated counterfeit or fraud finding suspends the seller; another
    operator decides it (FR-MKP-064..066, BRU-MKP-11);
  * Seller Registration: KYC is verified only with the identity documents of
    the seller's type (FR-MKP-001/003).
"""

import base64
import types
from contextlib import contextmanager

import pytest
from odoo import Command
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, AccessError, ValidationError)
OPERATOR = "cd_marketplace.group_marketplace_operator"
COMPLIANCE = "cd_marketplace.group_marketplace_compliance"
SELLER_PORTAL = "cd_marketplace.group_fix_marketplace_seller"
ORDER = "fix.marketplace.order"
QUOTE = "fix.seller.quote"
EVIDENCE = "fix.marketplace.job.evidence"
REVIEW = "fix.seller.review"
SIGNAL = "fix.trust.signal"
PNG = base64.b64encode(b"\x89PNG evidence")


@contextmanager
def _refused(env, exc=REFUSED, match=None):
    with pytest.raises(exc, match=match) as info, env.cr.savepoint():
        yield info
    env.invalidate_all()


@pytest.fixture
def mc(odoo_env):
    env = odoo_env
    users = env["res.users"].with_context(no_reset_password=True)

    def user(login, *groups):
        return users.create(
            {
                "name": login.replace("_", " ").title(),
                "login": login,
                "group_ids": [Command.set([env.ref(g).id for g in groups])],
            }
        )

    x = types.SimpleNamespace(env=env)
    x.plain = user("mc_plain", "base.group_user")
    x.operator = user("mc_operator", "base.group_user", OPERATOR)
    x.operator2 = user("mc_operator_two", "base.group_user", OPERATOR)
    x.compliance = user("mc_compliance", "base.group_user", COMPLIANCE)
    x.seller_user = user("mc_seller", SELLER_PORTAL)
    x.category = env["product.category"].create({"name": "MC Screen Repair"})
    x.seller = (
        env["fix.marketplace.seller"]
        .sudo()
        .create(
            {
                "name": "MC Shop",
                "partner_id": x.seller_user.partner_id.id,
                "category_ids": [Command.set(x.category.ids)],
                "kyc_status": "verified",
                "cfo_approved": True,
            }
        )
    )
    x.listing = (
        env["fix.marketplace.listing"]
        .sudo()
        .create(
            {
                "name": "MC Display Swap",
                "seller_id": x.seller.id,
                "category_id": x.category.id,
                "state": "active",
            }
        )
    )
    x.customer = env["res.partner"].create({"name": "MC Customer"})

    def order(consent=True, **vals):
        base = {
            "customer_id": x.customer.id,
            "category_id": x.category.id,
            "description": "MC cracked display",
        }
        if consent:
            base.update({"customer_consent": True, "consent_method": "otp"})
        base.update(vals)
        return env[ORDER].with_user(x.operator).create(base)

    def in_progress():
        o = order()
        q = (
            env[QUOTE]
            .sudo()
            .create(
                {"marketplace_order_id": o.id, "seller_id": x.seller.id, "quoted_price": 4000.0}
            )
        )
        q.with_user(x.operator).action_select()
        o.with_user(x.operator).action_start_job()
        return o

    def evidence(o, kind, user=None, **vals):
        return (
            env[EVIDENCE]
            .with_user(user or x.operator)
            .create({"order_id": o.id, "artefact_type": kind, **vals})
        )

    def full_evidence(o):
        evidence(o, "before_photo", evidence_file=PNG, evidence_filename="b.png")
        evidence(o, "after_photo", evidence_file=PNG, evidence_filename="a.png")
        evidence(o, "qc_checklist", qc_passed=True, note="All checks passed")
        evidence(o, "parts_declaration", provenance="genuine", part_description="OEM display")

    def signed_off(rating=None):
        o = in_progress()
        full_evidence(o)
        as_op = o.with_user(x.operator)
        as_op.action_complete()
        as_op.action_review(rating=rating)
        return o

    x.order, x.in_progress, x.evidence = order, in_progress, evidence
    x.full_evidence, x.signed_off = full_evidence, signed_off
    return x


# ------------------------------------------------------------- consent


def test_no_quote_without_the_customers_consent(mc):
    o = mc.order(consent=False)
    with _refused(mc.env, UserError, "BRU-MKP-07"):
        mc.env[QUOTE].sudo().create(
            {"marketplace_order_id": o.id, "seller_id": mc.seller.id, "quoted_price": 1.0}
        )
    o.with_user(mc.operator).write({"customer_consent": True, "consent_method": "signed"})
    assert o.consent_at and o.consent_by_id == mc.operator
    mc.env[QUOTE].sudo().create(
        {"marketplace_order_id": o.id, "seller_id": mc.seller.id, "quoted_price": 1.0}
    )


def test_consent_needs_how_it_was_taken(mc):
    with _refused(mc.env, UserError, "how the customer's consent"):
        mc.order(consent=False, customer_consent=True)


def test_consent_is_pinned_once_quotes_arrive(mc):
    o = mc.in_progress()
    with _refused(mc.env, UserError, "pinned"):
        o.with_user(mc.operator).write({"customer_consent": False})
    # the workspace re-posts unchanged values on save: that is not a change
    o.with_user(mc.operator).write({"customer_consent": True, "consent_method": "otp"})


def test_a_refurb_resale_needs_no_consent(mc):
    o = mc.order(consent=False, order_type="refurb_resale")
    mc.env[QUOTE].sudo().create(
        {"marketplace_order_id": o.id, "seller_id": mc.seller.id, "quoted_price": 1.0}
    )


# ------------------------------------------------------------- evidence


def test_a_job_does_not_complete_without_its_evidence(mc):
    o = mc.in_progress()
    with _refused(mc.env, UserError, "BRU-MKP-02"):
        o.with_user(mc.operator).action_complete()
    mc.evidence(o, "before_photo", evidence_file=PNG)
    mc.evidence(o, "after_photo")  # no file: recorded but not compliant
    mc.evidence(o, "qc_checklist", qc_passed=False, note="Touch dead zone")
    mc.evidence(o, "parts_declaration", provenance="genuine")  # no part named
    with _refused(mc.env, UserError, "After Photograph, QC Checklist, Parts Used"):
        o.with_user(mc.operator).action_complete()
    mc.full_evidence(o)
    o.with_user(mc.operator).action_complete()
    assert o.state == "completed"


def test_no_parts_used_is_a_valid_declaration(mc):
    o = mc.in_progress()
    rec = mc.evidence(o, "parts_declaration", provenance="none")
    assert rec.compliant and rec.captured_by_id == mc.operator and rec.name.startswith("JEV/")
    assert rec.seller_id == mc.seller


def test_evidence_is_captured_while_the_job_runs_and_then_pinned(mc):
    o = mc.order()
    with _refused(mc.env, UserError, "in progress"):
        mc.evidence(o, "before_photo", evidence_file=PNG)
    o = mc.in_progress()
    mc.full_evidence(o)
    o.with_user(mc.operator).action_complete()
    rec = o.evidence_ids[:1]
    with _refused(mc.env, UserError, "in progress"):
        rec.with_user(mc.operator).write({"note": "edited later"})
    with _refused(mc.env):
        rec.with_user(mc.operator).unlink()


def test_a_plain_user_captures_no_evidence(mc):
    o = mc.in_progress()
    with _refused(mc.env):
        mc.evidence(o, "before_photo", user=mc.plain, evidence_file=PNG)


def test_completion_evidence_is_configurable(mc):
    mc.env["ir.config_parameter"].sudo().set_param(
        "cd_marketplace.completion_evidence", "diagnostic"
    )
    o = mc.in_progress()
    mc.evidence(o, "diagnostic", note="Display connector reseated")
    o.with_user(mc.operator).action_complete()
    assert o.state == "completed"


# ------------------------------------------------------------- reviews


def _review(mc, o, user=None, **vals):
    base = {"order_id": o.id, "rating_overall": 4, "review_text": "Quick and tidy."}
    base.update(vals)
    return mc.env[REVIEW].with_user(user or mc.operator).create(base)


def test_a_review_is_of_a_signed_off_job(mc):
    o = mc.in_progress()
    with _refused(mc.env, UserError, "verified job"):
        _review(mc, o)
    o = mc.signed_off(rating=3)
    rev = _review(mc, o, rating_workmanship=5, rating_timeliness=3)
    assert rev.state == "submitted" and rev.seller_id == mc.seller
    assert rev.customer_id == mc.customer and rev.name.startswith("SRV/")
    with _refused(mc.env, UserError, "already has"):
        _review(mc, o)


@pytest.mark.parametrize(
    "bad",
    [{"rating_overall": 0}, {"rating_overall": 6}, {"rating_value": 9}, {"rating_timeliness": -1}],
)
def test_ratings_are_one_to_five(mc, bad):
    o = mc.signed_off()
    with _refused(mc.env, ValidationError, "1 to 5"):
        _review(mc, o, **bad)


def test_another_operator_moderates(mc):
    o = mc.signed_off()
    rev = _review(mc, o)
    with _refused(mc.env, UserError, "Segregation"):
        rev.with_user(mc.operator).action_publish()
    with _refused(mc.env):
        rev.with_user(mc.plain).action_publish()
    rev.with_user(mc.operator2).action_publish()
    assert rev.state == "published" and rev.moderated_by_id == mc.operator2
    with _refused(mc.env, UserError, "pinned"):
        rev.with_user(mc.operator).write({"rating_overall": 5})


def test_a_rejection_needs_its_policy_reason(mc):
    rev = _review(mc, mc.signed_off())
    with _refused(mc.env, UserError, "policy reason"):
        rev.with_user(mc.operator2).action_reject(note=" ")
    rev.with_user(mc.operator2).action_reject(note="Contains a phone number")
    assert rev.state == "rejected"


def test_the_seller_responds_once(mc):
    rev = _review(mc, mc.signed_off())
    with _refused(mc.env, UserError, "published"):
        rev.with_user(mc.operator).action_record_response(response="Thanks")
    rev.with_user(mc.operator2).action_publish()
    rev.with_user(mc.seller_user).action_record_response(response="Thank you!")
    assert rev.seller_response == "Thank you!" and rev.response_at
    with _refused(mc.env, UserError, "already responded"):
        rev.with_user(mc.operator).action_record_response(response="Again")


def test_the_seller_reads_only_published_reviews_of_their_work(mc):
    o = mc.signed_off()
    rev = _review(mc, o)
    Review = mc.env[REVIEW].with_user(mc.seller_user)
    assert not Review.search([("id", "=", rev.id)])
    rev.with_user(mc.operator2).action_publish()
    assert Review.search([("id", "=", rev.id)]) == rev


def test_a_published_review_rates_the_job_in_the_score(mc):
    o = mc.signed_off(rating=2)
    assert o._fix_job_rating() == 2
    rev = _review(mc, o, rating_overall=5)
    assert o._fix_job_rating() == 2  # awaiting moderation: not yet
    rev.with_user(mc.operator2).action_publish()
    o.invalidate_recordset()
    assert o._fix_job_rating() == 5


# ------------------------------------------------------------- trust & safety


def _report(mc, user=None, **vals):
    base = {
        "seller_id": mc.seller.id,
        "signal_type": "counterfeit_part",
        "source": "customer",
        "listing_id": mc.listing.id,
        "description": "Customer reports a non-genuine display on a listed swap.",
    }
    base.update(vals)
    return mc.env[SIGNAL].with_user(user or mc.operator).create(base)


def test_a_counterfeit_report_suspends_the_listing_at_once(mc):
    rep = _report(mc)
    assert rep.name.startswith("TSR/") and rep.reported_by_id == mc.operator
    assert mc.listing.state == "paused" and rep.listing_paused


def test_other_concerns_leave_the_listing_live(mc):
    rep = _report(mc, signal_type="off_platform")
    assert mc.listing.state == "active" and not rep.listing_paused


def test_a_substantiated_counterfeit_finding_suspends_the_seller(mc):
    rep = _report(mc)
    rep.with_user(mc.operator).action_investigate()
    with _refused(mc.env, UserError, "Segregation"):
        rep.with_user(mc.operator).action_substantiate(finding="Part is a copy")
    rep.with_user(mc.operator2).action_substantiate(finding="Lab confirms a copy")
    assert rep.state == "substantiated" and rep.decided_by_id == mc.operator2
    cq = rep.consequence_id
    assert cq.consequence_type == "suspension" and cq.state == "active"
    assert cq.trigger == "counterfeit" and cq.imposed_by_id == mc.operator2
    assert mc.seller._active_suspension() == cq
    # the suspension blocks quoting (BRU-MKP-11)
    o = mc.order()
    with _refused(mc.env, UserError, "suspended"):
        mc.env[QUOTE].with_user(mc.operator).create(
            {"marketplace_order_id": o.id, "seller_id": mc.seller.id, "quoted_price": 9.0}
        )


def test_an_off_platform_finding_imposes_no_suspension(mc):
    rep = _report(mc, signal_type="off_platform", listing_id=False)
    rep.with_user(mc.operator).action_investigate()
    rep.with_user(mc.operator2).action_substantiate(finding="Contact exchange confirmed")
    assert not rep.consequence_id and not mc.seller._active_suspension()


def test_a_dismissed_report_puts_the_listing_back(mc):
    rep = _report(mc)
    rep.with_user(mc.operator).action_investigate()
    with _refused(mc.env, UserError, "finding"):
        rep.with_user(mc.operator2).action_dismiss(finding="")
    rep.with_user(mc.operator2).action_dismiss(finding="Part is genuine (invoice seen)")
    assert rep.state == "dismissed" and mc.listing.state == "active"


def test_a_report_is_decided_after_investigation_and_then_pinned(mc):
    rep = _report(mc)
    with _refused(mc.env, UserError, "after its investigation"):
        rep.with_user(mc.operator2).action_dismiss(finding="x")
    rep.with_user(mc.operator).action_investigate()
    with _refused(mc.env, UserError, "pinned"):
        rep.with_user(mc.operator).write({"signal_type": "other"})


def test_the_listing_must_be_the_sellers(mc):
    other = (
        mc.env["fix.marketplace.seller"]
        .sudo()
        .create({"name": "Other Shop", "partner_id": mc.customer.id})
    )
    with _refused(mc.env, ValidationError, "another seller"):
        _report(mc, seller_id=other.id)


def test_trust_reports_are_hidden_from_the_seller_and_plain_users_record_none(mc):
    rep = _report(mc, signal_type="payment_fraud", listing_id=False)
    with _refused(mc.env, AccessError):
        mc.env[SIGNAL].with_user(mc.seller_user).search([("id", "=", rep.id)])
    with _refused(mc.env):
        _report(mc, user=mc.plain)


# ------------------------------------------------------------- seller type


def test_kyc_verification_needs_the_types_identity(mc):
    Seller = mc.env["fix.marketplace.seller"].sudo()
    shop = Seller.create(
        {"name": "MC New Shop", "partner_id": mc.env["res.partner"].create({"name": "S"}).id}
    )
    assert shop.seller_type == "business"
    shop.with_user(mc.operator).action_submit_kyc(trade_license_no="TL-9")
    with _refused(mc.env, UserError, "e-TIN"):
        shop.with_user(mc.compliance).action_verify_kyc()
    shop.write({"tin_number": "123456789012"})
    shop.with_user(mc.compliance).action_verify_kyc()
    assert shop.kyc_status == "verified"
    solo = Seller.create(
        {
            "name": "MC Engineer",
            "seller_type": "individual",
            "partner_id": mc.env["res.partner"].create({"name": "E"}).id,
        }
    )
    solo.with_user(mc.operator).action_submit_kyc()
    with _refused(mc.env, UserError, "National ID"):
        solo.with_user(mc.compliance).action_verify_kyc()


# ------------------------------------------------------------- deployment


def test_the_wiring_is_installed(mc):
    env = mc.env
    for code in (EVIDENCE, REVIEW, SIGNAL):
        assert env["ir.sequence"].sudo().search_count([("code", "=", code)]) == 1, code
        model = env["ir.model"]._get(code)
        assert env["ir.model.access"].sudo().search_count([("model_id", "=", model.id)]) >= 2
        assert env["ir.rule"].sudo().search_count([("model_id", "=", model.id)]) >= 2
    param = env["ir.config_parameter"].sudo().get_param("cd_marketplace.completion_evidence")
    assert "before_photo" in (param or "")
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g

    for code in (EVIDENCE, REVIEW, SIGNAL):
        assert code in g.SURFACES, code
