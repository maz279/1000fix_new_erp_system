# A10 remediation (2026-11-05), K1: reviewed publishing of technical content.
#
# The audit found any employee could publish any article, tree or bulletin,
# and safety-critical content (electrical, battery, high-voltage work a
# technician follows in the field) reached devices with no review at all
# (report §6 K1, M61-1/-2). Publishing is now a Knowledge Publisher's act;
# safety-critical content additionally needs a named reviewer from that
# group who is not the author; a published edit is a REVISION that re-syncs
# (M61-3).
#
# Every control is exercised as NON-ADMIN users holding only the role
# groups each step needs (the superuser is trusted by the field guard and
# would hide a gap). Each gate is attacked three ways: the wrong role, a
# plain write() (the JSON-RPC path) and the real P03 endpoints. The
# legitimate path runs end to end through the real actions. The odoo_env
# fixture rolls everything back.
import itertools
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
_MA = getattr(g.P03GenericApiController.model_action, "original_endpoint", None) or (
    g.P03GenericApiController.model_action
)

_SEQ = itertools.count(1)


def _user(env, login, groups=()):
    n = next(_SEQ)
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A10 K1 %s %d" % (login, n),
                "login": "a10k1.%s.%d@a10.test" % (login, n),
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(x).id for x in groups])
                ],
            }
        )
    )
    assert not user.has_group("base.group_system")
    return user


def _events(env, event_type, aggregate_id=None):
    domain = [("event_type", "=", event_type)]
    if aggregate_id is not None:
        domain.append(("aggregate_id", "=", aggregate_id))
    return [json.loads(e.payload) for e in env["fix.event.outbox"].search(domain, order="id")]


@pytest.fixture
def k(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env)
    x.clerk = _user(env, "clerk")
    x.author = _user(env, "author", [PUBLISHER])
    x.publisher = _user(env, "publisher", [PUBLISHER])
    saved = getattr(g, "request", None)
    yield x
    g.request = saved


def _article(x, vals=None, user=None):
    vals = dict(
        {
            "name": "Zeltrix Z14 battery swelling",
            "category": "repair_procedure",
            "content": "<p>Discharge below 30% before opening</p>",
        },
        **(vals or {}),
    )
    return x.env["fix.knowledge.article"].with_user(user or x.author).create(vals)


def p03(x, endpoint, user=None, **kw):
    g.request = types.SimpleNamespace(env=x.env(user=(user or x.clerk).id))
    return endpoint(g.P03GenericApiController(), **kw)


# ------------------------------------------------------------------ the publish gate
def test_k1_publishing_is_a_publishers_act(k):
    art = _article(k, {"tags": "battery, z14"})
    with pytest.raises(UserError, match="Only a Knowledge Publisher"):
        art.with_user(k.clerk).action_publish()
    # ordinary content publishes without a named reviewer
    plain = _article(k, {"name": "Zeltrix Z15 hinge torque"})
    plain.with_user(k.publisher).action_publish()
    assert plain.state == "published"
    assert (plain.reviewed_by_id, plain.version) == (k.env["res.users"], 2)


def test_k1_safety_content_needs_a_second_publisher(k):
    art = _article(k, {"tags": "battery, swelling"})  # safety-critical by tag
    assert art.safety_critical is True
    # no reviewer at all
    with pytest.raises(UserError, match="cannot be published without a reviewer"):
        art.with_user(k.publisher).action_publish()
    # a reviewer who is not a publisher is a typo, not a review
    with pytest.raises(UserError, match="must belong to the Knowledge Publisher"):
        art.with_user(k.publisher).action_publish(reviewer_id=k.clerk.id)
    # the author cannot be their own reviewer (M61-1)
    with pytest.raises(UserError, match="cannot be its reviewer"):
        art.with_user(k.author).action_publish(reviewer_id=k.author.id)
    # a second publisher reviews and the record names them
    art.with_user(k.publisher).action_publish(reviewer_id=k.publisher.id)
    assert art.state == "published"
    assert (art.reviewed_by_id, art.reviewed_on) == (
        k.publisher,
        fields.Date.context_today(art),
    )
    payload = _events(k.env, "knowledge.published", art.id)[-1]
    assert payload["version"] == 2 and payload["content_hash"] == art.content_hash


def test_k1_safety_bulletins_are_safety_content(k):
    # the category alone makes it safety-critical — no tag needed
    bulletin_article = _article(
        k, {"name": "Recall: Z14 battery batch", "category": "safety_bulletin"}
    )
    assert bulletin_article.safety_critical is True
    with pytest.raises(UserError, match="cannot be published without a reviewer"):
        bulletin_article.with_user(k.publisher).action_publish()
    bulletin_article.with_user(k.publisher).action_publish(reviewer_id=k.publisher.id)
    assert bulletin_article.reviewed_by_id == k.publisher


def test_k1_lifecycle_fields_are_guarded(k):
    art = _article(k)
    with pytest.raises(UserError, match=GUARD):
        art.with_user(k.author).write({"state": "published"})
    with pytest.raises(UserError, match=GUARD):
        art.with_user(k.author).write({"version": 9})
    with pytest.raises(UserError, match=GUARD):
        art.with_user(k.author).write({"reviewed_by_id": k.publisher.id})
    with pytest.raises(UserError, match=GUARD):
        k.env["fix.knowledge.article"].with_user(k.author).create(
            {
                "name": "born published",
                "category": "training",
                "content": "<p>x</p>",
                "state": "published",
            }
        )
    # archiving is a publisher's act over published content only
    with pytest.raises(UserError, match="Only a Knowledge Publisher"):
        art.with_user(k.clerk).action_archive()
    with pytest.raises(UserError, match="Only a published article"):
        art.with_user(k.author).action_archive()
    art.with_user(k.author).action_publish()
    art.with_user(k.author).action_archive()
    assert art.state == "archived"


def test_k1_published_edit_is_a_revision_that_resyncs(k):
    art = _article(k, {"article_code": "KB-K1-901"})
    art.with_user(k.author).action_publish()
    before_hash = art.content_hash
    # the edit is allowed — it is the author's content to improve — but it
    # MUST NOT die silently on the server: version and event move so the
    # offline sync (version_after + hash) re-delivers it (M61-3)
    art.with_user(k.author).write({"content": "<p>Discharge below 25%; new fuse spec</p>"})
    assert art.version == 3
    assert art.content_hash != before_hash
    payload = _events(k.env, "knowledge.published", art.id)[-1]
    assert payload == {
        "title": "Zeltrix Z14 battery swelling",
        "category": "repair_procedure",
        "code": "KB-K1-901",
        "version": 3,
        "content_hash": art.content_hash,
    }
    # a metadata-only touch of a published article that changes nothing is
    # not a revision
    art.with_user(k.author).write({"name": art.name})
    assert art.version == 3


def test_k1_trees_publish_under_the_same_gate(k):
    Tree = k.env["fix.knowledge.tree"]
    tree = Tree.with_user(k.author).create(
        {"name": "Z14 no power tree", "tags": "high voltage", "nodes_text": "PSU -> fuse"}
    )
    assert tree.safety_critical is True
    with pytest.raises(UserError, match="cannot be published without a reviewer"):
        tree.with_user(k.publisher).action_publish()
    tree.with_user(k.publisher).action_publish(reviewer_id=k.publisher.id)
    assert (tree.state, tree.reviewed_by_id) == ("published", k.publisher)
    with pytest.raises(UserError, match=GUARD):
        tree.with_user(k.author).write({"state": "archived"})
    tree.with_user(k.author).action_archive()
    assert tree.state == "archived"


def test_k1_bulletins_route_through_distribute_and_close(k):
    Bulletin = k.env["fix.knowledge.bulletin"]
    rec = Bulletin.with_user(k.author).create(
        {"name": "SB-2026-11", "brand": "Zeltrix", "issued_on": fields.Date.today()}
    )
    with pytest.raises(UserError, match="Only a Knowledge Publisher"):
        rec.with_user(k.clerk).action_distribute()
    with pytest.raises(UserError, match=GUARD):
        rec.with_user(k.author).write({"state": "distributed"})
    rec.with_user(k.author).action_distribute()
    assert rec.state == "distributed"
    with pytest.raises(UserError, match="closure note"):
        rec.with_user(k.author).action_close()
    rec.with_user(k.author).action_close("Field swapped all affected batteries")
    assert rec.state == "closed"


def test_k1_p03_surface_takes_content_not_state(k):
    art = _article(k)
    # tags are the author's to edit through the workspace form
    out = p03(
        k,
        _MW,
        user=k.author,
        model="fix.knowledge.article",
        record_id=art.id,
        values={"tags": "battery, swelling"},
    )
    assert "error" not in out and art.tags == "battery, swelling"
    # the lifecycle never moves through the write endpoint
    out = p03(
        k,
        _MW,
        user=k.author,
        model="fix.knowledge.article",
        record_id=art.id,
        values={"state": "published"},
    )
    assert "error" in out and GUARD in out["error"]
    out = p03(
        k,
        _MW,
        user=k.author,
        model="fix.knowledge.article",
        record_id=art.id,
        values={"reviewed_by_id": k.publisher.id},
    )
    assert "error" in out and GUARD in out["error"]
    # the action endpoint carries the gate and the reviewer prompt
    out = p03(
        k,
        _MA,
        user=k.clerk,
        model="fix.knowledge.article",
        ids=art.ids,
        method="action_publish",
    )
    assert out.get("success") is False and "Knowledge Publisher" in out.get("error", "")
    out = p03(
        k,
        _MA,
        user=k.publisher,
        model="fix.knowledge.article",
        ids=art.ids,
        method="action_publish",
        kwargs={"reviewer_id": k.publisher.id},
    )
    assert out.get("success") is True
    assert (art.state, art.reviewed_by_id) == ("published", k.publisher)
