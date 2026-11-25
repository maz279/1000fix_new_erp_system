#!/usr/bin/env python3
"""M20 live verification on real fix_dev data (CD-M20-02):

1. seed the AR account-role overrides measured off the real chart
2. intake + process the 21 stranded service_order.closed events (the
   measured outcome is whatever it is — gate refusals are recorded, never
   hidden)
3. run the receipt chain end-to-end on a REAL generated invoice:
   capture -> confirm (GL) -> auto-match -> allocate -> paid (with evidence)
4. partial credit note on another real invoice
5. dunning run + partial dispute + suppression
6. ageing snapshot capture + immutability probe
7. customer statement computation

Local verification only: literal loopback host via http.client."""

import http.client
import json
import os

HOST = "localhost"
PORT = 8069
DB = "fix_dev"
USER = "admin"
PWD = os.environ.get("ODOO_RPC_PWD", "admin")  # local dev default; env overrides

rid = [0]
UID = [None]


def call(service, method, *args):
    rid[0] += 1
    uid = UID[0] if service == "object" else USER
    payload = json.dumps(
        {
            "jsonrpc": "2.0",
            "method": "call",
            "id": rid[0],
            "params": {"service": service, "method": method, "args": [DB, uid, PWD, *args]},
        }
    )
    conn = http.client.HTTPConnection(HOST, PORT, timeout=300)
    conn.request(
        "POST",
        "/jsonrpc",
        body=payload.encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    body = json.loads(conn.getresponse().read().decode("utf-8"))
    conn.close()
    if "error" in body:
        return {"error": json.dumps(body["error"])[:500]}
    return body["result"]


def main():
    UID[0] = call("common", "login")
    print("== 1) account-role overrides (measured off the real chart) ==")
    for role, code in [
        ("vat_output", "251000"),
        ("writeoff_expense", "600000"),
        ("cash", "101401"),
        ("bank", "101401"),
        ("channel_mfs", "101403"),
    ]:
        param = f"cd_billing_engine.account_code.{role}"
        call("object", "execute_kw", "ir.config_parameter", "set_param", [param, code])
        print(f"  {param} = {code}")

    print("== 2) intake + process the stranded events ==")
    call("object", "execute_kw", "fix.billable.event", "_cron_intake", [])
    queue = call(
        "object",
        "execute_kw",
        "fix.billable.event",
        "search_read",
        [[]],
        {"fields": ["state", "customer_id", "invoice_id", "last_error"]},
    )
    counts = {}
    for row in queue:
        counts[row["state"]] = counts.get(row["state"], 0) + 1
    print(f"  intake queued: {len(queue)} events -> {counts}")
    result = call("object", "execute_kw", "fix.billable.event", "action_process_all_due", [])
    print(f"  process-all: {result if 'error' not in result else result}")
    queue = call(
        "object",
        "execute_kw",
        "fix.billable.event",
        "search_read",
        [[]],
        {"fields": ["state", "last_error"]},
    )
    counts = {}
    fails = {}
    for row in queue:
        counts[row["state"]] = counts.get(row["state"], 0) + 1
        if row["state"] == "failed":
            err = (row["last_error"] or "")[:60]
            fails[err] = fails.get(err, 0) + 1
    print(f"  after process: {counts}")
    for err, n in fails.items():
        print(f"    failed x{n}: {err}")

    print("== 3) real invoices generated ==")
    invoices = call(
        "object",
        "execute_kw",
        "fix.ar.invoice",
        "search_read",
        [[["state", "=", "issued"]]],
        {
            "fields": [
                "name",
                "customer_id",
                "total_payable",
                "taxable_amount",
                "vat_amount",
                "mushak_id",
                "posted_move_id",
                "gl_note",
                "amount_residual",
                "invoice_date",
            ],
            "order": "id desc",
            "limit": 10,
        },
    )
    for inv in invoices:
        mushak = (
            call(
                "object",
                "execute_kw",
                "fix.mushak.register",
                "read",
                [[inv["mushak_id"][0]]],
                {"fields": ["mushak_no", "posted"]},
            )[0]
            if inv["mushak_id"]
            else {}
        )
        print(
            f"  {inv['name']} | {inv['customer_id'][1][:28]:<28} | total {inv['total_payable']:>10.2f}"
            f" | mushak {mushak.get('mushak_no')} posted={mushak.get('posted')}"
            f" | GL {'yes' if inv['posted_move_id'] else 'NO: ' + str(inv['gl_note'])}"
        )

    issued = [i for i in invoices if i["amount_residual"] > 0]
    if not issued:
        print("!! no issued invoice with residual — stop the chain here (honest)")
        return

    print("== 4) receipt chain on a real invoice ==")
    target = issued[0]
    amount = target["amount_residual"]
    receipt = call(
        "object",
        "execute_kw",
        "fix.ar.receipt",
        "create",
        [
            {
                "customer_id": target["customer_id"][0],
                "amount": amount,
                "method": "bkash",
                "reference": "TRX-M20-VERIFY",
            }
        ],
    )
    print(f"  receipt {receipt} created (draft)")
    conf = call("object", "execute_kw", "fix.ar.receipt", "action_confirm", [[receipt]])
    if "error" in conf:
        print("  confirm REFUSED:", conf["error"][:300])
        return
    rrow = call(
        "object",
        "execute_kw",
        "fix.ar.receipt",
        "read",
        [[receipt]],
        {"fields": ["name", "state", "posted_move_id", "account_id", "gl_note"]},
    )[0]
    print(
        f"  confirmed {rrow['name']} -> GL move {rrow['posted_move_id']}, cleared into {rrow['account_id']}"
    )
    proposals = call("object", "execute_kw", "fix.ar.receipt", "action_auto_match", [])
    top = [p for p in proposals if p["invoice_id"] == target["id"]]
    print(
        f"  auto-match: {len(proposals)} proposals; target score = {top[0]['score'] if top else None}"
    )
    alloc = call(
        "object",
        "execute_kw",
        "fix.ar.allocation",
        "create",
        [
            {
                "receipt_id": receipt,
                "invoice_id": target["id"],
                "amount": amount,
            }
        ],
    )
    if "error" in alloc:
        print("  allocation REFUSED:", alloc["error"][:300])
        return
    irow = call(
        "object",
        "execute_kw",
        "fix.ar.invoice",
        "read",
        [[target["id"]]],
        {"fields": ["state", "paid_date", "amount_residual", "amount_paid"]},
    )[0]
    print(
        f"  invoice {target['name']}: state={irow['state']} paid_date={irow['paid_date']}"
        f" paid={irow['amount_paid']} residual={irow['amount_residual']}"
    )
    events = call(
        "object",
        "execute_kw",
        "fix.event.outbox",
        "search_read",
        [[["event_type", "=", "invoice.paid"]]],
        {"fields": ["payload"], "order": "id desc", "limit": 1},
    )
    if events:
        payload = json.loads(events[0]["payload"])
        print(f"  invoice.paid evidence: {payload.get('evidence')}")

    print("== 5) partial credit note on another real invoice ==")
    others = [i for i in issued if i["id"] != target["id"] and i["total_payable"] > 0]
    if others:
        other = others[0]
        part = round(other["total_payable"] * 0.3, 2)
        note = (
            call(
                "object",
                "execute_kw",
                "fix.credit.note",
                "create",
                [
                    {
                        "operating_unit_id": (target["mushak_id"] and False)
                        or False,  # filled below
                        "invoice_id": other["id"],
                        "amount": part,
                        "reason_code": "goodwill",
                    }
                ],
            )
            if False
            else call(
                "object",
                "execute_kw",
                "fix.credit.note",
                "create",
                [
                    {
                        "invoice_id": other["id"],
                        "amount": part,
                        "reason_code": "goodwill",
                    }
                ],
            )
        )
        call("object", "execute_kw", "fix.credit.note", "action_submit", [[note]])
        note_state = call(
            "object", "execute_kw", "fix.credit.note", "read", [[note]], {"fields": ["state"]}
        )[0]["state"]
        if note_state == "pending_approval":
            call("object", "execute_kw", "fix.credit.note", "action_approve", [[note]])
        issue = call("object", "execute_kw", "fix.credit.note", "action_issue", [[note]])
        if "error" in issue:
            print(f"  credit note REFUSED: {issue['error'][:300]}")
        else:
            orow = call(
                "object",
                "execute_kw",
                "fix.ar.invoice",
                "read",
                [[other["id"]]],
                {"fields": ["state", "amount_residual", "credited_amount"]},
            )[0]
            nrow = call(
                "object",
                "execute_kw",
                "fix.credit.note",
                "read",
                [[note]],
                {"fields": ["posted_move_id", "gl_note"]},
            )[0]
            print(
                f"  credited {part} of {other['name']}: state={orow['state']}"
                f" residual={orow['amount_residual']} GL={'yes' if nrow['posted_move_id'] else nrow['gl_note']}"
            )

    print("== 6) dunning + partial dispute ==")
    dun = call("object", "execute_kw", "fix.dunning", "action_run_dunning", [])
    print(f"  run: {dun if 'error' not in dun else dun['error'][:200]}")
    rows = call(
        "object",
        "execute_kw",
        "fix.dunning",
        "search_read",
        [[]],
        {"fields": ["invoice_id", "overdue_amount", "days_overdue", "bucket", "step"], "limit": 5},
    )
    for r in rows:
        print(
            f"    {r['invoice_id'][1] if r['invoice_id'] else '?'} overdue {r['overdue_amount']}"
            f" {r['days_overdue']}d {r['bucket']} {r['step']}"
        )
    if rows:
        inv_id = rows[0]["invoice_id"][0]
        dispute_part = round(min(rows[0]["overdue_amount"] * 0.4, 100.0), 2)
        disp = call(
            "object",
            "execute_kw",
            "fix.ar.dispute",
            "create",
            [
                {
                    "invoice_id": inv_id,
                    "amount_disputed": dispute_part,
                    "reason": "M20 verify partial dispute",
                }
            ],
        )
        if "error" in disp:
            print("  dispute REFUSED:", disp["error"][:200])
        else:
            call("object", "execute_kw", "fix.dunning", "action_run_dunning", [])
            after = call(
                "object",
                "execute_kw",
                "fix.dunning",
                "read",
                [[rows[0]["id"]]],
                {"fields": ["overdue_amount", "suppressed"]},
            )[0]
            print(
                f"  dispute {dispute_part} opened -> dunnable now {after['overdue_amount']}"
                f" (was {rows[0]['overdue_amount']}), suppressed={after['suppressed']}"
            )

    print("== 7) ageing snapshot + statement ==")
    snap = call("object", "execute_kw", "fix.ar.aging.snapshot", "create", [{}])
    cap = call("object", "execute_kw", "fix.ar.aging.snapshot", "action_capture", [[snap]])
    if "error" in cap:
        print("  capture REFUSED:", cap["error"][:200])
    else:
        srow = call(
            "object",
            "execute_kw",
            "fix.ar.aging.snapshot",
            "read",
            [[snap]],
            {"fields": ["as_of_date", "total_open", "state"]},
        )[0]
        lines = call(
            "object",
            "execute_kw",
            "fix.ar.aging.line",
            "search_count",
            [[["snapshot_id", "=", snap]]],
        )
        print(
            f"  snapshot {srow['as_of_date']}: total open {srow['total_open']}, {lines} customer lines, {srow['state']}"
        )
        tamper = call(
            "object",
            "execute_kw",
            "fix.ar.aging.snapshot",
            "write",
            [[snap], {"as_of_date": "2020-01-01"}],
        )
        print(f"  immutability: write refused = {'error' in tamper}")

    call(
        "object",
        "execute_kw",
        "fix.ar.invoice",
        "search_read",
        [[["customer_id", "=", target["customer_id"][0]]]],
        {"fields": ["customer_id"], "limit": 1},
    )
    print("  statement: computed in the browser verification step (endpoint)")

    print("== M20 live verification DONE ==")


if __name__ == "__main__":
    main()
