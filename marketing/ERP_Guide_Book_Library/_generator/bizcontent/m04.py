# -*- coding: utf-8 -*-
"""
M04 — Branch & Front-Desk Operations.

The counter. The module that 150 to 250 agents touch more than any other, and
the first thing a walk-in customer experiences of the whole programme. Its
design constraint is a stopwatch: intake in under three minutes, against about
ten on paper today.

Worked examples name customers, branches and amounts so the reader can picture
the counter. Those details are illustrative; the thresholds, rules and targets
come from the specification.
"""
from bizcontent import common as CM

CONTENT = {

    # ============================================================== front
    "cover_line":
        "The counter. For most customers and most branch staff, this module "
        "is the ERP — and if a walk-in intake takes longer than the paper form "
        "it replaces, they will keep the paper.",

    "cover_inside": [
        ("Part one", "What the module is for, who uses it, and where it stops"),
        ("Part two", "All thirty-two things it lets you do, with worked "
                     "examples and five walkthroughs from a normal day"),
        ("Part three", "The rules, the automatic work, the permissions, the "
                       "measures and the troubleshooting"),
        ("Appendix A", "The full technical register for builders and testers"),
    ],

    "about": CM.about("the Branch and Front-Desk Operations module, M04"),
    "audience": CM.AUDIENCE,
    "how_arranged": CM.HOW_ARRANGED,
    "parts_table": CM.parts_table("M04"),
    "reading_note": CM.READING_NOTE,
    "appendix_note": CM.APPENDIX_NOTE,
    "part1_blurb": CM.PART1_BLURB,
    "part2_blurb": CM.PART2_BLURB,
    "part3_blurb": CM.PART3_BLURB,
    "appendix_blurb": CM.APPENDIX_BLURB,
    "part1_sections": CM.part1_sections(
        "M04", "The kinds of counter visit it has to handle"),
    "part2_sections": CM.part2_sections("The journey of a counter visit"),
    "part3_sections": CM.PART3_SECTIONS,
    "appendix_sections": CM.APPENDIX_SECTIONS,
    "change_control": CM.CHANGE_CONTROL,
    "change_table": CM.change_table("The Branch Operations Lead"),
    "change_note": CM.CHANGE_NOTE,

    # ============================================================ exhibits
    "headline": [
        ("3 min", "the intake time constraint", "ten minutes on paper today"),
        ("150-250", "agents will use it daily", None),
        ("51+", "branches on one process", None),
        ("32", "things the module lets you do", None),
        ("4 hrs", "target time to competence", "two to three days today"),
        ("<1", "cash variance per branch a month", None),
        (">98%", "devices found inside 60 seconds", None),
        ("100%", "intakes with no paper form", "the whole point"),
    ],

    "volume": [
        ("10 min", "intake today", "on paper, with no history to hand"),
        ("3 min", "intake required", "or staff will keep the paper"),
        ("8 min", "the abandonment threshold", "how long people will wait"),
        ("51+", "branches", "with no consistent process today"),
        ("500+", "staff", "every one of them doing it differently"),
    ],
    "volume_title": "Why three minutes is the whole design",
    "volume_sub": "The number the counter succeeds or fails on",
    "volume_caption": "The constraint every other decision in this module "
                      "serves",

    "does": [
        "Tokens, the queue, and the display in the waiting area",
        "Priority for members, appointments and customers who need it",
        "The counter workstation: fast intake, lookup and device recall",
        "Where each device is physically stored, and finding it again",
        "Collection and handover, with the collector's identity verified",
        "Selling parts, accessories, memberships and protection plans",
        "The cash drawer: float, receipts, refunds, petty expense",
        "Taking payment by any method the customer offers",
        "Opening and closing a shift, counting, and handling variance",
        "Recording deposits to the bank",
        "The branch's daily discipline: checklists and handover notes",
        "The branch operations board",
        "Chasing devices nobody has collected",
        "Self-service kiosks, receipts and labels",
        "Showing the data-protection notice at the moment personal data is "
        "captured",
    ],
    "does_not": [
        "The service order itself and its lifecycle, which are M01",
        "The customer master record, which is M33",
        "The wording of the privacy notice and the consent record, which are "
        "M33 — M04 only presents them",
        "Device identity and history, which are M17",
        "Repairing anything, which is M31",
        "Working out a price, which is M11 and M36",
        "Creating the invoice, which is M20",
        "Reconciling the bank and the treasury position, which are M50",
        "Retail stock levels and replenishment, which are M15",
        "The premises, the lease and the maintenance, which are M47",
        "The branch as an organisational unit, which is M30 configuration",
        "Rosters and attendance, which are M55",
        "The online shop checkout, which is M38",
    ],

    "areas_map": [
        ("The queue", 8,
         "Tokens, priority, waiting times and a display people can read."),
        ("The counter itself", 8,
         "Intake in three minutes, collection in seconds, and everything sold "
         "across it."),
        ("Cash and payment", 7,
         "The drawer, the shift, the count, the variance and the deposit."),
        ("Running the branch day", 8,
         "Opening, closing, handover, the board, and the devices nobody has "
         "collected."),
    ],

    "area_bars": [
        ("The queue", 8), ("The counter itself", 8),
        ("Running the branch day", 8), ("Cash and payment", 7),
    ],

    "channels": [
        "A walk-in customer with a broken device",
        "A customer collecting a finished repair",
        "A customer paying an outstanding bill",
        "A pre-booked appointment checking in",
        "A corporate account holder with several devices",
        "Somebody buying an accessory or a membership",
        "A customer chasing a job they cannot track",
        "A Privilege member expecting priority",
    ],
    "channels_hub": "The counter",
    "channels_title": "Eight reasons somebody walks in",
    "channels_sub": ("One token system, one queue and one workstation handle "
                     "all of them"),
    "channels_note": "one token, one place to go",
    "channels_caption": "What actually arrives at a branch counter",

    # ============================================ 1. what it is for
    "s1_lede":
        "M04 runs the counter, and its design constraint is a stopwatch: a "
        "walk-in intake in under three minutes, against about ten on paper "
        "today.",

    "s1_intro": [
        "Walk-in is the highest-volume way customers reach 1000FiX. Every one "
        "of those visits involves a queue, an intake, somewhere to put the "
        "device, a handover later on, and in most cases a cash transaction — "
        "across fifty-one or more locations, with five hundred staff, and no "
        "consistent process between any of them.",

        "The first version of the plan treated the counter as a feature of the "
        "service order module. That was a category error, and correcting it is "
        "why M04 exists separately. The counter has its own rhythm, its own "
        "physical constraints — a storeroom, a drawer, a printer, a queue of "
        "people who can see each other — and its own daily discipline of "
        "opening and closing. Folding all of that into the service order "
        "module would have made the service order module unusable in the one "
        "place it is used most.",

        "The three-minute constraint deserves to be taken literally. If the "
        "software takes longer than the paper it replaces, branch staff will "
        "keep the paper. The data will then be wrong, and every module "
        "downstream inherits that error. Almost every design decision in this "
        "module — search-first lookup, defaulted fields, device recall, "
        "one-screen customer context — exists to serve that one number.",
    ],

    "s1_problem": [
        "At the counter today an agent writes on paper or types into a branch "
        "spreadsheet. There is no way to see the customer's history, so the "
        "customer explains it from memory. There is no way to check warranty, "
        "so the agent promises and hopes. Tracking numbers are inconsistent "
        "between branches, and there is no acknowledgement the customer can "
        "take away that means anything to anyone else in the company.",

        "The queue is an undefined crowd. Nobody knows how long the wait is, "
        "including the staff, and customers who have been standing for eight "
        "minutes start to leave. When a device is finished, finding it in the "
        "storeroom is a search — which is the single most visible source of "
        "embarrassment at a counter.",

        "The cash position is the least controlled part of the whole "
        "operation. Fifty-one branches count their drawers in fifty-one "
        "different ways and report in fifty-one different formats. A variance "
        "is discovered, if at all, days later, by which point nobody can say "
        "which shift it belonged to. That is as unfair to honest staff as it "
        "is convenient for anybody dishonest.",
    ],

    "s1_replaces": [
        ["A paper form and a ten-minute intake",
         "Search-first lookup, device recall, defaulted fields — under three "
         "minutes",
         "About seven minutes released per walk-in customer, across the "
         "highest-volume channel in the business."],
        ["An undefined crowd at the door",
         "A token, a stated wait, and a display in Bengali and English",
         "Customers stop leaving at the eight-minute mark because they cannot "
         "tell how long it will be."],
        ["The customer explaining their own history",
         "Open orders, devices, contracts, entitlements, dues and tier on one "
         "screen",
         "The agent knows more about the visit than the customer does."],
        ["Searching the storeroom",
         "A recorded shelf or bin, retrieved in seconds",
         "Over 98 per cent of devices located inside a minute at collection."],
        ["Counting the drawer and hoping",
         "Every movement recorded, an expected balance computed, variance "
         "surfaced at close",
         "Fewer than one variance incident per branch per month, and honest "
         "staff protected from suspicion."],
        ["Fifty-one branches reporting in fifty-one formats",
         "One consolidated cash position, reconciled daily",
         "Finance stops reconstructing the estate's position from "
         "spreadsheets."],
        ["Devices quietly accumulating in the store room",
         "Ageing, reminders at 3, 7, 15 and 30 days, then the abandonment "
         "process",
         "Uncollected devices beyond thirty days fall below half a per cent."],
        ["Personal data captured with no record of consent",
         "The transparency notice presented and the consent recorded at the "
         "moment of capture",
         "A lawful basis that can be evidenced, rather than reconstructed "
         "after a complaint."],
    ],

    "s1_one_sentence":
        "M04 turns the counter from a paper process that varies by branch into "
        "a three-minute, evidenced, cash-controlled operation that works the "
        "same way in all fifty-one of them.",

    # ============================================ 2. who uses it
    "s2_lede":
        "More people use this module than any other in the system, and most of "
        "them will judge the whole programme by it.",

    "s2_intro": [
        "Between one hundred and fifty and two hundred and fifty service "
        "centre agents will spend their entire working day in M04, along with "
        "fifty-one or more branch managers and every cashier in the company. "
        "For all of them, and for every walk-in customer, this module is the "
        "ERP. Nothing else in the programme will be seen by as many people as "
        "often.",

        "That has a consequence worth stating plainly. If the counter works "
        "well, branch staff will advocate for the rest of the system. If it "
        "does not, they will resist all of it, including the parts that are "
        "excellent. The adoption of the entire programme rests "
        "disproportionately on this one module being fast and pleasant to "
        "use.",
    ],

    "s2_roles": [
        ["Service centre agent",
         "Taking jobs in, handing devices back, selling at the counter",
         "The counter workstation, with the customer's whole context on one "
         "screen"],
        ["Cashier",
         "Taking payment and running the drawer",
         "The payment screen and the shift position"],
        ["Branch manager",
         "Running the branch day and approving what needs approval",
         "The branch board: intake, work in progress, ready, overdue, revenue "
         "and queue health"],
        ["Operations Director",
         "Comparing branches on things that were never comparable before",
         "The branch comparison report"],
        ["Finance manager",
         "The estate's cash position, and every variance in it",
         "Daily cash reconciliation across all branches"],
        ["Finance officer",
         "Reconciling deposits and receipts",
         "Their assigned scope of the cash position"],
        ["Inventory manager",
         "What was sold across the counter",
         "Counter sale stock movements, read-only"],
        ["Quality manager",
         "Checklist compliance and counter satisfaction",
         "The checklist and satisfaction reports"],
        ["Compliance officer",
         "Whether personal data is being captured lawfully",
         "Consent capture completeness"],
        ["Walk-in customer",
         "Getting served",
         "A token, a wait estimate, a display and their name being called"],
    ],

    "s2_days": [
        {
            "title": "If you work at a counter",
            "text": [
                "This is your whole day. You will open a shift with a counted "
                "float, serve tokens as they come, and close with a counted "
                "balance. In between, most of what you do is one of three "
                "things: taking a job in, handing one back, or taking money.",

                "The intake screen is built around a stopwatch. Search by "
                "phone number first — that finds most people. The device is "
                "usually already known, and if it is not you can register it "
                "without leaving the screen. Entitlement appears before you "
                "commit anything, so you can tell the customer who pays while "
                "they are still standing in front of you. Then the job sheet "
                "prints. Three minutes is the target and it is achievable "
                "within your first week.",

                "The thing that will feel different is that you can see "
                "everything. Open orders, devices, contracts, entitlements, "
                "what they owe, their tier, recent conversations — all on one "
                "screen before you have said anything. Customers notice this "
                "immediately, and it is the single biggest change in how a "
                "counter conversation feels.",
            ],
        },
        {
            "title": "If you handle cash",
            "text": [
                "The discipline is stricter than you are used to and the "
                "benefit runs mostly in your favour. Every movement in the "
                "drawer is recorded: receipts, refunds, petty expenses, "
                "transfers and banking. At close the system computes what "
                "should be there, you count what is, and the difference is "
                "the variance.",

                "Above a tolerance the variance needs the branch manager's "
                "approval before the shift can close, and a branch cannot open "
                "a new shift while an old one is still open. That sounds "
                "unforgiving. In practice it means a discrepancy is found "
                "within hours by the person who can still remember the "
                "afternoon, rather than three weeks later by somebody who "
                "cannot.",

                "One rule to know before you meet it: the person who handles "
                "the cash cannot be the person who reconciles the shift. That "
                "is a separation of duties and it exists to protect you.",
            ],
        },
        {
            "title": "If you manage a branch",
            "text": [
                "The board replaces the end-of-day discovery. Intake, work in "
                "progress, ready for collection, overdue, revenue and queue "
                "health are all live, which means the useful question changes "
                "from 'what happened today?' to 'what is happening now?'.",

                "You will spend most of your attention on two things. The "
                "first is queue health — when the wait passes the threshold, "
                "an alert tells you to open another counter, and acting on "
                "that quickly is the difference between customers waiting and "
                "customers leaving. The second is uncollected devices, which "
                "accumulate quietly and which the system will chase for you at "
                "three, seven, fifteen and thirty days.",

                "You are also the approval point for cash variance, and you "
                "should expect that to feel intrusive for the first month. It "
                "settles.",
            ],
        },
        {
            "title": "If you work in finance or compliance",
            "text": [
                "For finance the change is a single consolidated cash position "
                "across every branch, reconciled daily, with every movement "
                "attributable to a shift and a person. Variances above "
                "tolerance arrive with an approval attached and a pattern "
                "visible across branches.",

                "For compliance the change is more fundamental. Cash receipts "
                "above the statutory threshold require the customer's national "
                "identity number, and under the Personal Data Protection Act "
                "2026 that is sensitive personal data. The system presents the "
                "transparency notice and records the consent before the field "
                "can be written at all. Consent capture completeness is "
                "reported monthly with a target of one hundred per cent, "
                "because anything less is not a lawful basis.",
            ],
        },
    ],

    "s2_note":
        "The customer's national identity number is write-only at the counter. "
        "The agent who captures it cannot read it back. Retrieval is "
        "restricted to finance and the branch manager, with every access "
        "logged.",

    # ============================================ 3. boundary
    "s3_lede":
        "M04 is a channel into the rest of the system, not a parallel copy of "
        "it. It owns the queue, the drawer and the shelf — and almost nothing "
        "else.",

    "s3_intro": [
        "The counter creates service orders, but it does not own them. It "
        "looks up customers, but it does not own the customer record. It "
        "identifies devices, but the device outlives the counter. Almost "
        "everything an agent touches during a three-minute intake belongs to "
        "another module, and M04's job is to be a fast, well-designed window "
        "onto all of it.",

        "What M04 does own is physical and local: the queue token, the storage "
        "location of a device in branch custody, the cash drawer and the "
        "shift. Those things exist only at a counter and nowhere else in the "
        "system, which is exactly why the module exists.",

        "One boundary is subtle and important. M04 presents the "
        "data-protection transparency notice and records that the customer "
        "acknowledged it, but the wording of that notice and the consent "
        "record itself belong to M33. That separation means the notice can be "
        "updated centrally when the law changes, without touching fifty-one "
        "branches.",
    ],

    "s3_shared_intro":
        "Almost everything at the counter is shared. This table says who "
        "actually owns each of them.",

    "s3_shared": [
        ["The queue token", "M04 — this module owns it",
         "Issues it, prioritises it, calls it and closes it"],
        ["The storage location", "M04 — for devices in branch custody",
         "Assigns the shelf, and finds the device again"],
        ["The cash drawer and the shift", "M04",
         "Records every movement; M50 reconciles the position"],
        ["The service order", "M01",
         "Creates it and hands it over. Never owns its state logic"],
        ["The customer", "M33 Party Master",
         "Looks them up, or creates them inline. Does not own the record"],
        ["The consent and the notice", "M33",
         "Presents the notice and records the acknowledgement. Does not own "
         "the wording"],
        ["The device", "M17 Asset Registry",
         "Identifies it, or registers it inline. Devices outlive counters"],
        ["The payment", "M20 and M50",
         "Captures it at the counter. Does not create the invoice or "
         "reconcile the bank"],
        ["Counter stock", "M15 Inventory",
         "Sells from it. Does not hold the levels or plan replenishment"],
        ["The branch as an organisation", "M30",
         "Operates within it. Codes, zones and cost centres are configuration"],
    ],

    # ============================================ 4. kinds of visit
    "s4k_title": "The kinds of counter visit it has to handle",

    "s4k_lede":
        "Eight reasons somebody walks into a branch, each needing a different "
        "amount of the agent's time and a different route through the queue.",

    "s4k_intro": [
        "A queue that treats every visit the same is a badly designed queue. "
        "Somebody collecting a finished repair needs ninety seconds; somebody "
        "bringing in three devices for a corporate account needs fifteen "
        "minutes. Putting them in the same line makes both experiences worse.",

        "So tokens are issued by service category and routed to counters by "
        "capability — intake, collection, payment, corporate, technical. On "
        "top of that sits priority: Privilege Gold and Diamond members, "
        "corporate account holders, elderly customers and customers with "
        "accessibility needs are placed ahead by policy, automatically.",
    ],

    "kinds_columns": [
        ("Quick visits", "Ninety seconds to three minutes", [
            "Collecting a finished repair",
            "Paying an outstanding bill",
            "Buying an accessory",
            "Checking on a job",
        ]),
        ("Intake visits", "The three-minute constraint applies", [
            "A walk-in repair, out of warranty",
            "A warranty job with proof of purchase",
            "A pre-booked appointment checking in",
            "An emergency needing same-day handling",
        ]),
        ("Longer visits", "Book a counter, not a slot in the line", [
            "Corporate account with several devices",
            "A membership or protection product sale",
            "A dispute or complaint",
            "A device with a data-services requirement",
        ]),
    ],
    "kinds_title": "Three kinds of counter visit",
    "kinds_sub": "Different time, different counter, different priority",

    "s4k_header": ["The kind of visit", "What is different about it",
                   "What stays the same"],
    "s4k_table": [
        ["Walk-in repair intake",
         "The three-minute constraint applies in full. Customer lookup, device "
         "recall, entitlement and job sheet, all in one pass.",
         "A token, a counter, a recorded interaction and a printed "
         "acknowledgement"],
        ["Collection of a finished repair",
         "Identity verification of whoever is collecting, retrieval from a "
         "recorded shelf, accessories confirmed, signature, gate pass.",
         "As above"],
        ["Payment only",
         "Routed to a payment counter. May trigger the identity requirement "
         "above the statutory cash threshold.",
         "As above"],
        ["Appointment check-in",
         "Merged into the queue at the reserved time rather than joining the "
         "back of it.",
         "As above"],
        ["Privilege member",
         "Gold and Diamond receive priority placement automatically, whatever "
         "they have come for.",
         "As above"],
        ["Corporate account",
         "Often several devices under one batch reference, and routed to a "
         "counter with the capability for it.",
         "As above"],
        ["Counter sale",
         "Parts, accessories, memberships, warranty extensions and AMC "
         "contracts. A membership or protection sale requires the customer's "
         "acceptance of terms to be recorded.",
         "As above"],
        ["A customer who needs help",
         "Accessibility need or age gives priority placement by policy.",
         "As above"],
    ],
    "s4k_caption": "The kinds of counter visit and what distinguishes each",

    "s4k_note":
        "Priority is applied by the system from the customer's tier and "
        "circumstances, not decided at the token machine. An agent who thinks "
        "somebody should have had priority and did not should report it as a "
        "policy question, not resolve it at the counter.",

    # ============================================ 5. vocabulary
    "s4_lede":
        "Twelve words that mean something specific at a counter, several of "
        "them about money and one of them about the law.",

    "s4_intro": [
        "Counter vocabulary mixes retail, service and cash handling. These are "
        "the terms that appear on screen, on the printed slips and in every "
        "report the module produces.",
    ],

    "s4_glossary": [
        ["Token",
         "The queue position issued to a customer, by service category. It can "
         "come from a kiosk, a counter or the customer's own phone by QR code.",
         "The first thing that happens on a visit"],
        ["Priority placement",
         "Being put ahead in the queue by policy — membership tier, corporate "
         "account, age or accessibility need.",
         "Applied automatically, not decided at the machine"],
        ["Counter capability",
         "What a particular counter is set up to do: intake, collection, "
         "payment, corporate or technical.",
         "Tokens are routed to counters that can serve them"],
        ["Intake",
         "Taking a job in: customer, device, complaint, condition, "
         "entitlement, job sheet. The three-minute constraint applies to this "
         "and nothing else.",
         "The most-performed action in the system"],
        ["Storage location",
         "The recorded shelf or bin holding a device while it is in branch "
         "custody. A device cannot be in two of them at once.",
         "Assigned when a device arrives, used when it is collected"],
        ["Gate pass",
         "The printed authority for a device to leave the branch, issued at "
         "handover.",
         "Familiar from the paper process; now generated"],
        ["Shift",
         "One period of counter operation with an opening float, recorded "
         "movements and a counted close.",
         "A branch cannot open one while another is unclosed"],
        ["Float",
         "The cash a drawer starts with, counted at open.",
         "The baseline everything else is measured against"],
        ["Variance",
         "The difference between what the system says should be in the drawer "
         "and what is actually counted.",
         "Above tolerance it needs the branch manager before the shift can "
         "close"],
        ["Petty cash",
         "The branch's small-expense float, with capture and replenishment.",
         "Separate from the counter drawer"],
        ["Transparency notice",
         "The statement shown to a customer explaining what personal data is "
         "being collected and why, before it is captured.",
         "Mandatory before any national identity number is recorded"],
        ["Consent record",
         "The recorded fact that the customer acknowledged the notice, with "
         "when and by whom.",
         "Without it the capture is not lawful, and the field will not write"],
    ],

    # ============================================ 6. what you can do
    "s5_lede":
        "Thirty-two things, in four areas. Nearly all of them are in service "
        "of one number.",

    "s5_intro": [
        "The four areas follow the shape of a branch day: the queue that "
        "brings people to you, the counter where you serve them, the money "
        "that changes hands, and the discipline of opening and closing.",

        "Read the second area first if you work at a counter. It contains the "
        "three-minute intake, and almost every other function in the module "
        "exists to make that one possible.",
    ],

    "areas": [
        {
            "title": "The queue",
            "who": [
                ("Mostly used by", "Customers, and the kiosk"),
                ("Also relied on by", "Branch managers watching queue health"),
                ("Where it happens", "The door, the waiting area and the "
                                     "display"),
            ],
            "intro": [
                "A queue is a small piece of software with a large effect on "
                "how a company is perceived. Customers abandon a wait at "
                "around eight minutes — not because eight minutes is "
                "intolerable, but because an undefined wait of unknown length "
                "is. Telling somebody the wait is twelve minutes keeps most of "
                "them; telling them nothing loses a proportion of them at "
                "eight.",

                "So the queue does three things: it issues a token by "
                "category, it estimates and displays the wait, and it applies "
                "priority by policy. Everything else — the kiosk, the QR code, "
                "the recall, the counter routing — is arrangement around those "
                "three.",
            ],
            "features": [
                ["Token issuance",
                 "Issues a numbered token by service category from a kiosk, a "
                 "counter or the customer's own phone by QR code.",
                 "The customer knows they are in the system before they have "
                 "spoken to anybody."],
                ["Queue display",
                 "Drives the waiting-area display showing which tokens are "
                 "being served at which counter, in Bengali and English, with "
                 "an audible call.",
                 "Nobody has to hover near the counter to avoid missing their "
                 "turn."],
                ["Wait-time estimation",
                 "Estimates and shows the expected wait from live throughput "
                 "and queue depth.",
                 "The customer decides whether to wait or come back, which is "
                 "better than deciding to leave."],
                ["Priority queueing",
                 "Places Privilege Gold and Diamond members, corporate account "
                 "holders, elderly and disabled customers ahead, by policy.",
                 "A membership sold on priority service actually delivers it."],
                ["Appointment check-in",
                 "Checks in a pre-booked appointment and merges it into the "
                 "queue at the reserved time.",
                 "Booking an appointment means something."],
                ["Recall and no-show",
                 "Recalls a skipped token once, then marks it a no-show and "
                 "releases the position.",
                 "One missed call is forgivable; the queue keeps moving."],
                ["Counter routing",
                 "Routes tokens to counters by what each counter is set up to "
                 "do.",
                 "A ninety-second collection is not stuck behind a fifteen-"
                 "minute corporate intake."],
                ["Self-service kiosk",
                 "Lets a customer take a token, check status or check in for "
                 "an appointment with no staff involvement.",
                 "The first thirty seconds of a visit stops needing an "
                 "employee."],
            ],
            "example": (
                "a busy Saturday at Dhanmondi",
                "It is 11:20 on a Saturday and eighteen people are waiting. "
                "The display shows tokens now serving at four counters and an "
                "estimated wait of nineteen minutes for intake, seven for "
                "collection. A Privilege Gold member arrives, takes a token "
                "from the kiosk and is placed fourth rather than nineteenth — "
                "automatically, with no conversation and no visible favour. An "
                "elderly customer is given priority on the same basis. Two "
                "customers with collection tokens are through in under two "
                "minutes each because collection is routed to its own counter. "
                "At 11:34 the average wait crosses the branch threshold and an "
                "alert reaches the branch manager, who opens a fifth counter. "
                "Nobody left. Under the old arrangement — one undefined line, "
                "no display, no estimate — a proportion of those eighteen "
                "would have walked out at around the eight-minute mark, and "
                "nobody would have known."),
            "mistakes": [
                "Calling a customer out of turn as a favour. The queue is "
                "visible to everybody waiting in it, and visible unfairness "
                "costs more than the favour is worth.",
                "Ignoring the wait-time alert because the queue 'always clears'. "
                "The threshold is set at the point where people start "
                "leaving.",
                "Marking a token as a no-show on the first call. The policy is "
                "one recall, and it exists because people do miss the first "
                "announcement.",
                "Issuing an intake token to somebody who has come to collect. "
                "It puts a ninety-second visit into a twenty-minute line.",
            ],
        },
        {
            "title": "The counter itself",
            "who": [
                ("Mostly used by", "Service centre agents, all day"),
                ("Also relied on by", "Every module downstream, which inherits "
                                      "whatever is captured here"),
                ("Where it happens", "The counter workstation"),
            ],
            "intro": [
                "Eight functions, and the first one carries the whole module. "
                "A walk-in intake has to be complete in under three minutes: "
                "customer found, device identified, complaint captured, "
                "condition recorded, entitlement resolved, job sheet printed.",

                "It is achievable because of the order the screen does things "
                "in. Search first — a phone number finds most people. The "
                "device is usually already on their record; if not it can be "
                "registered without leaving the screen. Fields default from "
                "what is already known. Entitlement is evaluated and shown "
                "before anything is committed, so the commercial conversation "
                "happens once, at the right moment.",

                "The other function worth singling out is storage location. "
                "Recording which shelf a device is on sounds trivial and is "
                "the difference between a collection taking ninety seconds and "
                "an agent disappearing into a storeroom for five minutes while "
                "a customer watches.",
            ],
            "features": [
                ["Fast intake",
                 "Completes a walk-in intake in under three minutes with "
                 "search-first lookup, device recall and defaulted fields.",
                 "The constraint the whole module is designed around."],
                ["Counter dashboard",
                 "Shows everything about the person in front of you: open "
                 "orders, devices, contracts, entitlements, dues, tier and "
                 "recent conversations.",
                 "The agent knows more about the visit than the customer "
                 "does."],
                ["Collection and handover",
                 "Verifies identity, retrieves the device from its recorded "
                 "location, confirms accessories, captures a signature and "
                 "issues the gate pass.",
                 "A collection takes ninety seconds and nobody searches a "
                 "storeroom."],
                ["Storage location tracking",
                 "Records and retrieves the physical shelf or bin holding each "
                 "device in branch custody.",
                 "Over 98 per cent of devices found inside sixty seconds."],
                ["Counter sales",
                 "Sells parts, accessories, Privilege memberships, warranty "
                 "extensions and AMC contracts across the counter.",
                 "The moment a customer is grateful is the moment to offer a "
                 "protection plan."],
                ["Quotation printing",
                 "Prints or sends an estimate from the counter.",
                 "A customer leaves with the price in writing."],
                ["Receipt and label printing",
                 "Prints receipts, job sheets, device labels, gate passes and "
                 "token slips on thermal and A4 printers.",
                 "Everything the paper process produced, generated instead of "
                 "written."],
                ["Customer feedback at the counter",
                 "Captures a quick satisfaction rating at handover on a "
                 "customer-facing display or tablet.",
                 "Satisfaction becomes a number per branch and per agent."],
            ],
            "example": (
                "a three-minute intake, timed",
                "A customer arrives at the Uttara counter with a desktop that "
                "will not start. Token called at 10:31:00. The agent types the "
                "last four digits of a mobile number and the customer appears, "
                "with two previous jobs and one registered device — a laptop, "
                "not this desktop. Twenty seconds. The desktop is registered "
                "inline from its serial plate: forty seconds. Symptom captured "
                "from the coded list, 'will not power on', with a note in "
                "Bengali: thirty seconds. Accessories recorded as power cable "
                "only, condition photographed, customer acknowledges: "
                "thirty-five seconds. Entitlement returns out of warranty, and "
                "the agent says so before anything is confirmed: ten seconds. "
                "Job sheet prints with the order number and tracking link: "
                "fifteen seconds. Total 02:50. The old paper equivalent, "
                "measured at the same branch, took a little over nine minutes "
                "and produced a form that only that branch could read."),
            "mistakes": [
                "Creating a new customer because the search did not find them "
                "on the first attempt. Try the phone number, then the name, "
                "then the device serial before creating.",
                "Skipping the condition photographs to save thirty seconds. "
                "They are the only defence against a dispute at collection.",
                "Not assigning a storage location because the device is 'going "
                "straight to the workshop'. It rarely does, and then nobody "
                "can find it.",
                "Handing over to whoever presents the job sheet. Identity "
                "verification is a hard rule and it is there because devices "
                "have been collected by the wrong people.",
                "Offering a membership without recording the customer's "
                "acceptance of terms. The sale is not valid without it.",
            ],
            "caution":
                "If an intake is regularly taking you longer than three "
                "minutes, that is worth reporting rather than absorbing. The "
                "constraint is a design commitment, and a screen that misses "
                "it is a defect in the screen, not in you.",
        },
        {
            "title": "Cash and payment",
            "who": [
                ("Mostly used by", "Cashiers and agents taking payment"),
                ("Also relied on by", "Branch managers approving variance, and "
                                      "finance daily"),
                ("Where it happens", "The drawer, and the shift open and "
                                     "close"),
            ],
            "intro": [
                "Seven functions, and between them they replace the least "
                "controlled process in the company. Every movement in and out "
                "of the drawer is recorded — receipts, refunds, petty expense, "
                "transfers and banking — and at close the system computes what "
                "should be there against what is counted.",

                "Two rules shape everything here. A branch cannot open a shift "
                "while a previous one remains unclosed, and a variance beyond "
                "tolerance needs the branch manager's approval before the "
                "shift can close. Together they mean a discrepancy surfaces "
                "within hours, while the people involved still remember the "
                "afternoon.",

                "The third thing to know concerns the law rather than the "
                "money. Cash receipts above the statutory threshold require "
                "the customer's national identity number, and under the "
                "Personal Data Protection Act 2026 that is sensitive personal "
                "data. The transparency notice must be presented and the "
                "consent recorded before the field can be written at all.",
            ],
            "features": [
                ["Shift open and close",
                 "Opens with a counted float and closes with a counted "
                 "balance.",
                 "Every taka of the day is bounded by two counts."],
                ["Cash drawer",
                 "Records every movement: receipts, refunds, petty expense, "
                 "transfers and banking.",
                 "The expected balance is always known, not reconstructed."],
                ["Payment capture",
                 "Takes cash, card, bKash, Nagad and bank transfer with an "
                 "instant receipt.",
                 "However the customer wants to pay, the record is the same."],
                ["Variance handling",
                 "Records any difference at close and requires approval above "
                 "the tolerance.",
                 "A discrepancy is found in hours rather than weeks."],
                ["Banking deposit",
                 "Records deposits with the slip reference for reconciliation "
                 "in M50.",
                 "The bank statement and the branch record can be matched."],
                ["High-value cash control",
                 "Requires the customer's national identity number above the "
                 "statutory threshold, presenting the transparency notice and "
                 "recording consent first.",
                 "The statutory obligation and the data-protection obligation "
                 "are satisfied in the same action."],
                ["Petty cash",
                 "Manages the branch's small-expense float with capture and "
                 "replenishment.",
                 "Branch expenses stop being settled out of the counter "
                 "drawer."],
            ],
            "example": (
                "a variance found the same afternoon",
                "The Mirpur branch closes its afternoon shift at 18:05. The "
                "system computes an expected balance of BDT 47,850 from the "
                "opening float and the day's recorded movements. The counted "
                "balance is BDT 47,350 — a shortfall of BDT 500, which is "
                "above the branch tolerance. The shift cannot close. The "
                "cashier and the branch manager review the movements together "
                "and find a refund of BDT 500 issued at 15:40 that was given "
                "from the drawer but recorded as a card reversal. The record "
                "is corrected, the variance resolves to zero, and the shift "
                "closes at 18:20. Under the old arrangement this would have "
                "been discovered — if at all — during a monthly reconciliation "
                "weeks later, by which time nobody would have remembered a "
                "Tuesday afternoon refund, and the cashier would have carried "
                "an unexplained shortfall on their record."),
            "mistakes": [
                "Leaving a shift open overnight because it was busy. The next "
                "shift cannot open, which will be somebody else's problem at "
                "eight in the morning.",
                "Settling a small branch expense from the counter drawer. That "
                "is what petty cash is for, and it makes the variance "
                "unexplainable.",
                "Recording a refund against the wrong method. The commonest "
                "single cause of an unexplained variance.",
                "Capturing a national identity number without the notice "
                "appearing. If the field lets you write it without the notice, "
                "that is a serious fault and should be reported the same day.",
                "Reconciling your own shift. The separation of duties is not a "
                "formality and the system will not allow it.",
            ],
            "caution":
                "A national identity number captured at the counter is "
                "write-only to the agent who captured it. If you can read one "
                "back and your role is not finance or branch manager, stop and "
                "report it.",
        },
        {
            "title": "Running the branch day",
            "who": [
                ("Mostly used by", "Branch managers"),
                ("Also relied on by", "Agents reading handover notes, and "
                                      "operations comparing branches"),
                ("Where it happens", "Opening, closing, and the board in "
                                     "between"),
            ],
            "intro": [
                "Eight functions covering the discipline that turns fifty-one "
                "independent shops into one operation. Opening and closing "
                "checklists cover safety, equipment, stock, cash and staffing, "
                "and their completion is reported monthly because a checklist "
                "nobody checks is decoration.",

                "The branch board is the manager's main screen: today's "
                "intake, work in progress, ready for collection, overdue, "
                "revenue and queue health, live. And the uncollected device "
                "report is the quiet one that saves the most space — devices "
                "ready but not collected, by age, with reminders at three, "
                "seven, fifteen and thirty days and then the abandonment "
                "process.",
            ],
            "features": [
                ["Opening checklist",
                 "Enforces a daily opening covering safety, equipment, stock, "
                 "cash and staffing.",
                 "The branch opens the same way every day in every location."],
                ["Branch dashboard",
                 "Shows today's intake, work in progress, ready for "
                 "collection, overdue, revenue and queue health.",
                 "The manager finds out during the day rather than at the end "
                 "of it."],
                ["Shift handover notes",
                 "Records structured notes between shifts, visible to the "
                 "incoming team.",
                 "The afternoon team knows what the morning team knows."],
                ["Uncollected device report",
                 "Lists devices ready but uncollected, by age, with reminder "
                 "actions and escalation.",
                 "The storeroom stops silently filling with devices nobody "
                 "owns."],
                ["Closing checklist",
                 "Enforces closing: cash counted, devices secured, orders "
                 "updated, alarms set.",
                 "The last person out has a list rather than a memory."],
                ["Multi-counter configuration",
                 "Configures counters per branch with capability and staffing.",
                 "A large branch and a small one can both be set up sensibly."],
                ["Counter performance analytics",
                 "Reports throughput, handling time, queue metrics and "
                 "satisfaction per counter and per agent.",
                 "Comparable numbers across every branch, for the first "
                 "time."],
                ["Branch announcements",
                 "Publishes branch-level announcements, targets and notices to "
                 "counter staff.",
                 "One channel instead of a noticeboard and a group chat."],
            ],
            "example": (
                "the storeroom that emptied itself",
                "A branch manager opens the uncollected device report on a "
                "Monday and finds forty-one devices ready but not collected: "
                "twelve under seven days, nineteen between seven and fifteen, "
                "eight between fifteen and thirty, and two beyond thirty. She "
                "does nothing about the first thirty-one, because the reminder "
                "sequence is already running at three, seven and fifteen days. "
                "The eight in the fifteen-to-thirty band get a personal "
                "telephone call, which recovers five of them within the week. "
                "The two beyond thirty days have already entered the "
                "abandonment process with statutory notice, raised "
                "automatically by M01. Six weeks later the report shows "
                "fourteen devices, almost all of them under seven days old. "
                "The storeroom has about half the physical space it had, and "
                "the branch has collected the revenue on five repairs it had "
                "already done."),
            "mistakes": [
                "Treating the opening checklist as a formality to click "
                "through. It is reported monthly, and the items on it are the "
                "ones that cause the day to go wrong when they are missed.",
                "Writing handover notes as 'all fine'. The incoming shift "
                "inherits whatever you did not say.",
                "Chasing every uncollected device personally. The reminder "
                "sequence handles the first fifteen days; your time is worth "
                "more on the older ones.",
                "Comparing your branch's throughput to another's without "
                "looking at handling time and satisfaction. Fast and bad is "
                "not better than steady and good.",
            ],
        },
    ],

    # ============================================ 7. the journey
    "s6_title": "The journey of a counter visit",
    "s6_lede":
        "From a token to a printed job sheet, and separately from a shelf to a "
        "gate pass.",

    "s6_intro": [
        "M04 has three short lifecycles rather than one long one: the queue "
        "token, the branch shift, and a device in branch custody. All three "
        "are measured in minutes or hours rather than days, and all three are "
        "bounded at both ends by something being counted or verified.",

        "The one below is the token's, because it is the journey a customer "
        "actually experiences. The other two appear in Appendix A.",
    ],

    "journey": [
        ("Issued", "Kiosk, counter or QR", None),
        ("Waiting", "The customer", None),
        ("Prioritised", "System, by policy", None),
        ("Called", "System, to a counter", None),
        ("Recalled", "System, once only", None),
        ("Being served", "Agent", None),
        ("Intake saved", "Agent", "gate"),
        ("Device stored", "Agent", "gate"),
        ("Ready", "M01 or M31", None),
        ("Collected", "Agent + customer", "gate"),
        ("No-show", "System", None),
    ],
    "journey_title": "The path a counter visit follows",
    "journey_sub": ("From the door to the job sheet, and back again weeks "
                    "later for the collection"),
    "journey_caption": "What a customer actually experiences at a branch",

    "s6_stages": [
        ["Issued", "The customer has a token and a category.",
         "Kiosk, counter or the customer's phone",
         "Nothing. Anybody can take a token."],
        ["Waiting", "They are in the queue with an estimated wait shown.",
         "The customer",
         "Nothing, but the estimate is what stops them leaving."],
        ["Prioritised", "Policy has decided where in the queue they sit.",
         "System",
         "Tier, corporate account, age or accessibility need."],
        ["Called", "Their number is on the display and announced.",
         "System, when a capable counter frees",
         "A counter with the right capability being available."],
        ["Recalled", "They missed the first call and are being called again.",
         "System",
         "One recall only, then the position is released."],
        ["Being served", "They are at the counter.", "Agent",
         "Nothing — but the three-minute clock is now running."],
        ["Intake saved", "The job exists.", "Agent",
         "Device identified and customer contact verified. Both are hard "
         "requirements."],
        ["Device stored", "It is on a recorded shelf.", "Agent",
         "A storage location assigned. A device cannot be in two at once."],
        ["Ready", "The repair is done and it is waiting to be collected.",
         "M01 or M31",
         "The work completed and quality passed elsewhere."],
        ["Collected", "The customer has it back.", "Agent and customer",
         "The collector's identity verified, accessories confirmed, signature "
         "captured, gate pass issued."],
        ["No-show", "They did not answer the recall.", "System",
         "One recall having already been made."],
    ],

    "s6_gates_intro":
        "Four points in a counter day will simply refuse to proceed. Three of "
        "them protect the customer or the company; the fourth protects the "
        "person handling the money.",

    "gates": [
        ("Intake needs a device and a contact",
         "An intake cannot be saved without device identification and verified "
         "customer contact", "Agent"),
        ("One device, one shelf",
         "A device cannot occupy two storage locations at the same time",
         "System"),
        ("Identity before handover",
         "A device cannot be handed over without verifying who is collecting "
         "it", "Agent"),
        ("Notice before personal data",
         "A national identity number cannot be written until the transparency "
         "notice has been presented and consent recorded", "System"),
        ("Counted balance before close",
         "A shift cannot close without a counted cash balance", "Cashier"),
        ("Approval for variance",
         "A variance beyond tolerance needs the branch manager before the "
         "shift can close", "Branch manager"),
        ("One shift at a time",
         "A branch cannot open a shift while a previous one remains unclosed",
         "System"),
    ],

    "s6_wrong_intro":
        "Counter problems are concentrated at four points, and a branch "
        "manager can see three of them on the board before a customer "
        "mentions them.",

    "s6_wrong": [
        ["Waiting",
         "The estimated wait passes the threshold and people start leaving.",
         "An alert to the branch manager, and abandonment rising in the daily "
         "queue report.",
         "Open another counter. The alert exists because acting quickly is the "
         "whole intervention."],
        ["Being served",
         "Intake takes longer than three minutes, repeatedly.",
         "The intake time distribution report, by branch and by agent.",
         "If it is one agent, coach. If it is one branch, look at the "
         "hardware. If it is everywhere, it is a defect in the screen."],
        ["Intake saved",
         "A duplicate customer has been created.",
         "It surfaces later as split history and a failed entitlement check.",
         "Merge in M33. The prevention is searching properly, which is a "
         "training matter."],
        ["Device stored",
         "No location was assigned because the device was 'going straight "
         "through'.",
         "Nobody can find it at collection.",
         "Assign a location every time. Devices very rarely go straight "
         "through."],
        ["Ready",
         "The customer does not come.",
         "The uncollected ageing report.",
         "Nothing for fifteen days — the sequence runs. Call personally in the "
         "fifteen-to-thirty band."],
        ["Collected",
         "Somebody other than the customer arrives with the job sheet.",
         "Identity verification fails.",
         "Do not release it. The customer can nominate a collector properly "
         "instead."],
        ["Shift close",
         "A variance that nobody can explain.",
         "The shift will not close.",
         "Walk the movements with the cashier. It is almost always a refund "
         "recorded against the wrong method."],
        ["Shift open",
         "The branch cannot open because last night's shift was left open.",
         "An alert at opening time.",
         "Close it. The prevention is the closing checklist, which is why it "
         "is enforced."],
    ],

    "s6_note":
        "The token, the shift and the device in custody are three separate "
        "lifecycles that happen to share a counter. A device can sit in branch "
        "custody across dozens of shifts, and the shift discipline is what "
        "keeps track of who was responsible for it at each point.",

    # ============================================ 8. day in the life
    "s7_lede":
        "Five walkthroughs from a branch day, from opening the shutters to "
        "counting the drawer.",

    "s7_intro": [
        "These follow the counter rather than a single job, because that is "
        "how a branch day actually works — many short interactions rather than "
        "one long one.",

        "Customers, branches, amounts and times are illustrative. The "
        "constraints, thresholds and rules behind them are exactly as the "
        "specification states them.",
    ],

    "scenarios": [
        {
            "title": "Opening a branch",
            "narrative": [
                "The first twenty minutes of a branch day, which set up "
                "everything that follows and which nobody notices when they "
                "are done properly.",
            ],
            "lanes": [
                ("Branch manager", [(0, "Works the opening checklist"),
                                    (1, "Reads the overnight handover notes")]),
                ("Cashier", [(1, "Opens a shift with a counted float")]),
                ("Agents", [(2, "Log in; counters go live")]),
                ("System", [(0, "Blocks if last night's shift is open"),
                            (2, "Starts the queue; kiosk goes live"),
                            (3, "Publishes the branch board")]),
            ],
            "columns": ["Checklist", "Shift open", "Counters live", "Board"],
            "exhibit_title": "Opening a branch, in four steps",
            "exhibit_sub": "The twenty minutes that decide the rest of the day",
            "caption": "How a branch day starts",
            "table": [
                ["1", "Branch manager",
                 "Works the opening checklist: safety, equipment, stock, cash "
                 "and staffing. If last night's shift was left open the system "
                 "will not allow a new one, and this is where that surfaces."],
                ["2", "Branch manager and cashier",
                 "Overnight handover notes are read. The cashier counts the "
                 "opening float and opens the shift against it."],
                ["3", "Agents and system",
                 "Agents log in and their counters go live with their "
                 "configured capabilities — two intake, one collection, one "
                 "payment. The kiosk starts issuing tokens."],
                ["4", "System",
                 "The branch board publishes: yesterday's carry-over work in "
                 "progress, devices ready for collection, the overdue list and "
                 "today's queue health."],
            ],
            "outcome":
                "The branch opens the same way it did yesterday and the same "
                "way the branch in Sylhet is opening this morning. Checklist "
                "completion is reported monthly with a target above 97 per "
                "cent, which is the only way fifty-one independent shops "
                "become one operation.",
        },
        {
            "title": "A three-minute intake",
            "narrative": [
                "The most-performed action in the entire ERP, timed against "
                "the constraint the module is designed around.",
            ],
            "lanes": [
                ("Customer", [(0, "Takes a token from the kiosk"),
                              (2, "Confirms the condition note"),
                              (3, "Leaves with a job sheet")]),
                ("Agent", [(1, "Finds the customer by phone; registers the "
                               "device"),
                           (2, "Captures symptom, accessories, photographs")]),
                ("System", [(1, "Shows history, contracts and dues"),
                            (2, "Resolves entitlement before commit"),
                            (3, "Creates the order in M01; prints; sends the "
                                "link")]),
            ],
            "columns": ["Token", "Identify", "Capture", "Print"],
            "exhibit_title": "A walk-in intake in two minutes fifty",
            "exhibit_sub": "Against about nine minutes on paper",
            "caption": "The action the whole module is designed around",
            "table": [
                ["1", "Customer and kiosk",
                 "Token taken at 10:29, category 'repair intake'. Estimated "
                 "wait shown as four minutes. Called at 10:31:00."],
                ["2", "Agent and system",
                 "Last four digits of a mobile number find the customer with "
                 "two previous jobs. Twenty seconds. The desktop is not on "
                 "their record, so it is registered inline from its serial "
                 "plate: forty seconds."],
                ["3", "Agent",
                 "Symptom chosen from the coded list with a free-text note in "
                 "Bengali: thirty seconds. Accessories, condition photographs "
                 "and the customer's acknowledgement: thirty-five seconds."],
                ["4", "System and agent",
                 "Entitlement resolves to out of warranty and is shown before "
                 "anything is committed. The agent says so, plainly: ten "
                 "seconds."],
                ["5", "System",
                 "Intake saved. The service order is created in M01, the job "
                 "sheet prints, the acknowledgement and tracking link are "
                 "sent, and a storage location is assigned. Fifteen seconds. "
                 "Total elapsed: 02:50."],
            ],
            "outcome":
                "About six minutes saved against the paper equivalent, on the "
                "highest-volume interaction in the business. And the record "
                "that exists afterwards can be read by any branch, the "
                "workshop, finance and the customer — which the paper form "
                "never could.",
        },
        {
            "title": "A collection that took ninety seconds",
            "narrative": [
                "The other half of a counter's work, and the one where the old "
                "process was most visibly embarrassing.",
            ],
            "lanes": [
                ("Customer", [(0, "Arrives with the tracking link"),
                              (2, "Verifies identity"),
                              (3, "Signs and rates the visit")]),
                ("Agent", [(1, "Retrieves from shelf C-14"),
                           (2, "Confirms the accessories")]),
                ("System", [(0, "Routes to the collection counter"),
                            (1, "Shows the storage location"),
                            (3, "Issues the gate pass; emits the event")]),
            ],
            "columns": ["Arrives", "Retrieved", "Verified", "Released"],
            "exhibit_title": "A collection, start to finish",
            "exhibit_sub": "The shelf reference is the whole difference",
            "caption": "Handing a device back without searching for it",
            "table": [
                ["1", "Customer and system",
                 "The customer arrives having had the ready notification. "
                 "Their token is routed to the collection counter rather than "
                 "the intake queue, and the wait is under three minutes."],
                ["2", "Agent",
                 "The order shows storage location C-14. The device is in the "
                 "agent's hands in under thirty seconds."],
                ["3", "Agent and customer",
                 "Identity verified — a hard rule, not a courtesy. Accessories "
                 "confirmed against what was recorded at intake: a power cable "
                 "and nothing else."],
                ["4", "Customer and system",
                 "Signature captured, gate pass printed, satisfaction rating "
                 "taken on the customer-facing tablet. Total 01:30."],
            ],
            "outcome":
                "Over 98 per cent of devices located within sixty seconds is "
                "the target, and it removes the single most visible source of "
                "embarrassment at a counter — an agent disappearing into a "
                "storeroom while a customer waits and watches.",
        },
        {
            "title": "A cash variance, resolved the same afternoon",
            "narrative": [
                "The control that pays for the module, working exactly as "
                "designed and feeling mildly unpleasant while it does.",
            ],
            "lanes": [
                ("Cashier", [(0, "Requests shift close at 18:05"),
                             (2, "Walks the movements with the manager")]),
                ("System", [(0, "Computes expected BDT 47,850"),
                            (1, "Variance BDT 500 — blocks the close"),
                            (3, "Closes; emits the position to M50")]),
                ("Branch manager", [(2, "Finds a refund recorded wrongly")]),
            ],
            "columns": ["Close requested", "Blocked", "Investigated",
                        "Closed"],
            "exhibit_title": "A BDT 500 variance found in fifteen minutes",
            "exhibit_sub": "Rather than in a monthly reconciliation, or never",
            "caption": "How the cash control actually behaves",
            "table": [
                ["1", "Cashier and system",
                 "Close requested at 18:05. The system computes an expected "
                 "balance of BDT 47,850 from the opening float and the day's "
                 "recorded movements."],
                ["2", "System",
                 "The counted balance is BDT 47,350. The BDT 500 shortfall is "
                 "above tolerance, so the close is blocked and routed to the "
                 "branch manager."],
                ["3", "Cashier and branch manager",
                 "They walk the day's movements together. A BDT 500 refund at "
                 "15:40 was paid from the drawer but recorded as a card "
                 "reversal."],
                ["4", "System",
                 "The record is corrected, the variance resolves to zero, the "
                 "shift closes at 18:20 and the position is emitted to M50 for "
                 "the estate-wide reconciliation."],
            ],
            "outcome":
                "Fifteen minutes, while everybody still remembered the "
                "afternoon. The alternative is a monthly reconciliation weeks "
                "later where the cashier carries an unexplained shortfall they "
                "cannot account for — which is unfair to them and useless to "
                "the company.",
        },
        {
            "title": "A high-value cash payment",
            "narrative": [
                "Where the statutory requirement and the data-protection "
                "requirement meet, in a single interaction at a counter.",
            ],
            "lanes": [
                ("Customer", [(0, "Pays BDT 62,000 in cash"),
                              (2, "Reads and acknowledges the notice")]),
                ("System", [(1, "Requires identity above the threshold"),
                            (1, "Presents the transparency notice"),
                            (3, "Writes to the resident store only")]),
                ("Agent", [(2, "Captures the number, write-only"),
                           (3, "Issues the receipt")]),
            ],
            "columns": ["Payment", "Threshold", "Consent", "Recorded"],
            "exhibit_title": "A payment that triggered two legal obligations",
            "exhibit_sub": "Satisfied in one interaction, in the right order",
            "caption": "How personal data is captured lawfully at a counter",
            "table": [
                ["1", "Customer",
                 "Pays BDT 62,000 in cash for a corporate repair, above the "
                 "statutory threshold for identity capture."],
                ["2", "System",
                 "The payment cannot complete without the customer's national "
                 "identity number. Before that field opens, the transparency "
                 "notice is presented — what is being collected, why, and on "
                 "what basis."],
                ["3", "Customer and agent",
                 "The customer acknowledges the notice; the acknowledgement is "
                 "recorded with when and by whom. Only then does the field "
                 "accept input."],
                ["4", "System",
                 "The number is written to the Bangladesh-resident store only. "
                 "It is never cached locally, exported, or printed beyond the "
                 "statutory receipt. The agent who captured it cannot read it "
                 "back."],
                ["5", "Agent",
                 "The receipt is issued and the payment completes."],
            ],
            "outcome":
                "A lawful basis that can be evidenced rather than "
                "reconstructed after a complaint. Consent capture completeness "
                "is reported monthly against a target of one hundred per cent, "
                "and the specification puts the exposure of a rights violation "
                "at up to BDT 25 lakh.",
        },
    ],

    "s9t_lede":
        "Five moments from one branch day, and the same four ideas underneath "
        "them.",

    "s9t_intro": [
        "The walkthroughs covered opening, an intake, a collection, a cash "
        "variance and a legally sensitive payment. They are deliberately "
        "small; a counter day is made of small things repeated many times.",

        "What connects them is that in each case the system removed a "
        "judgement call from somebody under time pressure. That is the design "
        "philosophy of the whole module.",
    ],

    "s9t_table": [
        ["Speed is a feature, not a nicety",
         "The intake walkthrough: two minutes fifty against about nine.",
         "If the software is slower than the paper, staff keep the paper, and "
         "every module downstream inherits bad data."],
        ["Tell the customer what is happening",
         "The queue estimate, the ready notification, the tracking link.",
         "Most of what customers dislike about a counter is uncertainty rather "
         "than waiting."],
        ["Record it where it happens",
         "The shelf reference, the condition photographs, the cash movement.",
         "A shelf reference written at the time turns a five-minute search "
         "into thirty seconds."],
        ["Find the problem while somebody still remembers",
         "The variance walkthrough: fifteen minutes rather than a month.",
         "Same-day discovery is what makes the cash control fair as well as "
         "effective."],
        ["Do the legal thing in the right order",
         "The high-value payment: notice, then consent, then the field opens.",
         "Consent recorded afterwards is not consent, and the field will not "
         "write without it."],
    ],

    "s9t_close":
        "For most customers and most branch staff, M04 is the ERP. The rest of "
        "the programme could be excellent and it would not matter if the "
        "counter were slow. Everything in this module should be judged against "
        "that: does it make the next three minutes faster and calmer than the "
        "paper it replaced?",

    # ============================================ 10. rules
    "s8_lede":
        "Fourteen rules. Most of them are about money or personal data, and "
        "two of them will stop a branch from opening.",

    "s8_intro": [
        "The counter handles other people's money and other people's personal "
        "information, in fifty-one places, with a high turnover of staff. That "
        "combination is why the rules here are firmer than anywhere else in "
        "the system.",

        "Two are worth reading before you meet them. A branch cannot open a "
        "shift while a previous one remains unclosed — which means an "
        "unfinished close last night becomes an eight-in-the-morning problem "
        "today. And a national identity number cannot be written until the "
        "transparency notice has been presented and the consent recorded, in "
        "that order.",
    ],

    "s8_rules": [
        ["Open a shift while a previous one is still open",
         "Cash cannot be attributed to a shift if two are running.",
         "Close the old one. If nobody present can, the branch manager can — "
         "but it has to happen before the counter opens."],
        ["Close a shift without counting the cash",
         "An uncounted close is not a close.",
         "Count it. The system computes what it expects; you supply what is "
         "there."],
        ["Close with a variance above tolerance and no approval",
         "An unexplained shortfall that nobody reviewed is how small losses "
         "become large ones.",
         "Get the branch manager. Walk the movements together — it is usually "
         "a refund recorded against the wrong method."],
        ["Take a large cash payment without the customer's identity",
         "It is a statutory requirement above the threshold.",
         "Capture it, after the notice. The payment cannot complete "
         "otherwise."],
        ["Hand a device over without verifying who is collecting",
         "Devices have been collected by the wrong people.",
         "Verify. If the customer wants somebody else to collect, they can "
         "nominate them properly."],
        ["Put a device in two storage locations",
         "One of the two is a lie, and at collection nobody will know which.",
         "Move it properly, so the record follows the device."],
        ["Give a Privilege Gold or Diamond member ordinary queue placement",
         "They bought priority service.",
         "Nothing — the system applies it automatically from their tier."],
        ["Mark a token a no-show on the first call",
         "People genuinely miss the first announcement.",
         "Nothing — one recall happens automatically, then the position is "
         "released."],
        ["Spend petty cash above the threshold without approval",
         "A branch float with no approval gate is an unaudited budget.",
         "Get branch manager approval. It is an override, not a block, so it "
         "is recorded rather than refused."],
        ["Sell a membership or protection product without recorded acceptance "
         "of terms",
         "The sale is not enforceable and the customer has no record of what "
         "they bought.",
         "Record the acceptance. It is one action and it is what makes the "
         "sale real."],
        ["Reconcile the shift you handled the cash for",
         "A check by the person being checked is not a check.",
         "Hand it to somebody else. The system will not accept it "
         "otherwise."],
        ["Save an intake without a device and verified customer contact",
         "An order with no device is a dead end, and one with no contact "
         "cannot be notified.",
         "Register the device inline and confirm the contact number. Both take "
         "seconds."],
        ["Write a national identity number before the notice and consent",
         "It is sensitive personal data under the Personal Data Protection Act "
         "2026, and capture without a lawful basis is a rights violation.",
         "Nothing — the notice appears automatically and the field opens after "
         "the acknowledgement."],
        ["Cache, export or print a national identity number",
         "It is written to the Bangladesh-resident store only, and nowhere "
         "else.",
         "Nothing — and if you find a way to do it, report it the same day as "
         "a serious defect."],
    ],

    "s8_note":
        "The two data-protection rules carry an exposure the specification "
        "puts at up to BDT 25 lakh per rights violation. They are not "
        "administrative preferences and they cannot be waived at a branch.",

    # ============================================ 11. automation
    "s9_lede":
        "Twelve behaviours that run without anybody asking, and between them "
        "they are most of what makes a three-minute intake possible.",

    "s9_intro": [
        "The counter is the place where automation is least visible and most "
        "valuable. A token prioritised, a wait estimated, a service order "
        "created, a job sheet printed, a link sent, a shelf assigned — that is "
        "six automatic behaviours inside one intake, and the agent performed "
        "none of them.",

        "Two are protective rather than helpful. When a cash receipt crosses "
        "the statutory threshold, the transparency notice is presented and "
        "consent recorded before the payment can complete. And when a variance "
        "exceeds tolerance, the close is blocked and routed for approval "
        "rather than merely flagged.",
    ],

    "automation_groups": [
        ("In the queue", 3,
         "Token prioritised, wait estimated, next token called and announced"),
        ("At intake and handover", 3,
         "Order created, job sheet printed, link sent, shelf assigned, rating "
         "captured"),
        ("Around cash", 4,
         "Threshold notice, expected balance, variance routing, position to "
         "M50"),
        ("Watching the branch", 2,
         "Uncollected reminders, queue-wait alerts, unopened-shift alerts"),
    ],

    "s9_table": [
        ["Assigns priority by tier and intent, estimates the wait, updates the "
         "display and offers to notify by message",
         "A token is issued",
         "The customer, and the waiting area"],
        ["Calls the next token by priority and sequence, updates the display "
         "and announces it",
         "A counter becomes free",
         "The customer being called, and everybody waiting"],
        ["Creates the service order in M01, prints the job sheet and sends the "
         "acknowledgement and tracking link",
         "An intake is saved",
         "The customer, immediately"],
        ["Assigns a storage location, notifies the customer and adds the "
         "device to the collection list",
         "A device is marked ready by M01 or M31",
         "The customer and the counter"],
        ["Sends escalating reminders, then triggers the abandonment process",
         "A device is uncollected at 3, 7, 15 and 30 days",
         "The customer, then the branch manager"],
        ["Presents the transparency notice, records consent and requires "
         "identity capture before the payment can complete",
         "A cash receipt crosses the statutory threshold",
         "The customer, at the counter"],
        ["Computes the expected balance and presents the count screen",
         "A shift close is requested",
         "The cashier"],
        ["Routes to the branch manager and blocks the close until approved",
         "A variance exceeds tolerance",
         "The branch manager, then operations"],
        ["Emits the cash position to M50 and produces the shift summary",
         "A shift closes",
         "Finance"],
        ["Alerts the branch manager and operations",
         "Opening time arrives with no shift open",
         "The branch manager, at eight in the morning"],
        ["Alerts the branch manager to open another counter",
         "The queue wait passes the configured threshold",
         "The branch manager, before customers leave"],
        ["Prompts for the satisfaction rating and emits the collection event",
         "A handover completes",
         "The customer, and the satisfaction reporting"],
    ],

    # ============================================ 12. permissions
    "s10_lede":
        "Nine roles, one separation of duties, and one field the person who "
        "captures it cannot read back.",

    "s10_intro": [
        "Counter permissions are mostly about money and personal data. Agents "
        "can do everything a counter needs and see nothing about cost or "
        "margin. Cashiers run a drawer. Branch managers approve.",

        "Two restrictions are unusual enough to explain. The person who "
        "handles counter cash cannot perform the shift reconciliation — a "
        "separation of duties the system enforces absolutely. And a customer's "
        "national identity number is write-only at the counter: the agent who "
        "captures it cannot read it back afterwards, and retrieval is limited "
        "to finance and the branch manager with every access logged.",
    ],

    "permissions": {
        "roles": [
            "Operations Director", "Finance Manager", "Branch Manager",
            "Service Centre Agent", "Cashier", "Finance Officer",
            "Inventory Manager", "Quality Manager", "Customer",
        ],
        "actions": ["Take an intake", "Hand a device over", "Run a drawer",
                    "Approve a variance", "Read a captured NID",
                    "See cost and margin"],
        "marks": [
            ["v", "v", "", "y", "", "y"],    # Operations Director
            ["", "", "", "y", "y", "y"],     # Finance Manager
            ["y", "y", "y", "y", "y", "y"],  # Branch Manager
            ["y", "y", "", "", "", ""],      # Service Centre Agent
            ["y", "y", "y", "", "", ""],     # Cashier
            ["", "", "", "", "y", "v"],      # Finance Officer
            ["", "", "", "", "", ""],        # Inventory Manager
            ["", "", "", "", "", ""],        # Quality Manager
            ["", "", "", "", "", ""],        # Customer
        ],
        "sub": "The six actions that decide who controls a counter",
    },

    "s10_roles": [
        ["Service centre agent", "Serving customers at a counter",
         "Nothing exclusive — but they are the only role most customers ever "
         "meet"],
        ["Cashier", "Running a drawer and taking payment",
         "Operating the cash drawer and the shift"],
        ["Branch manager", "Running the branch and approving exceptions",
         "Approving a cash variance, and reading a captured identity number"],
        ["Operations Director", "Comparing branches and setting policy",
         "Approving variance anywhere in the estate"],
        ["Finance manager", "The estate's cash position",
         "Approving variance and reading identity data across all branches"],
        ["Finance officer", "Reconciling within their assigned scope",
         "Reading identity data within scope, with access logged"],
        ["Inventory manager", "What was sold across counters",
         "Read-only on counter sale stock movements"],
        ["Quality manager", "Checklists and satisfaction",
         "Read-only on checklist compliance and counter satisfaction"],
        ["Customer", "Getting a token",
         "Issuing themselves a token by QR code — the only thing they can do "
         "in this module"],
    ],

    "s10_restrictions_intro":
        "Three restrictions are enforced in software and cannot be adjusted at "
        "a branch. Two of them exist because of the Personal Data Protection "
        "Act 2026.",

    "s10_restrictions": [
        ["The customer's national identity number",
         "Write-only at the counter. The agent who captures it cannot read it "
         "back. Retrieval is limited to the finance manager, finance officers "
         "and the branch manager, with every access logged.",
         "It is sensitive personal data. Restricting read access to the "
         "smallest possible set of roles is the control that makes capture "
         "defensible."],
        ["Where identity data is stored",
         "The Bangladesh-resident store only. Never cached locally, never "
         "exported, never printed beyond the statutory receipt.",
         "Data residency is a legal requirement, not a technical preference."],
        ["Cost and margin on counter sales",
         "Hidden from agents.",
         "An agent's advice to a customer should not be shaped by what the "
         "company makes on the item."],
        ["Cash handling and reconciliation",
         "The same person cannot do both.",
         "A separation of duties. It protects honest staff from suspicion at "
         "least as much as it deters anything else."],
        ["Variance approval",
         "The branch manager, the finance manager or the Operations Director. "
         "Never the cashier.",
         "The person whose count produced the variance cannot be the person "
         "who accepts it."],
    ],

    "s10_note":
        "If you can read back a national identity number you captured "
        "yourself, that is a serious defect. Report it the same day rather "
        "than mentioning it at the next branch meeting.",

    # ============================================ 13. measurement
    "s11_lede":
        "Eleven reports and twelve measures, and for the first time they are "
        "comparable across all fifty-one branches.",

    "s11_intro": [
        "Almost nothing at the counter is measured today. Queue wait is "
        "unmeasured. Abandonment is unmeasured. Handling time is unmeasured. "
        "Cash variance incidents are unmeasured. Device retrieval time is "
        "unmeasured. The only number anybody has is roughly how long an intake "
        "takes, and that is an estimate.",

        "The measure to watch above all others is average walk-in intake time, "
        "and specifically its distribution rather than its average. An average "
        "of three minutes with a long tail means some customers are having a "
        "very poor experience, and it usually points at one branch, one agent "
        "or one kind of visit rather than at the software.",
    ],

    "s11_reports": [
        ["Branch daily operations board",
         "What is happening in this branch right now",
         "The branch manager, continuously"],
        ["Queue performance",
         "Tokens issued, average wait, abandonment and the peak hours",
         "Branch managers and operations, daily"],
        ["Counter productivity",
         "Intakes per agent, handling time and satisfaction",
         "The branch manager, weekly"],
        ["Intake time distribution",
         "How the three-minute constraint is actually being met, by branch and "
         "agent",
         "The Operations Director, weekly"],
        ["Cash reconciliation",
         "Position, movements, variance and deposits by branch",
         "The Finance Manager, daily"],
        ["Variance exception report",
         "Variances above tolerance, their approvals, and any pattern",
         "Finance and governance, weekly"],
        ["Uncollected device ageing",
         "Devices ready, by age band, with what has been done about them",
         "Branch managers and operations, daily"],
        ["Counter sales",
         "Memberships, protection products and accessories sold, by branch",
         "The Chief Commercial Officer and finance, monthly"],
        ["Branch comparison",
         "All fifty-one branches on throughput, wait, handling time, "
         "satisfaction and cash discipline",
         "The Operations Director and CEO, monthly"],
        ["Checklist compliance",
         "Whether branches are actually opening and closing properly",
         "Operations and quality, monthly"],
        ["Consent capture completeness",
         "Identity captures with a valid recorded consent",
         "The Chief Data Officer and quality, monthly"],
    ],

    "s11_kpis": [
        ["Average walk-in intake time",
         "The constraint the module is designed around",
         "Under 3 minutes, from about 10 today"],
        ["Average queue wait",
         "How long somebody stands in a branch",
         "Under 12 minutes. Not currently measured"],
        ["Queue abandonment rate",
         "Customers who take a token and leave without being served",
         "Under 4 per cent. Not currently measured"],
        ["Devices located within 60 seconds",
         "Whether the shelf reference is being used properly",
         "Above 98 per cent. Not currently measured"],
        ["Cash variance incidents per branch per month",
         "How well the drawer is being run",
         "Fewer than 1. Not currently measured"],
        ["Shifts closed on time",
         "Whether the closing discipline is holding",
         "Above 97 per cent. Not currently measured"],
        ["Devices uncollected beyond 30 days",
         "How much of the storeroom is dead weight",
         "Under 0.5 per cent. Not currently measured"],
        ["Counter satisfaction rating",
         "What customers thought of the visit",
         "Above 4.5 out of 5. Not currently measured"],
        ["New agent time to competence",
         "How long before somebody can work a counter unsupervised",
         "Under 4 hours, from two to three days"],
        ["Intakes created without the paper form",
         "Whether the module has actually replaced the paper",
         "100 per cent. This is the adoption measure"],
        ["Opening and closing checklist completion",
         "Whether branch discipline is real or decorative",
         "Above 97 per cent, from nothing"],
        ["Identity captures with a valid recorded consent",
         "Whether personal data capture is lawful",
         "100 per cent. Anything less is not a lawful basis"],
    ],

    "dials": [
        ("Walk-in intakes inside three minutes", "<3 min", 0.90),
        ("Devices found within sixty seconds", ">98%", 0.98),
        ("Intakes created without paper", "100%", 1.0),
        ("Identity captures with recorded consent", "100%", 1.0),
    ],

    "s11_reading_title": "Reading the branch board",
    "s11_reading": [
        "The board shows six things at once: today's intake, work in progress, "
        "ready for collection, overdue, revenue and queue health. Five of them "
        "are useful once or twice a day. Queue health needs watching.",

        "A useful pattern for a branch manager is to check queue health "
        "hourly, ready and overdue twice a day, and revenue once. The "
        "uncollected report is a Monday-morning job rather than a daily one, "
        "because the reminder sequence handles the first fifteen days without "
        "you.",
    ],
    "s11_reading_table": [
        ["Queue wait climbing through the morning",
         "Counter capacity is below demand for that period, usually "
         "predictably.",
         "Open another counter now, and look at the peak analysis afterwards. "
         "Saturday mornings are usually the answer."],
        ["Intake time distribution with a long tail",
         "The average looks fine and some customers are having a bad visit.",
         "Look at the tail, not the mean. It is usually corporate intakes or "
         "one agent still learning."],
        ["Ready count rising and collections flat",
         "Customers are not being told, or not being told in a way that "
         "reaches them.",
         "Check contact details before chasing customers. A wrong mobile "
         "number silently disables the whole reminder sequence."],
        ["Recurring variance on one shift pattern",
         "Usually a process issue at that time of day rather than a person.",
         "Look at what is different about that shift — often it is refunds, or "
         "change-giving at a busy period."],
        ["Checklist completion below target in one branch",
         "Either understaffing at opening or a checklist that does not match "
         "that branch.",
         "Ask before enforcing. A checklist item that makes no sense locally "
         "gets clicked through everywhere."],
        ["Satisfaction falling while throughput rises",
         "The branch is going faster and serving worse.",
         "Throughput on its own is not a goal. Read the two together, always."],
    ],

    # ============================================ 14. neighbours
    "s12_lede":
        "M04 is a window onto ten other modules. Almost nothing a customer "
        "sees at a counter is owned here.",

    "s12_intro": [
        "During one three-minute intake the counter reads from the customer "
        "master, the asset registry, the warranty module, the contract module "
        "and the pricing engine, and writes to the service order module, the "
        "receivables module and the treasury module. The agent experiences one "
        "screen; underneath it, eight modules are involved.",

        "That is what makes performance a shared problem rather than a local "
        "one. If entitlement evaluation is slow, the counter is slow, and the "
        "three-minute constraint is missed in a module that did nothing "
        "wrong.",
    ],

    "s12_upstream": [
        ["M33 Party Master", "Who the customer is, and the consent record",
         "Nobody can be found, and personal data cannot be captured lawfully"],
        ["M17 Asset Registry", "Which device this is and what it has been in "
                               "for",
         "Intake cannot be saved — device identification is a hard rule"],
        ["M01 Service Request", "The order the counter creates and hands over",
         "There is nothing to create; the counter becomes a paper process "
         "again"],
        ["M09 Warranty", "Whether cover is active",
         "Entitlement cannot be shown before commit, and the counter starts "
         "promising and hoping again"],
        ["M08 Contract", "Contract cover and service level",
         "Contract customers are treated as walk-ins"],
        ["M11 Pricing", "The rates behind a counter sale or an estimate",
         "Nothing can be sold or quoted"],
        ["M15 Inventory", "What is on the shelf to sell",
         "Counter sales cannot be made"],
        ["M30 Organisation", "The branch, its code, zone and cost centre",
         "A shift has nothing to belong to"],
        ["M55 Workforce", "Who is working which counter",
         "Staffing on the board and the checklist is guesswork"],
        ["M29 Identity", "Who the agent is and what they may do",
         "Nobody can log in and no action is attributable"],
    ],

    "s12_downstream": [
        ["M01 Service Request", "Every walk-in service order",
         "The highest-volume intake channel stops producing records"],
        ["M20 Receivables", "Payments taken at the counter",
         "Counter revenue is not recorded against anything"],
        ["M50 Treasury", "The branch cash position, per shift",
         "The estate's cash position cannot be assembled"],
        ["M15 Inventory", "Counter sale stock movements",
         "Retail stock accuracy degrades branch by branch"],
        ["M33 Party Master", "New customers and consent acknowledgements",
         "The customer master stops growing, and consent has no record"],
        ["M17 Asset Registry", "Devices registered at intake",
         "New devices never enter the estate's record"],
        ["M34 Customer Experience", "Counter satisfaction ratings",
         "Satisfaction cannot be attributed to a branch or an agent"],
        ["M23 Quality", "Checklist compliance and counter exceptions",
         "Branch discipline becomes unmeasurable"],
        ["M12 Analytics", "Throughput, wait, handling time by branch",
         "Branches cannot be compared"],
        ["M31 Workshop", "Devices handed over from branch custody",
         "The workshop receives devices with no origin record"],
    ],

    "s12_close_up": [
        {
            "title": "The relationship that defines the module: M04 and M01",
            "text": [
                "M04 is a channel into M01, and the whole reason it exists "
                "separately is that a channel needs a different shape from the "
                "record it feeds. The service order module has to be complete; "
                "the counter has to be fast. Those are not the same design "
                "problem, and the first version of the plan discovered that by "
                "trying to solve both with one module.",

                "In practice the split means the counter never owns state "
                "logic. An agent saves an intake and M01 creates the order, "
                "assigns the SLA, starts the clocks and sends the "
                "acknowledgement. When the device is later marked ready — by "
                "M01 or by the workshop — M04 assigns a shelf and adds it to "
                "the collection list. The counter is a fast, well-designed "
                "window; it is not a second copy of the truth.",

                "The practical consequence for anybody working at a counter is "
                "that questions about the job belong to M01 and questions "
                "about the visit belong to M04. Where is my device is an M01 "
                "question. Which shelf is it on is an M04 question.",
            ],
        },
        {
            "title": "The relationship that carries legal weight: M04 and M33",
            "text": [
                "The counter is where most personal data enters the company. "
                "Names, telephone numbers, addresses and — above the statutory "
                "cash threshold — national identity numbers are all captured "
                "by an agent under time pressure with a customer waiting. "
                "Under the Personal Data Protection Act 2026 that is the "
                "moment the lawful basis is either established or lost.",

                "The division of responsibility is deliberate. M33 owns the "
                "wording of the transparency notice, its versions, and the "
                "consent record itself. M04 presents the notice at the point "
                "of capture and records that the customer acknowledged it. "
                "That means the notice can be updated centrally when the law "
                "or the practice changes, without touching fifty-one branches "
                "or retraining five hundred people.",

                "It also means neither module can quietly weaken the control. "
                "M04 cannot write the identity field without an acknowledgement "
                "from M33, and M33's notice has no effect unless M04 presents "
                "it. Consent capture completeness is reported monthly against "
                "a target of one hundred per cent, and it is one of the few "
                "measures in this book where anything below target is a legal "
                "exposure rather than a performance gap.",
            ],
        },
    ],

    "s12_note":
        "The three-minute constraint is a shared obligation. If entitlement "
        "evaluation, customer lookup or pricing is slow, the counter misses "
        "its constraint through no fault of its own — which is why counter "
        "response time should be treated as an estate-wide measure, not a "
        "branch one.",

    # ============================================ 15. troubleshooting
    "s13_lede":
        "What goes wrong at a counter, what it usually means, and what to do "
        "with a customer standing in front of you.",

    "s13_intro": [
        "Counter problems have to be resolved in seconds, with somebody "
        "watching. The list below is ordered roughly by how often each one "
        "happens.",
    ],

    "s13_troubleshooting": [
        ["The search does not find the customer",
         "Usually a different number, a spelling variation, or a genuinely new "
         "customer.",
         "Try the mobile number, then the name, then the device serial. Create "
         "only after all three."],
        ["I cannot save the intake",
         "No device identified, or the contact number is unverified.",
         "Register the device inline — it takes seconds. Confirm the number "
         "with the customer while they are there."],
        ["Entitlement says out of warranty and the customer disagrees",
         "The warranty is evaluated at the request date and the device may not "
         "be linked to the right purchase record.",
         "Check the device in M17. If the purchase evidence is genuinely "
         "missing, add it there rather than changing the order type."],
        ["The device is not on the shelf the system says",
         "Somebody moved it without updating the location.",
         "Find it and correct the location immediately. A device cannot be in "
         "two places, and the record has to follow the device."],
        ["Somebody else has come to collect",
         "The customer has sent a relative or a driver.",
         "Do not release it on the job sheet alone. The customer can nominate "
         "a collector properly, which takes them a minute on their phone."],
        ["The shift will not close",
         "Either the cash is uncounted or the variance is above tolerance.",
         "Count it, then get the branch manager if there is a difference. Walk "
         "the movements — it is usually a refund method."],
        ["The branch will not let me open a shift",
         "Last night's shift was left open.",
         "Close it. The branch manager can, and the closing checklist is what "
         "prevents it recurring."],
        ["The identity field will not accept anything",
         "The transparency notice has not been presented and acknowledged.",
         "Show the notice and record the acknowledgement. The field opens "
         "afterwards."],
        ["The queue display is not updating",
         "Usually the display, not the queue.",
         "Call tokens manually from the counter while it is fixed. The queue "
         "itself is unaffected."],
        ["The printer will not produce a job sheet",
         "Thermal printers fail more often than anything else at a counter.",
         "The intake is saved and the tracking link has already been sent; the "
         "customer is not stuck. Reprint when the printer is back."],
        ["Two customer records exist for the same person",
         "Created at two branches, or once by phone and once in person.",
         "Merge in M33. Do not simply use the newer one — history and "
         "entitlement live on the old one."],
        ["A Privilege member says they were not given priority",
         "Either their tier has lapsed or the token was taken before they were "
         "identified.",
         "Check the tier on their record. Priority applies from the tier, and "
         "a kiosk token taken anonymously cannot know who they are."],
    ],

    "s13_faq": [
        ["What if a customer refuses to give their identity for a large cash "
         "payment?",
         "The payment cannot complete above the statutory threshold. Offer "
         "another payment method, or a payment below the threshold. This is "
         "law rather than policy."],
        ["Can I see the identity number I captured this morning?",
         "No. It is write-only at the counter. Retrieval is limited to finance "
         "and the branch manager, with every access logged."],
        ["How do I give priority to somebody who obviously needs it?",
         "Priority is applied by policy from tier, corporate status, age and "
         "accessibility need. If somebody should qualify and does not, raise "
         "it as a policy question rather than resolving it at the counter — "
         "the queue is visible to everybody in it."],
        ["What happens to a token if the customer steps outside?",
         "They are called, then recalled once, then marked as a no-show and "
         "the position is released. If they opted for a message they will have "
         "been told."],
        ["Can I close a shift if the branch manager has gone home?",
         "Only if the variance is inside tolerance. Above it, the finance "
         "manager or Operations Director can also approve — but somebody has "
         "to."],
        ["Why can I not reconcile my own shift?",
         "It is a separation of duties. A check by the person being checked is "
         "not a check, and it protects you as much as it protects the "
         "company."],
        ["Is the three-minute target a performance measure for me?",
         "It is a design constraint on the software first. Intake time is "
         "reported by branch and by agent, and a distribution with a long tail "
         "usually points at a kind of visit rather than a person."],
        ["Do I have to complete the opening checklist if the branch was open "
         "yesterday?",
         "Yes, daily. Completion is reported monthly, and the items on it are "
         "precisely the ones that cause the day to go wrong when skipped."],
        ["A customer wants to buy a membership. What do I have to record?",
         "Their acceptance of the terms. The sale is not valid without it and "
         "the system will not complete it."],
        ["What do I do with a device nobody has collected for a month?",
         "Nothing. The reminder sequence has run at 3, 7, 15 and 30 days, and "
         "at thirty days M01 starts the abandonment process with statutory "
         "notice."],
    ],

    # ============================================ 16. worth
    "s14_lede":
        "Seven minutes per customer, across the highest-volume channel in the "
        "business — and a cash control that pays for the module on its own.",

    "s14_intro": [
        "The headline benefit is arithmetic. Reducing a walk-in intake from "
        "about ten minutes to under three releases roughly seven minutes per "
        "customer on the highest-volume service delivery mode the company "
        "operates. At around a quarter of a million monthly interactions, a "
        "material fraction of them walk-in, that is a large amount of counter "
        "capacity that does not have to be hired.",

        "The benefit that is easier to overlook is the cash control. The "
        "specification is direct about it: the control pays for the module. "
        "Shift discipline, recorded movements, enforced variance approval and "
        "blocked rollover between shifts, in fifty-one branches, is worth more "
        "than the software costs to build.",
    ],

    "benefits": [
        ("Intake capacity released", 7, "7 minutes per walk-in"),
        ("Data-protection exposure avoided", 25, "up to BDT 25 lakh per "
                                                 "violation"),
    ],
    "benefits_note": ("Cash leakage control and abandonment reduction are "
                      "expressed as rates rather than annual values."),

    "s14_benefits": [
        ["Intake capacity",
         "Ten minutes to three per walk-in, on the highest-volume delivery "
         "mode in the business",
         "About seven minutes released per customer, at roughly 250,000 "
         "monthly interactions"],
        ["Cash leakage control",
         "Shift discipline, recorded movements, enforced variance approval and "
         "blocked shift rollover",
         "Fewer than one variance incident per branch per month. The "
         "specification says this control alone pays for the module"],
        ["Customer abandonment reduction",
         "Visible wait times address the eight-minute threshold at which "
         "people leave",
         "Walk-ins retained that would otherwise have walked out"],
        ["Device retrieval time",
         "Storage location recorded at intake and used at collection",
         "Over 98 per cent located within sixty seconds, removing the most "
         "visible source of counter embarrassment"],
        ["Uncollected device recovery",
         "Systematic ageing, reminders and escalation",
         "Devices uncollected beyond thirty days below 0.5 per cent, freeing "
         "storage and recovering revenue already earned"],
        ["Counter sales uplift",
         "Memberships, warranty extensions and accessories offered at the "
         "moment of contact",
         "Contributes to Privilege base growth and warranty attach rate"],
        ["Data quality at source",
         "The counter is where most data enters the system; getting it right "
         "here prevents error everywhere downstream",
         "Underpins every measure in service, customer and finance"],
        ["Data-protection penalty avoidance",
         "Consent and notice recorded at capture rather than reconstructed "
         "after a complaint",
         "Avoids exposure the specification puts at up to BDT 25 lakh per "
         "rights violation"],
    ],

    "s14_soft": [
        ["The first impression of the whole transformation",
         "For most customers and most staff, M04 is the ERP. Its usability "
         "determines the programme's reputation internally more than any other "
         "module."],
        ["An adoption anchor",
         "If the counter works well, branch staff advocate for the rest of the "
         "system. If it does not, they resist all of it — including the parts "
         "that are excellent."],
        ["Standardisation across fifty-one branches",
         "One process, one job sheet, one gate pass. This is the foundation of "
         "the ISO 9001 claim that wins corporate tenders."],
        ["Dignity in queueing",
         "A token and a stated wait is a materially better experience than an "
         "undefined crowd, particularly for elderly customers."],
        ["Protection for honest staff",
         "Recorded cash movements protect the many from suspicion at least as "
         "much as they deter the few."],
        ["Training becomes manageable",
         "A new agent reaching competence in four hours rather than three days "
         "makes branch expansion and staff turnover survivable."],
        ["A lawful basis at the point of collection",
         "Consent captured at the counter is the only defensible way to "
         "satisfy the Personal Data Protection Act for walk-in customers."],
    ],

    "s14_close":
        "Judge this module on one number above all others: the proportion of "
        "intakes created without the paper form. If it is not one hundred per "
        "cent, the counter is slower than the paper somewhere, and everything "
        "downstream is inheriting the difference.",

    # ============================================ 17. learning it
    "s17_lede":
        "Four hours to competence is the target, against two to three days "
        "today. It is achievable because the module is narrow.",

    "s17_intro": [
        "A counter agent uses perhaps fifteen functions. The plan below gets "
        "somebody serving customers on their first afternoon and confident "
        "within a fortnight, and it deliberately teaches intake before "
        "anything else.",

        "The reason for that order is that almost every problem later in a job "
        "traces back to the first three minutes. An agent who takes a clean "
        "intake and can find anything is useful immediately, even if they "
        "cannot yet run a drawer.",
    ],

    "s17_plan": [
        ["Before you start",
         "Read section 1, then find yourself in section 2, then read the "
         "intake walkthrough in section 8.",
         "20 minutes",
         "Know what a good intake looks like"],
        ["Hour one",
         "Watch three real intakes. Do not touch anything. Time them.",
         "1 hour",
         "Recognise the shape of the three-minute flow"],
        ["Hour two",
         "Take one intake yourself with somebody beside you, then find it "
         "again three ways: phone, serial, order number.",
         "1 hour",
         "Create a record and retrieve it"],
        ["Hour three",
         "Read section 6.2 in full. Take three more intakes, including one "
         "where the device is not on the record.",
         "1 hour",
         "Take a job in unaided"],
        ["Hour four",
         "Do two collections: verify identity, retrieve from the shelf, "
         "confirm accessories, capture the signature, print the gate pass.",
         "1 hour",
         "Serve a counter unsupervised"],
        ["Day two",
         "Read section 10. Deliberately try three things the system refuses "
         "and read the message each time.",
         "30 minutes",
         "Recognise a rule rather than assuming a fault"],
        ["Day three",
         "Read section 6.3 if you will handle cash. Open and close a shift "
         "alongside the cashier.",
         "45 minutes",
         "Run a drawer"],
        ["End of week one",
         "Read section 6.1 on the queue and section 11 on what runs "
         "automatically.",
         "30 minutes",
         "Stop doing by hand what the system already does"],
        ["Week two",
         "Read section 15, and section 6.4 if you supervise. Save the two list "
         "views you will use every morning.",
         "40 minutes",
         "Diagnose before escalating"],
        ["End of week two",
         "Read section 18 and keep it at the counter.",
         "15 minutes",
         "Work unsupervised"],
    ],

    "s17_check_intro":
        "You have got it when you can do all of these without hesitating with "
        "a customer in front of you. Most agents get there in about forty real "
        "intakes.",

    "s17_checks": [
        "Take a clean intake for a new customer and an unknown device inside "
        "three minutes",
        "Find any job from any single thing a customer can remember",
        "Say who pays before the customer asks",
        "Complete a collection in under two minutes, including identity "
        "verification",
        "Open and close a shift, and explain a variance",
        "Show the transparency notice and capture consent without prompting",
        "Recognise when the system is enforcing a rule rather than "
        "malfunctioning",
        "Know the three things to report the same day: an identity number you "
        "can read back, an intake screen consistently over three minutes, and "
        "a device found on the wrong shelf",
    ],

    "s17_note":
        "Remove the paper form on day one. A branch that keeps a paper "
        "fallback will still be using it in six months, and the data in the "
        "system will be wrong in ways nobody can see.",

    # ============================================ 18. one page
    "s15_lede":
        "The module on one page, for the back of a counter.",

    "s15_figures": [
        ("32", "things you can do"),
        ("3 min", "the intake constraint"),
        ("14", "rules enforced"),
        ("12", "automatic behaviours"),
        ("11", "token states"),
        ("4 hrs", "to competence"),
        ("11", "reports available"),
        ("10", "modules depend on it"),
    ],

    "s15_never": [
        "Save an intake without identifying the device and verifying the "
        "contact",
        "Hand a device over without verifying who is collecting it",
        "Record a device in two storage locations",
        "Take a large cash payment without the customer's identity",
        "Write an identity number before the notice has been shown and consent "
        "recorded",
        "Close a shift without counting, or with an unapproved variance",
        "Open a shift while a previous one is still open",
        "Reconcile the shift you handled the cash for",
        "Sell a membership without recording acceptance of terms",
    ],

    "s15_where": CM.where_to_look("M04"),
}
