# -*- coding: utf-8 -*-
"""
Category A — Service Delivery & Operations.

The category guide book: how the seven modules fit together, which one owns
what, and which one a given reader should open next. Deliberately shorter than
a module book — depth is one page reference away.
"""

CONTENT = {

    "cover_line":
        "Everything that happens to a customer's device from the moment they "
        "ask for help until it is back in their hands — across seven modules, "
        "nine ways of delivering service, and fifty-one branches.",

    "cover_gists": {
        "M01": "the service order, and everything attached to it",
        "M02": "who goes where, and the technician's phone",
        "M03": "moving things, and proving who held them",
        "M04": "the counter, the queue and the cash drawer",
        "M05": "watching clients' equipment under contract",
        "M06": "recovering data, and destroying it properly",
        "M31": "the workshop bench",
    },

    "about":
        "This guide book explains how the seven Service Delivery and "
        "Operations modules fit together. It is written for somebody who needs "
        "the shape of the whole category rather than the detail of one module "
        "— a new joiner, a manager whose work crosses two of them, or anybody "
        "trying to work out which of the seven books to open. Every module has "
        "its own guide book, and this one points at them.",

    "audience":
        "New joiners, managers whose work spans more than one module, and "
        "anybody deciding which module guide book to read.",

    "read_when":
        "Before your first module guide book, and again whenever you start "
        "working with a team from a different module.",

    "reading_note":
        "Read section 1 to see what the category covers, then find your own "
        "module in section 2, then read the journey in section 6 that "
        "describes the work you actually do. Twenty minutes, and you will know "
        "which of the seven books to open next.",

    # ============================================================ exhibits
    "headline": [
        ("7", "modules in the category", "one of them new in v2.1"),
        ("355", "distinct functions", "measured, not estimated"),
        ("206", "person-weeks to build", None),
        ("9", "service delivery modes", "all seven modules support all nine"),
        ("51+", "branches", None),
        ("250,000+", "customer interactions a month", None),
        ("6", "delivery waves", "first transactions in Wave 1"),
        ("35", "identifiers retired unused", "never reissued"),
    ],

    "effort_bars": [
        ("M01 Service Request and Order Management", 46),
        ("M02 Field Service and Dispatch", 40),
        ("M05 Remote Support and Managed Services", 37),
        ("M31 Workshop and Depot Repair", 30),
        ("M03 Service Logistics", 22),
        ("M06 Data Services", 18),
        ("M04 Branch and Front-Desk Operations", 13),
    ],

    "modes_ribbon": [
        ("Walk-in at a service centre", "M04 then M31", "highest volume"),
        ("On-site or home service", "M01 then M02", None),
        ("Pick and drop", "M01, M03, M31, M03", "custody-critical"),
        ("Remote support", "M01 then M05", None),
        ("Workshop or depot repair", "M31", "board-level"),
        ("Preventive maintenance", "M08 then M02", "contract-driven"),
        ("Managed-service incident", "M05 then M02", "alert-driven"),
        ("Marketplace-fulfilled", "M12, M01, M02", "outside seller"),
        ("Data services", "M06", "confidentiality-controlled"),
    ],

    "wave_ribbon": [
        ("Wave 1", "M04 and M01 core", "first transactions"),
        ("Wave 2", "M01 complete, M31, M02", "full service execution"),
        ("Wave 3", "M03 Logistics", "pick and drop, custody"),
        ("Wave 5", "M05 Managed Services", "the MSP business line"),
        ("Wave 6", "M06 Data Services", "the data business line"),
    ],

    "split_title": "Why the service order and the repair order are separate",
    "split_sub": "The most important boundary in the category, and the one the "
                 "first draft got wrong",
    "split_columns": [
        ("M01 Service Request", "The customer's question", [
            "One record per customer need",
            "Changes a handful of times over days",
            "The customer sees it and tracks it",
            "Carries the promise and the SLA clock",
            "Says: in progress",
        ]),
        ("M31 Workshop Repair", "The workshop's question", [
            "One record per piece of bench work",
            "Changes fifteen times over hours",
            "No customer-facing surface at all",
            "Carries the bench, the components, the tests",
            "Says: awaiting a Level 3 bench, fourth in queue",
        ]),
    ],

    "owns_map": [
        ("M01 Service order", 70, "The customer's request, one per need."),
        ("M02 Work order", 63, "An assignable unit of field work."),
        ("M31 Repair order", 53, "An assignable unit of workshop work."),
        ("M03 Consignment", 42, "A movement of items, with custody."),
        ("M05 MSP ticket", 62, "A contracted client's support request."),
        ("M06 Data case", 34, "A confidentiality-controlled engagement."),
        ("M04 Queue token", 31, "A walk-in customer's place in line."),
    ],

    "dials": [
        ("Jobs per technician per day, against a target of 9", "8-9", 0.90),
        ("Repairs right the first time", "88%", 0.88),
        ("Walk-in intake inside three minutes", "<3 min", 0.90),
        ("Chain-of-custody exceptions, ceiling of zero", "0", 1.0),
    ],

    "risk_rows": [
        ("M02 Field Service",
         "Technicians reject the mobile application. The field model then "
         "collapses, and inventory accuracy, invoicing speed, warranty "
         "recovery and quality data all degrade with it.",
         "Bengali first, extreme simplicity, a field pilot before rollout, and "
         "visible earnings in the app. Adoption is treated as a business "
         "metric, not a technical one."),
        ("M31 Workshop",
         "Workshop staff keep a parallel paper board, so nothing is visible in "
         "real time and the measurement never becomes honest.",
         "The bench board goes on a wall-mounted screen, and the quality gate "
         "cannot be bypassed — so the paper board stops being sufficient."),
        ("M04 Branch",
         "Counter intake is slower than the paper form it replaces, so branch "
         "staff keep the paper and every module downstream inherits bad data.",
         "Three-minute intake is a hard design constraint and it is measured "
         "by branch and by agent, with the distribution watched rather than "
         "the average."),
        ("M03 Logistics",
         "Custody breaks during pick and drop, leaving the company with legal "
         "exposure on lost devices it cannot account for.",
         "A scan and both parties' identity at every handover, with no "
         "exceptions, into a ledger that can be added to and never edited."),
        ("M06 Data Services",
         "A confidentiality breach. Regulatory and reputational, and a single "
         "incident costs more than the module.",
         "Least privilege with per-case access, dual control on media, "
         "encryption with case-specific keys, and a full audit trail retained "
         "for five years."),
    ],

    # ============================================================ 1
    "s1_lede":
        "Everything that happens to a customer's device or IT estate from the "
        "moment a service need arises until the work is complete and the "
        "device is back in their hands.",

    "s1_intro": [
        "Category A is the operational heart of 1000FiX. It contains the "
        "modules that do the work the company is paid for: taking the request "
        "in, deciding who does it, doing it at a bench or at a customer's "
        "site, moving the device between the two, watching contracted "
        "equipment so it does not break, and handling the data on it.",

        "Seven modules, three hundred and fifty-five distinct functions, and "
        "two hundred and six person-weeks to build. It is the largest category "
        "in the programme and the first to be delivered, because almost "
        "nothing else in the system has anything to do until service delivery "
        "produces records for it to work on.",

        "One of the seven is new. M31 Workshop and Depot Repair did not exist "
        "in the first version of the plan; workshop execution sat inside the "
        "service order module. Splitting it out is the most consequential "
        "structural decision in the category and section 5 explains why.",
    ],

    "s1_modules": [
        ["M01 Service Request and Order Management",
         "The service order — the master record of every customer service "
         "need, from any channel, for any business line",
         "Wave 1 core, Wave 2 complete"],
        ["M04 Branch and Front-Desk Operations",
         "The counter at 51+ service centres: queue, intake, handover, cash "
         "and shift discipline",
         "Wave 1"],
        ["M31 Workshop and Depot Repair Management",
         "In-house bench repair: workshop routing, Level 1, 2 and 3 work, "
         "component-level repair, test and burn-in",
         "Wave 2 — new in this version"],
        ["M02 Field Service and Dispatch Management",
         "Who does field work, when and in what order — and the technician's "
         "mobile application",
         "Wave 2"],
        ["M03 Service Logistics and Reverse Logistics",
         "Moving devices, parts and assets between customers, branches, "
         "workshops, vendors and recyclers, with unbroken custody",
         "Wave 3"],
        ["M05 Remote Support and Managed Services",
         "Remote assistance and contracted managed IT services, with "
         "monitoring, alerting and service-level reporting",
         "Wave 5"],
        ["M06 Data Services and Secure Data Handling",
         "Data recovery, backup subscriptions, migration and certified "
         "destruction under controlled custody",
         "Wave 6"],
    ],

    "s1_test":
        "If a capability answers 'what work is being done, by whom, where, and "
        "to what standard', it belongs in Category A. If it answers 'what does "
        "it cost' or 'who is the customer', it does not.",

    # ============================================================ 2
    "s2_lede":
        "Seven modules, and each one owns exactly one kind of record. Learning "
        "which is which is most of what this book is for.",

    "s2_intro": [
        "The cleanest way to hold seven modules in your head is by the record "
        "each one owns. A service order is a customer's request. A work order "
        "is an instruction to a person to do field work. A repair order is a "
        "piece of bench work. A consignment is a movement. A queue token is a "
        "place in line. A managed-service ticket is a contracted client's "
        "request. A data case is a confidentiality-controlled engagement.",

        "Those seven records do not overlap, and that is deliberate. One "
        "customer request can produce several of the others — a service order "
        "generating a work order, two consignments and a repair order is an "
        "ordinary pick-and-drop repair — but each record has exactly one "
        "owner and one purpose.",
    ],

    "module_cards": [
        {
            "number": "2.1",
            "title": "M01 — Service Request and Order Management",
            "text": [
                "The record everything else hangs off. M01 owns the service "
                "order: one numbered record of everything a customer has asked "
                "for, from any of twelve intake channels, across nine delivery "
                "modes and fourteen revenue streams. Sixteen other modules "
                "depend on it, which is more than anything else in the "
                "system.",

                "It does not repair, move, price or invoice anything. What it "
                "does is hold the one true statement of what was asked for, "
                "what was promised, what has happened and what is left — and "
                "answer the question staff are asked more than any other: what "
                "is happening with my device?",
            ],
            "facts": [
                ("Owns", "The service order"),
                ("Biggest single idea", "One record, whatever channel the "
                                        "request arrived on"),
                ("Read it if", "You take jobs in, run a branch, or need to "
                               "know where anything is"),
                ("Its own guide book", "GB-M01, seventy functions in eighteen "
                                       "sections"),
            ],
        },
        {
            "number": "2.2",
            "title": "M04 — Branch and Front-Desk Operations",
            "text": [
                "The counter. The module that between one hundred and fifty "
                "and two hundred and fifty agents will touch more than any "
                "other, and the first thing a walk-in customer experiences of "
                "the whole programme.",

                "Its design constraint is a stopwatch: a walk-in intake in "
                "under three minutes, against about ten on paper today. If the "
                "software is slower than the paper it replaces, branch staff "
                "keep the paper and every module downstream inherits the bad "
                "data. Everything else in M04 — the queue, the shelf "
                "reference, the cash drawer, the shift discipline — serves "
                "that one number.",
            ],
            "facts": [
                ("Owns", "The queue token, the storage location, the cash "
                         "drawer and the shift"),
                ("Biggest single idea", "Three-minute intake, or staff keep "
                                        "the paper"),
                ("Read it if", "You work at, manage or audit a branch"),
                ("Its own guide book", "GB-M04, thirty-two functions"),
            ],
        },
        {
            "number": "2.3",
            "title": "M31 — Workshop and Depot Repair Management",
            "text": [
                "What happens at a bench: which bench, which technician, which "
                "components, which tests, and how long each of them took. This "
                "is the module the first version of the plan did not have.",

                "It exists because bench work has a completely different "
                "rhythm from a field visit — parallel work in progress, "
                "component-level part consumption, static-controlled "
                "environments, calibrated instruments, burn-in measured in "
                "hours, and a queue balanced across three certification "
                "levels. It has no customer-facing surface at all.",
            ],
            "facts": [
                ("Owns", "The repair order, the bench and the workshop"),
                ("Biggest single idea", "Forty per cent more devices per bench "
                                        "per day, from measurement alone"),
                ("Read it if", "You work at a bench or supervise a workshop"),
                ("Its own guide book", "GB-M31, fifty-three functions"),
            ],
        },
        {
            "number": "2.4",
            "title": "M02 — Field Service and Dispatch Management",
            "text": [
                "Two halves that belong together: the dispatch board three to "
                "eight managers work from, and the mobile application two to "
                "four hundred technicians will live inside for eight hours a "
                "day.",

                "The specification is blunt that the application is the "
                "highest-risk artefact in the whole programme. If technicians "
                "reject it, the field model collapses and inventory accuracy, "
                "invoicing speed, warranty recovery and quality data all "
                "degrade with it. It also carries the largest single "
                "operational benefit in the programme: four or five jobs a "
                "technician per day today, eight or nine as the target.",
            ],
            "facts": [
                ("Owns", "The work order and the technician application"),
                ("Biggest single idea", "The app has to work with no signal, "
                                        "for a full day"),
                ("Read it if", "You dispatch, work in the field, or depend on "
                               "field data"),
                ("Its own guide book", "GB-M02, sixty-three functions"),
            ],
        },
        {
            "number": "2.5",
            "title": "M03 — Service Logistics and Reverse Logistics",
            "text": [
                "Every physical movement of every item, and the unbroken "
                "record of who held it. An ordinary pick-and-drop repair "
                "passes through six pairs of hands, and today that journey is "
                "coordinated by telephone and recorded nowhere.",

                "The module's real product is not a delivery service; it is a "
                "proof. Everything else — scheduling, routing, courier "
                "integration, charging — exists to produce a custody ledger "
                "that can be added to and never edited, naming who held each "
                "item at every moment.",
            ],
            "facts": [
                ("Owns", "The consignment and the custody ledger"),
                ("Biggest single idea", "A scan and both identities at every "
                                        "handover, with no exceptions"),
                ("Read it if", "You are a rider, a coordinator, or you hand "
                               "devices to anybody"),
                ("Its own guide book", "GB-M03, forty-two functions"),
            ],
        },
        {
            "number": "2.6",
            "title": "M05 — Remote Support and Managed Services",
            "text": [
                "The module that turns 1000FiX from a company that fixes "
                "things when they break into one that stops them breaking, "
                "under contract, for a monthly fee.",

                "It is the highest-margin business line described anywhere in "
                "the company's documentation and the only one with recurring "
                "revenue and declining marginal cost. Six contract types and a "
                "24/7 support commitment are already sold; neither currently "
                "has a system behind it.",
            ],
            "facts": [
                ("Owns", "The managed-service ticket and the monitored "
                         "estate"),
                ("Biggest single idea", "Every alert that ends without a "
                                        "person is margin"),
                ("Read it if", "You support corporate clients or sell "
                               "contracts"),
                ("Its own guide book", "GB-M05, sixty-two functions"),
            ],
        },
        {
            "number": "2.7",
            "title": "M06 — Data Services and Secure Data Handling",
            "text": [
                "Recovering customers' data when they have lost it, and "
                "destroying it when the device leaves the company. Two things "
                "that look unrelated and are the same thing: temporary "
                "possession of information 1000FiX must never read, copy, "
                "retain or lose.",

                "It is the most confidentiality-critical module in the system "
                "and the only one where a single failure is a regulatory "
                "incident rather than an operational one. It also gates two "
                "other business lines outright: no device may be refurbished "
                "or recycled without a certificate produced here.",
            ],
            "facts": [
                ("Owns", "The data case and the certificate of destruction"),
                ("Biggest single idea", "Five of its twelve targets are zero "
                                        "or one hundred per cent"),
                ("Read it if", "You handle media, or you refurbish or recycle "
                               "anything"),
                ("Its own guide book", "GB-M06, thirty-four functions"),
            ],
        },
    ],

    # ============================================================ 3
    "s3_lede":
        "Nine ways the company can serve a customer, and every module in the "
        "category has to support all nine.",

    "s3_intro": [
        "A walk-in repair, an engineer at a customer's office, a device "
        "collected and returned, a fault fixed over a remote connection, a "
        "board rebuilt at a bench, a quarterly preventive visit, an alert from "
        "a monitored printer, a job fulfilled by a marketplace seller, a "
        "failed drive in a clean-room. Nine modes, and a customer may use "
        "several of them in a year.",

        "The decision the programme took is that a delivery mode is "
        "configuration rather than code. That means a new mode — a tenth way "
        "of serving somebody — is a configuration exercise rather than a "
        "project, and it is why the service order is a thin core with typed "
        "extensions rather than nine separate order types.",
    ],

    "s3_modes": [
        ["Walk-in at a service centre", "M04, then M31",
         "The highest-volume mode, and the one with a three-minute constraint "
         "on it"],
        ["On-site or home service", "M01, then M02",
         "Appliance and corporate work. The technician travels"],
        ["Pick and drop", "M01, M03, M31, then M03 again",
         "Custody-critical: six handovers on a single journey"],
        ["Remote support", "M01, then M05",
         "Software and configuration faults, resolved without travelling"],
        ["Workshop or depot repair", "M31",
         "Board-level and specialist work at a bench"],
        ["Preventive or scheduled maintenance", "M08, then M02",
         "Contract-driven. Nobody raises it; a maintenance plan does"],
        ["Managed-service incident", "M05, then M02",
         "Alert-driven. The equipment reports its own fault"],
        ["Marketplace-fulfilled", "M12, M01, then M02",
         "An outside seller executes, and 1000FiX remains accountable"],
        ["Data services", "M06",
         "Confidentiality-controlled from the moment the case is created"],
    ],

    "s3_note":
        "Only two of the nine modes involve a customer walking through a door. "
        "Five of them start without a person raising anything at all — a "
        "contract plan, a monitoring alert, a marketplace transaction. That "
        "shift, from work that arrives to work that generates itself, is the "
        "quiet change this category makes.",

    # ============================================================ 4
    "s4_lede":
        "Nine words that all seven modules use in exactly the same way. "
        "Divergence is a defect, not a dialect.",

    "s4_intro": [
        "Seven modules built by different squads will drift apart in their "
        "vocabulary unless somebody holds them together. These nine terms are "
        "held deliberately: each one has a single definition and a single "
        "owning module, and every guide book in the category uses them the "
        "same way.",

        "The distinction that causes the most confusion in practice is between "
        "a service order, a work order and a repair order. They are not three "
        "names for the same thing. One customer request produces one service "
        "order and may produce several of the other two.",
    ],

    "s4_vocab": [
        ["Service order", "The customer's request. One per need.", "M01"],
        ["Work order", "An assignable unit of field work.", "M02"],
        ["Repair order", "An assignable unit of workshop work.", "M31"],
        ["Consignment", "A movement of physical items, with custody.", "M03"],
        ["Queue token", "A walk-in customer's place in line.", "M04"],
        ["Managed-service ticket", "A contracted client's support request.",
         "M05"],
        ["Data case", "A confidentiality-controlled data engagement.", "M06"],
        ["Visit", "One physical attendance at a location.", "M02"],
        ["Custody event", "A transfer of physical possession.",
         "M03, shared with the others"],
    ],

    # ============================================================ 5
    "s5_lede":
        "Most of what a module in this category touches belongs to somebody "
        "else. Knowing which is which prevents more duplicated work than any "
        "other page here.",

    "s5_intro": [
        "Category A modules are execution modules. They do the work, and "
        "almost everything they need in order to do it — who the customer is, "
        "what the device is, what it costs, what the contract covers, whether "
        "the technician is certified — belongs to a module in another "
        "category.",

        "The table below is the anti-overlap control for the whole category. "
        "Every row names one capability, the module that owns it, and the "
        "modules that use it without owning it. A boundary that only one side "
        "agrees to is the single commonest cause of duplicated build effort.",
    ],

    "s5_boundary": [
        ["Customer identity", "M33 Party Master",
         "M01 references it and never edits it"],
        ["Device identity and history", "M17 Asset Registry",
         "M01 and M31 reference it; M31 writes component genealogy back"],
        ["Estimate and price", "M36 Quotation and M11 Pricing",
         "M01 displays what comes back; it never calculates"],
        ["Contract entitlement", "M08 Contract",
         "M01 and M05 validate against it"],
        ["Warranty entitlement", "M09 Warranty",
         "M01 validates against it; M31 supplies the evidence"],
        ["Parts stock and value", "M15 Inventory",
         "M31 and M02 consume; neither holds or values stock"],
        ["Technician availability", "M55 Workforce",
         "M02 consumes it and never maintains it"],
        ["Technician competency", "M22 Competency",
         "M02 and M31 enforce the gate; neither certifies"],
        ["The invoice", "M20 Receivables",
         "M01 triggers it and never creates it"],
        ["Quality checklists", "M23 Quality",
         "M01 and M31 execute them; neither authors them"],
        ["Customer notification", "M27 Contact Centre",
         "All seven raise events; none of them sends"],
        ["Vehicles and vans", "M46 Fleet",
         "M02 and M03 use them; neither manages them"],
    ],

    "split_heading": "The boundary that mattered most: M01 and M31",

    "s5_split": [
        "The first version of the plan had no separate workshop module; "
        "workshop execution sat inside the service order. Splitting them is "
        "the most consequential structural decision in the category, and it "
        "was taken for the same reason every tier-one service system takes it. "
        "SAP calls the second object In-House Repair, IFS calls it the Repair "
        "Shop, Oracle and QAD call it Depot Repair.",

        "They separate them because the two objects answer different "
        "questions, change at different rates, and have completely different "
        "audiences. A service order changes a handful of times over days and a "
        "customer watches it. A repair order changes fifteen times over hours "
        "and a workshop supervisor watches it.",

        "The practical consequence is the sentence worth remembering: a "
        "customer's tracking view shows 'in progress' while the workshop board "
        "shows 'awaiting a Level 3 board technician, position four in the "
        "queue'. Both are true. The customer does not need the second "
        "sentence and the workshop cannot work without it.",
    ],

    # ============================================================ 6
    "s6_lede":
        "Three journeys that cross several modules, which is how most real "
        "work actually behaves.",

    "s6_intro": [
        "Reading seven module guide books tells you what each module does. It "
        "does not tell you what a job feels like as it moves between them, and "
        "that is where most confusion between teams comes from.",

        "The three journeys below are the commonest multi-module paths in the "
        "category. Each one names the module that owns each step, so that when "
        "something goes wrong you know whose guide book to open.",
    ],

    "journeys": [
        {
            "number": "6.1",
            "title": "A pick-and-drop repair",
            "text": [
                "The most module-crossing journey in the company, and the one "
                "where custody matters most. A customer's laptop is collected "
                "from their home, repaired at a central workshop, and returned "
                "— passing through six pairs of hands and four modules.",
            ],
            "steps": [
                ["1", "M01 Service Request",
                 "The request is taken, the customer and device identified, "
                 "entitlement resolved and a service order created with its "
                 "clock running."],
                ["2", "M03 Logistics",
                 "A consignment is created with four legs. A rider collects "
                 "with a scan, both identities, an OTP, a signature and a "
                 "photograph of the sealed package."],
                ["3", "M04 Branch",
                 "The device reaches a branch and is scanned in. A storage "
                 "location is recorded so nobody has to search for it later."],
                ["4", "M03 Logistics",
                 "It travels to the central workshop on the scheduled shuttle, "
                 "with custody transferring at each handover."],
                ["5", "M31 Workshop",
                 "Booked in against the consignment with condition verified. "
                 "Benched, diagnosed, repaired, burn-in run, quality checked, "
                 "released."],
                ["6", "M03 and M04",
                 "Back to the branch, then to the customer, with proof of "
                 "delivery captured. The service order closes and the billable "
                 "event fires."],
            ],
        },
        {
            "number": "6.2",
            "title": "An on-site visit that could not be completed",
            "text": [
                "The second commonest cross-module path, and the one that "
                "tests whether the modules hand over cleanly. A technician "
                "arrives, finds the work needs a bench, and the job has to "
                "continue somewhere else without starting again.",
            ],
            "steps": [
                ["1", "M01 Service Request",
                 "An on-site service order is created and handed to field "
                 "service as work to be dispatched."],
                ["2", "M02 Field Service",
                 "Candidates are scored, a technician assigned, and the "
                 "overnight route solve places the visit. The customer sees an "
                 "arrival estimate on a map."],
                ["3", "M02 Field Service",
                 "On site, the fault turns out to be board-level and cannot be "
                 "done on a kitchen floor. Cannot-complete is recorded with "
                 "the reason and photographs."],
                ["4", "M03 Logistics",
                 "The visit converts to a collection. A consignment is "
                 "created; the customer chooses a pick-up slot from the "
                 "tracking link."],
                ["5", "M31 Workshop",
                 "The device arrives with the field diagnosis already "
                 "attached, so the bench technician does not repeat it."],
                ["6", "M01 Service Request",
                 "One service order throughout. The customer sees one job, "
                 "one clock and one promise, not three separate events."],
            ],
        },
        {
            "number": "6.3",
            "title": "A monitored printer that booked its own service",
            "text": [
                "The journey that shows what the category looks like when it "
                "is working well: nobody telephoned anybody, and the first the "
                "customer heard was a proposed visit slot.",
            ],
            "steps": [
                ["1", "M05 Managed Services",
                 "A printer under a managed print contract reports that its "
                 "fuser has passed ninety per cent of rated life. An alert is "
                 "raised and correlated."],
                ["2", "M05 Managed Services",
                 "The contract covers preventive replacement, so the alert is "
                 "escalated as work rather than as an incident."],
                ["3", "M01 Service Request",
                 "A service order is created automatically with the order type "
                 "set to managed service, entitlement already resolved, and "
                 "the customer and device already known."],
                ["4", "M02 Field Service",
                 "It enters the dispatch queue against the contract's "
                 "preventive window rather than an emergency clock. A "
                 "technician with the part on the van is assigned."],
                ["5", "M02 and M15",
                 "The fuser is replaced on site, scanned off the van, and the "
                 "van's replenishment request raises itself."],
                ["6", "M05 Managed Services",
                 "The intervention appears in the client's monthly service "
                 "report as planned maintenance rather than as an outage."],
            ],
        },
    ],

    # ============================================================ 7
    "s7_lede":
        "Six waves, and the first two carry most of the category. Nothing much "
        "else in the programme can start until they land.",

    "s7_intro": [
        "The sequence below is not arbitrary. M04 and the core of M01 come "
        "first because until a branch can take a job in and create a record, "
        "the system has nothing to work on. The workshop and field service "
        "follow immediately, because a record with no execution behind it is "
        "worse than paper.",

        "Logistics arrives in Wave 3, which unlocks pick and drop and the "
        "custody chain the circular business lines depend on. Managed services "
        "and data services come later — both are new business lines rather "
        "than replacements for existing work, and both can wait until the core "
        "is stable.",
    ],

    "s7_waves": [
        ["Wave 1", "M04 Branch and Front-Desk, M01 core",
         "The first real transactions. A branch can take a job in and create a "
         "record every other module can read."],
        ["Wave 2", "M01 complete, M31 Workshop, M02 Field Service",
         "Full service execution. Work can be done at a bench or at a "
         "customer's site and reported back."],
        ["Wave 3", "M03 Logistics",
         "Pick and drop becomes a channel rather than a favour, and the "
         "custody chain exists for the circular business lines."],
        ["Wave 5", "M05 Managed Services",
         "The managed-services business line becomes deliverable rather than "
         "sold on promise."],
        ["Wave 6", "M06 Data Services",
         "The data business line, and the certificates that make "
         "refurbishment and recycling lawful."],
    ],

    # ============================================================ 8
    "s8_lede":
        "Eleven measures across seven modules, and six of them have no "
        "baseline at all because nobody has ever been able to measure them.",

    "s8_intro": [
        "The striking thing about the category's measures is how many start "
        "from 'unmeasured'. Turnaround time is not measured. Rework is not "
        "measured. Workshop throughput is not measured. Chain-of-custody "
        "exceptions are not tracked. Walk-in queue wait is not measured.",

        "That is not a criticism of anybody. You cannot measure what is "
        "written on paper in fifty-one places. But it does mean the first "
        "quarter of honest figures will look worse than most people expect, "
        "and it is worth saying so before it happens rather than afterwards.",
    ],

    "s8_kpis": [
        ["Service order automation rate", "About 20 per cent", "85 per cent",
         "M01"],
        ["Average turnaround, IT equipment", "Unmeasured", "Under 24 hours",
         "M01 and M31"],
        ["Average turnaround, appliance on site", "Unmeasured",
         "Under 4 hours", "M02"],
        ["First-time fix rate", "About 70 per cent", "88 per cent",
         "M02 and M31"],
        ["Rework rate", "Unmeasured", "Under 3 per cent", "M01"],
        ["Jobs per technician per day", "4 to 5", "8 to 9", "M02"],
        ["Walk-in intake time", "About 10 minutes", "Under 3 minutes", "M04"],
        ["Workshop throughput per bench per day", "Unmeasured",
         "Forty per cent above baseline", "M31"],
        ["Chain-of-custody exceptions", "Untracked", "Zero", "M03"],
        ["Remote resolution rate, no site visit", "None", "65 per cent",
         "M05"],
        ["Data-services custody exceptions", "Not applicable", "Zero", "M06"],
    ],

    # ============================================================ 9
    "s9_lede":
        "Five risks, and three of them are about people choosing not to use "
        "the system rather than the system failing.",

    "s9_intro": [
        "The category's risk register is unusual in that its two most serious "
        "entries are adoption risks. A technician who rejects the mobile "
        "application and a workshop that keeps a parallel paper board are both "
        "rational responses to software that is worse than what it replaced, "
        "and neither can be fixed by management instruction.",

        "The third adoption risk is the counter. If intake takes longer than "
        "the paper form, branch staff will keep the paper — and because the "
        "counter is where most data enters the system, every module "
        "downstream inherits the consequence.",
    ],

    "s9_risks": [
        ["Technicians reject the mobile application",
         "Critical. The field model collapses, and inventory accuracy, "
         "invoicing speed, warranty recovery and quality data all degrade with "
         "it. This is the single largest risk in the category.",
         "Bengali first, extreme simplicity, a field pilot before rollout, "
         "visible earnings in the app, and adoption treated as a business "
         "metric rather than a technical one."],
        ["Workshop staff keep a parallel paper board",
         "High. Nothing is visible in real time, and the measurement the "
         "throughput target depends on never becomes honest.",
         "The bench board goes on a wall-mounted screen, and the quality gate "
         "cannot be bypassed — so paper stops being sufficient to release a "
         "device."],
        ["Counter intake is slower than paper",
         "High. Branch staff keep the paper form, and the counter is where "
         "most data enters the system.",
         "Three-minute intake is a hard design constraint, measured by branch "
         "and by agent, with the distribution watched rather than the "
         "average."],
        ["Custody breaks during pick and drop",
         "High. Legal exposure on lost devices the company cannot account for, "
         "and pick and drop cannot scale as a channel.",
         "A scan and both parties' identity at every handover, with no "
         "exceptions, into a ledger that can be added to and never edited."],
        ["A data-services confidentiality breach",
         "Critical, and regulatory as well as reputational. A single incident "
         "costs more than the module.",
         "Least privilege with per-case access, dual control on media, "
         "encryption with case-specific keys, and a full audit trail retained "
         "for five years."],
    ],

    "s9_note":
        "Notice what the mitigations have in common. Almost none of them is a "
        "control imposed on staff; they are design commitments that make the "
        "new way easier than the old one. That is the only mitigation that "
        "works against an adoption risk, and it is why speed at the counter "
        "and simplicity in the field are treated as business requirements "
        "rather than as preferences.",

    # ============================================================ 10
    "s10_lede":
        "Seven module guide books, and a suggested order depending on what you "
        "actually do.",

    "s10_intro": [
        "Every module in this category has its own guide book, written the "
        "same way: what it is for, who uses it, everything it lets you do, the "
        "rules it enforces, and what to do when something goes wrong. Each one "
        "is between sixty and seventy pages and each has a one-page summary at "
        "the end worth keeping.",

        "You will not need all seven. The table below suggests an order by "
        "role. Read your own module first, then the one immediately upstream "
        "or downstream of you, and stop there until you need more.",
    ],

    "s10_paths": [
        ["A counter agent or branch manager", "M04, then M01",
         "M04 is your day; M01 is the record you create. Add M31 if your "
         "branch sends work to a workshop."],
        ["A field technician", "M02, then M01",
         "M02 is your application; M01 is the promise you are working "
         "against."],
        ["A dispatcher", "M02, then M01, then M55 Workforce",
         "M02 is your board; M01 sets the priorities; workforce decides who is "
         "available."],
        ["A bench technician or workshop supervisor", "M31, then M01",
         "M31 is the bench; M01 is what the customer sees. Add M15 Inventory "
         "if you handle parts."],
        ["A rider or logistics coordinator", "M03, then M01",
         "M03 is the whole job; M01 explains why the movements exist."],
        ["A remote support engineer", "M05, then M01, then M02",
         "M05 is your queue; M01 is the customer record; M02 is where you "
         "escalate when hands are needed."],
        ["A data services technician", "M06 only",
         "It is a self-contained module and the access model means you will "
         "not see anything else."],
        ["A manager whose work crosses modules", "This book, then section 6",
         "Read the journeys before the modules. Then read whichever module "
         "owns the step you are arguing about."],
        ["Anybody new to the company", "This book, then your own module",
         "Twenty minutes here saves reading two hundred pages in the wrong "
         "order."],
    ],

    "s10_close":
        "Seven modules, three hundred and fifty-five functions, one shared "
        "vocabulary and nine ways of serving a customer. If you remember only "
        "one thing from this book, make it the seven records: service order, "
        "work order, repair order, consignment, queue token, managed-service "
        "ticket, data case. Knowing which one you are looking at tells you "
        "which module owns your problem.",
}
