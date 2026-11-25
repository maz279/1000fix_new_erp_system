# cd_gl_ext — tamper-evident hash chain on the posting log (M19-F11, FR-FIN-041, T-13).
#
# A08 audit M19-F11: fix.journal.posting.log was immutable only by ORM guard
# (write/unlink refused without force_edit) — there was no chain hash, so a
# database-level or force_edit alteration left no trace. Every log row now
# carries a per-company chain:
#
#   chain_hash = sha256(prev_chain_hash || "|" || canonical_json(row))
#
# Rows are chained in POSTING order (chain_seq 1, 2, ...), not insertion order:
# a manual journal is logged "requested" when drafted and only becomes part of
# the evidence chain when it is posted. The company's chain head
# (fix.journal.chain.head) is locked with SELECT ... FOR UPDATE (and a
# transaction advisory lock while the head row is first created), so two
# concurrent postings in the same company cannot read the same predecessor and
# fork the chain.
#
# GENESIS AT DEPLOYMENT: this build does not migrate existing rows. Log rows
# written before it carry no chain_hash and are outside the chain; verify_chain
# starts at chain_seq = 1, whose prev_chain_hash is CHAIN_GENESIS. The head row
# records the id of the last legacy log row (genesis_log_id) and the moment the
# chain started (genesis_at), so the boundary is documented in the data itself.
from __future__ import annotations

import hashlib
import json
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# The documented genesis constant. It is not a hash of anything: it marks the
# start of the chain at deployment (see the module docstring).
CHAIN_GENESIS = "0" * 64
# Advisory-lock namespace for "fix.journal.posting.log chain head" (any int4).
CHAIN_LOCK_NAMESPACE = 190042

CHAIN_RULE = "FR-FIN-041 / T-13 (M19-F11)"


class FixJournalChainHead(models.Model):
    """One row per company: the tail of that company's posting-log chain.

    The row is the serialisation point of concurrent postings. ``last_hash``
    is the chain_hash of ``last_log_id``; ``log_count`` is also the next
    chain_seq. ``genesis_log_id`` / ``genesis_at`` mark the deployment
    boundary described in the module docstring."""

    _name = "fix.journal.chain.head"
    _description = "Posting Log Hash Chain Head"
    _order = "company_id"

    _company_unique = models.Constraint(
        "UNIQUE (company_id)", "One posting-log chain head per company"
    )

    company_id = fields.Many2one("res.company", required=True, index=True, ondelete="cascade")
    last_log_id = fields.Many2one(
        "fix.journal.posting.log", string="Last Chained Entry", ondelete="set null"
    )
    last_hash = fields.Char(string="Chain Head Hash", readonly=True)
    log_count = fields.Integer(string="Chained Entries", readonly=True, default=0)
    genesis_log_id = fields.Many2one(
        "fix.journal.posting.log",
        string="Genesis — Last Legacy Entry",
        readonly=True,
        help="The last posting-log row written before the chain existed; "
        "it and every earlier row are outside the chain (no migration).",
    )
    genesis_at = fields.Datetime(string="Genesis At", readonly=True)


def _canonical_row(record, seq: int) -> dict:
    """The canonical content hashed for one log row.

    Only fields of the audit record itself; chain fields are excluded (the
    hash cannot cover itself) and currency ids are stored as ids so the
    payload is stable across locales. ``amount`` is fixed at two places, the
    precision of the ledger it records."""
    return {
        "seq": int(seq),
        "id": record.id,
        "company_id": record.company_id.id or 0,
        "operating_unit_id": record.operating_unit_id.id or 0,
        "move_id": record.move_id.id or 0,
        "move_name": record.move_name or "",
        "source": record.source or "",
        "state": record.state or "",
        "requested_by": record.requested_by.id or 0,
        "posted_by": record.posted_by.id or 0,
        "posted_at": fields.Datetime.to_string(record.posted_at) if record.posted_at else "",
        "template_id": record.template_id.id or 0,
        "currency_id": record.currency_id.id or 0,
        "amount": "%.2f" % round(float(record.amount or 0.0), 2),
        "note": record.note or "",
        "source_ref": record.source_ref or "",
        "posting_rule_id": (
            record.posting_rule_id.id or 0 if "posting_rule_id" in record._fields else 0
        ),
    }


def _row_hash(record, seq: int, prev_hash: str) -> str:
    payload = json.dumps(_canonical_row(record, seq), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256((prev_hash + "|" + payload).encode("utf-8")).hexdigest()


def _lock_head(env, company_id):
    """Serialise on the company chain head and return (head, prev_hash, count).

    The advisory transaction lock covers the first-ever posting (when there is
    no head row to lock yet); every later posting also takes SELECT ... FOR
    UPDATE on the head row, exactly as the chain contract requires. Both locks
    end with the transaction."""
    cr = env.cr
    cr.execute("SELECT pg_advisory_xact_lock(%s, %s)", (CHAIN_LOCK_NAMESPACE, int(company_id)))
    Head = env["fix.journal.chain.head"].sudo()
    head = Head.search([("company_id", "=", company_id)], limit=1)
    if not head:
        legacy = (
            env["fix.journal.posting.log"]
            .sudo()
            .search([("company_id", "=", company_id)], order="id desc", limit=1)
        )
        head = Head.create(
            {
                "company_id": company_id,
                "genesis_log_id": legacy.id or False,
                "genesis_at": fields.Datetime.now(),
            }
        )
    # cr.execute() does not flush the ORM: the previous posting's head update
    # is still pending in the cache and the FOR UPDATE read would see log_count
    # 0 twice, forking the chain. Flush the head fields first.
    Head.flush_model(["last_log_id", "last_hash", "log_count"])
    cr.execute(
        "SELECT id, last_hash, log_count FROM fix_journal_chain_head WHERE id = %s FOR UPDATE",
        (head.id,),
    )
    locked = cr.fetchone()
    if not locked:
        raise UserError(
            "The posting-log chain head of company %s vanished while posting (%s)."
            % (company_id, CHAIN_RULE)
        )
    return head, (locked[1] or CHAIN_GENESIS), int(locked[2] or 0)


class FixJournalPostingLogChain(models.Model):
    """The posting log's hash chain (FR-FIN-041, M19-F11)."""

    _inherit = "fix.journal.posting.log"

    chain_seq = fields.Integer(
        string="Chain Sequence",
        readonly=True,
        copy=False,
        index=True,
        help="1-based position in the company's posting chain (posting order); "
        "0/empty for rows outside the chain (legacy rows, drafts never posted).",
    )
    prev_chain_hash = fields.Char(string="Previous Chain Hash", readonly=True, copy=False)
    chain_hash = fields.Char(string="Chain Hash", readonly=True, copy=False, index=True)

    # ------------------------------------------------------------------ chaining
    def _fix_chain_row(self):
        """Append this row to its company's chain and advance the head."""
        self.ensure_one()
        if self.chain_hash:
            return self.chain_hash
        head, prev_hash, count = _lock_head(self.env, self.company_id.id)
        seq = count + 1
        digest = _row_hash(self, seq, prev_hash)
        # force_edit: the chain fields are written by the engine, never by a person.
        self.with_context(force_edit=True).sudo().write(
            {"chain_seq": seq, "prev_chain_hash": prev_hash, "chain_hash": digest}
        )
        head.write({"last_log_id": self.id, "last_hash": digest, "log_count": seq})
        return digest

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            # A requested draft is not evidence yet; it is chained when its
            # approval posts it (write below). A posted row is final at create.
            if record.state == "posted":
                record._fix_chain_row()
        return records

    def write(self, vals):
        becoming_posted = vals.get("state") == "posted"
        result = super().write(vals)
        if becoming_posted:
            for record in self:
                if record.state == "posted" and not record.chain_hash:
                    record._fix_chain_row()
        return result


def _broken(company, record, reason, checked, expected_hash=None):
    return {
        "ok": False,
        "company": company.name,
        "company_id": company.id,
        "checked": checked,
        "head_hash": None,
        "broken_row_id": record.id if record else None,
        "broken": (
            {
                "row_id": record.id,
                "chain_seq": record.chain_seq,
                "reason": reason,
                "expected_hash": expected_hash,
                "stored_hash": record.chain_hash,
            }
            if record
            else {"row_id": None, "chain_seq": None, "reason": reason}
        ),
    }


def verify_chain(env, company):
    """Verify one company's posting-log chain; return the first broken row.

    Returns a dict: ``ok``, ``checked``, ``head_hash``, and when broken
    ``broken_row_id`` plus a ``broken`` detail (row id, chain_seq, reason,
    expected vs stored hash). The scan is ordered by chain_seq, so it detects
    a changed amount/field at the exact row, a deleted row (sequence gap or a
    predecessor mismatch), and a truncated tail (the head row disagrees).
    Rows without a chain_hash (legacy pre-deployment rows, drafts never
    posted) are outside the chain and are skipped.
    """
    if isinstance(company, int):
        company = env["res.company"].browse(company)
    Log = env["fix.journal.posting.log"].sudo()
    rows = Log.search(
        [("company_id", "=", company.id), ("chain_hash", "!=", False)],
        order="chain_seq asc, id asc",
    )
    prev_hash = CHAIN_GENESIS
    expected_seq = 1
    checked = 0
    for record in rows:
        checked += 1
        if record.chain_seq != expected_seq:
            return _broken(
                company,
                record,
                "chain sequence gap: expected %d, found %s" % (expected_seq, record.chain_seq or 0),
                checked,
            )
        if record.prev_chain_hash != prev_hash:
            return _broken(
                company,
                record,
                "previous hash mismatch: the row does not follow its predecessor",
                checked,
                expected_hash=prev_hash,
            )
        expected = _row_hash(record, record.chain_seq, prev_hash)
        if expected != record.chain_hash:
            return _broken(
                company,
                record,
                "row content changed after it was chained",
                checked,
                expected_hash=expected,
            )
        prev_hash = record.chain_hash
        expected_seq += 1

    head = env["fix.journal.chain.head"].sudo().search([("company_id", "=", company.id)], limit=1)
    if rows and not head:
        return _broken(
            company,
            rows[-1],
            "a chained posting exists but the company chain head is missing",
            checked,
        )
    if head:
        if head.log_count != len(rows):
            return _broken(
                company,
                head.last_log_id,
                "chain length mismatch: head counts %s, found %s chained rows"
                % (head.log_count, len(rows)),
                checked,
            )
        if (head.last_hash or CHAIN_GENESIS) != prev_hash:
            return _broken(
                company,
                head.last_log_id,
                "chain head hash mismatch: the tail of the chain is not the head",
                checked,
            )
    return {
        "ok": True,
        "company": company.name,
        "company_id": company.id,
        "checked": checked,
        "head_hash": prev_hash,
        "broken_row_id": None,
        "broken": None,
    }
