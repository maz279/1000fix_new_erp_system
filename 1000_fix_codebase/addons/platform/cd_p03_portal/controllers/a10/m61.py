# A10 · M61 Knowledge & Technical Library — surfaces, packs and KPIs over the
# article library, troubleshooting trees, media assets and brand bulletins.
import datetime

SURFACES = {
    "fix.knowledge.article": {
        "order": "write_date desc, id desc",
        "limit": 500,
        "actions": {"action_publish"},
    },
    "fix.knowledge.tree": {
        "order": "name",
        "limit": 300,
        "actions": {"action_publish"},
    },
    "fix.knowledge.media": {"order": "name", "limit": 300, "actions": set()},
    "fix.knowledge.bulletin": {
        "order": "issued_on desc, id desc",
        "limit": 300,
        "actions": {"action_distribute"},
    },
}


def _pack(title, cols, labels, rows, notes, totals=None, empty=None):
    return {
        "title": title,
        "cols": cols,
        "labels": labels,
        "rows": rows,
        "totals": totals,
        "notes": notes,
        "empty": empty,
    }


def coverage_analysis(env, date_from=None, date_to=None, **params):
    """Coverage analysis: articles by category and brand."""
    articles = env["fix.knowledge.article"].sudo().search([])
    groups = {}
    for art in articles:
        key = (
            dict(art._fields["category"].selection).get(art.category),
            art.device_brand or "All brands",
        )
        groups[key] = groups.get(key, 0) + 1
    rows = [{"category": c, "brand": b, "articles": n} for (c, b), n in sorted(groups.items())]
    return _pack(
        "Coverage Analysis — %d article(s)" % len(articles),
        ["category", "brand", "articles"],
        {"category": "Article Type", "brand": "Brand", "articles": "Articles"},
        rows,
        [
            "Coverage counts catalogued articles; a brand with zero articles simply does not "
            "appear (the gap report lists it explicitly)."
        ],
        totals={"category": "Total", "articles": sum(r["articles"] for r in rows)},
        empty="No articles in the library.",
    )


def usage_usefulness(env, date_from=None, date_to=None, **params):
    """Article usage and usefulness from the article's view/helpful counters."""
    articles = env["fix.knowledge.article"].sudo().search([])
    rows = []
    for art in articles:
        views = art.views or 0
        helpful = art.helpful_votes or 0
        rows.append(
            {
                "article": art.name[:60],
                "code": art.article_code or "—",
                "category": dict(art._fields["category"].selection).get(art.category),
                "views": views,
                "helpful": helpful,
                "usefulness": round(helpful / views * 100.0, 1) if views else 0.0,
                "state": dict(art._fields["state"].selection).get(art.state, art.state),
            }
        )
    rows.sort(key=lambda r: -r["views"])
    return _pack(
        "Article Usage & Usefulness",
        ["article", "code", "category", "views", "helpful", "usefulness", "state"],
        {
            "article": "Article",
            "code": "Code",
            "category": "Type",
            "views": "Views",
            "helpful": "Helpful Votes",
            "usefulness": "Usefulness %",
            "state": "State",
        },
        rows,
        [
            "Usefulness = helpful votes / views for the article's own counters; articles with "
            "no views show 0 rather than a fabricated score."
        ],
        empty="No articles in the library.",
    )


def gap_report(env, date_from=None, date_to=None, **params):
    """Gap report by brand/model: service orders by the device's brand and model
    compared with published articles for the same combination."""
    articles = env["fix.knowledge.article"].sudo().search([("state", "=", "published")])
    orders = env["fix.service.order"].sudo().search([])
    groups = {}
    for order in orders:
        device = getattr(order, "device_id", False)
        brand = (
            device.brand_id.name if device and getattr(device, "brand_id", False) else "Unspecified"
        )
        model = (
            device.device_model_id.name
            if device and getattr(device, "device_model_id", False)
            else "—"
        )
        key = (brand, model)
        groups[key] = groups.get(key, 0) + 1
    rows = []
    for (brand, model), count in sorted(groups.items(), key=lambda kv: -kv[1]):
        matched = len(
            articles.filtered(
                lambda a, b=brand, m=model: (a.device_brand or "") == b
                and (not a.device_model or a.device_model == m)
            )
        )
        rows.append(
            {
                "brand": brand,
                "model": model,
                "service_orders": count,
                "articles": matched,
                "gap": "Covered" if matched else "GAP",
            }
        )
    gaps = len([r for r in rows if r["gap"] == "GAP"])
    return _pack(
        "Gap Report by Brand/Model — %d uncovered combination(s)" % gaps,
        ["brand", "model", "service_orders", "articles", "gap"],
        {
            "brand": "Brand",
            "model": "Model",
            "service_orders": "Service Orders",
            "articles": "Published Articles",
            "gap": "Coverage",
        },
        rows,
        [
            "Brand and model come from the service order's device registry record. A combination "
            "is a GAP when no published article names that brand and model (or the brand with no "
            "model restriction)."
        ],
        totals={
            "brand": "Total",
            "service_orders": sum(r["service_orders"] for r in rows),
            "articles": sum(r["articles"] for r in rows),
        },
        empty="No service orders recorded.",
    )


def contribution_leaderboard(env, date_from=None, date_to=None, **params):
    """Contribution leaderboard by creator (the article model carries no author
    field, so the creating user is the honest basis)."""
    articles = env["fix.knowledge.article"].sudo().search([])
    groups = {}
    for art in articles:
        key = art.create_uid.name if art.create_uid else "—"
        g = groups.setdefault(key, {"articles": 0, "views": 0, "helpful": 0})
        g["articles"] += 1
        g["views"] += art.views or 0
        g["helpful"] += art.helpful_votes or 0
    rows = [
        {"author": k, **v} for k, v in sorted(groups.items(), key=lambda kv: -kv[1]["articles"])
    ]
    return _pack(
        "Contribution Leaderboard",
        ["author", "articles", "views", "helpful"],
        {
            "author": "Author (creator)",
            "articles": "Articles",
            "views": "Views",
            "helpful": "Helpful Votes",
        },
        rows,
        [
            "Groups by the creating user because the article model has no author field; an "
            "author score is not invented."
        ],
        totals={
            "author": "Total",
            "articles": sum(r["articles"] for r in rows),
            "views": sum(r["views"] for r in rows),
            "helpful": sum(r["helpful"] for r in rows),
        },
        empty="No articles in the library.",
    )


REPORTS = {
    "coverage_analysis": coverage_analysis,
    "usage_usefulness": usage_usefulness,
    "gap_report": gap_report,
    "contribution_leaderboard": contribution_leaderboard,
}


def kpis(env):
    articles = env["fix.knowledge.article"].sudo().search([])
    published = articles.filtered(lambda a: a.state == "published")
    bulletins = env["fix.knowledge.bulletin"].sudo().search([])
    today = datetime.date.today()
    month_start = today.replace(day=1)
    views = sum(a.views or 0 for a in articles)
    helpful = sum(a.helpful_votes or 0 for a in articles)
    return {
        "articles": len(articles),
        "coverage_top_faults": round(len(published) / len(articles) * 100.0, 1)
        if articles
        else 0.0,
        "offline_synced_techs": len(articles.filtered(lambda a: a.offline_available)),
        "usefulness_score": round(helpful / views * 100.0, 1) if views else 0.0,
        "reviews_due": len(articles.filtered(lambda a: a.state == "draft")),
        "brand_bulletins_mtd": len(
            bulletins.filtered(lambda b: b.issued_on and b.issued_on >= month_start)
        ),
    }
