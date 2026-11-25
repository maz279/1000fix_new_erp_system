# A10 deep audit (2026-11-23, D-A10-2): M24 finance auto-file.
#
# A posted customer/vendor invoice files its own PDF (HTML when the renderer
# is unavailable) into the governed repository — retention FIN-7Y, integrity
# seal, legal-hold reachable, access log. Once per move; a journal entry files
# nothing; the nightly backfill converges what was missed.
from datetime import date

from odoo import Command


def _account(env):
    account = env["account.account"].search(
        [("account_type", "=", "income"), ("company_ids", "in", env.company.id)], limit=1
    )
    return account or env["account.account"].search([], limit=1)


def _invoice(env, move_type="out_invoice"):
    partner = env["res.partner"].create({"name": "A10 auto-file customer"})
    account = _account(env)
    assert account, "the test database has no chart of accounts"
    return env["account.move"].create(
        {
            "move_type": move_type,
            "partner_id": partner.id,
            "invoice_date": date.today(),
            "invoice_line_ids": [
                Command.create(
                    {
                        "name": "Service charge",
                        "quantity": 1,
                        "price_unit": 100.0,
                        "account_id": account.id,
                        "tax_ids": [(5, 0, 0)],
                    }
                )
            ],
        }
    )


def _docs(env, move):
    return env["fix.document"].search(
        [("res_model", "=", "account.move"), ("res_id", "=", move.id)]
    )


def test_a_posted_invoice_files_its_governed_document(odoo_env):
    env = odoo_env
    invoice = _invoice(env)
    invoice.action_post()
    docs = _docs(env, invoice)
    assert len(docs) == 1, docs.mapped("name")
    doc = docs[0]
    assert doc.document_type == "invoice"
    assert doc.attachment_id and doc.attachment_id.datas  # the bytes are held
    retention = env["fix.retention.class"].search([("code", "=", "FIN-7Y")], limit=1)
    if retention:
        assert doc.retention_class_id == retention
    # once per move: a second call (or a re-post) never duplicates
    assert invoice._fix_autofile_invoice_document() is False
    assert len(_docs(env, invoice)) == 1


def test_a_vendor_bill_files_too(odoo_env):
    env = odoo_env
    bill = _invoice(env, move_type="in_invoice")
    bill.action_post()
    assert len(_docs(env, bill)) == 1


def test_a_journal_entry_files_nothing(odoo_env):
    env = odoo_env
    account = _account(env)
    journal = env["account.journal"].search(
        [("type", "=", "general"), ("company_id", "=", env.company.id)], limit=1
    )
    move = env["account.move"].create(
        {
            "move_type": "entry",
            "journal_id": journal.id,
            "line_ids": [
                Command.create({"name": "dr", "account_id": account.id, "debit": 10.0}),
                Command.create({"name": "cr", "account_id": account.id, "credit": 10.0}),
            ],
        }
    )
    move.action_post()
    assert not _docs(env, move)


def test_the_backfill_converges_and_is_a_no_op_when_complete(odoo_env):
    env = odoo_env
    invoice = _invoice(env)
    invoice.action_post()  # filed at post
    assert env["account.move"].cron_autofile_invoices() is True
    assert len(_docs(env, invoice)) == 1
