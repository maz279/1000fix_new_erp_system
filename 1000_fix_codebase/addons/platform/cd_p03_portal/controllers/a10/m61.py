# A10 · M61 Knowledge & Technical Library — surfaces, packs and KPIs over the
# article library, troubleshooting trees, media assets and brand bulletins.
import datetime

SURFACES = {
    "fix.knowledge.article": {
        "order": "write_date desc, id desc",
        "limit": 500,
        "actions": {"action_publish", "action_archive"},
    },
    "fix.knowledge.tree": {
        "order": "name",
        "limit": 300,
        "actions": {"action_publish", "action_archive"},
    },
    "fix.knowledge.media": {"order": "name", "limit": 300, "actions": set()},
    "fix.knowledge.bulletin": {
        "order": "issued_on desc, id desc",
        "limit": 300,
        "actions": {"action_distribute", "action_acknowledge", "action_close"},
    },
    "fix.knowledge.bulletin.recipient": {
        "order": "bulletin_id desc, id desc",
        "limit": 400,
        "actions": set(),
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
    articles = env["fix.knowledge.article"].search([])
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
    articles = env["fix.knowledge.article"].search([])
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
    articles = env["fix.knowledge.article"].search([("state", "=", "published")])
    orders = env["fix.service.order"].search([])
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
    articles = env["fix.knowledge.article"].search([])
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


def recall_routing(env, date_from=None, date_to=None, **params):
    """Recall routing (A10 P1-7, M61-4): every safety recall with what it
    covers, which branches hold it, who acknowledged, and the M09 campaign it
    became. Counts come from the recipient lines and the campaign link, not
    from a status word."""
    bulletins = env["fix.knowledge.bulletin"].search([("bulletin_type", "=", "recall")])
    campaign_model = env.get("fix.warranty.recall")
    rows = []
    for b in bulletins:
        campaign = (
            campaign_model.search([("bulletin_id", "=", b.id)], limit=1)
            if campaign_model
            else False
        )
        pending = b.recipient_ids.filtered(lambda r: not r.acknowledged_on)
        rows.append(
            {
                "bulletin": b.name,
                "severity": dict(b._fields["severity"].selection).get(b.severity),
                "state": dict(b._fields["state"].selection).get(b.state, b.state),
                "scope": " / ".join(x for x in [b.affected_models or "", b.serial_scope or ""] if x)
                or "—",
                "branches": len(b.recipient_ids),
                "acknowledged": len(b.recipient_ids) - len(pending),
                "pending": ", ".join(pending.mapped("branch_id.name")) or "—",
                "campaign": campaign.name if campaign else "—",
            }
        )
    rows.sort(key=lambda r: r["bulletin"])
    return _pack(
        "Recall Routing — %d safety recall(s)" % len(rows),
        [
            "bulletin",
            "severity",
            "state",
            "scope",
            "branches",
            "acknowledged",
            "pending",
            "campaign",
        ],
        {
            "bulletin": "Bulletin",
            "severity": "Severity",
            "state": "State",
            "scope": "Affected Models / Serials",
            "branches": "Recipient Branches",
            "acknowledged": "Acknowledged",
            "pending": "Pending Branches",
            "campaign": "M09 Campaign",
        },
        rows,
        [
            "A10 P1-7: a recall distributes only over what it recalls (models or "
            "serials) to named branches; each branch acknowledges its own line, and "
            "the Quality Manager closes it once every branch has answered.",
            "Distribution hands the recall to M09 as an active warranty recall "
            "campaign and flags M01's open orders on the affected models (event "
            "bulletin.distributed). The campaign column reads that link — '—' means "
            "no campaign yet, not one nobody recorded.",
        ],
        empty="No safety recalls recorded.",
    )


REPORTS = {
    "coverage_analysis": coverage_analysis,
    "usage_usefulness": usage_usefulness,
    "gap_report": gap_report,
    "contribution_leaderboard": contribution_leaderboard,
    "recall_routing": recall_routing,
}


def kpis(env):
    # A10 S6 (M61-7): every tile measures what its label says. The old tiles
    # counted DRAFT articles as "reviews due", offline-available articles as
    # "techs synced" (the flag lives on articles, no device is ever counted),
    # and published/total as "coverage of top faults" — three labels, three
    # invented figures. Coverage is now the gap report's own join: of the
    # brand/model combinations the service orders actually saw, how many have
    # a published article.
    articles = env["fix.knowledge.article"].search([])
    published = articles.filtered(lambda a: a.state == "published")
    bulletins = env["fix.knowledge.bulletin"].search([])
    today = datetime.date.today()
    month_start = today.replace(day=1)
    views = sum(a.views or 0 for a in articles)
    helpful = sum(a.helpful_votes or 0 for a in articles)
    combos = {}
    for order in env["fix.service.order"].search([]):
        device = getattr(order, "device_id", False)
        brand = (
            device.brand_id.name if device and getattr(device, "brand_id", False) else "Unspecified"
        )
        model = (
            device.device_model_id.name
            if device and getattr(device, "device_model_id", False)
            else "—"
        )
        combos[(brand, model)] = combos.get((brand, model), 0) + 1
    covered = [
        key
        for key in combos
        if published.filtered(
            lambda a, b=key[0], m=key[1]: (a.device_brand or "") == b
            and (not a.device_model or a.device_model == m)
        )
    ]
    # the offline pack is the model's own offline domain — published content
    # flagged for the technician app's SQLite store.
    offline_articles = env["fix.knowledge.article"].search_count(
        [("state", "=", "published"), ("offline_available", "=", True)]
    )
    return {
        "articles": len(articles),
        "coverage_serviced": round(len(covered) / len(combos) * 100.0, 1) if combos else 0.0,
        "offline_articles": offline_articles,
        "usefulness_score": round(helpful / views * 100.0, 1) if views else 0.0,
        "reviews_due": len(published.filtered(lambda a: a.review_due and a.review_due <= today)),
        "brand_bulletins_mtd": len(
            bulletins.filtered(lambda b: b.issued_on and b.issued_on >= month_start)
        ),
    }
