# A10 remediation (2026-11-05), S6: the M61 -> M27 hand-off.
#
# cd_knowledge publishes knowledge.published on every article publication;
# nothing listened. The contact-centre knowledge binding now consumes it
# through the event relay: bindings that point at the article learn the
# version now in the field, and bindings whose article no longer resolves
# to a PUBLISHED article retire themselves — an agent is never offered a
# dead link. M27 deliberately does not depend on the governance stack, so
# this test runs only where both modules are installed (the full lineage);
# the consumer itself stays silent when M61 is absent.
import itertools

import pytest
from odoo.exceptions import AccessError

PUBLISHER = "cd_knowledge.group_knowledge_publisher"
_SEQ = itertools.count(1)


def _user(env, name, groups=()):
    n = next(_SEQ)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A10 S6 CC %s %d" % (name, n),
                "login": "a10s6cc.%s.%d@a10.test" % (name.replace(" ", "").lower(), n),
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(x).id for x in groups])
                ],
            }
        )
    )


@pytest.fixture(autouse=True)
def _relay_reaches_this_tests_events(odoo_env):
    """The test database carries a seed backlog of ~50,000 unrelayed events,
    and one relay pass takes the 500 OLDEST, so it never reached the event
    this test publishes (the live estate has no backlog: its relay cron
    drains it). Mark the earlier backlog relayed; this test's own events
    carry the transaction's timestamp and are left alone. Rolled back with
    the test."""
    odoo_env.cr.execute(
        "UPDATE fix_event_outbox SET relayed_at = now() AT TIME ZONE 'UTC' "
        "WHERE relayed_at IS NULL AND create_date < now() AT TIME ZONE 'UTC'"
    )


@pytest.fixture
def m(odoo_env):
    if "fix.knowledge.article" not in odoo_env or "fix.cc.knowledge.binding" not in odoo_env:
        pytest.skip("the M61<->M27 hand-off needs both modules installed")
    env = odoo_env
    x = type("M", (), {})()
    x.env = env
    x.clerk = _user(env, "clerk")
    x.publisher = _user(env, "publisher", [PUBLISHER])
    return x


def _article(env, code, name=None):
    n = next(_SEQ)
    return env["fix.knowledge.article"].create(
        {
            "name": name or "A10 S6 Article %d" % n,
            "article_code": code,
            "category": "troubleshooting",
            "content": "<p>Isolate the rail, then measure.</p>",
            "tags": "bench",
        }
    )


def _binding(env, ref, intent="battery swell"):
    return env["fix.cc.knowledge.binding"].create(
        {"intent": intent, "article_ref": ref, "note": "front-of-desk for this intent"}
    )


def test_the_binding_learns_the_published_version(m):
    env = m.env
    article = _article(env, "KB-S6-001")
    binding = _binding(env, "KB-S6-001")
    assert binding.resolve_article()["found"] is True  # resolved by CODE
    assert not binding.synced_on
    article.with_user(m.publisher).action_publish()
    env["fix.event.outbox"].sudo().cron_relay()
    binding.invalidate_recordset()
    assert binding.synced_version == article.version
    assert binding.synced_content_hash == article.content_hash
    assert binding.synced_on
    # a binding that points somewhere else is not stamped by this article
    other = _binding(env, "KB-OTHER")
    assert not other.synced_on


def test_a_retired_articles_binding_stops_offering_itself(m):
    env = m.env
    gone = _article(env, "KB-S6-GONE")
    gone.with_user(m.publisher).action_publish()
    binding = _binding(env, "KB-S6-GONE")
    live_article = _article(env, "KB-S6-002")
    live = _binding(env, "KB-S6-002")
    assert binding.active
    # the publisher archives the article; nothing re-publishes it…
    gone.with_user(m.publisher).action_archive()
    # …until the NEXT publication sweeps the bindings
    live_article.with_user(m.publisher).action_publish()
    env["fix.event.outbox"].sudo().cron_relay()
    binding.invalidate_recordset()
    live.invalidate_recordset()
    assert not binding.active
    assert "no longer resolves" in binding.note
    # the live binding survives the same sweep — and is stamped by it
    assert live.active and live.synced_on


def test_the_consumer_is_the_relays_and_is_registered(m):
    env = m.env
    consumers = (
        env["fix.event.consumer"].sudo().search([("event_type", "=", "knowledge.published")])
    )
    assert "consume_knowledge_published" in {c.method for c in consumers}
    with pytest.raises(AccessError, match="run only from the event relay"):
        env["fix.cc.knowledge.binding"].with_user(m.clerk).consume_knowledge_published(
            {
                "event_type": "knowledge.published",
                "aggregate": "fix.knowledge.article",
                "aggregate_id": 1,
                "payload": {"code": "KB-S6-001", "title": "x", "version": 2},
                "company_id": env.company.id,
            }
        )
