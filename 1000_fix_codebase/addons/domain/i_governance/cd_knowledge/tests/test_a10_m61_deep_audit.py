# A10 deep audit (2026-11-22) — M61 fix landed from the five-auditor sweep:
#
# A4-F01  the published-article revision path was the review gate's blind
#         spot: any internal user could write() new content on a published
#         article, the version bumped, knowledge.published fired and every
#         offline device re-synced — with no publisher, no author check and
#         the OLD review stamps still displayed next to the new content.
#         Now: the editor must be the superuser, a Knowledge Publisher, or
#         the article's own author; a revision clears the stale review
#         stamps; a safety-tags edit is itself a revision (A4-F07).
#
# The odoo_env fixture rolls everything back.
import itertools
import json
import types

import pytest
from odoo.exceptions import UserError

PUBLISHER = "cd_knowledge.group_knowledge_publisher"
_SEQ = itertools.count(1)


def _user(env, login, groups=()):
    n = next(_SEQ)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A10 DA %s %d" % (login, n),
                "login": "a10dam.%s.%d@a10.test" % (login, n),
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(x).id for x in groups])
                ],
            }
        )
    )


@pytest.fixture
def k(odoo_env):
    x = types.SimpleNamespace(env=odoo_env)
    x.clerk = _user(odoo_env, "clerk")
    x.author = _user(odoo_env, "author", [PUBLISHER])
    x.publisher = _user(odoo_env, "publisher", [PUBLISHER])
    return x


def _article(x, vals=None):
    vals = dict(
        {
            "name": "Zeltrix Z20 battery swelling",
            "category": "repair_procedure",
            "content": "<p>Discharge below 30% before opening</p>",
        },
        **(vals or {}),
    )
    # created by the author: owner_id (the author of record) stamps from the
    # creating session
    return x.env["fix.knowledge.article"].with_user(x.author).create(vals)


def _events(env, event_type, aggregate_id=None):
    domain = [("event_type", "=", event_type)]
    if aggregate_id:
        domain += [("aggregate", "=", "fix.knowledge.article"), ("aggregate_id", "=", aggregate_id)]
    return [json.loads(e.payload) for e in env["fix.event.outbox"].search(domain, order="id")]


def test_a_non_author_cannot_revise_published_content(k):
    art = _article(k)
    art.with_user(k.publisher).action_publish()
    assert art.state == "published" and art.version == 2
    # the clerk's edit is refused: published content ships to the field only
    # through its author or a publisher
    with pytest.raises(UserError, match="revised by its author or a Knowledge Publisher"):
        art.with_user(k.clerk).write({"content": "<p>quietly rewritten</p>"})
    art.invalidate_recordset()
    assert art.version == 2  # nothing moved


def test_an_authors_revision_resyncs_and_clears_the_stale_review(k):
    art = _article(k)
    art.with_user(k.publisher).action_publish()
    stamped_reviewer = art.reviewed_by_id
    assert stamped_reviewer  # the publish stamped a reviewer
    before_hash = art.content_hash
    art.with_user(k.author).write({"content": "<p>Discharge below 25%; new fuse spec</p>"})
    art.invalidate_recordset()
    # the revision still ships (M61-3) — the sync must re-deliver it
    assert art.version == 3
    assert art.content_hash != before_hash
    payload = _events(k.env, "knowledge.published", art.id)[-1]
    assert payload["version"] == 3 and payload["content_hash"] == art.content_hash
    # but the old review no longer stands behind the new bytes
    assert not art.reviewed_by_id and not art.reviewed_on
    # the publisher path is still open (a publisher may also revise)
    art.with_user(k.publisher).write({"content": "<p>publisher touch-up</p>"})
    art.invalidate_recordset()
    assert art.version == 4


def test_a_safety_tag_edit_is_itself_a_revision(k):
    art = _article(k, {"tags": ""})
    art.with_user(k.publisher).action_publish()
    assert not art.safety_critical
    art.with_user(k.author).write({"tags": "battery"})
    art.invalidate_recordset()
    # the tag flip changed what the content IS: version + event move
    assert art.version == 3
    assert art.safety_critical is True
    assert _events(k.env, "knowledge.published", art.id)[-1]["version"] == 3
