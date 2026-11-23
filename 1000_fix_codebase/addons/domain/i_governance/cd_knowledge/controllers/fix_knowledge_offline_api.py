# fix_knowledge_offline_api — the P02 technician library route (A10 deep
# audit 2026-11-23, D-A10-1/#3).
#
# "P02 offline library" was a registry claim with no transport: get_offline_manuals()
# and offline_manifest() computed selections and hashes nothing could download —
# the technician PWA has no library screen because no endpoint serves it.
#
# This controller serves the library to an AUTHENTICATED technician (the same
# session resolver the field-service API uses; bearer or session both work):
#   GET /api/knowledge/offline-manuals   the published+offline-safe articles
#                                        for a brand/model, with per-article
#                                        version + content hash for delta sync
#   GET /api/knowledge/offline-manifest  the technician's own offline set —
#                                        scope, budget, staleness — plus the
#                                        articles it selected
# The manifest carries no attachment bytes (the app fetches per-article
# content by id); responses are honest about empties.
import logging

from odoo import http
from odoo.http import request

from libs.py.fix_api_edge import api_edge

_logger = logging.getLogger(__name__)


def _technician():
    """The authenticated user's employee record, or an error payload."""
    user = request.env.user
    if not user or user._is_public():
        return None, {"error": "unauthenticated", "message": "Technician authentication is required"}
    employee = request.env["hr.employee"].sudo().search([("user_id", "=", user.id)], limit=1)
    if not employee:
        return None, {
            "error": "no_employee",
            "message": "No technician employee record is linked to the authenticated user",
        }
    return employee, None


def _article_payload(article):
    return {
        "id": article.id,
        "code": article.article_code or "",
        "title_en": article.name,
        "title_bn": article.title_bn or article.name,
        "category": article.category,
        "brand": article.device_brand or "",
        "model": article.device_model or "",
        "fault_symptom": article.fault_symptom or "",
        "rework_level": article.rework_level or "",
        "version": article.version,
        "content_hash": article.content_hash,
        "safety_critical": bool(article.safety_critical),
    }


class KnowledgeOfflineApi(http.Controller):
    @api_edge("/api/knowledge/offline-manuals")
    @http.route("/api/knowledge/offline-manuals", type="json", auth="user", methods=["POST"])
    def offline_manuals(self, brand=None, model=None, version_after=None):
        employee, err = _technician()
        if err:
            return err
        Article = request.env["fix.knowledge.article"].sudo()
        manuals = Article.get_offline_manuals(
            brand=brand,
            model=model,
            version_after=int(version_after) if version_after else None,
        )
        rows = []
        for row in manuals:
            article = Article.browse(row.get("id"))
            if not article.exists():
                continue
            payload = _article_payload(article)
            payload["has_content_bn"] = bool(article.content_bn)
            rows.append(payload)
        return {
            "technician": employee.name,
            "brand": brand or "",
            "model": model or "",
            "articles": rows,
            "count": len(rows),
        }

    @api_edge("/api/knowledge/offline-manifest")
    @http.route("/api/knowledge/offline-manifest", type="json", auth="user", methods=["POST"])
    def offline_manifest(self):
        employee, err = _technician()
        if err:
            return err
        sets = request.env["fix.knowledge.offline.set"].sudo().search(
            [("user_id", "=", employee.user_id.id), ("active", "=", True)]
        )
        if not sets:
            return {
                "technician": employee.name,
                "set": None,
                "message": "No active offline set — compute one in the knowledge workspace "
                "(M61) or ask your supervisor to assign one.",
                "articles": [],
            }
        offline_set = sets[0]
        return {
            "technician": employee.name,
            "set": {
                "name": offline_set.name,
                "max_level": offline_set.max_level,
                "brands": offline_set.brand_ids.mapped("name"),
                "device_models": offline_set.device_model_ids.mapped("name"),
                "budget_mb": offline_set.budget_mb,
                "stale_count": offline_set.stale_count,
                "article_count": len(offline_set.article_ids),
            },
            "articles": [_article_payload(a) for a in offline_set.article_ids],
        }
