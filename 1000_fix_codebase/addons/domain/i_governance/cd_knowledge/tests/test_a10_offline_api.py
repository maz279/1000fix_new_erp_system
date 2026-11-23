# A10 deep audit (2026-11-23, D-A10-1/#3): the P02 offline library transport.
#
# /api/knowledge/offline-manuals and /api/knowledge/offline-manifest serve
# the technician app (JSON routes, the estate's api_edge convention):
# authenticated technician only, published+offline-safe articles with
# version + content hash for delta sync, honest empties when no set exists.
from unittest.mock import patch

from odoo import api as odoo_api

from odoo.addons.cd_knowledge.controllers import fix_knowledge_offline_api as kapi
from odoo.addons.cd_knowledge.controllers.fix_knowledge_offline_api import (
    KnowledgeOfflineApi,
)


class _Request:
    """The slice of ``odoo.http.request`` the controller reads."""

    def __init__(self, env):
        self.env = env


def _as(env, user):
    return patch.object(kapi, "request", _Request(env(user=user.id)))


def _as_anonymous(env):
    return patch.object(
        kapi, "request", _Request(odoo_api.Environment(env.cr, None, env.context))
    )


def _call(env, user, method, **params):
    with _as(env, user):
        return getattr(KnowledgeOfflineApi(), method)(**params)


def _tech_user(env):
    user = env["res.users"].create(
        {
            "name": "P02 Tech",
            "login": "p02.tech@a10.test",
            "group_ids": [(6, 0, [env.ref("base.group_user").id])],
        }
    )
    env["hr.employee"].create({"name": "P02 Tech", "user_id": user.id})
    return user


def test_the_anonymous_call_is_refused(odoo_env):
    with _as_anonymous(odoo_env):
        payload = KnowledgeOfflineApi().offline_manuals(brand="Zeltrix")
    assert payload["error"] == "unauthenticated"


def test_a_user_without_an_employee_is_refused(odoo_env):
    env = odoo_env
    user = env["res.users"].create(
        {
            "name": "No Employee",
            "login": "no.employee@a10.test",
            "group_ids": [(6, 0, [env.ref("base.group_user").id])],
        }
    )
    assert _call(env, user, "offline_manifest")["error"] == "no_employee"


def test_the_manifest_is_honest_when_no_set_exists(odoo_env):
    payload = _call(odoo_env, _tech_user(odoo_env), "offline_manifest")
    assert payload["set"] is None
    assert "No active offline set" in payload["message"]
    assert payload["articles"] == []


def test_the_manuals_serve_published_offline_articles_for_a_brand(odoo_env):
    env = odoo_env
    Article = env["fix.knowledge.article"]
    author = _tech_user(env)  # any internal user authors
    online = Article.create(
        {
            "name": "Online only Z14",
            "category": "troubleshooting",
            "content": "<p>na</p>",
            "device_brand": "Zeltrix",
            "device_model": "Z14",
            "offline_available": False,  # the field DEFAULTS to True
        }
    )
    shelf = Article.create(
        {
            "name": "Offline Z14 service",
            "category": "repair_procedure",
            "content": "<p>steps</p>",
            "device_brand": "Zeltrix",
            "device_model": "Z14",
            "offline_available": True,
        }
    )
    online.sudo().action_publish()
    shelf.sudo().action_publish()
    online.invalidate_recordset()
    shelf.invalidate_recordset()
    assert shelf.state == "published" and online.state == "published"
    payload = _call(env, author, "offline_manuals", brand="Zeltrix", model="Z14")
    ids = [row["id"] for row in payload["articles"]]
    assert shelf.id in ids
    assert online.id not in ids  # offline_available=False stays out
    row = next(r for r in payload["articles"] if r["id"] == shelf.id)
    assert row["version"] == 2 and row["content_hash"]
    assert payload["count"] == len(payload["articles"])
    # delta sync: nothing new since this version
    payload = _call(env, author, "offline_manuals", brand="Zeltrix", version_after=2)
    assert shelf.id not in [row["id"] for row in payload["articles"]]
