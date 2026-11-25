# A10 · M61 Knowledge & Technical Library — surfaces, packs and KPIs over the
# article library, troubleshooting trees, media assets and brand bulletins.
import datetime

# M61 capture audit (2026-11-18): reviewers and technicians are internal
# users; the server checks the rest (publisher, not the author, the QM).
_INTERNAL = [("share", "=", False)]

SURFACES = {
    "fix.knowledge.article": {
        "order": "write_date desc, id desc",
        "limit": 500,
        "actions": {"action_publish", "action_archive"},
    },
    "fix.knowledge.article.version": {
        "order": "article_id, version desc",
        "limit": 500,
        "actions": set(),
    },
    "fix.knowledge.capture": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_take", "action_draft_article", "action_merge"},
    },
    "fix.knowledge.review": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_approve", "action_return", "action_safety_approve", "action_cancel"},
        "pickers": {
            "reviewer_id": _INTERNAL,
            "article_id": [("state", "=", "draft")],
            "tree_id": [("state", "=", "draft")],
        },
    },
    "fix.knowledge.tree": {
        "order": "name",
        "limit": 300,
        "actions": {"action_publish", "action_archive"},
    },
    "fix.knowledge.tree.node": {"order": "tree_id, sequence, id", "limit": 500, "actions": set()},
    "fix.knowledge.media": {"order": "name", "limit": 300, "actions": set()},
    "fix.knowledge.library": {
        "order": "brand_id, name",
        "limit": 300,
        "actions": {"action_make_available", "action_withdraw"},
    },
    "fix.knowledge.link": {
        "order": "relevance_weight desc, id",
        "limit": 500,
        "actions": set(),
        "pickers": {
            "article_id": [("state", "!=", "archived")],
            "tree_id": [("state", "!=", "archived")],
        },
    },
    "fix.knowledge.offline.set": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_compute"},
        "pickers": {"user_id": _INTERNAL},
    },
    "fix.knowledge.feedback": {
        "order": "id desc",
        "limit": 500,
        "actions": set(),
        "pickers": {"article_id": [("state", "=", "published")]},
    },
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
    """Article usage and usefulness. Usefulness is measured from the
    usefulness feedback (FR-KMS-030): the share of "did this resolve it?"
    answers that said yes, and the average 1-5 rating. M61 capture audit: the
    old score divided helpful votes by a view counter nothing increments."""
    articles = env["fix.knowledge.article"].search([])
    today = datetime.date.today()
    rows = []
    for art in articles:
        if art.flagged_on:
            health = "FLAGGED: %s" % art.flag_reason
        elif art.state == "published" and art.review_due and art.review_due <= today:
            health = "Review overdue"
        else:
            health = "—"
        rows.append(
            {
                "article": art.name[:60],
                "code": art.article_code or "—",
                "category": dict(art._fields["category"].selection).get(art.category),
                "version": art.version,
                "feedback": art.feedback_count,
                "resolved": art.resolution_rate,
                "rating": round(art.avg_rating, 2) if art.feedback_count else 0.0,
                "health": health,
                "state": dict(art._fields["state"].selection).get(art.state, art.state),
            }
        )
    rows.sort(key=lambda r: (r["health"] == "—", -r["feedback"], r["article"]))
    return _pack(
        "Article Usage & Usefulness",
        [
            "article",
            "code",
            "category",
            "version",
            "feedback",
            "resolved",
            "rating",
            "health",
            "state",
        ],
        {
            "article": "Article",
            "code": "Code",
            "category": "Type",
            "version": "Version",
            "feedback": "Feedback",
            "resolved": "Resolved It %",
            "rating": "Avg Rating (1-5)",
            "health": "Health",
            "state": "State",
        },
        rows,
        [
            "Resolved It % = 'yes' answers / all feedback; the rating is the average of the "
            "1-5 ratings. Articles with no feedback show 0 rather than a fabricated score.",
            "Flagged = three 'did not resolve' answers in a row, or an average below 2.5 over "
            "five or more ratings, on the current version (AUT-KMS-17).",
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
    """Contribution leaderboard (FR-KMS-029): articles owned, field captures
    contributed, reviews done and "resolved it" answers on their articles."""
    groups = {}

    def row(user):
        return groups.setdefault(
            user.name if user else "—",
            {"articles": 0, "captures": 0, "reviews": 0, "resolved": 0},
        )

    for art in env["fix.knowledge.article"].search([]):
        g = row(art.owner_id or art.create_uid)
        g["articles"] += 1
        g["resolved"] += len(art.feedback_ids.filtered(lambda f: f.resolved == "yes"))
    for cap in env["fix.knowledge.capture"].search([]):
        row(cap.captured_by_id)["captures"] += 1
    reviews = env["fix.knowledge.review"].search(
        [("state", "in", ("approved", "returned", "reviewed"))]
    )
    for rev in reviews:
        row(rev.reviewer_id)["reviews"] += 1
    rows = [
        {"author": k, **v}
        for k, v in sorted(
            groups.items(), key=lambda kv: (-(kv[1]["articles"] + kv[1]["captures"]), kv[0])
        )
    ]
    return _pack(
        "Contribution Leaderboard",
        ["author", "articles", "captures", "reviews", "resolved"],
        {
            "author": "Contributor",
            "articles": "Articles Owned",
            "captures": "Field Captures",
            "reviews": "Reviews Done",
            "resolved": "Resolved-It Answers on Their Articles",
        },
        rows,
        [
            "Recognition context only (spec 12.2: M57 receives it as context, not a metric). "
            "Resolved-it answers are counted; no causal first-time-fix claim is made "
            "(BRU-KMS-17)."
        ],
        totals={
            "author": "Total",
            "articles": sum(r["articles"] for r in rows),
            "captures": sum(r["captures"] for r in rows),
            "reviews": sum(r["reviews"] for r in rows),
            "resolved": sum(r["resolved"] for r in rows),
        },
        empty="No contributions yet.",
    )


def expertise_map(env, date_from=None, date_to=None, **params):
    """Expertise map (FR-KMS-035, AUT-KMS-18): who knows what, derived from
    authored articles, field captures and reviews per brand, and the brands
    whose knowledge sits with fewer than three people. Derived, never typed."""
    people = {}

    def bump(brand, user, key):
        if not user:
            return
        brand = (brand or "").strip() or "All brands"
        g = people.setdefault(brand, {}).setdefault(
            user.name, {"authored": 0, "captured": 0, "reviewed": 0}
        )
        g[key] += 1

    for art in env["fix.knowledge.article"].search([("state", "!=", "archived")]):
        bump(art.device_brand, art.owner_id or art.create_uid, "authored")
    for cap in env["fix.knowledge.capture"].search([]):
        bump(cap.device_brand, cap.captured_by_id, "captured")
    for rev in env["fix.knowledge.review"].search([("state", "in", ("approved", "reviewed"))]):
        subject = rev.article_id or rev.tree_id
        bump(subject.device_brand, rev.reviewer_id, "reviewed")
    rows = []
    for brand, users in sorted(people.items()):
        concentrated = len(users) < 3
        for name, g in sorted(users.items(), key=lambda kv: -sum(kv[1].values())):
            rows.append(
                {
                    "brand": brand,
                    "person": name,
                    "authored": g["authored"],
                    "captured": g["captured"],
                    "reviewed": g["reviewed"],
                    "holders": len(users),
                    "risk": "CONCENTRATED" if concentrated else "—",
                }
            )
    concentrated = len([b for b, u in people.items() if len(u) < 3])
    return _pack(
        "Expertise Map — %d brand(s), %d concentrated" % (len(people), concentrated),
        ["brand", "person", "authored", "captured", "reviewed", "holders", "risk"],
        {
            "brand": "Brand",
            "person": "Person",
            "authored": "Articles Authored",
            "captured": "Field Captures",
            "reviewed": "Reviews Done",
            "holders": "People on This Brand",
            "risk": "Concentration (< 3 people)",
        },
        rows,
        [
            "Derived from articles (owner), field captures (contributor) and approved reviews "
            "(reviewer), by the content's brand. A brand whose knowledge sits with fewer than "
            "three people is flagged (KPI-C61-12). Nothing on this page is typed."
        ],
        empty="No knowledge contributions yet.",
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
    "expertise_map": expertise_map,
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
    # M61 capture audit: usefulness is the feedback's "resolved it" share;
    # the old views counter was never incremented, so the tile was always 0.
    feedback = env["fix.knowledge.feedback"].search([])
    resolved = len(feedback.filtered(lambda f: f.resolved == "yes"))
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
        "usefulness_score": round(resolved / len(feedback) * 100.0, 1) if feedback else 0.0,
        "reviews_due": len(published.filtered(lambda a: a.review_due and a.review_due <= today)),
        "brand_bulletins_mtd": len(
            bulletins.filtered(lambda b: b.issued_on and b.issued_on >= month_start)
        ),
    }
