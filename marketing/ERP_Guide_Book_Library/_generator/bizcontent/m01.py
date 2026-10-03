# -*- coding: utf-8 -*-
"""
M01 — Service Request & Order Management.

The service order is the record everything else in the company hangs off. This
pack is the business reading of it: what it is for, what it lets a counter
agent, a dispatcher, a technician and a branch manager actually do, and what
changes on the day it goes live.

Worked examples name customers, devices, branches and amounts so the reader can
picture the job. Those details are illustrative — the service lines, delivery
modes, price bands and rules behind them are all from the specification.
"""
from bizcontent import common as CM

CONTENT = {

    # ============================================================== front
    "cover_line":
        "The service order is the single record of everything a customer has "
        "asked 1000FiX to do, and the honest answer to the question staff are "
        "asked more than any other: what is happening with my device?",

    "cover_inside": [
        ("Part one", "What the module is for, who uses it, and where it stops"),
        ("Part two", "All seventy things it lets you do, with worked examples "
                     "and five walkthroughs from a normal day"),
        ("Part three", "The rules, the automatic work, the permissions, the "
                       "measures and the troubleshooting"),
        ("Appendix A", "The full technical register for builders and testers"),
    ],

    "about": CM.about("the Service Request and Order Management module, M01"),
    "audience": CM.AUDIENCE,
    "how_arranged": CM.HOW_ARRANGED,
    "parts_table": CM.parts_table("M01"),
    "reading_note": CM.READING_NOTE,
    "appendix_note": CM.APPENDIX_NOTE,
    "part1_blurb": CM.PART1_BLURB,
    "part2_blurb": CM.PART2_BLURB,
    "part3_blurb": CM.PART3_BLURB,
    "appendix_blurb": CM.APPENDIX_BLURB,
    "part1_sections": CM.part1_sections("M01", "The kinds of work it has to carry"),
    "part2_sections": CM.part2_sections("The journey of a job"),
    "part3_sections": CM.PART3_SECTIONS,
    "appendix_sections": CM.APPENDIX_SECTIONS,
    "change_control": CM.CHANGE_CONTROL,
    "change_table": CM.change_table("The Service Operations Director"),
    "change_note": CM.CHANGE_NOTE,

    # ============================================================ exhibits
    "headline": [
        ("250,000+", "customer interactions a month", "every one lands here"),
        ("70", "things the module lets you do", None),
        ("12", "ways a job can reach us", "counter to WhatsApp"),
        ("51+", "branches on one record", None),
        ("9", "delivery modes, one order shape", None),
        ("14", "revenue streams it carries", None),
        ("16", "other modules depend on it", "more than any other module"),
        ("46", "person-weeks to build", "the largest single module"),
    ],

    "volume": [
        ("12", "ways in", "counter, phone, app, portal, bot, alert"),
        ("9", "delivery modes", "walk-in through to managed service"),
        ("14", "revenue streams", "one order shape covers all of them"),
        ("51+", "locations", "every branch working the same way"),
        ("16", "dependent modules", "field service to finance"),
    ],
    "volume_title": "The shape of the problem",
    "volume_sub": "Why a single, simple order type would never have worked",
    "volume_caption": "The scale the service order has to absorb",

    "does": [
        "Taking the request in, whatever channel it arrives on",
        "The order number, and the whole history attached to it",
        "Diagnosis, the estimate, and getting the customer to approve it",
        "The promise clock, and what happens when a promise is at risk",
        "Quality gates, handover, and the warranty on the repair itself",
        "Spotting repeat failures and attributing them",
        "Telling the customer where their device is, without being asked",
    ],
    "does_not": [
        "Bench-level repair execution — that is M31 Workshop",
        "Sending a technician to a customer's site — that is M02 Field Service",
        "Physically moving the device — that is M03 Logistics",
        "Working out the price — that is M36 Quotation and M11 Pricing",
        "Claiming money back from the brand — that is M09 Warranty",
        "Raising and chasing the invoice — that is M20 Receivables",
        "Holding the customer record — that is M33 Party Master",
        "Holding the device record — that is M17 Asset Registry",
    ],

    "areas_map": [
        ("Taking the job in", 15,
         "Twelve ways a customer can reach us, all landing on one record."),
        ("Running the job", 11,
         "Holds, transfers, splits, merges and reopens without losing "
         "the thread."),
        ("Diagnosis, estimate and approval", 10,
         "A price the customer has agreed to before anyone opens the device."),
        ("Getting the work done", 7,
         "Parts, people, workshop bench and outside specialists, all against "
         "one order."),
        ("Quality and handover", 8,
         "Nothing leaves the counter without a passed check and a signature."),
        ("Promises and repeat failures", 7,
         "A clock on every promise, and a name against every job done twice."),
        ("Keeping the customer informed", 4,
         "The customer finds out before they think to ask."),
        ("The other business lines", 8,
         "Rentals, data services, refurbishment, marketplace, contracts and "
         "recalls."),
    ],

    "area_bars": [
        ("Taking the job in", 15), ("Running the job", 11),
        ("Diagnosis, estimate and approval", 10), ("Quality and handover", 8),
        ("The other business lines", 8), ("Getting the work done", 7),
        ("Promises and repeat failures", 7),
        ("Keeping the customer informed", 4),
    ],

    "channels": [
        "Web portal", "Customer mobile app", "WhatsApp",
        "The AI assistant", "Hotline 16743", "Walk-in counter",
        "Email", "Corporate bulk upload", "Marketplace",
        "Partner referral", "Managed-service alert",
        "Contract maintenance schedule",
    ],
    "channels_hub": "Service order",
    "channels_title": "Twelve ways in, one record",
    "channels_sub": ("However the customer reaches us, the same numbered "
                     "record is created and the same clock starts"),
    "channels_note": "the single master record",
    "channels_caption": "Every intake channel produces the same kind of record",

    # ============================================ 1. what it is for
    "s1_lede":
        "M01 owns the service order — one numbered record covering everything "
        "a customer has asked us to do, from the moment they ask to the moment "
        "the money is settled.",

    "s1_intro": [
        "Everything 1000FiX sells eventually becomes a job someone has to do "
        "for a customer: a laptop repaired, a printer serviced on site, data "
        "recovered from a failed drive, a fleet of machines checked under "
        "contract. M01 is the module that holds that job. It creates the "
        "order, gives it a number, records who the customer is and what device "
        "is involved, works out who pays, keeps the clock, and follows the job "
        "until it is finished and billed.",

        "It is deliberately a thin record with a wide reach. M01 does not "
        "repair anything, does not move anything, does not price anything and "
        "does not invoice anything — other modules do all of that. What it "
        "does is hold the one true statement of what was asked for, what was "
        "promised, what has happened so far and what is left. Sixteen other "
        "modules read from it. That is more than any other module in the "
        "system, and it is why the specification calls M01 the object the "
        "company revolves around.",

        "For anyone working at a branch or in a workshop, the practical "
        "meaning is simple. There is one place to look. The order number a "
        "customer quotes on the phone finds the same record the technician has "
        "open on the bench, the same record the dispatcher sees in the queue, "
        "and the same record finance will invoice from. Nobody has to "
        "reconcile a counter book against a workshop register against a "
        "spreadsheet, because there is only one book.",
    ],

    "s1_problem": [
        "Today a service request is written on paper or typed into whichever "
        "spreadsheet that branch happens to keep. There is no consistent order "
        "number, so the same job can be called three different things in three "
        "places. There is no searchable history, so nobody at the counter can "
        "tell whether this customer brought the same device in six weeks ago. "
        "There is no clock, so nobody knows a promise has been broken until "
        "the customer rings to say so. And there is no reliable link between "
        "what was promised and what was delivered.",

        "The specification measures the consequence. Only around one fifth of "
        "the service order lifecycle is automated at all. Turnaround time is "
        "not measured. Rework — the same device coming back for the same "
        "fault — is completely invisible, which means nobody can be held to "
        "account for it and nobody can fix the cause. Warranty claims are "
        "compiled by hand, weeks after the work, from paper that may or may "
        "not still exist. Invoices are typed from those same forms three to "
        "seven days late.",

        "None of that is a technology problem in the first instance; it is a "
        "record-keeping problem. What M01 changes is that the record is made "
        "once, at the moment the customer asks, and everything afterwards is "
        "attached to it.",
    ],

    "s1_replaces": [
        ["A paper job sheet or a branch spreadsheet, one per branch",
         "One numbered service order, visible from any branch",
         "A customer can be helped by whoever picks up the phone, not only by "
         "the branch that took the job in."],
        ["An order number invented locally, or none at all",
         "A gapless order number built from branch, business line and year",
         "The number the customer quotes always finds the job, and no two jobs "
         "can share a number."],
        ["Asking the customer whether the device is under warranty",
         "Warranty, contract and membership cover checked automatically at "
         "intake",
         "The commercial treatment is settled before the job sheet prints, so "
         "there is no argument at collection."],
        ["A verbal promise about when it will be ready",
         "A clock, per stage, that everybody can see",
         "Late jobs surface before the customer notices rather than after."],
        ["Findings written on the back of the form",
         "A structured diagnosis with fault codes and photographs",
         "The warranty claim, the quality analysis and the next technician all "
         "read the same record."],
        ["Discovering rework when a customer complains",
         "The same device with the same fault inside thirty days flagged "
         "automatically and linked to the original job",
         "Rework becomes a number that can be reduced instead of an "
         "impression."],
        ["Invoicing from paper, days later",
         "A billable event the moment the job is delivered",
         "Work that has been done stops quietly failing to be billed."],
    ],

    "s1_one_sentence":
        "M01 turns 'a customer asked us to fix something' into a numbered, "
        "timed, evidenced record that everyone from the counter to the finance "
        "office reads the same way.",

    # ============================================ 2. who uses it
    "s2_lede":
        "Almost everybody. Sixteen roles have access to the service order, and "
        "for most of them it is the first screen they open in the morning.",

    "s2_intro": [
        "M01 is not a specialist tool. It is the shared surface where the "
        "counter, the workshop, the road, the contact centre and the finance "
        "office all meet, which is why so much care has gone into who can see "
        "and change what. The table that follows names the roles and what each "
        "one comes to the module for. Section 10 covers the permissions in "
        "detail; this is the plain version.",

        "Two things are worth noticing before the detail. First, the customer "
        "is on this list. They see a restricted view of their own orders "
        "through the tracking link and the portal, and that view is built from "
        "the same record — not from a copy that somebody has to keep in step. "
        "Second, several roles have read-only access for context: logistics "
        "needs to know what is in the box it is carrying, finance needs to "
        "know what it is billing for, quality needs to see everything. "
        "Read-only is a deliberate design, not an oversight.",
    ],

    "s2_roles": [
        ["Service centre agent",
         "Taking jobs in at the counter, finding existing orders, printing job "
         "sheets, handing devices back",
         "The intake screen, and the queue of jobs at their own branch"],
        ["Dispatch manager",
         "Deciding who does what and when, and rescuing jobs that are running "
         "late",
         "The live queue, sorted by which job is closest to breaching its "
         "promise"],
        ["Technician",
         "Reading the job, recording the diagnosis, logging time and parts, "
         "capturing photographs",
         "Their own assigned orders, on a phone or a bench terminal"],
        ["Workshop supervisor",
         "Loading the bench, moving work between technicians, releasing "
         "finished jobs",
         "The workshop's open orders with their repair level and age"],
        ["Quality inspector",
         "Running the checklist before a device may be released",
         "The list of orders waiting for a quality check"],
        ["Branch manager",
         "Watching work in progress, uncollected devices, SLA risk and value "
         "at the branch",
         "The branch board — open orders by state, age and value"],
        ["Contact centre agent",
         "Answering 'where is my device?', raising orders taken by phone",
         "Search by phone number, order number or device serial"],
        ["Warranty claims officer",
         "Reading completed warranty orders and their evidence packs",
         "All warranty-type orders, read-only"],
        ["Finance officer",
         "Confirming what is billable and what has been delivered",
         "All orders, read-only, with the billing context"],
        ["Operations Director",
         "Volume, turnaround, SLA and rework across every branch",
         "The estate-wide operations board"],
        ["Customer",
         "Seeing where their own device is, approving or rejecting an estimate",
         "The tracking link, with no login required"],
        ["Corporate portal user",
         "Raising and tracking jobs for their own company's fleet",
         "Their own company's orders only"],
    ],

    "s2_days": [
        {
            "title": "If you work at a counter",
            "text": [
                "The module is your morning. You will open the branch queue, "
                "check what is ready and uncollected, and then spend most of "
                "the day in two screens: intake and search. Intake is the one "
                "that matters. Everything that goes wrong later in a job — the "
                "dispute about a missing charger, the warranty claim the brand "
                "rejects, the customer who says they were never told the price "
                "— traces back to what was or was not captured in the first "
                "three minutes.",

                "The good news is that the screen does most of the "
                "remembering. It will not let you confirm without a device. It "
                "tells you who pays before you have to say anything. It prints "
                "the job sheet with the terms and the tracking link already on "
                "it. What it cannot do is take the condition photographs for "
                "you, and that is the one habit worth building deliberately.",
            ],
        },
        {
            "title": "If you dispatch or supervise",
            "text": [
                "You live in the queue, and the sort order you choose is the "
                "job. Sorted by SLA risk it tells you what will embarrass the "
                "branch today; sorted by state it tells you where the "
                "bottleneck is; sorted by age it tells you what has been "
                "forgotten. Section 13 goes through how to read it.",

                "The escalations will find you whether you look or not. They "
                "fire at half time on purpose, and acknowledging one without "
                "acting on it is recorded — an acknowledged breach reads worse "
                "in the report than one nobody saw. Most of the skill in this "
                "role is deciding, early, which jobs need a person and which "
                "will resolve themselves.",
            ],
        },
        {
            "title": "If you are a technician",
            "text": [
                "You will see the module on a phone or a bench terminal, and "
                "you will use perhaps ten of its seventy functions. The job "
                "arrives with its history attached: what the customer said, "
                "what came in with the device, what this device has been in "
                "for before. Then the diagnostic tree asks you questions and "
                "records your answers, measurements and photographs as you go.",

                "The part that feels like extra work is the evidence, and it "
                "is the part that protects you. A photograph taken at the "
                "bench is what settles an argument about a scratch six weeks "
                "later, and what gets a warranty claim paid instead of "
                "rejected. Nothing you record disappears into an archive "
                "nobody reads — the fault codes you assign are what the "
                "quality analysis and the predictive models are built from.",
            ],
        },
        {
            "title": "If you manage a branch",
            "text": [
                "Most of what you need arrives without you asking for it. The "
                "board shows open work, ageing, SLA risk and uncollected "
                "devices in real time; escalations reach you before breaches "
                "rather than after; the uncollected report is a saved view you "
                "will open every morning.",

                "The two figures worth watching weekly are first-pass quality "
                "and rework, because both are new. Neither has ever been "
                "measurable at 1000FiX, and both say something about the "
                "branch that turnaround time does not. Expect the first few "
                "months of rework figures to look worse than you assumed — "
                "that is the measurement starting, not the work deteriorating.",
            ],
        },
        {
            "title": "If you work in finance, warranty or quality",
            "text": [
                "You will mostly read rather than write, and what you read "
                "will arrive earlier than it does today. Finance gets a "
                "billable event the moment a job is delivered rather than a "
                "paper form three to seven days later. The warranty officer "
                "gets a claim-eligible event within twenty-four hours of "
                "completion, with the evidence pack already assembled. Quality "
                "gets rework attributed to a technician, a branch and a root "
                "cause without anybody having to admit to anything.",

                "The change for all three is the same: the work moves from "
                "assembling information to acting on it.",
            ],
        },
    ],

    "s2_note":
        "Cost, margin and internal notes are never shown to a customer, a "
        "corporate portal user or a marketplace seller. That is enforced by "
        "the system, not by staff remembering — see section 10.",

    # ============================================ 3. boundary
    "s3_lede":
        "M01 holds the request. Other modules do the work. Knowing exactly "
        "where the line falls saves more arguments than any other page in this "
        "book.",

    "s3_intro": [
        "The commonest mistake with a module this central is to assume it does "
        "everything. It does not, and the things it deliberately refuses to do "
        "are listed as carefully as the things it does. A service order says "
        "what was asked for and what state it is in. It does not say how the "
        "board was reflowed, which van the device travelled in, what the "
        "labour rate is, or whether the brand has paid the claim. Each of "
        "those belongs to a module that owns it properly.",

        "The most important boundary is between M01 and M31 Workshop. Before "
        "the current version of the specification, workshop execution sat "
        "inside M01 and the module had grown unmanageable. It was split: M01 "
        "keeps the customer-facing order, M31 keeps the bench. The practical "
        "effect is that a customer's tracking view shows 'in progress' while "
        "the workshop sees 'awaiting a Level 3 board technician, position four "
        "in the queue'. The customer does not need the second sentence and the "
        "workshop cannot work without it.",
    ],

    "s3_shared_intro":
        "Some ideas appear in more than one module. In every case exactly one "
        "module owns the idea and the others use it. This table says which is "
        "which for the concepts you will meet most often.",

    "s3_shared": [
        ["The customer", "M33 Party Master",
         "Looks them up and links them to the order. Never edits the customer "
         "record from here."],
        ["The device", "M17 Asset Registry",
         "Identifies it, or registers a new one inline during intake, then "
         "links it. The device's own history lives in M17."],
        ["The price", "M36 Quotation, using rates from M11 Pricing",
         "Asks for an estimate and displays what comes back. Never calculates "
         "a price itself."],
        ["Warranty cover", "M09 Warranty",
         "Asks whether cover is active at the request date, and hands over the "
         "evidence pack when the job is done."],
        ["The contract", "M08 Contract",
         "Reads whether this device is on a covered-asset list, and what "
         "service level the contract promises."],
        ["The parts", "M15 Inventory",
         "Raises a requirement against the order and tracks whether it has "
         "been met. Does not hold stock."],
        ["The invoice", "M20 Receivables",
         "Emits a billable event when the job is delivered. Never creates an "
         "invoice."],
        ["The technician's time", "M02 Field Service and M31 Workshop",
         "Receives the recorded time and rolls it up for costing."],
        ["The quality record", "M23 Quality",
         "Emits the quality and rework events. The analysis and corrective "
         "action live in M23."],
    ],

    # ============================================ 4. kinds of work
    "s4k_title": "The kinds of work it has to carry",

    "s4k_lede":
        "Nine ways of delivering a service, fourteen streams of revenue and "
        "twelve order types, all on one record. This section explains why that "
        "was the right decision and what it means in practice.",

    "s4k_intro": [
        "A repair brought to a counter, a technician sent to a customer's "
        "office, a printer serviced under contract, a hard drive sent to a "
        "clean-room, a rented projector returned damaged, a device refurbished "
        "for resale, an order fulfilled through a marketplace, a fault fixed "
        "over a remote connection, a fleet checked in one visit — these are "
        "not variations on a theme. They involve different people, different "
        "money, different risks and different promises.",

        "The design decision taken in the specification was to represent all "
        "of them with one order shape and typed extensions, rather than "
        "building nine separate order types. That is unusual: SAP's service "
        "management would model several document types with a document flow "
        "between them. The reason 1000FiX went the other way is the queue. A "
        "branch manager has one list of work, a dispatcher has one queue, a "
        "customer has one tracking link, and the operations board sums one "
        "kind of thing. Nine order types would have meant nine of everything.",

        "The cost of that decision is that the intake screen has to change "
        "shape according to the order type, and that some rules apply only to "
        "some types. The benefit is that turnaround time means the same thing "
        "everywhere, and that adding a tenth business line is configuration "
        "rather than a project.",
    ],

    "kinds_columns": [
        ("Repair work", "The core: something is broken and we fix it", [
            "Warranty — the brand pays",
            "Out of warranty — the customer pays",
            "AMC and RAMC — the contract pays",
            "Emergency — premium tariff, on-call rota",
            "Rework — nobody pays; it comes back free",
        ]),
        ("Contracted service", "Ongoing, planned, paid by agreement", [
            "Managed services — raised by an alert",
            "Preventive — raised by a maintenance plan",
            "Bulk site visits — many devices, one journey",
            "Recall campaigns — a batch against serial numbers",
        ]),
        ("Everything else", "Same record, different subject", [
            "Rental service — agreement, deposit, liability",
            "Data services — restricted visibility from creation",
            "Refurbishment — from trade-in or unrepairable",
            "Marketplace — an outside seller does the work",
        ]),
    ],
    "kinds_title": "Twelve order types, three families",
    "kinds_sub": ("Different money, different rules, different risks — one "
                  "record shape"),

    "s4k_header": ["The kind of work", "What is different about it",
                   "What stays the same"],
    "s4k_table": [
        ["Warranty repair",
         "The brand pays. Entitlement must be active on the request date. "
         "Before and after photographs are mandatory and the job cannot close "
         "without them. A claim event fires on delivery.",
         "One order number, one clock, the same quality gate, the same "
         "handover"],
        ["Out-of-warranty repair",
         "The customer pays. An estimate must be approved before work starts "
         "above BDT 5,000.",
         "As above"],
        ["AMC and RAMC",
         "A contract pays. The device must appear on the contract's "
         "covered-asset list. The contract's service level replaces the "
         "default promise.",
         "As above"],
        ["Managed service",
         "Raised by an alert or a ticket rather than by a person. Entitlement "
         "comes from the managed-service agreement.",
         "As above"],
        ["Emergency",
         "Premium tariff, out-of-hours routing to the on-call rota, priority "
         "handling.",
         "As above"],
        ["Preventive",
         "Created by a maintenance plan at the right lead time. Scheduled "
         "against a window rather than an emergency clock.",
         "As above"],
        ["Rental service",
         "Carries the rental agreement, the deposit position and the "
         "liability question. Who pays depends on how the damage happened.",
         "As above"],
        ["Data service",
         "Confidentiality-controlled from the moment it is created. Restricted "
         "visibility; not everyone at the branch can see it.",
         "As above"],
        ["Refurbishment",
         "The subject is stock, not a customer's property. Created from a "
         "trade-in, an unrepairable outcome or a retired rental.",
         "As above"],
        ["Marketplace",
         "An outside seller performs the work. We remain accountable for the "
         "customer's experience. The seller's access is time-limited and "
         "scoped to the awarded order.",
         "As above"],
        ["Recycling",
         "The device is being disposed of rather than repaired. Evidence and "
         "certification requirements apply.",
         "As above"],
        ["Rework",
         "Created automatically when the same device returns with the same "
         "fault inside thirty days. No charge; attributed to the original job.",
         "As above"],
    ],
    "s4k_caption": "The twelve order types and what distinguishes each",

    "s4k_note":
        "The order type is chosen at intake and drives almost everything that "
        "follows: who pays, which rules apply, what the customer is told and "
        "which promise the clock is measuring against. It is the single most "
        "consequential field on the intake screen.",

    # ============================================ 5. vocabulary
    "s4_lede":
        "Seventeen words that mean something specific here. Learn them once and "
        "the rest of the book, and most of the screens, become obvious.",

    "s4_intro": [
        "Every trade has its shorthand, and a shared system only works if "
        "everybody's shorthand means the same thing. These are the terms M01 "
        "uses in a particular way. Where a word already has a loose meaning on "
        "the shop floor, the tighter meaning is given here and the system will "
        "hold you to it.",
    ],

    "s4_glossary": [
        ["Service order",
         "The one numbered record of everything a customer has asked for on "
         "one occasion. Not the repair, not the visit — the request itself.",
         "Everywhere. It is the spine of the whole module."],
        ["Order type",
         "What kind of commercial job this is: warranty, out-of-warranty, AMC, "
         "managed service, emergency, rental, data service and so on. It "
         "decides who pays and which rules apply.",
         "Chosen at intake, and it changes what the screen asks you for."],
        ["Entitlement",
         "The answer to 'who pays for this?' — worked out at intake from "
         "brand warranty, extended warranty, contract cover, managed-service "
         "cover and membership tier.",
         "Shown on screen before the job sheet prints."],
        ["Job sheet",
         "The printed or messaged summary the customer takes away: what was "
         "brought in, its condition, the terms, the estimated turnaround and "
         "the tracking link.",
         "Printed at the counter at the end of intake."],
        ["Work order",
         "An instruction to somebody to do a piece of work. One service order "
         "can produce several — a site visit, a bench repair, a collection.",
         "Created from the service order once the work is approved."],
        ["SLA clock",
         "The timer against a promise. There are four running independently: "
         "response, diagnosis, repair and total resolution. Business hours and "
         "approved holds are honoured.",
         "Visible on the order and driving the dispatcher's queue order."],
        ["Hold",
         "A formally recorded pause with a reason — waiting for a part, for "
         "the customer, for the brand, for site access. It suspends the clock.",
         "Applied by a technician or dispatcher; released automatically."],
        ["Quality gate",
         "A checklist that must be passed before the device may be marked "
         "ready. Above a value threshold it must be passed by somebody other "
         "than the person who did the repair.",
         "Between 'in progress' and 'ready'. There is no way round it."],
        ["Rework",
         "The same device returning with the same fault category inside the "
         "configured window. Flagged automatically and linked to the original "
         "job.",
         "Raised by the system, not by a person; feeds quality reporting."],
        ["Repair warranty",
         "The guarantee 1000FiX gives on its own repair, as distinct from the "
         "brand's warranty on the product.",
         "Granted at handover and printed on the service report."],
        ["Beyond economic repair",
         "A formal declaration that fixing the device costs more than it is "
         "worth. Requires photographs and a second technician's confirmation.",
         "Ends the repair path and routes to trade-in, recycling or return."],
        ["Repair level",
         "How deep the work goes: Level 1 basic, Level 2 component, Level 3 "
         "board and micro-soldering. It decides who is allowed to do the job.",
         "Set during diagnosis; it drives routing and the choice of quality "
         "checklist."],
        ["Evidence pack",
         "The bundle of before and after photographs, fault codes, part "
         "serials and certifications that supports a warranty claim.",
         "Assembled automatically as the work proceeds; handed to M09 on "
         "delivery."],
        ["Billable event",
         "The signal M01 sends to finance to say there is now something to "
         "invoice. Not an invoice, and not a price — just the fact.",
         "Fires the moment a job is delivered. It is why nothing delivered "
         "goes unbilled."],
        ["Batch reference",
         "The shared identifier that groups several devices from one customer "
         "or one site so they are coordinated together.",
         "Used for corporate collections, site visits and recall campaigns."],
        ["Escalation",
         "An automatic message to a named role when a promise reaches 50, 75, "
         "90 or 100 per cent of its clock. Acknowledgement is tracked.",
         "It arrives before the breach, which is the whole point of it."],
        ["Privilege tier",
         "The customer's membership level — Gold and Diamond members receive "
         "priority-1 service automatically, whatever the service type.",
         "Applied at intake as part of the entitlement result."],
    ],

    # ============================================ 5. what you can do
    "s5_lede":
        "Seventy distinct things, grouped into eight areas of work. This "
        "section is the reference you will come back to.",

    "s5_intro": [
        "What follows is everything the module lets you do, area by area. Each "
        "area opens with a paragraph or two on what that part of the module is "
        "for, then a table of the individual functions: what it is called, "
        "what it does for you, and a typical use at 1000FiX. Most areas close "
        "with a worked example.",

        "The functions are not listed in the order they were specified; they "
        "are listed in the order the work happens. If you are learning the "
        "module, read the areas in sequence. If you are looking something up, "
        "the table of contents will take you straight to the area.",
    ],

    "areas": [
        # ---------------------------------------------------- 5.1 intake
        {
            "title": "Taking the job in",
            "intake": True,
            "who": [
                ("Mostly used by", "Service centre agents, contact centre "
                                   "agents and corporate portal users"),
                ("Also relied on by", "Dispatchers, who inherit whatever "
                                      "intake produced"),
                ("Where it happens", "The counter, the hotline, the app, the "
                                     "portal and the monitoring system"),
            ],
            "mistakes": [
                "Skipping the accessory and condition log because the customer "
                "is in a hurry. It takes forty seconds and it is the only "
                "defence against a dispute three weeks later.",
                "Creating a new customer instead of searching properly. "
                "Duplicates break history, warranty and the corporate account "
                "view all at once.",
                "Recording the symptom as free text without choosing the coded "
                "category. The diagnostic tree cannot act on a sentence.",
                "Promising a turnaround verbally instead of letting the job "
                "sheet state it. The clock is what the company is held to.",
                "Choosing a convenient order type to save time. It is the most "
                "consequential field on the screen and it is hard to unpick "
                "afterwards.",
            ],
            "intro": [
                "A job can reach 1000FiX in twelve different ways, from a "
                "customer walking into a branch in Dhanmondi to an automatic "
                "alert from a printer under a managed-service contract. All "
                "twelve produce the same kind of record. That is the single "
                "most important design decision in the module: whatever the "
                "channel, there is one service order, one number, one clock "
                "and one history.",

                "Intake is also where the commercial position is settled. "
                "Before the job sheet prints, the system has identified the "
                "customer, identified the device, checked what cover applies "
                "and shown the counter agent what the customer will be "
                "charged. Doing that at the start removes the argument at the "
                "end, which is where it usually happens today.",
            ],
            "features": [
                ["Twelve-channel intake",
                 "Creates a service order from any of the twelve ways a "
                 "customer can reach us, without anybody re-typing anything.",
                 "A request raised in the mobile app at midnight is in the "
                 "branch queue when the counter opens."],
                ["Order numbering",
                 "Gives every order a unique number built from branch, "
                 "business line and year, with no gaps and no reuse.",
                 "The number a customer reads out over the phone finds exactly "
                 "one job."],
                ["Order type classification",
                 "Sets what kind of job this is — warranty, out-of-warranty, "
                 "AMC, managed service, emergency, rental, data service and "
                 "eight more — which decides who pays and which rules apply.",
                 "A device under an active AMC is typed as AMC at intake, so "
                 "no invoice is ever raised against the customer."],
                ["Customer identification",
                 "Finds the customer, or creates them there and then, and "
                 "warns you if the phone number, email or national ID already "
                 "exists.",
                 "Stops the same corporate customer being created four times "
                 "across four branches."],
                ["Device identification",
                 "Identifies the device by serial, IMEI, asset tag, QR label, "
                 "or brand and model with proof of purchase — and registers a "
                 "new one without leaving the intake screen.",
                 "A customer arriving with a laptop bought elsewhere is served "
                 "in the same flow as one with a device we sold."],
                ["Entitlement evaluation",
                 "Works out who pays before the job is confirmed: brand "
                 "warranty, extended warranty, AMC or RAMC cover, "
                 "managed-service entitlement and Privilege tier.",
                 "The counter agent can say 'this is covered' with the screen "
                 "in front of them instead of promising and hoping."],
                ["Structured complaint capture",
                 "Records the problem through a symptom, category and "
                 "sub-category list plus free text in Bengali or English, with "
                 "voice input on mobile.",
                 "'Screen flickers when moved' becomes a coded symptom the "
                 "diagnostic tree can act on, not a phrase in a notebook."],
                ["Accessory and condition log",
                 "Records what came in with the device, its cosmetic "
                 "condition, any damage that was already there, and gets the "
                 "customer to acknowledge it.",
                 "Settles the argument about a scratched lid before it starts."],
                ["Intake evidence capture",
                 "Photographs the device as it was received, stamped with "
                 "time, location and the staff member who took it.",
                 "A dispute three weeks later is answered with a photograph, "
                 "not a memory."],
                ["Job sheet",
                 "Prints or sends a bilingual job sheet with the terms, the "
                 "estimated turnaround and the tracking link.",
                 "The customer leaves with something in their hand and a link "
                 "on their phone."],
                ["Multi-device job batch",
                 "Groups several devices from one customer or one corporate "
                 "site under a shared reference with a single point of "
                 "coordination.",
                 "Twelve laptops from one office are one conversation, not "
                 "twelve."],
                ["Appointment booking",
                 "Reserves a slot, checking that the branch actually has the "
                 "capacity and the skill for that kind of work.",
                 "A customer is not booked in for board-level work on a day "
                 "with no Level 3 technician."],
                ["Emergency and after-hours intake",
                 "Flags an emergency, applies the premium tariff and routes it "
                 "to the on-call rota outside business hours.",
                 "A server down at 11 p.m. reaches somebody, and the pricing "
                 "reflects it."],
                ["Universal search",
                 "Finds an order by anything — number, phone, serial, customer "
                 "name, or free text including Bengali — in well under a "
                 "second.",
                 "A caller who remembers nothing but their own phone number "
                 "can still be helped."],
                ["Saved views and filters",
                 "Lets you save, name and share the lists you use every day.",
                 "A branch manager opens 'uncollected over seven days' with "
                 "one click every morning."],
            ],
            "example": (
                "an out-of-warranty laptop at the counter",
                "Mrs Rahman brings a two-year-old laptop into the Dhanmondi "
                "branch on a Tuesday morning: the keyboard has stopped "
                "responding. The agent types her mobile number, and the system "
                "finds her — she bought a printer from us in 2024. She is not "
                "a Privilege member. The agent scans the service tag on the "
                "laptop; the device is not known, so it is registered inline "
                "in about fifteen seconds. Entitlement comes back as "
                "out-of-warranty: the brand cover expired four months ago, and "
                "there is no AMC. The screen shows this before anything is "
                "committed, so the agent tells her plainly that this will be a "
                "chargeable repair and that a price will be sent to her before "
                "any work starts. The agent records the symptom as "
                "'keyboard — no response — multiple keys', notes that the "
                "charger and the sleeve came in with it, photographs a "
                "pre-existing dent on the lid, and asks Mrs Rahman to confirm "
                "the condition note. The job sheet prints in Bengali and "
                "English with order number DHN-SRV-2026-04187 and a tracking "
                "link. Elapsed time at the counter: under three minutes."),
            "caution":
                "Entitlement is evaluated against the date the customer asked, "
                "not the date the job is worked. A device whose warranty "
                "expires while it is on the bench is still a warranty job. Do "
                "not re-type an order to 'fix' this — it is correct.",
        },

        # ---------------------------------------------------- 5.2 lifecycle
        {
            "title": "Running the job",
            "who": [
                ("Mostly used by", "Dispatch managers, branch managers and "
                                   "workshop supervisors"),
                ("Also relied on by", "Technicians, who apply and release "
                                      "holds"),
                ("Where it happens", "The queue and the order screen, rarely "
                                     "at the counter"),
            ],
            "mistakes": [
                "Applying a hold after the delay rather than when it starts. "
                "The clock is not recovered retrospectively, and that is "
                "deliberate.",
                "Cancelling a duplicate instead of merging it. Merging keeps "
                "both histories; cancelling throws one away.",
                "Choosing a hold reason that does not fit because the right "
                "one is not on the list. Raise the missing reason instead.",
                "Transferring a job without telling the receiving branch. The "
                "custody trail records the move; it does not make a telephone "
                "call.",
                "Reopening an old order for what is really new work because it "
                "is quicker. It corrupts the rework figure for everybody.",
            ],
            "caution":
                "Splitting and merging both preserve history, but neither is "
                "reversible in one click. Check the device and the fault "
                "before you split, not afterwards.",
            "intro": [
                "Once an order exists it has to survive contact with reality. "
                "Parts do not arrive. Customers stop answering. A device turns "
                "out to have two unrelated faults. Somebody raises the same job "
                "twice. A technician goes on leave halfway through. This area "
                "is the set of things you can do to a live order without "
                "losing its history or breaking its clock.",

                "The underlying idea is that an order moves through a fixed "
                "set of states, and the system knows which moves are legal. "
                "You cannot mark a device ready before it has passed quality, "
                "and you cannot invoice a job that has not been delivered. "
                "Everything else — pausing, transferring, splitting, "
                "reopening — is available, and every one of them leaves a "
                "trail.",
            ],
            "features": [
                ["Lifecycle state machine",
                 "Keeps the order in one of a known set of states and only "
                 "allows moves that make sense.",
                 "Nobody can quietly skip the quality check to get a device "
                 "out of the door."],
                ["Transition guards",
                 "Blocks a move until its preconditions are met — approval "
                 "before parts are issued, quality passed before ready, "
                 "payment or credit cleared before release.",
                 "The system refuses rather than warning, so the gate actually "
                 "holds."],
                ["Hold management",
                 "Pauses an order with a recorded reason and stops the SLA "
                 "clock, then restarts it automatically when the hold is "
                 "released.",
                 "Three days waiting for a part from Singapore do not count "
                 "against the branch's turnaround figure."],
                ["Reassignment and transfer",
                 "Moves an order between technicians, branches or workshops "
                 "with a complete custody trail.",
                 "A board-level repair moves from Sylhet to the Dhaka central "
                 "workshop and everyone can see who has the device."],
                ["Split and merge",
                 "Splits an order when a device needs two independent repairs, "
                 "and merges duplicates raised for the same device.",
                 "A laptop with a failed screen and a failed battery gets two "
                 "estimates the customer can approve separately."],
                ["Cancellation and abandonment",
                 "Cancels with a reason code, and automatically flags devices "
                 "left uncollected past the configured period, generating the "
                 "statutory notice.",
                 "The store room stops silently filling with devices nobody "
                 "owns."],
                ["Reopen",
                 "Reopens a closed order inside the repair-warranty window and "
                 "automatically links it as rework.",
                 "A customer returning with the same fault is not treated as a "
                 "new job at full price."],
                ["Priority override",
                 "Lets an authorised role raise or lower priority, with a "
                 "reason that is recorded.",
                 "A hospital's diagnostic printer jumps the queue, and there "
                 "is a record of who decided that and why."],
                ["Case linkage",
                 "Ties every visit, repair and consignment belonging to one "
                 "customer problem into a single view.",
                 "Two site visits, a collection and a bench repair read as one "
                 "story instead of four unrelated jobs."],
                ["Bulk operations",
                 "Changes state, assigns or notifies across many orders at "
                 "once, with a preview, a confirmation and the ability to undo.",
                 "Fifty orders affected by a courier failure are put on hold "
                 "and their customers told, in one action."],
                ["Archival",
                 "Moves long-closed orders out of the working lists while "
                 "keeping them fully retrievable.",
                 "The daily queue stays fast without anybody deleting history."],
            ],
            "example": (
                "the part that did not arrive",
                "Order CTG-SRV-2026-01922 is a printer fuser replacement at "
                "the Chittagong branch, promised in 48 hours. On day one the "
                "technician finds the fuser is out of stock across the whole "
                "network. The system raises a sourcing request, places the "
                "order on hold with the reason 'part unavailable — network "
                "wide', and stops the SLA clock at eleven hours elapsed. The "
                "customer receives a message the same afternoon with a revised "
                "commitment; nobody had to remember to send it. The part "
                "arrives on day four. Releasing the hold restarts the clock at "
                "eleven hours, not at eighty. The job completes with a total "
                "of nineteen working hours against a 48-hour promise, and the "
                "branch's turnaround figure records the truth: this job was "
                "not slow, it was blocked."),
        },

        # ---------------------------------------------------- 5.3 diagnosis
        {
            "title": "Diagnosis, estimate and approval",
            "who": [
                ("Mostly used by", "Technicians and service advisors"),
                ("Also relied on by", "Branch managers approving above the "
                                      "threshold, and customers, who approve "
                                      "or reject"),
                ("Where it happens", "On a phone at the bench, and on the "
                                     "customer's own phone"),
            ],
            "mistakes": [
                "Working through the diagnostic tree from memory instead of on "
                "screen. The recorded answers are what the warranty claim and "
                "the quality analysis are built from.",
                "Assigning an approximate fault code because the exact one "
                "takes longer to find. Brands reject claims coded loosely.",
                "Telling the customer a price on the telephone before the "
                "estimate is issued. What is recorded is what is enforceable.",
                "Starting work while approval is still pending, to save a day. "
                "Above BDT 5,000 the system will refuse; below it you are "
                "personally exposed.",
                "Quoting one line for a device with two unrelated faults. The "
                "customer loses the ability to approve one and defer the "
                "other.",
            ],
            "intro": [
                "This is where a complaint becomes a plan with a price on it. "
                "The module guides the technician through a diagnostic tree "
                "built for that device category, brand, model and symptom; "
                "records every answer, measurement and photograph; assigns a "
                "standard fault code; and asks M36 for an estimate based on "
                "that code. The customer then sees the estimate on whichever "
                "channel they prefer and accepts, part-accepts or rejects it.",

                "The discipline here is that nobody opens a device and starts "
                "spending money before the customer has agreed. Estimates "
                "above BDT 5,000 need documented customer approval; above BDT "
                "25,000 they need the branch manager as well. Those thresholds "
                "are configurable, and the system enforces them rather than "
                "trusting anyone to remember.",
            ],
            "features": [
                ["Diagnostic template library",
                 "Holds the decision trees — per device category, brand, model "
                 "and symptom — with branching and version history.",
                 "A new laptop model gets a diagnostic tree once, and every "
                 "branch benefits from it the same day."],
                ["Guided diagnosis",
                 "Walks the technician through the tree on a phone or bench "
                 "terminal and records every answer, reading and photograph.",
                 "A Level 1 technician reaches the same conclusion a senior "
                 "colleague would, because the questions are the same."],
                ["Fault coding",
                 "Assigns a standard fault code and root cause used "
                 "consistently across warranty claims, quality analysis and "
                 "the predictive models.",
                 "The brand accepts the claim because the fault is described "
                 "in their language, not ours."],
                ["Repair-level routing",
                 "Classifies the work as Level 1 basic, Level 2 component or "
                 "Level 3 board and micro-soldering, and routes it to somebody "
                 "qualified.",
                 "Board-level work never lands on a bench that cannot do it."],
                ["Estimate request",
                 "Asks M36 for a price using the fault code, the device, the "
                 "parts indication and the labour classification, and shows "
                 "what comes back.",
                 "The technician does not have to know the price list; they "
                 "have to know the fault."],
                ["Customer approval loop",
                 "Sends the quotation on the customer's preferred channel with "
                 "accept, part-accept and reject options, and an expiry.",
                 "Mrs Rahman approves the keyboard replacement from her phone "
                 "on the bus."],
                ["Internal approval thresholds",
                 "Requires internal sign-off above configurable values, on top "
                 "of the customer's approval.",
                 "A BDT 40,000 motherboard replacement needs the branch "
                 "manager as well as the customer."],
                ["Declined-repair handling",
                 "On a rejection, raises the diagnostic fee, issues reassembly "
                 "instructions and creates the return or collection task.",
                 "A declined job ends tidily instead of sitting in a drawer."],
                ["Second opinion",
                 "Routes high-value or contentious diagnoses to a senior "
                 "technician for review before anything is quoted.",
                 "An expensive diagnosis is checked before it reaches the "
                 "customer, not after they complain."],
                ["Multi-fault handling",
                 "Handles several independent faults on one device with "
                 "separate estimate lines the customer can approve "
                 "independently.",
                 "The customer fixes the screen now and leaves the battery for "
                 "next month, and both decisions are recorded."],
            ],
            "example": (
                "an estimate the customer part-accepts",
                "Diagnosis on Mrs Rahman's laptop finds two things: the "
                "keyboard ribbon connector has failed, and the battery is at "
                "61 per cent of its design capacity. The technician records "
                "both, with photographs, and the tree assigns fault codes for "
                "each. M36 returns an estimate of BDT 4,200 for the keyboard "
                "and BDT 7,800 for the battery. Because the total is above the "
                "BDT 5,000 threshold, documented customer approval is now "
                "mandatory and the system will not release the work without "
                "it. Mrs Rahman receives the quotation by SMS with a link. She "
                "accepts the keyboard line and rejects the battery line. The "
                "order proceeds with the keyboard work only; the battery "
                "finding stays on the device's record in M17 so that the next "
                "technician who sees this laptop knows about it. Nobody has to "
                "re-diagnose it."),
            "caution":
                "An expired estimate must be re-issued, never extended. If a "
                "customer comes back after the expiry, raise a fresh estimate "
                "— prices and part availability will have moved, and the "
                "system will not let you quietly reopen the old one.",
        },

        # ---------------------------------------------------- 5.4 execution
        {
            "title": "Getting the work done",
            "who": [
                ("Mostly used by", "Dispatchers, workshop supervisors and "
                                   "technicians"),
                ("Also relied on by", "Inventory, logistics and finance, "
                                      "downstream"),
                ("Where it happens", "The order screen and the bench"),
            ],
            "mistakes": [
                "Taking a part off the shelf without raising the requisition "
                "against the order. The job then shows a margin it did not "
                "earn.",
                "Recording labour time in a notebook and posting it later. "
                "Anything not posted to the order does not exist for costing.",
                "Sending a component to a specialist without recording the "
                "sub-contract. The device is then somewhere nobody can name.",
                "Declaring a device unrepairable without the second "
                "technician. The system will refuse, and rightly.",
                "Issuing a loan device informally. Loan units disappear "
                "exactly when they are not attached to an order.",
            ],
            "caution":
                "Job cost roll-up is only as good as what is posted to the "
                "order. Every hour and every part recorded somewhere else is "
                "profitability the company cannot see.",
            "intro": [
                "M01 does not perform the repair. What it does is coordinate "
                "everybody who does: it generates the work orders, tracks the "
                "parts, absorbs the labour time back from the field and the "
                "workshop, manages sub-contracting when the work goes outside, "
                "and accumulates every cost so the job's true margin is "
                "visible at the end.",

                "The costing point is easy to overlook and matters a great "
                "deal. Labour from a site visit, labour from the bench, parts "
                "from stock, a courier movement, an outside specialist's "
                "invoice and an overhead allocation all roll up to the one "
                "service order. Without that, nobody can say whether a "
                "particular kind of job makes money.",
            ],
            "features": [
                ["Work order generation",
                 "Turns an approved service order into one or more work orders "
                 "for the field or repair orders for the workshop, each with "
                 "its scope, skill requirement and target time.",
                 "One customer request becomes a site visit and a bench "
                 "repair, both traceable to the same job."],
                ["Labour time roll-up",
                 "Pulls the time recorded by field and workshop technicians "
                 "back onto the service order.",
                 "The job's real labour content is known without anyone "
                 "totalling timesheets."],
                ["Parts requisition",
                 "Raises a parts requirement against the order and tracks it "
                 "through M15 until it is met.",
                 "The dispatcher can see that a job is waiting on a part, not "
                 "on a person."],
                ["Sub-contracting",
                 "Sends an order or a component to an outside specialist or a "
                 "marketplace seller, tracking cost, promised time and custody.",
                 "A cracked display panel goes to a specialist and we still "
                 "know where the device is."],
                ["Unrepairable determination",
                 "Declares a device beyond economic repair, with photographic "
                 "evidence and a second technician's confirmation, then routes "
                 "it to trade-in, recycling or return.",
                 "The decision is defensible if the customer disputes it."],
                ["Loan device management",
                 "Issues and tracks a loan device while the customer's own is "
                 "in repair, and reconciles its return.",
                 "Loan units stop disappearing, because each one is attached "
                 "to an order."],
                ["Job cost roll-up",
                 "Accumulates labour, parts, logistics, sub-contract and "
                 "overhead against the order.",
                 "Finance can answer whether printer contract work is actually "
                 "profitable."],
            ],
            "example": (
                "one request, two work orders",
                "A corporate customer in Gulshan reports that a networked "
                "multifunction printer is jamming and that nobody in the "
                "office can scan to email. Intake creates one service order. "
                "Diagnosis establishes two things: a worn pickup roller, which "
                "is physical, and a scan-to-email configuration failure, which "
                "is not. The order generates two work orders. The first is a "
                "field visit for the roller, assigned through M02 to a "
                "technician with the right parts on the van. The second is a "
                "remote task, handled through M05 by an engineer who never "
                "leaves the office. Both report back to the same service "
                "order. The customer sees one job, one promise and one "
                "completion message. Finance sees one job with two labour "
                "lines, one part and no travel charged twice."),
        },

        # ---------------------------------------------------- 5.5 quality
        {
            "title": "Quality and handover",
            "who": [
                ("Mostly used by", "Quality inspectors and counter agents"),
                ("Also relied on by", "Technicians capturing the evidence, and "
                                      "warranty claims officers reading it "
                                      "later"),
                ("Where it happens", "The bench and the counter"),
            ],
            "mistakes": [
                "Taking the after photographs before final reassembly. The "
                "evidence has to show the device as the customer receives it.",
                "Passing a checklist item without performing it because the "
                "repair obviously works. The checklist is the audit trail.",
                "Releasing a device to whoever arrives holding the job sheet. "
                "Identity verification is part of the handover for a reason.",
                "Capturing the signature after the device has changed hands. "
                "The signature evidences the state at handover, not the fact "
                "of it.",
                "Explaining the repair warranty verbally instead of pointing at "
                "the service report. The report is what the customer will "
                "still have in three weeks.",
            ],
            "intro": [
                "Nothing leaves 1000FiX without passing a check, and nothing "
                "is handed to a customer without a signature. This area is the "
                "part of the module that protects the company's reputation and "
                "its ISO 9001 certification, and it is the part with the "
                "fewest exceptions in it.",

                "The quality gate is a hard block. An order cannot reach "
                "'ready' without a passed checklist appropriate to the device "
                "type and the repair level. Above a configurable value, the "
                "check must be done by somebody other than the person who did "
                "the repair — the system enforces the separation, so a "
                "technician cannot pass their own work. Before and after "
                "photographs are mandatory on every warranty order and the job "
                "cannot close without them.",
            ],
            "features": [
                ["Quality gate",
                 "Stops an order reaching 'ready' until a checklist "
                 "appropriate to that device and that repair level has been "
                 "passed.",
                 "A board-level repair gets a board-level check, not the "
                 "generic one."],
                ["Independent quality control",
                 "Requires the check to be done by someone other than the "
                 "repairing technician above a set value or risk level.",
                 "Above BDT 25,000 the repairer physically cannot mark their "
                 "own work as passed."],
                ["Before and after evidence",
                 "Requires photographs before and after, stamped with time and "
                 "location, and assembles them into the warranty evidence pack.",
                 "The claim pack is complete on the day the job finishes, not "
                 "reconstructed weeks later."],
                ["Customer handover",
                 "Captures identity verification, confirmation that the "
                 "accessories went back, and an electronic signature.",
                 "A device is never released to the wrong person, and the "
                 "charger going missing is not a matter of opinion."],
                ["Service report",
                 "Produces a bilingual report of what was found, what was "
                 "done, what was replaced and what warranty applies to the "
                 "repair.",
                 "The customer leaves knowing exactly what they paid for."],
                ["Repair warranty",
                 "Applies and tracks a guarantee period on our own work, and "
                 "automatically treats a return inside that window as warranty "
                 "rework.",
                 "A customer who comes back in three weeks is not charged "
                 "again, and the branch knows it happened."],
                ["Delivery coordination",
                 "Either triggers a logistics consignment for return delivery, "
                 "or tells the customer the device is ready to collect.",
                 "The handoff to the courier is part of the job, not a "
                 "separate phone call."],
                ["Device photo library",
                 "Keeps the full photographic history of a device across every "
                 "service event it has ever had.",
                 "The dent that appears in year three can be traced to the "
                 "year-one intake photograph."],
            ],
            "example": (
                "the check that failed",
                "A technician at the Uttara branch completes a screen "
                "replacement worth BDT 18,500 and marks the work complete. The "
                "order moves to quality control. The inspector runs the "
                "checklist for a Level 2 display repair: power on, display "
                "uniformity, touch response across the panel, hinge alignment, "
                "no cosmetic damage introduced. Touch response fails in the "
                "bottom right corner. The inspector marks the check as failed "
                "with a note and a photograph, and the order returns to 'in "
                "progress' automatically. The technician reseats the digitiser "
                "connector and resubmits. The second check passes. What "
                "matters is what did not happen: the customer was never "
                "telephoned to come and collect a device that would have gone "
                "straight back out again as rework, and the branch's "
                "first-pass quality figure now honestly records one failure "
                "and one pass."),
        },

        # ---------------------------------------------------- 5.6 SLA
        {
            "title": "Promises and repeat failures",
            "who": [
                ("Mostly used by", "Dispatch managers, branch managers and the "
                                   "quality manager"),
                ("Also relied on by", "Everybody, indirectly — the clock runs "
                                      "on every job"),
                ("Where it happens", "The queue, the escalation inbox and the "
                                     "weekly rework analysis"),
            ],
            "mistakes": [
                "Acknowledging an escalation without acting on it. "
                "Acknowledgement is tracked, and an acknowledged breach reads "
                "worse than an unacknowledged one.",
                "Treating the 50 per cent escalation as noise. It exists "
                "precisely because there is still time to act.",
                "Arguing about a rework flag instead of correcting the fault "
                "code. The flag follows the code.",
                "Reading SLA compliance without reading breach causes. The "
                "figure on its own tells you nothing you can act on.",
                "Assuming a customer delay excuses a breach. It does, but only "
                "if the hold was applied at the time.",
            ],
            "intro": [
                "Two problems that look unrelated and are not. The first is "
                "keeping the promise made at intake. The second is knowing "
                "when a job has had to be done twice. Both come down to "
                "measuring something the company currently does not measure at "
                "all.",

                "On the promise side, there are four clocks running "
                "independently on every order — response, diagnosis, repair "
                "and total resolution — and they understand business hours, "
                "holidays and approved holds. Escalations fire at 50, 75, 90 "
                "and 100 per cent of the promise, to named roles, with "
                "acknowledgement tracked. The point is that a manager finds "
                "out at 50 per cent, when something can still be done.",

                "On the rework side, any new order for the same device and the "
                "same fault category inside thirty days is flagged "
                "automatically and linked to the original. It is attributed to "
                "the technician, the branch and the root cause. This is the "
                "first time rework has been visible at 1000FiX at all.",
            ],
            "features": [
                ["SLA definition",
                 "Sets the promise by service type, business line, brand, "
                 "customer tier, contract and priority, understanding the "
                 "working calendar.",
                 "A Gold member's emergency and a walk-in's routine repair "
                 "carry different promises, automatically."],
                ["Multi-clock SLA",
                 "Runs response, diagnosis, repair and total-resolution clocks "
                 "separately, honouring holds and business hours.",
                 "A fast response followed by a slow repair shows up as "
                 "exactly that, instead of averaging into nothing."],
                ["Escalation matrix",
                 "Escalates at 50, 75, 90 and 100 per cent of the promise to "
                 "defined roles, and tracks whether the escalation was "
                 "acknowledged.",
                 "The branch manager hears about a job at risk with time left "
                 "to rescue it."],
                ["Automatic re-prioritisation",
                 "Reassigns or re-prioritises on its own when a promise is "
                 "about to be missed and the assignee is not responding.",
                 "A technician who has gone quiet does not silently take a job "
                 "past its deadline."],
                ["Rework detection",
                 "Flags a new order for the same device and fault category "
                 "inside the configured window and links it to the original.",
                 "Nobody has to notice; the system notices."],
                ["Rework accountability",
                 "Attributes the rework to the original technician, branch and "
                 "root cause, and raises the quality event.",
                 "Training and coaching can be aimed at a real pattern instead "
                 "of a hunch."],
                ["Repeat-failure analysis",
                 "Identifies devices, models or parts failing more often than "
                 "they should and raises a quality alert.",
                 "A bad batch of chargers is spotted from the data rather than "
                 "from complaints."],
            ],
            "example": (
                "an escalation that saved a promise",
                "A corporate AMC customer logs a printer fault at 09:40 on a "
                "Sunday. The contract promises resolution within eight working "
                "hours, so the clock will expire at 17:40. At 13:40, at 50 per "
                "cent, the job is still unassigned because the allocated "
                "technician called in sick and nobody reassigned it. The "
                "escalation fires to the dispatch manager, who reassigns it "
                "within ten minutes. At 15:20, at 75 per cent, the technician "
                "is on site but waiting for building access; the second "
                "escalation reaches the account manager, who telephones the "
                "customer's facilities team. The job completes at 16:55, "
                "inside the promise. Under the old way of working the first "
                "anybody would have known was the customer's complaint on "
                "Monday morning."),
            "caution":
                "The clock only stops for an approved hold reason. Putting a "
                "job on hold because you are busy is not one of them, and the "
                "hold reasons are a short, governed list for exactly that "
                "reason.",
        },

        # ---------------------------------------------------- 5.7 visibility
        {
            "title": "Keeping the customer informed",
            "who": [
                ("Mostly used by", "Nobody, directly — it runs itself"),
                ("Also relied on by", "Contact centre agents, who read the "
                                      "notification history when a customer "
                                      "queries it"),
                ("Where it happens", "The customer's phone"),
            ],
            "mistakes": [
                "Telephoning a customer to repeat something the system has "
                "already sent. It reads as disorganisation, not attentiveness.",
                "Writing internal detail into a note on the assumption the "
                "customer will never see it. They will not — but write as "
                "though they might.",
                "Ignoring an out-of-date contact number. Every message after "
                "that point is wasted and the customer believes they were "
                "forgotten.",
                "Sending a manual apology instead of letting the proactive "
                "delay notice go with its revised commitment. The commitment "
                "is the part the customer actually wants.",
            ],
            "caution":
                "Everything in this area depends on the contact details being "
                "right in M33. One wrong mobile number silently disables all "
                "four functions for that customer.",
            "intro": [
                "Four functions, and between them they are expected to remove "
                "three in every five calls to the hotline. Almost all of those "
                "calls are the same question — what is happening with my "
                "device? — and the module answers it before it is asked.",

                "The mechanism is a tokenised tracking link issued on the job "
                "sheet. It needs no login and shows a visual timeline of where "
                "the job has got to, in language written for a customer rather "
                "than for the workshop. Behind it, every lifecycle milestone "
                "emits an event with a customer-safe message, and the "
                "notification module turns that into an SMS, an email or a "
                "WhatsApp message depending on what the customer prefers.",
            ],
            "features": [
                ["Milestone events",
                 "Announces every significant step in the job with a message "
                 "written to be safe to show a customer.",
                 "'Your device has passed its quality check' goes out; "
                 "'awaiting Level 3 bench slot' does not."],
                ["Tracking link",
                 "Gives the customer a private link showing a visual timeline "
                 "of their job, with no account and no password.",
                 "A customer checks progress at midnight without telephoning "
                 "anybody."],
                ["Proactive delay notice",
                 "Notices that a promised date is going to be missed and tells "
                 "the customer, with a revised commitment, before they find "
                 "out themselves.",
                 "The conversation becomes 'thank you for letting me know' "
                 "instead of 'why did nobody call me?'"],
                ["Post-service survey trigger",
                 "Asks the customer what they thought, a set interval after "
                 "handover.",
                 "Satisfaction becomes a number per branch and per technician "
                 "rather than an anecdote."],
            ],
            "example": (
                "the call that was never made",
                "Mrs Rahman's keyboard repair takes two days. In that time she "
                "receives four messages: her job was received and here is the "
                "link; the diagnosis is complete and an estimate is on its "
                "way; the repair is finished and has passed its quality check; "
                "the device is ready to collect at Dhanmondi until 8 p.m. She "
                "opens the tracking link twice, both times in the evening. She "
                "does not telephone the branch at all. Multiply that across "
                "the roughly quarter of a million interactions the company "
                "handles each month and the contact centre gets a substantial "
                "part of its capacity back for work that actually needs a "
                "human being."),
        },

        # ---------------------------------------------------- 5.8 extensions
        {
            "title": "The other business lines",
            "who": [
                ("Mostly used by", "Account managers, specialist teams and the "
                                   "system itself"),
                ("Also relied on by", "Branches, who see this work in the same "
                                      "queue as everything else"),
                ("Where it happens", "Mostly nowhere visible — most of this "
                                     "work creates itself"),
            ],
            "mistakes": [
                "Treating a contract-generated preventive job as lower "
                "priority because nobody telephoned about it. The contract "
                "promised it.",
                "Discussing a data-services case in an open branch channel. "
                "Restricted visibility exists for a reason.",
                "Raising a separate order per device for a corporate site "
                "visit. Use the batch, or one visit is counted thirty times.",
                "Handling a marketplace job informally because an outside "
                "seller is doing the work. We remain accountable for the "
                "customer's experience.",
            ],
            "intro": [
                "1000FiX is not only a repair business. It rents equipment, "
                "recovers data, refurbishes and resells, fulfils marketplace "
                "orders, runs managed services and delivers preventive work "
                "under contract. Each of those creates work that has to be "
                "tracked, and the decision taken in the specification was to "
                "use one order shape with typed extensions rather than nine "
                "separate systems.",

                "The practical result is that a rental service call, a data "
                "recovery case and a contract preventive visit are all service "
                "orders. They carry different extra fields, obey different "
                "rules and have different visibility, but they queue in the "
                "same list, use the same clock and report into the same "
                "numbers.",
            ],
            "features": [
                ["Rental service intake",
                 "Creates an order for a rental asset carrying the agreement, "
                 "the deposit and the liability position.",
                 "A damaged rental projector is assessed with the contract "
                 "terms already on the screen."],
                ["Data-service intake",
                 "Creates a data recovery case as a confidentiality-controlled "
                 "order with restricted visibility from the moment it exists.",
                 "A law firm's failed drive is not visible to the whole "
                 "branch."],
                ["Refurbishment intake",
                 "Creates refurbishment work from a trade-in, an unrepairable "
                 "outcome or a rental retirement.",
                 "A device declared beyond economic repair becomes stock "
                 "instead of waste."],
                ["Marketplace job creation",
                 "Creates an order from a marketplace transaction with the "
                 "outside seller as the executing party.",
                 "We stay accountable for the customer experience even when "
                 "somebody else does the work."],
                ["Managed-service generated work",
                 "Creates an order from a monitoring alert, a managed-service "
                 "ticket or a scheduled task.",
                 "A printer that reports a failing fuser books its own service "
                 "call."],
                ["Contract-generated work",
                 "Creates scheduled preventive work from contract maintenance "
                 "plans, at the right lead time.",
                 "Quarterly preventive visits appear in the queue without "
                 "anyone maintaining a diary."],
                ["Bulk corporate site visit",
                 "Plans one visit covering many devices at a single site, with "
                 "each device's outcome tracked separately.",
                 "Thirty machines at a bank branch are one visit and thirty "
                 "outcomes."],
                ["Recall campaign",
                 "Runs a brand recall as a batch of orders against the "
                 "affected serial numbers.",
                 "A manufacturer's battery recall is executed and evidenced "
                 "across every affected customer."],
            ],
            "example": (
                "a printer that raised its own job",
                "A multifunction printer at a corporate site under a managed "
                "print contract reports that its fuser has passed 90 per cent "
                "of rated life. M05 raises the alert; because the contract "
                "covers preventive replacement, a service order is created "
                "automatically with the order type set to managed service, the "
                "entitlement already resolved to 'covered by contract', and "
                "the device and customer already identified from the "
                "monitoring record. The dispatcher sees a new job in the "
                "queue, scheduled against the contract's preventive window "
                "rather than an emergency clock. No customer telephoned, no "
                "agent typed anything, and the first the customer hears is a "
                "message proposing a visit slot."),
        },
    ],

    # ============================================ 6. the journey
    "s6_title": "The journey of a job",
    "s6_lede":
        "Fourteen states from the moment a customer asks to the moment the "
        "record is archived, and the handful of them that are hard stops.",

    "s6_intro": [
        "Every service order follows the same path, whatever kind of job it "
        "is. Some states are skipped — a warranty job with no chargeable work "
        "goes straight from received to in progress with no estimate at all — "
        "but the order of the states never changes and no state can be jumped.",

        "The value of a fixed path is that everybody, in every branch, is "
        "describing the same thing when they say a job is 'in QC'. It also "
        "means the customer's tracking view can be generated from the state "
        "without anybody writing an update.",
    ],

    "journey": [
        ("Draft", "Agent or portal", None),
        ("Received", "Agent, portal, API", None),
        ("Diagnosing", "Technician", None),
        ("Estimate pending", "System", None),
        ("Awaiting approval", "Customer", "gate"),
        ("Approved", "Customer + approver", None),
        ("In progress", "Technician", None),
        ("On hold", "Technician, dispatcher", "clock stops"),
        ("Quality check", "QC inspector", "gate"),
        ("Ready", "Branch", None),
        ("Delivered", "Agent, technician, rider", "gate"),
        ("Invoiced", "System", None),
        ("Closed", "System", None),
        ("Archived", "System", None),
    ],
    "journey_title": "The path every service order follows",
    "journey_sub": ("Fourteen states. Three are gates that need a person, and "
                    "one stops the clock."),
    "journey_caption": "The service order lifecycle, in the order it happens",

    "s6_stages": [
        ["Draft", "Intake has started but the order is not confirmed yet.",
         "Agent or portal",
         "Nothing. This is the only state you can abandon freely."],
        ["Received", "The job exists, the clock is running.",
         "Agent, portal or API",
         "Customer and device identified; entitlement evaluated."],
        ["Diagnosing", "Somebody is working out what is wrong.",
         "Dispatcher or agent assigns; technician works",
         "Assigned to a technician or a workshop."],
        ["Estimate pending", "The fault is known; a price is being prepared.",
         "Technician completes; system requests",
         "Diagnostic checklist complete and a fault code assigned."],
        ["Awaiting approval", "The customer has the price and has not answered "
                              "yet.",
         "System issues; customer decides",
         "An estimate received from M36 and issued to the customer."],
        ["Approved", "The customer has said yes, and any internal sign-off has "
                     "been given.",
         "Customer, plus an approver above the threshold",
         "Customer decision recorded; internal thresholds satisfied."],
        ["In progress", "The work is being done.", "Technician",
         "Required parts reserved or confirmed available."],
        ["On hold", "Work is paused for a recorded reason and the clock has "
                    "stopped.",
         "Technician or dispatcher",
         "An approved hold reason selected from the governed list."],
        ["Quality check", "The work is finished and is being checked.",
         "Technician submits; inspector checks",
         "Work recorded complete, with time and parts posted."],
        ["Ready", "The device has passed and is waiting to go back.",
         "QC inspector releases",
         "A passed quality checklist. This is a hard gate."],
        ["Delivered", "The customer has it.",
         "Agent, technician or rider",
         "Identity verified, accessories confirmed, signature captured."],
        ["Invoiced", "Finance has been told there is something to bill.",
         "System", "A billable event accepted by M20."],
        ["Closed", "The money is settled or the claim has been raised.",
         "System",
         "Payment settled, credit terms applied, or a warranty claim raised."],
        ["Archived", "Out of the working lists, still fully retrievable.",
         "System", "The retention window has passed."],
    ],

    "s6_gates_intro":
        "Three points in the path are hard stops: the system refuses to move "
        "the order on until the condition is met, and there is no override. "
        "Two more are conditional stops that apply above a value threshold. "
        "Between them they are the reason a device cannot leave the building "
        "unchecked, unapproved or unsigned-for.",

    "gates": [
        ("Entitlement resolved",
         "Who pays is decided before the job sheet prints: brand warranty, "
         "contract cover, managed service or the customer", "System"),
        ("Customer approved the price",
         "Above BDT 5,000, no part is issued and no labour booked until "
         "documented approval exists", "Customer"),
        ("Manager approved the price",
         "Above BDT 25,000, the branch manager's approval is required as well "
         "as the customer's", "Branch manager"),
        ("Quality check passed",
         "A checklist appropriate to the device and repair level; above BDT "
         "25,000 it must be a second person", "QC inspector"),
        ("Handover evidenced",
         "Identity verified, accessories confirmed and an electronic signature "
         "captured before the device is released", "Agent or rider"),
        ("Billable event raised",
         "The order cannot close until finance has been given something to "
         "bill or a warranty claim has been raised", "System"),
    ],

    "s6_wrong_intro":
        "Jobs do not fail evenly across the path. Almost all of the trouble "
        "collects at four points, and knowing which four saves a great deal of "
        "hunting. This table is the distilled version of what the operations "
        "board will show you once the module is live.",

    "s6_wrong": [
        ["Received",
         "The record was made in a hurry: no condition photographs, a free-text "
         "symptom, the wrong order type.",
         "Everything downstream takes longer, and disputes at collection.",
         "There is no fix later. This is why intake is worth the three "
         "minutes."],
        ["Diagnosing",
         "The job sits unassigned because nobody picked it up.",
         "It appears near the top of the age sort with no technician against "
         "it.",
         "Assign it. If this happens regularly the dispatch rota needs "
         "looking at, not the individual."],
        ["Awaiting approval",
         "The customer does not answer. This is the single largest cause of "
         "slow jobs.",
         "A cluster of orders in this state on the board.",
         "The reminders run at 24 and 48 hours by themselves. Check the "
         "contact details are right before chasing by hand."],
        ["In progress",
         "A part is unavailable and the job was not put on hold.",
         "The clock keeps running and the job drifts towards a breach that "
         "was not the branch's fault.",
         "Apply the hold when the wait starts. Retrospective holds do not "
         "recover the clock."],
        ["On hold",
         "The hold is never released because the reason resolved quietly.",
         "Old jobs with stopped clocks sitting at the bottom of the age sort.",
         "Review held jobs weekly. The clock being stopped is not the same as "
         "the customer being happy."],
        ["Quality check",
         "A queue forms because there is one inspector on shift.",
         "A cluster in this state, usually in the afternoon.",
         "This is a rota question. It is also the one place where clearing "
         "the queue by relaxing the check is absolutely not available."],
        ["Ready",
         "The customer does not come.",
         "The uncollected report grows.",
         "Nothing, for thirty days — the reminder sequence handles it. Then "
         "the abandonment process starts by itself."],
        ["Delivered",
         "The signature or the accessory confirmation was skipped.",
         "The system will have refused, so in practice this means somebody "
         "found a way round the process outside the system.",
         "Investigate. A device released without evidence is a liability "
         "nobody has priced."],
    ],

    "s10_restrictions_intro":
        "Some things are hidden from people who otherwise have full access to "
        "the order. These are not oversights and they are not negotiable at a "
        "branch level; they are enforced in the software.",

    "s10_restrictions": [
        ["Unit cost, total cost and margin",
         "Senior operational roles and finance only — the Operations Director, "
         "branch and workshop managers, and the finance officer",
         "A technician's judgement about a repair should not be influenced by "
         "what it costs the company, and cost data reaching a customer through "
         "any route would be damaging."],
        ["Internal notes",
         "Internal staff only. Never shown on the customer portal, the "
         "corporate portal or to a marketplace seller.",
         "Internal notes are where honest operational language lives. The "
         "system guarantees they stay internal so that people write honestly."],
        ["Data-services case content",
         "The data services team and the case's own technician",
         "Data recovery involves other people's personal and commercial "
         "information. Restricted visibility from creation is the only safe "
         "default."],
        ["Independent quality check on your own repair",
         "Nobody — the repairing technician is blocked above the value "
         "threshold",
         "A check by the person who did the work is not a check, and the "
         "certification the company holds depends on it being one. This is a "
         "segregation of duties rule and it has no override."],
        ["Marketplace seller access",
         "Scoped to the order they were awarded, and time-limited",
         "An outside party should see the job they are doing and nothing "
         "else, for exactly as long as they are doing it."],
        ["Customer data-access notes",
         "Captured only with explicit consent, and purged at handover",
         "They are personal data on somebody else's device. Keeping them "
         "after the job is finished serves no purpose and creates risk."],
    ],

    "s6_note":
        "The path can be entered again from the end. Reopening a closed order "
        "inside the repair-warranty window puts it back at 'received' and "
        "links it to the original as rework. This is the only way back in, and "
        "it is deliberately visible.",

    # ============================================ 7. day in the life
    "s7_lede":
        "Five walkthroughs from an ordinary week, following one job each from "
        "the first contact to the last.",

    "s7_intro": [
        "The sections above describe the module a piece at a time. These "
        "walkthroughs put the pieces together. Each follows a single job "
        "across every person who touches it, so you can see where your own "
        "part of the work sits in somebody else's day.",

        "The customers, devices, branches and amounts are illustrative. The "
        "service lines, delivery modes, thresholds and rules behind them are "
        "exactly as the specification states them.",
    ],

    "scenarios": [
        {
            "title": "A walk-in repair, paid by the customer",
            "narrative": [
                "The commonest job in the company, and the one most people "
                "will learn first. A customer arrives at a branch with a "
                "device that is out of warranty, and leaves two days later "
                "with it working.",
            ],
            "lanes": [
                ("Customer", [(0, "Brings the laptop to the Dhanmondi counter"),
                              (2, "Approves the keyboard line by SMS"),
                              (5, "Collects and signs")]),
                ("Counter agent", [(0, "Finds her by phone number; registers "
                                       "the device; prints the job sheet"),
                                   (5, "Verifies identity; returns charger and "
                                       "sleeve")]),
                ("Technician", [(1, "Guided diagnosis; two faults found and "
                                    "coded"),
                                (3, "Replaces the keyboard ribbon")]),
                ("QC inspector", [(4, "Runs the Level 2 checklist and passes "
                                      "it")]),
                ("System", [(0, "Entitlement: out of warranty. Clock starts"),
                            (2, "Estimate requested from M36 and issued"),
                            (4, "Service report generated; billable event to "
                                "M20"),
                            (5, "Repair warranty applied and printed")]),
            ],
            "columns": ["Intake", "Diagnose", "Quote", "Repair", "Check",
                        "Hand over"],
            "exhibit_title": "A walk-in repair, from counter to collection",
            "exhibit_sub": "Six steps, five people, one record",
            "caption": "The commonest journey in the company",
            "table": [
                ["1", "Counter agent",
                 "Customer found by phone number; device registered inline; "
                 "entitlement returns out-of-warranty; condition photographed; "
                 "job sheet printed with the tracking link."],
                ["2", "Technician",
                 "Guided diagnosis records a failed keyboard ribbon and a "
                 "degraded battery; both get standard fault codes and "
                 "photographs."],
                ["3", "System and customer",
                 "Estimate requested from M36, returned at BDT 4,200 and BDT "
                 "7,800, issued by SMS. Above the BDT 5,000 threshold, so "
                 "approval is now mandatory. The customer accepts one line and "
                 "rejects the other."],
                ["4", "Technician",
                 "Keyboard replaced. Time and parts posted; the order moves "
                 "itself to quality check."],
                ["5", "QC inspector",
                 "Level 2 display and input checklist passed. Service report "
                 "generated; billable event sent to M20; the customer is told "
                 "the device is ready."],
                ["6", "Counter agent",
                 "Identity verified, accessories confirmed, signature "
                 "captured. Repair warranty applied and printed on the "
                 "report."],
            ],
            "outcome":
                "One record from first contact to settlement. The customer was "
                "told four times what was happening and telephoned nobody. The "
                "branch's turnaround, first-pass quality and approval "
                "conversion figures all moved by exactly one job, without "
                "anybody filling in a return.",
        },
        {
            "title": "A warranty job, paid by the brand",
            "narrative": [
                "Commercially the most important variant, because this is "
                "where the company has historically lost money. A warranty job "
                "costs 1000FiX labour and parts, and the brand only reimburses "
                "against a complete evidence pack submitted inside their "
                "window. Compiling that pack by hand, weeks later, from paper, "
                "is why claims have been missed.",
                "In M01 the pack assembles itself as the job proceeds.",
            ],
            "lanes": [
                ("Customer", [(0, "Reports a dead monitor under brand "
                                  "warranty"),
                              (4, "Collects; signs")]),
                ("Counter agent", [(0, "Serial scanned; warranty confirmed "
                                       "active")]),
                ("Technician", [(1, "Before photographs; fault coded to the "
                                    "brand's scheme"),
                                (2, "Panel replaced; after photographs")]),
                ("QC inspector", [(3, "Checklist passed")]),
                ("System", [(0, "Entitlement: brand warranty. No charge to "
                                "customer"),
                            (3, "Evidence pack assembled"),
                            (4, "Claim-eligible event to M09 within 24 hours")]),
            ],
            "columns": ["Intake", "Diagnose", "Repair", "Check", "Hand over"],
            "exhibit_title": "A warranty job and the claim it generates",
            "exhibit_sub": "The evidence pack is built as the work happens",
            "caption": "How a warranty claim stops being a paper exercise",
            "table": [
                ["1", "Counter agent",
                 "Serial scanned; M09 confirms brand warranty active at the "
                 "request date. Order type set to warranty; the customer is "
                 "told there is no charge."],
                ["2", "Technician",
                 "Before photographs captured with time and location. Fault "
                 "coded using the standard scheme the brand recognises."],
                ["3", "Technician",
                 "Panel replaced; part serial recorded; after photographs "
                 "captured."],
                ["4", "QC inspector",
                 "Checklist passed. Because the order type is warranty, the "
                 "system will not allow closure without both photograph sets."],
                ["5", "System",
                 "On delivery, a claim-eligible event goes to M09 with the "
                 "evidence pack reference attached — inside 24 hours of "
                 "completion, not 30 to 90 days later."],
            ],
            "outcome":
                "The specification attributes BDT 100 lac a year of "
                "recoverable warranty revenue to closing this gap. M09 "
                "realises it; M01 is what makes it possible, by having the "
                "evidence already assembled on the day the work is done.",
        },
        {
            "title": "A corporate contract visit, planned by the system",
            "narrative": [
                "Nobody raises this job. A contract maintenance plan does, at "
                "the right lead time, and it arrives in the queue looking like "
                "any other order.",
            ],
            "lanes": [
                ("Contract (M08)", [(0, "Quarterly preventive plan falls due")]),
                ("System", [(0, "Service order created; type set to AMC; "
                                "entitlement resolved from the contract"),
                            (1, "Visit slot proposed to the customer"),
                            (4, "Billable event suppressed — covered by "
                                "contract")]),
                ("Account manager", [(1, "Confirms the window with the "
                                         "customer")]),
                ("Dispatcher", [(2, "Assigns a technician with the right skill "
                                    "and parts")]),
                ("Technician", [(3, "Thirty devices checked; outcomes recorded "
                                    "per device")]),
            ],
            "columns": ["Plan due", "Schedule", "Assign", "Visit", "Close"],
            "exhibit_title": "A preventive visit that nobody had to remember",
            "exhibit_sub": "From contract plan to completed site visit",
            "caption": "Contract-generated work, end to end",
            "table": [
                ["1", "System",
                 "The quarterly preventive plan on the contract falls due. A "
                 "service order is created with order type AMC and entitlement "
                 "already resolved to contract cover."],
                ["2", "Account manager",
                 "A visit window is proposed to the customer and confirmed. "
                 "The SLA applied is the contract's, not the walk-in default."],
                ["3", "Dispatcher",
                 "Assigned to a technician with the right certification and "
                 "the consumables on the van."],
                ["4", "Technician",
                 "One visit, thirty devices, each with its own recorded "
                 "outcome under the shared batch reference."],
                ["5", "System",
                 "No invoice is raised — the work is covered — but the full "
                 "cost rolls up to the order so contract profitability is "
                 "measurable."],
            ],
            "outcome":
                "Preventive work stops depending on somebody keeping a diary, "
                "and the company finds out whether its contracts actually make "
                "money, because the cost of servicing them is attached to the "
                "orders they generate.",
        },
        {
            "title": "A job that goes wrong, and is caught",
            "narrative": [
                "The interesting cases are the ones that fail. This walkthrough "
                "follows a job that misses its part, misses its technician and "
                "still lands inside its promise, because three separate "
                "automatic behaviours intervened.",
            ],
            "lanes": [
                ("Technician", [(1, "Finds the part is out of stock network "
                                    "wide"),
                                (4, "Completes the repair")]),
                ("System", [(1, "Hold applied; clock stops; sourcing request "
                                "raised"),
                            (2, "Revised commitment sent to the customer"),
                            (3, "Part arrives; hold released; clock resumes"),
                            (3, "50% escalation fires — job unassigned")]),
                ("Dispatcher", [(3, "Reassigns within ten minutes")]),
                ("Branch manager", [(3, "Sees the escalation; no action "
                                        "needed")]),
            ],
            "columns": ["Diagnose", "Blocked", "Inform", "Recover", "Complete"],
            "exhibit_title": "Three interventions on one job",
            "exhibit_sub": "A hold, a proactive notice and an escalation",
            "caption": "What the module does when a job starts to fail",
            "table": [
                ["1", "Technician",
                 "Diagnosis complete, part identified, and the part is out of "
                 "stock everywhere in the network."],
                ["2", "System",
                 "A sourcing request is raised in M15, the order goes on hold "
                 "with the reason recorded, and the SLA clock stops at eleven "
                 "hours elapsed."],
                ["3", "System",
                 "A proactive delay notice goes to the customer with a revised "
                 "commitment, the same afternoon, without anybody being asked "
                 "to send it."],
                ["4", "System and dispatcher",
                 "The part arrives; the hold releases and the clock resumes at "
                 "eleven hours. The original technician is now on another "
                 "site, so the 50 per cent escalation fires and the dispatcher "
                 "reassigns."],
                ["5", "Technician",
                 "Repair completed at nineteen working hours against a 48-hour "
                 "promise."],
            ],
            "outcome":
                "Nothing here required a heroic individual. A hold that stops "
                "the clock, a notice the customer did not have to ask for, and "
                "an escalation that fired at half time rather than after the "
                "breach. The branch's SLA figure records a job kept, and the "
                "reason it was nearly lost is on the record for anyone "
                "analysing causes.",
        },
        {
            "title": "A device that comes back",
            "narrative": [
                "The job nobody wants and everybody has. A customer returns "
                "with the same fault three weeks after collection. What matters "
                "is not that it happened — it will — but that the company can "
                "see it, cost it and learn from it.",
            ],
            "lanes": [
                ("Customer", [(0, "Returns with the same fault"),
                              (4, "Collects; no charge")]),
                ("Counter agent", [(0, "Searches by serial; finds the closed "
                                       "order")]),
                ("System", [(0, "Same device, same fault, inside 30 days — "
                                "rework flag raised automatically"),
                            (1, "Original order reopened and linked; no charge "
                                "applied"),
                            (4, "Quality event emitted to M23 with attribution")]),
                ("Technician", [(2, "Reworks; root cause recorded")]),
                ("Quality manager", [(3, "Sees the rework in the weekly "
                                         "analysis")]),
            ],
            "columns": ["Return", "Reopen", "Rework", "Analyse", "Hand over"],
            "exhibit_title": "Rework, made visible for the first time",
            "exhibit_sub": "The system flags it; nobody has to admit to it",
            "caption": "How a repeat failure is detected and attributed",
            "table": [
                ["1", "Counter agent",
                 "The device is found by serial. The system sees the same "
                 "device and the same fault category inside thirty days and "
                 "raises the rework flag before the agent has typed anything "
                 "else."],
                ["2", "System",
                 "The original order is reopened inside the repair-warranty "
                 "window and the two are linked. The order carries no charge "
                 "to the customer."],
                ["3", "Technician",
                 "The rework is done and the root cause is recorded against "
                 "the standard list."],
                ["4", "System",
                 "The quality event goes to M23 attributed to the original "
                 "technician, the original branch and the root cause."],
                ["5", "Quality manager",
                 "It appears in the weekly rework analysis by technician, "
                 "branch, model and fault code."],
            ],
            "outcome":
                "Rework is currently unmeasured at 1000FiX, which means it "
                "cannot be reduced and nobody can be fairly held to account "
                "for it. Once it is a number, coaching is aimed at a pattern "
                "and the argument about whose fault it was is settled by the "
                "record.",
        },
    ],

    # ============================================ 9. putting it together
    "s9t_lede":
        "Five different jobs, and the same six habits underneath all of them.",

    "s9t_intro": [
        "The walkthroughs deliberately covered very different work: a walk-in "
        "repair paid by a customer, a warranty job paid by a brand, a "
        "preventive visit nobody raised, a job that nearly failed, and a "
        "device that came back. Read together they show what the module is "
        "actually changing, which is not really the software — it is the "
        "habits.",

        "None of the five depended on somebody being unusually diligent. That "
        "is the point worth carrying away. The evidence was captured because "
        "the screen asked for it; the customer was told because the system "
        "told them; the escalation fired because a clock reached half time. "
        "Where the old way of working depended on individuals remembering, the "
        "new way depends on the record.",
    ],

    "s9t_table": [
        ["The record is made once, at the start",
         "Every walkthrough. The counter, the alert, the contract plan and the "
         "returning customer all created or found one order.",
         "Nothing downstream has to be reconciled, because there is nothing to "
         "reconcile it against."],
        ["The commercial position is settled before the work",
         "Walkthroughs one, two and three: entitlement resolved at intake; the "
         "estimate approved before any part was issued.",
         "The argument at collection disappears, because the answer was given "
         "at the counter."],
        ["Evidence is captured while it is cheap",
         "Walkthrough two: photographs taken as part of the job, not "
         "assembled weeks later for a claim.",
         "The warranty claim, the dispute and the quality analysis all draw on "
         "the same evidence, gathered once."],
        ["The customer is told before they ask",
         "Walkthroughs one and four: four milestone messages and a proactive "
         "delay notice, none of them sent by a person.",
         "Three in five status calls stop happening, and the ones that remain "
         "are about something real."],
        ["Failure is caught while it can still be fixed",
         "Walkthrough four: a hold that stopped the clock, and an escalation "
         "at 50 per cent rather than after the breach.",
         "A manager intervenes with time in hand instead of apologising "
         "afterwards."],
        ["What went wrong becomes a number, not an argument",
         "Walkthrough five: rework detected automatically and attributed to "
         "the original job, technician, branch and root cause.",
         "Coaching aims at a pattern; nobody has to accuse anybody."],
    ],

    "s9t_close":
        "Every one of the five stories works because the record was made "
        "properly at the start. Almost everything that goes wrong with a "
        "service order can be traced back to the first three minutes at the "
        "counter — which is why intake has fifteen functions and why this "
        "guide book spends so long on it.",

    # ============================================ 10. rules
    "s8_lede":
        "Eighteen rules the system enforces. Most of them will stop you doing "
        "something, and every one of them exists because doing it cost the "
        "company money.",

    "s8_intro": [
        "A business rule in this system is not advice. Where a rule is marked "
        "as a hard block, the system refuses the action outright and there is "
        "no override — not for a manager, not for a director. Where it is an "
        "approved override, a named role can authorise the exception and the "
        "authorisation is recorded. Where it is computed, the system works the "
        "answer out and there is nothing to override.",

        "That firmness is deliberate. A rule that can be waived by whoever is "
        "under pressure at the time is not a rule. The table below gives the "
        "plain reading of each one: what you will not be able to do, why, and "
        "what to do instead. Appendix A.4 gives the same rules in the form the "
        "specification states them, with their identifiers and classes.",
    ],

    "s8_rules": [
        ["Create an order without identifying the device",
         "Everything downstream — warranty, history, quality analysis, the "
         "brand claim — hangs off the device record. An order with no device "
         "is a dead end.",
         "Register the device inline during intake. It takes about fifteen "
         "seconds and does not leave the screen."],
        ["Create a warranty order when warranty was not active on the day the "
         "customer asked",
         "The brand will reject the claim, and the company absorbs the cost.",
         "Check the entitlement result on screen. If it says out of warranty, "
         "say so at the counter, before the job sheet prints."],
        ["Create an AMC order for a device that is not on the contract's "
         "covered-asset list",
         "Work would be done free against a contract that does not cover it.",
         "Ask the account manager to add the device to the contract, or raise "
         "it as a chargeable order."],
        ["Mark a device ready without a passed quality check",
         "This is the single control that stops unchecked work reaching a "
         "customer, and it protects the ISO 9001 certification that wins "
         "corporate tenders.",
         "Complete the checklist. If it fails, the order goes back to in "
         "progress, which is the correct outcome."],
        ["Raise an invoice for an order that has not been delivered",
         "Billing for work the customer has not received is the fastest way to "
         "lose one.",
         "Complete the handover. The billable event fires by itself."],
        ["Start work above BDT 5,000 without documented customer approval",
         "Disputes over unapproved charges are unwinnable without a record.",
         "Issue the estimate and wait for the answer. The customer can approve "
         "from their phone in seconds."],
        ["Start work above BDT 25,000 without the branch manager as well",
         "High-value work needs a second pair of eyes on both the diagnosis "
         "and the commercial position.",
         "Route it for internal approval; it appears in the manager's queue "
         "immediately."],
        ["Assign brand warranty work to an uncertified technician",
         "The brand voids the claim, and the company pays for the repair.",
         "Check the certification requirement on the order and assign someone "
         "who holds it."],
        ["Record the independent quality check on your own repair above the "
         "threshold",
         "A check by the person who did the work is not a check.",
         "Hand it to another inspector. The system will not accept it "
         "otherwise."],
        ["Close a warranty order without before and after photographs",
         "The claim pack is incomplete and the brand will not pay.",
         "Capture both sets while the device is in front of you. Doing it "
         "later is not possible."],
        ["Declare a device beyond economic repair on one person's word",
         "It is a decision the customer may well challenge.",
         "Capture photographic evidence and get a second technician to "
         "confirm."],
        ["Extend an estimate that has expired",
         "Prices and part availability move. An extended estimate quietly "
         "commits the company to yesterday's cost base.",
         "Re-issue a fresh estimate. It takes one action."],
        ["Stop the SLA clock without an approved hold reason",
         "If the clock could be stopped at will, the promise would mean "
         "nothing.",
         "Choose from the governed list of hold reasons. If none of them "
         "fits, the job is not on hold."],
        ["Keep an uncollected device indefinitely without process",
         "Storage costs money and there is a statutory position to protect.",
         "The system runs the reminder sequence and starts the abandonment "
         "process with the statutory notice after thirty days. Let it."],
        ["Reopen a job outside the repair-warranty period",
         "Outside the window it is a new job, at a price.",
         "Raise a new order. Inside the window, reopening is allowed and links "
         "automatically as rework."],
        ["Record customer data-access notes without explicit consent",
         "It is personal data on somebody else's device.",
         "Ask, record the consent, and let the system purge the note at "
         "handover as it is designed to."],
        ["Give a Privilege Gold or Diamond member a lower priority",
         "The membership was sold on that promise.",
         "Nothing to do — the system applies priority-1 automatically, "
         "whatever the service type."],
        ["Assume rework will not be noticed",
         "The same device with the same fault inside thirty days is detected "
         "and linked automatically.",
         "Record the root cause honestly. The analysis is aimed at causes, not "
         "at individuals."],
    ],

    "s8_note":
        "If a rule is genuinely stopping legitimate work, that is a change to "
        "raise, not a rule to work around. Appendix B says how. Inventing a "
        "workaround — a second order, a wrong order type, a fictional hold "
        "reason — corrupts the numbers everybody else is relying on.",

    # ============================================ 9. automation
    "s9_lede":
        "Twelve things the module does on its own. Between them they are the "
        "difference between a system that records work and a system that "
        "helps do it.",

    "s9_intro": [
        "Most of what makes M01 feel different from a spreadsheet is not a "
        "feature anybody clicks. It is the work that happens between clicks: "
        "the clock that starts itself, the estimate that is requested without "
        "being asked for, the customer who is told before they wonder, the "
        "escalation that fires at half time.",

        "Each automatic behaviour also has a defined failure path. If the "
        "system cannot do the automatic thing — an estimate cannot be built, "
        "a part cannot be found anywhere — it does not fail silently. It "
        "creates a task for a human being and says what it could not do.",
    ],

    "automation_groups": [
        ("When an order changes state", 6,
         "Entitlement evaluated, clocks started, estimate requested, parts "
         "reserved, report generated"),
        ("When a promise is at risk", 3,
         "Escalation, automatic re-prioritisation, proactive delay notice"),
        ("On a timetable", 2,
         "Uncollected-device reminders at 3, 7, 15 and 30 days; the "
         "abandonment process"),
        ("When a pattern is detected", 1,
         "Same device, same fault, inside thirty days — flagged as rework"),
    ],

    "s9_table": [
        ["Evaluates entitlement, assigns the SLA policy, starts the clocks, "
         "sends the acknowledgement and puts the job in the dispatch queue",
         "An order is confirmed",
         "The customer gets an acknowledgement; the dispatcher sees a new job"],
        ["Requests a draft estimate from M36 using the fault code",
         "A diagnosis is recorded",
         "The technician and the service advisor"],
        ["Starts the approval timer, reminds at 24 and 48 hours, and expires "
         "the estimate at the configured limit",
         "An estimate is issued",
         "The customer, and the branch if it expires"],
        ["Reserves the parts in M15, releases the work order and notifies "
         "whoever it is assigned to",
         "The customer approves",
         "The assigned technician; the inventory team"],
        ["Raises a sourcing request, puts the order on hold and sends the "
         "customer a revised commitment",
         "A part is unavailable across the whole network",
         "The customer, the inventory manager and the branch"],
        ["Generates the service report, sends the billable event to M20 and "
         "tells the customer the device is ready",
         "Quality check passed",
         "The customer, finance and the branch"],
        ["Sends the claim-eligible event to M09 with the evidence pack "
         "reference",
         "A warranty order is delivered",
         "The warranty claims officer"],
        ["Escalates to the branch manager, then to the operations manager if "
         "nobody acknowledges",
         "An order sits idle beyond its threshold",
         "The branch manager, then the operations manager"],
        ["Raises the rework flag, links the two orders and emits the quality "
         "event",
         "The same device and fault category inside thirty days",
         "The quality manager and the original branch"],
        ["Runs the reminder sequence at 3, 7, 15 and 30 days, then starts the "
         "abandonment process with the statutory notice",
         "A device is ready and uncollected",
         "The customer and the branch manager"],
        ["Sends a proactive delay notice with a revised commitment",
         "The promised date is going to be missed",
         "The customer, before they notice"],
        ["Sends the post-service survey",
         "A configured interval after delivery",
         "The customer; results reach the customer experience team"],
    ],

    # ============================================ 10. permissions
    "s10_lede":
        "Sixteen roles, and a small number of things that only one of them can "
        "do. Most disputes about the system turn out to be disputes about this "
        "page.",

    "s10_intro": [
        "Permissions in M01 work on two axes at once: what you may do, and "
        "which orders you may do it to. A branch manager has full rights over "
        "their own branch and none over anybody else's. A technician may "
        "update only the orders assigned to them. A customer may see only "
        "their own.",

        "Three restrictions are worth calling out because they catch people. "
        "Cost, total cost and margin are visible only to senior operational "
        "and finance roles — a technician does not see what the job cost the "
        "company. Internal notes are never shown on any external portal, to "
        "any customer, corporate user or marketplace seller. And the "
        "technician who did a repair cannot record the independent quality "
        "check on it above the value threshold; that is a segregation of "
        "duties rule and the system holds it absolutely.",
    ],

    "permissions": {
        "roles": [
            "Operations Director", "Branch Manager", "Dispatch Manager",
            "Service Centre Agent", "Workshop Supervisor", "Technician",
            "Quality Manager", "Warranty Claims Officer", "Finance Officer",
            "Contact Centre Agent", "Customer", "Corporate Portal User",
        ],
        "actions": ["Create an order", "Change priority", "Approve a "
                    "high-value estimate", "Pass quality", "Release the "
                    "device", "Reopen a closed job", "See cost and margin"],
        "marks": [
            ["y", "y", "y", "v", "y", "y", "y"],   # Operations Director
            ["y", "y", "y", "v", "y", "a", "y"],   # Branch Manager
            ["y", "y", "", "", "v", "", ""],       # Dispatch Manager
            ["y", "", "", "", "y", "", ""],        # Service Centre Agent
            ["y", "y", "", "v", "y", "", "y"],     # Workshop Supervisor
            ["", "", "", "", "", "", ""],          # Technician
            ["", "", "", "y", "v", "", ""],        # Quality Manager
            ["", "", "", "", "", "", ""],          # Warranty Claims Officer
            ["", "", "", "", "", "", "y"],         # Finance Officer
            ["y", "", "", "", "", "", ""],         # Contact Centre Agent
            ["", "", "", "", "", "", ""],          # Customer
            ["y", "", "", "", "", "", ""],         # Corporate Portal User
        ],
        "sub": "The seven actions that come up most often in an argument",
    },

    "s10_roles": [
        ["Operations Director",
         "Running service delivery across every branch",
         "Overriding priority anywhere in the estate, and seeing cost and "
         "margin on any order"],
        ["Branch Manager",
         "Running one branch: workload, ageing, uncollected devices, value",
         "Approving estimates above BDT 25,000 for their branch, and "
         "authorising a reopen outside the normal path"],
        ["Dispatch Manager",
         "Deciding who does what, and rescuing jobs at risk",
         "Reassigning and re-prioritising across their zones"],
        ["Service Centre Agent",
         "Taking jobs in and handing them back",
         "Nothing exclusive — but they are the only role most customers ever "
         "meet"],
        ["Workshop Supervisor",
         "Loading the bench and releasing finished work",
         "Moving work between technicians inside their own workshop"],
        ["Technician",
         "Doing the work and recording it",
         "Nothing exclusive. Deliberately: a technician records, and the "
         "system decides"],
        ["Quality Manager",
         "Passing quality checks and owning the rework analysis",
         "Recording the independent quality check, which nobody else may do"],
        ["Warranty Claims Officer",
         "Reading completed warranty work and its evidence",
         "Read-only across all warranty orders, wherever they were raised"],
        ["Finance Officer",
         "Confirming what is billable",
         "Read-only across everything, including cost and margin"],
        ["Contact Centre Agent",
         "Answering the phone and raising jobs taken by it",
         "Creating orders for customers they cannot see in person"],
        ["Customer",
         "Watching their own job and answering the estimate",
         "Accepting or rejecting an estimate — nobody may do that for them"],
        ["Corporate Portal User",
         "Raising and tracking their own company's fleet",
         "Bulk upload of many devices at once"],
    ],

    "s10_note":
        "Access is granted by role, never by person. If somebody needs to see "
        "something they cannot see, the question to answer is which role they "
        "should hold — not whether to make an exception for them.",

    # ============================================ 11. measurement
    "s11_lede":
        "Ten reports and twelve measures. Several of them are numbers 1000FiX "
        "has never been able to produce at all.",

    "s11_intro": [
        "The most striking thing about the measures below is how many carry a "
        "baseline of 'unmeasured'. Turnaround time is not currently measured. "
        "Rework is not measured. SLA compliance is not measured. Quality "
        "first-pass rate is not measured. Revenue leakage is unknown. That is "
        "not a criticism of anybody; you cannot measure what is written on "
        "paper in fifty-one places.",

        "Where a baseline is unmeasured, the specification says so and states "
        "no starting figure. That is deliberate: a target against an unknown "
        "baseline cannot be assessed as met or missed, and inventing a "
        "starting number to make a chart look complete would poison the "
        "business case. The first job of Wave 1 is to establish the "
        "baselines honestly, and the targets below are the Wave 8 positions.",
    ],

    "s11_reports": [
        ["Live operations board",
         "What is open right now, how old it is, what is at risk and what it "
         "is worth",
         "Dispatch, branch and operations managers, continuously"],
        ["Work-in-progress ageing",
         "Where jobs are getting stuck, and how long each state is taking",
         "The Operations Director, daily"],
        ["SLA compliance",
         "Are we keeping our promises, and where are we not",
         "Operations and quality, daily and monthly"],
        ["Rework analysis",
         "Which technicians, branches, models and faults generate repeat work",
         "The Quality Manager and HR, weekly"],
        ["Turnaround time analysis",
         "How long jobs actually take, by service type and delivery mode, "
         "against what was promised",
         "The Operations Director, weekly"],
        ["Uncollected devices",
         "What is sitting in the store room, how long it has been there, and "
         "what is being done",
         "Branch managers, daily"],
        ["Channel performance",
         "Which of the twelve ways in actually work, and what each costs",
         "The Chief Commercial and Chief Technology Officers, monthly"],
        ["Approval conversion",
         "How often customers say yes to an estimate, by value band, device "
         "and branch",
         "The Chief Commercial Officer, weekly"],
        ["Fault patterns",
         "Which brands, models and components fail, and how",
         "Quality, and shared with brand partners, monthly"],
        ["Service order cost and margin",
         "Whether a kind of work makes money",
         "Finance and operations, monthly"],
    ],

    "s11_kpis": [
        ["Service order automation rate",
         "How much of the job lifecycle happens without manual intervention",
         "85 per cent, up from about 20 per cent today"],
        ["Turnaround time, IT equipment",
         "How long a customer waits, end to end",
         "Under 24 hours. Not currently measured at all"],
        ["First-time fix rate",
         "How often the job is finished on the first attempt",
         "88 per cent, up from about 70 per cent"],
        ["Rework rate",
         "How often a device comes back for the same fault",
         "Under 3 per cent. Not currently measured at all"],
        ["SLA compliance",
         "How often we keep the promise we made",
         "96 per cent. Not currently measured at all"],
        ["Quality first-pass rate",
         "How often work passes the check the first time",
         "95 per cent. Not currently measured at all"],
        ["Estimate approval conversion",
         "How often a customer says yes to a quoted repair",
         "78 per cent. Not currently measured at all"],
        ["Devices uncollected beyond 30 days",
         "How much of the store room is dead weight",
         "Under 0.5 per cent. Not currently measured at all"],
        ["Status enquiries deflected",
         "How many 'where is my device?' calls the tracking link removes",
         "80 per cent, from a base of none"],
        ["Revenue leakage",
         "Work delivered and never billed",
         "Under 0.5 per cent. Currently unknown"],
        ["Order creation speed",
         "How long the system takes to create an order",
         "Under half a second, 95 times out of 100"],
        ["Orders created without manual typing",
         "How much intake comes through digital channels",
         "90 per cent, from a base of none"],
    ],

    "dials": [
        ("Jobs delivered inside the promised time", "96%", 0.96),
        ("Repairs right the first time", "88%", 0.88),
        ("Quality checks passed first time", "95%", 0.95),
        ("Status calls removed by self-service", "80%", 0.80),
    ],

    "s11_reading_title": "Reading the live operations board",
    "s11_reading": [
        "The board is the screen most managers will have open all day, and it "
        "repays a few minutes spent learning to read it properly. It shows "
        "every open order in one list, and it can be sorted four ways: by "
        "age, by SLA risk, by value and by state. Each of those answers a "
        "different question, and using the wrong one is the commonest reason "
        "a manager misses something.",

        "Sorting by age answers 'what have we forgotten?'. Sorting by SLA risk "
        "answers 'what will embarrass us today?'. Those are not the same list. "
        "An old job that is on hold with an approved reason is not urgent; a "
        "four-hour-old emergency at 90 per cent of its clock is. Sorting by "
        "value answers 'what is at stake?', and sorting by state answers "
        "'where is the bottleneck?'.",

        "The habit worth forming is to look at SLA risk first thing in the "
        "morning, state through the middle of the day, and age at the end of "
        "the week. Value only when somebody asks.",
    ],
    "s11_reading_table": [
        ["A cluster of jobs sitting in one state",
         "That state is the bottleneck. Usually it is 'awaiting approval' or "
         "'quality check'.",
         "If it is approval, the estimates are going out too slowly or the "
         "reminders are not landing. If it is quality check, there are not "
         "enough inspectors on shift."],
        ["A long tail of old jobs, all on hold",
         "Almost always parts. The clock is stopped so they are not breaching, "
         "but the devices are occupying space and the customers are waiting.",
         "Check the sourcing requests in M15. Consider whether the customers "
         "have had a second revised commitment."],
        ["SLA risk high but ageing normal",
         "The promises are tighter than the work takes — often a contract "
         "service level applied to work the branch is not staffed for.",
         "This is a capacity or a contract question, not a discipline "
         "question. Escalate it as such."],
        ["Ageing high but SLA risk low",
         "Jobs are slow but the promises are generous. Customers are probably "
         "unhappy even though nothing is technically breaching.",
         "Look at turnaround time against the promise, not compliance. The "
         "promise may be the wrong promise."],
        ["A spike in one branch only",
         "A local cause: somebody absent, a bench out of action, a training "
         "gap after a new joiner started.",
         "Compare the branch's rework and first-pass quality figures for the "
         "same period before concluding anything."],
        ["Uncollected devices rising steadily",
         "The reminder sequence is running but customers are not responding. "
         "Often a contact-details problem rather than an apathy problem.",
         "Check the notification history on a sample. If the messages are not "
         "reaching people, fix M33 before chasing the customers."],
    ],

    # ============================================ 12. neighbours
    "s12_lede":
        "M01 reads from thirteen modules and feeds thirteen more. Sixteen "
        "modules cannot work at all without it.",

    "s12_intro": [
        "No module in this system is worth much on its own, and M01 less than "
        "most: it is a coordination record, so almost all of its value is in "
        "what it connects. The exhibit below shows the full picture. The two "
        "tables after it say what would actually break.",

        "The practical reading for somebody working in the business is this. "
        "If the customer master or the asset registry is wrong, M01 is wrong, "
        "and no amount of care at the counter will fix it. And if M01 is down "
        "or its data is poor, field service, the workshop, logistics, "
        "warranty, invoicing and the customer's own tracking view all lose "
        "their reference point at once.",
    ],

    "s12_upstream": [
        ["M33 Party Master", "Who the customer is",
         "No order can be created — customer identification is a hard rule"],
        ["M17 Asset Registry", "Which device this is, and its history",
         "No order can be created; warranty and quality analysis lose their "
         "subject"],
        ["M09 Warranty", "Whether brand or extended cover is active",
         "Entitlement cannot be resolved; warranty jobs get billed to "
         "customers by mistake"],
        ["M08 Contract", "Whether the device is on a covered-asset list, and "
         "at what service level",
         "AMC and managed-service work cannot be typed correctly"],
        ["M36 Quotation", "The estimate for the diagnosed fault",
         "Nothing above the approval threshold can proceed"],
        ["M11 Pricing", "The rates the estimate is built from",
         "Estimates cannot be produced at all"],
        ["M37 Catalogue", "The service catalogue jobs are raised against",
         "Order types and service definitions have no source"],
        ["M15 Inventory", "Whether the parts exist and where",
         "Parts requisition and reservation stop working"],
        ["M29 Identity", "Who the staff member is and what they may do",
         "Nobody can log in or be held accountable for an action"],
        ["M28 Integration", "The channel connections that carry inbound "
         "requests",
         "Nine of the twelve intake channels stop delivering"],
        ["M23 Quality", "The checklists and the quality standards",
         "The quality gate has nothing to check against"],
        ["M55 Workforce", "Who is available, and what they are certified for",
         "Assignment cannot respect skill or certification rules"],
        ["M27 Contact Centre", "Requests taken by telephone",
         "Hotline intake stops"],
    ],

    "s12_downstream": [
        ["M02 Field Service", "The work order for a site visit",
         "No field work can be raised or costed"],
        ["M31 Workshop", "The repair order for the bench",
         "The workshop has no queue"],
        ["M03 Logistics", "The consignment to collect or return a device",
         "Movements lose their reason and their custody trail"],
        ["M15 Inventory", "The parts requirement against a job",
         "Parts are issued with nothing to charge them to"],
        ["M09 Warranty", "The claim-eligible event and the evidence pack",
         "Warranty claims go back to being compiled by hand"],
        ["M20 Receivables", "The billable event on delivery",
         "Delivered work is not invoiced"],
        ["M23 Quality", "Quality and rework events",
         "Rework becomes invisible again"],
        ["M27 Contact Centre", "The status a caller is asking about",
         "Agents cannot answer the commonest question they receive"],
        ["M34 Customer Experience", "The survey trigger and the satisfaction "
                                    "context",
         "Satisfaction cannot be attributed to a job"],
        ["M25 Customer Portal", "The tracking timeline",
         "The self-service view goes dark and the calls come back"],
        ["M12 Analytics", "Volume, turnaround, SLA and rework data",
         "The operational dashboards have no source"],
        ["M26 Intelligence", "The training data for dispatch, duration and "
                             "fault models",
         "Every predictive model in the programme loses its foundation"],
        ["M06 Data Services", "The confidentiality-controlled case record",
         "Data recovery work has no order to hang off"],
    ],

    "s12_close_up": [
        {
            "title": "The relationship that matters most: M01 and M31 Workshop",
            "text": [
                "These two were one module until the current version of the "
                "specification split them, and understanding why is the "
                "quickest route to understanding both. The problem with a "
                "single module was that a service order and a bench repair "
                "answer to different audiences. A customer wants to know "
                "whether their laptop will be ready on Thursday. A workshop "
                "supervisor wants to know that this device needs a Level 3 "
                "technician, that there are four ahead of it, and that the "
                "board rework rig is booked until Wednesday.",

                "Put both in one record and one of the two audiences is always "
                "being shown the wrong thing. Worse, the module becomes the "
                "place every new requirement lands, and it grows until nobody "
                "can change it safely — which is exactly what had happened.",

                "The split gives M01 the customer's question and M31 the "
                "bench's. A service order generates a repair order; the repair "
                "order reports progress, time and parts back; the service "
                "order translates that into something a customer can read. "
                "Neither module has to compromise. In practice this means a "
                "counter agent never needs to understand bench scheduling, and "
                "a workshop supervisor never has to think about what the "
                "customer is being told.",
            ],
        },
        {
            "title": "The relationship that catches people: M01 and M09 "
                     "Warranty",
            "text": [
                "Warranty is where the company loses money quietly, and the "
                "relationship between these two modules is where it is either "
                "recovered or lost. M09 owns the answer to 'is this covered?' "
                "and it owns the claim. M01 owns the evidence.",

                "The direction of the dependency changes during the job. At "
                "intake M01 asks M09 a question: is cover active for this "
                "device on this date? At delivery the flow reverses: M01 tells "
                "M09 that a claimable job has completed, and hands over the "
                "reference to an evidence pack it has already assembled — "
                "before and after photographs, the fault code in the brand's "
                "own scheme, the part serial numbers, the technician's "
                "certification.",

                "That handover happens inside twenty-four hours of the work "
                "finishing. The reason it matters is the current position: "
                "claims are compiled by hand thirty to ninety days later, from "
                "paper, and a material number of them are never submitted at "
                "all. The specification puts BDT 100 lac a year on closing "
                "that gap. None of it is realised by M01 — it is all realised "
                "in M09 — but none of it is possible without M01 having "
                "gathered the evidence while the device was still on the "
                "bench.",
            ],
        },
    ],

    "s12_note":
        "M01 is a dependency of sixteen modules — more than anything else in "
        "the system. That is why it is priority P0 and why it is built in Wave "
        "1. Nothing much else can be delivered before it exists.",

    # ============================================ 13. troubleshooting
    "s13_lede":
        "The things that go wrong most often, what they usually mean, and what "
        "to do about them.",

    "s13_intro": [
        "Almost everything in this section is the system working correctly and "
        "somebody expecting it to work differently. That is worth saying "
        "plainly, because the instinct when a screen refuses is to assume a "
        "fault. Where a genuine fault is possible it is named.",
    ],

    "s13_troubleshooting": [
        ["The system will not let me confirm the order",
         "A device has not been identified, or the customer record is "
         "incomplete.",
         "Register the device inline. If the customer is a duplicate, merge "
         "them in M33 rather than creating another."],
        ["Entitlement says out of warranty but the customer has the receipt",
         "The warranty is being evaluated against the request date, and the "
         "device may not be linked to the right purchase record.",
         "Check the device in M17. If the purchase evidence is genuinely "
         "missing, add it there — do not change the order type by hand."],
        ["I cannot release the device to the customer",
         "The quality check has not been passed, or the handover evidence "
         "is incomplete.",
         "Complete whichever is outstanding. If the checklist has failed, the "
         "device is not ready and should not go out."],
        ["The estimate has expired and the customer now wants to proceed",
         "Estimates expire on purpose; prices and stock have moved.",
         "Issue a fresh estimate. Do not attempt to reopen the old one — the "
         "system will refuse."],
        ["The SLA shows a breach but the delay was the customer's fault",
         "The order was probably not put on hold with an approved reason at "
         "the time.",
         "Apply the hold when the wait starts, not afterwards. A retrospective "
         "hold does not recover the clock, and that is intentional."],
        ["This job is flagged as rework and I do not think it is",
         "The same device and the same fault category have appeared inside "
         "thirty days.",
         "If the fault category is genuinely different, correct the fault code "
         "— the flag follows the code. If it is the same fault, it is rework."],
        ["I cannot see the cost on an order",
         "Cost and margin are restricted to senior operational and finance "
         "roles.",
         "That is correct and not a fault. If you need it for your job, the "
         "question is which role you should hold."],
        ["A customer says they never received the estimate",
         "It was sent to the channel recorded as their preference, which may "
         "be out of date.",
         "Check the notification history on the order, correct the contact "
         "details in M33, and re-issue."],
        ["Two orders exist for the same device and the same problem",
         "Raised twice, probably through two different channels.",
         "Merge them. Do not cancel one — merging preserves both histories."],
        ["The device has been ready for three weeks and nobody has collected it",
         "The reminder sequence has run at 3, 7 and 15 days.",
         "Nothing, yet. At thirty days the abandonment process starts "
         "automatically with the statutory notice. Let it run."],
        ["The technician I want is not on the assignment list",
         "They are not certified for that brand's warranty work.",
         "Assign somebody who is. Certification is held in M55 and is a hard "
         "rule here."],
        ["The tracking link does not work for the customer",
         "The token may have expired, or the link was mistyped from a printed "
         "job sheet.",
         "Re-issue the link from the order. If it still fails, that is a "
         "genuine fault — report it."],
    ],

    "s13_faq": [
        ["Can I change the order type after the job has started?",
         "Only for corrections, and it is recorded. The order type drives who "
         "pays, which rules apply and what the customer has already been told, "
         "so changing it mid-job is a significant act rather than a tidy-up."],
        ["What happens if the customer never answers the estimate?",
         "They are reminded at 24 and 48 hours, and the estimate expires at "
         "the configured limit. The order stays open and the branch gets a "
         "follow-up task; nothing is lost."],
        ["Who decides the promised turnaround?",
         "The SLA policy does, from the service type, business line, brand, "
         "customer tier, contract and priority. Nobody types a date."],
        ["Can I give a customer a better promise than the system's?",
         "You can raise the priority if your role allows it, and the reason is "
         "recorded. You cannot simply type a different date, because the whole "
         "point of the clock is that it is not negotiable after the fact."],
        ["My branch's SLA figure looks wrong. Who do I ask?",
         "Start with the SLA compliance report, which shows breach causes. "
         "Most apparent breaches are holds that were applied late. If the "
         "report and your records genuinely disagree, raise it — see "
         "Appendix B."],
        ["Does the customer see the internal notes?",
         "Never. Internal notes are not exposed to any external portal, to any "
         "customer, corporate user or marketplace seller. The system enforces "
         "this rather than relying on staff discretion."],
        ["What is the difference between the brand's warranty and our repair "
         "warranty?",
         "The brand's warranty covers the product as manufactured. Our repair "
         "warranty covers the work we did. A device can be outside the brand's "
         "warranty and inside ours."],
        ["Why can I not pass quality on my own repair?",
         "Above the value threshold it is a segregation of duties rule. A "
         "check by the person who did the work is not an independent check, "
         "and the certification the company holds depends on it being one."],
        ["Where do I find a job if I only have the customer's phone number?",
         "Universal search takes a phone number, an order number, a serial, a "
         "name or free text, including Bengali, and returns results in well "
         "under a second."],
        ["What happens to a job when a branch closes for a public holiday?",
         "The SLA clock understands the working calendar. Business hours and "
         "holidays do not count against the promise."],
    ],

    # ============================================ 14. worth
    "s14_lede":
        "What the specification says this module is worth, and — just as "
        "importantly — what it declines to put a number on.",

    "s14_intro": [
        "Three of the benefits below carry a monetary figure and the fourth "
        "does not. That is worth pausing on. Rework reduction is obviously "
        "valuable: every percentage point avoided is roughly one per cent of "
        "job volume not being done twice. But rework is currently unmeasured, "
        "so there is no baseline to reduce from, and the specification "
        "explicitly refuses to state a figure until Wave 2 baselining is done. "
        "No number should be carried into the business case before then.",

        "That discipline runs through the whole programme. Where a baseline "
        "exists, a target is set against it. Where it does not, the document "
        "says so rather than inventing one.",
    ],

    "benefits": [
        ("Warranty revenue recovered", 100, "BDT 100 lac/yr"),
        ("Customer retention protected", 78, "BDT 78 lac/yr"),
        ("Administrative labour saved", 62, "BDT 62 lac/yr"),
    ],
    "benefits_note": ("Rework reduction is excluded: the baseline is "
                      "unmeasured, so no figure is claimed."),

    "s14_benefits": [
        ["Warranty revenue recovered",
         "The claim is created automatically when a warranty order is "
         "delivered, with the evidence pack already assembled — closing the 30 "
         "to 90 day submission delay that currently loses claims",
         "Enables BDT 100 lac a year. M09 realises it; M01 makes it possible"],
        ["Administrative labour saved",
         "No more double entry between paper, spreadsheet and accounts; "
         "invoicing and notification happen by themselves",
         "BDT 62 lac a year across the estate"],
        ["Customer churn reduced",
         "Transparency and proactive notification; satisfaction measured; "
         "complaints traceable to a job",
         "Contributes to BDT 78 lac a year of retained revenue"],
        ["Hotline calls deflected",
         "The tracking link and milestone messages remove the reason for the "
         "call",
         "60 per cent fewer status enquiries, releasing contact centre "
         "capacity"],
        ["Revenue leakage closed",
         "No completed job can be closed without a billable event",
         "Delivered-but-unbilled work falls from unknown to under 0.5 per "
         "cent"],
        ["Rework reduced",
         "Rework becomes visible and attributable for the first time; root "
         "causes reach the quality module",
         "No figure stated. The baseline is unmeasured and will not be known "
         "until Wave 2"],
        ["ISO 9001 defensibility",
         "A documented, traceable process with enforced quality gates",
         "Protects the certification that wins corporate tenders"],
    ],

    "s14_soft": [
        ["Institutional memory",
         "Device and customer history stops living in a technician's head or a "
         "branch drawer. When somebody leaves, what they knew stays."],
        ["Fair measurement of people",
         "Technician performance becomes measurable, which means it can be "
         "argued about on evidence instead of impression. That protects good "
         "technicians as much as it exposes poor ones."],
        ["Disputes settled by record",
         "Intake condition photographs and a signed handover settle an "
         "argument in seconds that currently takes a week and costs "
         "goodwill."],
        ["Ready for an audit",
         "Traceable records support tax, brand-partner and certification "
         "audits without a scramble."],
        ["Change becomes cheap",
         "A configurable state machine means a new business line is a "
         "configuration exercise, not a project."],
        ["A foundation for the intelligent modules",
         "Every predictive model the programme plans — dispatch, duration, "
         "fault classification, quality risk — trains on M01 data. Without it "
         "they have nothing to learn from."],
    ],

    "s14_close":
        "M01 does not make the company money directly. It makes it possible to "
        "know what the company did, which turns out to be the precondition for "
        "almost everything else: claiming from the brand, billing the "
        "customer, keeping the promise, spotting the repeat failure, and "
        "training the models that will eventually do some of this work for us.",

    # ============================================ 17. learning it
    "s17_lede":
        "A fortnight, in about six hours of actual effort, spread out. Nobody "
        "needs to learn seventy functions before they start.",

    "s17_intro": [
        "M01 is large, but the part any one person uses is not. A counter "
        "agent touches perhaps fifteen functions; a technician about ten; a "
        "branch manager mostly reads. The plan below is written so that you "
        "are useful on the first afternoon and confident inside two weeks, "
        "without anybody sitting through a course on functions they will "
        "never use.",

        "The order matters more than the hours. Learn to create a clean record "
        "before anything else, because almost every problem later in the job "
        "traces back to intake. Learn to find things second, because that is "
        "what you will spend most of your day doing. Everything else can be "
        "picked up as it arises, with this book open.",
    ],

    "s17_plan": [
        ["Before you start",
         "Read section 1, then find yourself in section 2, then read the "
         "walkthrough in section 8 that matches your job.",
         "20 minutes",
         "Explain what the module is for and where your part of it sits"],
        ["Day one, morning",
         "Watch somebody take three jobs in at the counter. Do not touch "
         "anything. Notice how long entitlement takes to appear.",
         "1 hour",
         "Recognise a clean intake when you see one"],
        ["Day one, afternoon",
         "Take a job in yourself, with somebody beside you. Then find it "
         "again by phone number, by serial and by order number.",
         "1 hour",
         "Create a record and find it three ways"],
        ["Day two",
         "Read section 6.1 in full. Then work through the intake screen "
         "deliberately, including the fields you skipped yesterday: accessory "
         "log, condition photographs, symptom taxonomy.",
         "45 minutes",
         "Take a job in without help"],
        ["Day three",
         "Read section 10. Deliberately try to do three things the system "
         "will refuse, and read the message it gives you.",
         "30 minutes",
         "Recognise a rule rather than assuming a fault"],
        ["End of week one",
         "Read section 7 — the journey of a job — and follow one of your own "
         "jobs all the way through on screen.",
         "30 minutes",
         "Say where any job is and what has to happen next"],
        ["Week two, early",
         "Read section 11. Notice which of the messages your customers "
         "received were sent by a person and which were not.",
         "20 minutes",
         "Stop doing by hand what the system already does"],
        ["Week two, middle",
         "Read section 15 and skim section 13. Save the two list views you "
         "will use every morning.",
         "40 minutes",
         "Diagnose a problem before escalating it"],
        ["End of week two",
         "Read section 18 and keep it. Read section 14 if you work with "
         "another department.",
         "20 minutes",
         "Work unsupervised"],
    ],

    "s17_check_intro":
        "You have got it when you can do all of these without opening this "
        "book. Most people reach this point inside three weeks of real work.",

    "s17_checks": [
        "Take a job in for a customer you have never met, on a device we have "
        "never seen, in under four minutes",
        "Say who pays before the customer asks",
        "Find any job from any one piece of information a customer can "
        "remember",
        "Explain to a customer, in their own language, what stage their job is "
        "at and what happens next",
        "Recognise when the system is enforcing a rule rather than "
        "malfunctioning, and say which rule",
        "Put a job on hold for the right reason, and know why the wrong reason "
        "matters",
        "Read your branch's SLA and rework figures and say what is behind them",
        "Know which three things you must never do, and why each one exists",
    ],

    "s17_note":
        "If you are training somebody else, resist the temptation to show them "
        "everything. The commonest failure in ERP training is teaching the "
        "system instead of the job. Teach intake properly and let the rest "
        "arrive when it is needed.",

    # ============================================ 18. one page
    "s15_lede":
        "The whole module on one page, for a first day, a counter drawer or a "
        "meeting you did not expect to be in.",

    "s15_figures": [
        ("70", "things you can do"),
        ("12", "ways a job arrives"),
        ("14", "lifecycle stages"),
        ("18", "rules enforced"),
        ("12", "automatic behaviours"),
        ("16", "roles with access"),
        ("10", "reports available"),
        ("16", "modules depend on it"),
    ],

    "s15_never": [
        "Create an order without identifying the device",
        "Type a warranty order when warranty was not active on the request "
        "date",
        "Start work above BDT 5,000 without documented customer approval, or "
        "above BDT 25,000 without the branch manager as well",
        "Mark a device ready without a passed quality check",
        "Pass the independent quality check on your own repair above the "
        "threshold",
        "Close a warranty order without before and after photographs",
        "Invoice an order that has not been delivered",
        "Stop the SLA clock without an approved hold reason",
        "Extend an expired estimate — re-issue it instead",
    ],

    "s15_where": CM.where_to_look("M01"),
}
