# A12 · M65 Multi-Entity & Localisation — entities, country packs, locale
# packs and jurisdiction rules.

SURFACES = {
    "fix.country.pack": {"order": "name", "limit": 100, "actions": set()},
    "fix.country.pack.line": {"order": "pack_id", "limit": 500, "actions": set()},
    "fix.locale.pack": {
        "order": "code",
        "limit": 100,
        "actions": {"action_activate"},
    },
    "fix.jurisdiction.rule": {"order": "jurisdiction", "limit": 300, "actions": set()},
    "fix.payment.gateway": {
        "order": "provider",
        "limit": 100,
        "actions": {"action_activate"},
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


def entity_structure(env, date_from=None, date_to=None, **params):
    entities = env["fix.entity"].sudo().search([])
    rows = [
        {
            "code": e.code or "—",
            "legal_name": e.legal_name,
            "branches": len(e.branch_ids),
            "active": "Yes" if e.active else "No",
        }
        for e in entities
    ]
    return _pack(
        "Entity Structure — %d legal entit(ies)" % len(rows),
        ["code", "legal_name", "branches", "active"],
        {
            "code": "Entity Code",
            "legal_name": "Legal Name",
            "branches": "Branches",
            "active": "Active",
        },
        rows,
        ["Each entity is a legal company in the group; branches roll up to entities."],
        empty="No entities defined.",
    )


def country_pack_status(env, date_from=None, date_to=None, **params):
    packs = env["fix.country.pack"].sudo().search([])
    rows = [
        {
            "pack": p.name,
            "code": p.code,
            "kind": dict(p._fields["kind"].selection).get(p.kind, p.kind) if p.kind else "—",
            "version": p.version,
            "lines": len(p.line_ids),
            "loaded": str(p.loaded_at or "—")[:19],
            "active": "Yes" if p.active else "No",
        }
        for p in packs
    ]
    return _pack(
        "Country Pack Status",
        ["pack", "code", "kind", "version", "lines", "loaded", "active"],
        {
            "pack": "Pack",
            "code": "Code",
            "kind": "Kind",
            "version": "Version",
            "lines": "Lines",
            "loaded": "Loaded At",
            "active": "Active",
        },
        rows,
        ["Country packs carry divisions/districts, holidays and postcodes."],
        empty="No country packs loaded.",
    )


def locale_readiness(env, date_from=None, date_to=None, **params):
    packs = env["fix.locale.pack"].sudo().search([])
    rows = [
        {
            "locale": p.code,
            "name": p.name,
            "number_format": dict(p._fields["number_format"].selection).get(p.number_format),
            "coverage": p.coverage_pct,
            "state": dict(p._fields["state"].selection).get(p.state, p.state),
        }
        for p in packs
    ]
    return _pack(
        "Locale Pack Readiness",
        ["locale", "name", "number_format", "coverage", "state"],
        {
            "locale": "Locale",
            "name": "Name",
            "number_format": "Number Format",
            "coverage": "Coverage %",
            "state": "State",
        },
        rows,
        ["Coverage is the measured translated-string share of the pack."],
        empty="No locale packs defined.",
    )


def bengali_support(env, date_from=None, date_to=None, **params):
    """Bengali (bn-BD) readiness: the locale pack's declared coverage plus the
    number of code-list entries that actually carry a Bengali label."""
    locales = env["fix.locale.pack"].sudo().search([])
    entries = env["fix.mdm.code.entry"].sudo().search([])
    with_bn = entries.filtered(lambda e: (e.label_bn or "").strip())
    rows = []
    for pack in locales:
        rows.append(
            {
                "locale": pack.code,
                "name": pack.name,
                "coverage_pct": pack.coverage_pct,
                "state": dict(pack._fields["state"].selection).get(pack.state, pack.state),
            }
        )
    return _pack(
        "Bengali Support (bn-BD) - %d of %d code entries carry a Bengali label"
        % (len(with_bn), len(entries)),
        ["locale", "name", "coverage_pct", "state"],
        {"locale": "Locale", "name": "Name", "coverage_pct": "Coverage %", "state": "State"},
        rows,
        [
            "Coverage is the locale pack's measured string coverage. The Bengali label count "
            "is read from the governed code lists (M64), not estimated."
        ],
        empty="No locale packs.",
    )


def translation_completeness(env, date_from=None, date_to=None, **params):
    locales = env["fix.locale.pack"].sudo().search([])
    rows = [
        {
            "locale": p.code,
            "number_format": dict(p._fields["number_format"].selection).get(p.number_format),
            "date_format": p.date_format,
            "coverage_pct": p.coverage_pct,
            "gap_pct": round(100.0 - (p.coverage_pct or 0.0), 1),
        }
        for p in locales
    ]
    rows.sort(key=lambda r: r["coverage_pct"] or 0.0)
    return _pack(
        "Translation Completeness",
        ["locale", "number_format", "date_format", "coverage_pct", "gap_pct"],
        {
            "locale": "Locale",
            "number_format": "Number Format",
            "date_format": "Date Format",
            "coverage_pct": "Coverage %",
            "gap_pct": "Gap %",
        },
        rows,
        [
            "Gap = 100 - coverage. A pack below 100% will fall back to English for the "
            "untranslated strings."
        ],
        empty="No locale packs.",
    )


def expansion_assessment(env, date_from=None, date_to=None, **params):
    """Readiness for a new country: packs loaded, jurisdiction rules captured and
    gateways configured per country code."""
    packs = env["fix.country.pack"].sudo().search([])
    rules = env["fix.jurisdiction.rule"].sudo().search([("active", "=", True)])
    gateways = env["fix.payment.gateway"].sudo().search([("state", "=", "active")])
    countries = {}
    for pack in packs:
        cc = (pack.code or "")[:2] or "??"
        countries.setdefault(cc, {"packs": 0, "rules": 0, "gateways": 0})
        countries[cc]["packs"] += 1
    for rule in rules:
        cc = (rule.jurisdiction or "")[:2]
        countries.setdefault(cc, {"packs": 0, "rules": 0, "gateways": 0})
        countries[cc]["rules"] += 1
    for gw in gateways:
        cc = gw.country_code or "??"
        countries.setdefault(cc, {"packs": 0, "rules": 0, "gateways": 0})
        countries[cc]["gateways"] += 1
    rows = []
    for cc, v in sorted(countries.items()):
        missing = [k for k in ("packs", "rules", "gateways") if not v[k]]
        rows.append(
            {
                "country": cc,
                "packs": v["packs"],
                "jurisdiction_rules": v["rules"],
                "gateways": v["gateways"],
                "readiness": "Ready" if not missing else ("Missing: " + ", ".join(missing)),
            }
        )
    return _pack(
        "Expansion Assessment - %d countr(ies) assessed" % len(rows),
        ["country", "packs", "jurisdiction_rules", "gateways", "readiness"],
        {
            "country": "Country",
            "packs": "Country Packs",
            "jurisdiction_rules": "Jurisdiction Rules",
            "gateways": "Active Gateways",
            "readiness": "Readiness",
        },
        rows,
        [
            "A country is Ready only when a pack, at least one jurisdiction rule and an active "
            "gateway all exist; otherwise the missing pieces are named."
        ],
        empty="No country data.",
    )


REPORTS = {
    "entity_structure": entity_structure,
    "country_pack_status": country_pack_status,
    "locale_readiness": locale_readiness,
}

REPORTS["bengali_support"] = bengali_support
REPORTS["translation_completeness"] = translation_completeness
REPORTS["expansion_assessment"] = expansion_assessment


def kpis(env):
    entities = env["fix.entity"].sudo().search([])
    country = env["fix.country.pack"].sudo().search([])
    locales = env["fix.locale.pack"].sudo().search([("state", "=", "active")])
    jurisdictions = env["fix.jurisdiction.rule"].sudo().search([("active", "=", True)])
    return {
        "entities": len(entities),
        "country_packs": len(country),
        "locales_active": len(locales),
        "jurisdiction_rules": len(jurisdictions),
    }
