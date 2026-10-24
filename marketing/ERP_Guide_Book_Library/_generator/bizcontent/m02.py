# -*- coding: utf-8 -*-
"""
M02 — Field Service & Dispatch Management.

The dispatch board and the technician's phone. This is the module that decides
who goes where, and the one that two to four hundred technicians will spend
eight hours a day inside. The specification calls that application the single
highest-risk artefact in the programme, and the business reading has to respect
that: if technicians reject it, everything downstream degrades with it.

Worked examples name people, places and amounts so the reader can picture the
job. Those details are illustrative; the productivity baselines, thresholds and
rules behind them come from the specification.
"""

from bizcontent import common as CM

CONTENT = {
    # ============================================================== front
    "cover_line": "Who does this job, when, and in what order — answered thousands of "
    "times a day. And then the phone in the technician's hand that makes "
    "sure what happened in the field is what the system knows.",
    "cover_inside": [
        ("Part one", "What the module is for, who uses it, and where it stops"),
        (
            "Part two",
            "All sixty-three things it lets you do, with worked "
            "examples and five walkthroughs from a normal day",
        ),
        (
            "Part three",
            "The rules, the automatic work, the permissions, the "
            "measures and the troubleshooting",
        ),
        ("Appendix A", "The full technical register for builders and testers"),
    ],
    "about": CM.about("the Field Service and Dispatch Management module, M02"),
    "audience": CM.AUDIENCE,
    "how_arranged": CM.HOW_ARRANGED,
    "parts_table": CM.parts_table("M02"),
    "reading_note": CM.READING_NOTE,
    "appendix_note": CM.APPENDIX_NOTE,
    "part1_blurb": CM.PART1_BLURB,
    "part2_blurb": CM.PART2_BLURB,
    "part3_blurb": CM.PART3_BLURB,
    "appendix_blurb": CM.APPENDIX_BLURB,
    "part1_sections": CM.part1_sections(
        "M02", "The kinds of field work it has to carry"
    ),
    "part2_sections": CM.part2_sections("The journey of a field visit"),
    "part3_sections": CM.PART3_SECTIONS,
    "appendix_sections": CM.APPENDIX_SECTIONS,
    "change_control": CM.CHANGE_CONTROL,
    "change_table": CM.change_table("The Dispatch Manager"),
    "change_note": CM.CHANGE_NOTE,
    # ============================================================ exhibits
    "headline": [
        ("4-5", "jobs per technician per day today", "the industry norm is 7-9"),
        ("8-9", "jobs per day the module targets", "the largest single gain"),
        ("55%", "technician utilisation today", None),
        ("35%", "of the working day spent travelling", None),
        ("63", "things the module lets you do", None),
        ("200-400", "technicians will live in the app", None),
        ("24 hrs", "the app must work with no signal", None),
        (
            "BDT 130 lac",
            "a year from productivity alone",
            "the biggest single " "benefit",
        ),
    ],
    "volume": [
        ("3-8", "dispatchers", "one board between them"),
        ("200-400", "field technicians", "the app is their whole day"),
        ("51+", "branches with zones", "and overflow rules between them"),
        ("0%", "auto-assignment today", "the target is 70 per cent"),
        ("70%", "first-time fix today", "the target is 88 per cent"),
    ],
    "volume_title": "The scale of the field operation",
    "volume_sub": "Why dispatch cannot stay a coordinator with a paper list",
    "volume_caption": "The size of the problem M02 has to solve",
    "does": [
        "Deciding which technician should take each job, and why",
        "The dispatch board: calendar, list and map, with drag and drop",
        "Planning routes overnight and re-planning them when the day breaks",
        "Zones, territories and the geofences that define them",
        "The technician mobile application, in full",
        "Working with no signal for a full day, then synchronising cleanly",
        "Live technician tracking and the customer's arrival estimate",
        "Evidence from the field: photographs, video, voice, signature",
        "Van stock consumed at the point of use",
        "Money collected at the customer's door, reconciled the same day",
        "Lone-worker safety, panic alerts and field incident reporting",
    ],
    "does_not": [
        "The customer's promise and the SLA clock, which are M01",
        "Bench work in a workshop, which is M31",
        "Shifts, rosters and leave, which are M55 Workforce",
        "The certification record itself, which is M22 — M02 only enforces it",
        "Van stock levels and replenishment planning, which are M15",
        "Vehicles, their servicing and their documents, which are M46",
        "Moving a device between sites, which is M03 Logistics",
        "Working out a price, which is M11 and M36",
        "Creating the invoice, which is M20",
        "Sending the message to the customer, which is M27",
    ],
    "areas_map": [
        (
            "Deciding who goes",
            17,
            "Scoring, assigning, the board, crews, capacity and the on-call rota.",
        ),
        (
            "Planning the route",
            7,
            "An overnight solve, and a re-solve every time the day changes.",
        ),
        (
            "The technician's phone",
            21,
            "The whole working day in one application, signal or no signal.",
        ),
        (
            "Watching it happen",
            6,
            "Live positions, arrival estimates and what the customer can see.",
        ),
        (
            "When the visit fails",
            7,
            "Nobody home, no access, a bigger job than expected, a device that "
            "has to come back.",
        ),
        (
            "Parts and money in the van",
            5,
            "Stock consumed where it is used, and cash reconciled the same day.",
        ),
    ],
    "area_bars": [
        ("The technician's phone", 21),
        ("Deciding who goes", 17),
        ("Planning the route", 7),
        ("When the visit fails", 7),
        ("Watching it happen", 6),
        ("Parts and money in the van", 5),
    ],
    "channels": [
        "A service order ready for dispatch",
        "An emergency raised at the counter",
        "A contract preventive visit falling due",
        "A monitoring alert from a customer site",
        "A second visit after a failed first one",
        "A workshop job that needs collection",
        "An overflow job offered to a marketplace seller",
        "A multi-visit job returning for its next stage",
    ],
    "channels_hub": "Work order",
    "channels_title": "Everything that becomes a visit",
    "channels_sub": (
        "However the work arises, it becomes a work order with a "
        "technician, a time and a route position"
    ),
    "channels_note": "one instruction, one person",
    "channels_caption": "The sources of field work, and the record they all " "become",
    # ============================================ 1. what it is for
    "s1_lede": "M02 answers three questions thousands of times a day — who does this "
    "job, when, and in what order — and then makes sure what happens at "
    "the customer's door is what the system knows.",
    "s1_intro": [
        "There are two halves to this module and they belong together. The "
        "first is the dispatch board, which three to eight dispatch managers "
        "will work from. It scores every available technician against every "
        "job on skill, certification, zone, current workload, travel time, "
        "what is on their van and what the customer has asked for before, and "
        "then either assigns automatically or hands the dispatcher a ranked "
        "list with the reasoning shown.",
        "The second half is the application in the technician's hand. Between "
        "two and four hundred people will spend their entire working day "
        "inside it: reading the job, running the diagnosis, scanning parts off "
        "the van, photographing what they found, taking the customer's "
        "signature and sometimes their money. It has to do all of that with no "
        "mobile signal, for up to twenty-four hours, and then synchronise "
        "without losing or duplicating anything.",
        "The specification is unusually blunt about the risk here, and it is "
        "worth repeating. The mobile application is the single highest-risk "
        "artefact in the entire programme. If technicians reject it — if it is "
        "slow, if it drains the battery, if it eats their data allowance, if "
        "it loses a job when the signal drops — the field model collapses, and "
        "with it inventory accuracy, invoicing speed, warranty recovery and "
        "quality data. Everything else in this book depends on the phone being "
        "good.",
    ],
    "s1_problem": [
        "Dispatch today is a coordinator with a paper list and a telephone. "
        "Assignment is verbal: somebody is telephoned or sent a message, and "
        "there is no record of whether they accepted. Nobody knows where any "
        "technician is. Nobody plans a route; technicians work out their own "
        "order and often criss-cross the city. Nobody knows a job is at risk "
        "until the customer telephones to complain.",
        "The cost of that is measurable, and the baseline is stark. A 1000FiX "
        "technician completes four to five jobs a day against an industry norm "
        "of seven to nine. Utilisation sits at 55 per cent. Roughly 35 per "
        "cent of the working day is spent travelling. First-time fix is 70 per "
        "cent, which means three visits in ten achieve nothing except a second "
        "appointment.",
        "None of those numbers reflects badly on the technicians. They reflect "
        "a system where nobody could have done better: no route planning, no "
        "way to know whether the right part is on the van before setting off, "
        "no history of the device in the technician's hand, and an hour of "
        "paperwork written up at the end of the day from memory.",
    ],
    "s1_replaces": [
        [
            "A coordinator telephoning technicians one at a time",
            "Candidate scoring across the whole available pool, with automatic "
            "assignment above a confidence threshold",
            "A full morning is assigned in under ten minutes instead of two " "hours.",
        ],
        [
            "No record of who accepted what",
            "Accept or decline in the app, with a reason, and automatic "
            "reassignment on a decline",
            "A job never sits unstarted because everybody assumed somebody else "
            "had it.",
        ],
        [
            "Technicians working out their own order",
            "An overnight route solve honouring time windows, skills and "
            "priorities, re-solved whenever the day changes",
            "Travel drops from 35 per cent of the day towards 22 per cent.",
        ],
        [
            "No idea where anyone is",
            "Live positions on a map, with geofence events on arrival and " "departure",
            "A dispatcher can answer 'where is he?' without telephoning to ask.",
        ],
        [
            "The customer waiting all day",
            "A live tracking page with the technician's photograph, name and "
            "arrival estimate",
            "The most visible single proof that 1000FiX is a modern operation.",
        ],
        [
            "A paper form written up at the end of the day",
            "Everything captured on the phone at the point it happens, offline if "
            "necessary",
            "Documentation time falls from fifteen to twenty minutes plus a "
            "write-up to under five minutes total.",
        ],
        [
            "Van stock as a black hole",
            "Parts scanned off the van at the point of use, replenishment raised "
            "automatically",
            "Van variance goes from untracked to under one per cent.",
        ],
        [
            "Field cash reconciled on trust",
            "Reconciled per technician per shift against jobs and deposits, and "
            "the next shift blocked until it is done",
            "Cash variance becomes a number instead of a worry.",
        ],
    ],
    "s1_one_sentence": "M02 turns dispatch from a person with a phone list into a scored, "
    "routed, tracked operation — and gives the technician everything they "
    "need to finish the job before they leave the customer's premises.",
    # ============================================ 2. who uses it
    "s2_lede": "Two populations with completely different needs: a handful of "
    "dispatchers on a board, and hundreds of technicians on a phone.",
    "s2_intro": [
        "Most modules have one primary audience. M02 has two, and designing "
        "for both is what makes it difficult. A dispatcher needs breadth: "
        "every job, every technician, every zone, all at once, with the ability "
        "to change any of it in one gesture. A technician needs the opposite: "
        "one job at a time, the fewest possible taps, and absolute reliability "
        "when there is no signal.",
        "Everybody else on the list below is a consumer of what those two "
        "populations produce. Inventory finds out what came off the van. "
        "Finance finds out what cash was collected. HR and payroll find out "
        "how many jobs each technician completed and how well. The customer "
        "finds out when somebody is arriving.",
    ],
    "s2_roles": [
        [
            "Dispatch manager",
            "Assigning the day's work, watching for jobs at risk, and rescuing "
            "the ones that slip",
            "The dispatch board: calendar, list and map in one screen",
        ],
        [
            "Field technician",
            "Everything: reading the job, diagnosing, consuming parts, capturing "
            "evidence, taking payment",
            "Today's queue on a phone, in optimised order",
        ],
        [
            "Senior and specialist technician",
            "The same, plus the jobs that need a certification others do not hold",
            "Their own queue, with the harder work in it",
        ],
        [
            "Branch manager",
            "Seeing every technician and job attached to their branch",
            "The live map, filtered to their branch",
        ],
        [
            "Operations Director",
            "Productivity, utilisation, travel share and first-time fix across "
            "the estate",
            "The productivity board",
        ],
        [
            "Inventory manager",
            "What was consumed from which van, and what needs replenishing",
            "Van stock consumption, read-only",
        ],
        [
            "Finance officer",
            "Field cash collected, deposited and reconciled",
            "The daily field cash reconciliation",
        ],
        [
            "Quality manager",
            "Failed visits, field incidents and evidence quality",
            "Failed visit analysis and the incident log",
        ],
        [
            "Contact centre agent",
            "Answering 'when will somebody arrive?'",
            "Job status and the current arrival estimate",
        ],
        [
            "Customer",
            "Watching the technician approach on a map",
            "The tracking page — position, photograph, name and estimate",
        ],
        [
            "Marketplace seller",
            "Work offered to them as overflow capacity",
            "Only the orders they have been awarded, for as long as they hold " "them",
        ],
        [
            "Safety officer",
            "Lone-worker compliance, panic alerts and incidents",
            "The safety report",
        ],
    ],
    "s2_days": [
        {
            "title": "If you dispatch",
            "text": [
                "Your morning starts with a board that has already done most "
                "of the work. Routes were solved overnight at five o'clock and "
                "published to the technicians' phones. What is left for you is "
                "the jobs the system was not confident enough to assign on its "
                "own, and those arrive as a ranked list with the reasoning "
                "written in plain language — this technician, because the "
                "skill matches, the certification is current, they are already "
                "in that zone, and the part is on their van.",
                "The rest of your day is disruption. An emergency comes in and "
                "the affected route re-solves itself; you approve rather than "
                "rebuild. A technician declines a job and it returns to the "
                "pool automatically. Somebody goes quiet and an idle alert "
                "reaches you. The skill in the role shifts from allocating "
                "work to judging exceptions, which is a better use of an "
                "experienced dispatcher than reading out addresses down a "
                "telephone.",
                "Every override you make of an automatic recommendation asks "
                "you for a reason code. That is not bureaucracy: those reasons "
                "are what raise auto-assignment from nothing towards seventy "
                "per cent. When you disagree with the system, telling it why "
                "is the most productive thing you will do all day.",
            ],
        },
        {
            "title": "If you are a field technician",
            "text": [
                "The application is your day. It opens on today's jobs in the "
                "order the route solver put them, each one carrying the "
                "customer, the device, the history, the complaint and who is "
                "paying. You accept or decline; a decline with a reason sends "
                "it back to the pool rather than leaving it stranded.",
                "From then on most of what the system needs happens by itself. "
                "Departing, arriving, starting, pausing, finishing and leaving "
                "are all timestamped, and arrival is confirmed by the geofence "
                "rather than by you remembering to tap something. What you do "
                "actively is the work: run the diagnosis, scan the parts off "
                "your van, photograph before and after, and take the "
                "signature.",
                "It has to work with no signal, and it does — for a full "
                "twenty-four hours. Everything you do offline queues and "
                "synchronises within about thirty seconds of the signal "
                "returning, and if two versions of something disagree you are "
                "shown what was reconciled rather than left to wonder. The "
                "target the specification sets is a job documented in under "
                "five minutes, against fifteen to twenty plus an evening "
                "write-up today.",
            ],
        },
        {
            "title": "If you manage a branch",
            "text": [
                "For the first time you can see the field. Every technician "
                "attached to your branch appears on a live map with their "
                "current job and its state. You will find that most of your "
                "attention goes not to where people are but to failed visits — "
                "the reasons cluster, and the clusters are usually fixable.",
                "The productivity figures will be uncomfortable at first. Jobs "
                "per technician per day, utilisation and travel share have "
                "never been measured at 1000FiX, and the first honest numbers "
                "will be lower than most people assume. That is the "
                "measurement starting, not performance falling.",
            ],
        },
        {
            "title": "If you work in inventory or finance",
            "text": [
                "Van stock stops being a black hole. Parts are scanned as they "
                "are used, replenishment requests raise themselves when a van "
                "drops below its par level, and a daily reconciliation tells "
                "you what each van should be carrying against what it is.",
                "Field cash follows the same discipline. A technician cannot "
                "start their next shift until the previous shift's collections "
                "are reconciled against the jobs and the deposits. It sounds "
                "severe; in practice it turns a monthly argument into a "
                "five-minute daily habit.",
            ],
        },
    ],
    "s2_note": "Technicians cannot see cost or margin, and location history is "
    "visible only to four named roles with every access logged. Location "
    "capture stops outside working hours and during recorded breaks, and "
    "the technician can see when tracking is active.",
    # ============================================ 3. boundary
    "s3_lede": "M02 executes. It does not promise, price, invoice or roster. The most "
    "useful thing to hold on to is that the work order belongs to M02 and "
    "the service order belongs to M01.",
    "s3_intro": [
        "A service order is what the customer asked for. A work order is an "
        "instruction to a named person to do a specific piece of that work at "
        "a specific place and time. One service order can produce several work "
        "orders — a first visit, a follow-up, a collection — and M02 owns all "
        "of them while M01 owns the customer's single view of the whole thing.",
        "That split explains most of the boundary. The SLA clock and the "
        "promise live with the customer's record in M01; M02 works against "
        "them and reports back. The technician's shift pattern lives in M55, "
        "because rostering is a workforce discipline with its own cadence; M02 "
        "consumes availability and never edits it. The certification record "
        "lives in M22; M02 enforces it at the moment of assignment and refuses "
        "to be overridden.",
        "The one boundary people find counter-intuitive is van stock. M02 "
        "consumes parts and reports the consumption; M15 owns the ledger, the "
        "par levels and the replenishment planning. If a van is carrying the "
        "wrong things, that is a conversation with inventory, not with "
        "dispatch.",
    ],
    "s3_shared_intro": "Several ideas span this module and its neighbours. In every case one "
    "module owns the idea and the others use it.",
    "s3_shared": [
        [
            "The work order",
            "M02 — this module owns it",
            "Creates it, assigns it, tracks it and closes it",
        ],
        [
            "The service order",
            "M01",
            "Reports progress against it. Never changes its state directly",
        ],
        [
            "The SLA and the promise",
            "M01",
            "Sequences routes to protect jobs at risk, but does not set or stop "
            "the clock",
        ],
        [
            "Technician availability",
            "M55 Workforce",
            "Reads shifts, leave and holidays so an unavailable person is never "
            "offered",
        ],
        [
            "Certification",
            "M22",
            "Enforces the gate at assignment. The record itself is held " "elsewhere",
        ],
        [
            "Van stock",
            "M15 Inventory",
            "Consumes at the point of use and reports it. Does not hold the " "ledger",
        ],
        [
            "The vehicle",
            "M46",
            "Records which vehicle a technician is using and reports usage",
        ],
        [
            "The diagnostic tree",
            "M01",
            "Runs it on the device, offline, and returns the answers",
        ],
        [
            "The customer notification",
            "M27",
            "Raises the event. Never sends the message itself",
        ],
        [
            "The assignment scoring model",
            "M26 Intelligence",
            "Consumes the model and feeds it override reasons. Does not train " "it",
        ],
    ],
    # ============================================ 4. kinds of work
    "s4k_title": "The kinds of field work it has to carry",
    "s4k_lede": "One technician, one van and one working day — but seven quite "
    "different shapes of visit, each with its own constraints.",
    "s4k_intro": [
        "Field work is not uniform. A routine repair booked three days ago and "
        "an emergency raised twenty minutes ago make completely different "
        "demands on the schedule. A two-person crew installing something is a "
        "different planning problem from one technician replacing a part. A "
        "corporate site with thirty devices is one journey and thirty "
        "outcomes.",
        "M02 handles all of them on the same board and in the same "
        "application, but the rules differ. Emergency work may displace "
        "lower-priority jobs — but never a job that is already at risk of "
        "breaching its own promise. Multi-visit work has to keep one coherent "
        "customer view across several appointments. Marketplace overflow can "
        "only be offered where score, certification and category access all "
        "qualify.",
    ],
    "kinds_columns": [
        (
            "Planned work",
            "Scheduled in advance, routed overnight",
            [
                "Routine repair at a customer site",
                "Contract preventive visits",
                "Installations and commissioning",
                "Multi-visit jobs, tracked as one story",
            ],
        ),
        (
            "Unplanned work",
            "Arrives during the day and disrupts",
            [
                "Emergency insertion, with automatic re-routing",
                "A second visit after a failed first",
                "An on-site scope change needing fresh approval",
                "Overflow offered to marketplace capacity",
            ],
        ),
        (
            "Work with extra constraints",
            "Same visit, additional rules",
            [
                "Brand warranty — certification enforced absolutely",
                "Multi-technician crews with separate time tracking",
                "After-hours work from the on-call rota",
                "Corporate sites — one visit, many devices",
            ],
        ),
    ],
    "kinds_title": "Three families of field work",
    "kinds_sub": "Different planning problems, one board and one application",
    "s4k_header": [
        "The kind of visit",
        "What is different about it",
        "What stays the same",
    ],
    "s4k_table": [
        [
            "Routine repair",
            "Booked in advance, routed in the overnight solve, single technician.",
            "One work order, geofenced arrival, evidence captured, signature at "
            "the end",
        ],
        [
            "Emergency",
            "Inserted during the day. The nearest qualified available technician "
            "is identified and their remaining route re-solved automatically. It "
            "may displace lower-priority work but never a job already at risk.",
            "As above",
        ],
        [
            "Contract preventive",
            "Created by a maintenance plan rather than a person, and scheduled "
            "against the contract's window rather than an emergency clock.",
            "As above",
        ],
        [
            "Brand warranty work",
            "Cannot be assigned to a technician whose certification for that "
            "brand has lapsed. The system removes them from the pool "
            "automatically on expiry.",
            "As above",
        ],
        [
            "Multi-technician crew",
            "Roles are defined — lead, assistant, specialist — and each member's "
            "time is tracked separately.",
            "As above",
        ],
        [
            "Multi-visit job",
            "Several appointments under one coherent customer view, with the SLA "
            "and the tracking page staying sensible across all of them.",
            "As above",
        ],
        [
            "Corporate site visit",
            "One journey, many devices, each with its own recorded outcome under "
            "a shared batch reference.",
            "As above",
        ],
        [
            "After-hours and on-call",
            "Dispatched from the standby rota rather than the day roster. "
            "Working-time limits apply and overtime must be approved first.",
            "As above",
        ],
        [
            "Marketplace overflow",
            "An outside engineer does the work. Offered only where score, "
            "certification and category access all qualify, and their access is "
            "scoped to that order and time-limited.",
            "As above",
        ],
        [
            "Failed visit",
            "No work happens, but the visit still has to be evidenced — "
            "geotagged proof is required before a failed visit can be recorded.",
            "The record, the evidence and the customer notification",
        ],
    ],
    "s4k_caption": "The shapes of field work and what distinguishes each",
    "s4k_note": "Emergency insertion is the one that causes arguments. The rule is "
    "computed, not discretionary: an emergency may displace lower-priority "
    "jobs, but it may never displace a job that is already at risk of "
    "breaching. The board will not offer you that option.",
    # ============================================ 5. vocabulary
    "s4_lede": "Fifteen words that mean something specific here — several of them "
    "borrowed from logistics rather than from repair.",
    "s4_intro": [
        "Dispatch has its own vocabulary, much of it shared with delivery and "
        "haulage rather than with service. These are the terms that appear on "
        "the board, in the application and in every report the module "
        "produces.",
    ],
    "s4_glossary": [
        [
            "Work order",
            "An instruction to a named person to do a specific piece of work at a "
            "specific place. Not the customer's request — that is the service "
            "order in M01.",
            "The central record of this module",
        ],
        [
            "Candidate scoring",
            "Ranking every available technician against a job on skill, "
            "certification, zone, load, travel time, van stock, customer "
            "preference and past rating.",
            "Runs the moment a job is ready for dispatch",
        ],
        [
            "Confidence threshold",
            "The score above which the system assigns on its own rather than "
            "asking a dispatcher.",
            "Configurable. Raising it means more automation and more risk",
        ],
        [
            "Zone and territory",
            "The geographic area a technician normally works, with defined "
            "overflow rules to neighbouring zones.",
            "Set per branch; a major input to scoring",
        ],
        [
            "Geofence",
            "An invisible boundary around a customer site, a branch or a "
            "warehouse. Crossing it raises an event automatically.",
            "How arrival is confirmed without anybody tapping anything",
        ],
        [
            "Route solve",
            "Working out the best order and path for every technician's day, "
            "honouring time windows, skills, capacity and priorities.",
            "Runs nightly at five o'clock, and again whenever the day changes",
        ],
        [
            "Re-optimisation",
            "Re-solving the affected routes when a job is added, cancelled or "
            "over-runs, or a technician becomes unavailable.",
            "Happens continuously; the dispatcher approves rather than rebuilds",
        ],
        [
            "ETA",
            "The published estimate of when the technician will arrive, "
            "recalculated as conditions change.",
            "Shown to the customer on the tracking page",
        ],
        [
            "Van stock and par level",
            "What a technician carries, and what they are supposed to carry. Par "
            "levels are set per technician from their skill profile and job mix.",
            "Consumed here, owned by M15 Inventory",
        ],
        [
            "Offline mode",
            "The application working with no signal for up to twenty-four hours, "
            "queueing every action.",
            "Not an edge case. Large parts of the country need it daily",
        ],
        [
            "Conflict resolution",
            "What happens when the phone and the server disagree after a long "
            "period offline. The server decides, and the technician is shown what "
            "was reconciled.",
            "Visible in the app, not hidden",
        ],
        [
            "Failed visit",
            "A visit where no work happened — nobody home, no access, unsafe. "
            "Requires geotagged evidence before it can be recorded.",
            "Reported and analysed weekly by cause",
        ],
        [
            "Lone-worker check-in",
            "A periodic confirmation that a technician working alone is safe, "
            "with a panic alert available.",
            "A duty-of-care mechanism the company does not currently have",
        ],
        [
            "First-time fix",
            "The proportion of jobs finished on the first visit. The single most "
            "important field measure.",
            "70 per cent today; the target is 88 per cent",
        ],
        [
            "Utilisation",
            "The share of a technician's paid time spent on productive work "
            "rather than travelling, waiting or idle.",
            "55 per cent today; the target is 82 per cent",
        ],
    ],
    # ============================================ 6. what you can do
    "s5_lede": "Sixty-three things, in six areas. Twenty-one of them are in the "
    "technician's phone, which tells you where the weight of this module "
    "sits.",
    "s5_intro": [
        "The areas below follow the shape of a field day: deciding who goes, "
        "planning the route, doing the work, watching it happen, handling the "
        "visits that fail, and settling the parts and money at the end.",
        "The third area — the technician's phone — is the largest and the most "
        "consequential. Read it carefully even if you never use the "
        "application yourself, because almost every benefit claimed elsewhere "
        "in this book depends on technicians being willing to use it.",
    ],
    "areas": [
        {
            "title": "Deciding who goes",
            "who": [
                ("Mostly used by", "Dispatch managers"),
                (
                    "Also relied on by",
                    "Branch managers and the operations "
                    "director, who see its results",
                ),
                ("Where it happens", "The dispatch board"),
            ],
            "intro": [
                "Assignment used to be a judgement made under time pressure "
                "with incomplete information. This area turns it into a score "
                "that can be explained. Every available technician is ranked "
                "against the job on eight or nine factors at once, and if the "
                "top candidate is clearly ahead the job is simply assigned. If "
                "not, the dispatcher gets the ranked list with the reasoning "
                "in plain language and makes the call.",
                "The design point worth understanding is that the system is "
                "trying to earn the dispatcher's agreement rather than replace "
                "them. Auto-assignment starts at zero and is targeted to reach "
                "seventy per cent, and it gets there by learning from every "
                "override a dispatcher makes and explains.",
            ],
            "features": [
                [
                    "Candidate scoring",
                    "Ranks every available technician against the job on skill, "
                    "certification, zone, current load, travel time, van stock, "
                    "customer preference and past rating.",
                    "The best person for a job in Mirpur is chosen on evidence, "
                    "not on who answered the phone.",
                ],
                [
                    "Automatic assignment",
                    "Assigns without asking when the top candidate is clearly "
                    "ahead; otherwise hands you the ranked list.",
                    "A dispatcher spends their attention on the difficult 30 per "
                    "cent.",
                ],
                [
                    "The dispatch board",
                    "Calendar, list and map in one screen, with drag-and-drop "
                    "reassignment and immediate conflict detection.",
                    "Moving a job to another technician is one gesture, and the "
                    "board tells you at once if it will not work.",
                ],
                [
                    "Capacity view",
                    "Shows available capacity by zone, skill and day, and "
                    "highlights over- and under-capacity before it bites.",
                    "Next Thursday's shortage of printer technicians in Uttara is "
                    "visible on Monday.",
                ],
                [
                    "Territories and zones",
                    "Defines zones and geofences per branch, assigns technicians "
                    "to them, and sets the rules for overflow.",
                    "Work stays local by default and spills over by rule rather "
                    "than by negotiation.",
                ],
                [
                    "Availability from the roster",
                    "Reads shifts, leave and holidays so that somebody who is not "
                    "working is never offered.",
                    "Nobody is dispatched on their day off.",
                ],
                [
                    "Certification gate",
                    "Refuses to assign brand warranty work to a technician whose "
                    "certification has expired.",
                    "The brand cannot reject the claim on the grounds of who did "
                    "the work.",
                ],
                [
                    "Multi-technician crews",
                    "Assigns a crew with defined roles and tracks each member's "
                    "time separately.",
                    "A two-person installation is costed properly.",
                ],
                [
                    "Multi-visit jobs",
                    "Plans and tracks work needing several visits while keeping "
                    "the promise and the customer's view coherent.",
                    "The customer sees one job, not three appointments.",
                ],
                [
                    "Emergency insertion",
                    "Slots an emergency in and re-optimises the affected "
                    "technician's remaining route automatically.",
                    "A hospital's failed printer is covered without wrecking the "
                    "rest of the day.",
                ],
                [
                    "External capacity",
                    "Offers overflow work to marketplace sellers where score, "
                    "certification and category access all qualify.",
                    "A demand spike is absorbed without turning customers away.",
                ],
                [
                    "Dispatcher productivity tools",
                    "Bulk assignment, saved filters, keyboard shortcuts and undo.",
                    "A full morning is assigned in under ten minutes.",
                ],
                [
                    "Assignment explanation",
                    "Says, in plain language, why a technician was recommended.",
                    "A dispatcher can agree or disagree on the reasoning rather "
                    "than on faith.",
                ],
                [
                    "Override logging",
                    "Records every override of an automatic recommendation with a "
                    "reason code.",
                    "Those reasons are what raise auto-assignment from nothing to "
                    "seventy per cent.",
                ],
                [
                    "Slot capacity management",
                    "Manages bookable capacity by branch, skill and slot so that "
                    "intake cannot overbook.",
                    "The counter stops promising Thursday appointments that "
                    "Thursday cannot deliver.",
                ],
                [
                    "Working-time awareness",
                    "Prevents scheduling that would breach working-time limits "
                    "without approved overtime.",
                    "The company stays on the right side of both the law and the "
                    "technician.",
                ],
                [
                    "Standby and on-call rota",
                    "Manages the after-hours rota and dispatches from it.",
                    "An 11 p.m. emergency reaches somebody who is expecting to be "
                    "called.",
                ],
            ],
            "example": (
                "a morning assigned in eight minutes",
                "It is 07:50 on a Tuesday. Overnight the route solver has "
                "already planned and published routes for the thirty-one "
                "technicians attached to the Dhaka North branches, so most of "
                "the day is settled before anybody arrives. The dispatcher "
                "opens the board and sees nine jobs the system was not "
                "confident enough to assign. Six are straightforward: the "
                "reasoning shows a clear top candidate and she accepts each in "
                "one click. One is a brand warranty repair where the nearest "
                "technician's certification lapsed last week — the system has "
                "already removed him from that pool, and the next candidate is "
                "twenty minutes further away. She takes it. One needs a crew "
                "of two and she assigns a lead and an assistant. The last is a "
                "customer who has asked specifically for the technician who "
                "came last time; the score ranks him third on travel, but she "
                "overrides with the reason code 'customer preference'. Total "
                "elapsed time: eight minutes. Under the old way of working the "
                "same morning took until about half past nine, on the "
                "telephone.",
            ),
            "mistakes": [
                "Overriding a recommendation without giving a reason, or "
                "giving the same reason for everything. The reason codes are "
                "the training signal; generic ones teach the system nothing.",
                "Dragging jobs around the board to make the map look tidy. The "
                "route solver has already balanced travel against promises, "
                "and a tidier map is often a later day.",
                "Assigning around the certification gate by re-typing the "
                "order. It voids the warranty claim and it will be visible.",
                "Treating the capacity view as a report rather than a warning. "
                "It is showing you next week so that this week you can do "
                "something about it.",
                "Inserting an emergency and then manually re-sequencing the "
                "rest of the route. The re-optimisation has already done it, "
                "and better.",
            ],
        },
        {
            "title": "Planning the route",
            "who": [
                ("Mostly used by", "Nobody, directly — it runs overnight"),
                (
                    "Also relied on by",
                    "Dispatchers approving re-solves, and "
                    "technicians following the sequence",
                ),
                (
                    "Where it happens",
                    "At five o'clock in the morning, and " "continuously after that",
                ),
            ],
            "intro": [
                "Routing is the quietest area of the module and one of the "
                "most valuable. At five o'clock each morning the system solves "
                "the whole day for every technician at once — which jobs, in "
                "which order, by which roads — honouring time windows, skill "
                "requirements, van capacity and job priorities. The result is "
                "pushed to the phones before anybody starts.",
                "Then reality happens, and the second half of this area "
                "matters more. A job is cancelled, another over-runs by two "
                "hours, an emergency arrives, a technician calls in sick. Each "
                "of those triggers a re-solve of the affected routes only, and "
                "the change reaches the affected phones. Nobody re-plans a day "
                "by hand.",
            ],
            "features": [
                [
                    "Overnight route solve",
                    "Plans the whole next day for every technician at once, "
                    "respecting time windows, skills, capacity and priorities.",
                    "Technicians wake up to a sensible day rather than inventing "
                    "one.",
                ],
                [
                    "Live re-optimisation",
                    "Re-solves the affected routes when the day changes.",
                    "One over-running job does not wreck the four behind it.",
                ],
                [
                    "Travel-time estimation",
                    "Estimates travel from road-network data, with live traffic "
                    "for the Dhaka metro area.",
                    "The plan reflects Dhaka traffic rather than a straight line "
                    "on a map.",
                ],
                [
                    "Route publishing",
                    "Pushes the sequence to the technician's app and hands off to "
                    "turn-by-turn navigation.",
                    "No printed list, no telephoned addresses.",
                ],
                [
                    "Route adherence",
                    "Compares planned against actual and flags material " "deviation.",
                    "A technician consistently ignoring the sequence is a "
                    "conversation, and sometimes the plan is wrong.",
                ],
                [
                    "SLA-aware sequencing",
                    "Protects jobs that are close to their promise even at the "
                    "cost of extra travel.",
                    "The company would rather drive further than break a "
                    "commitment.",
                ],
                [
                    "Zone rebalancing",
                    "Recommends zone or roster changes where demand and capacity "
                    "are persistently mismatched.",
                    "A structural problem in Gazipur surfaces as a "
                    "recommendation, not as months of overtime.",
                ],
            ],
            "example": (
                "the day that rearranged itself",
                "A technician's second job of the day, a printer service in "
                "Banani, turns out to need a part he does not carry. He "
                "records it as cannot-complete with the reason, and the job "
                "converts to a follow-up. That leaves ninety minutes free in "
                "the middle of his route. Meanwhile a corporate customer in "
                "Gulshan — two kilometres away — has logged an urgent fault at "
                "10:40. The re-solve places it in his gap rather than sending "
                "the technician who was originally nearest but is now behind "
                "schedule. The customer's tracking page updates with an "
                "arrival estimate of 11:35. Nobody telephoned anybody, and the "
                "day absorbed both the failure and the emergency without any "
                "other job moving.",
            ),
            "mistakes": [
                "Assuming the overnight solve is a suggestion. It has balanced "
                "constraints no individual can hold in their head.",
                "Reading a route adherence flag as an accusation. Sometimes the "
                "plan is wrong, and persistent deviation in one zone is "
                "usually telling you something about the roads.",
                "Ignoring zone rebalancing recommendations because the roster "
                "is difficult to change. The recommendation is the cheap part; "
                "the overtime is the expensive part.",
            ],
        },
        {
            "title": "The technician's phone",
            "who": [
                ("Mostly used by", "Every field technician, for eight hours a " "day"),
                (
                    "Also relied on by",
                    "Everybody downstream — inventory, " "finance, warranty, quality",
                ),
                ("Where it happens", "At the customer's door, often with no " "signal"),
            ],
            "intro": [
                "Twenty-one of the module's sixty-three functions are in this "
                "application, and the specification is explicit that it is the "
                "highest-risk artefact in the whole programme. That is not "
                "because it is technically hard, although it is. It is because "
                "adoption is not optional in any useful sense: if technicians "
                "work around it, every number this book promises stops being "
                "true.",
                "So the design is unusually attentive to things that do not "
                "look like features. Photographs are compressed and "
                "non-critical uploads deferred, because a technician's mobile "
                "data costs them money. Location and sync frequency are "
                "managed so the phone survives a full shift. Blurred or dark "
                "photographs are rejected at the point of capture rather than "
                "discovered as useless a week later.",
                "And it all has to work with no signal at all, for a full "
                "day, then synchronise inside thirty seconds of reconnection "
                "with nothing lost and nothing duplicated. The target for "
                "offline sync failures is zero — not low, zero.",
            ],
            "features": [
                [
                    "Today's job queue",
                    "Shows the day's work in route order, each job carrying the "
                    "customer, device, history, complaint and who is paying.",
                    "A technician arrives knowing what this device has been in "
                    "for before.",
                ],
                [
                    "Accept or decline",
                    "Accepts a job, or declines it with a reason, which sends it "
                    "back to the pool.",
                    "A job is never stranded because somebody assumed it had been "
                    "picked up.",
                ],
                [
                    "Navigation",
                    "Hands off to turn-by-turn navigation to the job address.",
                    "No addresses read out over the telephone.",
                ],
                [
                    "Automatic timestamps",
                    "Records departed, arrived, started, paused, completed and "
                    "left, with location and geofence validation.",
                    "The record of the visit builds itself while the technician "
                    "works.",
                ],
                [
                    "On-site diagnosis",
                    "Runs the full diagnostic tree on the device, offline.",
                    "A junior technician reaches a senior technician's conclusion "
                    "at a customer's kitchen table.",
                ],
                [
                    "Parts scanning",
                    "Scans van stock by barcode or QR to consume it, and requests "
                    "what is not on the van.",
                    "Consumption is recorded where it happens, not remembered at "
                    "the depot.",
                ],
                [
                    "Media capture",
                    "Takes before and after photographs, short video and voice "
                    "notes, with the metadata attached automatically.",
                    "The warranty evidence pack assembles itself.",
                ],
                [
                    "Electronic signature",
                    "Captures the customer's signature on screen with the "
                    "declaration in Bengali or English.",
                    "No paper, and no argument about what was agreed.",
                ],
                [
                    "On-site payment",
                    "Takes cash, mobile money or card at the door, issues a "
                    "receipt and reconciles to the branch cash book.",
                    "Money is collected while the customer is pleased with the "
                    "work.",
                ],
                [
                    "Offline operation",
                    "Works fully for twenty-four hours with no signal, queueing "
                    "everything.",
                    "A day in a rural sub-district is a normal working day.",
                ],
                [
                    "Conflict resolution",
                    "Resolves disagreements between phone and server "
                    "deterministically, and shows the technician what was "
                    "reconciled.",
                    "A long offline stretch does not end in a mystery.",
                ],
                [
                    "Offline knowledge",
                    "Carries repair manuals, wiring diagrams and previous repair "
                    "notes with no signal needed.",
                    "The answer is in the technician's pocket rather than back at "
                    "the branch.",
                ],
                [
                    "In-app messaging",
                    "Messages dispatch, the workshop and, where permitted, the "
                    "customer — queueing offline.",
                    "One channel instead of three personal phone numbers.",
                ],
                [
                    "Personal scorecard",
                    "Shows the technician their own jobs, ratings, first-time-fix "
                    "rate and earned incentive.",
                    "Performance stops being something that happens to you in a "
                    "meeting.",
                ],
                [
                    "Safety and duty of care",
                    "Records site safety checks, lone-worker check-in and a panic "
                    "alert.",
                    "Somebody knows where you are and can reach you.",
                ],
                [
                    "Field expense capture",
                    "Records travel and incidental expenses in the field.",
                    "Reimbursement stops depending on keeping receipts in a van "
                    "door.",
                ],
                [
                    "Photo quality validation",
                    "Rejects blurred, dark or duplicate evidence photographs when "
                    "they are taken.",
                    "The claim is not rejected two months later for unusable "
                    "evidence.",
                ],
                [
                    "Data-usage optimisation",
                    "Compresses uploads and defers non-critical ones.",
                    "The application does not cost the technician money to use.",
                ],
                [
                    "Battery optimisation",
                    "Manages location and sync frequency to last a full shift.",
                    "The phone is still alive for the last job of the day.",
                ],
                [
                    "App update management",
                    "Delivers forced and optional updates with version "
                    "compatibility enforced.",
                    "Four hundred phones stay on versions that work together.",
                ],
                [
                    "Device enrolment",
                    "Registers technician devices and revokes access on loss or "
                    "departure.",
                    "A lost phone is not a data breach.",
                ],
            ],
            "example": (
                "a full job with no signal at all",
                "A technician is sent to a customer in a sub-district outside "
                "Mymensingh where there is no usable mobile data. His route "
                "and all four job records were on the phone before he left the "
                "branch. On site the geofence records his arrival from the "
                "device's own location. He runs the diagnostic tree, which is "
                "held locally, and identifies a failed power board. He scans "
                "the replacement off his van, photographs the old and new "
                "boards, and consults the wiring diagram — also local. The "
                "customer signs on screen and pays in cash; a receipt prints "
                "from the portable printer. He records the payment and moves "
                "on. Six hours later, back within coverage on the road home, "
                "everything queued that day synchronises in under thirty "
                "seconds: four completed jobs, eleven photographs, three parts "
                "consumed, two cash collections and around forty timestamps. "
                "Inventory sees the van drop below par and raises a "
                "replenishment. Finance sees the cash to be reconciled at "
                "shift end. None of that required a signal at the moment it "
                "mattered.",
            ),
            "mistakes": [
                "Taking photographs on the phone's own camera app instead of "
                "in the application. Those have no job, no timestamp "
                "validation and no place in the evidence pack.",
                "Marking a job complete before the customer has signed, "
                "intending to collect the signature afterwards. The signature "
                "evidences the state at handover.",
                "Turning off location to save battery. Battery is managed by "
                "the app, and an arrival with no geofence event has to be "
                "explained.",
                "Waiting for a signal before recording anything. The whole "
                "point of the queue is that you should work as though you were "
                "online.",
                "Collecting cash and not recording it in the app at the time. "
                "The shift will not close, and the reconciliation becomes "
                "somebody's evening.",
            ],
            "caution": "The offline target for lost or duplicated actions is zero, "
            "not 'low'. If you ever see a job that synchronised wrongly, "
            "report it immediately rather than correcting it by hand — a "
            "single reproducible sync fault matters more than the job it "
            "affected.",
        },
        {
            "title": "Watching it happen",
            "who": [
                ("Mostly used by", "Dispatchers and branch managers"),
                (
                    "Also relied on by",
                    "Customers, who see a restricted version " "of the same data",
                ),
                ("Where it happens", "The live map, and the customer's phone"),
            ],
            "intro": [
                "Six functions, and they change the relationship with the "
                "customer more than anything else in the module. A live map "
                "showing the technician's position, photograph, name and "
                "arrival estimate is the single most visible proof that "
                "1000FiX is a modern operation — and it removes the reason for "
                "most of the calls asking where somebody is.",
                "Internally the same data drives the dispatcher's map and the "
                "geofence events that timestamp arrivals. It is also the most "
                "privacy-sensitive part of the system, and it is treated that "
                "way: capture stops outside working hours and during recorded "
                "breaks, history is visible to four named roles only, and "
                "every access is logged.",
            ],
            "features": [
                [
                    "Live technician tracking",
                    "Streams technician positions at a set interval to an "
                    "operations map.",
                    "A dispatcher answers 'where is she?' by looking, not by "
                    "telephoning.",
                ],
                [
                    "Customer tracking page",
                    "Gives the customer a live map with the technician's "
                    "position, photograph, name and arrival estimate on the day.",
                    "The customer stops waiting in all day for a visit that could "
                    "be at four o'clock.",
                ],
                [
                    "Arrival estimate",
                    "Recalculates and republishes the estimate as conditions "
                    "change, raising an event when it moves materially.",
                    "A traffic delay reaches the customer before it becomes a "
                    "complaint.",
                ],
                [
                    "Geofence events",
                    "Raises automatic events on entering and leaving customer, "
                    "branch and warehouse boundaries.",
                    "Arrival is recorded whether or not anybody remembers to tap "
                    "anything.",
                ],
                [
                    "Privacy controls",
                    "Suspends location capture outside working hours and during "
                    "breaks, and logs every access to location history.",
                    "Tracking is a working-time tool, and it is visibly limited "
                    "to that.",
                ],
                [
                    "Route replay",
                    "Replays a technician's actual route and events for "
                    "investigation.",
                    "A disputed visit is settled from the record.",
                ],
            ],
            "example": (
                "the visit the customer could watch",
                "A customer in Dhanmondi has a morning appointment. At 09:12 "
                "the technician records departure from the branch and the "
                "system publishes an arrival estimate of 09:41 with a link. "
                "The customer opens it and sees a map, the technician's "
                "photograph and name, and a moving marker. At 09:26 traffic on "
                "Mirpur Road pushes the estimate to 09:52; the change is "
                "material, so an updated message goes out automatically. At "
                "09:50 the technician crosses the geofence and arrival is "
                "recorded without anybody tapping anything. The customer did "
                "not telephone the hotline once, and the branch received no "
                "'where is he?' call to handle.",
            ),
            "mistakes": [
                "Using the map to check up on individuals rather than to "
                "manage the day. Every access to location history is logged, "
                "and that log exists to be read.",
                "Promising a customer a time that is tighter than the "
                "published estimate. The estimate is what they are watching.",
                "Treating a geofence arrival as optional and tapping arrival "
                "manually from down the road. It requires an exception reason "
                "and it is visible.",
            ],
            "caution": "Location history is accessible to four named roles only and "
            "every access is recorded. If you can see a technician's "
            "location history and your role should not permit it, that is "
            "a fault to report the same day.",
        },
        {
            "title": "When the visit fails",
            "who": [
                ("Mostly used by", "Technicians, at the door"),
                (
                    "Also relied on by",
                    "Dispatchers rescheduling, and the "
                    "quality manager analysing causes",
                ),
                ("Where it happens", "On the doorstep, usually in a hurry"),
            ],
            "intro": [
                "Roughly one visit in ten achieves nothing: nobody is home, "
                "the building will not let the technician in, the job turns "
                "out to be bigger than the estimate, or the device simply "
                "cannot be fixed on site. Handling those well is worth more "
                "than it sounds, because a failed visit that is recorded badly "
                "becomes a dispute, and one that is recorded well becomes a "
                "statistic somebody can act on.",
                "The rule that matters here is that a failed visit requires "
                "geotagged evidence before it can be recorded at all. That "
                "protects the technician as much as the company: 'the "
                "technician never came' is a common complaint and a "
                "photograph of a locked gate with a time and a location on it "
                "ends the conversation.",
            ],
            "features": [
                [
                    "Customer absent",
                    "Records a failed visit with geotagged evidence, notifies the "
                    "customer and triggers rescheduling or a charge, per policy.",
                    "A wasted journey is evidenced, costed and rebooked in one "
                    "action.",
                ],
                [
                    "Cannot complete",
                    "Records why — parts, access, complexity, safety — and turns "
                    "it into a follow-up visit or a workshop transfer.",
                    "The job continues rather than restarting.",
                ],
                [
                    "On-site scope change",
                    "Raises a revised estimate at the customer's premises and "
                    "gets approval before going further.",
                    "A bigger job than expected is agreed, not assumed.",
                ],
                [
                    "Convert to collection",
                    "Turns a failed on-site repair into a pick-and-drop "
                    "consignment handled by M03.",
                    "The device comes to the workshop without a second visit to "
                    "arrange it.",
                ],
                [
                    "Field incident reporting",
                    "Reports accidents, hazards, abuse or security incidents from "
                    "the field.",
                    "What happens to technicians on the road stops being informal "
                    "knowledge.",
                ],
                [
                    "Customer rescheduling",
                    "Lets the customer move the appointment from the tracking "
                    "link, within policy.",
                    "A customer who cannot be there says so before the journey, "
                    "not after.",
                ],
                [
                    "No-access evidence",
                    "Captures geotagged proof when access is refused or nobody is "
                    "present.",
                    "Settles 'nobody came' with a photograph and a time.",
                ],
            ],
            "example": (
                "the visit that became a collection",
                "A technician arrives at a customer's house to repair a "
                "washing machine and finds the fault is a failed control "
                "board, not the pump the intake diagnosis suggested. Board "
                "work is Level 3 and cannot be done on a kitchen floor. He "
                "records cannot-complete with the reason 'requires workshop — "
                "board level', photographs the board and the serial plate, and "
                "converts the visit to a collection. M03 receives a "
                "consignment request; the customer is offered a pick-up slot "
                "from the tracking link and chooses the following morning. The "
                "service order in M01 stays open with its clock running and "
                "its history intact. What did not happen: a second visit "
                "arranged by telephone, a device carried away without a "
                "custody record, and a customer left wondering.",
            ),
            "mistakes": [
                "Recording a failed visit from the car park down the road. The "
                "evidence is geotagged, and evidence from the wrong place is "
                "worse than none.",
                "Telephoning the customer to agree extra work instead of "
                "raising a revised estimate. Verbal agreement is not "
                "enforceable and not recorded.",
                "Marking cannot-complete without choosing a specific reason. "
                "The weekly failure analysis is only as good as the reasons in "
                "it.",
                "Taking a device away without converting to a collection. "
                "Custody is a legal chain and it starts the moment the device "
                "leaves the customer.",
            ],
        },
        {
            "title": "Parts and money in the van",
            "who": [
                (
                    "Mostly used by",
                    "Technicians, and the inventory and finance " "teams",
                ),
                ("Also relied on by", "Branch managers, who close the shift"),
                ("Where it happens", "The van, and the end-of-shift " "reconciliation"),
            ],
            "intro": [
                "Five functions that close two long-standing gaps. The first "
                "is van stock, which is currently untracked between "
                "replenishments — nobody knows with confidence what is on any "
                "given van at any given moment. The second is field cash, "
                "which is reconciled on trust.",
                "Both are fixed the same way: record it where it happens. A "
                "part is scanned as it is fitted, not written down for later. "
                "Cash is recorded at the door, and the technician's next shift "
                "will not start until the previous one is reconciled.",
            ],
            "features": [
                [
                    "Van par levels",
                    "Uses the per-technician stock levels set in M15 from their "
                    "skill profile and job mix.",
                    "A printer specialist's van carries different things from a "
                    "laptop technician's.",
                ],
                [
                    "Van stock in assignment",
                    "Considers what is actually on the van when scoring "
                    "candidates for a job.",
                    "The technician who can finish the job today outranks the one "
                    "who is slightly nearer.",
                ],
                [
                    "Field parts transfer",
                    "Transfers a part directly between two technicians in the "
                    "field, scanned by both.",
                    "A part twenty minutes away is better than a part at the " "depot.",
                ],
                [
                    "Field cash reconciliation",
                    "Reconciles cash collected daily against jobs and deposits.",
                    "Variance becomes a number rather than an impression.",
                ],
                [
                    "Vehicle assignment",
                    "Records which vehicle a technician is using and reports "
                    "usage to M46.",
                    "Fuel and servicing costs attach to the right vehicle.",
                ],
            ],
            "example": (
                "the part that came from another van",
                "A technician in Bashundhara opens a laptop and finds a failed "
                "keyboard ribbon he does not carry. Rather than abandoning the "
                "visit, the app shows that a colleague working two kilometres "
                "away has one on his van. A field transfer is raised; the two "
                "meet, both scan the part, and the ledger moves it from one "
                "van to the other. The job completes the same morning. The "
                "alternative — a cannot-complete, a second appointment, a trip "
                "to the depot — would have cost two job slots and a "
                "disappointed customer, and would have shown up in the "
                "first-time-fix figure for both of them.",
            ),
            "mistakes": [
                "Fitting a part and scanning it later. Consumption recorded "
                "after the fact is consumption nobody can rely on.",
                "Carrying stock above the configured maximum because it feels "
                "safer. The system will refuse, and the reason is that "
                "unrecorded stock in vans is how inventory accuracy dies.",
                "Depositing field cash without recording it against the jobs. "
                "The reconciliation is per technician per shift for a reason.",
                "Swapping parts between vans informally. If both people do not "
                "scan, the ledger is now wrong in two places.",
            ],
            "caution": "A technician's next shift is blocked until the previous "
            "shift's cash is reconciled. That is deliberate and it is not "
            "a branch-level discretion. Build the five minutes into the "
            "end of the day rather than discovering it at the start of the "
            "next one.",
        },
    ],
    # ============================================ 7. the journey
    "s6_title": "The journey of a field visit",
    "s6_lede": "Thirteen states from 'somebody should go' to 'the record is closed', "
    "and the three that need a human being.",
    "s6_intro": [
        "A work order has its own life, separate from the service order it "
        "serves. It is created when M01 says there is field work to do, and it "
        "is closed when everything the technician recorded has synchronised "
        "and reconciled. In between it passes through the states below.",
        "Two of the transitions are worth noticing because they happen without "
        "anybody doing anything. Arrival is normally recorded by crossing the "
        "customer geofence, not by tapping a button. And closure happens when "
        "the phone's queued work reaches the server and the parts, time and "
        "evidence all reconcile — which for an offline day may be hours after "
        "the technician actually finished.",
    ],
    "journey": [
        ("Created", "System, from M01", None),
        ("Proposed", "Scoring or dispatcher", None),
        ("Assigned", "System", "gate"),
        ("Accepted", "Technician", "gate"),
        ("En route", "Technician", None),
        ("On site", "Geofence", None),
        ("In progress", "Technician", None),
        ("Paused", "Technician", None),
        ("Customer sign", "Technician", "gate"),
        ("Completed", "Technician + customer", None),
        ("Closed", "System, on sync", None),
        ("Customer absent", "Technician", "evidence"),
        ("Cannot complete", "Technician", "reason"),
    ],
    "journey_title": "The path a work order follows",
    "journey_sub": (
        "Eleven states in the normal path, and two ways out when " "the visit fails"
    ),
    "journey_caption": "The work order lifecycle, in the order it happens",
    "s6_stages": [
        [
            "Created",
            "M01 has said there is field work to do.",
            "System",
            "A service order exists and is ready for dispatch.",
        ],
        [
            "Proposed",
            "A candidate has been identified but not committed.",
            "Scoring engine or dispatcher",
            "The candidate scored above threshold, or the dispatcher chose.",
        ],
        [
            "Assigned",
            "A named technician now owns the job.",
            "System",
            "Certification valid, technician available, no schedule conflict.",
        ],
        [
            "Accepted",
            "The technician has confirmed they will do it.",
            "Technician",
            "Their confirmation. A decline returns the job to the pool.",
        ],
        [
            "En route",
            "They are travelling to the site.",
            "Technician",
            "Departure recorded and location active.",
        ],
        [
            "On site",
            "They have arrived.",
            "Geofence, or manual with a reason",
            "Crossing the customer geofence. Manual arrival needs an exception "
            "reason.",
        ],
        ["In progress", "The work is happening.", "Technician", "Work start recorded."],
        [
            "Paused",
            "Work has stopped for a recorded reason.",
            "Technician",
            "An approved pause reason.",
        ],
        [
            "Customer sign",
            "The work is done and awaiting signature.",
            "Technician",
            "Diagnostic, parts, evidence and checklist all complete.",
        ],
        [
            "Completed",
            "The customer has signed, or refused with evidence.",
            "Technician and customer",
            "A captured signature, or documented refusal with alternative " "evidence.",
        ],
        [
            "Closed",
            "Everything has reached the server and reconciled.",
            "System",
            "Synchronised; parts, time and evidence all reconciled.",
        ],
        [
            "Customer absent",
            "Nobody was there.",
            "Technician",
            "Geotagged evidence. This is a hard requirement.",
        ],
        [
            "Cannot complete",
            "The job could not be finished on site.",
            "Technician",
            "A recorded reason, and a follow-up or transfer created.",
        ],
    ],
    "s6_gates_intro": "Three points in the path will stop a job dead until a condition is "
    "met, and two more require evidence rather than permission. They are "
    "the reason a work order cannot be quietly closed without the work "
    "having demonstrably happened.",
    "gates": [
        (
            "Certification valid",
            "Brand warranty work cannot be assigned to a technician whose "
            "certification has lapsed. On expiry they leave the pool "
            "automatically",
            "System",
        ),
        (
            "Technician available",
            "Somebody on leave, off shift or at capacity is never offered as a "
            "candidate",
            "System, from M55",
        ),
        (
            "Technician accepted",
            "A job is not truly assigned until the technician has confirmed. A "
            "decline with a reason returns it to the pool",
            "Technician",
        ),
        (
            "Arrival evidenced",
            "On-site status comes from crossing the geofence. Marking on-site "
            "from outside it requires a recorded exception reason",
            "Geofence",
        ),
        (
            "Work evidenced before signature",
            "Diagnostic, parts, evidence and checklist must all be complete "
            "before the signature screen opens",
            "Technician",
        ),
        (
            "Failed visit evidenced",
            "A failed visit cannot be recorded at all without geotagged proof",
            "Technician",
        ),
        (
            "Cash reconciled",
            "The next shift cannot start until the last shift's field cash is "
            "reconciled against jobs and deposits",
            "Technician",
        ),
    ],
    "s6_wrong_intro": "Field jobs fail in a small number of predictable ways, and most of "
    "them are visible on the board before the customer notices. This is "
    "the distilled version of what the dispatch map will show you.",
    "s6_wrong": [
        [
            "Proposed",
            "Nobody scores above the threshold — usually a certification or a "
            "zone gap rather than a shortage of people.",
            "The job sits in the dispatcher's queue with a thin candidate list.",
            "Look at why the list is thin. A recurring gap is a rostering or "
            "training problem, not a dispatch problem.",
        ],
        [
            "Assigned",
            "The technician does not respond.",
            "The job stays assigned but not accepted, and the idle alert fires.",
            "Reassign. If it happens repeatedly with one person, it is a "
            "conversation rather than a system fault.",
        ],
        [
            "En route",
            "Traffic makes the arrival estimate meaningless.",
            "The estimate moves repeatedly and the customer gets several " "updates.",
            "Nothing, usually. Repeated material changes on the same route are "
            "worth feeding back to the travel-time model.",
        ],
        [
            "On site",
            "The job is bigger than the estimate.",
            "It sits in progress far past its planned duration.",
            "Raise a revised estimate on site. Do not proceed on a verbal "
            "agreement.",
        ],
        [
            "In progress",
            "The required part is not on the van.",
            "A cannot-complete, or a long pause.",
            "Check for a field transfer before abandoning the visit. Two "
            "kilometres beats a second appointment.",
        ],
        [
            "Customer sign",
            "The customer refuses to sign.",
            "The job cannot reach completed.",
            "Record the refusal with alternative evidence. Do not sign on their "
            "behalf under any circumstances.",
        ],
        [
            "Completed but not closed",
            "The phone has not synchronised.",
            "Jobs completed hours ago still showing open, and after 26 hours an "
            "alert.",
            "Usually coverage. If a device has not synced for over a day, treat "
            "it as a possible lost phone.",
        ],
        [
            "Customer absent",
            "Recorded without evidence, or with evidence from the wrong place.",
            "The system will have refused, so in practice this means a visit that "
            "was never recorded at all.",
            "Investigate. An unrecorded journey is a cost nobody can see.",
        ],
    ],
    "s6_note": "A work order can end in three places: closed, customer absent or "
    "cannot complete. Only the first is a finished job, and the other two "
    "both create something else — a reschedule, a follow-up, or a "
    "collection. Nothing is ever simply abandoned.",
    # ============================================ 8. day in the life
    "s7_lede": "Five walkthroughs from an ordinary week in the field, following one "
    "job each from the board to the signature.",
    "s7_intro": [
        "These follow jobs across everybody who touches them: the dispatcher, "
        "the technician, the customer and the people downstream who never "
        "leave the office. Read the one closest to your own work first.",
        "Customers, places, devices and amounts are illustrative. The "
        "baselines, thresholds and rules behind them are exactly as the "
        "specification states them.",
    ],
    "scenarios": [
        {
            "title": "A routine on-site repair",
            "narrative": [
                "The ordinary case, and the one the productivity target is "
                "built on. A booked job, a planned route, a technician with "
                "the right part on the van, finished and documented before "
                "leaving the customer's premises.",
            ],
            "lanes": [
                (
                    "Customer",
                    [
                        (0, "Books a morning slot at intake"),
                        (2, "Watches the technician approach"),
                        (4, "Signs on screen"),
                    ],
                ),
                ("Route solver", [(1, "Places the job third in the route")]),
                (
                    "Technician",
                    [
                        (2, "Departs; navigation launches"),
                        (3, "Diagnoses, scans the part, photographs"),
                        (4, "Takes the signature"),
                    ],
                ),
                ("Dispatcher", [(1, "Accepts the recommendation in one click")]),
                (
                    "System",
                    [
                        (0, "Scores candidates"),
                        (2, "Publishes the arrival estimate"),
                        (4, "Reports completion to M01"),
                    ],
                ),
            ],
            "columns": ["Booked", "Assigned", "Travelling", "On site", "Finished"],
            "exhibit_title": "A routine on-site repair, board to signature",
            "exhibit_sub": "Five steps, and the customer watching three of them",
            "caption": "The ordinary field job, end to end",
            "table": [
                [
                    "1",
                    "Intake and system",
                    "The service order is created at the counter with an on-site "
                    "delivery mode and a morning slot. M01 hands it to M02 as "
                    "field work; candidates are scored immediately.",
                ],
                [
                    "2",
                    "Dispatcher and route solver",
                    "The recommendation is clear — right skill, right zone, part "
                    "on the van — and is accepted in one click. The overnight "
                    "solve places it third in that technician's route.",
                ],
                [
                    "3",
                    "Technician",
                    "Accepts the job, departs at 09:12, navigation launches. The "
                    "customer's arrival estimate publishes automatically.",
                ],
                [
                    "4",
                    "Geofence and technician",
                    "Arrival recorded on crossing the boundary. Diagnosis run on "
                    "the phone, part scanned off the van, before and after "
                    "photographs captured.",
                ],
                [
                    "5",
                    "Customer and system",
                    "Signature captured on screen. Completion reported to M01, "
                    "which raises the billable event; van stock drops below par "
                    "and replenishment raises itself.",
                ],
            ],
            "outcome": "Documented in under five minutes on site rather than fifteen "
            "to twenty plus an evening write-up. The customer watched the "
            "technician approach and telephoned nobody. Inventory, finance "
            "and the service order all learned what happened without a "
            "single form being typed.",
        },
        {
            "title": "An emergency that reshaped the afternoon",
            "narrative": [
                "A hospital's diagnostic printer fails at 13:20. The contract "
                "promises four working hours. Nothing in the existing schedule "
                "has room, and yet the day absorbs it.",
            ],
            "lanes": [
                ("Customer", [(0, "Logs the emergency at 13:20")]),
                (
                    "System",
                    [
                        (
                            0,
                            "Creates the order; identifies the nearest "
                            "qualified technician",
                        ),
                        (1, "Re-solves that technician's remaining route"),
                        (2, "Notifies both parties; publishes the " "estimate"),
                    ],
                ),
                ("Dispatcher", [(1, "Reviews the displacement and approves")]),
                (
                    "Technician",
                    [
                        (2, "Diverts; arrives 14:05"),
                        (3, "Replaces the fuser; signs off 15:10"),
                    ],
                ),
            ],
            "columns": ["Logged", "Re-planned", "Diverted", "Fixed"],
            "exhibit_title": "An emergency inserted into a full afternoon",
            "exhibit_sub": "The route re-solved itself; the dispatcher approved",
            "caption": "How urgent work is absorbed without wrecking the day",
            "table": [
                [
                    "1",
                    "System",
                    "The emergency is created and typed as such. The nearest "
                    "qualified, available, certified technician is identified in "
                    "seconds.",
                ],
                [
                    "2",
                    "System and dispatcher",
                    "That technician's remaining route re-solves. Two "
                    "lower-priority jobs move to tomorrow; a third, already close "
                    "to its own promise, is explicitly protected and does not "
                    "move. The dispatcher reviews the displacement and approves.",
                ],
                [
                    "3",
                    "Technician and customer",
                    "The technician is notified and diverts. The customer "
                    "receives a link with an arrival estimate of 14:05.",
                ],
                [
                    "4",
                    "Technician",
                    "Arrives, replaces the fuser from van stock, captures "
                    "evidence and signs off at 15:10 — inside the four-hour "
                    "contract promise.",
                ],
                [
                    "5",
                    "Customers of the displaced jobs",
                    "Both are notified automatically of the new date, with a "
                    "revised commitment, that afternoon.",
                ],
            ],
            "outcome": "The promise was kept, two customers were told about their "
            "changed appointments before they noticed, and the job that "
            "was already at risk was never even offered as a candidate for "
            "displacement. The dispatcher made one decision instead of "
            "twenty telephone calls.",
        },
        {
            "title": "A full day with no signal",
            "narrative": [
                "Four jobs in a sub-district with no usable mobile data. "
                "Everything the technician does queues on the phone, and the "
                "whole day reaches the system on the drive home.",
            ],
            "lanes": [
                (
                    "Technician",
                    [
                        (0, "Downloads the route before leaving"),
                        (1, "Works four jobs offline"),
                        (2, "Signal returns on the road home"),
                    ],
                ),
                (
                    "Phone",
                    [
                        (1, "Queues 4 jobs, 11 photos, 3 parts, 2 payments"),
                        (2, "Synchronises in under 30 seconds"),
                    ],
                ),
                (
                    "System",
                    [
                        (2, "Reconciles parts, time and evidence"),
                        (3, "Releases the invoice triggers"),
                    ],
                ),
                ("Inventory", [(3, "Sees the van below par; raises " "replenishment")]),
                ("Finance", [(3, "Sees cash for shift-end reconciliation")]),
            ],
            "columns": ["Prepared", "Offline day", "Reconnected", "Settled"],
            "exhibit_title": "Twenty-four hours offline, then thirty seconds",
            "exhibit_sub": "Nothing lost, nothing duplicated",
            "caption": "How the application behaves with no coverage",
            "table": [
                [
                    "1",
                    "Technician and phone",
                    "The route, four job records, the diagnostic trees, the "
                    "manuals and the wiring diagrams are all on the device before "
                    "leaving branch coverage.",
                ],
                [
                    "2",
                    "Technician",
                    "Four jobs worked. Arrivals recorded from the device's own "
                    "location against the stored geofences. Parts scanned, "
                    "photographs taken and validated for quality at the point of "
                    "capture, signatures collected, two cash payments recorded "
                    "with printed receipts.",
                ],
                [
                    "3",
                    "Phone",
                    "Everything queues locally: four completions, eleven "
                    "photographs, three parts consumed, two payments and around "
                    "forty timestamps.",
                ],
                [
                    "4",
                    "System",
                    "Signal returns on the road home. The queue synchronises in "
                    "under thirty seconds. Parts, time and evidence reconcile "
                    "against the server; nothing conflicts.",
                ],
                [
                    "5",
                    "Inventory and finance",
                    "Van stock drops below par and a replenishment request "
                    "reaches the branch store. Field cash appears in the "
                    "shift-end reconciliation.",
                ],
            ],
            "outcome": "A working day in a place with no coverage is an ordinary "
            "working day. The specification's target for offline sync "
            "failures is zero, and this is what zero has to look like in "
            "practice: the technician never thought about it.",
        },
        {
            "title": "A visit that failed, handled properly",
            "narrative": [
                "The technician arrives and the customer is not there. What "
                "happens next decides whether this becomes a statistic or a "
                "dispute.",
            ],
            "lanes": [
                (
                    "Technician",
                    [
                        (0, "Arrives; nobody answers"),
                        (1, "Photographs the door with time and " "location"),
                    ],
                ),
                (
                    "System",
                    [
                        (1, "Records the failed visit; notifies the " "customer"),
                        (2, "Triggers rescheduling per policy"),
                        (3, "Adds the cause to the weekly analysis"),
                    ],
                ),
                ("Customer", [(2, "Reschedules from the tracking link")]),
                ("Quality manager", [(3, "Sees the cause cluster by zone")]),
            ],
            "columns": ["Arrived", "Evidenced", "Rebooked", "Analysed"],
            "exhibit_title": "A failed visit that produced something useful",
            "exhibit_sub": "Evidence first, then a reschedule, then a cause",
            "caption": "How a wasted journey is recorded and learned from",
            "table": [
                [
                    "1",
                    "Technician",
                    "Arrives inside the published window. The geofence records "
                    "the arrival. Nobody answers; he waits the policy period.",
                ],
                [
                    "2",
                    "Technician",
                    "Photographs the entrance with time and location attached. "
                    "Without that evidence the system will not let the failed "
                    "visit be recorded at all.",
                ],
                [
                    "3",
                    "System and customer",
                    "The failure is recorded, the customer is notified "
                    "immediately, and the policy on charging for a wasted journey "
                    "is applied. The customer reschedules from the tracking "
                    "link.",
                ],
                [
                    "4",
                    "System",
                    "The cause is added to the failed-visit analysis alongside "
                    "the zone and the technician.",
                ],
                [
                    "5",
                    "Quality manager",
                    "The weekly review shows a cluster of absent customers in one "
                    "zone for morning slots — which turns out to be a booking "
                    "practice, not a customer problem.",
                ],
            ],
            "outcome": "The complaint that never came: 'the technician never turned "
            "up' is answered by a geotagged photograph. And a pattern that "
            "would previously have been invisible — morning bookings "
            "failing in one zone — became a fixable process problem in a "
            "single week's data.",
        },
        {
            "title": "A shift that closed clean",
            "narrative": [
                "The least dramatic walkthrough and the one finance cares "
                "about most. Six jobs, four cash collections, three parts and "
                "a reconciliation that took four minutes.",
            ],
            "lanes": [
                (
                    "Technician",
                    [
                        (0, "Completes six jobs across the day"),
                        (2, "Reconciles cash at shift end"),
                    ],
                ),
                (
                    "System",
                    [
                        (1, "Totals collections against jobs"),
                        (2, "Compares against the deposit"),
                        (3, "Releases the next shift"),
                    ],
                ),
                (
                    "Inventory",
                    [(1, "Sees three parts consumed; raises " "replenishment")],
                ),
                ("Finance", [(3, "Sees zero variance for that technician")]),
            ],
            "columns": ["Working day", "Totalled", "Reconciled", "Closed"],
            "exhibit_title": "Closing a shift in four minutes",
            "exhibit_sub": "Parts and cash settled where they were used",
            "caption": "The end-of-shift reconciliation",
            "table": [
                [
                    "1",
                    "Technician",
                    "Six jobs completed. Four customers paid at the door — two in "
                    "cash, one by mobile money, one by card. Three parts scanned "
                    "off the van as they were fitted.",
                ],
                [
                    "2",
                    "System",
                    "Collections are totalled against the jobs they belong to. "
                    "Van stock is compared with par levels and a replenishment "
                    "request goes to the branch store.",
                ],
                [
                    "3",
                    "Technician",
                    "At shift end the app prompts for reconciliation. The cash "
                    "total is confirmed against the deposit slip. Four minutes.",
                ],
                [
                    "4",
                    "System",
                    "Reconciliation complete, so the next shift is released. Had "
                    "it not been, the technician would not have been able to "
                    "start tomorrow.",
                ],
                [
                    "5",
                    "Finance",
                    "Zero variance recorded for that technician, that day, "
                    "against the jobs that generated it.",
                ],
            ],
            "outcome": "Field cash variance goes from untracked to under 0.3 per "
            "cent, and van variance from a black hole to under one per "
            "cent. Neither is achieved by supervision; both are achieved "
            "by recording things where and when they happen.",
        },
    ],
    "s9t_lede": "Five different days, and the same five habits underneath all of them.",
    "s9t_intro": [
        "The walkthroughs deliberately covered a routine job, an emergency, a "
        "day with no coverage, a failure and an ordinary shift close. Read "
        "together they show what actually changes in the field, which is less "
        "about software than about where and when information gets recorded.",
        "In none of them did anybody have to remember to do something at the "
        "end of the day. That is the thread. Every piece of information was "
        "captured at the moment and in the place it existed, which is the only "
        "way it survives contact with a working day.",
    ],
    "s9t_table": [
        [
            "Record it where it happens",
            "Every walkthrough: parts scanned at the van, arrival from the "
            "geofence, signature at the door, cash at the point of payment.",
            "Information recorded later is information recorded worse, and "
            "usually less.",
        ],
        [
            "Let the system absorb the disruption",
            "The emergency and the failed visit: routes re-solved, follow-ups "
            "created, customers notified, all without a decision.",
            "A dispatcher's judgement is worth more on the exceptions than on the "
            "arithmetic.",
        ],
        [
            "Evidence protects the technician first",
            "The failed visit and the offline day: geotagged proof, validated "
            "photographs, timestamped arrivals.",
            "Almost every field dispute is about whether somebody was there and "
            "what they found.",
        ],
        [
            "Offline is normal, not exceptional",
            "The whole third walkthrough, and parts of every other one.",
            "A system that only works with a signal is a system that does not "
            "work in Bangladesh.",
        ],
        [
            "Close the day, every day",
            "The shift-close walkthrough, and the replenishment in three others.",
            "Small daily reconciliations replace large monthly arguments.",
        ],
    ],
    "s9t_close": "Everything the module promises — nine jobs a day instead of five, "
    "88 per cent first-time fix, van variance under one per cent — depends "
    "on a technician being willing to use the application while standing "
    "at somebody's door. That is the whole programme's biggest single "
    "dependency, and it is worth remembering every time somebody proposes "
    "adding another field to a screen.",
    # ============================================ 10. rules
    "s8_lede": "Fourteen rules. Most of them protect either the customer's claim or "
    "the technician's safety, and none of them can be argued with in the "
    "moment.",
    "s8_intro": [
        "Field work happens away from supervision, which means the rules have "
        "to be in the software rather than in a manager's line of sight. Where "
        "a rule below is a hard block, the application simply will not proceed.",
        "Two of them are unusual and worth flagging. Location capture stops "
        "outside working hours — that is a privacy rule enforced against the "
        "company, not against the technician. And field cash must be "
        "reconciled before the next shift starts, which is the only rule in "
        "this book that stops somebody working.",
    ],
    "s8_rules": [
        [
            "Be offered a job while on leave, off shift or at capacity",
            "Dispatch cannot be allowed to solve its problem by ignoring the "
            "roster.",
            "Nothing. Availability comes from M55 and the candidate list already "
            "reflects it.",
        ],
        [
            "Be assigned work you do not have the skill for",
            "A skill mismatch shows up as a failed visit or a second attempt, and "
            "the customer pays for it in time.",
            "If the skill match looks wrong, the competency record in M22 is the "
            "thing to fix.",
        ],
        [
            "Have a job auto-assigned on a marginal score",
            "Automation is only worth having when it is right more often than a "
            "dispatcher would be.",
            "Nothing. Below the confidence threshold it comes to you as a ranked "
            "list.",
        ],
        [
            "Override a recommendation without a reason",
            "The reasons are the training signal that lifts auto-assignment from "
            "nothing to seventy per cent.",
            "Choose the code that actually fits. If none does, that is worth "
            "reporting.",
        ],
        [
            "Be tracked outside working hours or during a break",
            "Location is a working-time tool. Capture stops automatically and the "
            "technician can see when it is active.",
            "Nothing. This one protects you.",
        ],
        [
            "Mark yourself on site from outside the customer geofence",
            "Arrival time drives the promise, the customer's expectation and any "
            "later dispute.",
            "If the geofence is genuinely wrong, record the exception reason and "
            "report the boundary.",
        ],
        [
            "Start your next shift with last shift's cash unreconciled",
            "Cash reconciled monthly is cash nobody can trace.",
            "Reconcile at the end of the shift. It takes about four minutes.",
        ],
        [
            "Carry more of an item than the configured maximum",
            "Unrecorded stock in vans is how inventory accuracy dies.",
            "If a par level is wrong for your job mix, raise it with inventory — "
            "they own the level.",
        ],
        [
            "Record a failed visit without geotagged evidence",
            "'The technician never came' is a common complaint and evidence is "
            "the only answer.",
            "Photograph the door, with the location on. It takes ten seconds and "
            "it is entirely in your interest.",
        ],
        [
            "Be scheduled past working-time limits without approved overtime",
            "Both the law and fatigue-related error are real risks.",
            "Get the overtime approved first. The board will then allow it.",
        ],
        [
            "Displace an at-risk job with an emergency",
            "An emergency that creates another breach has not solved anything.",
            "Nothing. The board will not offer that option.",
        ],
        [
            "Offer work to a marketplace seller who does not qualify",
            "An outside engineer represents 1000FiX to the customer.",
            "Score, certification and category access all have to pass. They are "
            "checked automatically.",
        ],
        [
            "Assign brand warranty work to an expired certification",
            "The brand voids the claim and the company absorbs the repair.",
            "Nothing to do — the technician leaves that pool automatically on "
            "expiry. Renewal is an M22 matter.",
        ],
        [
            "Look at somebody's location history unlogged",
            "It is personal data about a person's movements.",
            "Four named roles have access and every access is recorded. If you "
            "need it and cannot see it, the question is which role you hold.",
        ],
    ],
    "s8_note": "The cash reconciliation rule is the one that generates most "
    "resistance in the first month and least in the third. It stops the "
    "next shift, deliberately, because a soft version of this rule is the "
    "same as no rule.",
    # ============================================ 11. automation
    "s9_lede": "Thirteen behaviours that run without anybody asking, and one of them "
    "may one day matter more than everything else in this book.",
    "s9_intro": [
        "Most of these are conveniences: a route solved overnight, an arrival "
        "recorded by a geofence, a replenishment request raised when a van "
        "drops below par. They add up to the difference between four jobs a "
        "day and nine.",
        "One is not a convenience. When a panic alert is raised, the "
        "dispatcher, the branch manager and the safety officer are notified "
        "immediately with the technician's location, through every channel at "
        "once. It is the only automation in this module with no failure "
        "behaviour except 'escalate harder', and it is the reason the safety "
        "functions are worth the effort of building.",
    ],
    "automation_groups": [
        (
            "When work arrives or changes",
            4,
            "Candidates scored, emergencies routed, ETAs published and revised",
        ),
        (
            "On a timetable",
            2,
            "The five o'clock route solve, and the shift-end cash prompt",
        ),
        (
            "When the technician moves",
            3,
            "Departure, geofence arrival, and the offline sync reconciliation",
        ),
        (
            "When something is wrong",
            4,
            "Idle alerts, van below par, unsynced devices, and the panic alert",
        ),
    ],
    "s9_table": [
        [
            "Scores candidates and assigns above the threshold, or queues the "
            "ranked list",
            "A service order becomes ready for dispatch",
            "The dispatcher; the technician if assigned",
        ],
        [
            "Optimises every route for the next day, publishes it and notifies "
            "the technicians",
            "Five o'clock every morning",
            "Every technician, before they start",
        ],
        [
            "Finds the nearest qualified technician, re-optimises their route and "
            "notifies both parties",
            "An emergency job is created",
            "The technician, the customer and the dispatcher",
        ],
        [
            "Publishes the arrival estimate and raises the en-route event",
            "The technician records departure",
            "The customer, through M27",
        ],
        [
            "Records arrival, raises the arrival event and starts the on-site " "clock",
            "The technician crosses the customer geofence",
            "The dispatcher and the customer",
        ],
        [
            "Reconciles parts, time and evidence, and releases the invoice " "trigger",
            "A job completed offline reaches the server",
            "Finance, inventory and M01",
        ],
        [
            "Alerts the dispatcher",
            "A technician is idle beyond the threshold during a shift",
            "The dispatcher",
        ],
        [
            "Raises a replenishment request to the branch store",
            "Van stock falls below par after a job",
            "The inventory manager and the branch store",
        ],
        [
            "Publishes a revised arrival estimate",
            "The estimate changes materially",
            "The customer",
        ],
        [
            "Prompts for cash reconciliation and blocks the next shift until it "
            "is done",
            "Shift end",
            "The technician, then the branch manager if it is not done",
        ],
        [
            "Notifies dispatcher, branch manager and safety officer immediately "
            "with the location, through every channel at once",
            "A panic alert is raised",
            "Everybody who can help, simultaneously",
        ],
        [
            "Removes the technician from that brand's warranty dispatch pool",
            "A certification expires",
            "The dispatcher, by the candidate list changing",
        ],
        [
            "Alerts the dispatcher to a possible lost device",
            "A phone has not synchronised for 26 hours",
            "The dispatcher and the branch manager",
        ],
    ],
    # ============================================ 12. permissions
    "s10_lede": "Thirteen roles, and one dividing line that matters more than the "
    "rest: who can see where a person has been.",
    "s10_intro": [
        "Most of the permission structure here is unsurprising — technicians "
        "see their own work, dispatchers see their zones, managers see their "
        "branch. Two areas are handled with particular care.",
        "The first is cost and margin, which technicians cannot see at all. "
        "The second is location history, which four named roles can see and "
        "everybody else cannot, with every single access written to a log. "
        "That log is not decorative; it exists because a system that records "
        "where people go creates an obligation, and the obligation is met by "
        "making the watching visible.",
    ],
    "permissions": {
        "roles": [
            "Operations Director",
            "Dispatch Manager",
            "Branch Manager",
            "Senior Technician",
            "Junior Technician",
            "Specialist Technician",
            "Service Centre Agent",
            "Inventory Manager",
            "Quality Manager",
            "Contact Centre Agent",
            "Customer",
            "Marketplace Seller",
        ],
        "actions": [
            "Assign a job",
            "Override a recommendation",
            "See live positions",
            "See location history",
            "Complete a job",
            "See cost and margin",
        ],
        "marks": [
            ["y", "y", "y", "y", "v", "y"],  # Operations Director
            ["y", "y", "y", "y", "v", ""],  # Dispatch Manager
            ["y", "a", "y", "y", "v", "y"],  # Branch Manager
            ["", "", "", "", "y", ""],  # Senior Technician
            ["", "", "", "", "y", ""],  # Junior Technician
            ["", "", "", "", "y", ""],  # Specialist Technician
            ["", "", "v", "", "", ""],  # Service Centre Agent
            ["", "", "", "", "", ""],  # Inventory Manager
            ["", "", "v", "y", "v", ""],  # Quality Manager
            ["", "", "v", "", "", ""],  # Contact Centre Agent
            ["", "", "v", "", "", ""],  # Customer
            ["", "", "", "", "y", ""],  # Marketplace Seller
        ],
        "sub": "The six actions that decide who can do what in the field",
    },
    "s10_roles": [
        [
            "Operations Director",
            "Field productivity across the estate",
            "Seeing everything, everywhere, including cost and location history",
        ],
        [
            "Dispatch manager",
            "Assigning and rescuing the day's work",
            "Overriding recommendations and reassigning across their zones",
        ],
        [
            "Branch manager",
            "The field activity attached to one branch",
            "Approving overtime and seeing their branch's location history",
        ],
        [
            "Senior technician",
            "Doing the work, including the harder jobs",
            "Nothing exclusive — but the certifications they hold widen the pool "
            "they can be assigned from",
        ],
        [
            "Junior technician",
            "Doing the work within their competency",
            "Nothing exclusive",
        ],
        [
            "Specialist technician",
            "Work that needs a specific certification",
            "Being the only candidate for certain brand warranty jobs",
        ],
        [
            "Service centre agent",
            "Answering for field jobs at their branch",
            "Read-only visibility of their branch's field activity",
        ],
        [
            "Inventory manager",
            "What came off which van",
            "Read-only across van stock consumption",
        ],
        [
            "Quality manager",
            "Failed visits, evidence and field incidents",
            "Reading location history for investigation",
        ],
        [
            "Contact centre agent",
            "Answering 'when will somebody arrive?'",
            "Reading job status and the current estimate",
        ],
        [
            "Customer",
            "Watching their own technician approach",
            "Rescheduling their own appointment from the tracking link",
        ],
        [
            "Marketplace seller",
            "Work awarded to them as overflow",
            "Completing only the orders they hold, only while they hold them",
        ],
    ],
    "s10_restrictions_intro": "Three restrictions are enforced in the software and are not "
    "adjustable locally. Each of them exists because of something that "
    "could otherwise go badly wrong.",
    "s10_restrictions": [
        [
            "Cost and margin",
            "Senior operational and finance roles only. Technicians never see " "them.",
            "A technician's judgement about what a job needs should not be "
            "influenced by what it costs the company.",
        ],
        [
            "Location history",
            "The Operations Director, dispatch managers, branch managers and the "
            "quality manager. Every single access is logged.",
            "Recording where people go creates an obligation. The log is how that "
            "obligation is met.",
        ],
        [
            "Location capture itself",
            "Suspended outside working hours and during recorded breaks. The "
            "technician can see when tracking is active.",
            "It is a working-time tool and it is visibly limited to working " "time.",
        ],
        [
            "Marketplace seller access",
            "Scoped to the awarded work order and time-limited.",
            "An outside engineer should see the job they are doing and nothing "
            "else, for exactly as long as they are doing it.",
        ],
        [
            "Customer visibility",
            "Only their own job's technician position and estimate — not the "
            "technician's other work, and not their route.",
            "The customer is entitled to know when somebody is coming to them, "
            "not where else that person has been.",
        ],
    ],
    "s10_note": "If you can see a technician's location history and your role should "
    "not permit it, report it the same day. That is a privacy fault, not "
    "an inconvenience.",
    # ============================================ 13. measurement
    "s11_lede": "Ten reports and thirteen measures, several of which will produce the "
    "first honest picture of field productivity the company has ever had.",
    "s11_intro": [
        "This is the module where measurement changes the most, because field "
        "work has been essentially unmeasured. Jobs per technician per day is "
        "known only approximately. Utilisation is estimated. Travel share is a "
        "guess. On-time arrival has never been recorded at all.",
        "Expect the first three months of figures to be uncomfortable. They "
        "will not show performance getting worse; they will show measurement "
        "starting. The important discipline is to establish the baseline "
        "honestly before setting local targets against it.",
    ],
    "s11_reports": [
        [
            "Live dispatch map",
            "Where is everybody, what are they doing, and what is at risk",
            "Dispatch, branch and operations managers, continuously",
        ],
        [
            "Daily dispatch summary",
            "What was assigned, completed, failed and reassigned, and how much "
            "was automatic",
            "The dispatch manager, daily",
        ],
        [
            "Technician productivity",
            "Jobs a day, utilisation, travel share, first-time fix and customer "
            "satisfaction",
            "The Operations Director and HR, weekly",
        ],
        [
            "Route efficiency",
            "Planned against actual travel, adherence, and what the optimisation "
            "is actually saving",
            "The Operations Director, weekly",
        ],
        [
            "Failed visit analysis",
            "Why visits fail, by cause, zone and technician",
            "Operations and quality, weekly",
        ],
        [
            "Assignment quality",
            "How often the system assigns on its own, how often it is overridden "
            "and why",
            "Operations and the CTO, monthly",
        ],
        [
            "Capacity against demand",
            "Where the next seven days are short of people or skills",
            "The Operations Director, weekly",
        ],
        [
            "Field cash reconciliation",
            "Collected, deposited and the variance, per technician",
            "The Finance Manager, daily",
        ],
        [
            "App adoption and health",
            "Daily active users, crash-free rate, sync failures and offline "
            "duration",
            "The CTO and Operations Director, weekly",
        ],
        [
            "Safety report",
            "Incidents, panic alerts and lone-worker compliance",
            "The Safety Officer and HR, monthly",
        ],
    ],
    "s11_kpis": [
        [
            "Jobs per technician per day",
            "The headline productivity number for the whole field operation",
            "8 to 9, from 4 to 5 today",
        ],
        [
            "Technician utilisation",
            "How much of a paid day is productive work",
            "82 per cent, from 55 per cent",
        ],
        [
            "Automatic assignment rate",
            "How much of dispatch the system does on its own",
            "70 per cent, from nothing",
        ],
        [
            "Travel as a share of the working day",
            "How much of the day is spent getting there",
            "22 per cent, from about 35 per cent",
        ],
        [
            "On-time arrival within the window",
            "Whether the company keeps the time it gave",
            "92 per cent. Not currently measured at all",
        ],
        [
            "App daily active usage",
            "Whether technicians are actually using it",
            "95 per cent. This is the adoption number to watch above all others",
        ],
        [
            "Offline sync failures",
            "Actions lost or duplicated after working with no signal",
            "Zero. Not low — zero",
        ],
        [
            "First-time fix rate",
            "Jobs finished on the first visit",
            "88 per cent, from 70 per cent",
        ],
        [
            "Dispatcher agreement with the recommendation",
            "How often the dispatcher accepts what the system suggested",
            "90 per cent. It is the leading indicator for auto-assignment",
        ],
        [
            "Job documentation time",
            "How long paperwork takes",
            "Under 5 minutes, from 15 to 20 plus an evening write-up",
        ],
        [
            "Crash-free sessions",
            "Application stability on four hundred varied phones",
            "99.5 per cent",
        ],
        [
            "Field cash variance",
            "The gap between collected and deposited",
            "Under 0.3 per cent, from untracked",
        ],
        [
            "Technician satisfaction with the app",
            "Whether the people who have to use it think it is any good",
            "Above 4.2 out of 5. Treat a fall here as an emergency",
        ],
    ],
    "dials": [
        ("Jobs per technician per day, against a target of 9", "8-9", 0.90),
        ("Technician utilisation", "82%", 0.82),
        ("Jobs assigned without a dispatcher", "70%", 0.70),
        ("Repairs right the first time", "88%", 0.88),
    ],
    "s11_reading_title": "Reading the live dispatch map",
    "s11_reading": [
        "The map is the screen a dispatcher will have open all day. It shows "
        "every technician as a moving marker with their current job and its "
        "state, and every open job as a pin coloured by how close it is to its "
        "promise.",
        "The instinct is to watch the markers. Resist it. The markers tell you "
        "where people are, which is rarely actionable; the pins tell you what "
        "is about to go wrong, which always is. A useful habit is to spend the "
        "morning on the pins and only look at the markers when a pin needs "
        "somebody moved.",
    ],
    "s11_reading_table": [
        [
            "Several red pins in one zone",
            "That zone is short of capacity today, not badly managed.",
            "Look at overflow rules before moving anybody. If it recurs weekly it "
            "is a rostering question.",
        ],
        [
            "A technician stationary for a long time",
            "Usually a bigger job than estimated. Occasionally a problem.",
            "Check the job state before telephoning. Paused with a reason needs "
            "nothing; in progress and silent may need a call.",
        ],
        [
            "Markers criss-crossing the city",
            "The published route is being ignored, or the route was wrong.",
            "Route adherence will tell you which. Persistent deviation in one "
            "area is usually the roads, not the person.",
        ],
        [
            "A high override rate on one dispatcher's shift",
            "Either the model is weak for that zone or that dispatcher knows "
            "something it does not.",
            "Read the override reasons. They are the whole point of collecting "
            "them.",
        ],
        [
            "Failed visits clustering by time of day",
            "A booking practice problem, not a customer problem.",
            "Look at which slots are being offered and to whom before blaming "
            "attendance.",
        ],
        [
            "A device that has not synced today",
            "Coverage, a flat battery, or a lost phone.",
            "Under 26 hours, wait. Over it, treat it as a possible lost device "
            "and act on the alert.",
        ],
    ],
    # ============================================ 14. neighbours
    "s12_lede": "M02 sits between the customer's promise and the physical world. It "
    "reads from ten modules and feeds twelve.",
    "s12_intro": [
        "The dependencies here are unusually operational. M02 cannot function "
        "without knowing who is on shift, who is certified, what is on the "
        "van and what the customer was promised — and four different modules "
        "own those four facts.",
        "In the other direction, M02 is where a great deal of the system's raw "
        "material is generated. Every timestamp, photograph, part consumption "
        "and customer rating that inventory, finance, warranty, quality and "
        "the predictive models depend on originates at somebody's front door.",
    ],
    "s12_upstream": [
        [
            "M01 Service Request",
            "The work that needs doing, and the promise",
            "There is nothing to dispatch",
        ],
        [
            "M55 Workforce",
            "Shifts, leave, holidays and availability",
            "People get dispatched on their days off",
        ],
        [
            "M22 Competency",
            "Who is certified for what, and until when",
            "Warranty work goes to uncertified technicians and claims are voided",
        ],
        [
            "M15 Inventory",
            "Van par levels and the stock ledger",
            "Assignment cannot consider whether the part is on the van",
        ],
        [
            "M33 Party Master",
            "Who the customer is and where they are",
            "Routing has no destinations",
        ],
        [
            "M17 Asset Registry",
            "Which device, and its history",
            "The technician arrives knowing nothing",
        ],
        [
            "M29 Identity",
            "Who the technician is and what they may do",
            "Nobody can log in to the application",
        ],
        [
            "M26 Intelligence",
            "The assignment scoring model",
            "Assignment falls back to manual dispatch",
        ],
        [
            "M46 Fleet",
            "Which vehicles exist and are roadworthy",
            "Vehicle usage cannot be attributed",
        ],
        [
            "M08 Contract",
            "Contract service levels for contracted customers",
            "Contract work is scheduled against the wrong promise",
        ],
    ],
    "s12_downstream": [
        [
            "M01 Service Request",
            "Progress, completion, time and evidence",
            "The customer's record stops reflecting reality",
        ],
        [
            "M15 Inventory",
            "Parts consumed at the point of use",
            "Van stock becomes untrackable again",
        ],
        [
            "M20 Receivables",
            "The trigger to invoice, and field payments taken",
            "Cash collection at the door cannot be reconciled",
        ],
        [
            "M03 Logistics",
            "Collection requests from failed on-site repairs",
            "A device that must come back has no custody chain",
        ],
        [
            "M31 Workshop",
            "Transfers where site repair is not possible",
            "Work stalls at the customer's premises",
        ],
        [
            "M09 Warranty",
            "Field evidence for claims",
            "Site-repair claims lose their proof",
        ],
        [
            "M23 Quality",
            "Failed visits, evidence quality, first-time fix",
            "Field quality becomes invisible",
        ],
        [
            "M57 Incentives",
            "Objective performance measurements",
            "Performance-linked pay has no defensible basis",
        ],
        [
            "M27 Contact Centre",
            "Live status and arrival estimates",
            "Agents cannot answer the commonest field question",
        ],
        [
            "M25 Customer Portal",
            "The tracking page and the map",
            "The most visible customer-facing feature disappears",
        ],
        [
            "M59 Health and Safety",
            "Field incidents and panic alerts",
            "The duty-of-care mechanism has no destination",
        ],
        [
            "M26 Intelligence",
            "Every field action, as training data",
            "Auto-assignment never rises above its starting point",
        ],
    ],
    "s12_close_up": [
        {
            "title": "The relationship that defines the module: M02 and M01",
            "text": [
                "M01 owns what the customer asked for and what they were "
                "promised. M02 owns the instruction to a specific person to do "
                "a specific piece of it. Everything about the boundary follows "
                "from that one distinction.",
                "In practice it means the customer sees one job while the "
                "field may see three. A repair that needs a first visit, a "
                "part order and a second visit is one service order and three "
                "work orders. The customer's tracking page, the SLA clock and "
                "the invoice all attach to the service order; the routing, the "
                "assignment and the evidence all attach to the work orders.",
                "It also means M02 never stops the clock. A technician can "
                "pause a work order, but only M01 can put the customer's "
                "promise on hold, and only for an approved reason. That "
                "separation stops the field quietly protecting its own numbers "
                "at the customer's expense.",
            ],
        },
        {
            "title": "The relationship people underestimate: M02 and M55 " "Workforce",
            "text": [
                "Dispatch feels like it should own the roster, and it "
                "deliberately does not. Shifts, leave, holidays and "
                "availability windows belong to M55, because workforce "
                "planning runs on a different cadence from dispatch — weeks "
                "and months rather than hours — and because it is an HR "
                "discipline with obligations dispatch should not be arbitrating.",
                "What M02 does is consume availability, absolutely. A "
                "technician who is on leave is not a low-scoring candidate; "
                "they are not a candidate at all. A dispatcher cannot assign "
                "around it, and the board offers no override, because the "
                "moment it did the roster would stop meaning anything.",
                "The friction this creates is real and it is the right "
                "friction. When dispatch cannot cover a day, the answer is a "
                "rostering change or approved overtime, both of which are "
                "visible decisions with a cost attached — rather than an "
                "invisible one made under pressure at eight in the morning.",
            ],
        },
    ],
    "s12_note": "Twelve modules take something from M02 that they cannot get anywhere "
    "else, because it is the only module that observes the physical world. "
    "Nothing else in the system knows what a device actually looked like "
    "when somebody arrived to fix it.",
    # ============================================ 15. troubleshooting
    "s13_lede": "What goes wrong in the field, what it usually means, and what to do "
    "about it.",
    "s13_intro": [
        "Field problems divide into three kinds: the system refusing something "
        "for a good reason, coverage, and a genuine fault. The first two "
        "account for almost everything. The third is rare and matters "
        "enormously, particularly anything involving offline synchronisation.",
    ],
    "s13_troubleshooting": [
        [
            "I cannot assign this job to the technician I want",
            "They are unavailable, uncertified for this brand, or already at "
            "capacity.",
            "The candidate list shows why. If the underlying record is wrong, fix "
            "it in M55 or M22 — not on the board.",
        ],
        [
            "The app will not let me mark myself on site",
            "You are outside the customer geofence.",
            "If you are genuinely at the right address, record the exception "
            "reason and report the boundary. It may be plotted wrongly.",
        ],
        [
            "My phone has not synchronised for hours",
            "Almost always coverage.",
            "Keep working — everything queues. If it is still unsynced after a "
            "day, an alert has already reached your dispatcher.",
        ],
        [
            "A job I completed offline looks wrong now",
            "A conflict was resolved in the server's favour during " "synchronisation.",
            "The reconciliation log in the app shows what changed. If it "
            "reconciled incorrectly, report it immediately — that is a real "
            "fault.",
        ],
        [
            "The route sends me past a job and back again",
            "Usually SLA-aware sequencing protecting a job close to its promise.",
            "Follow it. If it happens repeatedly on the same pair of addresses, "
            "the travel-time data may be wrong; report it.",
        ],
        [
            "The customer says nobody told them we were coming",
            "The en-route event fires on departure. If they had no message, the "
            "contact details are probably out of date.",
            "Check the notification history on the job and correct the details in "
            "M33.",
        ],
        [
            "I cannot record this failed visit",
            "There is no geotagged evidence attached.",
            "Photograph the entrance with location enabled. The rule is absolute "
            "and it protects you more than anyone.",
        ],
        [
            "My shift will not close",
            "Field cash has not been reconciled.",
            "Reconcile it. Your next shift will not start until it is done, and "
            "that is not something a branch manager can waive.",
        ],
        [
            "The part I need is not on my van",
            "Par levels are set from your skill profile and typical job mix, and "
            "this job was unusual.",
            "Check for a field transfer from a nearby colleague before recording "
            "cannot-complete.",
        ],
        [
            "Auto-assignment has stopped suggesting anybody",
            "Either the confidence threshold is set high, or the available pool "
            "genuinely has no good match.",
            "Look at the ranked list. If the top candidate is obviously right and "
            "scored low, that is worth an override with a reason.",
        ],
        [
            "The battery does not last the shift",
            "The app manages location and sync frequency to prevent this.",
            "If it is genuinely failing, report it as an app health issue — do "
            "not turn off location as a workaround.",
        ],
        [
            "A customer wants to reschedule while I am on my way",
            "They can, from the tracking link, within policy.",
            "Point them at the link. A reschedule they make themselves is "
            "recorded properly; one you agree verbally is not.",
        ],
    ],
    "s13_faq": [
        [
            "Can I choose my own order of jobs?",
            "You can, and route adherence will record the deviation. The "
            "sequence balances travel against promises, so departing from it "
            "occasionally is fine and doing so daily will show up.",
        ],
        [
            "What happens if I decline a job?",
            "It returns to the pool with your reason attached and is reassigned. "
            "Declining is a normal action, not a black mark; declining without a "
            "reason is what causes problems.",
        ],
        [
            "Does the customer see where I am when I am not on their job?",
            "No. They see your position and estimate only on the day of their own "
            "service, and never your other work or your route.",
        ],
        [
            "Can the office see where I am at the weekend?",
            "No. Location capture is suspended outside working hours and during "
            "recorded breaks, and you can see when tracking is active.",
        ],
        [
            "What if the customer refuses to sign?",
            "Record the refusal and capture alternative evidence. Never sign on "
            "their behalf, under any circumstances.",
        ],
        [
            "How long can I work offline?",
            "Twenty-four hours, with everything queued. Beyond twenty-six hours "
            "without synchronising, your dispatcher is alerted in case the device "
            "has been lost.",
        ],
        [
            "Who decides whether an emergency displaces my other jobs?",
            "The system, by rule. It may displace lower-priority work but never a "
            "job already at risk of breaching. The dispatcher approves the result "
            "rather than choosing it.",
        ],
        [
            "Why does the app reject some of my photographs?",
            "Blurred, dark or duplicate evidence is rejected at the moment of "
            "capture rather than being discovered as useless when a claim is "
            "submitted two months later.",
        ],
        [
            "Does the app use a lot of my mobile data?",
            "It is designed not to. Uploads are compressed and non-critical ones "
            "are deferred until the phone finds a better connection.",
        ],
        [
            "Can I see my own performance figures?",
            "Yes — your personal scorecard shows your jobs, ratings, first-time "
            "fix rate and earned incentive. Nobody else's.",
        ],
    ],
    # ============================================ 16. worth
    "s14_lede": "The largest single operational benefit in the whole programme sits in "
    "this module, and it depends entirely on people being willing to use a "
    "phone application.",
    "s14_intro": [
        "Moving from four or five jobs a technician per day to eight or nine "
        "is worth roughly BDT 130 lac a year on its own — more than any other "
        "single change the programme proposes. It comes from three sources at "
        "once: less travel, fewer second visits, and the elimination of an "
        "hour of evening paperwork.",
        "It is also the most fragile benefit in the programme, because it "
        "cannot be achieved by management action. A dispatcher can be told to "
        "use the board. A technician standing at somebody's door with a phone "
        "in the rain cannot usefully be told anything. The application has to "
        "be good enough that using it is easier than not.",
    ],
    "benefits": [
        ("Technician productivity", 130, "BDT 130 lac/yr"),
        ("Warranty evidence protected", 100, "protects BDT 100 lac/yr"),
    ],
    "benefits_note": (
        "Travel, first-time fix and inventory gains are real but "
        "are expressed as rates rather than annual values."
    ),
    "s14_benefits": [
        [
            "Technician productivity",
            "Optimised routing, van-stock-aware assignment, no travel to depot to "
            "write up, and no evening paperwork",
            "4-5 to 8-9 jobs a day. BDT 130 lac a year — the largest single "
            "operational benefit in the programme",
        ],
        [
            "Travel cost reduction",
            "Route optimisation and zone discipline",
            "Travel falls from about 35 per cent of the working day to 22 per "
            "cent, and fuel and vehicle cost with it",
        ],
        [
            "First-time fix improvement",
            "Skill matching, the right part on the van at the moment of "
            "assignment, and the device's history in the technician's hand",
            "70 per cent to 88 per cent. Every avoided second visit is a whole "
            "job slot recovered",
        ],
        [
            "Faster cash conversion",
            "Payment taken at the customer's door and the invoice triggered "
            "immediately",
            "Contributes to bringing debtor days below 32",
        ],
        [
            "Inventory accuracy",
            "Consumption recorded at the point of use, reconciled daily",
            "Van variance from untracked to under one per cent",
        ],
        [
            "Warranty evidence",
            "Photographs, location, timestamps and signature captured "
            "automatically as the work happens",
            "Protects the BDT 100 lac a year of warranty recovery that M09 " "realises",
        ],
        [
            "Reduced hotline load",
            "Live tracking and arrival notification",
            "Contributes to the 60 per cent deflection of status enquiries",
        ],
        [
            "Defensible incentives",
            "Objective performance data per technician",
            "Makes performance-linked pay possible without dispute — which is "
            "itself a precondition for the productivity gain",
        ],
    ],
    "s14_soft": [
        [
            "Technician safety",
            "Lone-worker check-in and a panic alert give the company a duty-of-"
            "care mechanism it does not currently have at all. This is the "
            "benefit that would justify the module on its own if none of the "
            "others existed.",
        ],
        [
            "Disputes settled by evidence",
            "Geotagged arrival, validated photographs and an on-screen signature "
            "answer 'the technician never came' in seconds.",
        ],
        [
            "Fairness in how work is shared",
            "Assignment by visible score and rule removes favouritism from job "
            "distribution — which technicians notice long before managers do.",
        ],
        [
            "Evidence for progression",
            "Measured competence supports promotion from junior to senior to "
            "specialist on something better than impression.",
        ],
        [
            "The training data for everything that follows",
            "Every field action feeds the models that lift auto-assignment from "
            "nothing towards seventy per cent.",
        ],
        [
            "Visible modernity",
            "A customer watching a named, photographed technician approach on a "
            "map is the single most persuasive thing 1000FiX can show them.",
        ],
    ],
    "s14_close": "Everything here rests on one thing: a technician, at a door, in the "
    "rain, choosing to use the application rather than a notebook. Treat "
    "app adoption, crash rate, battery life and data usage as business "
    "metrics rather than technical ones, because in this module they are.",
    # ============================================ 17. learning it
    "s17_lede": "Two quite different learning paths, depending on whether you are on "
    "the board or on the road.",
    "s17_intro": [
        "A dispatcher and a technician need almost nothing in common from this "
        "module. The plan below covers both; take the half that applies to "
        "you and skim the other so you understand what the person on the far "
        "end of your day is looking at.",
        "For technicians the whole plan is really one instruction: use the app "
        "for a real job on the first day, with somebody beside you, and do not "
        "keep a parallel notebook. The notebook is what kills adoption, "
        "because it lets you postpone learning indefinitely.",
    ],
    "s17_plan": [
        [
            "Before you start",
            "Read section 1, then find yourself in section 2, then read the "
            "walkthrough in section 8 closest to your job.",
            "20 minutes",
            "Explain what the module changes and why",
        ],
        [
            "Day one — technicians",
            "Do a real job with the app, with somebody beside you. Accept, "
            "navigate, arrive, diagnose, scan, photograph, sign.",
            "1 job",
            "Complete a job without paper",
        ],
        [
            "Day one — dispatchers",
            "Watch a morning being assigned. Read the reasoning on five "
            "recommendations before agreeing with any of them.",
            "1 hour",
            "Understand what the score is weighing",
        ],
        [
            "Day two — technicians",
            "Read section 6.3 in full. Then deliberately work one job in "
            "aeroplane mode and watch it synchronise afterwards.",
            "45 minutes",
            "Trust the offline queue",
        ],
        [
            "Day two — dispatchers",
            "Read sections 6.1 and 6.2. Insert a test emergency and watch the "
            "route re-solve.",
            "45 minutes",
            "Let the board absorb disruption",
        ],
        [
            "Day three",
            "Read section 10. Try three things the system will refuse and read "
            "the message each time.",
            "30 minutes",
            "Recognise a rule rather than assuming a fault",
        ],
        [
            "End of week one",
            "Technicians: practise a failed visit and a cannot-complete properly. "
            "Dispatchers: read the override reasons your team recorded this week.",
            "30 minutes",
            "Handle the exceptions without help",
        ],
        [
            "Week two, early",
            "Read section 11. Notice how much of your day the system did without "
            "being asked.",
            "20 minutes",
            "Stop duplicating automatic work",
        ],
        [
            "Week two, middle",
            "Read section 15 and skim section 13. Technicians: reconcile a shift "
            "unaided. Dispatchers: read the dispatch map properly.",
            "40 minutes",
            "Diagnose before escalating",
        ],
        [
            "End of week two",
            "Read section 18 and keep it.",
            "15 minutes",
            "Work unsupervised",
        ],
    ],
    "s17_check_intro": "You have got it when you can do these without opening this book. "
    "For technicians that is usually about ten real jobs; for dispatchers "
    "about a week of mornings.",
    "s17_checks": [
        "Complete a whole job on the phone, offline, without touching paper",
        "Record a failed visit properly, with evidence, in under a minute",
        "Explain to a customer where the technician is and when they will " "arrive",
        "Reconcile a shift's cash unaided",
        "Say why the system recommended a particular technician",
        "Override a recommendation with a reason that would help somebody else",
        "Recognise when the system is enforcing a rule rather than " "malfunctioning",
        "Know the three things about the app that must be reported "
        "immediately: a sync that lost data, a geofence in the wrong place, "
        "and a panic alert that did not reach anybody",
    ],
    "s17_note": "If you are training technicians, do it on real jobs from the first "
    "hour and remove the paper alternative on the same day. Every day a "
    "parallel paper process survives is a day adoption does not happen.",
    # ============================================ 18. one page
    "s15_lede": "The module on one page, for a van door, a dispatch desk or a first "
    "day.",
    "s15_figures": [
        ("63", "things you can do"),
        ("13", "work order states"),
        ("14", "rules enforced"),
        ("13", "automatic behaviours"),
        ("21", "functions in the app"),
        ("24 hrs", "offline capability"),
        ("10", "reports available"),
        ("12", "modules depend on it"),
    ],
    "s15_never": [
        "Assign brand warranty work to a lapsed certification",
        "Offer a job to somebody on leave, off shift or at capacity",
        "Override a recommendation without a reason code",
        "Mark yourself on site from outside the customer geofence without an "
        "exception reason",
        "Record a failed visit without geotagged evidence",
        "Start your next shift with the last shift's cash unreconciled",
        "Carry more of an item than the configured van maximum",
        "Displace a job that is already at risk in order to fit an emergency",
        "Look at a technician's location history if your role does not permit " "it",
    ],
    "s15_where": CM.where_to_look("M02"),
}
