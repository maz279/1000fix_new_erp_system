# M33 capture audit pass 2 (2026-11-19): a credit limit changes only through
# an approved Credit Limit Change (M33 FR-CPM-047, BRU-CPM-12, SOD-04). Run as
# an accountant, a requester and two Finance Managers (Accounting
# Administrators), never as the superuser. Rolled back per test.
import pytest
from odoo.exceptions import UserError, ValidationError

ACCOUNTANT = "account.group_account_user"
MANAGER = "account.group_account_manager"


@pytest.fixture
def make_user(odoo_env):
    def _make(login, *groups):
        xmlids = ("base.group_user", *groups)
        return (
            odoo_env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Credit %s" % login,
                    "login": "m33clc-%s" % login,
                    "email": "%s@m33clc.invalid" % login,
                    "group_ids": [(6, 0, [odoo_env.ref(x).id for x in xmlids])],
                }
            )
        )

    return _make


def _refused(env, exc, match, fn):
    with pytest.raises(exc, match=match), env.cr.savepoint():
        fn()


def _profile(env, user):
    customer = env["res.partner"].create({"name": "CLC Customer"})
    return env["fix.credit.profile"].with_user(user).create({"customer_id": customer.id})


def test_a_limit_is_never_typed(odoo_env, make_user):
    acct = make_user("a1", ACCOUNTANT)
    customer = odoo_env["res.partner"].create({"name": "CLC Typed"})
    Profile = odoo_env["fix.credit.profile"].with_user(acct)
    _refused(
        odoo_env,
        UserError,
        "starts with no limit",
        lambda: Profile.create({"customer_id": customer.id, "credit_limit": 50000}),
    )
    profile = Profile.create({"customer_id": customer.id})
    _refused(odoo_env, UserError, "BRU-CPM-12", lambda: profile.write({"credit_limit": 1}))
    # the AR table posts the unchanged limit with new terms: that still saves
    profile.write({"credit_limit": 0.0, "payment_terms_days": 45})
    assert profile.payment_terms_days == 45 and profile.credit_limit == 0
    assert profile.display_name == "CLC Typed"


def test_another_finance_manager_approves_and_the_limit_applies(odoo_env, make_user):
    acct, mgr, mgr2 = (
        make_user("a2", ACCOUNTANT),
        make_user("m2", MANAGER),
        make_user("m2b", MANAGER),
    )
    profile = _profile(odoo_env, acct)
    Change = odoo_env["fix.credit.limit.change"]
    req = Change.with_user(mgr).create(
        {"profile_id": profile.id, "proposed_limit": 75000, "reason": "Two years clean payment"}
    )
    assert req.current_limit == 0 and req.requested_by == mgr and req.state == "submitted"
    _refused(
        odoo_env,
        UserError,
        "awaiting decision",
        lambda: Change.with_user(acct).create(
            {"profile_id": profile.id, "proposed_limit": 1, "reason": "dup"}
        ),
    )
    _refused(
        odoo_env, UserError, "workflow", lambda: req.with_user(mgr).write({"state": "approved"})
    )
    _refused(
        odoo_env, UserError, "group|role|Accounting", lambda: req.with_user(acct).action_approve()
    )
    _refused(odoo_env, UserError, "SOD-04", lambda: req.with_user(mgr).action_approve())
    req.with_user(mgr2).action_approve(note="Within policy")
    assert req.state == "approved" and req.decided_by == mgr2 and req.applied_at
    assert profile.credit_limit == 75000
    _refused(odoo_env, UserError, "already", lambda: req.with_user(mgr2).action_reject("late"))
    _refused(
        odoo_env,
        UserError,
        "decided limit change",
        lambda: req.with_user(mgr).write({"proposed_limit": 1}),
    )


def test_a_rejection_needs_a_reason_and_a_stale_request_is_not_applied(odoo_env, make_user):
    acct, mgr, mgr2 = (
        make_user("a3", ACCOUNTANT),
        make_user("m3", MANAGER),
        make_user("m3b", MANAGER),
    )
    profile = _profile(odoo_env, acct)
    Change = odoo_env["fix.credit.limit.change"]
    req = Change.with_user(acct).create(
        {"profile_id": profile.id, "proposed_limit": 10000, "reason": "New dealer"}
    )
    _refused(odoo_env, ValidationError, "why", lambda: req.with_user(mgr).action_reject(""))
    req.with_user(mgr).action_reject("No trade references")
    assert req.state == "rejected" and profile.credit_limit == 0

    same = Change.with_user(acct)
    _refused(
        odoo_env,
        ValidationError,
        "already in force",
        lambda: same.create({"profile_id": profile.id, "proposed_limit": 0, "reason": "noop"}),
    )
    stale = same.create({"profile_id": profile.id, "proposed_limit": 20000, "reason": "Second try"})
    # the limit moved underneath it (a migration, as the superuser)
    profile.sudo().write({"credit_limit": 5000})
    _refused(odoo_env, UserError, "changed since", lambda: stale.with_user(mgr2).action_approve())
    assert profile.credit_limit == 5000

    _refused(odoo_env, UserError, "requester", lambda: stale.with_user(mgr).action_cancel())
    stale.with_user(acct).action_cancel()
    assert stale.state == "cancelled"
