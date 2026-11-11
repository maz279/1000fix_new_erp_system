# Who may run the party cut-over loader (2026-11-10 authorization audit).
#
# The loader activates draft parties under sudo and stamps both registration
# tiers, and every internal user could create a batch and run it. Each attack
# runs as a NON-admin user holding only what that job holds; the proper path
# is then run by a registration administrator, also a non-superuser.
from __future__ import annotations

import base64
import io
import itertools
import uuid

import pytest
from odoo.exceptions import AccessError, UserError

U = uuid.uuid4().hex[:6].upper()
ADMIN = "cd_party_master.group_party_registration_admin"
LM = "cd_party_master.group_party_registration_lm"
STEWARD = "cd_party_master.group_party_data_steward"
CONTACTS = "base.group_partner_manager"
BATCH = "fix.party.import.batch"
REFUSED = (AccessError, UserError)
_SEQ = itertools.count(1)

HEADER = [
    "City",
    "Complete Name",
    "Country",
    "Email",
    "Phone",
    "Salesperson",
    "Address",
    "PAN",
    "CIN",
    "Customer Area",
]


def _workbook(tag, dealer=True) -> str:
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    ws.append(HEADER)
    if dealer:
        # a company-shaped name: a dealer, which opens a two-tier registration
        ws.append(["Dhaka", "AUTH TRADERS %s" % tag, "Bangladesh", "", "", "", "", "", "", ""])
    ws.append([None, "Mr Auth %s" % tag, None, None, None, None, None, None, None, None])
    buf = io.BytesIO()
    wb.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


def _user(env, *xmlids):
    n = next(_SEQ)
    groups = [env.ref("base.group_user").id] + [env.ref(x).id for x in xmlids]
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "M33 Import Probe %d" % n,
                "login": "m33.import.probe.%s.%d@a03.test" % (U.lower(), n),
                "group_ids": [(6, 0, groups)],
            }
        )
    )


def _vals(kind="customer", dealer=True):
    tag = "%s%d" % (U, next(_SEQ))
    return {
        "sheet_kind": kind,
        "import_ref": "AUTH-%s" % tag,
        "source_file": _workbook(tag, dealer),
        "source_filename": "authority_test.xlsx",
    }


def _batch_at(env, state, kind="customer", dealer=True):
    """A batch the cut-over loader (superuser) has brought to `state`."""
    batch = env[BATCH].create(_vals(kind, dealer))
    steps = ["action_stage", "action_validate", "action_import", "action_decide_registrations"]
    reached = ["staged", "validated", "imported", "approved"]
    for step, at in zip(steps, reached, strict=True):
        if batch.state == state:
            break
        getattr(batch, step)()
        assert batch.state == at
    assert batch.state == state
    return batch


@pytest.fixture
def env(odoo_env):
    return odoo_env


@pytest.fixture
def clerk(env):
    """A front-desk clerk: an internal user who maintains contacts."""
    return _user(env, CONTACTS)


@pytest.fixture
def admin(env):
    """The 1000FiX registration administrator, who also maintains contacts."""
    return _user(env, CONTACTS, ADMIN)


# ---------------------------------------------------------------- the decision
def test_a_clerk_cannot_decide_registrations(env, clerk):
    batch = _batch_at(env, "imported")
    partners = batch.line_ids.mapped("created_partner_id")
    assert set(partners.mapped("party_status")) == {"draft", "pending_approval"}
    with pytest.raises(AccessError, match="1000FiX Administrator"), env.cr.savepoint():
        batch.with_user(clerk).action_decide_registrations()
    env.invalidate_all()
    assert "active" not in partners.mapped("party_status")
    approval = partners.approval_ids
    assert (approval.lm_state, approval.admin_state) == ("pending", "pending")
    assert not approval.lm_decided_by and not approval.admin_decided_by
    assert batch.state == "imported"


@pytest.mark.parametrize("other_role", [LM, STEWARD])
def test_the_other_party_master_roles_do_not_decide_either(env, other_role):
    batch = _batch_at(env, "imported")
    user = _user(env, CONTACTS, other_role)
    with pytest.raises(AccessError, match="1000FiX Administrator"), env.cr.savepoint():
        batch.with_user(user).action_decide_registrations()


@pytest.mark.parametrize(
    "state,method",
    [
        ("validated", "action_import"),
        ("approved", "action_assign_roles"),
        ("imported", "action_rollback"),
    ],
)
def test_a_clerk_cannot_run_the_loader_steps(env, clerk, state, method):
    # individuals only, so nothing but the loader's own check stands in the way
    batch = _batch_at(env, state, dealer=False)
    created = batch.line_ids.mapped("created_partner_id")
    with pytest.raises(AccessError, match="1000FiX Administrator"), env.cr.savepoint():
        getattr(batch.with_user(clerk), method)()
    env.invalidate_all()
    assert batch.state == state
    assert batch.line_ids.mapped("created_partner_id") == created
    assert created.exists() == created


# --------------------------------------------------------------------- the ACL
def test_a_clerk_reads_batches_but_cannot_create_or_change_them(env, clerk):
    batch = _batch_at(env, "staged")
    Batch = env[BATCH].with_user(clerk)
    assert Batch.search([("id", "=", batch.id)]) == batch  # the list still opens
    assert Batch.browse(batch.id).line_ids  # and its lines
    with pytest.raises(AccessError), env.cr.savepoint():
        Batch.create(_vals())
    with pytest.raises(AccessError), env.cr.savepoint():
        batch.with_user(clerk).write({"import_ref": "HIJACK-%s" % U})
    with pytest.raises(AccessError), env.cr.savepoint():
        batch.line_ids[:1].with_user(clerk).write({"clean_name": "Hijacked"})
    with pytest.raises(AccessError), env.cr.savepoint():
        batch.with_user(clerk).unlink()
    # the steps that only write the batch and its lines stop on the same ACL
    for method in ("action_stage", "action_validate", "action_reconcile"):
        with pytest.raises(AccessError), env.cr.savepoint():
            getattr(batch.with_user(clerk), method)()


# ------------------------------------------------------------- the proper path
def test_a_registration_administrator_runs_the_whole_cutover(env, admin):
    batch = env[BATCH].with_user(admin).create(_vals())
    batch.action_stage()
    batch.action_validate()
    batch.action_import()
    batch.action_decide_registrations()
    batch.action_reconcile()
    assert batch.state == "reconciled"
    partners = batch.line_ids.mapped("created_partner_id")
    assert len(partners) == 2
    assert set(partners.mapped("party_status")) == {"active"}
    approval = partners.sudo().approval_ids
    assert (approval.lm_state, approval.admin_state) == ("approved", "approved")
    assert approval.admin_decided_by == admin
    roles = env["fix.party.role"].search([("partner_id", "in", partners.ids)])
    assert set(roles.mapped("role_type")) == {"customer"} and len(roles) == 2


def test_a_registration_administrator_can_roll_back(env, admin):
    # individuals only: removing a dealer's registration approval needs a
    # delete right no group holds, a limit of the rollback itself
    batch = _batch_at(env, "imported", dealer=False)
    partners = batch.line_ids.mapped("created_partner_id")
    assert len(partners) == 1
    batch.with_user(admin).action_rollback()
    assert batch.state == "validated" and not partners.exists()


def test_the_superuser_loader_is_still_trusted(env):
    # the cut-over scripts run as SUPERUSER_ID, with no group at all
    assert env.su
    batch = _batch_at(env, "approved")
    assert set(batch.line_ids.mapped("created_partner_id.party_status")) == {"active"}


# ------------------------------------------- the supplier-register extension
def test_a_clerk_cannot_register_suppliers_on_a_decided_vendor_batch(env, clerk):
    if not hasattr(env[BATCH], "action_register_suppliers"):
        pytest.skip("cd_vendor_portal is not installed")
    batch = _batch_at(env, "approved", kind="vendor")
    partners = batch.line_ids.mapped("created_partner_id")
    with pytest.raises(REFUSED), env.cr.savepoint():
        batch.with_user(clerk).action_register_suppliers()
    env.invalidate_all()
    assert not env["fix.supplier"].search_count([("partner_id", "in", partners.ids)])
