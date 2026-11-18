# A12 · M65 Multi-Entity & Localisation — entities, country packs, locale
# packs, jurisdiction rules and payment gateways.
#
# A12 workflow audit (2026-11-04) R4: every surface declares what
# /p03/model/write may set (WRITABLE, merged by controllers/a12/__init__.py);
# lifecycle fields (state, certification stamps, credentials) are NEVER in
# it, and the reports and KPIs below read as the CALLER (no sudo().search([])).
#
# M65 capture audit (2026-11-18): five registers M65's specification owns
# (cd_multi_entity/models/fix_m65_capture.py) are served here, so the Entity
# Structure, Jurisdiction and Translation pages capture what they cover. The
# intercompany page captures through M19's own forms (M19 serves those models).

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
            "action_back_to_draft",
            "action_load_bangladesh_drafts",
        },
    },
    "fix.country.pack.line": {"order": "pack_id", "limit": 500, "actions": set()},
    "fix.locale.pack": {
        "order": "code",
        "limit": 100,
        "actions": {"action_activate", "action_retire"},
    },
    "fix.jurisdiction.rule": {"order": "jurisdiction", "limit": 300, "actions": set()},
    "fix.entity.jurisdiction": {
        "order": "entity_id, pack_kind, assigned_on desc",
        "limit": 300,
        "actions": set(),
    },
    "fix.jurisdiction.residency.rule": {
        "order": "country_id, data_class, effective_from desc",
        "limit": 300,
        "actions": {"action_verify", "action_retire"},
    },
    "fix.country.onboarding": {
        "order": "initiated_on desc, id desc",
        "limit": 100,
        "actions": {"action_advance", "action_abandon"},
    },
    "fix.translation.entry": {
        "order": "create_date desc, id desc",
        "limit": 500,
        "actions": {"action_approve", "action_reject"},
    },
    "fix.rendering.verification": {
        "order": "verified_on desc, id desc",
        "limit": 300,
        "actions": set(),
    },
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
    # M65 capture audit: stamps (assigned/verified/reviewed by, state, phase,
    # applied) move only through create and the actions.
    "fix.entity.jurisdiction": (
        "entity_id",
        "country_pack_id",
        "locale_pack_id",
        "reporting_currency_id",
        "note",
    ),
    "fix.jurisdiction.residency.rule": (
        "country_id",
        "data_class",
        "residency_required",
        "cross_border_permitted",
        "notification_required",
        "safeguard_required",
        "authority_name",
        "statute_reference",
        "effective_from",
    ),
    "fix.country.onboarding": (
        "country_id",
        "lead_id",
        "pack_ids",
        "locale_pack_id",
        "gateway_ids",
        "core_changes_required",
        "core_change_note",
    ),
    "fix.translation.entry": (
        "locale_pack_id",
        "module_code",
        "target_model",
        "target_id",
        "target_field",
        "source_string",
        "translated_string",
        "machine_translated",
    ),
    "fix.rendering.verification": (
        "locale_pack_id",
        "target",
        "device",
        "test_set_ref",
        "verified_on",
        "result",
        "issues",
        "evidence_attachment_id",
    ),
    "fix.payment.gateway": (
        "provider",
        "country_code",
        "currencies",
        # credential_ref enters at creation only (afterwards: Rotate); mode is
        # always system-set. `active` is deliberately absent: archiving a
        # suspended rail reopened checkout (A12 finish E5).
        "mode",
        "credential_ref",
        "settlement_cycle_days",
        "supports_refund",
        "supports_partial_refund",
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
    # M65 capture audit: the country packs each entity is assigned (current only)
    Assignment = env["fix.entity.jurisdiction"]
    by_entity = {}
    for a in Assignment.search([("state", "=", "current")]):
        by_entity[a.entity_id.id] = by_entity.get(a.entity_id.id, Assignment) | a
    rows = []
    for e in entities:
        mine = by_entity.get(e.id, Assignment)
        rows.append(
            {
                "code": e.code or "—",
                "legal_name": e.legal_name,
                "branches": len(e.branch_ids),
                "packs": ", ".join(
                    "%s v%s" % (a.country_pack_id.code, a.pack_version) for a in mine
                )
                or "none assigned",
                "locale": ", ".join(mine.mapped("locale_pack_id.code")) or "—",
                "active": "Yes" if e.active else "No",
            }
        )
    return _pack(
        "Entity Structure — %d legal entit(ies)" % len(rows),
        ["code", "legal_name", "branches", "packs", "locale", "active"],
        {
            "code": "Entity Code",
            "legal_name": "Legal Name",
            "branches": "Branches",
            "packs": "Country Packs In Use",
            "locale": "Default Locale",
            "active": "Active",
        },
        rows,
        [
            "Each entity is a legal company in the group; branches roll up to entities.",
            "Country Packs In Use lists the entity's current pack assignments with the "
            "version assigned. A new assignment supersedes the old one, which stays on "
            "record so older documents can still be traced to the version they used.",
        ],
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
            "load_summary": p.load_summary or "—",
            "state": dict(p._fields["state"].selection).get(p.state, p.state),
        }
        for p in packs
    ]
    return _pack(
        "Country Pack Status",
        [
            "pack",
            "code",
            "kind",
            "version",
            "lines",
            "certified",
            "loaded",
            "load_summary",
            "state",
        ],
        {
            "pack": "Pack",
            "code": "Code",
            "kind": "Kind",
            "version": "Version",
            "lines": "Lines",
            "certified": "Certified On",
            "loaded": "Loaded At",
            "load_summary": "What The Load Did",
            "state": "State",
        },
        rows,
        [
            "Country packs carry divisions/districts, holidays and postcodes. Only a "
            "CERTIFIED pack can be activated and only an ACTIVE pack can be loaded "
            "(P1-4): loading requires certification, not just existence.",
            "Certification is a person's statement that they checked the pack against the "
            "official source. This system does not verify statutory content; the person "
            "who certifies must not be the person who created the pack.",
            "Only an active, loaded holiday pack moves the VAT due date.",
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
            "Coverage is measured: the share of menus and field labels holding a translation "
            "in this language; strings inside code are not counted. A draft pack activates "
            "only at the configured minimum coverage (ir.config_parameter "
            "fix_locale.min_activation_coverage_pct, default 100%), and activating it makes "
            "the language available. Translations themselves come from the language-install "
            "tool.",
        ],
        empty="No locale packs defined.",
    )


def bengali_support(env, date_from=None, date_to=None, **params):
    """Bengali (bn-BD) readiness: the locale pack's declared coverage plus the
    number of code-list entries that actually carry a Bengali label."""
    locales = env["fix.locale.pack"].search([])
    entries = env["fix.mdm.code.entry"].search([])
    with_bn = entries.filtered(lambda e: (e.label_bn or "").strip())
    Verification = env["fix.rendering.verification"]
    targets = dict(Verification._fields["target"].selection)
    rows = []
    for pack in locales:
        latest = Verification.latest_by_target(pack)
        passed = [targets[t] for t, v in latest.items() if v.result == "pass"]
        failed = [targets[t] for t, v in latest.items() if v.result == "fail"]
        unverified = [label for t, label in targets.items() if t not in latest]
        rows.append(
            {
                "locale": pack.code,
                "name": pack.name,
                "coverage_pct": pack.coverage_pct,
                "rendering_pass": ", ".join(passed) or "—",
                "rendering_fail": ", ".join(failed) or "—",
                "rendering_unverified": ", ".join(unverified) or "—",
                "state": dict(pack._fields["state"].selection).get(pack.state, pack.state),
            }
        )
    return _pack(
        "Bengali Support (bn-BD) - %d of %d code entries carry a Bengali label"
        % (len(with_bn), len(entries)),
        [
            "locale",
            "name",
            "coverage_pct",
            "rendering_pass",
            "rendering_fail",
            "rendering_unverified",
            "state",
        ],
        {
            "locale": "Locale",
            "name": "Name",
            "coverage_pct": "Coverage %",
            "rendering_pass": "Renders Correctly On",
            "rendering_fail": "Fails On",
            "rendering_unverified": "Not Yet Verified On",
            "state": "State",
        },
        rows,
        [
            "Coverage is the locale pack's measured string coverage. The Bengali label count "
            "is read from the governed code lists (M64), not estimated.",
            "Rendering is the latest verification recorded per target (Android, iOS, "
            "Windows, thermal and label printers, PDF): a person checked a test set on a "
            "real device and attached the evidence. A target with no verification is "
            "listed as not yet verified, not assumed to work.",
        ],
        empty="No locale packs.",
    )


def translation_completeness(env, date_from=None, date_to=None, **params):
    locales = env["fix.locale.pack"].search([])
    entries = env["fix.translation.entry"].search([])
    rows = []
    for p in locales:
        mine = entries.filtered(lambda e, p=p: e.locale_pack_id == p)
        rows.append(
            {
                "locale": p.code,
                "number_format": dict(p._fields["number_format"].selection).get(p.number_format),
                "date_format": p.date_format,
                "coverage_pct": p.coverage_pct,
                "gap_pct": round(100.0 - (p.coverage_pct or 0.0), 1),
                "in_review": len(mine.filtered(lambda e: e.state == "submitted")),
                "approved": len(mine.filtered(lambda e: e.state == "approved")),
                "rejected": len(mine.filtered(lambda e: e.state == "rejected")),
                "stale": len(mine.filtered(lambda e: e.state == "approved" and e.is_stale)),
            }
        )
    rows.sort(key=lambda r: r["coverage_pct"] or 0.0)
    return _pack(
        "Translation Completeness",
        [
            "locale",
            "number_format",
            "date_format",
            "coverage_pct",
            "gap_pct",
            "in_review",
            "approved",
            "rejected",
            "stale",
        ],
        {
            "locale": "Locale",
            "number_format": "Number Format",
            "date_format": "Date Format",
            "coverage_pct": "Coverage %",
            "gap_pct": "Gap %",
            "in_review": "Awaiting Review",
            "approved": "Approved",
            "rejected": "Rejected",
            "stale": "Approved, Source Since Changed",
        },
        rows,
        [
            "Gap = 100 - coverage. A pack below 100% will fall back to English for the "
            "untranslated strings.",
            "Reviewed translations: a second person approves each one, machine translation "
            "is refused, and an approved translation of a record's text is written into "
            "that record in the locale's language. An approved interface string is a "
            "reviewed record for the language file; approving it changes no screen by "
            "itself.",
            "Stale counts approved translations whose English text has changed since: "
            "they need translating again.",
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
            "credential": "set" if g.sudo().credential_ref else "missing",
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
            "audit chain. Storefront checkout calls assert_live_for_checkout(): only an "
            "ACTIVE gateway in LIVE mode, for this company and country, may take an order.",
            "Storefront checkout is the ONLY reader of this register. Front-desk bKash, "
            "payment links, billing and subscriptions do not consult it, and a rail with "
            "no row (Nagad today) is not gated.",
            "The credential reference is a pointer no integration reads: the storefront's "
            "secret is a system parameter. Rotating it records a routed decision and does "
            "not change a live secret.",
        ],
        empty="No payment gateways configured.",
    )


def expansion_assessment(env, date_from=None, date_to=None, **params):
    """Readiness for a new country: packs loaded, jurisdiction rules captured and
    gateways configured per country code.

    A12 finish E18: Nepal read Ready with an empty draft pack and a sandbox rail.
    Only a certified, active pack with lines and a gateway live for money count."""
    packs = env["fix.country.pack"].search([("state", "=", "active")]).filtered("line_ids")
    rules = env["fix.jurisdiction.rule"].search([("active", "=", True)])
    gateways = env["fix.payment.gateway"].search([("state", "=", "active"), ("mode", "=", "live")])
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
    # M65 capture audit: the onboarding under way per country, and its
    # verified residency rules
    latest = {}
    for o in env["fix.country.onboarding"].search([("phase", "!=", "abandoned")]):
        cc = (o.country_id.code or "??").upper()
        latest.setdefault(cc, o)
        countries.setdefault(cc, {"packs": 0, "rules": 0, "gateways": 0})
    for rule in env["fix.jurisdiction.residency.rule"].search([("state", "=", "verified")]):
        cc = (rule.country_id.code or "??").upper()
        countries.setdefault(cc, {"packs": 0, "rules": 0, "gateways": 0})
        countries[cc]["residency"] = countries[cc].get("residency", 0) + 1
    rows = []
    for cc, v in sorted(countries.items()):
        missing = [k for k in ("packs", "rules", "gateways") if not v[k]]
        if not v.get("residency"):
            missing.append("residency rules")
        onb = latest.get(cc)
        rows.append(
            {
                "country": cc,
                "packs": v["packs"],
                "jurisdiction_rules": v["rules"],
                "residency_rules": v.get("residency", 0),
                "gateways": v["gateways"],
                "onboarding": (
                    "%s (%s)" % (dict(onb._fields["phase"].selection).get(onb.phase), onb.name)
                    if onb
                    else "—"
                ),
                "weeks": onb.elapsed_weeks if onb else "—",
                "readiness": "Ready" if not missing else ("Missing: " + ", ".join(missing)),
            }
        )
    return _pack(
        "Expansion Assessment - %d countr(ies) assessed" % len(rows),
        [
            "country",
            "packs",
            "jurisdiction_rules",
            "residency_rules",
            "gateways",
            "onboarding",
            "weeks",
            "readiness",
        ],
        {
            "country": "Country",
            "packs": "Active Packs With Lines",
            "jurisdiction_rules": "Jurisdiction Rules",
            "residency_rules": "Verified Residency Rules",
            "gateways": "Live Gateways",
            "onboarding": "Onboarding Step",
            "weeks": "Weeks Elapsed (target 12)",
            "readiness": "Readiness",
        },
        rows,
        [
            "A country is Ready only when a certified, active pack with lines, at least one "
            "jurisdiction rule, a verified data residency rule and a gateway live for money "
            "all exist; otherwise the missing pieces are named.",
            "Onboarding Step is the country's onboarding record: each step is refused until "
            "its registers hold what it needs, the pilot is refused if standing the country "
            "up needs a core code change, and a second person approves activation.",
            "Residency rules are verified by a second Platform Admin. Data protection does "
            "not read them yet: they state the rule, they do not enforce it.",
            "Jurisdiction rules are documentation that a person typed: no calculation reads "
            "them, so counting one is not evidence of compliance.",
            "Jurisdiction literals in code (BD weekends, VAT days, statutory forms) are not "
            "yet driven by these registers (BRU-GLO-01/04 are not built).",
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
        # M65 capture audit
        "translations_in_review": env["fix.translation.entry"].search_count(
            [("state", "=", "submitted")]
        ),
        "onboardings_open": env["fix.country.onboarding"].search_count(
            [("phase", "not in", ("active", "abandoned"))]
        ),
    }
