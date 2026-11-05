# A12 · M65 Multi-Entity & Localisation — entities, country packs, locale
# packs, jurisdiction rules and payment gateways.
#
# A12 workflow audit (2026-11-04) R4: every surface declares what
# /p03/model/write may set (WRITABLE, merged by controllers/a12/__init__.py);
# lifecycle fields (state, certification stamps, credentials) are NEVER in
# it, and the reports and KPIs below read as the CALLER (no sudo().search([])).

SURFACES = {
    "fix.country.pack": {
        "order": "name",
        "limit": 100,
        # Lifecycle: draft -validate-> validated -certify-> certified
        # -activate-> active -load-> loaded data -retire-> retired (P1-4).
        "actions": {
            "action_validate",
            "action_certify",
            "action_activate",
            "action_load",
            "action_retire",
        },
    },
    "fix.country.pack.line": {"order": "pack_id", "limit": 500, "actions": set()},
    "fix.locale.pack": {
        "order": "code",
        "limit": 100,
        "actions": {"action_activate", "action_retire"},
    },
    "fix.jurisdiction.rule": {"order": "jurisdiction", "limit": 300, "actions": set()},
    "fix.payment.gateway": {
        "order": "provider",
        "limit": 100,
        # action_activate is NOT a button: activation is M63-routed
        # (P1-4) and runs from the approval inbox.
        "actions": {
            "action_request_approval",
            "action_recall_approval",
            "action_suspend",
            "action_rotate_credential",
        },
    },
}

# R4: the fields a user may legitimately type. Lifecycle state, certification
# stamps and the vault credential reference are set by the guarded actions
# and the server, never by the form endpoint.
WRITABLE = {
    "fix.country.pack": ("name", "code", "kind", "version"),
    "fix.country.pack.line": ("pack_id", "parent_code", "code", "name", "name_bn", "date_value"),
    "fix.locale.pack": (
        "code",
        "name",
        "number_format",
        "first_day_of_week",
        "date_format",
        "coverage_pct",
    ),
    "fix.jurisdiction.rule": (
        "jurisdiction",
        "rule_area",
        "requirement",
        "frequency",
        "authority",
        "penalty",
        "active",
    ),
    "fix.payment.gateway": (
        "provider",
        "country_code",
        "currencies",
        # mode/credential_ref are settable only while the record is a DRAFT:
        # once active, fix.guarded.mixin's _fix_form_locked_fields freezes
        # both at this endpoint AND on the model, so listing them here only
        # enables the initial draft creation (vault reference, sandbox).
        "mode",
        "credential_ref",
        "settlement_cycle_days",
        "supports_refund",
        "supports_partial_refund",
        "active",
    ),
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
    entities = env["fix.entity"].search([])
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
    packs = env["fix.country.pack"].search([])
    rows = [
        {
            "pack": p.name,
            "code": p.code,
            "kind": dict(p._fields["kind"].selection).get(p.kind, p.kind) if p.kind else "—",
            "version": p.version,
            "lines": len(p.line_ids),
            "certified": str(p.certified_on or "—"),
            "loaded": str(p.loaded_at or "—")[:19],
            "state": dict(p._fields["state"].selection).get(p.state, p.state),
        }
        for p in packs
    ]
    return _pack(
        "Country Pack Status",
        ["pack", "code", "kind", "version", "lines", "certified", "loaded", "state"],
        {
            "pack": "Pack",
            "code": "Code",
            "kind": "Kind",
            "version": "Version",
            "lines": "Lines",
            "certified": "Certified On",
            "loaded": "Loaded At",
            "state": "State",
        },
        rows,
        [
            "Country packs carry divisions/districts, holidays and postcodes. Only a "
            "CERTIFIED pack can be activated and only an ACTIVE pack can be loaded "
            "(P1-4): loading requires certification, not just existence.",
        ],
        empty="No country packs loaded.",
    )


def locale_readiness(env, date_from=None, date_to=None, **params):
    packs = env["fix.locale.pack"].search([])
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
        [
            "Coverage is the measured translated-string share of the pack. A draft pack "
            "activates only at the configured minimum coverage "
            "(ir.config_parameter fix_locale.min_activation_coverage_pct, default 100%).",
        ],
        empty="No locale packs defined.",
    )


def bengali_support(env, date_from=None, date_to=None, **params):
    """Bengali (bn-BD) readiness: the locale pack's declared coverage plus the
    number of code-list entries that actually carry a Bengali label."""
    locales = env["fix.locale.pack"].search([])
    entries = env["fix.mdm.code.entry"].search([])
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
    locales = env["fix.locale.pack"].search([])
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


def gateway_readiness(env, date_from=None, date_to=None, **params):
    """Payment gateway rails: state, mode and the countries they serve. The
    credential reference is deliberately NOT shown - only whether one exists."""
    gateways = env["fix.payment.gateway"].search([])
    rows = [
        {
            "provider": g.provider,
            "country": g.country_code or "—",
            "mode": dict(g._fields["mode"].selection).get(g.mode, g.mode),
            "credential": "set" if g.credential_ref else "missing",
            "settlement_days": g.settlement_cycle_days,
            "state": dict(g._fields["state"].selection).get(g.state, g.state),
        }
        for g in gateways
    ]
    return _pack(
        "Payment Gateway Rails — %d configured" % len(rows),
        ["provider", "country", "mode", "credential", "settlement_days", "state"],
        {
            "provider": "Provider",
            "country": "Country",
            "mode": "Mode",
            "credential": "Credential",
            "settlement_days": "Settlement (days)",
            "state": "State",
        },
        rows,
        [
            "Activation is routed (M63) and every transition is written to the security "
            "audit chain. Checkout calls assert_live_for_checkout(): only an ACTIVE "
            "gateway in LIVE mode with a credential set may take a payment; anything "
            "else is refused rather than retried on a rail that is not live.",
        ],
        empty="No payment gateways configured.",
    )


def expansion_assessment(env, date_from=None, date_to=None, **params):
    """Readiness for a new country: packs loaded, jurisdiction rules captured and
    gateways configured per country code."""
    packs = env["fix.country.pack"].search([])
    rules = env["fix.jurisdiction.rule"].search([("active", "=", True)])
    gateways = env["fix.payment.gateway"].search([("state", "=", "active")])
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
REPORTS["gateway_readiness"] = gateway_readiness
REPORTS["expansion_assessment"] = expansion_assessment


def kpis(env):
    entities = env["fix.entity"].search([])
    country = env["fix.country.pack"].search([])
    locales = env["fix.locale.pack"].search([("state", "=", "active")])
    jurisdictions = env["fix.jurisdiction.rule"].search([("active", "=", True)])
    gateways_live = env["fix.payment.gateway"].search(
        [("state", "=", "active"), ("mode", "=", "live")]
    )
    return {
        "entities": len(entities),
        "country_packs": len(country),
        "country_packs_certified": len(
            country.filtered(lambda p: p.state in ("certified", "active"))
        ),
        "locales_active": len(locales),
        "jurisdiction_rules": len(jurisdictions),
        "gateways_live": len(gateways_live),
    }
