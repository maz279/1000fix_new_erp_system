"""Shared test helpers: take a record through the M63 approval inbox.

Since the A03 audit's R7, routed approvals (campaign budget, complaint
concession, loyalty adjustment and scheme, discount request) are decided from
the approver's inbox, never by pressing Approve on the record. Suites that
exercise the DOFA rules behind those approvals go through here.
"""


def assigned(record):
    """Everyone the record's current request was routed to."""
    return record.approval_request_id.task_ids.mapped("assigned_user_id")


def inbox_task(record, approver):
    return record.approval_request_id.task_ids.filtered(
        lambda t: t.state == "pending" and t.assigned_user_id == approver
    )


def approve_via_inbox(record, approver, requester=None, justification=None, comment=None):
    """Request approval as `requester` (default: the record's creator) and
    decide it as `approver` from their inbox. Returns the deciding task."""
    requester = requester or record.create_uid
    if record.approval_state != "pending":
        record.with_user(requester).action_request_approval(justification=justification)
    task = inbox_task(record, approver)
    assert task, "%s received no inbox task for %s (routed to %s)" % (
        approver.name,
        record.display_name,
        ", ".join(assigned(record).mapped("name")),
    )
    task.with_user(approver).action_approve(comment=comment)
    return task
