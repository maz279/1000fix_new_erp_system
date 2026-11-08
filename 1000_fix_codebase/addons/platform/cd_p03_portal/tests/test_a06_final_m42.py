# A06 final pass, M42 screens: the supplier bank-detail change had a served surface
# and no screen (M42-3 was unreachable). A steward proposes on the form, a second
# person confirms from the list, and the account number stays with the people the
# access rules allow. Also the document file and a CFO-only block, on the endpoints.
import base64
import itertools
from unittest import mock

import pytest
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.exceptions import AccessError

GS = "cd_vendor_portal.group_fix_supplier_steward"
GSA = "cd_vendor_portal.group_fix_supplier_approver"
T4 = "cd_entity_config.group_dofa_tier_4"
ACCOUNT = "20501234567890123"
_SEQ = itertools.count(1)


class FakeRequest:
    def __init__(self, env):
        self.env = env


@pytest.fixture
def p03(odoo_env):
    def call(user, route, **kw):
        with mock.patch.object(api, "request", FakeRequest(odoo_env(user=user.id))):
            return getattr(api.P03GenericApiController(), route)(**kw)

    return call


def _user(env, tag, *groups):
    n = next(_SEQ)
    ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A06 Final M42 %s %d" % (tag, n),
                "login": "a06.final.m42.%s.%d@a06.test" % (tag, n),
                "group_ids": [(6, 0, ids)],
            }
        )
    )


@pytest.fixture
def w(odoo_env):
    env = odoo_env
    x = type("World", (), {})()
    x.env = env
    x.plain = _user(env, "plain")
    x.ap = _user(env, "ap", "account.group_account_user")
    x.steward = _user(env, "steward", GS)
    x.steward2 = _user(env, "steward2", GS)
    x.approver = _user(env, "approver", GSA)
    x.cfo = _user(env, "cfo", T4)
    partner = env["res.partner"].create({"name": "A06 Final M42 Vendor", "is_company": True})
    x.supplier = env["fix.supplier"].create({"name": partner.name, "partner_id": partner.id})
    x.bank = env["res.bank"].create({"name": "A06 Final Bank"})
    return x


def propose_values(w, **kw):
    vals = {
        "supplier_id": w.supplier.id,
        "acc_number": ACCOUNT,
        "bank_id": w.bank.id,
        "routing_number": "123456789",
        "acc_holder_name": "A06 Final M42 Vendor",
        "verification_ref": "Called 0171 on file, spoke to finance head",
        "evidence_ref": "dms://bank/a06-final",
    }
    vals.update(kw)
    return vals


def write(p03, user, values, record_id=False):
    return p03(
        user, "model_write", model="fix.supplier.bank.change", record_id=record_id, values=values
    )


def act(p03, user, rec_id, method, **kwargs):
    return p03(
        user,
        "model_action",
        model="fix.supplier.bank.change",
        ids=[rec_id],
        method=method,
        kwargs=kwargs,
    )


COLS = ["name", "supplier_id", "acc_number_masked", "acc_number", "proposed_by_id", "state"]


def test_a2_the_whole_change_runs_on_the_screen(w, p03):
    out = write(p03, w.steward, propose_values(w))
    assert "error" not in out, out
    change = w.env["fix.supplier.bank.change"].browse(out["id"])
    assert change.state == "draft" and not w.supplier.payment_block

    done = act(p03, w.steward, change.id, "action_propose")
    assert done["success"], done
    assert change.state == "proposed" and change.proposed_by_id == w.steward
    assert w.supplier.payment_block and change.supplier_payment_block

    # the proposer does not confirm
    done = act(p03, w.steward, change.id, "action_confirm")
    assert not done["success"] and "Segregation of duties" in done["error"]
    assert w.supplier.payment_block

    done = act(p03, w.approver, change.id, "action_confirm")
    assert done["success"], done
    assert change.state == "confirmed" and change.confirmed_by_id == w.approver
    assert not w.supplier.payment_block
    assert w.supplier.bank_account_id.acc_number == ACCOUNT


def test_a2_a_rejection_needs_its_reason_and_lifts_the_block(w, p03):
    change_id = write(p03, w.steward, propose_values(w))["id"]
    act(p03, w.steward, change_id, "action_propose")
    done = act(p03, w.steward2, change_id, "action_reject")
    assert not done["success"] and "rejected" in done["error"]
    assert w.supplier.payment_block
    done = act(p03, w.steward2, change_id, "action_reject", reason="Call-back number not on file")
    assert done["success"], done
    change = w.env["fix.supplier.bank.change"].browse(change_id)
    assert change.state == "rejected" and not w.supplier.payment_block
    assert not w.supplier.bank_account_id


def test_a2_propose_needs_the_verification_and_the_evidence(w, p03):
    change_id = write(p03, w.steward, propose_values(w, verification_ref=False))["id"]
    done = act(p03, w.steward, change_id, "action_propose")
    assert not done["success"] and "call-back" in done["error"]


def test_a2_a_proposal_cannot_be_edited_or_its_state_typed(w, p03):
    change_id = write(p03, w.steward, propose_values(w))["id"]
    assert "error" in write(p03, w.steward, {"state": "confirmed"}, record_id=change_id)
    act(p03, w.steward, change_id, "action_propose")
    assert "error" in write(p03, w.steward, {"acc_number": "999"}, record_id=change_id)
    change = w.env["fix.supplier.bank.change"].browse(change_id)
    assert change.acc_number == ACCOUNT and change.state == "proposed"


@pytest.mark.parametrize("who", ["plain", "ap", "cfo"])
def test_a2_outside_the_stewards_and_approvers_the_account_is_not_readable(w, p03, who):
    change_id = write(p03, w.steward, propose_values(w))["id"]
    user = getattr(w, who)
    rows = p03(user, "model_records", model="fix.supplier.bank.change", cols=COLS)
    assert "error" in rows and "rows" not in rows
    with pytest.raises(AccessError):
        w.env["fix.supplier.bank.change"].with_user(user).browse(change_id).read(["acc_number"])
    form = p03(
        user,
        "model_form",
        model="fix.supplier.bank.change",
        fields=[{"name": "acc_number"}],
        record_id=change_id,
    )
    assert "error" in form and not form.get("record")
    assert ACCOUNT not in str(form)
    done = act(p03, user, change_id, "action_confirm")
    assert not done["success"]
    assert "error" in write(p03, user, propose_values(w))


def test_a2_the_list_masks_the_number_and_the_form_shows_it_to_a_steward(w, p03):
    change_id = write(p03, w.steward, propose_values(w))["id"]
    rows = p03(
        w.steward,
        "model_records",
        model="fix.supplier.bank.change",
        cols=["name", "acc_number_masked", "state"],
        domain=[["id", "=", change_id]],
    )
    masked = rows["rows"][0]["acc_number_masked"]
    assert masked.endswith("0123") and ACCOUNT not in masked and len(masked) == len(ACCOUNT)
    form = p03(
        w.approver,
        "model_form",
        model="fix.supplier.bank.change",
        fields=[{"name": "acc_number"}, {"name": "proposed_by_id", "readonly": True}],
        record_id=change_id,
    )
    assert form["record"]["acc_number"] == ACCOUNT


def test_b5_the_block_button_on_the_endpoint_is_the_cfos(w, p03):
    press = {"model": "fix.supplier", "ids": [w.supplier.id], "method": "action_block"}
    out = p03(w.steward, "model_action", kwargs={"reason": "Counterfeit batch"}, **press)
    assert not out["success"] and "Blocking a supplier needs" in out["error"]
    assert w.supplier.status == "prospect"
    out = p03(w.cfo, "model_action", kwargs={"reason": "Counterfeit batch"}, **press)
    assert out["success"], out
    assert w.supplier.status == "deactivated"


def test_b10_the_document_form_saves_and_serves_the_file(w, p03):
    pdf = base64.b64encode(b"%PDF-1.4 a06 final m42").decode()
    fields_ = [{"name": "number"}, {"name": "file", "type": "binary"}, {"name": "file_filename"}]
    out = p03(
        w.steward,
        "model_write",
        model="fix.supplier.document",
        record_id=False,
        values={
            "supplier_id": w.supplier.id,
            "doc_type": "tin",
            "number": "TIN-77",
            "file": "data:application/pdf;base64," + pdf,
            "file_filename": "tin.pdf",
        },
    )
    assert "error" not in out, out
    doc = w.env["fix.supplier.document"].browse(out["id"])
    form = p03(
        w.steward2, "model_form", model="fix.supplier.document", fields=fields_, record_id=doc.id
    )
    served = form["record"]["file"]
    served = served.decode() if isinstance(served, bytes) else served
    assert served == pdf and form["record"]["file_filename"] == "tin.pdf"
    done = p03(
        w.steward2,
        "model_action",
        model="fix.supplier.document",
        ids=[doc.id],
        method="action_verify",
        kwargs={},
    )
    assert done["success"], done
    # the form's save posts the file back as it was served: still verified
    back = p03(
        w.steward,
        "model_write",
        model="fix.supplier.document",
        record_id=doc.id,
        values={"number": "TIN-77", "file": served, "file_filename": "tin.pdf"},
    )
    assert "error" not in back, back
    assert doc.state == "valid"
