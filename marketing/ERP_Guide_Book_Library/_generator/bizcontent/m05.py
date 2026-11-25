# -*- coding: utf-8 -*-
"""
M05 — Remote Support & Managed Services.

The module that turns 1000FiX from a company that fixes things when they break
into one that stops them breaking, under contract, for a monthly fee. It is the
highest-margin business line in the company's documentation and the only one
with recurring revenue and declining marginal cost.

Worked examples name clients, assets and figures so the reader can picture the
work. Those details are illustrative; the contract types, targets and rules come
from the specification.
"""

from bizcontent import common as CM

CONTENT = {
    # ============================================================== front
    "cover_line": "The module that stops things breaking rather than fixing them "
    "afterwards. Recurring revenue, above 55 per cent gross margin, and "
    "the only 1000FiX business line whose cost falls as it grows.",
    "cover_inside": [
        ("Part one", "What the module is for, who uses it, and where it stops"),
        (
            "Part two",
            "All sixty-two things it lets you do, with worked "
            "examples and five walkthroughs from a normal day",
        ),
        (
            "Part three",
            "The rules, the automatic work, the permissions, the "
            "measures and the troubleshooting",
        ),
        ("Appendix A", "The full technical register for builders and testers"),
    ],
    "about": CM.about("the Remote Support and Managed Services module, M05"),
    "audience": CM.AUDIENCE,
    "how_arranged": CM.HOW_ARRANGED,
    "parts_table": CM.parts_table("M05"),
    "reading_note": CM.READING_NOTE,
    "appendix_note": CM.APPENDIX_NOTE,
    "part1_blurb": CM.PART1_BLURB,
    "part2_blurb": CM.PART2_BLURB,
    "part3_blurb": CM.PART3_BLURB,
    "appendix_blurb": CM.APPENDIX_BLURB,
    "part1_sections": CM.part1_sections(
        "M05", "The kinds of managed service it has to deliver"
    ),
    "part2_sections": CM.part2_sections("The journey of an alert"),
    "part3_sections": CM.PART3_SECTIONS,
    "appendix_sections": CM.APPENDIX_SECTIONS,
    "change_control": CM.CHANGE_CONTROL,
    "change_table": CM.change_table("The Corporate Services Head"),
    "change_note": CM.CHANGE_NOTE,
    # ============================================================ exhibits
    "headline": [
        (">55%", "gross margin at steady state", "the highest of any line"),
        ("BDT 95 lac", "a year of recurring revenue", None),
        ("65%", "of issues resolved without a visit", None),
        ("62", "things the module lets you do", None),
        ("8,000", "client assets under monitoring", "from none today"),
        ("6", "contract types committed", "none of them has a system"),
        ("98%", "contractual SLA attainment target", None),
        ("24/7", "the coverage the company already sells", None),
    ],
    "volume": [
        ("6", "contract types", "Basic through to IT strategy"),
        (
            "6",
            "support disciplines",
            "remote, software, hardware, network, " "mobile, email",
        ),
        ("8,000", "assets to monitor", "endpoints, servers, network, cloud"),
        ("0", "of it has a system today", "all of it is already sold"),
        ("55%", "the margin floor", "recurring, not one-off"),
    ],
    "volume_title": "What is already promised and not yet built",
    "volume_sub": "Six contract types and a 24/7 commitment, with no system "
    "behind either",
    "volume_caption": "The gap between what is sold and what can be delivered",
    "does": [
        "Remote support sessions: consent, recording, metering and billing",
        "The monitored estate: onboarding assets, agents, and agentless " "monitoring",
        "Collecting metrics and scoring the health of every asset and estate",
        "Alert rules, correlation, de-duplication and turning alerts into " "tickets",
        "The on-call rota, escalation and acknowledgement tracking",
        "Runbooks, and automated remediation that fixes things unattended",
        "Maintenance windows and suppressing alerts during them",
        "Patch inventory, scheduling, deployment and compliance reporting",
        "Endpoint protection and vulnerability oversight",
        "The managed service desk, with contractual service levels",
        "Problem and change management in client environments",
        "Escalating from a remote engineer to a site visit",
        "Entitlement consumption, overage and service credits",
        "Client service reports and the review meetings that use them",
        "Onboarding and offboarding client organisations",
        "Cloud subscriptions, backup oversight and disaster-recovery testing",
    ],
    "does_not": [
        "Contract terms, entitlements and renewal, which are M08",
        "Recurring billing and invoicing, which are M39 and M20",
        "Posting a service credit to the account, which is M20 — M05 only "
        "calculates it",
        "Asset identity and ownership, which are M17",
        "Dispatching a field visit, which is M02 — M05 escalates to it",
        "Data recovery, backup execution and secure destruction, which are M06",
        "1000FiX's own internal IT support, which is M66 and a different " "business",
        "Telephony and the contact centre workspace, which are M27",
        "Customer identity and corporate hierarchy, which are M33",
        "The general telemetry platform, which is M48 — M05 is the "
        "managed-service overlay on it",
        "Security investigation of 1000FiX itself, which is M29 and M60",
    ],
    "areas_map": [
        (
            "Taking control remotely",
            8,
            "Consented sessions, recorded, metered and billed against a " "contract.",
        ),
        (
            "Watching the estate",
            10,
            "Agents, metrics, baselines, health scores and coverage gaps.",
        ),
        (
            "Alerts and incidents",
            9,
            "From a threshold breach to a ticket, an escalation or an automatic "
            "fix.",
        ),
        (
            "Patching and security",
            6,
            "What is missing, when it can be applied, and what the client is "
            "exposed to.",
        ),
        (
            "The client service desk",
            10,
            "Tickets, contractual promises, knowledge, problems and changes.",
        ),
        (
            "Delivering the contract",
            11,
            "Entitlement, overage, credits, reports, reviews, onboarding and "
            "profit.",
        ),
        (
            "The specialist lines",
            8,
            "Backup, cloud, disaster recovery, licensing and IT strategy.",
        ),
    ],
    "area_bars": [
        ("Delivering the contract", 11),
        ("Watching the estate", 10),
        ("The client service desk", 10),
        ("Alerts and incidents", 9),
        ("Taking control remotely", 8),
        ("The specialist lines", 8),
        ("Patching and security", 6),
    ],
    "channels": [
        "A monitoring alert from a client's server",
        "A client contact raising a ticket in the portal",
        "An email to the service desk",
        "A telephone call to the 24/7 line",
        "A chat session from the client portal",
        "A scheduled maintenance task falling due",
        "A backup job that failed twice running",
        "A patch that has become critical",
        "A warranty expiring across the client estate",
    ],
    "channels_hub": "MSP ticket",
    "channels_title": "Nine ways work reaches the managed service desk",
    "channels_sub": (
        "Whatever raises it, the same contractual clock starts "
        "and the same entitlement is consumed"
    ),
    "channels_note": "one queue, one contract",
    "channels_caption": "What generates work in a managed-services operation",
    # ============================================ 1. what it is for
    "s1_lede": "M05 turns 1000FiX from a company that fixes things when they break "
    "into one that stops them breaking — under contract, for a monthly "
    "fee, at gross margins above 55 per cent.",
    "s1_intro": [
        "The company's business plan already commits to six categories of "
        "managed service contract — Basic, Comprehensive, Security-focused, "
        "Cloud Services, Disaster Recovery and Business Continuity, and IT "
        "Strategy Consulting — and to a 24/7 technical support operation "
        "covering remote, software, hardware, networking, mobile and email "
        "support. Both are described in detail in the plan. Neither has a "
        "system behind it.",
        "M05 is that system. It watches client IT estates and scores their "
        "health. It turns a threshold breach into a ticket, escalates it "
        "through an on-call rota, and sometimes fixes it automatically with a "
        "runbook before a human being sees it. It runs the service desk that "
        "answers the client's own calls. It tracks what the contract entitles "
        "them to and how much of it they have used. And it produces the "
        "monthly report that makes the whole arrangement defensible at renewal.",
        "The commercial shape is different from everything else 1000FiX does. "
        "A repair job earns once. A managed-service contract earns every "
        "month, and — this is the part that matters — the better the "
        "monitoring gets, the fewer site visits are needed to service it. "
        "Marginal cost falls as the business grows, which is true of nothing "
        "else in the company.",
    ],
    "s1_problem": [
        "The managed-services line is the one most exposed by not having a "
        "system. An MSP contract sold without monitoring is a promise to react "
        "quickly to problems the company will not know about until the client "
        "telephones. That is not a managed service; it is a break-fix "
        "arrangement with a monthly invoice attached, and clients work that "
        "out.",
        "Three things follow from it. Service credits accrue silently, because "
        "nobody is measuring attainment against the contracted service level "
        "until the client produces their own figures at renewal. Every new "
        "client adds manual load rather than automated load, so the segment "
        "stays sub-scale by construction. And the 24/7 commitment is a "
        "marketing claim rather than a contractual, measurable service, "
        "because there is no rota, no escalation policy and no "
        "acknowledgement tracking behind it.",
        "There is also a strategic cost. Managed services is how a company "
        "moves up the value chain from break-fix vendor to IT services "
        "partner. Corporate buyers ask about estate health, patch compliance "
        "and SLA attainment in tenders, and today there is no answer to any of "
        "those questions.",
    ],
    "s1_replaces": [
        [
            "Finding out when the client telephones",
            "Monitoring that raises an alert before the failure",
            "Unplanned client downtime becomes planned maintenance.",
        ],
        [
            "An engineer with an ad-hoc remote tool and no record",
            "Consented, logged, recorded sessions metered against the contract",
            "The session is evidence, and it is billable.",
        ],
        [
            "Every problem becoming a site visit",
            "Remote resolution of software, configuration and network faults",
            "65 per cent resolved without anybody travelling — a full technician "
            "job slot saved each time.",
        ],
        [
            "A 24/7 claim with nobody rostered",
            "An on-call rota, escalation policy and tracked acknowledgement",
            "The commitment becomes contractual and measurable rather than "
            "aspirational.",
        ],
        [
            "Service credits discovered at renewal",
            "Credits calculated automatically from measured breach",
            "Margin erosion becomes visible before it accumulates.",
        ],
        [
            "A renewal conversation with no evidence",
            "A monthly service report with attainment, incidents, patch "
            "compliance and recommendations",
            "Supports the 90 per cent renewal target with something to point at.",
        ],
        [
            "Every new client adding manual work",
            "Automated alert-to-ticket, runbooks and scheduled tasks",
            "Marginal cost falls as the estate grows, which is what makes the "
            "margin possible.",
        ],
        [
            "No idea whether a contract makes money",
            "Cost to serve against contract value, per client, monthly",
            "An unprofitable contract is identified in month two rather than at "
            "renewal.",
        ],
    ],
    "s1_one_sentence": "M05 is the system behind a managed-services business: it watches "
    "clients' equipment, fixes what it can without being asked, escalates "
    "what it cannot, and proves at the end of every month that the "
    "contract was delivered.",
    # ============================================ 2. who uses it
    "s2_lede": "A small, highly skilled internal team, and a population of client IT "
    "managers who will judge 1000FiX by what they see in a portal.",
    "s2_intro": [
        "Managed services has fewer users than any other module in Category A "
        "and a higher proportion of them outside the company. A remote support "
        "engineer, a corporate services head, an account manager and a finance "
        "manager cover most of the internal population.",
        "The client-side users matter more than their number suggests. A "
        "client IT manager who can see their own estate health, open "
        "incidents, patch compliance and service-level attainment in a portal "
        "is having a fundamentally different relationship with 1000FiX from "
        "one who telephones when something breaks. That difference is most of "
        "what the module is selling.",
    ],
    "s2_roles": [
        [
            "Remote support engineer",
            "Working the alert queue, running remote sessions, resolving without "
            "travelling",
            "A prioritised queue of alerts and tickets across their clients",
        ],
        [
            "Corporate Services Head",
            "Running the whole managed-services business",
            "Estate health, coverage gaps, attainment and profitability",
        ],
        [
            "Account manager",
            "Renewal conversations and finding expansion opportunities",
            "Their own accounts' service reports and consumption",
        ],
        [
            "Operations Director",
            "Remote resolution rate and how much field work is being avoided",
            "The remote resolution report",
        ],
        [
            "Finance manager",
            "Whether contracts make money, and what credits are accruing",
            "Consumption, overage, credits and cost to serve",
        ],
        [
            "Contact centre agent",
            "Raising tickets for client callers",
            "Ticket creation and status, scoped to the caller's entitlement",
        ],
        [
            "Contact centre supervisor",
            "Client tickets that came in by telephone",
            "The tickets their team raised",
        ],
        [
            "Quality manager",
            "Major incidents, problems and things that keep recurring",
            "The problem and recurring incident report",
        ],
        [
            "IT administrator",
            "Keeping the monitoring platform itself healthy",
            "Agent platform administration",
        ],
        [
            "Client IT manager",
            "Watching their own estate and raising their own tickets",
            "Their organisation's estate health, incidents, compliance and "
            "attainment",
        ],
    ],
    "s2_days": [
        {
            "title": "If you are a remote support engineer",
            "text": [
                "Your queue is not a list of complaints; it is a list of "
                "things the system noticed. Most of what reaches you started "
                "as a metric crossing a threshold on a client's server, was "
                "correlated against other alerts so you get one ticket rather "
                "than forty, and arrived already prioritised by client tier "
                "and how close it is to a contractual deadline.",
                "A proportion of it will already have been attempted. Where an "
                "alert matches a runbook the system will have executed the "
                "remediation and recorded what it tried; sometimes the ticket "
                "you are reading is closed before you open it. Your attention "
                "goes to what automation could not fix.",
                "When you do need to take control of a client's machine, "
                "consent comes first and it is logged. A one-time code goes to "
                "the customer, they see what will be accessed, and the session "
                "is recorded where the contract requires it. Duration is "
                "metered and billed against the contract automatically, so "
                "there is no separate timesheet.",
            ],
        },
        {
            "title": "If you run the managed-services business",
            "text": [
                "Three numbers will tell you almost everything. Coverage — the "
                "proportion of contracted assets with a healthy monitoring "
                "agent — because an unmonitored asset is a contractual failure "
                "waiting to be discovered. Alert noise, because a queue full "
                "of alerts that close with no action trains engineers to "
                "ignore the ones that matter. And remote resolution rate, "
                "because that is where the margin comes from.",
                "The fourth number, cost to serve against contract value per "
                "client, is the one that will change how you sell. Some "
                "contracts will turn out to be unprofitable, and you will know "
                "in month two rather than at renewal.",
            ],
        },
        {
            "title": "If you manage a corporate account",
            "text": [
                "You get something you have never had: evidence. A monthly "
                "service report showing attainment against the contracted "
                "service level, incidents raised and resolved, patch "
                "compliance, estate health and recommendations. That report is "
                "the renewal conversation, and it is generated rather than "
                "assembled.",
                "It is also a sales instrument. Monitoring reveals ageing "
                "assets, warranties about to expire and configuration drift, "
                "and each of those is a qualified, evidenced opportunity "
                "rather than a cold suggestion.",
            ],
        },
        {
            "title": "If you are a client IT manager",
            "text": [
                "You see your own estate and nothing else — that boundary is "
                "enforced in software. Within it you get asset health, open "
                "incidents, patch compliance, service-level attainment and the "
                "monthly report, and you can raise and track your own tickets.",
                "The change from your point of view is that you stop being the "
                "person who notices. A failing disk, a backup that has failed "
                "twice, a machine that has dropped off patching — those reach "
                "1000FiX before they reach you, and often they are resolved "
                "before you would have noticed at all.",
            ],
        },
    ],
    "s2_note": "A client portal user sees only their own organisation's estate, "
    "tickets and reports. That is a hard rule, and it is the single "
    "assurance a corporate client cares about most.",
    # ============================================ 3. boundary
    "s3_lede": "M05 delivers the contract. It does not sell it, price it, bill it, or "
    "own the assets it watches.",
    "s3_intro": [
        "The cleanest way to hold the boundary is this: M08 owns the promise "
        "and M05 owns the delivery. What the client is entitled to, what it "
        "costs and when it renews are commercial questions belonging to the "
        "contract module. Whether the promise was kept this month, and by how "
        "much, is M05's answer to give.",
        "Two boundaries are worth stating because they surprise people. M05 "
        "calculates service credits but does not apply them — the calculation "
        "goes to M20, which posts the credit to the customer's account. And "
        "M05 escalates to a field visit but never dispatches one; M02 decides "
        "who goes and when.",
        "The third is organisational rather than technical. 1000FiX's own "
        "internal IT support is a different module, M66, and deliberately so. "
        "A client-facing managed service and an internal helpdesk have "
        "different service levels, different audiences and different "
        "commercial consequences, and running them on the same queue would "
        "damage both.",
    ],
    "s3_shared_intro": "Managed services overlays several things owned elsewhere. This table "
    "says which part belongs where.",
    "s3_shared": [
        [
            "The contract",
            "M08 Contract",
            "Owns the delivery instance against it. Never the terms or the " "renewal",
        ],
        [
            "The monitored asset",
            "M17 Asset Registry",
            "Owns the monitoring overlay — agent, metrics, health score. Not the "
            "asset itself",
        ],
        [
            "Telemetry",
            "M48 Telemetry Platform",
            "Owns the managed-service collection and alerting. M48 owns the "
            "platform",
        ],
        [
            "The ticket",
            "Shared — M05 owns the MSP ticket, M27 the conversation",
            "Owns classification, service level and resolution; M27 owns the "
            "channel",
        ],
        [
            "Entitlement consumption",
            "M08 owns the balance",
            "Reports what has been consumed. Does not hold the entitlement",
        ],
        [
            "The service credit",
            "M20 Receivables applies it",
            "Calculates it from measured breach. Never posts it",
        ],
        [
            "The field visit",
            "M02 Field Service",
            "Escalates into it, carrying full context. Does not dispatch",
        ],
        [
            "Backup execution",
            "M06 Data Services",
            "Oversees the outcomes and drives remediation. Does not run the " "backups",
        ],
        [
            "Client identity and hierarchy",
            "M33 Party Master",
            "Reads it. Maintains the authorised contacts and their permissions",
        ],
        [
            "1000FiX's own IT",
            "M66 Internal IT",
            "Nothing. A different business with a different audience",
        ],
    ],
    # ============================================ 4. kinds of service
    "s4k_title": "The kinds of managed service it has to deliver",
    "s4k_lede": "Six contract types and six support disciplines, all already sold, all "
    "running on the same monitoring and the same service desk.",
    "s4k_intro": [
        "The business plan commits to six categories of managed service "
        "contract, from a Basic arrangement through to IT Strategy Consulting. "
        "It also commits to 24/7 technical support across six disciplines. "
        "Those are two different axes of the same business, and a single "
        "client typically buys a point on each.",
        "What varies between them is scope, entitlement and which specialist "
        "lines are switched on. What does not vary is the machinery: assets "
        "are onboarded, agents deployed, thresholds set, alerts correlated, "
        "tickets raised against a contractual clock, and a monthly report "
        "produced. A Security-focused contract and a Basic one differ in what "
        "is watched and what is promised, not in how the watching works.",
    ],
    "kinds_columns": [
        (
            "Contract types",
            "What the client has bought",
            [
                "Basic — monitoring and reactive support",
                "Comprehensive — proactive maintenance included",
                "Security-focused — patch, endpoint and vulnerability posture",
                "Cloud Services — subscriptions, licences and spend",
                "Disaster Recovery and Business Continuity",
                "IT Strategy Consulting — roadmap and advisory",
            ],
        ),
        (
            "Support disciplines",
            "What the desk answers",
            [
                "Remote technical support",
                "Software support",
                "Hardware support",
                "Networking support",
                "Mobile device support",
                "Email and account support",
            ],
        ),
        (
            "Specialist lines",
            "Switched on per contract",
            [
                "Backup oversight and restore testing",
                "Cloud subscription and cost management",
                "Disaster recovery plan register and testing",
                "Licence compliance reporting",
            ],
        ),
    ],
    "kinds_title": "Two axes and a set of switches",
    "kinds_sub": "Six contract types, six support disciplines, one machine "
    "underneath",
    "s4k_header": [
        "The kind of service",
        "What is different about it",
        "What stays the same",
    ],
    "s4k_table": [
        [
            "Basic managed service",
            "Monitoring and reactive support. The narrowest entitlement and the "
            "widest client base.",
            "Assets onboarded, agents deployed, alerts to tickets, contractual "
            "clock, monthly report",
        ],
        [
            "Comprehensive",
            "Adds proactive maintenance: scheduled tasks, patching within agreed "
            "windows, and regular preventive work.",
            "As above",
        ],
        [
            "Security-focused",
            "Endpoint protection oversight, patch compliance and vulnerability "
            "reporting become the primary deliverable rather than a by-product.",
            "As above",
        ],
        [
            "Cloud Services",
            "Subscriptions, licences, usage and renewal tracked, with spend "
            "reporting and optimisation recommendations.",
            "As above",
        ],
        [
            "Disaster Recovery and Business Continuity",
            "A plan register per client, scheduled tests, and evidence that the "
            "tests were actually run and what they found.",
            "As above",
        ],
        [
            "IT Strategy Consulting",
            "Deliverables, roadmaps and refresh recommendations tracked as "
            "commitments rather than conversations.",
            "As above",
        ],
        [
            "24/7 coverage",
            "The service-level clock honours the contracted coverage window, not "
            "office hours. An on-call rota and out-of-hours cost recovery sit "
            "behind it.",
            "As above",
        ],
        [
            "Unattended access",
            "Permitted only on assets covered by a contract that grants it. "
            "Everything else requires attended consent every time.",
            "As above",
        ],
    ],
    "s4k_caption": "The contract types and what distinguishes each",
    "s4k_note": "The service-level clock honours the contracted coverage window rather "
    "than office hours. A client who bought 24/7 has a clock running at "
    "three in the morning, and a client who did not, does not.",
    # ============================================ 5. vocabulary
    "s4_lede": "Fifteen words, most of them from the managed-services trade rather "
    "than from repair.",
    "s4_intro": [
        "Managed services borrows heavily from IT operations vocabulary, and "
        "several of these terms have precise meanings that matter "
        "contractually. Alert, incident and problem are three different "
        "things, and treating them as synonyms is the commonest source of "
        "confusion in a service desk.",
    ],
    "s4_glossary": [
        [
            "Monitored asset",
            "A client machine, server, network device, printer or cloud "
            "subscription that 1000FiX is watching under contract.",
            "The unit of coverage, and of most contract pricing",
        ],
        [
            "Agent",
            "The small piece of software installed on a client asset that reports "
            "its metrics back. An asset without a healthy one is a coverage gap.",
            "Deployed at onboarding; its own health is monitored",
        ],
        [
            "Agentless monitoring",
            "Watching a device over the network where an agent cannot be "
            "installed — typically network hardware.",
            "Used for switches, routers and similar",
        ],
        [
            "Health score",
            "A single computed index per asset and per client estate, from the "
            "metrics collected.",
            "The first thing a client sees in their portal",
        ],
        [
            "Alert",
            "A threshold being crossed. Not yet a problem, and often not "
            "actionable on its own.",
            "Correlated and de-duplicated before anybody sees it",
        ],
        [
            "Incident",
            "Something that is actually wrong and needs resolving. Usually raised "
            "from an alert, sometimes by a client.",
            "The thing a contractual clock runs against",
        ],
        [
            "Problem",
            "The underlying cause behind incidents that keep recurring. Three "
            "occurrences of the same signature must be linked to one.",
            "Where permanent fixes are tracked, as opposed to repeated repairs",
        ],
        [
            "Runbook",
            "A defined remediation the system can execute automatically when an "
            "alert matches it, recording what it tried.",
            "How an incident gets fixed before an engineer reads it",
        ],
        [
            "Maintenance window",
            "An agreed period during which alerting is suppressed for a defined "
            "scope, so planned work does not generate noise.",
            "Agreed with the client; resumes automatically",
        ],
        [
            "Coverage gap",
            "A contracted asset with no healthy agent reporting. Contractually "
            "this is a failure, and it must be reported within 24 hours.",
            "The measure a client will ask about first",
        ],
        [
            "Entitlement",
            "What the contract includes — hours, incidents, assets or seats — and "
            "how much of it has been consumed.",
            "Notified at 80 per cent and again at 100",
        ],
        [
            "Overage",
            "Consumption beyond the entitlement. Either billed or escalated for a "
            "contract uplift; never absorbed silently.",
            "A commercial conversation, triggered by a number",
        ],
        [
            "Service credit",
            "Money owed back to the client because a contracted service level was "
            "missed. Calculated here, applied by finance.",
            "Automatic from measured breach; manual credits need the CFO",
        ],
        [
            "Attended and unattended access",
            "Attended means the customer is present and consents at the time. "
            "Unattended means the contract has granted standing access to that "
            "asset.",
            "The distinction is contractual and legally significant",
        ],
        [
            "Cost to serve",
            "What it actually costs 1000FiX to deliver a client's contract, "
            "against what the contract is worth.",
            "Reported monthly per client",
        ],
    ],
    # ============================================ 6. what you can do
    "s5_lede": "Sixty-two things, in seven areas. The second and third areas are "
    "where the margin comes from.",
    "s5_intro": [
        "The areas below follow the shape of a managed service: taking control "
        "of a machine, watching an estate, handling what the watching finds, "
        "keeping things patched, running the desk, delivering the contract, "
        "and the specialist lines that sit on top.",
        "If you are trying to understand why this business line has better "
        "margins than anything else 1000FiX does, read areas two and three. "
        "Monitoring plus automated remediation is what makes the marginal cost "
        "of the tenth client lower than the marginal cost of the first.",
    ],
    "areas": [
        {
            "title": "Taking control remotely",
            "who": [
                ("Mostly used by", "Remote support engineers"),
                (
                    "Also relied on by",
                    "Contact centre agents launching a " "session mid-call",
                ),
                ("Where it happens", "At a desk, on somebody else's machine"),
            ],
            "intro": [
                "The statement of work describes this plainly: something like "
                "TeamViewer, where a customer can give us access to their "
                "computer through a desktop application. The functions here "
                "make that into a service rather than a tool.",
                "The difference is consent, evidence and money. No connection "
                "is established without explicit, logged consent, and the "
                "customer is shown what will be accessed before they agree. "
                "Sessions are recorded where the contract or policy requires. "
                "Duration is metered and billed against the contract "
                "automatically. And the whole session attaches to a ticket, so "
                "it is part of the record rather than something that happened "
                "on somebody's laptop.",
            ],
            "features": [
                [
                    "Session initiation",
                    "Starts a remote session from a ticket, issuing a one-time "
                    "code to the customer.",
                    "The session belongs to a job rather than to a person's own "
                    "tool.",
                ],
                [
                    "Consent and authorisation",
                    "Requires explicit, logged consent before any connection, "
                    "showing the customer what will be accessed.",
                    "The one thing that makes remote access defensible.",
                ],
                [
                    "Attended and unattended access",
                    "Supports attended sessions, and unattended access only on "
                    "assets whose contract grants it.",
                    "A server can be worked on at three in the morning; a "
                    "personal laptop cannot.",
                ],
                [
                    "Session recording",
                    "Records sessions where policy or contract requires, stored as "
                    "evidence with retention rules.",
                    "A dispute about what an engineer did on a client machine is "
                    "answerable.",
                ],
                [
                    "Session metering and billing",
                    "Meters duration and bills by contract entitlement or on "
                    "demand.",
                    "No separate timesheet, and no unbilled remote work.",
                ],
                [
                    "File transfer control",
                    "Permits, logs and malware-scans any file transferred during "
                    "a session.",
                    "The support channel does not become an infection route.",
                ],
                [
                    "Session handover",
                    "Transfers a live session between engineers with full " "context.",
                    "A shift change does not mean starting again.",
                ],
                [
                    "Session from the contact centre",
                    "Launches a session from inside an active customer "
                    "conversation.",
                    "The caller does not have to be transferred and re-explain.",
                ],
            ],
            "example": (
                "a fault fixed while the client was still on the phone",
                "A client's finance manager telephones the 24/7 line at 16:20 "
                "because a reporting application will not start on her "
                "machine. The contact centre agent raises a ticket against the "
                "client's contract and launches a remote session from inside "
                "the call. A one-time code is read out; she enters it and is "
                "shown exactly what the engineer will be able to see. She "
                "consents, and the consent is logged with the time and her "
                "name. The engineer finds a corrupted configuration file, "
                "replaces it from the client's own baseline, and confirms the "
                "application opens. Eleven minutes of session time is metered "
                "and consumed against the contract's remote support "
                "entitlement, the recording is stored against the ticket, and "
                "the ticket closes. No visit, no travel, and the client's "
                "afternoon was not lost.",
            ),
            "mistakes": [
                "Using a personal remote tool because it is quicker to start. "
                "There is then no consent record, no recording, no metering "
                "and no ticket — and if anything goes wrong on the client "
                "machine there is no defence.",
                "Treating consent as a formality to click past. The customer "
                "is shown what will be accessed for a reason, and the log is "
                "what protects the engineer.",
                "Assuming unattended access is available because it was last "
                "time. It is granted per asset by the contract, not per "
                "client.",
                "Typing a client credential into a ticket note during a "
                "session. Credentials are vaulted and must never appear in a "
                "ticket, note or email.",
            ],
            "caution": "Client environment credentials are vaulted. They may never be "
            "recorded in a ticket, a note or an email — not temporarily, "
            "not in an internal-only field. If you find credentials in a "
            "ticket, report it rather than deleting it quietly.",
        },
        {
            "title": "Watching the estate",
            "who": [
                ("Mostly used by", "The monitoring platform, continuously"),
                (
                    "Also relied on by",
                    "Engineers, the corporate services head " "and client IT managers",
                ),
                (
                    "Where it happens",
                    "On thousands of client machines, all the " "time",
                ),
            ],
            "intro": [
                "Ten functions, and they are the foundation of the whole "
                "business line. Client assets are registered and linked to the "
                "central asset registry, agents are deployed and health-checked, "
                "network devices that cannot take an agent are watched over the "
                "network, and metrics are collected continuously: processor, "
                "memory, disk, temperature, uptime, service state, backup "
                "state and security state.",
                "Two of these deserve particular attention. Configuration "
                "baselines detect drift — a machine that has quietly changed "
                "from how it was set up is often the explanation for a fault "
                "nobody can reproduce. And agent health is monitored in its "
                "own right, because an asset that has stopped reporting looks "
                "exactly like an asset with no problems.",
                "That last point is a contractual matter rather than a "
                "technical one. A contracted asset with no healthy agent is a "
                "coverage gap, and coverage gaps must be reported within "
                "twenty-four hours. The target for unresolved gaps beyond "
                "twenty-four hours is zero.",
            ],
            "features": [
                [
                    "Asset onboarding",
                    "Registers a client's endpoints, servers, network devices, "
                    "printers and cloud subscriptions, linked to the central "
                    "asset registry.",
                    "The estate under contract is a list, not an assumption.",
                ],
                [
                    "Agent deployment",
                    "Deploys, registers and health-checks a monitoring agent per "
                    "asset.",
                    "Onboarding a new client is a process rather than a project.",
                ],
                [
                    "Agentless monitoring",
                    "Watches network devices over the network where an agent "
                    "cannot be installed.",
                    "Switches and routers are covered too.",
                ],
                [
                    "Metric collection",
                    "Collects processor, memory, disk, temperature, uptime, "
                    "service state, backup state and security state as time "
                    "series.",
                    "Trends become visible, which is how failures are predicted "
                    "rather than discovered.",
                ],
                [
                    "Software inventory",
                    "Maintains installed-software and licence inventory per " "asset.",
                    "A licence compliance question is answered by looking.",
                ],
                [
                    "Configuration baseline",
                    "Records how an asset class should be configured and detects "
                    "drift from it.",
                    "The machine that 'has always been like that' turns out to "
                    "have changed in March.",
                ],
                [
                    "Health score",
                    "Computes a single index per asset and per client estate.",
                    "A client IT manager sees one number before they see a "
                    "hundred metrics.",
                ],
                [
                    "Asset discovery",
                    "Finds assets on the client network and reconciles them "
                    "against the registered estate.",
                    "The machines nobody told us about get found.",
                ],
                [
                    "Client warranty tracking",
                    "Tracks manufacturer warranty across the client estate and "
                    "alerts before expiry.",
                    "An expiring warranty becomes a conversation rather than a "
                    "surprise.",
                ],
                [
                    "Agent health",
                    "Monitors and remediates agent health and coverage gaps.",
                    "An asset that stopped reporting is not mistaken for an asset "
                    "with no problems.",
                ],
            ],
            "example": (
                "the disk that was replaced before it failed",
                "A client's file server has been reporting normally for eight "
                "months. Over three weeks the disk error-rate metric climbs "
                "steadily — nothing that crosses an alarm threshold, but a "
                "clear trend against its own baseline. The health score for "
                "that asset drops from 94 to 71 and it surfaces in the "
                "estate health board as the worst asset in that client's "
                "estate. An engineer looks, sees the trend, and raises a "
                "planned replacement inside the client's next agreed "
                "maintenance window. The disk is swapped on a Saturday morning "
                "with the server offline for forty minutes by arrangement. "
                "What did not happen: a failure on a Tuesday afternoon, a "
                "restore from backup, a day of lost work for thirty people, "
                "and a service credit against the contract.",
            ),
            "mistakes": [
                "Onboarding a client's assets without deploying agents to all "
                "of them. The gap is contractual, not cosmetic.",
                "Ignoring an agent that has stopped reporting because the "
                "asset 'is probably fine'. That is precisely the assumption "
                "the coverage-gap rule exists to prevent.",
                "Watching absolute thresholds and ignoring trends against "
                "baseline. Most avoidable failures announce themselves as a "
                "trend for weeks first.",
                "Treating discovered assets as somebody else's problem. An "
                "unregistered machine on a monitored network is either a gap "
                "in the contract or a security question, and both need "
                "raising.",
            ],
        },
        {
            "title": "Alerts and incidents",
            "who": [
                ("Mostly used by", "Remote support engineers and the on-call " "rota"),
                (
                    "Also relied on by",
                    "The corporate services head, watching "
                    "noise and acknowledgement",
                ),
                ("Where it happens", "The alert queue, at all hours"),
            ],
            "intro": [
                "Nine functions turning raw threshold breaches into work that "
                "is worth doing. The hardest problem in this area is not "
                "detection; it is noise. A monitoring platform that raises "
                "forty alerts for one failing switch trains engineers to "
                "ignore alerts, at which point the whole investment is worth "
                "nothing.",
                "So alerts are correlated and de-duplicated before they become "
                "tickets, maintenance windows suppress them for agreed periods, "
                "and there is an explicit function for tuning noise down. The "
                "target is that fewer than fifteen per cent of alerts close "
                "with no action taken.",
                "Where an alert matches a runbook the system attempts the fix "
                "itself and records what it tried. Where nobody acknowledges, "
                "escalation walks up the on-call rota with acknowledgement "
                "tracked at each step. And a major incident can be declared, "
                "which notifies every affected client contact and runs a "
                "structured resolution and post-incident review.",
            ],
            "features": [
                [
                    "Alert rules",
                    "Defines thresholds and conditions per asset class, client "
                    "and contract tier.",
                    "A production server and a spare laptop are not held to the "
                    "same standard.",
                ],
                [
                    "Alert to ticket",
                    "Raises a ticket automatically from an alert, with "
                    "de-duplication and correlation.",
                    "Forty alerts from one failing switch become one ticket.",
                ],
                [
                    "Escalation policy",
                    "Escalates unacknowledged alerts through an on-call rota, "
                    "tracking acknowledgement.",
                    "The 24/7 commitment becomes a rota rather than a hope.",
                ],
                [
                    "Runbook automation",
                    "Attaches and executes remediation automatically, recording "
                    "what was attempted and what happened.",
                    "A disk cleared or a service restarted before anybody reads "
                    "the ticket.",
                ],
                [
                    "Maintenance windows",
                    "Suppresses alerting during agreed periods.",
                    "Planned work does not generate a night of false alarms.",
                ],
                [
                    "Major incident handling",
                    "Declares a major incident, notifies all affected client "
                    "contacts, and runs a structured resolution and review.",
                    "A serious outage is communicated rather than discovered.",
                ],
                [
                    "Alert noise reduction",
                    "Tunes, suppresses and correlates alerts to keep the "
                    "signal-to-noise ratio usable.",
                    "Engineers keep believing the alerts, which is the whole " "point.",
                ],
                [
                    "Automation library",
                    "Maintains reusable scripts with approval and an execution "
                    "audit.",
                    "What ran on a client machine, and who approved it, is "
                    "recorded.",
                ],
                [
                    "Scheduled tasks",
                    "Runs maintenance tasks on client assets on a timetable, with "
                    "evidence of completion.",
                    "Proactive maintenance becomes something you can prove you " "did.",
                ],
            ],
            "example": (
                "forty alerts, one ticket, no engineer",
                "At 02:14 a switch at a client site loses power. Within ninety "
                "seconds thirty-eight downstream devices stop responding and "
                "would each raise their own alert. Correlation recognises the "
                "pattern — a common upstream dependency — and raises one "
                "ticket for the switch rather than thirty-nine for its "
                "children. The alert matches a runbook, which attempts a "
                "remote power cycle through the managed PDU; it succeeds, and "
                "the devices come back within four minutes. The runbook "
                "records what it attempted and the outcome, and the ticket "
                "closes automatically. The on-call engineer's phone never "
                "rang. In the morning the client's IT manager sees a resolved "
                "incident in the portal with a four-minute duration, and the "
                "trend report flags that this is the second power event on "
                "that circuit in six weeks — which becomes a recommendation "
                "rather than a repeat call-out.",
            ),
            "mistakes": [
                "Acknowledging an alert to stop it escalating and then not "
                "working it. Acknowledgement is tracked, and an acknowledged "
                "breach reads worse than an unacknowledged one.",
                "Closing noisy alerts individually instead of tuning the rule. "
                "The noise ratio is a measured target, and the fix is the "
                "rule.",
                "Working an alert without checking whether a runbook already "
                "ran. It may have fixed part of the problem and changed what "
                "you are looking at.",
                "Forgetting to set a maintenance window before planned work. "
                "The night's false alarms then have to be explained.",
                "Not declaring a major incident because it might look bad. "
                "Undeclared major incidents are how clients find out from "
                "their own staff.",
            ],
        },
        {
            "title": "Patching and security",
            "who": [
                ("Mostly used by", "Remote support engineers, on a schedule"),
                ("Also relied on by", "Client IT managers and their auditors"),
                ("Where it happens", "Maintenance windows, mostly at night"),
            ],
            "intro": [
                "Six functions, and for a Security-focused contract they are "
                "the primary deliverable rather than housekeeping. Patch "
                "inventory tracks what is available and what is missing per "
                "asset; scheduling deploys by ring and within an agreed "
                "window, with rollback; compliance reporting says where each "
                "client stands by asset class and criticality.",
                "Alongside patching sits posture: endpoint protection status, "
                "coverage gaps in it, and known vulnerabilities on the "
                "monitored estate. For many corporate clients this reporting "
                "is the thing they are actually buying, because it is what "
                "their own auditors ask them for.",
            ],
            "features": [
                [
                    "Patch inventory",
                    "Tracks available and missing patches per asset.",
                    "The question 'are we patched?' has an answer.",
                ],
                [
                    "Patch scheduling",
                    "Schedules deployment by ring, maintenance window and client "
                    "approval, with rollback.",
                    "A bad patch reaches ten machines, not a thousand.",
                ],
                [
                    "Patch compliance reporting",
                    "Reports compliance per client, asset class and criticality.",
                    "The client's auditor gets a report rather than an " "assurance.",
                ],
                [
                    "Endpoint protection oversight",
                    "Monitors protection status and raises alerts on coverage " "gaps.",
                    "The one unprotected laptop is found before it matters.",
                ],
                [
                    "Vulnerability reporting",
                    "Reports known vulnerabilities on the monitored estate to the "
                    "client.",
                    "Risk becomes a list with owners rather than an anxiety.",
                ],
                [
                    "Security posture reporting",
                    "Reports endpoint protection, patch and vulnerability posture "
                    "as a periodic deliverable.",
                    "For a Security-focused contract this is the product.",
                ],
            ],
            "example": (
                "a patch that was stopped at ring one",
                "A critical update is released for an application used across "
                "a client's forty desktops. Patch scheduling deploys it first "
                "to ring one — four machines chosen to be representative and "
                "non-critical — inside the client's Wednesday night "
                "maintenance window. By morning two of the four are reporting "
                "a service that will not start. The rollback runs on all four, "
                "the remaining thirty-six are held, and a ticket is raised "
                "with the vendor. Compliance reporting shows those forty "
                "machines as intentionally held rather than simply "
                "non-compliant, with the reason attached. Three weeks later a "
                "corrected update is released and deploys cleanly. Without the "
                "ring, forty desktops would have been broken on a Thursday "
                "morning and the whole day would have been recovery.",
            ),
            "mistakes": [
                "Deploying outside an agreed maintenance window without client "
                "approval. It is a hard rule, and the reason is that a reboot "
                "at the wrong moment costs the client more than the patch is "
                "worth.",
                "Reporting compliance without distinguishing intentionally "
                "held from simply missed. They mean completely different "
                "things to an auditor.",
                "Treating endpoint protection coverage as a monthly check. A "
                "gap is an alert, not a report line.",
                "Skipping ring deployment when a patch is urgent. Urgency is "
                "an argument for a smaller ring, not for no ring.",
            ],
        },
        {
            "title": "The client service desk",
            "who": [
                ("Mostly used by", "Remote support engineers and client " "contacts"),
                ("Also relied on by", "The contact centre, and the quality " "manager"),
                ("Where it happens", "The portal, email, telephone and chat"),
            ],
            "intro": [
                "Ten functions running the desk a contracted client actually "
                "talks to. Tickets arrive by portal, email, telephone or chat, "
                "scoped to what that client is entitled to. They are "
                "classified by service, urgency and impact, and a priority is "
                "derived rather than argued about.",
                "The contractual service level is the part that distinguishes "
                "this from an ordinary helpdesk. Response and resolution "
                "clocks come from the client's own contract, honour their "
                "coverage window, and are measured and reported. A breach "
                "calculates a service credit automatically.",
                "Two functions here are about not repeating work. Problem "
                "management links recurring incidents to a single underlying "
                "cause with a permanent fix tracked against it — and a third "
                "recurrence of the same signature must be linked, as a rule. "
                "Change management records and approves changes to client "
                "environments with a rollback plan, and the engineer making "
                "the change cannot be its sole approver.",
            ],
            "features": [
                [
                    "Client ticketing",
                    "Accepts tickets from client contacts by portal, email, "
                    "telephone or chat, scoped to their entitlement.",
                    "The client raises work the way that suits them.",
                ],
                [
                    "Ticket classification",
                    "Classifies by service, urgency and impact and derives a "
                    "priority.",
                    "Priority stops being a negotiation.",
                ],
                [
                    "Contractual service levels",
                    "Applies response and resolution clocks from the client's "
                    "contract, and measures breach.",
                    "The promise that was sold is the promise being measured.",
                ],
                [
                    "Knowledge base",
                    "Maintains solution articles and publishes selected ones to "
                    "client self-service.",
                    "The same question stops being answered forty times.",
                ],
                [
                    "Problem management",
                    "Links recurring incidents to a problem record with root "
                    "cause and permanent fix tracked.",
                    "The third occurrence triggers a fix rather than a fourth "
                    "repair.",
                ],
                [
                    "Change management",
                    "Records and approves changes to client environments with "
                    "rollback plans.",
                    "Nothing changes on a client's system without a record and a "
                    "way back.",
                ],
                [
                    "Field escalation",
                    "Escalates a remote ticket into an on-site visit through M02, "
                    "carrying full context.",
                    "The technician arrives knowing what has already been tried.",
                ],
                [
                    "Client contact management",
                    "Maintains authorised contacts, their permissions and "
                    "escalation preferences.",
                    "Only people the client has authorised can raise or approve "
                    "things.",
                ],
                [
                    "Client portal scope",
                    "Defines exactly what each client may see and do in their "
                    "portal.",
                    "One client can never see another's estate.",
                ],
                [
                    "Client satisfaction",
                    "Measures satisfaction per ticket and per period.",
                    "Renewal risk becomes visible before the renewal.",
                ],
            ],
            "example": (
                "the third time was the last time",
                "A client reports that a shared printer stops responding "
                "roughly once a fortnight. Each time an engineer resolves it "
                "in about ten minutes by restarting a print spooler, and each "
                "time the ticket closes as resolved. On the third occurrence "
                "within the rolling period the system creates a problem record "
                "automatically and links all three incidents to it. That "
                "changes the question from 'how do we fix this?' to 'why does "
                "it keep happening?'. Investigation finds a driver conflict "
                "introduced by an update in the spring. A permanent fix is "
                "applied through change management with a rollback plan, "
                "approved by somebody other than the engineer making it, and "
                "the recurrence stops. Three ten-minute fixes had cost thirty "
                "minutes and looked like good service; the fourth, fifth and "
                "sixth never happened.",
            ),
            "mistakes": [
                "Closing recurring incidents individually because each one is "
                "quick. Three of the same signature must be linked to a "
                "problem, and the rule exists because quick repeated fixes are "
                "invisible waste.",
                "Making a change to a client environment without a change "
                "record. There is then no rollback plan and no approval, and "
                "if it goes wrong the client's contract is what absorbs it.",
                "Approving your own change. The separation of duties is "
                "enforced and it is there to catch the thing you did not "
                "think of.",
                "Accepting a ticket from somebody who is not an authorised "
                "contact. Their permissions exist because the client set "
                "them.",
                "Escalating to a field visit without attaching the context. "
                "The technician then repeats everything that has already been "
                "tried.",
            ],
        },
        {
            "title": "Delivering the contract",
            "who": [
                (
                    "Mostly used by",
                    "The corporate services head, account " "managers and finance",
                ),
                ("Also relied on by", "Clients, who receive the report"),
                ("Where it happens", "Monthly, mostly automatically"),
            ],
            "intro": [
                "Eleven functions covering the commercial reality of a managed "
                "service: how much of the entitlement has been used, what "
                "happens when it runs out, what is owed back when a promise is "
                "missed, and what the client sees at the end of the month.",
                "The entitlement functions close a quiet leak. Consumption is "
                "tracked against contracted hours, incidents, assets or seats, "
                "the account manager is notified at eighty per cent, and at a "
                "hundred the overage is either billed or escalated for an "
                "uplift. It is never absorbed silently, which is the current "
                "default and the reason some contracts lose money.",
                "The reporting functions are what make renewals winnable. A "
                "monthly service report covering attainment, incidents, patch "
                "compliance, estate health and recommendations, delivered on "
                "schedule, is the evidence base for a conversation that is "
                "otherwise conducted on impressions.",
            ],
            "features": [
                [
                    "Entitlement consumption",
                    "Tracks consumption against contracted hours, incidents, "
                    "assets or seats.",
                    "Everybody knows where the client stands, mid-month.",
                ],
                [
                    "Overage handling",
                    "Detects overage and either bills it or requests an uplift.",
                    "Extra work stops being absorbed silently.",
                ],
                [
                    "Service reports",
                    "Generates the periodic client report: attainment, incidents, "
                    "patch compliance, health and recommendations.",
                    "The renewal conversation has evidence in it.",
                ],
                [
                    "Service review meetings",
                    "Schedules, records and tracks actions from client reviews.",
                    "What was agreed in the meeting is still true next quarter.",
                ],
                [
                    "Service credits",
                    "Calculates credits automatically on breach and passes them "
                    "to finance.",
                    "Margin erosion is visible before it accumulates.",
                ],
                [
                    "24/7 coverage model",
                    "Defines follow-the-clock coverage, on-call rotas and "
                    "out-of-hours cost recovery.",
                    "A marketing claim becomes a costed, rostered service.",
                ],
                [
                    "Client onboarding",
                    "Runs a structured onboarding project for each new client.",
                    "The tenth client is onboarded the same way as the first, and "
                    "faster.",
                ],
                [
                    "Client offboarding",
                    "Runs controlled offboarding: agents removed, data returned, "
                    "access revoked, final reporting.",
                    "A departing client leaves cleanly, with nothing of ours left "
                    "behind and nothing of theirs kept.",
                ],
                [
                    "Profitability per client",
                    "Reports cost to serve against contract value.",
                    "An unprofitable contract is identified in month two.",
                ],
                [
                    "Capacity planning",
                    "Forecasts team capacity against contracted estate growth.",
                    "Growth stops outrunning the ability to deliver it.",
                ],
                [
                    "Managed-services analytics",
                    "Reports the whole operational and commercial picture of the "
                    "business line.",
                    "The margin target is measured, not assumed.",
                ],
            ],
            "example": (
                "the contract that was losing money",
                "A Comprehensive contract worth BDT 68,000 a month covers "
                "ninety assets for a manufacturing client. Cost-to-serve "
                "reporting in the second month shows it costing BDT 74,000 to "
                "deliver. Investigation finds two causes. The client's estate "
                "grew from ninety to a hundred and thirty-one assets in the "
                "eight months since the contract was signed, and nobody "
                "adjusted it. And a single ageing server generates about a "
                "third of all incidents on the account. The account manager "
                "goes to the renewal conversation with two things: an "
                "entitlement uplift for the extra forty-one assets, and a "
                "costed recommendation to replace the server, supported by the "
                "incident data. Both are agreed. The contract goes to BDT "
                "96,000 a month, the incident volume falls by a third, and "
                "1000FiX also sells the replacement hardware. None of that "
                "conversation was possible before, because none of the numbers "
                "existed.",
            ),
            "mistakes": [
                "Absorbing overage because the client is a good relationship. "
                "It is a hard rule that it is billed or escalated, and the "
                "reason is that silent absorption is how a whole business line "
                "loses money invisibly.",
                "Sending a service report late. On-schedule delivery is a "
                "measured target of one hundred per cent, because a late "
                "report is read as a bad month.",
                "Treating a service credit as a failure to hide. It is "
                "calculated automatically from measured breach, and disputing "
                "it internally wastes the credibility the measurement buys.",
                "Onboarding a client without the structured project. The "
                "shortcuts taken in week one are the coverage gaps found in "
                "month six.",
                "Offboarding informally. Agents left on machines and access not "
                "revoked is both a security problem and a contractual one.",
            ],
            "caution": "Offboarding is not complete until every agent is removed and "
            "every access revoked, with evidence. A client who has left "
            "and still has our software on their servers is a problem for "
            "both parties.",
        },
        {
            "title": "The specialist lines",
            "who": [
                ("Mostly used by", "Engineers on contracts that include them"),
                ("Also relied on by", "Account managers, and client auditors"),
                ("Where it happens", "Mostly scheduled, mostly quarterly"),
            ],
            "intro": [
                "Eight functions covering the contract types that sit above "
                "basic monitoring: backup oversight, cloud management, "
                "disaster recovery, licence compliance and IT strategy.",
                "What they have in common is that they are all promises about "
                "things that are rarely tested. A backup that has never been "
                "restored is a hope. A disaster-recovery plan that has never "
                "been exercised is a document. So the functions here are "
                "mostly about scheduling the test and evidencing that it "
                "happened.",
            ],
            "features": [
                [
                    "Backup oversight",
                    "Monitors client backup job outcomes, reports failures and "
                    "drives remediation.",
                    "A backup failing quietly for six weeks stops being possible.",
                ],
                [
                    "Cloud subscription management",
                    "Tracks client cloud subscriptions, licences, usage and "
                    "renewal.",
                    "The client stops paying for seats nobody uses.",
                ],
                [
                    "Cloud cost reporting",
                    "Reports spend with optimisation recommendations.",
                    "A recurring saving the client can see is a reason to keep "
                    "the contract.",
                ],
                [
                    "Disaster recovery plan register",
                    "Maintains client recovery and continuity plans.",
                    "The plan exists somewhere findable rather than in somebody's "
                    "drive.",
                ],
                [
                    "Disaster recovery test tracking",
                    "Schedules, executes and evidences tests, and reports the "
                    "results.",
                    "The plan is known to work, or known not to, before it " "matters.",
                ],
                [
                    "IT strategy deliverables",
                    "Tracks consulting deliverables, roadmaps and " "recommendations.",
                    "Advisory work becomes a commitment rather than a " "conversation.",
                ],
                [
                    "Technology roadmap",
                    "Maintains a per-client roadmap with refresh recommendations "
                    "feeding sales.",
                    "The next hardware purchase is planned jointly rather than "
                    "sold cold.",
                ],
                [
                    "Licence compliance",
                    "Reports software licence compliance across the client " "estate.",
                    "An audit letter is answerable in an afternoon.",
                ],
            ],
            "example": (
                "a restore test that found the problem",
                "A client on a Disaster Recovery contract has nightly backups "
                "reporting success for four months. The contract includes a "
                "quarterly restore test, which is scheduled and executed "
                "against a representative dataset. The restore fails: the "
                "backups have been running successfully, but one of the two "
                "database volumes was excluded from the job when the server "
                "was reconfigured in the spring, and nothing in a successful "
                "backup report reveals a volume that was never in scope. The "
                "job definition is corrected, a full backup is taken, and the "
                "restore test is repeated successfully the same week. The "
                "evidence goes into the client's service report. Four months "
                "of backups had been genuinely worthless for that volume, and "
                "nothing except an actual restore would have revealed it.",
            ),
            "mistakes": [
                "Reporting backup success without ever testing a restore. A "
                "successful backup job and a recoverable system are different "
                "claims.",
                "Letting a disaster-recovery test slip because the client is "
                "busy. An untested plan is a document, and the contract sold "
                "a capability.",
                "Reporting cloud spend without recommendations. The "
                "optimisation is the deliverable; the number is just the "
                "input.",
                "Treating IT strategy deliverables as advice rather than "
                "commitments. They are tracked because they were sold.",
            ],
        },
    ],
    # ============================================ 7. the journey
    "s6_title": "The journey of an alert",
    "s6_lede": "From a metric crossing a threshold to a closed incident, and the four "
    "places it can stop without a human being involved.",
    "s6_intro": [
        "The lifecycle that matters most in this module is not a ticket's — it "
        "is an alert's, because the whole economics of managed services "
        "depends on how many alerts never become work for a person.",
        "An alert can end in four places. It can be suppressed by a "
        "maintenance window. It can be de-duplicated into an existing ticket. "
        "It can be fixed by a runbook and closed automatically. Or it can "
        "reach an engineer. Every one of the first three is margin.",
    ],
    "journey": [
        ("Threshold crossed", "The monitoring agent", None),
        ("Suppressed", "Maintenance window", "ends here"),
        ("Correlated", "System", None),
        ("De-duplicated", "System", "joins a ticket"),
        ("Ticket raised", "System", None),
        ("Runbook attempted", "System", None),
        ("Auto-resolved", "System", "ends here"),
        ("Notified", "Escalation policy", None),
        ("Acknowledged", "Engineer", "gate"),
        ("In progress", "Engineer", None),
        ("Escalated to field", "Engineer", None),
        ("Resolved", "Engineer", "gate"),
        ("Linked to a problem", "System, on third recurrence", None),
    ],
    "journey_title": "The path an alert follows",
    "journey_sub": (
        "Four of the thirteen states end the alert without " "anybody's attention"
    ),
    "journey_caption": "How a threshold breach becomes work, or does not",
    "s6_stages": [
        [
            "Threshold crossed",
            "A metric has gone outside its rule.",
            "The monitoring agent",
            "Nothing. This is raw signal.",
        ],
        [
            "Suppressed",
            "It happened during an agreed maintenance window.",
            "The window",
            "An agreed window covering that scope.",
        ],
        [
            "Correlated",
            "It has been matched against other current alerts.",
            "System",
            "Nothing — this is how forty become one.",
        ],
        [
            "De-duplicated",
            "It is the same problem as an open ticket.",
            "System",
            "An existing ticket with the same signature.",
        ],
        [
            "Ticket raised",
            "It is now work with a contractual clock on it.",
            "System",
            "Correlation and de-duplication having found nothing to join.",
        ],
        [
            "Runbook attempted",
            "An automated remediation is running.",
            "System",
            "The alert matching a defined runbook.",
        ],
        [
            "Auto-resolved",
            "The runbook fixed it.",
            "System",
            "A successful remediation, with what was tried recorded.",
        ],
        [
            "Notified",
            "Somebody has been told, per the escalation policy.",
            "The escalation policy",
            "Nothing — but the acknowledgement clock is now running.",
        ],
        [
            "Acknowledged",
            "An engineer has taken it.",
            "Engineer",
            "Their acknowledgement. Unacknowledged, it escalates.",
        ],
        [
            "In progress",
            "Somebody is working on it.",
            "Engineer",
            "Nothing, but the resolution clock is running against the contract.",
        ],
        [
            "Escalated to field",
            "It needs hands on hardware.",
            "Engineer",
            "Full context attached, and M02 takes the dispatch decision.",
        ],
        [
            "Resolved",
            "It is fixed.",
            "Engineer",
            "The fix recorded. The client is notified.",
        ],
        [
            "Linked to a problem",
            "It has happened three times.",
            "System",
            "A third occurrence of the same signature in the rolling period. "
            "This is mandatory.",
        ],
    ],
    "s6_gates_intro": "Five points will stop work until a condition is met. Two of them are "
    "about consent, one about approval, and two about not letting things "
    "quietly accumulate.",
    "gates": [
        (
            "Consent before connection",
            "No remote connection may be established without explicit, logged "
            "customer consent",
            "Customer",
        ),
        (
            "Contract grants unattended access",
            "Unattended access is permitted only on assets whose contract grants " "it",
            "System",
        ),
        (
            "Change record before change",
            "Any change to a client environment needs a recorded change record "
            "with a rollback plan",
            "Engineer",
        ),
        (
            "Somebody else approves the change",
            "The engineer making a change cannot be its sole approver",
            "A second person",
        ),
        (
            "Client approval outside a window",
            "Patch deployment outside an agreed maintenance window requires "
            "client approval",
            "Client",
        ),
        (
            "Third recurrence becomes a problem",
            "Three incidents of the same signature in a rolling period must be "
            "linked to a problem record",
            "System",
        ),
        (
            "Offboarding evidenced",
            "A client offboarding is not complete until every agent is removed "
            "and every access revoked, with evidence",
            "System",
        ),
    ],
    "s6_wrong_intro": "Managed services fails in ways that are quiet rather than dramatic. "
    "The list below is ordered by how much damage each one does before "
    "anybody notices.",
    "s6_wrong": [
        [
            "Watching the estate",
            "An agent stops reporting and the asset looks healthy because it is "
            "silent.",
            "The coverage gap report, within 24 hours.",
            "Remediate the agent. A gap unresolved beyond 24 hours is a "
            "contractual failure and the target for those is zero.",
        ],
        [
            "Alerting",
            "Noise. Alerts that close with no action train engineers to ignore "
            "the queue.",
            "The alert noise ratio, which should be under 15 per cent.",
            "Tune the rule, do not close the alerts faster. This is the single "
            "most damaging failure mode in the module.",
        ],
        [
            "Ticket raised",
            "Nobody acknowledges, because everybody assumes somebody else has.",
            "Escalation up the on-call rota, with the acknowledgement clock "
            "visible.",
            "Acknowledge and work it, or hand it on explicitly. Acknowledging "
            "without working is worse than neither.",
        ],
        [
            "In progress",
            "The clock is the contract's, not office hours, and out-of-hours work "
            "is missed.",
            "Service-level attainment falling for one client only.",
            "Check the coverage window in the contract. A 24/7 client has a clock "
            "running at three in the morning.",
        ],
        [
            "Resolved",
            "The same thing recurs and each fix looks fast and good.",
            "Three linked incidents and an automatic problem record.",
            "Nothing — the link is automatic. Then actually work the problem.",
        ],
        [
            "Entitlement",
            "Consumption passes a hundred per cent and is absorbed.",
            "The notification at 80 and again at 100 per cent.",
            "Bill it or escalate for uplift. Absorbing it is against the rules and "
            "it is how a contract quietly loses money.",
        ],
        [
            "Reporting",
            "A service report is late or missing.",
            "The on-schedule delivery measure, targeted at 100 per cent.",
            "Send it. A late report is read by a client as a bad month being "
            "hidden.",
        ],
        [
            "Offboarding",
            "A client leaves and agents remain on their machines.",
            "The offboarding evidence is incomplete.",
            "Complete it. This is both a security exposure and a contractual "
            "breach.",
        ],
    ],
    "s6_note": "Four of the thirteen alert states end without a person: suppressed, "
    "de-duplicated, auto-resolved, and correlated into an existing ticket. "
    "The proportion of alerts that end in one of those four is, in "
    "commercial terms, the gross margin of the business line.",
    # ============================================ 8. day in the life
    "s7_lede": "Five walkthroughs, from a two-minute remote fix to a contract renewal "
    "won on evidence.",
    "s7_intro": [
        "Managed services looks quiet from the outside, which is the point. "
        "Four of these five walkthroughs describe something that did not "
        "become a problem.",
        "Clients, assets, figures and times are illustrative. The contract "
        "types, targets and rules behind them are exactly as the specification "
        "states them.",
    ],
    "scenarios": [
        {
            "title": "A fault fixed while the client was on the phone",
            "narrative": [
                "The everyday case for a remote support engineer, and the one "
                "that produces the 65 per cent remote resolution rate the "
                "margin depends on.",
            ],
            "lanes": [
                (
                    "Client",
                    [
                        (0, "Telephones the 24/7 line at 16:20"),
                        (1, "Enters the one-time code and consents"),
                        (3, "Confirms it works"),
                    ],
                ),
                ("Contact centre", [(0, "Raises a ticket against the " "contract")]),
                (
                    "Engineer",
                    [
                        (1, "Launches a session from the call"),
                        (2, "Replaces the file from the baseline"),
                    ],
                ),
                (
                    "System",
                    [
                        (1, "Logs the consent with time and name"),
                        (3, "Meters 11 minutes; stores the recording"),
                    ],
                ),
            ],
            "columns": ["Call", "Consent", "Fix", "Close"],
            "exhibit_title": "A remote fix, start to finish, in eleven minutes",
            "exhibit_sub": "No travel, no visit, one entitlement consumption",
            "caption": "The interaction that makes the margin possible",
            "table": [
                [
                    "1",
                    "Client and contact centre",
                    "A finance manager telephones at 16:20 — a reporting "
                    "application will not start. The agent raises a ticket "
                    "against the client's contract; the contractual response "
                    "clock starts.",
                ],
                [
                    "2",
                    "Engineer and client",
                    "A session is launched from inside the call. A one-time code "
                    "is read out; the client is shown exactly what will be "
                    "accessed and consents. The consent is logged with the time "
                    "and her name.",
                ],
                [
                    "3",
                    "Engineer",
                    "A corrupted configuration file is found and replaced from "
                    "the client's own recorded baseline. The application opens.",
                ],
                [
                    "4",
                    "System",
                    "The session ends. Eleven minutes is metered and consumed "
                    "against the remote support entitlement, the recording is "
                    "stored against the ticket, and the billable event is "
                    "emitted.",
                ],
            ],
            "outcome": "No site visit, no travel, and the client's afternoon "
            "continued. Each avoided visit saves a full technician job "
            "slot plus travel, and this is the transaction that has to "
            "happen sixty-five times in a hundred for the business line to "
            "work.",
        },
        {
            "title": "The night nobody was woken",
            "narrative": [
                "A switch fails at two in the morning, thirty-eight devices go "
                "down with it, and the on-call engineer's phone does not ring.",
            ],
            "lanes": [
                ("Client site", [(0, "A switch loses power at 02:14")]),
                (
                    "Monitoring",
                    [
                        (0, "38 downstream devices stop responding"),
                        (1, "Correlates to one upstream cause"),
                    ],
                ),
                (
                    "System",
                    [
                        (1, "Raises one ticket, not thirty-nine"),
                        (2, "Runs the runbook: remote power cycle"),
                        (3, "Closes automatically; records what it tried"),
                    ],
                ),
                (
                    "Client IT manager",
                    [(3, "Sees a four-minute resolved " "incident in the morning")],
                ),
            ],
            "columns": ["Failure", "Correlated", "Remediated", "Closed"],
            "exhibit_title": "Thirty-nine alerts, one ticket, no engineer",
            "exhibit_sub": "Correlation and a runbook, at two in the morning",
            "caption": "What automation actually looks like in practice",
            "table": [
                [
                    "1",
                    "Client site and monitoring",
                    "A switch loses power at 02:14. Within ninety seconds "
                    "thirty-eight downstream devices stop responding and would "
                    "each raise an alert.",
                ],
                [
                    "2",
                    "System",
                    "Correlation recognises the common upstream dependency and "
                    "raises one ticket for the switch rather than thirty-nine for "
                    "its children.",
                ],
                [
                    "3",
                    "System",
                    "The alert matches a runbook, which attempts a remote power "
                    "cycle through the managed distribution unit. It succeeds and "
                    "the devices return within four minutes.",
                ],
                [
                    "4",
                    "System",
                    "The runbook records what it attempted and the outcome. The "
                    "ticket closes automatically. Nobody was notified.",
                ],
                [
                    "5",
                    "Client IT manager",
                    "In the morning they see a resolved four-minute incident, and "
                    "the trend report flags this as the second power event on "
                    "that circuit in six weeks — which becomes a recommendation.",
                ],
            ],
            "outcome": "The target for alert-to-ticket automation is above 90 per "
            "cent, and this is why. An engineer woken at two in the "
            "morning costs out-of-hours pay and a degraded day after it; "
            "an engineer not woken costs nothing and the client's outage "
            "was four minutes instead of six hours.",
        },
        {
            "title": "A failure prevented three weeks early",
            "narrative": [
                "The walkthrough that explains the difference between managed "
                "service and break-fix, and the hardest one to sell because "
                "nothing appears to happen.",
            ],
            "lanes": [
                (
                    "Monitoring",
                    [
                        (0, "Disk error rate climbs over three weeks"),
                        (1, "Health score drops from 94 to 71"),
                    ],
                ),
                (
                    "Engineer",
                    [
                        (1, "Sees the worst asset on the estate board"),
                        (2, "Raises planned replacement"),
                    ],
                ),
                ("Client", [(2, "Agrees a Saturday window")]),
                ("Field", [(3, "Swaps the disk in a 40-minute outage")]),
            ],
            "columns": ["Trend", "Detected", "Planned", "Replaced"],
            "exhibit_title": "A disk replaced before it failed",
            "exhibit_sub": "The trend, not the threshold, is what found it",
            "caption": "Proactive intervention, which is the product",
            "table": [
                [
                    "1",
                    "Monitoring",
                    "A client's file server has reported normally for eight "
                    "months. Over three weeks the disk error-rate metric climbs "
                    "steadily — nothing crossing an alarm threshold, but a clear "
                    "trend against its own baseline.",
                ],
                [
                    "2",
                    "Monitoring and engineer",
                    "The health score for that asset falls from 94 to 71 and it "
                    "becomes the worst asset in the client's estate on the health "
                    "board. An engineer looks and sees the trend.",
                ],
                [
                    "3",
                    "Engineer and client",
                    "A planned replacement is raised for the client's next agreed "
                    "maintenance window. The client chooses a Saturday morning.",
                ],
                [
                    "4",
                    "Field",
                    "The disk is swapped with the server offline for forty "
                    "minutes, by arrangement, with nobody working.",
                ],
            ],
            "outcome": "What did not happen: a failure on a Tuesday afternoon, a "
            "restore from backup, a day of lost work for thirty people, "
            "and a service credit against the contract. This is the "
            "difference between a company that fixes things and one that "
            "stops them breaking, and it is entirely invisible unless "
            "somebody points at it in a service review.",
        },
        {
            "title": "A patch stopped at ring one",
            "narrative": [
                "Forty desktops that were not broken on a Thursday morning, "
                "because four of them were tried first.",
            ],
            "lanes": [
                (
                    "System",
                    [
                        (0, "Critical update released for 40 desktops"),
                        (1, "Deploys to ring one: 4 machines"),
                        (2, "Rolls back all four; holds the remaining 36"),
                    ],
                ),
                (
                    "Engineer",
                    [
                        (2, "Raises a ticket with the vendor"),
                        (3, "Deploys the corrected update cleanly"),
                    ],
                ),
                (
                    "Client",
                    [
                        (
                            3,
                            "Sees 40 machines held with a reason, not "
                            "simply non-compliant",
                        )
                    ],
                ),
            ],
            "columns": ["Released", "Ring one", "Held", "Corrected"],
            "exhibit_title": "A bad patch that reached four machines",
            "exhibit_sub": "Ring deployment, and a rollback that worked",
            "caption": "Why patches go out in rings",
            "table": [
                [
                    "1",
                    "System",
                    "A critical update is released for an application used across "
                    "forty of the client's desktops.",
                ],
                [
                    "2",
                    "System",
                    "Ring one deployment goes to four representative, "
                    "non-critical machines inside the client's Wednesday night "
                    "maintenance window.",
                ],
                [
                    "3",
                    "System and engineer",
                    "By morning two of the four report a service that will not "
                    "start. Rollback runs on all four, the remaining thirty-six "
                    "are held, and a ticket is raised with the vendor.",
                ],
                [
                    "4",
                    "Client reporting",
                    "Compliance reporting shows those forty machines as "
                    "intentionally held with the reason attached, rather than "
                    "simply non-compliant — which means something quite different "
                    "to an auditor.",
                ],
                [
                    "5",
                    "Engineer",
                    "Three weeks later a corrected update is released and deploys "
                    "cleanly across all forty.",
                ],
            ],
            "outcome": "Without the ring, forty desktops would have been broken on a "
            "Thursday morning and the day would have been recovery. Patch "
            "compliance across the managed estate is targeted above 95 per "
            "cent, and the way to reach it safely is in small groups.",
        },
        {
            "title": "A renewal won on evidence",
            "narrative": [
                "The commercial pay-off. A contract that was quietly losing "
                "money became a larger, profitable one, plus a hardware sale.",
            ],
            "lanes": [
                ("Finance", [(0, "Cost to serve BDT 74,000 against BDT " "68,000")]),
                (
                    "System",
                    [
                        (1, "Estate grew 90 to 131 assets, unadjusted"),
                        (1, "One server generates a third of incidents"),
                    ],
                ),
                (
                    "Account manager",
                    [
                        (2, "Takes both findings to the review"),
                        (3, "Agrees uplift and replacement"),
                    ],
                ),
                ("Client", [(3, "Accepts; incidents fall by a third")]),
            ],
            "columns": ["Loss found", "Causes", "Review", "Agreed"],
            "exhibit_title": "A loss-making contract turned around in a month",
            "exhibit_sub": "Two numbers that did not previously exist",
            "caption": "What cost-to-serve reporting makes possible",
            "table": [
                [
                    "1",
                    "Finance",
                    "A Comprehensive contract worth BDT 68,000 a month is costing "
                    "BDT 74,000 a month to deliver. This appears in the second "
                    "month of reporting.",
                ],
                [
                    "2",
                    "System",
                    "Two causes are visible. The client's estate has grown from "
                    "ninety to a hundred and thirty-one assets since signing, "
                    "with no entitlement adjustment. And one ageing server "
                    "generates about a third of all incidents on the account.",
                ],
                [
                    "3",
                    "Account manager and client",
                    "Both go to the service review with the data attached: an "
                    "entitlement uplift for forty-one additional assets, and a "
                    "costed recommendation to replace the server supported by "
                    "incident history.",
                ],
                [
                    "4",
                    "Client",
                    "Both are agreed. The contract moves to BDT 96,000 a month "
                    "and 1000FiX also sells the replacement hardware.",
                ],
                [
                    "5",
                    "System",
                    "Incident volume on the account falls by about a third the "
                    "following quarter, which improves cost to serve again.",
                ],
            ],
            "outcome": "Neither conversation was possible before, because neither "
            "number existed. Cost to serve per client and evidenced "
            "incident attribution are what turn a renewal from a "
            "negotiation about price into a discussion about the client's "
            "own estate.",
        },
    ],
    "s9t_lede": "Five stories, and the same four ideas in all of them.",
    "s9t_intro": [
        "The walkthroughs covered a remote fix, an automated overnight "
        "resolution, a prevented failure, a contained bad patch and a renewal. "
        "Only the first involved a person doing what would traditionally be "
        "called support.",
        "That is the shape of the business. Managed services is profitable "
        "precisely to the extent that the interesting cases are the ones where "
        "nobody had to do anything.",
    ],
    "s9t_table": [
        [
            "The best outcome is no work at all",
            "The overnight switch failure and the patch ring: both resolved with "
            "no engineer.",
            "Every alert that ends without a person is margin, and the "
            "alert-to-ticket automation target of above 90 per cent is the "
            "commercial plan.",
        ],
        [
            "Trends matter more than thresholds",
            "The disk replaced three weeks early on a trend that never crossed an "
            "alarm.",
            "Break-fix waits for a threshold. Managed service watches the " "gradient.",
        ],
        [
            "Consent and evidence make remote access a service",
            "The remote fix: one-time code, logged consent, recorded session, "
            "metered time.",
            "Without those four it is somebody using a tool on a client's "
            "machine, which is a liability rather than a product.",
        ],
        [
            "Small groups before big ones",
            "Ring deployment stopping a bad patch at four machines.",
            "The same principle as a quality gate: contain the failure at the "
            "cheapest point.",
        ],
        [
            "Numbers change the conversation",
            "The renewal: cost to serve and incident attribution.",
            "A renewal argued on impressions is a price negotiation. One argued "
            "on evidence is a discussion about the client's estate.",
        ],
    ],
    "s9t_close": "This is the only 1000FiX business line where growth reduces unit "
    "cost, and the mechanism is entirely visible in these five stories: "
    "watch continuously, automate the common case, contain the failures "
    "cheaply, and prove it monthly. Everything else in the module supports "
    "one of those four.",
    # ============================================ 10. rules
    "s8_lede": "Thirteen rules. Several of them govern access to somebody else's "
    "computer, which is the most sensitive thing 1000FiX does.",
    "s8_intro": [
        "Managed services involves taking control of client machines, holding "
        "their credentials, changing their configurations and seeing their "
        "data. The rules below exist because the trust required for that is "
        "easy to lose and impossible to rebuild.",
        "The first three are the ones that matter most. No connection without "
        "logged consent. Unattended access only where a contract grants it. "
        "And client credentials are vaulted and never appear in a ticket, note "
        "or email — not even temporarily, not even in an internal field.",
    ],
    "s8_rules": [
        [
            "Connect to a client machine without logged consent",
            "It is somebody else's computer, and often somebody else's data.",
            "Issue the one-time code and let them consent. It adds about twenty "
            "seconds.",
        ],
        [
            "Use unattended access on an asset the contract does not cover",
            "Standing access is a specific contractual grant, per asset.",
            "Use an attended session. If unattended access is genuinely needed, "
            "it is a contract change.",
        ],
        [
            "Put a client credential in a ticket, a note or an email",
            "Credentials in a ticket outlive the ticket and reach people who "
            "should never see them.",
            "Use the vault. If you find credentials in a ticket, report it rather "
            "than quietly deleting.",
        ],
        [
            "Leave a contracted asset without a healthy monitoring agent for more "
            "than a day",
            "An unmonitored asset is a contractual failure that looks exactly "
            "like a healthy one.",
            "Remediate the agent. Coverage gaps must be reported within 24 hours "
            "and the target for unresolved ones is zero.",
        ],
        [
            "Measure a service level against office hours",
            "The client bought a coverage window, and often that window is 24/7.",
            "Nothing — the clock honours the contract automatically. But do not "
            "be surprised by a clock running at three in the morning.",
        ],
        [
            "Issue a manual service credit",
            "Credits calculated from measured breach are defensible; discretionary "
            "ones are not.",
            "Automatic credits happen by themselves. A manual one needs the " "CFO.",
        ],
        [
            "Absorb over-consumption of the entitlement",
            "Silent absorption is how a whole business line loses money " "invisibly.",
            "Bill it, or escalate it for a contract uplift. Both are normal "
            "commercial conversations.",
        ],
        [
            "Change a client environment without a change record and a rollback "
            "plan",
            "If it goes wrong there is no way back and no record of what was " "done.",
            "Raise the change record. It takes minutes and it is what makes the "
            "change reversible.",
        ],
        [
            "Approve your own change",
            "A second pair of eyes catches the thing you did not think of.",
            "Get somebody else to approve. The system will not accept you as sole "
            "approver.",
        ],
        [
            "Patch outside an agreed maintenance window without client approval",
            "A reboot at the wrong moment costs the client more than the patch is "
            "worth.",
            "Get approval, or wait for the window.",
        ],
        [
            "Fix the same thing three times without linking it to a problem",
            "Three quick fixes look like good service and are invisible waste.",
            "Nothing — the link is automatic on the third occurrence. Then "
            "actually work the problem.",
        ],
        [
            "Finish an offboarding without removing agents and revoking access",
            "A departed client with our software on their servers is a problem "
            "for both parties.",
            "Complete the checklist with evidence. Offboarding is not complete "
            "until it is.",
        ],
        [
            "Let a client see another client's estate",
            "It is the single assurance a corporate buyer cares about most.",
            "Nothing — portal scope is enforced. If you ever see it fail, report "
            "it the same hour.",
        ],
    ],
    "s8_note": "Session recordings are retained per the contract and the retention "
    "schedule, and every access to one is logged. They exist as evidence "
    "for the engineer as much as for the client.",
    # ============================================ 11. automation
    "s9_lede": "Fourteen behaviours that run without anybody asking, and in this "
    "module they are not a convenience — they are the business model.",
    "s9_intro": [
        "In every other module automation saves time. Here it decides whether "
        "the business line is profitable. A managed service in which every "
        "alert reaches a human being has the cost structure of a break-fix "
        "operation with a monthly invoice, and the margin target of 55 per "
        "cent is unreachable.",
        "The behaviours below do three things: they reduce the number of "
        "alerts that become work, they make sure the ones that do are "
        "acknowledged by somebody, and they produce the commercial artefacts — "
        "credits, consumption notices, service reports — without anybody "
        "assembling them.",
    ],
    "automation_groups": [
        (
            "Turning alerts into work, or not",
            4,
            "Correlation, de-duplication, runbook remediation, window " "suppression",
        ),
        (
            "Making sure somebody responds",
            3,
            "Escalation up the rota, service-level escalation, coverage-gap " "alerts",
        ),
        (
            "Commercial consequences",
            4,
            "Service credits, consumption notices, overage handling, session "
            "metering",
        ),
        (
            "Periodic and lifecycle",
            3,
            "Service reports, offboarding, warranty and problem-record creation",
        ),
    ],
    "s9_table": [
        [
            "Correlates, de-duplicates, raises a ticket and notifies per the "
            "escalation policy",
            "An alert threshold is breached",
            "The on-call engineer, if it gets that far",
        ],
        [
            "Escalates through the on-call rota to the next level",
            "An alert is unacknowledged beyond the threshold",
            "The next person on the rota, then the corporate services head",
        ],
        [
            "Executes the automated remediation, records the outcome, and closes "
            "if it worked",
            "An alert matches a runbook",
            "Nobody, ideally — the client sees a resolved incident",
        ],
        [
            "Escalates to the engineer, then the team lead, then the head of "
            "service",
            "A ticket reaches 50, 75, 90 or 100 per cent of its contractual clock",
            "Increasingly senior people, in order",
        ],
        [
            "Calculates the service credit, records it against the contract and "
            "notifies the account manager",
            "A service level is breached",
            "The account manager, and finance",
        ],
        [
            "Raises a coverage-gap alert and a remediation ticket",
            "An agent stops reporting for the configured period",
            "The engineering team, within 24 hours",
        ],
        [
            "Notifies the account manager; at 100 per cent bills the overage or "
            "requests an uplift",
            "Entitlement consumption reaches 80 or 100 per cent",
            "The account manager, then finance",
        ],
        [
            "Creates a problem record and links the incidents to it",
            "A third recurring incident of the same signature",
            "The quality manager and the assigned engineer",
        ],
        [
            "Suppresses alerting for the defined scope, then resumes " "automatically",
            "A maintenance window starts",
            "Nobody — that is the point",
        ],
        [
            "Generates the client service report, publishes it to the portal and "
            "notifies the contacts",
            "The reporting period ends",
            "The client, on schedule",
        ],
        [
            "Initiates offboarding: agent removal, access revocation and data "
            "return",
            "A client contract terminates",
            "The engineering team and the client",
        ],
        [
            "Raises a priority ticket and notifies the client",
            "A backup job fails twice consecutively",
            "The client's IT manager, immediately",
        ],
        [
            "Stores the recording, meters the duration, attaches it to the ticket "
            "and emits the billable event",
            "A remote session ends",
            "Finance, and the ticket record",
        ],
        [
            "Notifies the account manager with a refresh or extension "
            "recommendation",
            "A client asset's warranty expires within 90 days",
            "The account manager, as a qualified opportunity",
        ],
    ],
    # ============================================ 12. permissions
    "s10_lede": "Ten roles, and one boundary that a corporate client will ask about "
    "before they ask about anything else.",
    "s10_intro": [
        "The permission structure here has an unusual feature: a significant "
        "proportion of the users are not 1000FiX employees. Client portal "
        "users see their own organisation's estate, tickets and reports, and "
        "the enforcement of that boundary is a hard rule rather than a "
        "configuration.",
        "Internally the sensitive areas are credentials, which are never "
        "displayed to anybody; cost to serve, which is visible only to the "
        "corporate services head, the finance manager and the Operations "
        "Director; and session recordings, which require an explicit grant "
        "rather than coming with a role.",
    ],
    "permissions": {
        "roles": [
            "Corporate Services Head",
            "Operations Director",
            "Remote Support Engineer",
            "Account Manager",
            "Contact Centre Supervisor",
            "Contact Centre Agent",
            "Quality Manager",
            "Finance Manager",
            "IT Administrator",
            "Client Portal User",
        ],
        "actions": [
            "Start a remote session",
            "Approve a client change",
            "Run a runbook",
            "See cost to serve",
            "View a session recording",
            "See another client's estate",
        ],
        "marks": [
            ["v", "y", "v", "y", "a", ""],  # Corporate Services Head
            ["", "y", "", "y", "a", ""],  # Operations Director
            ["y", "", "y", "", "a", ""],  # Remote Support Engineer
            ["", "", "", "v", "", ""],  # Account Manager
            ["v", "", "", "", "", ""],  # Contact Centre Supervisor
            ["y", "", "", "", "", ""],  # Contact Centre Agent
            ["", "", "", "", "a", ""],  # Quality Manager
            ["", "", "", "y", "", ""],  # Finance Manager
            ["", "", "y", "", "", ""],  # IT Administrator
            ["", "", "", "", "", ""],  # Client Portal User
        ],
        "sub": "Six actions, and one that nobody may take",
    },
    "s10_roles": [
        [
            "Corporate Services Head",
            "Running the managed-services business",
            "Approving client changes, and seeing cost to serve across every "
            "account",
        ],
        [
            "Remote support engineer",
            "Resolving alerts and tickets remotely",
            "Starting a remote session, and executing runbooks",
        ],
        [
            "Operations Director",
            "Remote resolution and avoided field work",
            "Approving changes, and seeing cost to serve",
        ],
        [
            "Account manager",
            "Renewals and expansion",
            "Nothing exclusive — but they are the only person who takes the "
            "service report to the client",
        ],
        [
            "Contact centre supervisor",
            "Client tickets raised by telephone",
            "Overseeing tickets their team created",
        ],
        [
            "Contact centre agent",
            "Raising tickets for client callers",
            "Starting a remote session from inside a live call",
        ],
        [
            "Quality manager",
            "Major incidents, problems and recurrence",
            "Reviewing session recordings on an explicit grant",
        ],
        [
            "Finance manager",
            "Consumption, overage, credits and profitability",
            "Approving a manual service credit, with the CFO",
        ],
        [
            "IT administrator",
            "Keeping the monitoring platform healthy",
            "Administering the agent platform itself",
        ],
        [
            "Client portal user",
            "Their own organisation's estate and tickets",
            "Raising and tracking their own organisation's tickets",
        ],
    ],
    "s10_restrictions_intro": "Four restrictions are enforced in software. The first is the one a "
    "corporate buyer will ask about in a tender.",
    "s10_restrictions": [
        [
            "Another client's estate",
            "Nobody outside 1000FiX, ever. A client portal user sees only their "
            "own organisation's estate, tickets and reports.",
            "It is the single assurance a corporate client cares about most, and "
            "one failure would end the business line.",
        ],
        [
            "Client credentials",
            "Never displayed to anybody. They are vaulted and used, not read.",
            "Credentials that can be read can be copied, and they are somebody "
            "else's.",
        ],
        [
            "Cost to serve",
            "The corporate services head, the finance manager and the Operations "
            "Director.",
            "It is commercially sensitive and an engineer's technical judgement "
            "should not be shaped by it.",
        ],
        [
            "Session recordings",
            "By explicit grant rather than by role.",
            "A recording of somebody's machine is sensitive to the client and to "
            "the engineer. Access is granted for a reason and logged.",
        ],
        [
            "Change approval",
            "Anybody except the engineer making the change.",
            "A separation of duties. The point is a second perspective, not a "
            "signature.",
        ],
    ],
    "s10_note": "If a client portal user can see anything belonging to another "
    "organisation, stop and report it immediately. That is not a "
    "permission fault; it is the failure that would end this business "
    "line.",
    # ============================================ 13. measurement
    "s11_lede": "Twelve reports and fourteen measures, and one of them is the monthly "
    "deliverable the client actually pays for.",
    "s11_intro": [
        "Managed services is unusual in that one of its reports is a product. "
        "The client service report — attainment, incidents, patch compliance, "
        "estate health and recommendations — is delivered to the client every "
        "month, and delivering it on schedule is itself a measured target of "
        "one hundred per cent.",
        "Internally the three numbers that decide whether the business works "
        "are estate coverage, alert noise ratio and remote resolution rate. "
        "Coverage says whether the promise is being kept. Noise says whether "
        "engineers still believe the alerts. Remote resolution says whether "
        "the margin is real.",
    ],
    "s11_reports": [
        [
            "Estate health board",
            "Every client's assets by health score, with open alerts and coverage "
            "gaps",
            "The remote support team, continuously",
        ],
        [
            "Alert queue",
            "What needs attention, prioritised by severity, client tier and "
            "contractual risk",
            "The remote support team, continuously",
        ],
        [
            "Service-level attainment",
            "Whether contracted promises are being kept, and where they are not",
            "The corporate services head and account managers, weekly and " "monthly",
        ],
        [
            "Client service report",
            "The monthly deliverable: attainment, incidents, patch compliance, "
            "estate health and recommendations",
            "The client, through their portal, monthly",
        ],
        [
            "Patch compliance",
            "Where each client stands by asset class and criticality",
            "The corporate services head and the client, monthly",
        ],
        [
            "Coverage gap report",
            "Assets with unhealthy or missing agents",
            "The corporate services head, daily",
        ],
        [
            "Remote resolution rate",
            "What proportion of work is resolved without a site visit",
            "The Operations Director, monthly",
        ],
        [
            "Client profitability",
            "Cost to serve against contract value",
            "The CFO and corporate services head, monthly",
        ],
        [
            "Entitlement consumption",
            "How much of each contract has been used, and where uplift is due",
            "Account managers and finance, monthly",
        ],
        [
            "Problem and recurring incident",
            "Problems open, permanent fixes applied, recurrence eliminated",
            "The Quality Manager, monthly",
        ],
        [
            "On-call effectiveness",
            "Out-of-hours volume, acknowledgement time and escalation rate",
            "The corporate services head, monthly",
        ],
        [
            "Capacity forecast",
            "Team capacity against contracted and pipeline estate growth",
            "The corporate services head, quarterly",
        ],
    ],
    "s11_kpis": [
        [
            "Monitored assets under management",
            "The size of the business line",
            "8,000, from none",
        ],
        [
            "Contractual service-level attainment",
            "Whether promises are being kept",
            "98 per cent",
        ],
        [
            "Remote resolution rate",
            "Work resolved without anybody travelling",
            "65 per cent, from none",
        ],
        [
            "Gross margin",
            "Whether the business model works",
            "55 per cent — the highest of any 1000FiX line",
        ],
        [
            "Alert-to-ticket automation rate",
            "How much of the handling is automatic",
            "Above 90 per cent, from none",
        ],
        [
            "Time to acknowledge a priority-one alert",
            "Whether the 24/7 commitment is real",
            "Under 10 minutes",
        ],
        [
            "Time to resolve a priority-one incident",
            "How fast the serious things get fixed",
            "Under 4 hours",
        ],
        [
            "Alert noise ratio",
            "Alerts that close with no action taken",
            "Under 15 per cent. Above that, engineers stop believing the queue",
        ],
        [
            "Estate coverage",
            "Contracted assets with a healthy agent",
            "Above 99 per cent",
        ],
        [
            "Service reports delivered on schedule",
            "Whether the monthly deliverable arrives",
            "100 per cent",
        ],
        [
            "Client satisfaction",
            "What the client thinks of the service",
            "Above 4.6 out of 5",
        ],
        ["Contract renewal rate", "Whether they stay", "Above 90 per cent"],
        [
            "Patch compliance across the managed estate",
            "Whether the security promise is being met",
            "Above 95 per cent",
        ],
        [
            "Coverage gaps unresolved beyond 24 hours",
            "Contractual failures left standing",
            "Zero. This one is absolute",
        ],
    ],
    "dials": [
        ("Contractual service levels met", "98%", 0.98),
        ("Work resolved without a site visit", "65%", 0.65),
        ("Alerts handled without an engineer", ">90%", 0.90),
        ("Contracted assets with a healthy agent", ">99%", 0.99),
    ],
    "s11_reading_title": "Reading the estate health board",
    "s11_reading": [
        "The board shows every client's assets by health score, with open "
        "alerts and coverage gaps alongside. It is tempting to sort by health "
        "score and work down the list. That is usually the wrong order.",
        "Sort by coverage gap first, because an asset with no agent has no "
        "health score at all and is the one genuinely at risk. Then sort by "
        "trend rather than absolute score: an asset that has fallen from 94 to "
        "71 in three weeks needs attention more urgently than one that has sat "
        "at 68 for two years.",
    ],
    "s11_reading_table": [
        [
            "A cluster of coverage gaps at one client",
            "Usually a network change or a group policy that blocked the agent.",
            "Treat it as one problem, not twelve tickets. It is also a "
            "contractual clock running.",
        ],
        [
            "A health score that has been low for months",
            "Often an old machine the client knows about and has chosen to live "
            "with.",
            "Check whether it is already on the technology roadmap. If not, it "
            "should be.",
        ],
        [
            "A sharp fall in a previously healthy asset",
            "Something has changed. This is the highest-value signal on the " "board.",
            "Investigate before it becomes an incident. This is what proactive "
            "means in practice.",
        ],
        [
            "High alert volume with low ticket volume",
            "Correlation and de-duplication are working, or noise is being closed "
            "without tuning.",
            "Check the noise ratio. Under 15 per cent it is working; above it, "
            "the rules need tuning.",
        ],
        [
            "One client generating a third of all incidents",
            "Usually one or two assets rather than the whole estate.",
            "Attribute the incidents to assets before concluding anything about "
            "the client.",
        ],
        [
            "Configuration drift across several assets at once",
            "Somebody at the client has made a change outside the change process.",
            "Raise it with the client contact. It is a conversation, not a " "ticket.",
        ],
    ],
    # ============================================ 14. neighbours
    "s12_lede": "M05 delivers a promise that M08 sold, using assets M17 owns, and "
    "hands the commercial consequences to finance.",
    "s12_intro": [
        "The dependency chain in managed services is commercial before it is "
        "technical. The contract module defines what was promised; this module "
        "delivers against it and measures the result; finance turns the "
        "measurement into money — an invoice for overage, or a credit for a "
        "breach.",
        "On the technical side the relationship with the telemetry platform is "
        "worth understanding. M48 owns the general platform for collecting "
        "telemetry from anything; M05 owns the managed-service overlay on it — "
        "the alert rules, the correlation, the health scoring and the client "
        "boundary. Building the overlay separately is what stops a "
        "managed-service alert and an internal equipment reading being treated "
        "as the same kind of thing.",
    ],
    "s12_upstream": [
        [
            "M08 Contract",
            "What the client is entitled to and what was promised",
            "There is no service level to measure and no entitlement to consume",
        ],
        [
            "M17 Asset Registry",
            "Which assets exist and who owns them",
            "The monitored estate has nothing to attach to",
        ],
        [
            "M48 Telemetry Platform",
            "The collection and time-series platform",
            "No metrics arrive and no health scores can be computed",
        ],
        [
            "M33 Party Master",
            "Client identity and corporate hierarchy",
            "Portal scope cannot be enforced",
        ],
        [
            "M29 Identity",
            "Who each engineer is and what they may do",
            "Nothing is attributable and access cannot be controlled",
        ],
        [
            "M27 Contact Centre",
            "The channels client callers arrive on",
            "Telephone and chat tickets stop",
        ],
        [
            "M06 Data Services",
            "Backup execution outcomes",
            "Backup oversight has nothing to oversee",
        ],
        [
            "M24 Records",
            "Retention rules for session recordings",
            "Recordings are kept without a lawful basis or a disposal date",
        ],
        [
            "M55 Workforce",
            "Who is on the on-call rota",
            "Out-of-hours escalation has nobody to reach",
        ],
    ],
    "s12_downstream": [
        [
            "M20 Receivables",
            "Service credits and metered session billing",
            "Credits are never applied and remote work is never billed",
        ],
        [
            "M39 Recurring Billing",
            "Entitlement consumption and overage",
            "Contract billing cannot reflect what was actually delivered",
        ],
        [
            "M02 Field Service",
            "Escalation into a site visit, with context",
            "A remote engineer who needs hands on hardware has no route",
        ],
        [
            "M08 Contract",
            "Attainment against the contracted service level",
            "Renewal has no evidence base",
        ],
        [
            "M07 Sales",
            "Qualified opportunities from ageing assets and " "expiring warranties",
            "A rich source of evidenced pipeline disappears",
        ],
        [
            "M23 Quality",
            "Major incidents, problems and recurrence",
            "Client-facing service quality becomes invisible",
        ],
        [
            "P04 Corporate Portal",
            "Estate health, tickets, reports and " "attainment",
            "The client sees nothing, which removes most of what they bought",
        ],
        [
            "M12 Analytics",
            "The operational and commercial picture of the line",
            "Margin and capacity cannot be managed",
        ],
        [
            "M17 Asset Registry",
            "Health, software inventory and warranty status " "for client assets",
            "The asset record stops reflecting the asset's condition",
        ],
        [
            "M60 Security",
            "Vulnerability and endpoint posture across managed " "estates",
            "Security reporting to clients has no source",
        ],
    ],
    "s12_close_up": [
        {
            "title": "The relationship that defines the module: M05 and M08 "
            "Contract",
            "text": [
                "Every number in this module is meaningless without a "
                "contract behind it. A service-level clock is only a clock "
                "because a contract said four hours. An entitlement is only "
                "consumed because a contract granted forty hours. A credit is "
                "only owed because a contract specified one.",
                "The division is that M08 owns the promise and M05 owns the "
                "evidence about whether it was kept. That sounds like a "
                "technicality until a renewal. An account manager arriving "
                "with a contract but no attainment data is negotiating on "
                "price. One arriving with both is discussing the client's "
                "estate, and the specification puts the renewal target above "
                "90 per cent on the strength of that difference.",
                "The relationship also runs the other way. Monitoring reveals "
                "things the contract should cover and does not — an estate "
                "that has grown by forty per cent, a server generating a third "
                "of the incidents, warranties expiring across a fleet. Each of "
                "those is a contract change that only exists because somebody "
                "was watching.",
            ],
        },
        {
            "title": "The separation that protects both: M05 and M66 Internal " "IT",
            "text": [
                "1000FiX's own internal IT support is a different module, and "
                "the temptation to merge them is worth resisting explicitly, "
                "because they look identical from a distance. Both are "
                "helpdesks. Both handle tickets. Both fix computers.",
                "They are different in the ways that matter. A client ticket "
                "runs against a contractual clock with a financial consequence "
                "for missing it; an internal one does not. A client ticket "
                "consumes an entitlement somebody paid for; an internal one is "
                "a cost. A client expects a monthly report; a colleague does "
                "not. And when both queues are under pressure, one of them has "
                "a service credit attached and the other has a slightly "
                "irritated colleague.",
                "Running them together means the internal work is always "
                "deprioritised, which degrades the company's own operation, or "
                "the client work is not, which costs money. Keeping them "
                "separate means each can be resourced and measured on its own "
                "terms, and it means an engineer always knows which kind of "
                "clock they are working against.",
            ],
        },
    ],
    "s12_note": "M05 generates qualified sales opportunities as a by-product: expiring "
    "warranties, ageing assets, configuration drift and capacity "
    "constraints all surface from monitoring. That pipeline is evidenced "
    "rather than speculative, which makes it the highest-quality lead "
    "source in the company.",
    # ============================================ 15. troubleshooting
    "s13_lede": "What goes wrong in managed services, what it usually means, and what "
    "to do about it.",
    "s13_intro": [
        "The failures here are mostly quiet. An agent that stopped reporting, "
        "a noise ratio creeping upwards, an entitlement being absorbed — none "
        "of them announce themselves, and all of them cost money for months "
        "before anybody looks.",
    ],
    "s13_troubleshooting": [
        [
            "An asset shows no data at all",
            "The agent has stopped reporting. Silent looks exactly like healthy.",
            "Treat it as a coverage gap immediately. It must be reported within "
            "24 hours and the target for unresolved gaps is zero.",
        ],
        [
            "The alert queue is full of things that need no action",
            "Rules are too sensitive, or correlation is not catching a pattern.",
            "Tune the rule. Closing them faster is the wrong fix and the noise "
            "ratio is measured for exactly this reason.",
        ],
        [
            "I cannot start a remote session",
            "Either the client has not consented, or the asset does not have "
            "unattended access under its contract.",
            "Issue the one-time code for an attended session. Unattended access "
            "is a contract grant, not an escalation.",
        ],
        [
            "A runbook ran and made things worse",
            "It recorded what it attempted, which is the starting point.",
            "Read the execution record before doing anything else. Then disable "
            "the runbook, not just this instance of it.",
        ],
        [
            "The service-level clock says we breached and I disagree",
            "The clock honours the contracted coverage window, not office hours.",
            "Check the coverage window on the contract. A 24/7 client's clock ran "
            "overnight.",
        ],
        [
            "A patch broke something",
            "That is what ring deployment is for.",
            "Roll back the ring, hold the remaining machines, and raise it with "
            "the vendor. Record the hold reason so compliance reporting is "
            "honest.",
        ],
        [
            "The same incident keeps coming back",
            "Three occurrences create a problem record automatically.",
            "Work the problem, not the fourth incident. A permanent fix goes "
            "through change management.",
        ],
        [
            "Entitlement is over-consumed and the client is unhappy",
            "It was notified at 80 per cent and again at 100.",
            "Bill it or escalate for an uplift. Absorbing it is against the rules "
            "and it will happen again next month.",
        ],
        [
            "A client says they cannot see something in the portal",
            "Portal scope is defined per client, and their contact permissions "
            "are set by them.",
            "Check both. If a client contact needs more, the client's own "
            "authorised administrator grants it.",
        ],
        [
            "A backup reports success but a restore fails",
            "A successful backup job and a recoverable system are different "
            "claims. Usually a volume was excluded.",
            "This is why restore tests exist. Correct the job definition, take a "
            "full backup and re-test the same week.",
        ],
        [
            "Cost to serve looks wrong for one client",
            "Usually estate growth without an entitlement adjustment, or one "
            "asset generating disproportionate incidents.",
            "Attribute incidents to assets before concluding anything about the "
            "client.",
        ],
        [
            "A departed client's agents are still reporting",
            "Offboarding was not completed.",
            "Complete it with evidence. This is both a security exposure and a "
            "contractual breach, and it is a hard rule.",
        ],
    ],
    "s13_faq": [
        [
            "What is the difference between an alert, an incident and a problem?",
            "An alert is a threshold being crossed. An incident is something "
            "actually wrong that needs resolving. A problem is the underlying "
            "cause behind incidents that keep recurring. Treating them as "
            "synonyms is the commonest confusion in a service desk.",
        ],
        [
            "Can I get unattended access to a client machine to save time?",
            "Only where the contract grants it for that asset. It is a "
            "contractual question, not an operational one.",
        ],
        [
            "Why can I not approve my own change?",
            "A separation of duties. The point is a second perspective on the "
            "rollback plan, not a signature.",
        ],
        [
            "What happens if nobody acknowledges an out-of-hours alert?",
            "It escalates up the on-call rota with acknowledgement tracked at "
            "each step, then to the corporate services head.",
        ],
        [
            "Does a maintenance window stop everything?",
            "It suppresses alerting for the defined scope only, and resumes "
            "automatically at the end. Set the scope carefully.",
        ],
        [
            "Who decides a service credit?",
            "The system, from measured breach. A manual credit needs CFO "
            "approval, which is deliberately awkward.",
        ],
        [
            "Is a session recording kept forever?",
            "No — per the contract and the retention schedule, and every access "
            "to one is logged.",
        ],
        [
            "Can a client see how many incidents another client has?",
            "No. A portal user sees only their own organisation's estate, tickets "
            "and reports, and that is enforced rather than configured.",
        ],
        [
            "What counts as a coverage gap?",
            "A contracted asset without a healthy monitoring agent. It must be "
            "reported within 24 hours, and the target for gaps unresolved beyond "
            "that is zero.",
        ],
        [
            "Why is remote resolution rate a business metric rather than a "
            "technical one?",
            "Because every avoided site visit saves a full technician job slot "
            "plus travel. At 65 per cent it is what makes the margin target "
            "reachable.",
        ],
    ],
    # ============================================ 16. worth
    "s14_lede": "The highest-margin business line 1000FiX has described anywhere, and "
    "the only one whose unit cost falls as it grows.",
    "s14_intro": [
        "A repair job earns once. A managed-service contract earns every "
        "month, and the better the monitoring gets the fewer site visits are "
        "needed to service it. That combination — recurring revenue with "
        "declining marginal cost — does not exist anywhere else in the "
        "company.",
        "The base case is BDT 95 lac a year at steady state, at gross margins "
        "above 55 per cent. But the strategic value is larger than the "
        "revenue. Managed services is how a company stops being a break-fix "
        "vendor and becomes an IT services partner, and that repositioning "
        "changes what 1000FiX can bid for.",
    ],
    "benefits": [
        ("New recurring revenue", 95, "BDT 95 lac/yr at steady state"),
        ("Gross margin", 55, ">55%, the highest of any line"),
    ],
    "benefits_note": (
        "Truck-roll avoidance and proactive intervention are "
        "expressed as rates; both feed the margin figure."
    ),
    "s14_benefits": [
        [
            "A new recurring revenue line",
            "A managed-services business that can actually be delivered at scale, "
            "rather than a promise",
            "BDT 95 lac a year at steady state, base case",
        ],
        [
            "Site visits avoided",
            "Remote resolution of software, configuration and network faults",
            "65 per cent resolved remotely. Each avoided visit saves a full "
            "technician job slot plus travel",
        ],
        [
            "Margin quality",
            "Recurring revenue whose marginal cost falls as automation matures",
            "Above 55 per cent gross margin — the highest of any 1000FiX line",
        ],
        [
            "Proactive intervention",
            "Alerts before failure rather than telephone calls after it",
            "Converts unplanned client downtime into planned maintenance",
        ],
        [
            "Service credit control",
            "Credits calculated automatically and visible before they accumulate",
            "Prevents silent margin erosion on contracts",
        ],
        [
            "Renewal defensibility",
            "Evidence-based monthly service reports and structured reviews",
            "Supports the 90 per cent renewal target",
        ],
        [
            "Corporate account expansion",
            "Monitoring reveals ageing assets, expiring warranties and refresh "
            "needs",
            "Feeds the sales pipeline with qualified, evidenced opportunities",
        ],
        [
            "A 24/7 commitment made real",
            "An on-call rota, out-of-hours routing and coverage-aware service "
            "levels",
            "Turns a marketing claim into a contractual, measurable service",
        ],
    ],
    "s14_soft": [
        [
            "Strategic repositioning",
            "Moves 1000FiX up the value chain from break-fix vendor to IT "
            "services partner. This is the single largest change in how the "
            "company is perceived by corporate buyers.",
        ],
        [
            "Client stickiness",
            "A client with agents deployed and eighteen months of history "
            "accumulated does not switch casually.",
        ],
        [
            "Capability development",
            "Remote engineering is a different skill set from field repair, and "
            "building it broadens the company's talent base.",
        ],
        [
            "Reference customers",
            "Enterprise clients under managed service become the references that "
            "win the next tender.",
        ],
        [
            "Security credibility",
            "Managing clients' security posture requires managing your own. This "
            "line raises 1000FiX's internal standard as a side effect.",
        ],
        [
            "Geographic expansion",
            "Managed services is geography-independent. This is the line that "
            "could serve a second country before a physical branch exists there.",
        ],
    ],
    "s14_close": "Judge this module on three numbers: estate coverage, alert noise "
    "ratio and remote resolution rate. Coverage says the promise is being "
    "kept, noise says engineers still believe the system, and remote "
    "resolution says the margin is real. If those three are healthy, "
    "everything else in the business case follows.",
    # ============================================ 17. learning it
    "s17_lede": "A fortnight for an engineer, and about an hour for everybody else.",
    "s17_intro": [
        "M05 has a small user population and a steep learning curve for the "
        "people at its centre. A remote support engineer needs to understand "
        "monitoring, alerting, runbooks, contractual clocks and remote access "
        "discipline. Almost nobody else needs more than an overview.",
        "The plan below is written for engineers. Account managers should read "
        "sections 1, 6.6 and 13. Anybody else should read section 1 and stop.",
    ],
    "s17_plan": [
        [
            "Before you start",
            "Read section 1, then section 6.1 on remote access discipline, then "
            "the rules in section 10.",
            "30 minutes",
            "Take a remote session lawfully",
        ],
        [
            "Day one",
            "Shadow the alert queue for a morning. Do not touch anything. Notice "
            "how many alerts never became tickets.",
            "1 hour",
            "Understand what correlation is doing",
        ],
        [
            "Day one, afternoon",
            "Run one attended remote session with somebody beside you, end to "
            "end: code, consent, fix, meter, close.",
            "1 session",
            "Complete a session correctly",
        ],
        [
            "Day two",
            "Read section 6.2. Look at three clients' estate health boards and "
            "find the worst asset on each.",
            "1 hour",
            "Read an estate rather than a list of alerts",
        ],
        [
            "Day three",
            "Read section 6.3. Trace one alert from threshold to closure, "
            "including whatever a runbook did.",
            "45 minutes",
            "Know where an alert can end without you",
        ],
        [
            "End of week one",
            "Read section 6.5. Handle three tickets against contractual clocks, "
            "checking the coverage window each time.",
            "1 hour",
            "Work to a contract rather than to office hours",
        ],
        [
            "Week two, early",
            "Read section 6.4 and section 11. Observe one patch ring deployment "
            "and one maintenance window.",
            "45 minutes",
            "Deploy safely",
        ],
        [
            "Week two, middle",
            "Read sections 12 and 15. Raise one change record with a rollback "
            "plan and get it approved.",
            "45 minutes",
            "Change a client environment properly",
        ],
        [
            "End of week two",
            "Read section 6.6 so you understand what the client sees monthly, "
            "then read section 18 and keep it.",
            "30 minutes",
            "Work unsupervised",
        ],
    ],
    "s17_check_intro": "You have got it when these are automatic. For an engineer that is "
    "usually about three weeks of live queue work.",
    "s17_checks": [
        "Run an attended remote session with consent, recording and metering, "
        "without prompting",
        "Say whether an asset is covered, and what to do if it is not",
        "Tell an alert, an incident and a problem apart without thinking about " "it",
        "Read a runbook execution record and know what it changed",
        "Check a contractual coverage window before assuming a clock",
        "Raise a change record with a rollback plan and get it approved by "
        "somebody else",
        "Explain to a client why a patch is being held rather than deployed",
        "Know the three things to report immediately: credentials in a ticket, "
        "a client seeing another client's data, and an agent that stopped "
        "reporting more than a day ago",
    ],
    "s17_note": "Teach remote access discipline before anything else. An engineer who "
    "is fast at diagnosis and casual about consent is a liability; one who "
    "is slow and rigorous is merely new.",
    # ============================================ 18. one page
    "s15_lede": "The module on one page, for a support desk or a first day.",
    "s15_figures": [
        ("62", "things you can do"),
        ("13", "alert states"),
        ("13", "rules enforced"),
        ("14", "automatic behaviours"),
        ("6", "contract types"),
        (">55%", "gross margin target"),
        ("12", "reports available"),
        ("10", "modules depend on it"),
    ],
    "s15_never": [
        "Connect to a client machine without logged consent",
        "Use unattended access where the contract does not grant it",
        "Put a client credential in a ticket, a note or an email",
        "Leave a contracted asset without a healthy agent for more than a day",
        "Change a client environment without a change record and rollback plan",
        "Approve your own change",
        "Patch outside an agreed window without client approval",
        "Absorb over-consumption of an entitlement",
        "Finish an offboarding without removing agents and revoking access",
    ],
    "s15_where": CM.where_to_look("M05"),
}
