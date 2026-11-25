# -*- coding: utf-8 -*-
"""
M31 — Workshop & Depot Repair Management.

What happens inside the workshop: which bench a device sits on, which
technician has it, which components were replaced, which tests it passed, and
how long each of those took. The module the first version of the plan did not
have, and whose absence would have been expensive.

Worked examples name devices, benches and figures so the reader can picture the
floor. Those details are illustrative; the repair levels, gates and rules come
from the specification.
"""

from bizcontent import common as CM

CONTENT = {
    # ============================================================== front
    "cover_line": "What happens inside the workshop: which bench, which technician, "
    "which components, which tests, and how long each of them took. The "
    "part of a repair the customer never sees and the company cannot run "
    "without.",
    "cover_inside": [
        ("Part one", "What the module is for, who uses it, and where it stops"),
        (
            "Part two",
            "All fifty-three things it lets you do, with worked "
            "examples and five walkthroughs from a normal day",
        ),
        (
            "Part three",
            "The rules, the automatic work, the permissions, the "
            "measures and the troubleshooting",
        ),
        ("Appendix A", "The full technical register for builders and testers"),
    ],
    "about": CM.about("the Workshop and Depot Repair Management module, M31"),
    "audience": CM.AUDIENCE,
    "how_arranged": CM.HOW_ARRANGED,
    "parts_table": CM.parts_table("M31"),
    "reading_note": CM.READING_NOTE,
    "appendix_note": CM.APPENDIX_NOTE,
    "part1_blurb": CM.PART1_BLURB,
    "part2_blurb": CM.PART2_BLURB,
    "part3_blurb": CM.PART3_BLURB,
    "appendix_blurb": CM.APPENDIX_BLURB,
    "part1_sections": CM.part1_sections(
        "M31", "The kinds of bench work it has to carry"
    ),
    "part2_sections": CM.part2_sections("The journey of a repair order"),
    "part3_sections": CM.PART3_SECTIONS,
    "appendix_sections": CM.APPENDIX_SECTIONS,
    "change_control": CM.CHANGE_CONTROL,
    "change_table": CM.change_table("The Workshop Supervisor"),
    "change_note": CM.CHANGE_NOTE,
    # ============================================================ exhibits
    "headline": [
        ("+40%", "devices per bench per day", "the largest capacity gain"),
        ("53", "things the module lets you do", None),
        ("3", "repair levels, skill-gated", "basic, component, board"),
        ("<30 hrs", "workshop cycle time target", "not measured today"),
        ("99%", "component genealogy completeness", "from nothing"),
        ("78%", "bench utilisation target", None),
        ("0", "calibration exceptions", "by Wave 8"),
        ("BDT 65 lac", "refurbishment margin it enables", "same benches"),
    ],
    "volume": [
        ("3", "repair levels", "L1 basic, L2 component, L3 board"),
        ("7", "device families", "laptop to appliance"),
        ("15", "workshop states", "from booked in to released"),
        ("1", "active repair per bench", "enforced, not conventional"),
        ("0%", "measured today", "the floor runs on a whiteboard"),
    ],
    "volume_title": "Why the bench needed its own module",
    "volume_sub": "A workshop has a completely different rhythm from a field " "visit",
    "volume_caption": "The shape of the work that happens at a bench",
    "does": [
        "Creating a repair order from a service order, refurbishment, RMA or "
        "internal request",
        "Workshops and benches: capability, capacity, ESD zone and equipment",
        "Allocating benches, managing the queue and the work-in-progress board",
        "Repair level classification and routing gated on skill",
        "Component-level diagnosis, teardown record and the repair itself",
        "Consuming parts at component level, with serials and genealogy",
        "Test protocols, burn-in scheduling and recording the results",
        "Rework loops inside the workshop, before anything is released",
        "Transfers to another workshop for a specialist stage",
        "Costing the repair: labour minutes, components, equipment time",
        "Throughput, utilisation and cycle-time analysis",
        "Releasing the device back to the service order that owns it",
        "Capturing a technique and promoting it to the knowledge library",
        "ESD, safety and environmental records at the bench",
    ],
    "does_not": [
        "Talking to the customer or driving the tracking timeline, which are " "M01",
        "The service order's promise date and SLA, which are M01",
        "The estimate and the customer's approval, which are M36 and M01",
        "Field visits and technician routing, which are M02",
        "Moving devices between sites, which is M03",
        "Stock levels, valuation and reordering, which are M15",
        "Calibration schedules and certificates, which are M45",
        "Certifying technicians, which is M22 — M31 only enforces the gate",
        "Writing quality checklists and running corrective action, which are " "M23",
        "The refurbishment grading standard and resale, which are M14",
        "Filing the warranty claim, which is M09 — M31 supplies the evidence",
    ],
    "areas_map": [
        (
            "Getting the device in",
            8,
            "Routing, booking in, the incoming buffer and how the queue is " "ordered.",
        ),
        (
            "Benches and capacity",
            9,
            "Workshops, benches, allocation, the board and moving work between "
            "shifts.",
        ),
        (
            "Doing the repair",
            13,
            "Teardown, procedure, components, consumables, time and technique.",
        ),
        (
            "Testing and burn-in",
            10,
            "Protocols, measured results, timed burn-in, and the gate before "
            "release.",
        ),
        (
            "Releasing and measuring",
            9,
            "Handing the device back, costing it, and finding the bottleneck.",
        ),
        (
            "Safety at the bench",
            4,
            "Static, hazardous materials, conditions and overnight security.",
        ),
    ],
    "area_bars": [
        ("Doing the repair", 13),
        ("Testing and burn-in", 10),
        ("Benches and capacity", 9),
        ("Releasing and measuring", 9),
        ("Getting the device in", 8),
        ("Safety at the bench", 4),
    ],
    "channels": [
        "A service order routed to the workshop",
        "A field visit that could not be completed on site",
        "A refurbishment order from trade-in stock",
        "A device returned under an RMA",
        "An internal 1000FiX asset needing repair",
        "A corporate decommissioning batch",
        "A recall campaign batch",
        "A transfer from another workshop for a specialist stage",
    ],
    "channels_hub": "Repair order",
    "channels_title": "Eight ways work arrives at a bench",
    "channels_sub": (
        "Whatever sent it, the same booking-in, the same queue "
        "and the same gates before it can leave"
    ),
    "channels_note": "one bench, one device",
    "channels_caption": "Everything that becomes bench work",
    # ============================================ 1. what it is for
    "s1_lede": "M31 owns what happens inside the workshop — which bench, which "
    "technician, which components, which tests, and how long each of them "
    "took.",
    "s1_intro": [
        "1000FiX performs Level 1, Level 2 and Level 3 repair — basic, "
        "component-level, and board-level with micro-soldering — across "
        "laptops, desktops, servers, printers, motherboards, mobile devices "
        "and appliances. That work happens at a bench rather than in the "
        "field, and it has an entirely different rhythm from a site visit.",
        "A field technician does one job at a time in one place. A bench "
        "technician has three devices in flight: one on the bench, two in "
        "burn-in. Parts are consumed at component level rather than as whole "
        "units. The environment is static-controlled. Test equipment has to be "
        "calibrated and the calibration has to be traceable. Burn-in periods "
        "are measured in hours and cannot be shortened. And the queue has to "
        "be balanced across specialised skills that only a few people hold.",
        "Every tier-one service system separates the customer-facing order "
        "from the internal repair execution — SAP calls it In-House Repair, "
        "IFS calls it the Repair Shop, Oracle and QAD call it Depot Repair. "
        "They separate them because the two objects answer different "
        "questions, change at different rates, and have completely different "
        "audiences. This module is 1000FiX's version of that separation.",
    ],
    "s1_problem": [
        "Without M31, workshop work in progress stays on a whiteboard. That "
        "means it is invisible to the branch and to the customer, so a branch "
        "manager answering 'where is my customer's laptop?' has to telephone "
        "the workshop and hope somebody knows.",
        "It also means bench capacity cannot be measured, so throughput cannot "
        "be improved. Nobody knows how many devices a bench releases in a day, "
        "how long a device spends waiting versus being worked on, or which "
        "state is the bottleneck. Improvement without measurement is guesswork "
        "and it usually makes things worse somewhere else.",
        "Three more consequences follow. Component-level parts consumption is "
        "not traceable to the board it went into, so a part leaves stock and "
        "vanishes. Burn-in and test results are recorded on paper, so a "
        "rejected warranty claim cannot be defended. And a device that visits "
        "two workshops has no coherent record of where it has been. The "
        "current process returns paper forms to the service centre, where they "
        "are typed in one to three days late.",
    ],
    "s1_replaces": [
        [
            "A whiteboard on the workshop wall",
            "A live work-in-progress board showing every device by state, bench, "
            "technician, age and risk",
            "The branch can see the workshop, and the customer's tracking view "
            "stays honest.",
        ],
        [
            "Paper job cards typed up one to three days later",
            "The device scanned to open the repair, everything recorded at the "
            "bench",
            "The record exists while the work is happening rather than " "afterwards.",
        ],
        [
            "A supervisor guessing at capacity",
            "Available bench-hours by workshop, repair level and skill, seven "
            "days ahead",
            "Bottlenecks are seen before they form.",
        ],
        [
            "Parts leaving stock and disappearing",
            "Component-level consumption with serial capture and genealogy",
            "Which part, from which purchase order, went into which board.",
        ],
        [
            "Test results on paper, if at all",
            "Measured values against a protocol, with the instrument identity "
            "recorded",
            "A rejected warranty claim can be defended with evidence.",
        ],
        [
            "Burn-in shortened when the floor is busy",
            "A timed state that cannot be shortened below the protocol",
            "The device that would have failed in the customer's hands fails on "
            "the bench instead.",
        ],
        [
            "Internal rework quietly absorbed",
            "Quality-check failures counted and attributed, separately from "
            "customer returns",
            "The workshop can improve because it can see itself.",
        ],
        [
            "A device visiting two workshops with no record",
            "A transfer with confirmation from the receiving workshop and a "
            "logistics consignment",
            "The device is never in an undefined place.",
        ],
    ],
    "s1_one_sentence": "M31 turns the workshop from a room with a whiteboard into a measured "
    "production floor, where every device, every component and every test "
    "is on the record while the work is happening.",
    # ============================================ 2. who uses it
    "s2_lede": "Bench technicians and workshop supervisors, plus everybody downstream "
    "who has been waiting for evidence the workshop could not previously "
    "produce.",
    "s2_intro": [
        "The primary users are few and highly skilled. A workshop supervisor "
        "runs a floor. Technicians at three levels work benches, and the "
        "level they hold determines what they may be assigned. Everybody else "
        "on the list reads what those two populations produce.",
        "The reading population matters more than it might appear. A warranty "
        "claims officer cannot defend a rejected claim without test evidence. "
        "An inventory manager cannot close the loop on a part without knowing "
        "which board it went into. A branch manager cannot answer a customer "
        "without seeing workshop state. All three of those are currently "
        "unanswerable questions, and all three are answered by somebody at a "
        "bench recording what they did.",
    ],
    "s2_roles": [
        [
            "Workshop supervisor",
            "Running the floor: allocation, sequencing, transfers and shift "
            "handover",
            "The work-in-progress board for their own workshop",
        ],
        [
            "Specialist technician, Level 3",
            "Board-level and micro-soldering work",
            "Their own assigned repair orders, at any repair level",
        ],
        [
            "Senior technician, Level 2",
            "Component-level repair",
            "Their own assigned repair orders, Level 1 and 2 only",
        ],
        [
            "Junior technician, Level 1",
            "Basic repair",
            "Their own assigned repair orders, Level 1 only",
        ],
        [
            "Quality manager",
            "Quality checks, internal rework and failure patterns",
            "All quality records and rework across every workshop",
        ],
        [
            "Operations Director",
            "Throughput, cycle time and where the bottleneck is",
            "The workshop dashboard across the estate",
        ],
        [
            "Branch manager",
            "Where their customers' devices are",
            "Repair orders that originated at their branch",
        ],
        [
            "Service centre agent",
            "Answering a customer at the counter",
            "Repair orders from their own branch, read-only",
        ],
        [
            "Inventory manager",
            "What components were consumed and into what",
            "Component consumption, read-only",
        ],
        [
            "Warranty claims officer",
            "Evidence for a claim",
            "Test results, measurements and photographs",
        ],
        [
            "Logistics coordinator",
            "Devices ready to leave, and transfers between workshops",
            "Outgoing staging and transfers",
        ],
    ],
    "s2_days": [
        {
            "title": "If you work at a bench",
            "text": [
                "You scan the device and the repair opens. What appears is the "
                "history — what this device has been in for before — the "
                "diagnostic template extended with component-level checks for "
                "your repair level, the applicable repair procedure as a step "
                "list, and the parts you are likely to need.",
                "Most of the difference from a paper job card is in when "
                "things get recorded. Teardown is recorded as you do it, with "
                "photographs at defined points. Parts are consumed at the "
                "moment you fit them, with the serial captured, so the record "
                "knows which component went into which board. Time is captured "
                "as start, pause, resume and stop, which distinguishes work "
                "from waiting — and that distinction is what makes the "
                "workshop's productivity figures fair.",
                "You will also find you can hold more than one device at once, "
                "within limits: one on the bench and two in burn-in is the "
                "normal shape. That is deliberate, because burn-in is measured "
                "in hours and a technician standing over a device for four "
                "hours is not a good use of anybody.",
            ],
        },
        {
            "title": "If you supervise a workshop",
            "text": [
                "The board replaces the whiteboard, and it is designed to go "
                "on a wall. Every device appears by state, bench, technician, "
                "age and how close it is to its promise. When a bench becomes "
                "free the system proposes the next repair order from the queue "
                "by risk and skill match, and you accept or choose "
                "differently.",
                "The number that will change how you run the floor is cycle "
                "time by state. It breaks the workshop's time into waiting, "
                "diagnosis, repair, waiting for parts, burn-in, quality check "
                "and staging — and it names the bottleneck rather than leaving "
                "you to infer it. Most workshops discover their bottleneck is "
                "not where they assumed.",
                "Two things you will be held to. Benches hold exactly one "
                "active repair each, which sounds obvious and is enforced "
                "because it is the only way occupancy can be measured. And "
                "burn-in cannot be shortened below its protocol duration — "
                "extended yes, reduced never, whatever the queue looks like.",
            ],
        },
        {
            "title": "If you work at a branch",
            "text": [
                "You gain an answer. 'Where is my customer's laptop?' becomes "
                "a screen rather than a telephone call to the workshop, and it "
                "shows the state rather than a guess — booked in, on bench, in "
                "burn-in, waiting for a part, in quality check, staged for "
                "collection.",
                "What you should not do is relay bench detail to the customer. "
                "The customer's view lives in M01 and is deliberately simpler: "
                "'in progress' rather than 'awaiting a Level 3 board "
                "technician, position four in the queue'. The second sentence "
                "is true and useless to them.",
            ],
        },
        {
            "title": "If you work in quality, warranty or inventory",
            "text": [
                "Each of you gets something that does not exist today. Quality "
                "gets internal rework counted and attributed by technician, "
                "repair level, device model and failure reason — before the "
                "customer sees it rather than after they complain.",
                "Warranty gets test results with measured values, the identity "
                "of the instrument that made each measurement, and "
                "photographs, all attached automatically to the claim. When a "
                "brand rejects a claim, that evidence is what answers them.",
                "Inventory gets component genealogy: which part, from which "
                "purchase order, into which board. The gap where parts leave "
                "stock and become untraceable is the single largest source of "
                "inventory inaccuracy in a repair business, and this closes "
                "it.",
            ],
        },
    ],
    "s2_note": "Technicians see labour minutes but not monetary cost rates. Repair "
    "cost and margin are restricted to the Operations Director, branch and "
    "workshop managers and finance — a technician's judgement about a "
    "repair should not be shaped by what it costs.",
    # ============================================ 3. boundary
    "s3_lede": "M31 has no customer-facing surface at all. That is the most important "
    "sentence in this section.",
    "s3_intro": [
        "The boundary between M31 and M01 is the reason this module exists "
        "separately, and it is drawn on audience rather than on function. M01 "
        "answers the customer's question: what is happening with my device? "
        "M31 answers the workshop's: which bench, which technician, which "
        "component, which test?",
        "Both are true simultaneously and neither audience wants the other's "
        "answer. A customer's tracking view shows 'in progress' while the "
        "workshop board shows 'awaiting a Level 3 board technician, position "
        "four in the queue, estimated bench time Thursday'. The workshop "
        "cannot function without the second; the customer would be confused "
        "and alarmed by it.",
        "So M31 has no customer-facing surface. It reports state to M01 and "
        "M01 decides what the customer sees. A branch agent can look at the "
        "workshop board, but what they say to the customer should come from "
        "the service order.",
    ],
    "s3_shared_intro": "Almost everything on a bench belongs to somebody else. This table "
    "says who.",
    "s3_shared": [
        [
            "The repair order",
            "M31 — this module owns it",
            "Creates it, benches it, works it, tests it and releases it",
        ],
        [
            "The bench and the workshop",
            "M31",
            "Owns the capability, capacity, ESD zone and equipment inventory",
        ],
        [
            "The service order",
            "M01",
            "The parent. M31 reports status to it and never touches its state",
        ],
        [
            "The device",
            "M17 Asset Registry",
            "Reads identity, and writes component genealogy back to it",
        ],
        [
            "The part",
            "M15 Inventory",
            "Requests, reserves and consumes. Does not hold or value stock",
        ],
        [
            "Test equipment",
            "M45 Equipment",
            "Uses it and records which instrument. Calibration lives in M45",
        ],
        [
            "The quality checklist",
            "M23 Quality",
            "Executes it at the defined gates and raises non-conformances",
        ],
        [
            "Technician competency",
            "M22",
            "Enforced at bench assignment. The certification record is elsewhere",
        ],
        [
            "The repair procedure",
            "M61 Knowledge",
            "Consumes procedures, and contributes new ones back",
        ],
        [
            "The grading standard",
            "M14 Refurbishment",
            "Does the bench work. M14 owns the standard and the commercial " "outcome",
        ],
    ],
    # ============================================ 4. kinds of bench work
    "s4k_title": "The kinds of bench work it has to carry",
    "s4k_lede": "Three repair levels and seven device families, with skill gates "
    "between them that cannot be overridden.",
    "s4k_intro": [
        "Repair level is already a commercial concept at 1000FiX — the company "
        "profile advertises level-based repair services — and M31 makes it an "
        "operational one. Level 1 is basic: modules swapped, assemblies "
        "replaced. Level 2 is component-level. Level 3 is board-level, "
        "including micro-soldering, and it is a genuine competitive "
        "differentiator in Bangladesh.",
        "The levels are gates rather than labels. A device cannot be allocated "
        "to a technician who lacks the certification for its repair level and "
        "brand. Level 3 work may only happen at a workshop with the required "
        "equipment and static-control classification. Neither can be "
        "overridden by a supervisor under pressure.",
        "The level is also provisional until somebody has opened the device. "
        "Confirming or revising it after physical inspection is an explicit "
        "step, and a revision upward that pushes cost past the approved "
        "estimate requires re-approval before work continues.",
    ],
    "kinds_columns": [
        (
            "By repair level",
            "What determines who may touch it",
            [
                "Level 1 — basic, module and assembly replacement",
                "Level 2 — component-level repair",
                "Level 3 — board-level and micro-soldering",
                "Level revised upward after inspection",
            ],
        ),
        (
            "By device family",
            "What determines the bench and equipment",
            [
                "Laptops and desktops",
                "Servers and storage",
                "Printers, plotters and photocopiers",
                "Motherboards, mobile devices, appliances",
            ],
        ),
        (
            "By where it came from",
            "What determines the parent record",
            [
                "A customer service order",
                "A field visit that could not be completed",
                "A refurbishment order from trade-in stock",
                "An RMA return, or an internal 1000FiX asset",
            ],
        ),
    ],
    "kinds_title": "Three ways bench work differs",
    "kinds_sub": "Level decides who, family decides where, origin decides who "
    "gets it back",
    "s4k_header": [
        "The kind of work",
        "What is different about it",
        "What stays the same",
    ],
    "s4k_table": [
        [
            "Level 1 — basic repair",
            "Module and assembly replacement. Any certified technician may take "
            "it, and it usually needs no specialist equipment.",
            "Booked in, benched, tested, quality-checked, released",
        ],
        [
            "Level 2 — component repair",
            "Component-level work. Requires Level 2 certification, and the "
            "quality check must be performed by somebody other than the "
            "repairer.",
            "As above",
        ],
        [
            "Level 3 — board repair",
            "Micro-soldering and board-level work. Requires Level 3 "
            "certification, a workshop with the equipment, and an appropriate "
            "static-control classification. Independent quality check "
            "mandatory.",
            "As above",
        ],
        [
            "Refurbishment",
            "The device is stock rather than a customer's property, and the "
            "grading standard belongs to M14. Same benches, same measurement.",
            "As above",
        ],
        [
            "Returned from field",
            "A visit that could not be completed on site. Arrives with the "
            "field diagnosis already attached.",
            "As above",
        ],
        [
            "RMA return",
            "Carries the RMA reference, the expected fault and the originating "
            "channel.",
            "As above",
        ],
        [
            "Internal asset repair",
            "1000FiX's own equipment. No customer, but the same discipline.",
            "As above",
        ],
        [
            "Batch intake",
            "A corporate decommission, a recall campaign or a refurbishment lot, "
            "booked in as one operation.",
            "As above, per device",
        ],
        [
            "Workshop transfer",
            "A specialist stage at another workshop. Needs the receiving "
            "workshop's confirmation and a logistics consignment.",
            "As above",
        ],
        [
            "Beyond economic repair",
            "Requires photographic evidence, a documented cost comparison and a "
            "second technician's confirmation.",
            "Ends the repair path rather than completing it",
        ],
    ],
    "s4k_caption": "The kinds of bench work and what distinguishes each",
    "s4k_note": "A repair level revision that increases cost beyond the approved "
    "estimate requires re-approval before work continues. Discovering the "
    "job is bigger than expected is normal; continuing anyway is not.",
    # ============================================ 5. vocabulary
    "s4_lede": "Fifteen words, most of them from a production floor rather than a "
    "service counter.",
    "s4_intro": [
        "Workshop vocabulary borrows from manufacturing, and several of these "
        "terms are unfamiliar to somebody who has worked at a counter. Two of "
        "them — genealogy and burn-in — are worth learning precisely, because "
        "they are where most of the module's value sits.",
    ],
    "s4_glossary": [
        [
            "Repair order",
            "The instruction to repair one device at a bench. Not the customer's "
            "request, which is the service order in M01.",
            "The central record of this module",
        ],
        [
            "Repair level",
            "How deep the work goes: Level 1 basic, Level 2 component, Level 3 "
            "board and micro-soldering. It gates who may do the work.",
            "Provisional at intake, confirmed after inspection",
        ],
        [
            "Bench",
            "A physical working position with its own capability and equipment. "
            "It holds exactly one active repair at a time.",
            "The unit of workshop capacity",
        ],
        [
            "Incoming buffer",
            "Where a booked-in device waits, physically and logically, until a "
            "bench is allocated.",
            "The first place a device sits, with its location tracked",
        ],
        [
            "Teardown record",
            "The disassembly sequence, components removed and their condition, "
            "with photographs at defined points.",
            "What lets somebody else reassemble it, or explain what was found",
        ],
        [
            "Component genealogy",
            "The record of which part, from which purchase order, went into which "
            "board.",
            "The gap this closes is the largest source of inventory inaccuracy",
        ],
        [
            "Harvested component",
            "A part taken from a donor board, added to inventory with its "
            "provenance. It cannot be used on a warranty repair.",
            "Common in board-level work, and tracked separately",
        ],
        [
            "Test protocol",
            "The defined set of tests for a device category, repair level and "
            "fault type, with pass criteria and durations.",
            "Results are measured values, not only pass or fail",
        ],
        [
            "Burn-in",
            "Running the device under load for a defined period to surface faults "
            "that only appear after time. It cannot be shortened.",
            "A timed state with its own station capacity",
        ],
        [
            "Burn-in station",
            "A constrained resource with its own queue. Devices wait for one.",
            "Often the real bottleneck in a workshop",
        ],
        [
            "Independent quality check",
            "A check performed by somebody other than the repairing technician. "
            "Mandatory for Level 2 and Level 3.",
            "A separation of duties, enforced by the system",
        ],
        [
            "Internal rework",
            "A device that failed its quality check and went back to a bench. "
            "Counted separately from a customer-returned repair.",
            "Never hidden — that is a rule",
        ],
        [
            "Outgoing staging",
            "Where a released device waits to be collected by the branch or "
            "logistics.",
            "Devices sitting here beyond a threshold raise an alert",
        ],
        [
            "Cycle time by state",
            "How long a device spends waiting, in diagnosis, under repair, "
            "waiting for parts, in burn-in, in quality check and in staging.",
            "The report that names the bottleneck",
        ],
        [
            "Beyond economic repair",
            "A formal declaration that repair costs more than the device is "
            "worth. Requires evidence, a cost comparison and a second "
            "technician.",
            "Ends the repair path and routes the device elsewhere",
        ],
    ],
    # ============================================ 6. what you can do
    "s5_lede": "Fifty-three things, in six areas, following a device from the "
    "workshop door to the outgoing shelf.",
    "s5_intro": [
        "The areas below follow the physical path of a device: getting it in, "
        "getting it onto a bench, doing the work, testing it, releasing it, "
        "and the safety discipline that runs alongside all of it.",
        "The third and fourth areas — doing the repair and testing it — hold "
        "twenty-three of the fifty-three functions between them, which is "
        "roughly where the value sits. Component genealogy and enforced "
        "burn-in are the two individual functions that change the most.",
    ],
    "areas": [
        {
            "title": "Getting the device in",
            "who": [
                ("Mostly used by", "Workshop clerks and supervisors"),
                (
                    "Also relied on by",
                    "The originating branch, which hears " "about discrepancies",
                ),
                ("Where it happens", "The workshop door and the incoming " "buffer"),
            ],
            "intro": [
                "Eight functions covering everything before a device reaches a "
                "bench. A repair order is created — from a service order, a "
                "refurbishment order, an internal asset request or a device "
                "returned from the field — and routed to a workshop by repair "
                "level, device category, brand certification, equipment "
                "requirement and current load.",
                "The function that matters most is booking in. Physical "
                "receipt is recorded with condition verified against the "
                "intake record, discrepancies flagged and photographic "
                "evidence captured. This is where a missing charger or a new "
                "scratch is found — while the previous custodian is still "
                "identifiable rather than three weeks later when nobody can "
                "say.",
            ],
            "features": [
                [
                    "Repair order creation",
                    "Creates a repair order from a service order, a refurbishment "
                    "order, an internal asset repair or a device returned from "
                    "the field.",
                    "Every route into the workshop produces the same kind of "
                    "record.",
                ],
                [
                    "Several repairs per service order",
                    "Supports zero, one or many repair orders against one service "
                    "order, each tracked independently.",
                    "A device needing two independent repairs is two pieces of "
                    "bench work and one customer promise.",
                ],
                [
                    "Workshop routing",
                    "Routes to the right workshop by repair level, device "
                    "category, brand certification, equipment and current load.",
                    "Board-level work never lands where there is no board-level "
                    "capability.",
                ],
                [
                    "Booking in",
                    "Records physical receipt with condition verified against the "
                    "intake record, discrepancies flagged and photographs taken.",
                    "A missing accessory is found while somebody can still "
                    "explain it.",
                ],
                [
                    "Incoming buffer",
                    "Holds booked-in devices in a tracked physical and logical "
                    "location until a bench is free.",
                    "Nothing sits in an undefined place.",
                ],
                [
                    "Priority and sequencing",
                    "Sequences the queue by risk, customer tier, repair level and "
                    "promised date, with supervisor override.",
                    "The workshop works on what matters rather than what arrived "
                    "first.",
                ],
                [
                    "RMA returns",
                    "Receives devices returned under an RMA with the reference, "
                    "expected fault and originating channel.",
                    "A return arrives with its history rather than as a mystery.",
                ],
                [
                    "Batch intake",
                    "Books in a whole batch — a corporate decommission, a recall, "
                    "a refurbishment lot — in one operation.",
                    "Thirty devices are one action and thirty records.",
                ],
            ],
            "example": (
                "the charger that was missing on arrival",
                "A laptop arrives at the Dhaka central workshop from the "
                "Mirpur branch under a logistics consignment. The clerk books "
                "it in and the screen shows the intake record: the customer "
                "handed over the laptop, a charger and a sleeve, with three "
                "condition photographs. The charger is not in the package. The "
                "clerk records a discrepancy rather than a note, which flags "
                "it immediately to the originating branch. Mirpur checks and "
                "finds the charger on the counter shelf, separated during "
                "packing. It travels on the next shuttle. What did not happen: "
                "the discrepancy discovered at collection three weeks later, "
                "with the branch, the workshop and the courier each certain it "
                "was not them, and the company replacing a charger to settle "
                "an argument it could not win.",
            ),
            "mistakes": [
                "Booking in without checking against the intake record. The "
                "verification is the whole point of the step, and after it the "
                "workshop owns whatever is missing.",
                "Recording a discrepancy as a note. A note does not reach the "
                "originating branch; a flagged discrepancy does, while "
                "somebody can still find the item.",
                "Leaving a device in the buffer without a location. The buffer "
                "is tracked precisely because it is where devices are easiest "
                "to lose.",
                "Overriding the queue sequence for a device that shouted "
                "loudest. The sequence already weighs risk and promised date; "
                "override for a reason, not for a phone call.",
            ],
        },
        {
            "title": "Benches and capacity",
            "who": [
                ("Mostly used by", "Workshop supervisors"),
                (
                    "Also relied on by",
                    "Technicians, branches and the " "operations director",
                ),
                ("Where it happens", "The board, usually on a wall"),
            ],
            "intro": [
                "Nine functions turning a room full of benches into measurable "
                "capacity. Workshops are defined with their capability "
                "profile, operating hours, static-control classification and "
                "equipment. Benches are defined within them with their own "
                "capability and attached equipment, and each holds exactly one "
                "active repair.",
                "That single-occupancy rule sounds pedantic and is what makes "
                "occupancy measurable. If a bench could hold three repairs at "
                "once, bench utilisation would mean nothing, and utilisation "
                "is one of the numbers the forty per cent throughput gain is "
                "built on.",
                "The parallel-work function is the counterpart. A technician "
                "may hold several devices across states — typically one on the "
                "bench and two in burn-in — within explicit limits. The bench "
                "is single-occupancy; the technician is not.",
            ],
            "features": [
                [
                    "Workshop master",
                    "Defines each workshop with location, capability, operating "
                    "hours, static-control classification and equipment.",
                    "Routing knows what each workshop can actually do.",
                ],
                [
                    "Bench master",
                    "Defines benches with their capability and attached "
                    "equipment, enforcing one active repair each.",
                    "Occupancy becomes a number rather than an impression.",
                ],
                [
                    "Bench allocation",
                    "Allocates a repair to a bench and a technician, enforcing "
                    "skill, certification and equipment availability.",
                    "A Level 3 board never reaches a Level 1 technician.",
                ],
                [
                    "Work-in-progress board",
                    "Shows every device by state, bench, technician, age and "
                    "risk, designed for a wall display.",
                    "The whiteboard becomes something the branch can see too.",
                ],
                [
                    "Capacity view",
                    "Shows available bench-hours by workshop, repair level and "
                    "skill for the next seven days.",
                    "Next Thursday's shortage of board capacity is visible on "
                    "Monday.",
                ],
                [
                    "Parallel work",
                    "Lets one technician hold several devices across states, "
                    "within explicit limits.",
                    "Nobody stands watching a four-hour burn-in.",
                ],
                [
                    "Bench handover",
                    "Hands a device between technicians or shifts with a "
                    "structured note and a transfer of accountability.",
                    "A half-finished board repair survives a shift change.",
                ],
                [
                    "Workshop transfer",
                    "Transfers a repair to another workshop for a specialist "
                    "stage, creating the logistics consignment automatically.",
                    "The device is never in an undefined place between two "
                    "workshops.",
                ],
                [
                    "Shift board",
                    "Shows each shift's incoming, in progress, at risk and "
                    "released counts at open and close.",
                    "A shift starts knowing what it inherited.",
                ],
            ],
            "example": (
                "a bottleneck that was not where anybody thought",
                "The Dhaka central workshop is releasing fewer devices per day "
                "than its bench count suggests it should, and the assumption "
                "on the floor is that Level 3 capacity is short. Cycle time by "
                "state says otherwise. Diagnosis averages 40 minutes, repair "
                "2 hours 10, quality check 25 minutes — all reasonable. Burn-in "
                "averages 6 hours 40 against a protocol duration of 4 hours. "
                "The extra two hours forty is devices waiting for a burn-in "
                "station, because there are five stations and eleven benches. "
                "Three more stations cost a fraction of a technician's salary "
                "and release roughly a fifth of the workshop's throughput. "
                "Nobody had suspected it, because a device sitting in a "
                "burn-in queue looks exactly like a device in burn-in.",
            ),
            "mistakes": [
                "Putting two devices on one bench because they are both small. "
                "It is a hard rule, and the reason is that occupancy stops "
                "meaning anything.",
                "Allocating on availability rather than certification. The "
                "system will refuse, and working round it voids the warranty "
                "claim.",
                "Handing over a device at shift end without a structured note. "
                "The next technician then re-diagnoses, which is the most "
                "expensive kind of rework.",
                "Reading the capacity view as a report. It shows seven days "
                "ahead so that something can be done this week.",
            ],
        },
        {
            "title": "Doing the repair",
            "who": [
                ("Mostly used by", "Bench technicians at all three levels"),
                (
                    "Also relied on by",
                    "Inventory, warranty and the knowledge " "library",
                ),
                ("Where it happens", "The bench, all day"),
            ],
            "intro": [
                "Thirteen functions, the largest area in the module, covering "
                "everything between a device reaching a bench and the first "
                "test. Diagnosis extends the template from M01 with "
                "component-level checks appropriate to the repair level. "
                "Teardown is recorded as it happens, with photographs at "
                "defined points. The repair procedure appears as a step list "
                "from the knowledge library, and completion, measurements and "
                "deviations are recorded against it.",
                "Two functions here change more than the rest. Component-level "
                "part consumption captures a serial or batch and records "
                "exactly which component went into which board — which is what "
                "closes the gap where parts leave stock and become "
                "untraceable. And component harvesting records parts taken "
                "from a donor board with their provenance, which is common in "
                "board-level work and currently invisible.",
                "The last function is about the future. When a repair resolves "
                "a fault that is not in the library, the note can be proposed "
                "for promotion to the technical library. That is how a "
                "specialist's technique stops living only in their head — "
                "which matters in a company whose Level 3 capability is "
                "concentrated in a few people.",
            ],
            "features": [
                [
                    "Bench diagnosis",
                    "Runs the diagnostic template at bench level, extended with "
                    "component checks for the repair level.",
                    "A board technician gets board-level questions, not the "
                    "counter's.",
                ],
                [
                    "Teardown record",
                    "Records the disassembly sequence, components removed and "
                    "their condition, with photographs at defined points.",
                    "Somebody else can reassemble it, or explain what was " "found.",
                ],
                [
                    "Repair level confirmation",
                    "Confirms or revises the level after physical inspection, "
                    "triggering re-routing and re-estimation if it changes.",
                    "The estimate reflects the device rather than the guess made "
                    "at the counter.",
                ],
                [
                    "Repair procedure execution",
                    "Presents the applicable procedure as a step list, recording "
                    "completion, measurements and deviations.",
                    "A junior technician follows a senior technician's method.",
                ],
                [
                    "Component-level part consumption",
                    "Consumes parts at component level with serial or batch "
                    "capture, recording which component went into which board.",
                    "The largest source of inventory inaccuracy in a repair "
                    "business closes.",
                ],
                [
                    "Component harvesting",
                    "Records components taken from a donor board, adding them to "
                    "inventory with provenance.",
                    "Harvested parts stop being invisible — and cannot be used on "
                    "warranty work.",
                ],
                [
                    "Consumables tracking",
                    "Records solder, flux, thermal paste, adhesive and cleaning "
                    "agents against the repair.",
                    "The true cost of a board repair includes what it consumed.",
                ],
                [
                    "Equipment usage",
                    "Records which test and repair equipment was used, capturing "
                    "the instrument identity.",
                    "A measurement can be traced to the instrument that made it.",
                ],
                [
                    "Labour time capture",
                    "Records start, pause, resume and stop per technician, "
                    "distinguishing active work from waiting.",
                    "Productivity figures measure work rather than presence.",
                ],
                [
                    "Repair notes",
                    "Captures findings, technique and cautions in Bengali or "
                    "English, with voice input.",
                    "What was learned is written down while it is fresh.",
                ],
                [
                    "Knowledge promotion",
                    "Proposes a repair note for the technical library when it "
                    "resolves an undocumented fault.",
                    "A specialist's technique outlives the specialist.",
                ],
                [
                    "Escalation to a specialist",
                    "Escalates to a higher-level technician or another workshop "
                    "with the full context and the reason.",
                    "A stuck repair moves rather than sitting.",
                ],
                [
                    "Beyond economic repair",
                    "Declares a device unrepairable with evidence, a cost "
                    "comparison and a second technician's confirmation.",
                    "The company stops spending BDT 8,000 of labour on a BDT "
                    "6,000 device.",
                ],
            ],
            "example": (
                "a board repair, and the part that could be traced",
                "A laptop motherboard arrives for Level 3 work: no power, "
                "suspected power management failure. The technician runs the "
                "bench diagnosis, records the teardown with photographs at "
                "four defined points, and isolates a failed power management "
                "chip. The repair procedure for that board family appears as a "
                "step list from the knowledge library, and each step is "
                "recorded as it is completed with the measured values taken. "
                "The replacement chip is consumed at component level with its "
                "batch captured, so the record now shows this chip, from this "
                "purchase order, into this board, in this laptop, on this "
                "date. Consumables — solder, flux, isopropyl — are recorded. "
                "The rework station used is captured by instrument identity, "
                "which matters because its calibration will be checked against "
                "this date if anything is ever disputed. Total active bench "
                "time 3 hours 20, distinguished from 40 minutes of waiting for "
                "the part. Eight months later the brand queries a warranty "
                "claim on that board and every one of those facts is still "
                "attached to it.",
            ),
            "mistakes": [
                "Fitting a part and consuming it in the system afterwards. "
                "Genealogy recorded from memory is genealogy nobody can rely "
                "on.",
                "Using a harvested component on a warranty repair. It is a "
                "hard rule and the brand will reject the claim.",
                "Continuing after discovering the repair level is higher than "
                "approved. Re-approval comes first if it pushes past the "
                "estimate.",
                "Leaving the clock running through a wait for parts. The pause "
                "is what separates work from waiting, and without it your own "
                "productivity figures look worse than they are.",
                "Solving an undocumented fault and not proposing the note. The "
                "next technician will spend the same three hours you just "
                "did.",
            ],
            "caution": "Brand-supplied warranty parts cannot be consumed on a "
            "non-warranty repair, and harvested components cannot be used "
            "on warranty work. Both are hard rules, both are about who "
            "pays, and both are checked at consumption.",
        },
        {
            "title": "Testing and burn-in",
            "who": [
                ("Mostly used by", "Technicians and quality inspectors"),
                ("Also relied on by", "Warranty, which needs the evidence"),
                ("Where it happens", "Test benches and burn-in stations"),
            ],
            "intro": [
                "Ten functions, and the area where a workshop earns the right "
                "to release a device. Test protocols are defined by device "
                "category, repair level and fault type, with required tests, "
                "pass criteria and durations. Results record measured values "
                "rather than only pass or fail, which is what makes them "
                "useful to a warranty claim.",
                "Burn-in is the function that changes behaviour most. Running "
                "a device under load for a defined period surfaces faults that "
                "only appear after time — the intermittent fault that returns "
                "as a rework three weeks later. It is a timed state with "
                "automatic completion prompting, and it cannot be shortened "
                "below the protocol duration. Extension is permitted; "
                "reduction never is.",
                "Then the gate. Release requires a passed quality checklist "
                "appropriate to the device type and repair level, and for "
                "Level 2 and Level 3 the check must be performed by somebody "
                "other than the repairer. A failure loops the device back to a "
                "bench with the reason recorded, and internal rework is "
                "counted separately from customer-returned rework and never "
                "hidden.",
            ],
            "features": [
                [
                    "Test protocol library",
                    "Maintains protocols by device category, repair level and "
                    "fault type, with required tests, pass criteria and "
                    "durations.",
                    "Every device of a kind gets the same test, everywhere.",
                ],
                [
                    "Functional test capture",
                    "Records results against the protocol with measured values, "
                    "not only pass or fail.",
                    "A brand disputing a claim can be answered with numbers.",
                ],
                [
                    "Burn-in scheduling",
                    "Schedules burn-in with a defined duration and load profile, "
                    "tracking a timed state with completion prompting.",
                    "The fault that only appears after four hours appears here "
                    "rather than at the customer's desk.",
                ],
                [
                    "Burn-in station management",
                    "Manages station capacity as a constrained resource with its "
                    "own queue.",
                    "Often the real bottleneck, and now a visible one.",
                ],
                [
                    "Post-burn-in verification",
                    "Requires a verification test after burn-in before release is "
                    "permitted.",
                    "Burn-in is not useful unless somebody checks the result.",
                ],
                [
                    "Quality gate",
                    "Prevents release without a passed checklist appropriate to "
                    "the device and the repair level.",
                    "Nothing leaves the workshop unchecked.",
                ],
                [
                    "Independent quality check",
                    "Requires a check by somebody other than the repairer for "
                    "Level 2 and Level 3, and above the value threshold.",
                    "A check by the person who did the work is not a check.",
                ],
                [
                    "In-workshop rework",
                    "Loops a failed device back to a bench with the reason "
                    "recorded, counting internal rework separately.",
                    "The workshop sees its own failures before the customer " "does.",
                ],
                [
                    "Test evidence",
                    "Attaches results, measurements and photographs to the repair "
                    "order and the service order's evidence pack.",
                    "The warranty claim assembles itself.",
                ],
                [
                    "Calibration enforcement",
                    "Warns when a repair uses an instrument whose calibration has "
                    "lapsed, and flags the resulting quality record.",
                    "A measurement made with an uncalibrated instrument is "
                    "identified rather than trusted.",
                ],
            ],
            "example": (
                "the fault that appeared in hour three",
                "A desktop comes in with intermittent restarts. The technician "
                "finds a failing capacitor bank on the board, replaces it, and "
                "the machine passes its initial functional test — it starts, "
                "runs, and shows no fault. Under the old process it would have "
                "gone back to the customer that afternoon. Instead the "
                "protocol for that repair type requires four hours of burn-in "
                "under load, and a station is reserved. At three hours ten the "
                "machine restarts. The burn-in record captures it. Back to the "
                "bench: a second, marginal capacitor on the same rail, which "
                "was within tolerance at room temperature and not under a "
                "three-hour thermal load. It is replaced, burn-in is run "
                "again, and the machine passes cleanly. The device is released "
                "the following morning. The customer got their machine a day "
                "later than they might have — and did not get it back a third "
                "time, as a rework, in three weeks.",
            ),
            "mistakes": [
                "Shortening burn-in because the floor is busy. It is a hard "
                "rule, and it is the single function most responsible for the "
                "rework target.",
                "Recording pass or fail without the measured values. A "
                "warranty claim is defended with numbers, and pass is not a "
                "number.",
                "Performing the independent check on your own Level 2 repair. "
                "The system will refuse and it is a separation of duties.",
                "Treating an internal rework as something to absorb quietly. "
                "It is counted, attributed and never hidden — and that is what "
                "makes the workshop able to improve.",
                "Continuing to use an instrument whose calibration has lapsed. "
                "The warning exists because every measurement it makes becomes "
                "questionable, retrospectively.",
            ],
            "caution": "Burn-in duration can be extended and never reduced. If a "
            "device is holding up the floor, the answer is more burn-in "
            "stations, not less burn-in — the third walkthrough in section "
            "8 shows what that discovery is worth.",
        },
        {
            "title": "Releasing and measuring",
            "who": [
                (
                    "Mostly used by",
                    "Supervisors, finance and the operations " "director",
                ),
                ("Also relied on by", "Branches waiting for their devices"),
                ("Where it happens", "The outgoing shelf, and the reports"),
            ],
            "intro": [
                "Nine functions covering the end of the bench process and the "
                "measurement of the whole of it. Release reports the outcome, "
                "work summary, parts consumed and test results back to the "
                "service order that owns the device, and assigns an outgoing "
                "staging location.",
                "The costing functions turn a repair into a number. Labour "
                "minutes at the applicable rate, components, consumables, "
                "equipment time and overhead absorption produce a full cost, "
                "compared against the estimate with variance flagged beyond "
                "tolerance.",
                "And the analytics are how the forty per cent throughput gain "
                "is actually found. Devices released per bench per day, cycle "
                "time broken down by state, and bench utilisation against "
                "available hours — together they name the bottleneck rather "
                "than leaving a supervisor to infer it from a busy-looking "
                "floor.",
            ],
            "features": [
                [
                    "Release to the service order",
                    "Releases the device back to M01 with outcome, work summary, "
                    "parts consumed and test results.",
                    "The branch and the customer find out without telephoning.",
                ],
                [
                    "Outgoing staging",
                    "Tracks released devices in a staging location until the "
                    "branch or logistics collects them.",
                    "A finished device does not sit unnoticed on a shelf.",
                ],
                [
                    "Repair costing",
                    "Calculates full cost: labour minutes at rate, components, "
                    "consumables, equipment time and overhead.",
                    "Whether a kind of repair makes money becomes knowable.",
                ],
                [
                    "Cost against estimate",
                    "Compares actual cost to the estimate and flags variance "
                    "beyond tolerance.",
                    "Estimating gets better because the misses are visible.",
                ],
                [
                    "Throughput analytics",
                    "Reports devices released per bench per day, per workshop and "
                    "per repair level.",
                    "The headline productivity number for the whole floor.",
                ],
                [
                    "Cycle time analytics",
                    "Reports time by state — waiting, diagnosis, repair, burn-in, "
                    "quality check, awaiting release.",
                    "Names the bottleneck instead of leaving it to be guessed.",
                ],
                [
                    "Bench utilisation",
                    "Reports occupancy against available hours.",
                    "Whether the constraint is benches or something else.",
                ],
                [
                    "Failure pattern analytics",
                    "Reports component failure patterns by device model.",
                    "Feeds brand feedback and the predictive models.",
                ],
                [
                    "Workshop dashboard",
                    "Presents workshop performance to the supervisor and the "
                    "operations director.",
                    "Two workshops become comparable.",
                ],
            ],
            "example": (
                "the repair that cost more than it earned",
                "Cost-against-estimate reporting flags a pattern: Level 2 "
                "printer repairs at one workshop are running an average of 34 "
                "per cent above estimate, well beyond the eight per cent "
                "tolerance. Investigation finds two causes. Consumables on "
                "printer work — rollers, belts, cleaning agents — were not "
                "being recorded at all before M31, so the original estimating "
                "model never included them. And one particular fault, a "
                "specific paper-feed failure on one model, is taking an "
                "average of four hours against a ninety-minute estimate "
                "because no repair procedure exists for it in the library. The "
                "estimating model is corrected for consumables. A senior "
                "technician documents the paper-feed procedure and it is "
                "promoted to the library, after which the same repair takes "
                "one hour fifty. Variance falls inside tolerance the following "
                "month, and the company stops quietly losing money on a repair "
                "type it thought was profitable.",
            ),
            "mistakes": [
                "Releasing a device without the test results attached. The "
                "warranty claim then has to be assembled by hand later, if it "
                "can be at all.",
                "Leaving released devices in staging. Devices sitting beyond "
                "the threshold raise an alert because they are finished work "
                "nobody is collecting.",
                "Reading throughput without cycle time. Throughput tells you "
                "the workshop is slow; cycle time tells you where.",
            ],
        },
        {
            "title": "Safety at the bench",
            "who": [
                (
                    "Mostly used by",
                    "Technicians at shift start, and " "supervisors at shift close",
                ),
                ("Also relied on by", "Quality, safety and the insurer"),
                ("Where it happens", "The bench, and the secure store"),
            ],
            "intro": [
                "Four functions that are short to describe and consequential "
                "to skip. Static-discharge verification is recorded at shift "
                "start for benches in controlled zones. Handling of batteries, "
                "refrigerant and chemicals is recorded against the safety "
                "procedure. Temperature and humidity are recorded where the "
                "repair type requires it. And high-value devices held "
                "overnight must be recorded into secure storage at shift "
                "close, which blocks the shift from closing until it is done.",
                "None of these produces revenue. All of them are what a brand "
                "auditor, an insurer or a safety inspector asks for, and all "
                "of them are currently assumed rather than recorded.",
            ],
            "features": [
                [
                    "Static discharge compliance",
                    "Records wrist-strap and mat verification at shift start for "
                    "benches in controlled zones.",
                    "Board-level work is protected from the commonest invisible "
                    "damage.",
                ],
                [
                    "Hazardous material handling",
                    "Records handling of batteries, refrigerant and chemicals per "
                    "the safety procedure.",
                    "The company can show what was handled and how.",
                ],
                [
                    "Environmental conditions",
                    "Records workshop temperature and humidity where the repair "
                    "type requires it.",
                    "A condition-sensitive repair has the conditions on record.",
                ],
                [
                    "Overnight device security",
                    "Tracks the physical security of devices held overnight, "
                    "including high-value segregation.",
                    "The shift cannot close until high-value devices are in "
                    "secure storage.",
                ],
            ],
            "example": (
                "the shift that could not close",
                "A Thursday evening shift at the central workshop tries to "
                "close at 19:40. The system blocks it: three devices with a "
                "declared value above the high-value threshold are still shown "
                "at benches rather than in secure storage. Two are found on "
                "the shelf beside the bench where the technician left them "
                "mid-repair; one has genuinely been moved but was not recorded. "
                "All three are recorded into the secure store, and the shift "
                "closes at 19:52. The twelve minutes are the entire cost of "
                "the control. The alternative — discovering on Friday morning "
                "that a customer's BDT 210,000 workstation spent the night on "
                "an open bench in an unlocked area — is a conversation with an "
                "insurer that nobody wants to have.",
            ),
            "mistakes": [
                "Clicking through the static-discharge check without doing it. "
                "Electrostatic damage does not announce itself; it appears as "
                "a rework three weeks later.",
                "Recording secure storage before the device is actually in it. "
                "The record is only worth something if it is true.",
                "Treating environmental conditions as optional because the "
                "workshop 'is always fine'. It is required for specific repair "
                "types precisely because those are the ones where it is not.",
            ],
        },
    ],
    # ============================================ 7. the journey
    "s6_title": "The journey of a repair order",
    "s6_lede": "Fifteen states from the workshop door to the outgoing shelf, and the "
    "four that will stop a device leaving.",
    "s6_intro": [
        "A repair order has a longer and more granular life than almost "
        "anything else in the system, and that granularity is the point. "
        "Knowing that a device is 'in the workshop' is nearly useless. Knowing "
        "it is in burn-in with two hours ten remaining, or waiting for a part "
        "with a sourcing request raised, is what lets a supervisor run a "
        "floor and a branch answer a customer.",
        "Two of the states below are not part of the forward path. Waiting is "
        "where a device sits when work has stopped for a recorded reason. And "
        "a failed quality check returns the device to a bench, counting as "
        "internal rework.",
    ],
    "journey": [
        ("Created", "M01, M14 or M45", None),
        ("Booked in", "Workshop clerk", "gate"),
        ("Queued", "Workshop clerk", None),
        ("On bench", "Supervisor", "gate"),
        ("Level confirmed", "Technician", None),
        ("Under repair", "Technician", None),
        ("Waiting", "Technician", "clock aside"),
        ("Testing", "Technician", None),
        ("Burn-in", "System, timed", "cannot shorten"),
        ("Post-burn verify", "Technician", None),
        ("Quality check", "QC inspector", "gate"),
        ("Released", "QC inspector", "gate"),
        ("Outgoing staging", "System", None),
        ("Transferred", "Supervisor", None),
        ("Unrepairable", "Supervisor", None),
    ],
    "journey_title": "The path a repair order follows",
    "journey_sub": (
        "Thirteen states in the forward path, and two ways a "
        "repair can end differently"
    ),
    "journey_caption": "The repair order lifecycle, in the order it happens",
    "s6_stages": [
        [
            "Created",
            "The workshop has been asked to repair something.",
            "M01, M14, M45 or a field return",
            "A parent service order, refurbishment order or internal request. "
            "There is no such thing as an orphan repair order.",
        ],
        [
            "Booked in",
            "The device is physically here.",
            "Workshop clerk",
            "Physical receipt scanned and condition verified against the intake "
            "record.",
        ],
        [
            "Queued",
            "It is waiting for a bench.",
            "Workshop clerk",
            "A location assigned in the incoming buffer.",
        ],
        [
            "On bench",
            "A technician has it.",
            "Supervisor allocates",
            "A free bench, and a technician certified for that repair level and "
            "brand.",
        ],
        [
            "Level confirmed",
            "Somebody has opened it and knows what it needs.",
            "Technician",
            "Bench diagnosis recorded.",
        ],
        [
            "Under repair",
            "The work is happening.",
            "Technician",
            "Parts available or reserved, and re-estimation complete if the level "
            "changed.",
        ],
        [
            "Waiting",
            "Work has stopped for a recorded reason.",
            "Technician",
            "An approved waiting reason selected.",
        ],
        [
            "Testing",
            "The initial functional test is running.",
            "Technician",
            "Repair work recorded complete, with parts and time posted.",
        ],
        [
            "Burn-in",
            "It is running under load for a defined period.",
            "System, timed",
            "The initial test passed and a burn-in station available.",
        ],
        [
            "Post-burn verify",
            "The burn-in period has finished and it is being " "rechecked.",
            "Technician",
            "The configured duration elapsed. It cannot be cut short.",
        ],
        [
            "Quality check",
            "Somebody is checking the work.",
            "QC inspector",
            "The verification test passed.",
        ],
        [
            "Released",
            "It is finished and can leave.",
            "QC inspector",
            "A passed quality checklist, and an independent check for Level 2 and "
            "3.",
        ],
        [
            "Outgoing staging",
            "It is waiting to be collected.",
            "System",
            "Outcome reported to M01 and a staging location assigned.",
        ],
        [
            "Transferred",
            "It has gone to another workshop for a specialist " "stage.",
            "Supervisor",
            "The receiving workshop's confirmation and a logistics consignment.",
        ],
        [
            "Unrepairable",
            "It cannot economically be fixed.",
            "Supervisor",
            "Photographic evidence, a documented cost comparison and a second "
            "technician's confirmation.",
        ],
    ],
    "s6_gates_intro": "Six points will refuse to let a repair proceed. Two are about who is "
    "allowed to do the work, two about what has to be proved, and two "
    "about money and safety.",
    "gates": [
        (
            "A parent record must exist",
            "A repair order cannot be created without a parent service order, "
            "refurbishment order or internal asset request",
            "System",
        ),
        (
            "Certification for the level and brand",
            "A device cannot be allocated to a technician who lacks the "
            "certification for its repair level and brand",
            "System",
        ),
        (
            "The right workshop for Level 3",
            "Board-level repair may only happen at a workshop with the required "
            "equipment and static-control classification",
            "System",
        ),
        (
            "Re-approval if the level rises",
            "A level revision that pushes cost beyond the approved estimate "
            "requires re-approval before work continues",
            "Estimator",
        ),
        (
            "Burn-in in full",
            "Burn-in cannot be shortened below the protocol duration. Extension "
            "is permitted; reduction is not",
            "System",
        ),
        (
            "Quality passed, independently above Level 1",
            "No release without a passed checklist, and for Level 2 and 3 the "
            "check must be by somebody other than the repairer",
            "QC inspector",
        ),
        (
            "High-value devices secured overnight",
            "The shift cannot close until high-value devices held overnight are "
            "recorded into secure storage",
            "Supervisor",
        ),
    ],
    "s6_wrong_intro": "Workshops fail in predictable places, and a supervisor can see most "
    "of them on the board. This is what the states actually mean when they "
    "start piling up.",
    "s6_wrong": [
        [
            "Queued",
            "Devices accumulate in the incoming buffer.",
            "The queue grows while benches show as occupied.",
            "Check bench utilisation. If benches are busy it is a capacity "
            "problem; if not, it is an allocation problem.",
        ],
        [
            "On bench",
            "No certified technician is available for a Level 3 device.",
            "It sits queued with a thin allocation list.",
            "A recurring gap is a training or rostering question, not a dispatch "
            "one.",
        ],
        [
            "Under repair",
            "The device turns out to need more than was estimated.",
            "The level is revised upward and cost exceeds the estimate.",
            "Re-approval first. Continuing is a hard rule violation and the "
            "customer has not agreed to it.",
        ],
        [
            "Waiting",
            "A part is unavailable and the wait is not recorded as waiting.",
            "Bench time looks worse than it is, and the bench is occupied doing "
            "nothing.",
            "Move it to waiting with the reason. It frees the bench and it keeps "
            "the productivity figures honest.",
        ],
        [
            "Burn-in",
            "Devices queue for a burn-in station.",
            "Cycle time in burn-in exceeds the protocol duration — the difference "
            "is queueing.",
            "This is the commonest hidden bottleneck in a workshop. Count "
            "stations against benches.",
        ],
        [
            "Quality check",
            "One inspector, several devices.",
            "A cluster in quality check, usually late in the day.",
            "A rota question. It is also the one queue that must never be cleared "
            "by relaxing the check.",
        ],
        [
            "Quality check failed",
            "Internal rework, which nobody enjoys recording.",
            "The internal rework counter, which is separate and never hidden.",
            "Record it honestly. Attribution feeds coaching, and hidden rework "
            "makes the workshop unable to improve.",
        ],
        [
            "Outgoing staging",
            "Finished devices sit uncollected.",
            "An alert after the threshold, to the branch and logistics.",
            "Chase the collection. Finished work on a shelf is capital and space "
            "doing nothing.",
        ],
    ],
    "s6_note": "A device in 'waiting' has stopped consuming bench capacity, which is "
    "why the state exists. Leaving a stalled repair on a bench because "
    "moving it feels like admitting defeat is the commonest way a workshop "
    "loses capacity it does not know it has lost.",
    # ============================================ 8. day in the life
    "s7_lede": "Five walkthroughs from a workshop week, from a board repair to a "
    "bottleneck nobody had suspected.",
    "s7_intro": [
        "These follow devices and decisions rather than people, because a "
        "workshop day is measured in devices released rather than in "
        "conversations.",
        "Devices, workshops, figures and times are illustrative. The repair "
        "levels, gates, protocols and rules behind them are exactly as the "
        "specification states them.",
    ],
    "scenarios": [
        {
            "title": "A board-level repair, traced end to end",
            "narrative": [
                "Level 3 work, which is the company's genuine competitive "
                "differentiator and the most thoroughly recorded thing that "
                "happens at a bench.",
            ],
            "lanes": [
                ("Branch", [(0, "Sends a laptop under a consignment")]),
                ("Clerk", [(0, "Books in; verifies condition")]),
                ("Supervisor", [(1, "Allocates to an L3 bench and " "technician")]),
                (
                    "Technician",
                    [
                        (2, "Teardown, diagnosis, four photographs"),
                        (3, "Replaces the chip; records batch and " "instrument"),
                    ],
                ),
                (
                    "System",
                    [
                        (3, "Genealogy written; 3h20 active, 40m waiting"),
                        (4, "Evidence attached to the service order"),
                    ],
                ),
            ],
            "columns": ["Booked in", "Benched", "Diagnosed", "Repaired", "Evidenced"],
            "exhibit_title": "A Level 3 board repair, fully traced",
            "exhibit_sub": "Every component, instrument and minute on the " "record",
            "caption": "What board-level work looks like when it is recorded",
            "table": [
                [
                    "1",
                    "Branch and clerk",
                    "A laptop arrives from Mirpur under a logistics consignment. "
                    "It is booked in with condition verified against the intake "
                    "record: no power, suspected power management failure.",
                ],
                [
                    "2",
                    "Supervisor",
                    "Routed to the central workshop because Level 3 requires "
                    "equipment and a static-control classification the branch "
                    "workshop does not have. Allocated to a Level 3 certified "
                    "technician on a board bench.",
                ],
                [
                    "3",
                    "Technician",
                    "Bench diagnosis run, teardown recorded with photographs at "
                    "four defined points, and a failed power management chip "
                    "isolated.",
                ],
                [
                    "4",
                    "Technician",
                    "The repair procedure for that board family appears as a step "
                    "list. Each step recorded with measured values. The "
                    "replacement chip is consumed with its batch captured; "
                    "consumables recorded; the rework station captured by "
                    "instrument identity.",
                ],
                [
                    "5",
                    "System",
                    "Genealogy written: this chip, from this purchase order, into "
                    "this board, in this laptop, on this date. Active bench time "
                    "3 hours 20, distinguished from 40 minutes waiting for the "
                    "part.",
                ],
            ],
            "outcome": "Eight months later the brand queried a warranty claim on that "
            "board, and every one of those facts was still attached to it "
            "— including which instrument made each measurement and when "
            "it was last calibrated. That is the difference between "
            "defending a claim and absorbing it.",
        },
        {
            "title": "The fault that appeared in hour three",
            "narrative": [
                "Why burn-in cannot be shortened, demonstrated on a device "
                "that passed every test it was given and was still broken.",
            ],
            "lanes": [
                (
                    "Technician",
                    [
                        (0, "Replaces a failing capacitor bank"),
                        (1, "Initial functional test passes"),
                        (3, "Finds a second marginal capacitor"),
                    ],
                ),
                (
                    "System",
                    [
                        (2, "Reserves a station; 4-hour burn-in starts"),
                        (2, "Restart captured at 3h10"),
                        (4, "Second burn-in passes cleanly"),
                    ],
                ),
                ("QC", [(4, "Independent check passed; released")]),
            ],
            "columns": ["Repaired", "Tested", "Burn-in", "Reworked", "Released"],
            "exhibit_title": "A device that passed its test and failed its " "burn-in",
            "exhibit_sub": "Four hours of load found what a functional test "
            "could not",
            "caption": "The rework that happened in the workshop instead of at "
            "the customer",
            "table": [
                [
                    "1",
                    "Technician",
                    "A desktop with intermittent restarts. A failing capacitor "
                    "bank on the board is identified and replaced.",
                ],
                [
                    "2",
                    "Technician",
                    "The initial functional test passes. It starts, it runs, it "
                    "shows no fault. Under the old process it would have gone "
                    "back that afternoon.",
                ],
                [
                    "3",
                    "System",
                    "The protocol for this repair type requires four hours of "
                    "burn-in under load. A station is reserved and the timed "
                    "state begins.",
                ],
                [
                    "4",
                    "System and technician",
                    "At three hours ten the machine restarts. The burn-in record "
                    "captures it. Back to the bench: a second capacitor on the "
                    "same rail, within tolerance at room temperature and not "
                    "under a three-hour thermal load.",
                ],
                [
                    "5",
                    "Technician and QC",
                    "Replaced, burn-in run again, passes cleanly. Independent "
                    "quality check passed and the device released the following "
                    "morning.",
                ],
            ],
            "outcome": "The customer got their machine a day later than they might "
            "have, and did not get it back a third time as a rework in "
            "three weeks. This single behaviour is the largest contributor "
            "to the workshop's share of the rework target, and it is the "
            "one most often shortened when a floor is busy.",
        },
        {
            "title": "A bottleneck that was not where anybody thought",
            "narrative": [
                "The measurement walkthrough. A workshop below target for "
                "reasons everybody had confidently misdiagnosed.",
            ],
            "lanes": [
                (
                    "Supervisor",
                    [(0, "Throughput below target; assumes L3 " "capacity")],
                ),
                (
                    "System",
                    [
                        (1, "Cycle time by state: burn-in 6h40 vs 4h " "protocol"),
                        (2, "Five stations against eleven benches"),
                    ],
                ),
                ("Ops Director", [(3, "Approves three more stations")]),
                ("Workshop", [(4, "Throughput rises about a fifth")]),
            ],
            "columns": ["Below target", "Measured", "Diagnosed", "Fixed", "Result"],
            "exhibit_title": "Cycle time by state, and what it revealed",
            "exhibit_sub": "The queue for a station looks exactly like the " "station",
            "caption": "Why a workshop needs its time broken down by state",
            "table": [
                [
                    "1",
                    "Supervisor",
                    "The central workshop is releasing fewer devices per day than "
                    "its bench count suggests. The assumption on the floor is "
                    "that Level 3 capacity is short.",
                ],
                [
                    "2",
                    "System",
                    "Cycle time by state says otherwise. Diagnosis averages 40 "
                    "minutes, repair 2 hours 10, quality check 25 minutes. "
                    "Burn-in averages 6 hours 40 against a protocol duration of "
                    "4 hours.",
                ],
                [
                    "3",
                    "Supervisor",
                    "The extra two hours forty is devices waiting for a burn-in "
                    "station. There are five stations and eleven benches, and a "
                    "device queueing for a station looks exactly like a device in "
                    "burn-in.",
                ],
                [
                    "4",
                    "Operations Director",
                    "Three more burn-in stations are approved. They cost a "
                    "fraction of a technician's annual salary.",
                ],
                [
                    "5",
                    "Workshop",
                    "Throughput rises by roughly a fifth without hiring anybody "
                    "or changing how anybody works.",
                ],
            ],
            "outcome": "Nobody had suspected the burn-in queue, and nobody could "
            "have, because the whiteboard had one column for burn-in. "
            "Breaking cycle time down by state is what turns 'we are busy' "
            "into 'we need three more stations', and it is the mechanism "
            "behind most of the forty per cent throughput target.",
        },
        {
            "title": "A repair type that was losing money",
            "narrative": [
                "Cost against estimate, and a fix that was partly a spreadsheet "
                "and partly a piece of knowledge nobody had written down.",
            ],
            "lanes": [
                (
                    "System",
                    [
                        (0, "L2 printer repairs 34% over estimate"),
                        (1, "Consumables never in the estimating model"),
                        (1, "One fault taking 4h against 90m"),
                    ],
                ),
                ("Finance", [(2, "Corrects the estimating model")]),
                ("Senior technician", [(3, "Documents the paper-feed " "procedure")]),
                ("Workshop", [(4, "Same repair now 1h50; variance in " "tolerance")]),
            ],
            "columns": [
                "Flagged",
                "Diagnosed",
                "Model fixed",
                "Documented",
                "Resolved",
            ],
            "exhibit_title": "A 34 per cent cost variance, traced to two causes",
            "exhibit_sub": "One was arithmetic; one was undocumented knowledge",
            "caption": "What cost-against-estimate reporting finds",
            "table": [
                [
                    "1",
                    "System",
                    "Level 2 printer repairs at one workshop are averaging 34 per "
                    "cent above estimate, well beyond the eight per cent "
                    "tolerance.",
                ],
                [
                    "2",
                    "Investigation",
                    "Two causes. Consumables on printer work — rollers, belts, "
                    "cleaning agents — were never recorded before M31, so the "
                    "estimating model never included them.",
                ],
                [
                    "3",
                    "Investigation",
                    "And one specific paper-feed failure on one model is taking "
                    "an average of four hours against a ninety-minute estimate, "
                    "because no repair procedure exists for it in the library.",
                ],
                [
                    "4",
                    "Finance and a senior technician",
                    "The estimating model is corrected for consumables. A senior "
                    "technician documents the paper-feed procedure and it is "
                    "promoted to the technical library.",
                ],
                [
                    "5",
                    "Workshop",
                    "The same repair now takes one hour fifty. Variance falls "
                    "inside tolerance the following month.",
                ],
            ],
            "outcome": "The company had been quietly losing money on a repair type it "
            "believed was profitable. Neither cause was findable before, "
            "because consumables were not recorded and because the four "
            "hours looked like a difficult repair rather than an "
            "undocumented one.",
        },
        {
            "title": "The shift that could not close",
            "narrative": [
                "The smallest walkthrough here, and the one that would have "
                "cost the most.",
            ],
            "lanes": [
                ("Shift", [(0, "Tries to close at 19:40")]),
                ("System", [(0, "Blocks: three high-value devices at benches")]),
                (
                    "Supervisor",
                    [
                        (1, "Finds two on a shelf, one unrecorded"),
                        (2, "Records all three into secure storage"),
                    ],
                ),
                ("Shift", [(3, "Closes at 19:52")]),
            ],
            "columns": ["Close attempted", "Blocked", "Resolved", "Closed"],
            "exhibit_title": "Twelve minutes, and one conversation avoided",
            "exhibit_sub": "High-value devices, secure storage, shift close",
            "caption": "A small control with a large downside behind it",
            "table": [
                [
                    "1",
                    "Shift and system",
                    "A Thursday evening shift tries to close at 19:40. The system "
                    "blocks it: three devices above the high-value threshold are "
                    "still shown at benches rather than in secure storage.",
                ],
                [
                    "2",
                    "Supervisor",
                    "Two are found on the shelf beside the bench where the "
                    "technician left them mid-repair. One has genuinely been "
                    "moved but was never recorded.",
                ],
                [
                    "3",
                    "Supervisor",
                    "All three are recorded into the secure store. The shift "
                    "closes at 19:52.",
                ],
            ],
            "outcome": "Twelve minutes is the entire cost of the control. The "
            "alternative is discovering on Friday morning that a "
            "customer's BDT 210,000 workstation spent the night on an open "
            "bench in an unlocked area — which is a conversation with an "
            "insurer, and possibly with a customer, that nobody wants to "
            "have.",
        },
    ],
    "s9t_lede": "Five stories, and four ideas that recur in all of them.",
    "s9t_intro": [
        "The walkthroughs covered a board repair, a burn-in catch, a "
        "bottleneck, a costing failure and a shift close. Two describe money "
        "found, two describe failures prevented, and one describes evidence "
        "that survived eight months.",
        "What they share is that in each case a measurement or a record made "
        "at the bench answered a question somebody asked much later.",
    ],
    "s9t_table": [
        [
            "Record it at the bench, not afterwards",
            "The board repair: genealogy, instrument identity and time captured "
            "as the work happened.",
            "A record made a day later from a paper form is missing precisely the "
            "details a warranty dispute turns on.",
        ],
        [
            "Break the time down or you cannot improve it",
            "The burn-in bottleneck, invisible until cycle time was split by " "state.",
            "'We are busy' is not actionable. 'Two hours forty of queueing for a "
            "station' is.",
        ],
        [
            "Gates cost minutes and save days",
            "Burn-in finding the second capacitor; the shift close finding three "
            "high-value devices.",
            "Every one of these gates is mildly inconvenient at the moment it "
            "fires and far cheaper than the thing it prevented.",
        ],
        [
            "Undocumented knowledge is a cost, not a skill",
            "The paper-feed repair taking four hours because nobody had written "
            "it down.",
            "A specialist's technique that lives only in their head is a "
            "single point of failure with a price attached.",
        ],
        [
            "Honest counting makes improvement possible",
            "Internal rework counted separately and never hidden.",
            "A workshop that hides its own failures cannot find its own "
            "bottlenecks.",
        ],
    ],
    "s9t_close": "The forty per cent throughput gain is not a technology outcome. It "
    "comes from seeing where the time actually goes, which requires "
    "somebody at a bench recording start, pause, resume and stop honestly "
    "— and a supervisor willing to be told the bottleneck is not where "
    "they assumed.",
    # ============================================ 10. rules
    "s8_lede": "Fourteen rules, thirteen of them hard blocks. Most protect either a "
    "warranty claim or somebody's fingers.",
    "s8_intro": [
        "Workshop rules divide roughly into three groups. Some protect the "
        "quality of the repair — certification gates, independent checks, "
        "burn-in duration. Some protect the commercial position — warranty "
        "parts, harvested components, re-approval when cost rises. And a few "
        "protect people and property.",
        "The one that generates most argument is burn-in. It cannot be "
        "shortened below the protocol duration under any circumstances, "
        "including a busy floor and a waiting customer. The second walkthrough "
        "in section 8 is the reason.",
    ],
    "s8_rules": [
        [
            "Create a repair order with no parent",
            "An orphan repair order has no customer, no promise and no way to "
            "report an outcome.",
            "Create it from the service order, refurbishment order or internal "
            "request that caused it.",
        ],
        [
            "Give a device to a technician without the right certification",
            "The brand voids the warranty claim, and the repair is more likely to "
            "come back.",
            "Allocate to somebody certified for that level and brand. "
            "Certification lives in M22.",
        ],
        [
            "Do Level 3 work in a workshop without the equipment or the "
            "static-control classification",
            "Board-level work in an uncontrolled environment damages what it is "
            "meant to fix.",
            "Route it to a workshop that has both. That is what routing is for.",
        ],
        [
            "Release without a passed quality check",
            "It is the one control that stops unchecked work reaching a customer.",
            "Complete the checklist. For Level 2 and 3 it must be somebody other "
            "than the repairer.",
        ],
        [
            "Declare a device unrepairable on one person's word",
            "The customer may well challenge it, and it ends their repair.",
            "Capture photographic evidence, a documented cost comparison and a "
            "second technician's confirmation.",
        ],
        [
            "Put two active repairs on one bench",
            "Occupancy stops being measurable, and utilisation is one of the "
            "numbers throughput improvement is built on.",
            "One bench, one active repair. Hold your other devices in burn-in or "
            "waiting.",
        ],
        [
            "Shorten burn-in",
            "The fault that appears in hour three is exactly the fault that comes "
            "back as a rework.",
            "Extend it if you need to. Never reduce it, whatever the floor looks "
            "like.",
        ],
        [
            "Use a brand warranty part on a non-warranty repair",
            "The part was supplied for a specific claim and using it elsewhere is "
            "a commercial and contractual problem.",
            "Consume from ordinary stock. The system checks at consumption.",
        ],
        [
            "Ignore a lapsed calibration warning",
            "Every measurement that instrument makes becomes questionable, "
            "retrospectively.",
            "This is the one approved-override rule here: you may proceed, and "
            "the quality record is flagged for review. Do it knowingly.",
        ],
        [
            "Hide internal rework",
            "A workshop that cannot see its own failures cannot find its own "
            "bottlenecks.",
            "Record it. It is counted separately from customer returns precisely "
            "so that it is safe to record honestly.",
        ],
        [
            "Continue after the repair level rises past the approved estimate",
            "The customer agreed to a price for a different job.",
            "Stop and get re-approval. Discovering the job is bigger is normal; "
            "continuing is not.",
        ],
        [
            "Use a harvested component on a warranty repair",
            "Its provenance is a donor board, and the brand will reject it.",
            "Use a new part for warranty work. Harvested components are tracked "
            "separately for this reason.",
        ],
        [
            "Leave a high-value device out overnight",
            "It is somebody else's property and the insurance position depends on "
            "it.",
            "Record it into secure storage. The shift will not close otherwise.",
        ],
        [
            "Transfer to another workshop without confirmation",
            "A device in transit between two workshops that neither has confirmed "
            "is a device nobody is accountable for.",
            "Get the receiving workshop's confirmation. The logistics consignment "
            "is created automatically.",
        ],
    ],
    "s8_note": "There is exactly one approved-override rule in this module — "
    "proceeding with a lapsed-calibration instrument, which flags the "
    "quality record. Everything else is a hard block, and the burn-in rule "
    "is the one people most often wish were not.",
    # ============================================ 11. automation
    "s9_lede": "Twelve behaviours that run without anybody asking, and most of them "
    "move a device to the next state so nobody has to remember.",
    "s9_intro": [
        "A workshop's automation is mostly about handoffs. A bench becomes "
        "free and the next repair is proposed. An initial test passes and a "
        "burn-in station is reserved. Burn-in finishes and the technician is "
        "prompted. Quality fails and the device returns to a bench with the "
        "reason recorded.",
        "Two are protective. When an instrument's calibration lapses it is "
        "marked out of service and any quality record created with it is "
        "flagged. And the shift cannot close until high-value devices held "
        "overnight are recorded into secure storage.",
    ],
    "automation_groups": [
        (
            "Getting work onto a bench",
            3,
            "Repair order created and routed, condition verified, next job " "proposed",
        ),
        (
            "Moving through the process",
            4,
            "Re-approval on level change, parts requests, burn-in reserved, "
            "post-burn prompt",
        ),
        (
            "When something fails",
            3,
            "Quality failure loop, calibration lapse, staging overdue",
        ),
        ("Closing out", 2, "Release reported to M01, shift close and secure storage"),
    ],
    "s9_table": [
        [
            "Creates the repair order, selects the workshop by capability and "
            "load, and notifies the supervisor",
            "A service order is routed to the workshop",
            "The receiving workshop supervisor",
        ],
        [
            "Verifies condition against the intake record and flags discrepancies "
            "to the originating branch",
            "A device is booked in",
            "The branch that sent it, immediately",
        ],
        [
            "Proposes the next repair order from the queue by risk and skill " "match",
            "A bench becomes free",
            "The supervisor, who accepts or chooses differently",
        ],
        [
            "Recalculates cost, compares it to the approved estimate and requests "
            "re-approval if exceeded",
            "The repair level is revised upward",
            "The estimator and the customer",
        ],
        [
            "Raises a parts request, moves the order to waiting and notifies M01 "
            "with a revised estimate",
            "Parts are unavailable at the bench",
            "Inventory, and the customer through M01",
        ],
        [
            "Reserves a burn-in station, starts the timed session and sets the "
            "completion prompt",
            "The initial test passes",
            "The technician, when it finishes",
        ],
        [
            "Prompts the technician for post-burn verification, escalating if it "
            "is not actioned",
            "The burn-in duration elapses",
            "The technician, then the supervisor",
        ],
        [
            "Returns the device to a bench, records the reason, increments the "
            "internal rework counter and raises a quality event",
            "A quality check fails",
            "The technician and the quality manager",
        ],
        [
            "Reports outcome, work summary, parts and test results to M01 and "
            "assigns an outgoing staging location",
            "A repair order is released",
            "The branch, the customer through M01, and logistics",
        ],
        [
            "Alerts the originating branch and logistics",
            "A device sits in outgoing staging beyond the threshold",
            "The branch and logistics",
        ],
        [
            "Marks the instrument out of service and flags any quality record "
            "created with it",
            "An instrument's calibration lapses",
            "The supervisor, immediately",
        ],
        [
            "Prompts for secure storage recording and produces the shift summary",
            "Shift close",
            "The supervisor. The shift will not close until it is done",
        ],
    ],
    # ============================================ 12. permissions
    "s10_lede": "Eleven roles, and one dividing line drawn by certification rather "
    "than by seniority.",
    "s10_intro": [
        "Most permission models here are ordinary — supervisors run their own "
        "workshop, technicians see their own assigned repairs, branches see "
        "what they sent. The distinctive thing is that a technician's "
        "permissions are set by what they are certified for rather than by "
        "their job title.",
        "A Level 1 technician can be given Level 1 repairs and nothing else. A "
        "Level 2 technician can take Level 1 and 2. Only a Level 3 specialist "
        "can be allocated board-level work, and only in a workshop with the "
        "equipment. That is not a hierarchy of trust; it is a hierarchy of "
        "certification, and it changes the moment somebody's certification "
        "changes.",
    ],
    "permissions": {
        "roles": [
            "Operations Director",
            "Workshop Supervisor",
            "Specialist Technician L3",
            "Senior Technician L2",
            "Junior Technician L1",
            "Quality Manager",
            "Branch Manager",
            "Service Centre Agent",
            "Inventory Manager",
            "Warranty Claims Officer",
            "Logistics Coordinator",
        ],
        "actions": [
            "Allocate a bench",
            "Take an L3 repair",
            "Pass an independent quality check",
            "Release a device",
            "Declare beyond economic repair",
            "See repair cost",
        ],
        "marks": [
            ["y", "v", "v", "y", "y", "y"],  # Operations Director
            ["y", "v", "v", "y", "y", "y"],  # Workshop Supervisor
            ["", "y", "y", "", "", ""],  # Specialist Technician L3
            ["", "", "y", "", "", ""],  # Senior Technician L2
            ["", "", "", "", "", ""],  # Junior Technician L1
            ["", "", "y", "v", "", ""],  # Quality Manager
            ["", "", "", "", "", "y"],  # Branch Manager
            ["", "", "", "", "", ""],  # Service Centre Agent
            ["", "", "", "", "", ""],  # Inventory Manager
            ["", "", "", "", "", ""],  # Warranty Claims Officer
            ["", "", "", "", "", ""],  # Logistics Coordinator
        ],
        "sub": "Six actions, and the level gate that decides three of them",
    },
    "s10_roles": [
        [
            "Workshop supervisor",
            "Running one workshop floor",
            "Allocating benches, overriding the queue sequence, and authorising "
            "transfers",
        ],
        [
            "Specialist technician, Level 3",
            "Board-level and micro-soldering",
            "Being the only person who may be allocated Level 3 work",
        ],
        [
            "Senior technician, Level 2",
            "Component-level repair",
            "Nothing exclusive — but the certification widens what they can be "
            "given",
        ],
        [
            "Junior technician, Level 1",
            "Basic repair",
            "Nothing exclusive. Progression to Level 2 is measurable, which makes "
            "promotion defensible",
        ],
        [
            "Quality manager",
            "Quality records and rework across all workshops",
            "Recording the independent quality check, and reviewing "
            "calibration-flagged records",
        ],
        [
            "Operations Director",
            "Throughput and cycle time across the estate",
            "Approving beyond-economic-repair, and seeing cost everywhere",
        ],
        [
            "Branch manager",
            "Devices they sent to a workshop",
            "Seeing repair cost for their own branch's work",
        ],
        [
            "Service centre agent",
            "Answering a customer at the counter",
            "Read-only on their branch's repair orders",
        ],
        [
            "Inventory manager",
            "What components were consumed",
            "Read-only on component consumption and genealogy",
        ],
        [
            "Warranty claims officer",
            "Evidence for a claim",
            "Read-only on test results, measurements and photographs",
        ],
        [
            "Logistics coordinator",
            "Devices ready to move",
            "Outgoing staging and workshop transfers",
        ],
    ],
    "s10_restrictions_intro": "Three restrictions are enforced. The first is a separation of duties "
    "and the other two are about not letting the wrong information shape a "
    "technical judgement.",
    "s10_restrictions": [
        [
            "Independent quality check on your own repair",
            "Nobody. For Level 2 and Level 3 the check must be by somebody other "
            "than the repairing technician.",
            "A check by the person who did the work is not a check, and the "
            "certification the company holds depends on it being one.",
        ],
        [
            "Repair cost and margin",
            "The Operations Director, branch and workshop managers, and finance. "
            "Technicians see labour minutes but no monetary rates.",
            "A technician deciding whether a repair is worth continuing should be "
            "making a technical judgement, not a commercial one.",
        ],
        [
            "Allocation above your certification",
            "Enforced absolutely. A Level 1 technician cannot be given Level 2 "
            "work regardless of who asks.",
            "The gate is about competence rather than trust, and it changes the "
            "day somebody's certification does.",
        ],
        [
            "Beyond-economic-repair declaration",
            "A supervisor, with a second technician's confirmation.",
            "It ends the customer's repair and they may well challenge it. One "
            "person's opinion is not enough.",
        ],
        [
            "Bench detail reaching the customer",
            "M31 has no customer-facing surface. Everything the customer sees "
            "comes from M01.",
            "The customer does not need to know their laptop is fourth in a "
            "Level 3 queue, and telling them helps nobody.",
        ],
    ],
    "s10_note": "Certification is held in M22 and enforced here. If a technician "
    "should be able to take work they cannot be allocated, the fix is the "
    "certification record — never a workaround at the allocation screen.",
    # ============================================ 13. measurement
    "s11_lede": "Ten reports and eleven measures, almost every one of them producing a "
    "number the workshop has never had.",
    "s11_intro": [
        "Nothing about workshop performance is currently measured. Devices per "
        "bench per day is unknown. Cycle time is unknown. Bench utilisation is "
        "unknown. Internal rework is unknown, because it is not recorded. "
        "Component genealogy completeness is zero because genealogy does not "
        "exist.",
        "The report that changes the most is cycle time by state. It is the "
        "difference between knowing a workshop is slow and knowing that "
        "devices spend two hours forty queueing for a burn-in station. Almost "
        "every improvement in this module starts there.",
    ],
    "s11_reports": [
        [
            "Workshop work-in-progress board",
            "Every device by state, bench, technician, age and risk — designed "
            "for a wall display",
            "The workshop floor, continuously",
        ],
        [
            "Bench throughput",
            "Devices released per bench per day against target",
            "Supervisors and the Operations Director, daily",
        ],
        [
            "Cycle time by state",
            "Time in queue, diagnosis, repair, waiting, burn-in, quality check "
            "and staging — with the bottleneck named",
            "The Operations Director, weekly",
        ],
        [
            "Internal rework analysis",
            "Rework by technician, repair level, device model and failure reason",
            "The Quality Manager, weekly",
        ],
        [
            "Repair cost against estimate",
            "Variance by repair level and device category",
            "Finance and operations, weekly",
        ],
        [
            "Component failure pattern",
            "Which component fails on which model, with volumes",
            "Quality, and shared with brand partners, monthly",
        ],
        [
            "Bench utilisation",
            "Occupancy against available hours",
            "The workshop supervisor, weekly",
        ],
        [
            "Burn-in station utilisation",
            "Whether station capacity is the constraint",
            "The workshop supervisor, weekly",
        ],
        [
            "Calibration exception report",
            "Repairs performed with instruments whose calibration had lapsed",
            "The Quality Manager, weekly",
        ],
        [
            "Beyond-economic-repair report",
            "Volume, value and pattern of unrepairable determinations",
            "The Operations Director, monthly",
        ],
    ],
    "s11_kpis": [
        [
            "Devices released per bench per day",
            "The headline productivity number for the floor",
            "Forty per cent above baseline, once a baseline exists",
        ],
        [
            "Workshop cycle time, booked in to released",
            "How long a device spends in the workshop",
            "Under 30 hours. Not currently measured",
        ],
        [
            "Bench utilisation",
            "How much of the available bench time is occupied",
            "78 per cent. Not currently measured",
        ],
        [
            "Internal rework rate",
            "Quality-check failures as a share of repairs",
            "Under 5 per cent. Not currently measured",
        ],
        [
            "First-time fix rate, workshop contribution",
            "Repairs finished right the first time",
            "88 per cent, from about 70 per cent",
        ],
        [
            "Quality first-pass rate",
            "Work passing its check on the first attempt",
            "95 per cent. Not currently measured",
        ],
        [
            "Burn-in completed per protocol without shortcut",
            "Whether the discipline is actually holding",
            "100 per cent. Absolute",
        ],
        [
            "Component genealogy completeness",
            "Parts traceable to the board they went into",
            "99 per cent, from nothing",
        ],
        [
            "Calibration exceptions",
            "Repairs performed with a lapsed instrument",
            "Zero by Wave 8, from untracked",
        ],
        [
            "Repair cost variance against estimate",
            "Whether estimates reflect what repairs actually cost",
            "Within 8 per cent. Not currently measured",
        ],
        [
            "Devices in outgoing staging beyond 24 hours",
            "Finished work nobody has collected",
            "Under 2 per cent. Not currently measured",
        ],
    ],
    "dials": [
        ("Devices per bench per day, against a +40% target", "+40%", 0.90),
        ("Bench utilisation", "78%", 0.78),
        ("Quality checks passed first time", "95%", 0.95),
        ("Component genealogy completeness", "99%", 0.99),
    ],
    "s11_reading_title": "Reading cycle time by state",
    "s11_reading": [
        "This is the report that will change how a workshop is run, and it "
        "repays being read carefully rather than glanced at. It breaks the "
        "time between booking in and release into seven states, and the "
        "interesting number is almost never the largest one.",
        "Compare each state against what it should be. Repair time longer than "
        "expected is a skills or procedure question. Burn-in longer than the "
        "protocol duration is queueing, not burn-in. Waiting is parts. Time in "
        "the incoming buffer is bench capacity. Time in staging is not a "
        "workshop problem at all — it is a collection problem.",
    ],
    "s11_reading_table": [
        [
            "Burn-in exceeding the protocol duration",
            "Devices are queueing for a station. The queue looks identical to the "
            "process.",
            "Count burn-in stations against benches. This is the commonest hidden "
            "bottleneck in a repair workshop.",
        ],
        [
            "A large incoming buffer time",
            "Devices are waiting for a bench.",
            "Check bench utilisation. High utilisation means capacity; low means "
            "allocation.",
        ],
        [
            "A large waiting time",
            "Parts. Almost always parts.",
            "Look at the sourcing requests, not the technicians. Also check that "
            "waits are being recorded as waiting rather than left on a bench.",
        ],
        [
            "Repair time varying widely for the same repair type",
            "Usually an undocumented procedure — one technician knows how and the "
            "others are working it out.",
            "Get the technique documented and promoted to the library. The fourth "
            "walkthrough in section 8 is exactly this.",
        ],
        [
            "A cluster in quality check late in the day",
            "One inspector, several devices finishing at once.",
            "A rota question. Never solve it by relaxing the check.",
        ],
        [
            "A large staging time",
            "Finished devices are not being collected.",
            "This is a branch or logistics conversation, not a workshop one — but "
            "it makes the workshop's cycle time look bad, so it is worth raising.",
        ],
    ],
    # ============================================ 14. neighbours
    "s12_lede": "M31 is downstream of the customer's request and upstream of almost "
    "every piece of evidence the company later needs.",
    "s12_intro": [
        "The workshop sits in the middle of the value chain and produces "
        "material that four other modules cannot get anywhere else: component "
        "genealogy for inventory, test evidence for warranty, failure patterns "
        "for quality and the predictive models, and cost data for finance.",
        "That is worth understanding because it changes how a delay here is "
        "felt. A device sitting in a workshop is not just a late repair; it is "
        "an unbilled job, an unclaimed warranty, an unmeasured failure pattern "
        "and a customer being told nothing.",
    ],
    "s12_upstream": [
        [
            "M01 Service Request",
            "The customer's request and the promise",
            "There is no parent record and no repair order can exist",
        ],
        [
            "M14 Refurbishment",
            "Refurbishment orders for trade-in stock",
            "The refurbishment line loses its bench capacity",
        ],
        [
            "M17 Asset Registry",
            "The identity and history of the device",
            "Genealogy has nothing to attach to",
        ],
        [
            "M15 Inventory",
            "Parts, their availability and reservation",
            "Nothing can be consumed and repairs stall at the bench",
        ],
        [
            "M22 Competency",
            "Who is certified for which level and brand",
            "The allocation gate cannot be enforced and warranty claims are " "voided",
        ],
        [
            "M45 Equipment",
            "Test instruments and their calibration status",
            "Measurements cannot be traced and calibration cannot be enforced",
        ],
        [
            "M23 Quality",
            "Checklists and quality standards",
            "The release gate has nothing to check against",
        ],
        [
            "M61 Knowledge",
            "Repair procedures as step lists",
            "Every technician works it out for themselves, expensively",
        ],
        [
            "M03 Logistics",
            "Devices arriving and transfers between workshops",
            "Devices reach the workshop with no custody record",
        ],
    ],
    "s12_downstream": [
        [
            "M01 Service Request",
            "Outcome, work summary, parts and test results",
            "The customer's record and tracking view stop reflecting reality",
        ],
        [
            "M15 Inventory",
            "Component-level consumption and genealogy",
            "Parts leave stock and become untraceable again",
        ],
        [
            "M09 Warranty",
            "Test evidence, measurements and instrument identity",
            "A rejected claim cannot be defended",
        ],
        [
            "M23 Quality",
            "Internal rework, failure reasons and non-conformances",
            "Workshop quality becomes invisible until customers complain",
        ],
        [
            "M17 Asset Registry",
            "Component genealogy written to the device",
            "A device's repair history stays incomplete",
        ],
        [
            "M14 Refurbishment",
            "The completed bench work",
            "Refurbishment has no execution capability",
        ],
        [
            "M03 Logistics",
            "Devices in outgoing staging and workshop transfers",
            "Finished devices have no route back to the branch",
        ],
        [
            "M61 Knowledge",
            "New repair procedures promoted from bench notes",
            "The technical library stops growing",
        ],
        [
            "M26 Intelligence",
            "Component failure patterns by model",
            "Predictive failure models lose their training data",
        ],
        [
            "M12 Analytics",
            "Throughput, cycle time and utilisation",
            "Workshop performance cannot be managed",
        ],
    ],
    "s12_close_up": [
        {
            "title": "The separation that created this module: M31 and M01",
            "text": [
                "The first version of the plan had no M31, and workshop "
                "execution sat inside the service order module. It was split "
                "for the same reason every tier-one service system splits it: "
                "the two objects answer different questions, change at "
                "different rates and have different audiences.",
                "A service order changes a handful of times over days. A "
                "repair order changes fifteen times over hours. A customer "
                "wants one sentence; a workshop supervisor wants a board. Put "
                "both in one record and either the customer is shown bench "
                "detail they cannot use, or the workshop is denied detail it "
                "cannot work without.",
                "The practical rule that follows is simple and worth stating "
                "explicitly: M31 has no customer-facing surface. It reports "
                "state to M01 and M01 decides what the customer sees. A branch "
                "agent may look at the workshop board, but what they tell the "
                "customer should come from the service order.",
            ],
        },
        {
            "title": "The relationship that closes an old gap: M31 and M15 "
            "Inventory",
            "text": [
                "In a repair business the largest single source of inventory "
                "inaccuracy is the gap between a part leaving stock and "
                "arriving in a device. A part is issued, it goes to a bench, "
                "and after that the ledger knows nothing. Some of it is "
                "fitted, some is returned, some is left in a drawer, and some "
                "is genuinely lost.",
                "Component-level consumption with serial or batch capture "
                "closes that gap by recording exactly which component went "
                "into which board. The target for genealogy completeness is "
                "ninety-nine per cent, from a starting point of nothing.",
                "The second half of the relationship is harvesting. "
                "Board-level work routinely takes components from donor boards "
                "and reuses them. Today those parts are invisible: they appear "
                "in no ledger and their provenance is somebody's memory. M31 "
                "records them into inventory with a harvested classification, "
                "which makes them usable — and also enforces the rule that "
                "they can never be used on a warranty repair, because a brand "
                "will reject a claim on a part with no purchase record.",
            ],
        },
    ],
    "s12_note": "Four modules get material from M31 that they cannot obtain anywhere "
    "else: component genealogy, test evidence, failure patterns and repair "
    "cost. A workshop that records well is doing work for four other teams "
    "as a by-product.",
    # ============================================ 15. troubleshooting
    "s13_lede": "What goes wrong at a bench, what it usually means, and what to do "
    "about it.",
    "s13_intro": [
        "Most of what follows is a control working correctly. The exceptions "
        "are worth knowing because they are the ones where something has "
        "genuinely broken rather than been prevented.",
    ],
    "s13_troubleshooting": [
        [
            "I cannot be allocated this repair",
            "You are not certified for that repair level or brand.",
            "That is correct and not a fault. If the certification record is "
            "wrong, it is fixed in M22.",
        ],
        [
            "The device will not move from queued to on bench",
            "No free bench with the required capability, or no certified "
            "technician available.",
            "Check the capacity view. A recurring gap is a rostering or training "
            "question.",
        ],
        [
            "I found the repair is more than was estimated",
            "That is normal and the level revision handles it.",
            "Revise the level. If it pushes cost past the approved estimate, stop "
            "and get re-approval before continuing.",
        ],
        [
            "I need to shorten burn-in to clear the floor",
            "You cannot. It is a hard rule with no override.",
            "Extend it if needed. If the burn-in queue is the constraint, that is "
            "a station count problem and worth raising.",
        ],
        [
            "The quality check failed on my repair",
            "It is recorded as internal rework, attributed and counted.",
            "Take it back, record the fix, and let the counter increment. Hidden "
            "rework is the one thing that makes the workshop unable to improve.",
        ],
        [
            "I cannot record the independent check on my own repair",
            "For Level 2 and Level 3 it must be somebody else.",
            "Hand it to another inspector. The system will not accept it " "otherwise.",
        ],
        [
            "The part I consumed is not showing against the board",
            "Consumption was probably recorded after fitting rather than at the "
            "bench.",
            "Consume at the moment of fitting with the serial or batch captured. "
            "Genealogy recorded from memory is unreliable.",
        ],
        [
            "The instrument is out of calibration and I need it",
            "This is the one approved override in the module.",
            "You may proceed, and the quality record is flagged for review. Do it "
            "knowingly and tell the supervisor.",
        ],
        [
            "My productivity figures look worse than my work",
            "Waiting time is probably being recorded as active bench time.",
            "Use pause and resume properly, and move stalled repairs to waiting. "
            "The distinction exists to protect you.",
        ],
        [
            "A device has been in staging for two days",
            "Nobody has collected it. The alert has already fired.",
            "This is a branch or logistics conversation. It also inflates the "
            "workshop's cycle time, so it is worth chasing.",
        ],
        [
            "The shift will not close",
            "High-value devices held overnight are not recorded into secure "
            "storage.",
            "Record them. It takes minutes and the alternative is an insurance "
            "conversation.",
        ],
        [
            "A harvested part was rejected on a warranty repair",
            "Harvested components cannot be used on warranty work.",
            "Use a new part. The rule exists because the brand will reject a "
            "claim on a part with no purchase record.",
        ],
    ],
    "s13_faq": [
        [
            "Why can a bench hold only one repair?",
            "Because occupancy has to be measurable, and bench utilisation is one "
            "of the numbers the throughput target is built on. You can hold "
            "several devices as a technician — one on the bench and two in "
            "burn-in is normal.",
        ],
        [
            "Can a supervisor authorise a shorter burn-in?",
            "No. Burn-in can be extended and never reduced, by anybody. The "
            "second walkthrough in section 8 is the reason.",
        ],
        [
            "What is the difference between internal and customer rework?",
            "Internal rework is a device that failed its quality check and went "
            "back to a bench, before the customer ever saw it. Customer rework is "
            "a device that came back. They are counted separately because they "
            "mean different things.",
        ],
        [
            "Does the customer see any of this?",
            "No. M31 has no customer-facing surface. The customer's view comes "
            "from M01 and is deliberately simpler.",
        ],
        [
            "Why do I have to record which instrument I used?",
            "So that a measurement can be traced to the instrument that made it "
            "and to its calibration status. It is what survives a brand audit.",
        ],
        [
            "What happens if I solve a fault nobody has documented?",
            "Propose the note for promotion to the technical library. That is how "
            "a specialist's technique stops living only in their head.",
        ],
        [
            "Can I use a warranty part on a paying repair?",
            "No. Brand-supplied warranty parts cannot be consumed on a "
            "non-warranty repair, and the check happens at consumption.",
        ],
        [
            "Who decides a device is beyond economic repair?",
            "A supervisor, with photographic evidence, a documented cost "
            "comparison and a second technician's confirmation. It ends the "
            "customer's repair, so one opinion is not enough.",
        ],
        [
            "Why is my time split into active and waiting?",
            "Because a productivity figure that counts waiting for a part as "
            "unproductive bench time is unfair to you and useless to the "
            "supervisor.",
        ],
        [
            "What happens when a device goes to another workshop?",
            "The receiving workshop confirms, a logistics consignment is created "
            "automatically, and custody passes to M03 for the journey.",
        ],
    ],
    # ============================================ 16. worth
    "s14_lede": "A forty per cent increase in devices per bench per day — the single "
    "largest capacity gain in the programme that does not require hiring "
    "anybody.",
    "s14_intro": [
        "The throughput gain comes from four things at once: identifying the "
        "bottleneck, sequencing the queue by risk rather than arrival, "
        "managing parallel work properly, and eliminating the time technicians "
        "spend hunting for parts and information. None of them requires new "
        "equipment or new people.",
        "The second benefit is harder to see and possibly larger. Test "
        "evidence, instrument traceability and photographs assembled "
        "automatically are what protect the warranty recovery benefit against "
        "rejection. A claim the brand rejects is a claim the company pays for "
        "itself, and today there is no way to argue.",
    ],
    "benefits": [
        ("Workshop throughput", 40, "+40% devices per bench per day"),
        ("Warranty recovery protected", 100, "protects BDT 100 lac/yr"),
        ("Refurbishment capacity enabled", 65, "enables BDT 65 lac/yr"),
    ],
    "benefits_note": (
        "Rework reduction is excluded: the baseline is "
        "unmeasured, so no monetary figure is claimed."
    ),
    "s14_benefits": [
        [
            "Workshop throughput",
            "Bottleneck identification, queue sequencing by risk, parallel work "
            "management, and the elimination of part-hunting time",
            "Forty per cent more devices per bench per day — the largest capacity "
            "gain in the programme",
        ],
        [
            "Rework reduction",
            "Burn-in as an enforced state, independent quality checks on Level 2 "
            "and 3, and internal rework counted and attributed",
            "Contributes directly to the under-3-per-cent rework target. No "
            "monetary figure is stated because the baseline is unmeasured",
        ],
        [
            "Warranty claim defensibility",
            "Test evidence, instrument traceability and photographs assembled "
            "automatically",
            "Protects the BDT 100 lac a year of warranty recovery against " "rejection",
        ],
        [
            "Turnaround time",
            "A visible queue sequenced by risk rather than by arrival order",
            "Supports the under-24-hour IT turnaround target",
        ],
        [
            "Parts accountability",
            "Component-level consumption closes the gap where parts leave stock "
            "untraceably",
            "Contributes to the BDT 34 lac a year inventory benefit",
        ],
        [
            "Refurbishment capacity",
            "The same bench infrastructure serves repair and refurbishment with "
            "shared measurement",
            "Enables the BDT 65 lac a year refurbishment margin without a "
            "separate facility",
        ],
        [
            "Fewer losses on unrepairable devices",
            "A cost-against-value comparison made explicit before work proceeds",
            "Avoids spending BDT 8,000 of labour on a BDT 6,000 device",
        ],
    ],
    "s14_soft": [
        [
            "Board-level expertise becomes visible",
            "The company's Level 3 capability is a genuine competitive moat in "
            "Bangladesh. Today it is undocumented and concentrated in a few "
            "people, which makes it fragile.",
        ],
        [
            "Technique capture",
            "A successful repair on an unfamiliar fault becomes a knowledge "
            "article rather than being forgotten — and the fourth walkthrough "
            "shows what one undocumented procedure was costing.",
        ],
        [
            "Evidence for progression",
            "A junior technician's movement from Level 1 to Level 2 becomes "
            "measurable, which makes promotion decisions defensible.",
        ],
        [
            "ISO 9001 conformance at the point of production",
            "Documented work instructions, controlled conditions and traceability "
            "are what clause 8.5.1 asks for.",
        ],
        [
            "Calibration traceability",
            "The link between a measurement and the instrument that made it is "
            "what survives a brand audit.",
        ],
        [
            "Safety discipline",
            "Static control and hazardous-material handling recorded rather than "
            "assumed.",
        ],
    ],
    "s14_close": "Judge this module on devices released per bench per day and on cycle "
    "time by state. The first says whether the workshop is getting better; "
    "the second says where to look next. Everything else in this section "
    "follows from those two being measured honestly for the first time.",
    # ============================================ 17. learning it
    "s17_lede": "A fortnight for a technician, most of it on real devices, and a day "
    "for a supervisor learning to read the board.",
    "s17_intro": [
        "Bench work is learned by doing it. The plan below puts a technician "
        "on a real repair on the first day and builds the recording habits "
        "alongside the technical ones, because habits installed later never "
        "stick.",
        "The single most important habit is recording at the bench rather than "
        "afterwards. A technician who does everything correctly and writes it "
        "up at five o'clock has produced a worse record than one who is slower "
        "and records as they go.",
    ],
    "s17_plan": [
        [
            "Before you start",
            "Read section 1, then find yourself in section 2, then read the board "
            "repair walkthrough in section 8.",
            "20 minutes",
            "Know what a well-recorded repair looks like",
        ],
        [
            "Day one",
            "Do one real Level 1 repair with somebody beside you. Scan in, "
            "diagnose, record teardown, consume the part at the bench, record "
            "time properly.",
            "1 repair",
            "Complete a repair without paper",
        ],
        [
            "Day two",
            "Read section 6.3. Do two more repairs, deliberately using pause and "
            "resume when you wait for anything.",
            "2 repairs",
            "Separate work from waiting",
        ],
        [
            "Day three",
            "Read section 6.4. Watch a burn-in from start to post-burn "
            "verification, and watch one independent quality check.",
            "45 minutes",
            "Understand the gates before you meet them",
        ],
        [
            "End of week one",
            "Read section 10. Deliberately trigger two of the blocks — allocation "
            "above your level, and consuming a warranty part on a paying repair.",
            "30 minutes",
            "Recognise a rule rather than assuming a fault",
        ],
        [
            "Week two, early",
            "Consume a part with serial capture and check the genealogy record "
            "afterwards. Look at what inventory now knows.",
            "30 minutes",
            "Understand why the serial matters",
        ],
        [
            "Week two, middle",
            "Read section 15 and section 6.6. Do a shift close including secure "
            "storage recording.",
            "40 minutes",
            "Close a shift properly",
        ],
        [
            "Supervisors, any time in week two",
            "Read section 13 and spend an hour with cycle time by state for your "
            "own workshop. Find your bottleneck.",
            "1 hour",
            "Read the board rather than watching the floor",
        ],
        [
            "End of week two",
            "Read section 18 and keep it at the bench.",
            "15 minutes",
            "Work unsupervised",
        ],
    ],
    "s17_check_intro": "You have got it when these are automatic. For a technician that is "
    "usually about twenty repairs; the recording habits arrive before the "
    "technical range does.",
    "s17_checks": [
        "Record a teardown as you do it, with photographs at the defined " "points",
        "Consume a part at the moment of fitting, with the serial captured",
        "Use pause and resume so your own figures reflect your work",
        "Say why you cannot be allocated a particular repair",
        "Explain to a colleague why burn-in cannot be shortened",
        "Record an internal rework honestly, including your own",
        "Propose a repair note for the library when you solve something new",
        "Know the three things to report immediately: an instrument out of "
        "calibration, a high-value device left out overnight, and a bench "
        "showing two active repairs",
    ],
    "s17_note": "If you are training technicians, remove the paper job card on day "
    "one. Recording at the bench and writing up later are different "
    "habits, and only one of them produces a record a warranty claim can "
    "be defended with.",
    # ============================================ 18. one page
    "s15_lede": "The module on one page, for a workshop wall.",
    "s15_figures": [
        ("53", "things you can do"),
        ("15", "repair order states"),
        ("14", "rules enforced"),
        ("12", "automatic behaviours"),
        ("3", "repair levels, gated"),
        ("1", "active repair per bench"),
        ("10", "reports available"),
        ("10", "modules depend on it"),
    ],
    "s15_never": [
        "Create a repair order with no parent record",
        "Take a repair above your certification level",
        "Do Level 3 work in a workshop without the equipment and static " "control",
        "Put two active repairs on one bench",
        "Shorten burn-in below the protocol duration",
        "Release without a passed quality check, or check your own Level 2 or "
        "3 work",
        "Use a brand warranty part on a paying repair, or a harvested part on "
        "a warranty repair",
        "Continue after the level rises past the approved estimate",
        "Leave a high-value device out overnight",
    ],
    "s15_where": CM.where_to_look("M31"),
}
