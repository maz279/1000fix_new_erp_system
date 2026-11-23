# M57-F18 / decision D27 (owner, 2026-11-23): an out-of-band raise or
# promotion is no longer a hard refusal. The CFO tier approves an exception
# once, for a named employee and grade and up to a monthly gross; the band
# check then lets that contract or proposal through. The band itself is not
# changed, and the requester never approves their own exception.
import itertools

import pytest
from odoo.exceptions import UserError, ValidationError

_SEQ = itertools.count(1)
GRADE = "A09BX"


def _user(env, *groups):
    n = next(_SEQ)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A09 M57 Band %d" % n,
                "login": "a09-m57-band-%d@a09.test" % n,
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                ],
            }
        )
    )


def _decide(rec, requester, approver):
    rec.with_user(requester).action_request_approval()
    rec.invalidate_recordset()
    task = rec.approval_request_id.task_ids.filtered(
        lambda t: t.state == "pending" and t.assigned_user_id == approver
    )
    assert task, "no inbox task for %s; routed to %s" % (
        approver.name,
        rec.approval_request_id.task_ids.mapped("assigned_user_id.name"),
    )
    task.with_user(approver).action_approve()
    rec.invalidate_recordset()


def test_an_out_of_band_salary_needs_an_approved_cfo_exception(odoo_env):
    env = odoo_env
    Band = env["fix.compensation.band"]
    Band.sudo().create(
        {
            "name": "A09 band %s" % GRADE,
            "grade": GRADE,
            "range_min": 20000,
            "range_mid": 35000,
            "range_max": 50000,
        }
    )
    # the band still refuses the figure
    with pytest.raises(ValidationError, match="outside the"):
        Band._fix_check_amount(GRADE, 60000.0)
    employee = env["hr.employee"].create({"name": "A09 M57 Band Subject"})
    comp = _user(env, "cd_performance.group_compensation")
    cfo = _user(env, "cd_entity_config.group_dofa_tier_4")
    exc = (
        env["fix.band.exception"]
        .with_user(comp)
        .create(
            {
                "employee_id": employee.id,
                "grade": GRADE,
                "approved_monthly_gross": 60000.0,
                "reason": "Scarce RF technician, market rate above the band (D27)",
            }
        )
    )
    assert exc.state == "draft"
    # nothing decides it directly: the request is routed to the CFO tier
    with pytest.raises(UserError):
        exc.with_user(comp).action_approve()
    _decide(exc, comp, cfo)
    assert exc.state == "approved" and exc.approved_by_id == cfo
    # now the figure passes through the exception, and only up to its amount
    covering = env["fix.band.exception"].sudo()._fix_covering(employee, GRADE, 60000.0)
    assert covering == exc
    assert Band._fix_check_amount(GRADE, 60000.0, exception=covering) is True
    assert not env["fix.band.exception"].sudo()._fix_covering(employee, GRADE, 60001.0)
    assert not env["fix.band.exception"].sudo()._fix_covering(employee, "OTHER", 60000.0)
    # a withdrawn or unapproved exception covers nothing
    draft = (
        env["fix.band.exception"]
        .with_user(comp)
        .create(
            {
                "employee_id": employee.id,
                "grade": GRADE,
                "approved_monthly_gross": 60000.0,
                "reason": "draft only",
            }
        )
    )
    assert draft.state == "draft" and draft._fix_covers(60000.0, GRADE) is False
    draft.with_user(comp).action_cancel(reason="withdrawn before approval")
    assert draft.state == "cancelled" and draft._fix_covers(60000.0, GRADE) is False
