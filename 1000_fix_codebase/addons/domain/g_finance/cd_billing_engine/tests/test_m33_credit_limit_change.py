# M33 capture audit pass 2 (2026-11-19): a credit limit changes only through
# an approved Credit Limit Change (M33 FR-CPM-047, BRU-CPM-12, SOD-04). Run as
# an accountant, a requester and two Finance Managers (Accounting
# Administrators), never as the superuser. Rolled back per test.
#
# A08 fix wave B7 (Nov 2026): M20-F7 — fix.credit.profile (credit limit,
# exposure, hold) is finance-only readable; SOD-08 — whoever created the
# customer record never decides its credit limit.
from pathlib import Path

import pytest
from odoo.exceptions import AccessError, UserError, ValidationError

ACCOUNTANT = "account.group_account_user"
MANAGER = "account.group_account_manager"
READONLY = "account.group_account_readonly"
MODULE = Path(__file__).resolve().parents[1]


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


# ----------------------------------------------- M20-F7: finance-only profiles
def test_the_acl_matrix_keeps_credit_profiles_finance_only():
    """The CSV contract itself (the estate's ir_model_access matrix idiom —
    module security data only reaches a database at upgrade time):
    base.group_user has NO line on fix.credit.profile any more; the
    accounting groups keep theirs, so the P03 finance screens stay working
    for finance roles."""
    csv_text = (MODULE / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
    lines = [line.strip().split(",") for line in csv_text.strip().splitlines() if line.strip()]
    header = lines[0]
    rows = [dict(zip(header, row, strict=False)) for row in lines[1:]]
    profile_rows = [r for r in rows if r["model_id:id"] == "model_fix_credit_profile"]
    assert profile_rows, "fix.credit.profile keeps accounting-group ACL lines"
    assert all(
        r["group_id:id"] != "base.group_user" for r in profile_rows
    ), "base.group_user (every internal user) must not read credit profiles"
    groups = {r["group_id:id"] for r in profile_rows}
    assert {
        "account.group_account_readonly",
        "account.group_account_user",
        "account.group_account_manager",
    } <= groups


def _drop_stale_base_user_read(env):
    """The shared test database carries module security data as of ITS build;
    the removed base.group_user line lands with the module's next upgrade.
    Apply the CSV's contract inside this rolled-back transaction (exactly
    what the upgrade does — the unlink clears Odoo's ACL caches), so the
    runtime behaviour below is the behaviour this tree ships. The matrix
    test above guards the CSV itself."""
    env["ir.model.access"].sudo().search(
        [
            ("model_id.model", "=", "fix.credit.profile"),
            ("group_id", "=", env.ref("base.group_user").id),
        ]
    ).unlink()


def test_credit_profiles_are_finance_only_readable(odoo_env, make_user):
    """M20-F7: an internal user without an accounting role cannot read
    fix.credit.profile (credit limit / exposure / hold are finance data,
    spec M20 §13); the accounting groups still can."""
    _drop_stale_base_user_read(odoo_env)
    plain = make_user("plain7")
    acct = make_user("a7", ACCOUNTANT)
    readonly = make_user("ro7", READONLY)
    profile = _profile(odoo_env, acct)
    assert profile.with_user(acct).credit_limit == 0.0
    assert profile.with_user(readonly).credit_hold is False
    with pytest.raises(AccessError):
        odoo_env["fix.credit.profile"].with_user(plain).search([("id", "=", profile.id)])
    with pytest.raises(AccessError):
        profile.with_user(plain).read(["credit_limit", "exposure", "hold_reason"])


def test_credit_profiles_stay_company_isolated(odoo_env, make_user):
    """The AS-03 company-isolation record rule generated for the model keeps
    holding now that read is group-scoped: a finance user of one company
    never sees another company's profiles."""
    acct = make_user("a8", ACCOUNTANT)
    other = odoo_env["res.company"].create({"name": "M20-F7 Other Co"})
    customer = odoo_env["res.partner"].create({"name": "M20-F7 other-co customer"})
    away = odoo_env["fix.credit.profile"].create(
        {"customer_id": customer.id, "company_id": other.id}
    )
    here = _profile(odoo_env, acct)
    visible = odoo_env["fix.credit.profile"].with_user(acct).search([])
    assert here in visible and away not in visible


def test_a_non_finance_requester_can_still_raise_the_ladder(odoo_env, make_user):
    """M20-F7 must not break the ladder itself: the limit snapshot the change
    row audits is taken by the trusted service, so a non-finance internal
    user can raise the change a Finance Manager then decides."""
    plain = make_user("p9")
    mgr = make_user("m9", MANAGER)
    customer = odoo_env["res.partner"].create({"name": "Plain requester's customer"})
    profile = odoo_env["fix.credit.profile"].sudo().create({"customer_id": customer.id})
    req = (
        odoo_env["fix.credit.limit.change"]
        .with_user(plain)
        .create({"profile_id": profile.id, "proposed_limit": 5000, "reason": "Branch asked"})
    )
    assert req.current_limit == 0 and req.requested_by == plain
    req.with_user(mgr).action_approve(note="Within policy")
    assert profile.sudo().credit_limit == 5000


# --------------------------------------------------- SOD-08: creator vs decider
def test_the_customer_creator_never_decides_their_limit(odoo_env, make_user):
    """SOD-08 (M20 §13 / M20-F8): the Finance Manager who CREATED the
    customer record never decides its credit limit; a manager who is
    neither the requester (SOD-04) nor the creator can."""
    acct = make_user("a10", ACCOUNTANT)
    maker = make_user("m10", MANAGER, "base.group_partner_manager")
    other = make_user("m10b", MANAGER)
    customer = odoo_env["res.partner"].with_user(maker).create({"name": "Maker's customer"})
    assert customer.create_uid == maker
    profile = odoo_env["fix.credit.profile"].with_user(acct).create({"customer_id": customer.id})
    req = (
        odoo_env["fix.credit.limit.change"]
        .with_user(acct)
        .create({"profile_id": profile.id, "proposed_limit": 20000, "reason": "Growth plan"})
    )
    _refused(odoo_env, UserError, "SOD-08", lambda: req.with_user(maker).action_approve())
    # the refusal left the request untouched for a different manager
    assert req.state == "submitted" and profile.credit_limit == 0
    req.with_user(other).action_approve(note="Checked references")
    assert req.state == "approved" and profile.credit_limit == 20000
