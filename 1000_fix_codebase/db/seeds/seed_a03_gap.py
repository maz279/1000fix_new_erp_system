"""seed_a03_gap.py - synthetic seed rows for the A03 gap-closure models.

Why this exists. The A03 gap-closure build (S1-S10 + module rows) added 29
models and 53 screens, and `seed.py` was never extended to cover them. The
seed manifest promises "every transactional anchor and config master carries
seed rows"; for these 29 it did not, so on a developer database every new
screen opened on "0 records" and the build looked identical to the one before
it. This file closes that, under the same manifest rules:

  * synthetic only (DE-12), Bengali-first (DE-17), fixed seed;
  * state-complete where the model has a lifecycle (DE-16);
  * idempotent: every block looks for its own `SEED-A03-` marker first, so a
    second run creates nothing;
  * no outbound anything (DE-11): providers are `manual` transport and the
    grounding service runs with generation off.

Transactional rows are produced by the PRODUCTION services - `queue()`,
`intake()`, `set_presence()`, `enrol()`, `action_run()`, `record_answers()`,
`mine_from_traffic()`, `ask()` - never written field-by-field, so the seed is
also a smoke test of the build against a real estate.

It runs inside the ORM because those services take recordsets, which the
JSON-RPC client in `seed.py` cannot pass:

    PYTHONPATH=. .venv/Scripts/python.exe vendor/odoo/odoo-bin shell \
        -c infra/odoo-conf/local.resolved.conf -d fix_dev --no-http \
        < db/seeds/seed_a03_gap.py

Each block runs in its own savepoint and reports, so one refusal from a
business rule is visible without hiding what the other blocks did.
"""

import time
from contextlib import contextmanager
from datetime import timedelta

MARK = "SEED-A03-"
RESULTS = []


def seed(env):
    from odoo import fields
    from odoo.exceptions import UserError

    ou = env["operating.unit"].search([], limit=1)
    now = fields.Datetime.now()
    today = fields.Date.context_today(env["res.users"])

    @contextmanager
    def block(name):
        started = time.monotonic()
        print(f"seed_a03_gap: >> {name}", flush=True)
        try:
            with env.cr.savepoint():
                yield
            RESULTS.append(("ok", name, "%.1fs" % (time.monotonic() - started)))
        except Exception as exc:
            first = (str(exc).strip().splitlines() or [""])[0]
            RESULTS.append(("FAIL", name, f"{type(exc).__name__}: {first[:220]}"))

    def ensure(model, domain, vals):
        rec = env[model].search(domain, limit=1)
        return rec or env[model].create(vals)

    customers = env["res.partner"].search(
        [("email", "like", "seed.customer%"), ("phone", "!=", False)],
        order="id",
        limit=60,
    )
    # Contact-centre agents are EMPLOYEES. seed.py's users carry only workspace
    # groups (share=True), so routing rightly refuses to let them pick work.
    internal = env.ref("base.group_user")
    agents = env["res.users"].browse()
    for i, (given, family) in enumerate(
        (
            ("রাহাত", "হোসেন"),
            ("ফারিয়া", "ইসলাম"),
            ("সাব্বির", "আহমেদ"),
            ("নাজমা", "আক্তার"),
            ("আরিফ", "রহমান"),
            ("তাসনিম", "চৌধুরী"),
            ("মেহেদী", "হাসান"),
            ("জান্নাত", "ফেরদৌস"),
        )
    ):
        login = f"seed.cc.agent{i + 1:02d}@1000fix.local"
        agents |= env["res.users"].search([("login", "=", login)], limit=1) or env[
            "res.users"
        ].create(
            {
                "name": f"{given} {family}",
                "login": login,
                "email": login,
                "group_ids": [(6, 0, internal.ids)],
                "cc_skills": "laptop,bengali" if i % 2 else "mobile,bengali,english",
            }
        )
    Status = env["fix.cc.presence.status"]
    available = Status.search([("is_available_class", "=", True)], order="sequence", limit=1)
    voice_q = env["fix.cc.queue"].search([("channel", "=", "voice")], limit=1)
    notice = env["fix.transparency.notice"].search([], limit=1)

    def grant(partner, purpose, channel):
        return env["fix.consent"].create(
            {
                "partner_id": partner.id,
                "purpose": purpose,
                "channel": channel,
                "state": "granted",
                "proof": MARK + "OTP",
                "notice_version_id": notice.id,
            }
        )

    # ------------------------------------------------------------------ queues
    with block("M27 queues"):
        wa_q = ensure(
            "fix.cc.queue",
            [("code", "=", MARK + "WA")],
            {
                "name": "হোয়াটসঅ্যাপ সহায়তা (WhatsApp Support)",
                "code": MARK + "WA",
                "channel": "whatsapp",
            },
        )
        mail_q = ensure(
            "fix.cc.queue",
            [("code", "=", MARK + "MAIL")],
            {
                "name": "ইমেইল ব্যাক-অফিস (Email Back Office)",
                "code": MARK + "MAIL",
                "channel": "email",
            },
        )

    # ------------------------------------------------- S1 providers + deliveries
    with block("S1 notification providers"):
        for code, name, channel, cost, mask in (
            ("SMS", "এসএমএস গেটওয়ে — ম্যানুয়াল (SMS Gateway, manual)", "sms", 0.35, "1000FiX"),
            ("WA", "হোয়াটসঅ্যাপ বিজনেস — ম্যানুয়াল (WhatsApp Business, manual)", "whatsapp", 0.85, False),
            ("EMAIL", "ইমেইল — ম্যানুয়াল (Email, manual)", "email", 0.0, False),
        ):
            ensure(
                "fix.notif.provider",
                [("code", "=", MARK + code)],
                {
                    "name": name,
                    "code": MARK + code,
                    "channel": channel,
                    "transport": "manual",
                    "cost_per_message": cost,
                    "sender_mask": mask,
                },
            )

    Delivery = env["fix.notif.delivery"]
    ready_bn = "আপনার ডিভাইস মেরামত সম্পন্ন — শাখা থেকে সংগ্রহ করুন। হটলাইন ১৬৭৪৩।"
    with block("S1 deliveries (state-complete)"):
        if not Delivery.search_count([("dedup_key", "like", MARK + "%")]):
            plan = (
                [("sms", "service_updates", "contract", ready_bn)] * 12
                + [("sms", "marketing", "consent", "বর্ষার এসি সার্ভিস অফার — ২০% ছাড়।")] * 6
                + [("whatsapp", "service_updates", "contract", ready_bn)] * 4
                + [("email", "service_updates", "contract", ready_bn)] * 3
            )
            made = Delivery.browse()
            for n, (channel, purpose, basis, body) in enumerate(plan):
                made |= Delivery.queue(
                    channel=channel,
                    purpose=purpose,
                    partner=customers[n],
                    body=body,
                    lawful_basis=basis,
                    dedup_key=f"{MARK}DLV-{n:03d}",
                    source_model="res.partner",
                    source_id=customers[n].id,
                )
            queued = made.filtered(lambda d: d.state == "queued")
            for d in queued[:9]:
                d.action_mark_sent_manually(provider_ref=f"{MARK}REF-{d.id}")
            for d in queued[:5]:
                d.mark_delivered(provider_ref=f"{MARK}REF-{d.id}")
            queued[9:10].mark_failed("অপারেটর নম্বরটি প্রত্যাখ্যান করেছে (handset unreachable)")
            queued[10:11].action_cancel(
                reason="গ্রাহক শাখায় এসে নিজেই সংগ্রহ করেছেন (collected in person)"
            )

    # --------------------------------------------------- S3/S4 routing + presence
    with block("S3 capacity profiles"):
        cap = {}
        for code, name, limit, reset in (
            ("VOICE", "ভয়েস — একসাথে একটি কল (Voice, one at a time)", 1, "immediate"),
            ("CHAT", "চ্যাট — একসাথে তিনটি (Chat, three concurrent)", 3, "immediate"),
            ("URGENT", "জরুরি — অতিরিক্ত একটি (Urgent add-on)", 1, "immediate"),
            ("EMAIL", "ইমেইল — দৈনিক কোটা (Email daily quota)", 20, "end_of_day"),
        ):
            cap[code] = ensure(
                "fix.cc.capacity.profile",
                [("code", "=", MARK + code)],
                {
                    "name": name,
                    "code": MARK + code,
                    "work_item_limit": limit,
                    "reset_frequency": reset,
                },
            )

    WS = env["fix.routing.workstream"]
    with block("S3 workstreams + bullseye rings"):
        ws_voice = WS.search([("code", "=", MARK + "WS-VOICE")], limit=1)
        if not ws_voice:
            ws_voice = WS.create(
                {
                    "name": "১৬৭৪৩ ভয়েস সার্ভিস ডেস্ক (16743 Voice Service Desk)",
                    "code": MARK + "WS-VOICE",
                    "channel": "voice",
                    "work_type": "conversation",
                    "queue_id": voice_q.id,
                    "default_capacity_profile_id": cap["VOICE"].id,
                    "assignment_method": "pick",
                    "prefer_last_agent": True,
                    "prefer_last_agent_days": 14,
                }
            )
            for seq, name, wait in (
                (10, "প্রথম বলয় — অভিজ্ঞ এজেন্ট (Ring 1: senior agents)", 20),
                (20, "দ্বিতীয় বলয় — সকল এজেন্ট (Ring 2: all agents)", 45),
            ):
                env["fix.routing.bullseye.ring"].create(
                    {
                        "workstream_id": ws_voice.id,
                        "sequence": seq,
                        "name": name,
                        "wait_seconds": wait,
                    }
                )
            ws_voice.write({"assignment_method": "bullseye"})
        ws_wa = ensure(
            "fix.routing.workstream",
            [("code", "=", MARK + "WS-WA")],
            {
                "name": "হোয়াটসঅ্যাপ কথোপকথন (WhatsApp Conversations)",
                "code": MARK + "WS-WA",
                "channel": "whatsapp",
                "work_type": "conversation",
                "queue_id": wa_q.id,
                "default_capacity_profile_id": cap["CHAT"].id,
                "assignment_method": "push",
                "allowed_presence_ids": [(6, 0, available.ids)],
            },
        )
        ws_mail = ensure(
            "fix.routing.workstream",
            [("code", "=", MARK + "WS-MAIL")],
            {
                "name": "ইমেইল ও রেকর্ড কাজ (Email & Record Work)",
                "code": MARK + "WS-MAIL",
                "channel": "email",
                "work_type": "record",
                "queue_id": mail_q.id,
                "default_capacity_profile_id": cap["EMAIL"].id,
                "assignment_method": "pick",
            },
        )

    AgentState = env["fix.cc.agent.state"]
    with block("S4 agent presence + history"):
        if not env["fix.cc.agent.state.log"].search_count([("agent_id", "in", agents.ids)]):
            plan = ["available"] * 5 + ["busy", "busy_dnd", "offline"]
            for agent, final in zip(agents, plan, strict=False):
                state = AgentState.state_for(agent)
                state.set_presence("available", source="shift")
                if final != "available":
                    state.set_presence(final, source="manual")

    with block("M27 WFM shifts + adherence"):
        Shift = env["fix.cc.wfm.shift"]
        if not Shift.search_count([("agent_id", "in", agents.ids), ("shift_date", "=", today)]):
            local_hour = (now + timedelta(hours=6)).hour
            start = max(0, local_hour - 2)
            for agent in agents:
                for day in (today - timedelta(days=1), today):
                    Shift.create(
                        {
                            "agent_id": agent.id,
                            "queue_id": voice_q.id,
                            "shift_date": day,
                            "start_hour": start,
                            "end_hour": min(24, start + 8),
                            "state": "confirmed",
                        }
                    )
        Adh = env["fix.cc.wfm.adherence"]
        Adh.compute_for_date(today - timedelta(days=1))
        Adh.compute_for_date(today)

    # Conversations: a live queue (M27-queue shows new/with_ai/with_agent) and a
    # scrubbed history the intent miner is allowed to read (SC-003).
    Conv = env["fix.conversation"]
    live, history = Conv.browse(), Conv.browse()
    with block("M27 live conversations + scrubbed history"):
        live = Conv.search([("call_sid", "like", MARK + "LIVE%")])
        if not live:
            for n, (channel, state, intent) in enumerate(
                [("voice", "new", "order_status")] * 4
                + [("whatsapp", "with_ai", "warranty_query")] * 3
                + [("voice", "with_agent", "battery_issue")] * 3
            ):
                live |= Conv.create(
                    {
                        "channel": channel,
                        "state": state,
                        "intent": intent,
                        "call_sid": f"{MARK}LIVE-{n:02d}",
                        "contact_identity": customers[30 + n].phone,
                        "customer_id": customers[30 + n].id,
                        "queue_id": (wa_q if channel == "whatsapp" else voice_q).id,
                        "operating_unit_id": ou.id,
                        "started_at": now - timedelta(minutes=3 + 4 * n),
                        "queued_at": now - timedelta(minutes=2 + 4 * n),
                    }
                )
        history = Conv.search([("call_sid", "like", MARK + "HIST%")])
        if not history:
            phrases = [
                ("bn", "আমার ওয়ারেন্টি ক্লেইম এর অবস্থা কি"),
                ("bn", "পিকআপ কখন আসবে আজকে"),
                ("en", "warranty claim status please"),
                ("en", "when will pickup arrive"),
            ]
            disposition = env["fix.cc.disposition"].search([], limit=1)
            for n in range(8):
                conv = Conv.create(
                    {
                        "channel": "voice" if n % 2 else "chat",
                        "state": "resolved_agent" if n % 3 else "resolved_ai",
                        "ai_resolved": not n % 3,
                        "pii_masked": True,
                        "call_sid": f"{MARK}HIST-{n:02d}",
                        "customer_id": customers[40 + n].id,
                        "agent_id": agents[n % len(agents)].id,
                        "queue_id": voice_q.id,
                        "operating_unit_id": ou.id,
                        "intent": "warranty_query" if n % 2 else "order_status",
                        "disposition_id": disposition.id if n % 3 else False,
                        "started_at": now - timedelta(days=n + 1),
                    }
                )
                for k in range(3):
                    lang, text = phrases[(n + k) % len(phrases)]
                    env["fix.conversation.turn"].create(
                        {
                            "conversation_id": conv.id,
                            "sequence": 10 * (k + 1),
                            "speaker": "customer",
                            "lang": lang,
                            "text": text,
                        }
                    )
                history |= conv

    with block("S3 work items via intake + assignment"):
        Item = env["fix.routing.workitem"]
        if not Item.search_count([("workstream_id", "in", (ws_voice | ws_wa | ws_mail).ids)]):
            for conv in live:
                ws = ws_wa if conv.channel == "whatsapp" else ws_voice
                item = ws.intake(
                    "fix.conversation",
                    conv.id,
                    partner=conv.customer_id,
                    context_values={
                        "urgency_level": "critical" if conv.state == "with_agent" else "low"
                    },
                )
                if conv.state == "with_agent":
                    item.action_assign_manually(
                        agent=agents[0],
                        reason="ডিউটি ম্যানেজার নিযুক্ত করেছেন (duty manager assignment)",
                    )
            for n, partner in enumerate(customers[50:55]):
                item = ws_mail.intake("res.partner", partner.id, partner=partner)
                if n < 3:
                    item.with_user(agents[n + 1]).action_pick()
                if n == 0:
                    item.close_and_release(session_closed=True)
            ws_voice.assign_pending()
            ws_wa.assign_pending()

    # ------------------------------------------------ M27 productivity + quality
    with block("M27 macros + knowledge bindings"):
        template = env["fix.cc.notif.template"].search([], limit=1)
        macros = {}
        for code, name, action, extra in (
            ("CSAT", "সিস্যাট জরিপ পাঠান (Send CSAT survey)", "dispatch_csat", {}),
            (
                "READY",
                "মেরামত-সম্পন্ন এসএমএস (Repair-ready SMS)",
                "send_template",
                {"template_id": template.id},
            ),
            (
                "FIELD",
                "অন-সাইট টেকনিশিয়ান বুক (Book on-site technician)",
                "create_field_order",
                {"confirm_required": True},
            ),
            ("CMPL", "অভিযোগ নথিভুক্ত (Log a complaint)", "raise_complaint", {}),
            ("HANDOFF", "মানব এজেন্টে হস্তান্তর (Hand off to a human)", "handoff_agent", {}),
        ):
            macros[code] = ensure(
                "fix.cc.macro",
                [("code", "=", MARK + code)],
                {
                    "name": name,
                    "code": MARK + code,
                    "macro_action": action,
                    **extra,
                },
            )
        kb = {}
        for ref, intent, note in (
            (
                "KB-A03-WARRANTY-BN",
                "warranty_query",
                "ওয়ারেন্টি যোগ্যতা যাচাইয়ের ধাপ (warranty eligibility steps)",
            ),
            (
                "KB-A03-BATTERY-BN",
                "battery_issue",
                "ব্যাটারি ফুলে যাওয়া — নিরাপত্তা নির্দেশনা (swollen battery safety)",
            ),
            ("KB-A03-RESET-BN", "reset_request", "ফ্যাক্টরি রিসেটের আগে ব্যাকআপ (backup before reset)"),
            (
                "KB-A03-ORDER-STATUS",
                "order_status",
                "অর্ডার স্ট্যাটাস পড়ে শোনানোর নিয়ম (reading order status aloud)",
            ),
        ):
            kb[intent] = ensure(
                "fix.cc.knowledge.binding",
                [("article_ref", "=", ref)],
                {
                    "article_ref": ref,
                    "intent": intent,
                    "queue_id": voice_q.id,
                    "note": note,
                },
            )

    with block("M27 guided scripts + adherence"):
        Script = env["fix.cc.script"]
        script = Script.search([("code", "=", MARK + "SCR-STATUS")], limit=1)
        if not script:
            script = Script.create(
                {
                    "name": "Order status enquiry",
                    "name_bn": "অর্ডার স্ট্যাটাস জিজ্ঞাসা",
                    "code": MARK + "SCR-STATUS",
                    "queue_id": voice_q.id,
                    "intent": "order_status",
                }
            )
            for seq, name, instruction, extra in (
                (10, "অভিবাদন (Greet)", "১০০০ফিক্স-এ স্বাগতম জানিয়ে নিজের নাম বলুন।", {}),
                (
                    20,
                    "পরিচয় যাচাই (Verify identity)",
                    "জাতীয় পরিচয়পত্রের শেষ চার অঙ্ক নিশ্চিত করুন।",
                    {"is_mandatory": True},
                ),
                (
                    30,
                    "স্ট্যাটাস জানান (Read the status)",
                    "অর্ডারের বর্তমান ধাপ ও আনুমানিক সময় বলুন।",
                    {"knowledge_binding_id": kb["order_status"].id},
                ),
                (
                    40,
                    "এসএমএস প্রস্তাব (Offer SMS)",
                    "সংগ্রহের সময় হলে এসএমএস পাঠানোর প্রস্তাব দিন।",
                    {"macro_id": macros["READY"].id},
                ),
            ):
                env["fix.cc.script.step"].create(
                    {
                        "script_id": script.id,
                        "sequence": seq,
                        "name": name,
                        "instruction": instruction,
                        **extra,
                    }
                )
            script.action_publish()
        Completion = env["fix.cc.script.completion"]
        if not Completion.search_count([("script_id", "=", script.id)]):
            for conv in history.filtered(lambda c: c.intent == "order_status"):
                for step in script.step_ids.sorted("sequence"):
                    skip = step.sequence == 40 and conv.id % 2 == 0
                    Completion.create(
                        {
                            "conversation_id": conv.id,
                            "script_id": script.id,
                            "step_id": step.id,
                            "agent_id": (conv.agent_id or agents[0]).id,
                            "skipped": skip,
                            "skip_reason": "গ্রাহক এসএমএস চাননি (customer declined SMS)"
                            if skip
                            else False,
                        }
                    )

    with block("M27 QA rubric + evaluations"):
        rubric = env["fix.cc.qa.rubric"].search([("code", "=", MARK + "RUB-BOTH")], limit=1)
        if not rubric:
            rubric = env["fix.cc.qa.rubric"].create(
                {
                    "name": "এআই ও মানব একই মানদণ্ড (One rubric for AI and humans)",
                    "code": MARK + "RUB-BOTH",
                    "applies_to": "both",
                    "criterion_ids": [
                        (
                            0,
                            0,
                            {
                                "sequence": 10,
                                "code": "disp",
                                "name": "ডিসপোজিশন নথিভুক্ত (Disposition set)",
                                "weight": 30.0,
                                "measure": "disposition_set",
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "sequence": 20,
                                "code": "wrap",
                                "name": "র‍্যাপ-আপ মান (Wrap-up quality)",
                                "weight": 20.0,
                                "measure": "wrapup_quality",
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "sequence": 30,
                                "code": "script",
                                "name": "স্ক্রিপ্ট অনুসরণ (Script adherence)",
                                "weight": 20.0,
                                "measure": "script_adherence",
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "sequence": 40,
                                "code": "rec",
                                "name": "রেকর্ডিং সম্মতি (Recording integrity)",
                                "weight": 15.0,
                                "measure": "recording_integrity",
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "sequence": 50,
                                "code": "fcr",
                                "name": "প্রথম যোগাযোগে সমাধান (First-contact resolution)",
                                "weight": 15.0,
                                "measure": "fcr",
                            },
                        ),
                    ],
                }
            )
            rubric.action_publish()
            for conv in history:
                env["fix.cc.qa.evaluation"].evaluate_conversation(conv, rubric)

    # ------------------------------------------------------------- M32 assistant
    with block("M32 LLM providers"):
        for code, name, residency, latency, state, ctx in (
            (
                "LLM-CHAT",
                "স্বয়ং-হোস্টেড Ollama — চ্যাট (Self-hosted Ollama, chat)",
                "self_hosted",
                "chat",
                "active",
                True,
            ),
            (
                "LLM-VOICE",
                "স্বয়ং-হোস্টেড Ollama — ভয়েস (Self-hosted Ollama, voice)",
                "self_hosted",
                "voice",
                "draft",
                True,
            ),
            (
                "LLM-OFFSHORE",
                "অফশোর এপিআই — নিষ্ক্রিয় (Offshore API, disabled)",
                "offshore",
                "batch",
                "disabled",
                False,
            ),
        ):
            ensure(
                "fix.assistant.llm.provider",
                [("code", "=", MARK + code)],
                {
                    "name": name,
                    "code": MARK + code,
                    "residency": residency,
                    "latency_profile": latency,
                    "state": state,
                    "may_receive_customer_context": ctx,
                    "endpoint_config_key": "FIX_OLLAMA_MODEL"
                    if residency == "self_hosted"
                    else False,
                },
            )

    with block("M32 grounded asks"):
        Ask = env["fix.assistant.ask"]
        if not Ask.search_count([]):
            Intent = env["fix.assistant.intent"]
            for question, intent, lang in (
                ("আমার ল্যাপটপের ওয়ারেন্টি কি এখনও আছে?", "warranty_query", "bn"),
                ("Is my laptop still under warranty?", "warranty_query", "en"),
                ("ফোনের ব্যাটারি ফুলে গেছে, কী করব?", "battery_issue", "bn"),
                ("রিসেট করলে কি সব ডেটা মুছে যাবে?", "reset_request", "bn"),
                ("What time does the Dhanmondi branch close?", "store.hours", "en"),
                ("আমার অর্ডার কোন ধাপে আছে?", "order_status", "bn"),
                ("Can you write me a poem about rain?", "nonsense_intent", "en"),
                ("   ", None, "bn"),
            ):
                Intent.ask(
                    question,
                    intent=intent,
                    consumer="m27_agent_assist",
                    language=lang,
                    allow_generative=False,
                )

    with block("M32 intent mining (scrubbed traffic only)"):
        Cand = env["fix.assistant.intent.candidate"]
        if not Cand.search_count([]):
            result = Cand.mine_from_traffic(days=30)
            if not result.get("created"):
                raise UserError("miner created nothing: {}".format(result.get("note")))
            mined = Cand.search([], order="frequency desc")
            if len(mined) >= 3:
                mined[1].action_accept(note="নতুন ইনটেন্ট হিসেবে গ্রহণ (accepted as a new intent)")
                mined[2].action_reject(note="খুব সাধারণ বাক্যাংশ (too generic)")

    # ------------------------------------------------------------- M33 dedup
    with block("S8 duplicate-detection jobs"):
        Job = env["fix.dedup.job"]
        if not Job.search_count([("name", "like", MARK + "%")]):
            # An exact BIN rule, not the estate's fuzzy name+phone rule: seed.py
            # re-runs append the same 200 synthetic customers, so a full
            # name+phone sweep of a dev database correctly raises ~240k pairs -
            # a flooded steward queue, not a seed.
            rules = ensure(
                "fix.dedup.rule",
                [("name", "=", MARK + "BIN exact")],
                {
                    "name": MARK + "BIN exact",
                    "match_fields": "vat",
                    "scope": "exact",
                    "action": "flag",
                },
            )
            nightly = Job.create(
                {
                    "name": MARK + "রাত্রিকালীন সদৃশ অনুসন্ধান (Nightly duplicate sweep)",
                    "scheduled": True,
                    "rule_ids": [(6, 0, rules.ids)],
                }
            )
            nightly.action_run()
            Job.create(
                {
                    "name": MARK + "পরবর্তী সাপ্তাহিক অনুসন্ধান (Next weekly sweep)",
                    "rule_ids": [(6, 0, rules.ids)],
                }
            )

    # ------------------------------------------------------------- M07 cadences
    with block("M07 sales sequences + enrolments"):
        Seq = env["fix.crm.sequence"]
        cadence = Seq.search([("code", "=", MARK + "SEQ-CORP")], limit=1)
        if not cadence:
            cadence = Seq.create(
                {
                    "name": "কর্পোরেট লিড — প্রথম যোগাযোগ (Corporate lead first touch)",
                    "code": MARK + "SEQ-CORP",
                    "applies_to": "lead",
                    "sequence_kind": "cadence",
                    "first_touch_sla_hours": 4.0,
                }
            )
            for seq, name, kind, instruction in (
                (
                    10,
                    "পরিচিতি কল (Intro call)",
                    "call",
                    "১০০০ফিক্স কর্পোরেট এএমসি পরিচয় করিয়ে দিন এবং ডিভাইস সংখ্যা জানুন।",
                ),
                (20, "প্রস্তাব ইমেইল (Proposal email)", "email", "ডিভাইস সংখ্যা অনুযায়ী এএমসি প্রস্তাব পাঠান।"),
                (
                    30,
                    "অফিস পরিদর্শন (Site visit)",
                    "visit",
                    "আইটি ম্যানেজারের সাথে সাইট পরিদর্শন নির্ধারণ করুন।",
                ),
                (40, "শেষ (Exit)", "exit", False),
            ):
                env["fix.crm.sequence.step"].create(
                    {
                        "sequence_id": cadence.id,
                        "sequence": seq,
                        "name": name,
                        "step_type": kind,
                        "instructions": instruction,
                    }
                )
            cadence.action_activate()
        playbook = Seq.search([("code", "=", MARK + "SEQ-AMC")], limit=1)
        if not playbook:
            playbook = Seq.create(
                {
                    "name": "এএমসি নবায়ন প্লেবুক (AMC renewal playbook)",
                    "code": MARK + "SEQ-AMC",
                    "applies_to": "both",
                    "sequence_kind": "playbook",
                }
            )
            env["fix.crm.sequence.step"].create(
                {
                    "sequence_id": playbook.id,
                    "sequence": 10,
                    "name": "নবায়ন কল (Renewal call)",
                    "step_type": "call",
                    "instructions": "মেয়াদ শেষের ৬০ দিন আগে নবায়নের শর্ত আলোচনা করুন।",
                }
            )
            env["fix.crm.sequence.step"].create(
                {
                    "sequence_id": playbook.id,
                    "sequence": 20,
                    "name": "শেষ (Exit)",
                    "step_type": "exit",
                }
            )
            playbook.action_activate()
        Enrol = env["fix.crm.sequence.enrolment"]
        if not Enrol.search_count([("sequence_id", "in", (cadence | playbook).ids)]):
            leads = env["crm.lead"].search([], order="id", limit=12)
            cadence.enrol(leads[:8])
            playbook.enrol(leads[8:12])
            Seq.cron_advance_sequences()

    # ------------------------------------------------------------- M10 loyalty
    program = env["fix.loyalty.program"].search([], limit=1)
    silver = env["fix.loyalty.tier"].search([("program_id", "=", program.id)], limit=1)
    Account = env["fix.loyalty.account"]
    with block("M10 loyalty members"):
        have = Account.search([("partner_id", "in", customers[:12].ids)])
        for partner in customers[:12] - have.mapped("partner_id"):
            Account.create(
                {
                    "partner_id": partner.id,
                    "program_id": program.id,
                    "tier_id": silver.id,
                    "operating_unit_id": ou.id,
                    "name": f"{MARK}LOY-{partner.id:05d}",
                }
            )
    accounts = Account.search([("partner_id", "in", customers[:12].ids)], order="id")

    with block("M10 point types + affiliations"):
        for code, name, name_bn, klass, bdt, months in (
            ("PT-FIX", "FiX Points", "ফিক্স পয়েন্ট", "redeemable", 0.25, 24),
            ("PT-STATUS", "Status Points", "স্ট্যাটাস পয়েন্ট", "qualifying", 0.0, 12),
        ):
            ensure(
                "fix.loyalty.point.type",
                [("code", "=", MARK + code)],
                {
                    "name": name,
                    "name_bn": name_bn,
                    "code": MARK + code,
                    "program_id": program.id,
                    "point_class": klass,
                    "bdt_per_point": bdt,
                    "expiry_months": months,
                },
            )
        dealer = ensure(
            "fix.loyalty.affiliation",
            [("code", "=", MARK + "AFF-DEALER")],
            {
                "name": "Dealer Technicians",
                "name_bn": "ডিলার টেকনিশিয়ান",
                "code": MARK + "AFF-DEALER",
                "program_id": program.id,
                "description": "অনুমোদিত ডিলারের টেকনিশিয়ানরা উচ্চ হারে পয়েন্ট পান।",
            },
        )
        corporate = ensure(
            "fix.loyalty.affiliation",
            [("code", "=", MARK + "AFF-CORP")],
            {
                "name": "Corporate Staff",
                "name_bn": "কর্পোরেট কর্মী",
                "code": MARK + "AFF-CORP",
                "program_id": program.id,
                "description": "এএমসি চুক্তিভুক্ত প্রতিষ্ঠানের কর্মীরা।",
            },
        )
        dealer.add_members(accounts[:3], reason="ডিলার চুক্তি ২০২৬ (Dealer agreement 2026)")
        corporate.add_members(accounts[3:6], reason="কর্পোরেট এএমসি (Corporate AMC)")

    with block("M10 schemes + earn/burn rules"):
        Scheme = env["fix.loyalty.scheme"]
        if not Scheme.search_count([("code", "like", MARK + "%")]):
            old = Scheme.create(
                {
                    "name": "FiX Rewards 2025",
                    "name_bn": "ফিক্স রিওয়ার্ডস ২০২৫",
                    "code": MARK + "SCH-2025",
                    "program_id": program.id,
                    "valid_from": "2025-01-01",
                    "valid_until": "2025-12-31",
                }
            )
            env["fix.loyalty.earn.rule"].create(
                {
                    "scheme_id": old.id,
                    "priority": 10,
                    "name": "সব সেবায় (All services)",
                    "dimension": "all",
                    "points_per_bdt": 0.01,
                }
            )
            old.write({"state": "active"})
            old.action_retire()
            new = Scheme.create(
                {
                    "name": "FiX Rewards 2026",
                    "name_bn": "ফিক্স রিওয়ার্ডস ২০২৬",
                    "code": MARK + "SCH-2026",
                    "program_id": program.id,
                    "valid_from": "2026-01-01",
                    "valid_until": "2026-12-31",
                    "estimated_annual_cost": 45000.0,
                    "dofa_justification": "সিন্থেটিক সিড — বাজেট সীমার মধ্যে (synthetic seed, within budget)",
                }
            )
            EarnRule = env["fix.loyalty.earn.rule"]
            for prio, name, dim, value, ppb, extra in (
                (
                    1,
                    "ওয়ারেন্টি কাজে পয়েন্ট নেই (No points on warranty work)",
                    "category",
                    "warranty",
                    0.0,
                    {"excluded": True},
                ),
                (5, "ডিলার হার (Dealer rate)", "all", False, 0.05, {"affiliation_id": dealer.id}),
                (
                    8,
                    "সিলভার: যন্ত্রাংশে দ্বিগুণ (Silver: double on parts)",
                    "category",
                    "parts",
                    0.02,
                    {"tier_id": silver.id},
                ),
                (10, "সাধারণ হার (Standard rate)", "all", False, 0.01, {}),
            ):
                EarnRule.create(
                    {
                        "scheme_id": new.id,
                        "priority": prio,
                        "name": name,
                        "dimension": dim,
                        "dimension_value": value,
                        "points_per_bdt": ppb,
                        **extra,
                    }
                )
            BurnRule = env["fix.loyalty.burn.rule"]
            for prio, name, dim, value, extra in (
                (
                    1,
                    "কর্পোরেট: নগদায়ন বন্ধ (Corporate: no redemption)",
                    "all",
                    False,
                    {"affiliation_id": corporate.id, "blocked": True},
                ),
                (
                    5,
                    "যন্ত্রাংশে সর্বোচ্চ ১০% (Parts: at most 10%)",
                    "category",
                    "parts",
                    {"max_discount_pct": 10.0, "min_points": 100},
                ),
                (
                    10,
                    "সাধারণ: সর্বোচ্চ ২০% (Standard: at most 20%)",
                    "all",
                    False,
                    {
                        "max_discount_pct": 20.0,
                        "min_points": 100,
                        "max_points_per_transaction": 2000,
                    },
                ),
            ):
                BurnRule.create(
                    {
                        "scheme_id": new.id,
                        "priority": prio,
                        "name": name,
                        "dimension": dim,
                        "dimension_value": value,
                        **extra,
                    }
                )
            new.action_activate()
            Scheme.create(
                {
                    "name": "FiX Rewards 2027 (draft)",
                    "name_bn": "ফিক্স রিওয়ার্ডস ২০২৭ (খসড়া)",
                    "code": MARK + "SCH-2027",
                    "program_id": program.id,
                    "valid_from": "2027-01-01",
                    "valid_until": "2027-12-31",
                }
            )

    with block("M10 member cards"):
        Card = env["fix.loyalty.card"]
        if not Card.search_count([("card_number", "like", MARK + "%")]):
            for n, account in enumerate(accounts):
                card = Card.create(
                    {
                        "account_id": account.id,
                        "card_number": f"{MARK}C{n + 1:04d}",
                        "barcode": f"2990{n + 1:07d}",
                        "card_type": ("physical", "wallet", "virtual")[n % 3],
                        "issued_on": today - timedelta(days=30 * n),
                        "expires_on": today + timedelta(days=730 - 30 * n),
                    }
                )
                if n == 4:
                    card.action_block(reason="সদস্য কার্ড হারানোর খবর দিয়েছেন (reported lost)")

    # ------------------------------------------------------------- M34 surveys
    with block("M34 survey instruments + answers"):
        Tmpl = env["fix.survey.template"]
        csat = Tmpl.search([("code", "=", MARK + "SV-CSAT")], limit=1)
        if not csat:
            csat = Tmpl.create(
                {
                    "name": "Post-repair CSAT",
                    "name_bn": "মেরামত-পরবর্তী সন্তুষ্টি জরিপ",
                    "code": MARK + "SV-CSAT",
                    "purpose": "post_service",
                    "intro_text": "Thank you for choosing 1000FiX.",
                    "intro_text_bn": "১০০০ফিক্স বেছে নেওয়ার জন্য ধন্যবাদ।",
                }
            )
            Q = env["fix.survey.question"]
            overall = Q.create(
                {
                    "template_id": csat.id,
                    "sequence": 10,
                    "code": "overall",
                    "text": "How satisfied are you with the repair?",
                    "text_bn": "মেরামতে আপনি কতটা সন্তুষ্ট?",
                    "question_type": "rating_5",
                }
            )
            Q.create(
                {
                    "template_id": csat.id,
                    "sequence": 20,
                    "code": "why_low",
                    "text": "What went wrong?",
                    "text_bn": "কী ভুল হয়েছিল?",
                    "question_type": "text",
                    "ask_if_question_id": overall.id,
                    "ask_if_operator": "<=",
                    "ask_if_value": "2",
                }
            )
            Q.create(
                {
                    "template_id": csat.id,
                    "sequence": 30,
                    "code": "effort",
                    "text": "How easy was it to get your device repaired?",
                    "text_bn": "ডিভাইস মেরামত করানো কতটা সহজ ছিল?",
                    "question_type": "ces_7",
                }
            )
            Q.create(
                {
                    "template_id": csat.id,
                    "sequence": 40,
                    "code": "nps",
                    "text": "How likely are you to recommend 1000FiX?",
                    "text_bn": "১০০০ফিক্স সুপারিশ করার সম্ভাবনা কতটা?",
                    "question_type": "nps_11",
                }
            )
            csat.action_publish()
            nps = Tmpl.create(
                {
                    "name": "Relationship NPS",
                    "name_bn": "সম্পর্ক এনপিএস",
                    "code": MARK + "SV-NPS",
                    "purpose": "nps",
                }
            )
            Q.create(
                {
                    "template_id": nps.id,
                    "sequence": 10,
                    "code": "nps",
                    "text": "How likely are you to recommend 1000FiX?",
                    "text_bn": "১০০০ফিক্স সুপারিশ করার সম্ভাবনা কতটা?",
                    "question_type": "nps_11",
                }
            )
            nps.action_publish()
            Tmpl.create(
                {
                    "name": "Post-complaint follow-up",
                    "name_bn": "অভিযোগ-পরবর্তী জরিপ",
                    "code": MARK + "SV-CMPL",
                    "purpose": "post_complaint",
                }
            )
        Survey = env["fix.survey"]
        if not env["fix.survey.answer"].search_count([("survey_id.template_id", "=", csat.id)]):
            orders = env["fix.service.order"].search(
                [("state", "in", ("delivered", "closed"))], order="id", limit=10
            )
            for n, order in enumerate(orders):
                rating = (5, 4, 5, 2, 4, 1, 5, 3, 4, 5)[n]
                survey = Survey.create(
                    {
                        "service_order_id": order.id,
                        "operating_unit_id": ou.id,
                        "template_id": csat.id,
                        "state": "responded",
                        "rating": str(rating),
                    }
                )
                answers = {
                    "overall": rating,
                    "effort": max(1, min(7, rating + 2)),
                    "nps": min(10, rating * 2),
                }
                if rating <= 2:
                    answers["why_low"] = "যন্ত্রাংশের জন্য অনেক দিন অপেক্ষা করতে হয়েছে।"
                survey.record_answers(answers)

    # ------------------------------------------------------------- M35 journeys
    with block("M35 journey runtime + touches"):
        Journey = env["fix.campaign.journey"]
        journey = Journey.search([("name", "like", MARK + "%")], limit=1)
        if not journey:
            campaign = env["fix.campaign"].search(
                [("state", "=", "running")], order="id desc", limit=1
            )
            segment = ensure(
                "fix.segment",
                [("code", "=", MARK + "SEG-AC")],
                {
                    "code": MARK + "SEG-AC",
                    "name": "এসি মালিক — ঢাকা (AC owners, Dhaka)",
                    "evaluation_mode": "manual",
                },
            )
            audience = customers[12:27]
            segment.action_add_members(audience.ids)
            for partner in audience[:10]:
                grant(partner, "marketing", "sms")
            journey = Journey.create(
                {
                    "name": MARK + "বর্ষার এসি সার্ভিস যাত্রা (Monsoon AC service journey)",
                    "campaign_id": campaign.id,
                    "journey_kind": "segment_scheduled",
                    "segment_id": segment.id,
                    "exit_on_consent_withdrawal": True,
                }
            )
            # A branch never falls through: both arms name their next step, or
            # the engine completes the member on that arm (by design).
            Step = env["fix.campaign.journey.step"]
            done = Step.create(
                {
                    "journey_id": journey.id,
                    "sequence": 40,
                    "name": "সম্পন্ন (Done)",
                    "step_type": "exit",
                    "exit_reason": "Journey complete",
                }
            )
            send = Step.create(
                {
                    "journey_id": journey.id,
                    "sequence": 20,
                    "step_type": "send",
                    "name": "অফার এসএমএস (Offer SMS)",
                    "channel": "sms",
                    "purpose": "marketing",
                    "body": "প্রিয় {{name}}, বর্ষার আগে এসি সার্ভিসে ২০% ছাড় — ১৬৭৪৩।",
                }
            )
            Step.create(
                {
                    "journey_id": journey.id,
                    "sequence": 30,
                    "step_type": "wait",
                    "name": "অপেক্ষা (Wait)",
                    "wait_minutes": 0,
                }
            )
            Step.create(
                {
                    "journey_id": journey.id,
                    "sequence": 10,
                    "step_type": "branch",
                    "name": "মার্কেটিং সম্মতি আছে? (Has marketing consent?)",
                    "condition_kind": "consent_granted",
                    "true_step_id": send.id,
                    "false_step_id": done.id,
                }
            )
            journey.action_activate()
            for _ in range(4):
                Journey.cron_advance_journeys()
        Touch = env["fix.campaign.touch"]
        if not Touch.search_count([("campaign_id", "=", journey.campaign_id.id)]):
            Touch.cron_harvest_from_delivery_log(days=7)
            members = journey.member_ids.filtered("delivery_ids")
            for n, member in enumerate(members):
                if n % 2 == 0:
                    Touch.record(
                        journey.campaign_id,
                        member.partner_id,
                        "open",
                        channel="sms",
                        source_key=f"{MARK}TOUCH-OPEN-{member.id}",
                    )
                if n % 3 == 0:
                    Touch.record(
                        journey.campaign_id,
                        member.partner_id,
                        "click",
                        channel="sms",
                        source_key=f"{MARK}TOUCH-CLICK-{member.id}",
                    )
                if n == 0:
                    Touch.record(
                        journey.campaign_id,
                        member.partner_id,
                        "conversion",
                        channel="sms",
                        value_bdt=2500.0,
                        source_key=f"{MARK}TOUCH-CONV-{member.id}",
                    )


def report(env):
    counts = []
    for model in (
        "fix.notif.provider",
        "fix.notif.delivery",
        "fix.cc.capacity.profile",
        "fix.routing.workstream",
        "fix.routing.bullseye.ring",
        "fix.routing.workitem",
        "fix.cc.agent.state",
        "fix.cc.agent.state.log",
        "fix.cc.wfm.adherence",
        "fix.cc.macro",
        "fix.cc.knowledge.binding",
        "fix.cc.script",
        "fix.cc.script.completion",
        "fix.cc.qa.rubric",
        "fix.assistant.llm.provider",
        "fix.assistant.ask",
        "fix.assistant.intent.candidate",
        "fix.dedup.job",
        "fix.crm.sequence",
        "fix.crm.sequence.enrolment",
        "fix.loyalty.point.type",
        "fix.loyalty.affiliation",
        "fix.loyalty.scheme",
        "fix.loyalty.burn.rule",
        "fix.loyalty.card",
        "fix.survey.template",
        "fix.survey.answer",
        "fix.campaign.journey.member",
        "fix.campaign.touch",
    ):
        counts.append(f"  {model:<34} {env[model].sudo().search_count([])}")
    print("seed_a03_gap: blocks")
    for status, name, detail in RESULTS:
        print("  [{}] {}{}".format(status, name, (" - " + detail) if detail else ""))
    print("seed_a03_gap: row counts after seeding")
    print("\n".join(counts))


try:
    env  # noqa: B018 - provided by `odoo-bin shell`
except NameError:
    raise SystemExit(
        "seed_a03_gap: run inside `odoo-bin shell` (see the module docstring)"
    ) from None
seed(env)  # noqa: F821 - `env` comes from odoo-bin shell
env.cr.commit()  # noqa: F821
report(env)  # noqa: F821
