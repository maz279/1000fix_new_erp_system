# A10 remediation (2026-11-05), P1-2: the knowledge review clock (M61-6).
#
# The audit found published technical content had no review cycle: nothing
# ever came due, so a five-year-old wiring diagram was trusted exactly like
# one signed off yesterday. Publishing (or revising) now opens a 12-month
# review window and a daily cron announces content whose window closed —
# and the window is never typed by hand.
import datetime
import json
import types

import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as g
from odoo.exceptions import UserError

GUARD = "changes only through its workflow"
PUBLISHER = "cd_knowledge.group_knowledge_publisher"

_MW = getattr(g.P03GenericApiController.model_write, "original_endpoint", None) or (
    g.P03GenericApiController.model_write
)


def _events(env, event_type, aggregate_id=None):
    domain = [("event_type", "=", event_type)]
    if aggregate_id is not None:
        domain.append(("aggregate_id", "=", aggregate_id))
    return [json.loads(e.payload) for e in env["fix.event.outbox"].search(domain, order="id")]


@pytest.fixture
def c(odoo_env):
    saved = getattr(g, "request", None)
    yield types.SimpleNamespace(env=odoo_env)
    g.request = saved


def _user(env, name, groups=()):
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A10 P12 %s" % name,
                "login": "a10p12.%s@a10.test" % name.lower(),
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(x).id for x in groups])
                ],
            }
        )
    )


def test_publish_opens_a_window_and_a_revision_restarts_it(c):
    author = _user(c.env, "Author")
    Article = c.env["fix.knowledge.article"]
    art = Article.with_user(author).create(
        {
            "name": "Battery pack safe discharge",
            "category": "repair_procedure",
            "content": "Discharge to 30% before opening the pack.",
        }
    )
    # the owner is stamped at creation, not chosen later
    assert art.owner_id == author
    art.with_user(_user(c.env, "Publisher", [PUBLISHER])).action_publish()
    assert art.state == "published"
    assert art.review_due == fields.Date.context_today(art) + datetime.timedelta(days=365)
    # the window is never typed: a non-su edit of the clock fields is refused
    with pytest.raises(UserError, match=GUARD):
        art.with_user(author).write({"review_due": fields.Date.today()})
    with pytest.raises(UserError, match=GUARD):
        art.with_user(author).write({"owner_id": _user(c.env, "Other").id})
    # a revision is fresh content: the window restarts even from far overdue
    art._guarded().write({"review_due": fields.Date.today() - datetime.timedelta(days=400)})
    art.with_user(author).write({"content": "Discharge to 25% before opening the pack."})
    assert art.version == 3  # publish -> 2, revision -> 3
    assert art.review_due == fields.Date.context_today(art) + datetime.timedelta(days=365)


def test_review_clock_announces_once_a_day_until_revised(c):
    author = _user(c.env, "Author2")
    publisher = _user(c.env, "Publisher2", [PUBLISHER])
    Article = c.env["fix.knowledge.article"]
    art = Article.with_user(author).create(
        {"name": "Old schematic", "category": "schematic", "content": "<svg/>"}
    )
    art.with_user(publisher).action_publish()
    art._guarded().write({"review_due": fields.Date.today() - datetime.timedelta(days=1)})
    stale_draft = Article.with_user(author).create(
        {"name": "Never published", "category": "device_guide", "content": "draft"}
    )
    stale_draft._guarded().write({"review_due": fields.Date.today() - datetime.timedelta(days=30)})
    assert Article.cron_article_review() == 1  # only the published one — drafts are not field content
    (payload,) = _events(c.env, "knowledge.review.due", art.id)
    assert payload == {
        "title": "Old schematic",
        "code": "",
        "category": "schematic",
        "version": art.version,
        "review_due": str(fields.Date.today() - datetime.timedelta(days=1)),
    }
    assert art.review_notified_on == fields.Date.today()
    # at most once a day
    assert Article.cron_article_review() == 0
    # archiving retires the content and the nag with it
    art.with_user(publisher).action_archive()
    assert Article.cron_article_review() == 0


def test_the_clock_is_not_editable_through_the_workspace(c):
    author = _user(c.env, "Author3")
    Article = c.env["fix.knowledge.article"]
    art = Article.with_user(author).create(
        {"name": "Endpoint target", "category": "device_guide", "content": "x"}
    )
    g.request = types.SimpleNamespace(env=c.env(user=author.id))
    out = _MW(
        g.P03GenericApiController(),
        model="fix.knowledge.article",
        record_id=art.id,
        values={"review_due": str(fields.Date.today() + datetime.timedelta(days=3000))},
    )
    assert "error" in out and GUARD in out["error"]
    out = _MW(
        g.P03GenericApiController(),
        model="fix.knowledge.article",
        record_id=art.id,
        values={"owner_id": _user(c.env, "SomeoneElse").id},
    )
    assert "error" in out and GUARD in out["error"]
