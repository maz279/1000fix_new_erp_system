"""A12 finish build: bring live M30 rows into line with the new controls.

Nothing here forges an approval. Each row is moved to the state its existing data
supports, with a chatter note saying why, or is listed in the log for a person.
Models of later modules are not in the registry yet, so this touches only this one.
"""

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

# Created by uid 1 on the live database, and no code reads them (E20).
DECORATIVE_FLAGS = ("fix.new_checkout", "fix.ai_dispatch_beta", "fix.bn_search_v2")
CLASS_WINDOWS = {
    "security": "24/7",
    "transactional": "24/7",
    "service": "08:00-21:00",
    "marketing": "10:00-20:00",
}
NOTE = "A12 finish migration: "


def _branch_lifecycle(cr):
    # E19: the new state column took its default on every row. Existing branches
    # are in use (live) or were archived (closed); none is being provisioned.
    cr.execute("UPDATE fix_branch SET state = CASE WHEN active THEN 'live' ELSE 'closed' END")


def _supersede_stale_ladders(env):
    # E4: live ladders 2 and 4 are not in force but carry a ruling stamp, which the
    # old code let one Tier 4 holder reuse. The stamp goes; chatter keeps it.
    Ladder = env["fix.dofa.ladder"].sudo()
    for ladder in Ladder.search([("in_force", "=", False), ("ruled_by", "!=", False)]):
        winner = Ladder.search(
            [
                ("target_model", "=", ladder.target_model),
                ("company_id", "=", ladder.company_id.id),
                ("in_force", "=", True),
            ],
            limit=1,
        )
        ladder.message_post(
            body=NOTE + "this ladder is not in force but carried the ruling stamp "
            "(ruled by %s, countersigner %s, authority '%s'). The reference and countersigner "
            "are cleared so they cannot be reused; re-ruling needs a new reference and a fresh "
            "countersignature."
            % (
                ladder.ruled_by.name,
                ladder.countersigned_by.name or "-",
                ladder.ruling_reference or "-",
            )
        )
        ladder._guarded().write(
            {
                "ruling_reference": False,
                "countersigned_by": False,
                "superseded_at": ladder.ruled_at,
                "superseded_by_id": winner.id or False,
            }
        )
    # B1: say plainly what the ladders still in force rest on.
    for ladder in Ladder.search([("in_force", "=", True), ("countersigned_at", "=", False)]):
        ladder.message_post(
            body=NOTE + "this ruling predates the countersign step: %s was named as "
            "countersigner, and the code did not require them to act. Countersigned At is "
            "therefore empty. Re-take the ruling with the real authority holders (B1)."
            % (ladder.countersigned_by.name or "nobody")
        )


def _delete_decorative_flags(env):
    Flag = env["fix.feature.flag"].sudo()
    flags = Flag.search([("key", "in", DECORATIVE_FLAGS)])
    if flags:
        _logger.info("A12 finish: deleting unwired feature flags %s", flags.mapped("key"))
        flags.unlink()


def _notification_windows(cr):
    # E20: the class decides the window (NT-003). SQL, because the constraint also
    # checks the marketing cap, which needs a person or the seed script.
    for consent_class, window in CLASS_WINDOWS.items():
        cr.execute(
            "UPDATE fix_notification_config SET send_window = %s "
            "WHERE consent_class = %s AND send_window IS DISTINCT FROM %s",
            (window, consent_class, window),
        )


def _null_company_branches(env):
    # E20 / BRU-ADM-05: a branch with no stored company is invisible to everyone.
    # Only when exactly one real entity exists is there a single right answer.
    Branch = env["fix.branch"].sudo().with_context(active_test=False)
    lost = Branch.search([("company_id", "=", False)])
    if not lost:
        return
    entities = (
        env["fix.entity"].sudo().search([]).filtered(lambda e: not e.code.startswith("SMOKE"))
    )
    if len(entities) != 1:
        _logger.warning(
            "A12 finish: %d branches have no company and there are %d real entities, so they "
            "are left for a person: %s",
            len(lost),
            len(entities),
            lost.mapped("code"),
        )
        return
    entity = entities
    taken = set(Branch.search([("entity_id", "=", entity.id)]).mapped("code"))
    clashes = lost.filtered(lambda b: b.code in taken)
    if clashes:
        _logger.warning(
            "A12 finish: branch codes already used in entity %s, left for a person: %s",
            entity.code,
            clashes.mapped("code"),
        )
    for branch in lost - clashes:
        branch._guarded().write({"entity_id": entity.id})
        branch.message_post(
            body=NOTE + "this branch had no stored company and %s is the only real legal "
            "entity, so it was moved there. The real mapping is business decision B7." % entity.code
        )


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    _branch_lifecycle(cr)
    env.invalidate_all()
    _supersede_stale_ladders(env)
    _delete_decorative_flags(env)
    _notification_windows(cr)
    env.invalidate_all()
    _null_company_branches(env)
