# -*- coding: utf-8 -*-
"""
M03 — Service Logistics & Reverse Logistics.

Every physical movement of every item, and the unbroken record of who held it.
The module is unusual in that its central product is not a service but a proof:
the custody ledger is what turns a lost laptop from an argument into a fact.

Worked examples name customers, places and values so the reader can picture the
movement. Those details are illustrative; the thresholds, rules and states come
from the specification.
"""
from bizcontent import common as CM

CONTENT = {

    # ============================================================== front
    "cover_line":
        "Every physical movement of every item, and the unbroken record of who "
        "held it and when. When a customer's laptop goes missing between six "
        "pairs of hands, this is the module that can say where.",

    "cover_inside": [
        ("Part one", "What the module is for, who uses it, and where it stops"),
        ("Part two", "All forty-two things it lets you do, with worked "
                     "examples and five walkthroughs from a normal day"),
        ("Part three", "The rules, the automatic work, the permissions, the "
                       "measures and the troubleshooting"),
        ("Appendix A", "The full technical register for builders and testers"),
    ],

    "about": CM.about("the Service Logistics and Reverse Logistics module, "
                      "M03"),
    "audience": CM.AUDIENCE,
    "how_arranged": CM.HOW_ARRANGED,
    "parts_table": CM.parts_table("M03"),
    "reading_note": CM.READING_NOTE,
    "appendix_note": CM.APPENDIX_NOTE,
    "part1_blurb": CM.PART1_BLURB,
    "part2_blurb": CM.PART2_BLURB,
    "part3_blurb": CM.PART3_BLURB,
    "appendix_blurb": CM.APPENDIX_BLURB,
    "part1_sections": CM.part1_sections(
        "M03", "The kinds of movement it has to carry"),
    "part2_sections": CM.part2_sections("The journey of a consignment"),
    "part3_sections": CM.PART3_SECTIONS,
    "appendix_sections": CM.APPENDIX_SECTIONS,
    "change_control": CM.CHANGE_CONTROL,
    "change_table": CM.change_table("The Logistics Manager"),
    "change_note": CM.CHANGE_NOTE,

    # ============================================================ exhibits
    "headline": [
        ("6", "pairs of hands on one repair journey", "today, recorded "
                                                      "nowhere"),
        ("42", "things the module lets you do", None),
        ("<0.1%", "target loss and damage rate", None),
        ("100%", "proof of delivery capture", "from nothing today"),
        ("-15%", "cost per consignment by Wave 6", None),
        ("4", "business lines depend on it", "rental, trade-in, refurb, "
                                             "e-waste"),
        ("BDT 190 lac", "a year it makes possible elsewhere", None),
        ("0", "acceptable custody gaps", "not low — zero"),
    ],

    "volume": [
        ("6", "handovers", "on a single pick-and-drop repair"),
        ("5", "sources of movement", "service, rental, transfer, return, "
                                     "recycling"),
        ("2", "kinds of carrier", "own riders and courier partners"),
        ("12", "rules enforced", "eight of them hard blocks"),
        ("0", "tolerated custody gaps", "the ledger is append-only"),
    ],
    "volume_title": "Why movement needs its own module",
    "volume_sub": "A device changes hands more often than most people realise",
    "volume_caption": "The number of handovers in one ordinary repair journey",

    "does": [
        "Creating a consignment from any source that needs something moved",
        "Journeys with several legs, each with its own carrier and evidence",
        "The manifest: serials, declared value, condition and photographs",
        "Chain of custody — a scan and an identity at every single handover",
        "Proof of collection and proof of delivery, with OTP and signature",
        "The custody ledger, which can be added to but never edited",
        "Packaging, seals and tamper detection",
        "Scheduling collections and deliveries into windows people can keep",
        "Riders, their manifests and their mobile application",
        "Courier partners: booking, tracking, and reconciling their invoices",
        "Charging for movement, and waiving the charge where it is due",
        "Returns to vendors, returns to origin, and transfers to recycling",
        "Cash collected on delivery, reconciled per rider per shift",
        "Loss and damage claims, settled from the custody record",
    ],
    "does_not": [
        "The customer's promise and the service order, which are M01",
        "Repairing anything — movement stops at the workshop door, which is "
        "M31",
        "Sending a technician to a job, which is M02 Field Service",
        "What an item is worth as stock, which is M15 Inventory",
        "Bins, put-away and picking inside a warehouse, which is M41",
        "Vehicles, their servicing and documents, which is M46",
        "Employing, rostering or paying riders, which is Category H",
        "Sending the message to the customer, which is M27",
        "Raising the invoice for the logistics charge, which is M20",
        "Recycling partner certification and disposal certificates, which is "
        "M18",
        "Destroying the data before disposal, which is M06 — but M03 will not "
        "move the item without M06's certificate",
    ],

    "areas_map": [
        ("Setting up the movement", 7,
         "One consignment, several legs, everything on it listed and "
         "photographed."),
        ("Proving who held it", 8,
         "A scan and an identity at every handover, into a ledger nobody can "
         "edit."),
        ("Riders and scheduling", 10,
         "Windows, manifests, hubs, load planning and the rider's phone."),
        ("Working with couriers", 6,
         "Booking, tracking, reconciling and scoring outside carriers."),
        ("Charging, returns and things going wrong", 11,
         "What it costs, who pays, what comes back, and what happens when it "
         "is lost."),
    ],

    "area_bars": [
        ("Charging, returns and things going wrong", 11),
        ("Riders and scheduling", 10), ("Proving who held it", 8),
        ("Setting up the movement", 7), ("Working with couriers", 6),
    ],

    "channels": [
        "A pick-and-drop request at intake",
        "A rental device going out to a customer",
        "A rental device being collected back",
        "An inter-branch transfer",
        "A device the workshop needs from a branch",
        "A failed on-site repair converting to a collection",
        "A defective part going back to a vendor",
        "A trade-in device coming in",
        "End-of-life equipment going to recycling",
        "A marketplace fulfilment",
    ],
    "channels_hub": "Consignment",
    "channels_title": "Ten reasons something has to move",
    "channels_sub": ("Whatever the reason, one consignment carries the "
                     "manifest, the custody chain and the evidence"),
    "channels_note": "one record, one chain",
    "channels_caption": "Everything that generates a physical movement",

    # ============================================ 1. what it is for
    "s1_lede":
        "M03 owns every physical movement of every item, and the unbroken "
        "chain of custody that proves who held it and when.",

    "s1_intro": [
        "Consider an ordinary pick-and-drop repair. A laptop is collected from "
        "a customer's home in Uttara by a rider. The rider takes it to the "
        "Mirpur branch. The branch sends it to the Dhaka central workshop for "
        "board-level work. The workshop returns it to the branch. A rider "
        "takes it back to the customer. That is six pairs of hands, and today "
        "the whole journey is coordinated by telephone and recorded nowhere.",

        "At the volumes 1000FiX is planning, some devices will be lost and "
        "some will be damaged. That is not pessimism, it is arithmetic. The "
        "question is not whether it happens but what the company can say when "
        "it does. Today the answer is nothing, and the dispute is settled by "
        "argument. With M03 the answer is a name, a time, a location and a "
        "photograph.",

        "The module's central product, then, is not really a delivery service. "
        "It is a proof. Everything else — the scheduling, the routing, the "
        "courier integration, the charging — exists to produce a custody "
        "ledger that can be added to and never edited, and that names who held "
        "each item at every moment of its journey.",
    ],

    "s1_problem": [
        "Pick and drop is a headline service in the company profile, offered "
        "for laptops, desktops and printers. Reverse logistics is the physical "
        "backbone of four other business lines: rental delivery and "
        "collection, trade-in intake, refurbishment movement and e-waste "
        "collection. Parts returns to vendors, inter-branch transfers and "
        "sub-contractor movements all rely on it too.",

        "All of it currently runs on WhatsApp. A coordinator holds the state "
        "of the operation in their head and their phone. There is no "
        "dashboard, so problems are discovered when somebody complains. Riders "
        "carry a paper list and have no way to prove anything they did. Branch "
        "staff hand a device to whoever turns up wearing the right shirt.",

        "The consequence is that pick and drop cannot grow. A "
        "telephone-coordinated service is limited by one person's memory and "
        "attention, which means it stays a favour for good customers rather "
        "than becoming a channel. And every movement carries an unpriced "
        "risk, because the company cannot prove custody of somebody else's "
        "business laptop.",
    ],

    "s1_replaces": [
        ["Coordination by telephone and WhatsApp",
         "A live dashboard of pending, scheduled, in transit, delivered and "
         "exception consignments",
         "Pick and drop can scale beyond what one coordinator can remember."],
        ["A rider with a paper list",
         "A scannable manifest with an optimised sequence, working offline",
         "The rider can prove what they collected, from whom, and when."],
        ["Handing a device to whoever turns up",
         "A scan and an identity capture from both parties at every handover",
         "'I gave it to someone' stops being an acceptable sentence."],
        ["No record of a journey",
         "An append-only custody ledger per item",
         "A loss becomes a fact with a name attached instead of an argument."],
        ["Devices arriving at the workshop with no paperwork",
         "Book-in against a consignment, with discrepancies flagged at once",
         "A missing charger is noticed on arrival, not three weeks later."],
        ["A customer with no idea where their device is",
         "A tracking link showing custody state and expected return",
         "The commonest anxious phone call disappears."],
        ["Logistics cost that cannot be allocated",
         "Cost attached to the job, contract or business line that caused it",
         "The company finds out what pick and drop actually costs to run."],
        ["Courier invoices paid on trust",
         "Reconciled against consignments delivered and the contracted rate "
         "card",
         "Overbilling stops being invisible."],
    ],

    "s1_one_sentence":
        "M03 turns every physical movement into a numbered consignment with a "
        "manifest, a schedule, a price and — above all — a chain of custody "
        "that can prove who held the item at every step.",

    # ============================================ 2. who uses it
    "s2_lede":
        "A small operational team, a population of riders, and a great many "
        "people who only ever touch it at a handover.",

    "s2_intro": [
        "Most of the people who use M03 use it for about fifteen seconds at a "
        "time. A branch agent scans a device out. A workshop supervisor scans "
        "it in. A customer signs for it. Those brief moments are the whole "
        "point: each one writes a custody event, and the chain is only as good "
        "as its weakest handover.",

        "Behind them sit the two roles that live in the module. The logistics "
        "coordinator works the dashboard the whole day. The rider works the "
        "manifest and the app. Everybody else — finance reconciling courier "
        "invoices, quality reviewing exceptions, legal settling a claim — "
        "comes to the ledger after the fact and reads what those handovers "
        "recorded.",
    ],

    "s2_roles": [
        ["Logistics coordinator",
         "Scheduling collections and deliveries, assigning riders and "
         "couriers, and handling exceptions",
         "The live dashboard: pending, scheduled, in transit, delivered, "
         "exception"],
        ["Rider or delivery agent",
         "Collecting, carrying and delivering, and proving each one",
         "Today's manifest on a phone, in optimised order"],
        ["Branch agent",
         "Handing devices out and taking them in",
         "A scan screen — a few seconds per handover"],
        ["Workshop supervisor",
         "Booking devices in from a consignment and out again",
         "Consignments to and from their own workshop"],
        ["Branch manager",
         "Consignments attached to their branch",
         "The branch's pending and in-transit list"],
        ["Inventory manager",
         "Stock movements between locations",
         "Movements involving stock"],
        ["Procurement officer",
         "Defective parts going back to vendors",
         "Return-to-vendor movements and their credits"],
        ["Finance manager",
         "Charges, cash on delivery and courier invoices",
         "Cost per consignment and the reconciliation"],
        ["Quality manager",
         "Custody exceptions, seal breaks and restricted-item compliance",
         "The daily custody exception report"],
        ["Operations Director",
         "On-time performance and loss rates across the estate",
         "The estate-wide logistics board"],
        ["Customer",
         "Knowing where their device is",
         "A tracking link, and the ability to reschedule"],
        ["Courier partner",
         "The consignments they have been given",
         "Only those, with the minimum data needed to carry them"],
    ],

    "s2_days": [
        {
            "title": "If you coordinate logistics",
            "text": [
                "The dashboard is your day, and it is the thing the Service "
                "App statement of work asked for by name: a real-time view of "
                "pending, delivered and cancelled movements, with scheduling "
                "and rescheduling, viewable per service centre or centrally. "
                "You will spend most of your attention on two columns — "
                "exceptions and overdue — because everything else is "
                "proceeding.",

                "Assignment mostly happens without you. When a pick-and-drop "
                "is requested at intake the consignment is created, the charge "
                "calculated, any entitlement waiver applied and windows "
                "offered, all before you see it. A rider or courier is chosen "
                "by area, declared value and cost. What comes to you is the "
                "movements that do not fit the rules: a restricted item with "
                "no certified carrier available, a high-value consignment "
                "needing an escort, a delivery that has failed twice.",
            ],
        },
        {
            "title": "If you are a rider",
            "text": [
                "Your manifest arrives on the phone in the order the system "
                "wants you to do it. Each stop tells you what to collect or "
                "deliver, from whom, and what evidence you need. The evidence "
                "is not optional and it is not a formality: a scan, both "
                "parties' identity, an OTP, a signature and a photograph of "
                "the sealed package. Without them the app will not let you "
                "record the handover.",

                "That feels heavy for about a week and then it becomes the "
                "thing that protects you. When a customer says a device was "
                "already scratched, or that nothing was collected, the "
                "photograph with the time and place on it settles it in "
                "seconds. You will also notice that you are not shown the "
                "exact declared value of what you are carrying — only a band. "
                "That is deliberate and it is for your safety.",
            ],
        },
        {
            "title": "If you work at a branch or in a workshop",
            "text": [
                "Your involvement is brief and it matters more than its length "
                "suggests. When a device leaves your custody you scan it out; "
                "when one arrives you scan it in. Each scan writes a link in "
                "the chain, and each unscanned handover is a gap that somebody "
                "will eventually have to explain.",

                "Book-in is where discrepancies surface. If the manifest says "
                "a charger and there is no charger, say so at that moment. "
                "The system will raise it immediately, while the previous "
                "custodian is still identifiable. Discovered three weeks later "
                "it is nobody's fault and everybody's problem.",
            ],
        },
        {
            "title": "If you work in finance or claims",
            "text": [
                "Two things change for you. Logistics cost becomes allocable — "
                "every movement carries a cost that attaches to the job, "
                "contract or business line that caused it, so the company "
                "finds out what pick and drop actually costs. And courier "
                "invoices become checkable against consignments actually "
                "delivered and the contracted rate card.",

                "For claims the change is larger. A loss or damage claim today "
                "is a negotiation. With a custody ledger it is a reading "
                "exercise: the record names who held the item last, when, and "
                "where, and whether the seal was intact when they took it.",
            ],
        },
    ],

    "s2_note":
        "Riders see a declared-value band rather than the exact figure. That "
        "is a safety control, not an oversight — the exact value is visible to "
        "coordinators, managers, finance and quality only.",

    # ============================================ 3. boundary
    "s3_lede":
        "M03 moves things and proves custody. It does not repair them, value "
        "them, store them or decide what they are for.",

    "s3_intro": [
        "The boundary here is unusually clean because the module's subject is "
        "physical. M03's responsibility begins when an item is picked up and "
        "ends when it is put down, and its record covers exactly that "
        "interval. What the item is worth as stock belongs to M15. What "
        "happens to it in the workshop belongs to M31. Where it sits inside a "
        "warehouse belongs to M41.",

        "One boundary is worth dwelling on because it is a control rather than "
        "a convenience. M03 will not move an item to a recycling partner "
        "without a valid data destruction certificate from M06. The "
        "certificate is M06's to issue; the refusal to move without it is "
        "M03's to enforce. That is a deliberate separation: the module that "
        "would benefit from moving quickly is not the module that decides "
        "whether it is safe to.",

        "The other distinction people trip over is between M02 and M03. A "
        "technician driving to a customer is service, not logistics. A device "
        "being carried from that customer to a workshop is logistics. The test "
        "is simple: if the point of the journey is the goods, it is M03; if "
        "the point is the person, it is M02.",
    ],

    "s3_shared_intro":
        "Several concepts span the boundary. In each case one module owns the "
        "concept and the others use it.",

    "s3_shared": [
        ["The consignment", "M03 — this module owns it",
         "Creates it, schedules it, carries it, proves it and closes it"],
        ["The custody event", "M03 owns the ledger",
         "Other modules raise events into it; nobody can edit it"],
        ["The device", "M17 Asset Registry",
         "Reads its identity, and records its location and custody"],
        ["The part", "M15 Inventory",
         "Moves it. Does not value it or own the ledger"],
        ["The service order", "M01",
         "The parent context for pick and drop. M03 reports movement against "
         "it"],
        ["The rental agreement", "M13",
         "The parent context for rental delivery and collection"],
        ["The courier partner", "Shared — M03 operationally, M42 commercially",
         "M03 owns booking, tracking and performance; M42 owns the contract"],
        ["The data destruction certificate", "M06 Data Services",
         "Reads it and refuses to move to recycling without it"],
        ["The recycling partner's certification", "M18",
         "Reads it. Compliance and disposal certificates live in M18"],
        ["The vehicle", "M46 Fleet",
         "Records usage. Documents, servicing and telematics live in M46"],
    ],

    # ============================================ 4. kinds of movement
    "s4k_title": "The kinds of movement it has to carry",

    "s4k_lede":
        "Ten reasons something needs to move, from a customer's laptop to a "
        "pallet of end-of-life printers — and one record shape for all of "
        "them.",

    "s4k_intro": [
        "Logistics at 1000FiX is not one service. Pick and drop for a repair "
        "is a two-way journey with a customer at both ends. A rental delivery "
        "is one-way with a deposit attached. An inter-branch transfer has no "
        "customer at all. A recycling movement cannot start until somebody "
        "else has certified that the data is gone.",

        "What they share is the thing that matters: an item, a journey with "
        "legs, and a chain of custody. So they are all consignments, and they "
        "all obey the same handover discipline. What differs is the source, "
        "who pays, and which additional gates apply.",
    ],

    "kinds_columns": [
        ("Customer movements", "A customer at one end or both", [
            "Pick and drop for repair",
            "Rental delivery and collection",
            "Return of a completed repair",
            "Trade-in device coming in",
        ]),
        ("Internal movements", "Between our own places", [
            "Inter-branch transfers",
            "Branch to workshop and back",
            "Scheduled shuttle runs with a standing manifest",
            "Consolidated loads travelling the same route",
        ]),
        ("Outward movements", "Leaving the company for good", [
            "Defective parts back to a vendor",
            "End-of-life equipment to recycling",
            "Cross-border shipments with customs papers",
            "Return to origin after a failed delivery",
        ]),
    ],
    "kinds_title": "Three families of movement",
    "kinds_sub": "Different sources and different gates, one custody chain",

    "s4k_header": ["The kind of movement", "What is different about it",
                   "What stays the same"],
    "s4k_table": [
        ["Pick and drop for repair",
         "Two journeys with the same customer at both ends, usually months of "
         "elapsed time apart, attached to one service order.",
         "A manifest, a scan and identity at every handover, OTP, signature "
         "and photograph"],
        ["Rental delivery and collection",
         "Carries the rental agreement, the deposit position and a condition "
         "grade that matters commercially at both ends.",
         "As above"],
        ["Inter-branch transfer",
         "No customer. Often runs on a scheduled shuttle with a standing "
         "manifest.",
         "As above"],
        ["Branch to workshop",
         "Short, frequent, and the leg where discrepancies most often surface "
         "at book-in.",
         "As above"],
        ["Return to vendor",
         "Carries an RMA reference and is tracked through to the credit note, "
         "so defective-part credits are not written off silently.",
         "As above"],
        ["Trade-in intake",
         "A condition grade set at collection determines what the customer is "
         "paid.",
         "As above"],
        ["Recycling transfer",
         "Blocked outright until a valid data destruction certificate exists, "
         "and only certified partners may receive it.",
         "As above"],
        ["Restricted items",
         "Lithium batteries, refrigerant and similar. Only a rider or courier "
         "certified for them may carry them, and the certification is checked "
         "at assignment.",
         "As above"],
        ["High-value consignments",
         "Above the declared-value threshold: dual signature, insurance "
         "flagging, and possibly an escort or a restricted carrier.",
         "As above"],
        ["Cross-border shipment",
         "Customs documentation and distance-based charging.",
         "As above"],
    ],
    "s4k_caption": "The kinds of movement and what distinguishes each",

    "s4k_note":
        "A zero declared value is not permitted on any consignment. Every item "
        "must carry a declared value before it is collected, because the value "
        "drives the handling controls, the insurance position and any "
        "subsequent claim.",

    # ============================================ 5. vocabulary
    "s4_lede":
        "Thirteen words, most of them from the freight trade rather than the "
        "repair trade.",

    "s4_intro": [
        "Logistics borrows its vocabulary from shipping, and several of these "
        "terms will be unfamiliar to somebody who has spent their career at a "
        "service counter. They are worth learning precisely, because in a "
        "custody dispute the difference between two of them can matter.",
    ],

    "s4_glossary": [
        ["Consignment",
         "One movement instruction covering one or more items travelling "
         "together. The central record of this module.",
         "Created the moment anything needs to move"],
        ["Leg",
         "One stage of a journey with a single carrier. Customer to branch is "
         "one leg; branch to workshop is another.",
         "A pick-and-drop repair typically has four to six"],
        ["Manifest",
         "The list of what is in a consignment: serials, descriptions, "
         "declared values, condition grades and photographs.",
         "Built at creation; custody attaches to each item on it"],
        ["Chain of custody",
         "The unbroken record of who physically held each item, when and "
         "where.",
         "The module's real product"],
        ["Custody event",
         "One link in that chain, written by a scan plus an identity capture "
         "from both parties.",
         "Written at every handover, without exception"],
        ["Custody ledger",
         "The permanent record of custody events. Append-only: corrections are "
         "compensating entries with a stated reason, never edits.",
         "The evidence in any loss or damage claim"],
        ["Proof of collection",
         "The customer's signature, a photograph of the sealed package and OTP "
         "verification, captured when the item is taken.",
         "Required before a consignment can leave 'out for collection'"],
        ["Proof of delivery",
         "Recipient identity, signature, photograph and OTP, captured when the "
         "item is handed over.",
         "A consignment cannot be closed without it"],
        ["Declared value",
         "What the item is worth for handling and insurance purposes. A zero "
         "value is not permitted.",
         "Drives high-value controls; riders see a band, not the figure"],
        ["Seal and tamper tag",
         "The physical seal on a package and its recorded number. A break "
         "raises an incident and stops the consignment.",
         "Recorded at packing, checked at every handover"],
        ["Restricted item",
         "Something only a certified carrier may handle — lithium batteries, "
         "refrigerant and similar.",
         "Checked automatically when a carrier is assigned"],
        ["Return to origin",
         "What happens when delivery has failed as many times as policy "
         "allows.",
         "Automatic, with the charge rules applied"],
        ["Cash on delivery",
         "Money collected by the rider at the point of handover, reconciled "
         "per rider per shift.",
         "Zero tolerance for unexplained variance"],
    ],

    # ============================================ 6. what you can do
    "s5_lede":
        "Forty-two things, in five areas. The second area is the one the "
        "module exists for.",

    "s5_intro": [
        "The areas below follow a consignment's life: setting it up, proving "
        "who held it, getting it scheduled and carried, working with outside "
        "couriers, and settling the money and the exceptions at the end.",

        "If you read only one area, read the second. Chain of custody is the "
        "thing that makes everything else defensible, and it is the part of "
        "the module where the discipline has to be absolute rather than "
        "mostly reliable.",
    ],

    "areas": [
        {
            "title": "Setting up the movement",
            "who": [
                ("Mostly used by", "Logistics coordinators, and the system "
                                   "itself"),
                ("Also relied on by", "Whoever packs the item"),
                ("Where it happens", "At the branch, and at intake"),
            ],
            "intro": [
                "A consignment is created the moment anything needs to go "
                "anywhere, and most of them create themselves: a pick-and-drop "
                "requested at intake, a rental due for delivery, a failed "
                "on-site repair converting to a collection. What a person adds "
                "is the physical detail — what is actually in the package, "
                "what condition it is in, and how it has been sealed.",

                "The important idea here is the multi-leg journey. A repair "
                "collection is not one movement; it is customer to branch, "
                "branch to workshop, workshop to branch, branch to customer. "
                "Each leg has its own carrier, its own window and its own "
                "evidence, and the customer sees one journey.",
            ],
            "features": [
                ["Consignment creation",
                 "Creates a movement from any source — pick and drop, rental, "
                 "transfer, vendor return, recycling, marketplace "
                 "fulfilment.",
                 "A collection requested at the counter exists before the "
                 "customer has left."],
                ["Multi-leg journeys",
                 "Models the whole journey as ordered legs, each with its own "
                 "carrier, window, status and evidence.",
                 "Customer to branch to workshop and back is one journey, not "
                 "four unrelated errands."],
                ["Item manifest",
                 "Lists every item with serial, description, declared value, "
                 "condition grade and photographs, and attaches custody to "
                 "each item.",
                 "Two laptops in one bag are two custody chains, not one."],
                ["Packaging and sealing",
                 "Records packaging type, seal or tamper-tag number, weight "
                 "and dimensions.",
                 "A seal number written down is what makes tamper detection "
                 "possible later."],
                ["Consignment lifecycle",
                 "Enforces the state model with a guard at every transition.",
                 "Nothing moves on until the evidence for the last step "
                 "exists."],
                ["Consolidated movements",
                 "Puts several items travelling the same route into one "
                 "physical movement while keeping each item's custody "
                 "separate.",
                 "One van run instead of five, with no loss of "
                 "accountability."],
                ["Scheduled inter-branch runs",
                 "Operates shuttle runs between branches and hubs on a "
                 "standing manifest.",
                 "Routine internal movement stops needing a decision every "
                 "time."],
            ],
            "example": (
                "one repair, four legs",
                "A customer in Uttara requests pick and drop for a laptop with "
                "a suspected board fault. The consignment is created at "
                "intake, the charge calculated at BDT 350 for the zone, and "
                "the customer's Privilege Silver tier checked — no waiver "
                "applies, so the charge stands and is shown before booking. "
                "The journey is modelled as four legs: Uttara to Mirpur "
                "branch, Mirpur to the Dhaka central workshop, workshop back "
                "to Mirpur, Mirpur back to Uttara. The manifest lists the "
                "laptop with its serial, a declared value of BDT 95,000, a "
                "condition grade with three photographs, and the charger. The "
                "rider seals the package and records tamper tag 4471. Four "
                "weeks later, when the customer asks why the return delivery "
                "is late, the tracking link shows exactly which leg it is on "
                "and who is holding it."),
            "mistakes": [
                "Creating one consignment for two customers' devices because "
                "they are going the same way. Consolidate the movement, not "
                "the record.",
                "Leaving the declared value blank or entering a nominal "
                "figure. A zero value is refused, and a wrong one undermines "
                "any later claim.",
                "Sealing a package without recording the tag number. The seal "
                "is worthless as evidence if nobody wrote down which seal it "
                "was.",
                "Photographing the package instead of the item. The condition "
                "photographs need to show the device, because that is what the "
                "dispute will be about.",
            ],
        },
        {
            "title": "Proving who held it",
            "who": [
                ("Mostly used by", "Riders, branch agents and workshop staff — "
                                   "briefly, many times a day"),
                ("Also relied on by", "Quality, finance and legal, after the "
                                      "fact"),
                ("Where it happens", "At every single handover"),
            ],
            "intro": [
                "This is the module. Everything else is scaffolding around it. "
                "At every handover both parties are scanned and identified, "
                "with location and time captured, and a custody event is "
                "written to a ledger that can be added to but never edited. "
                "Corrections are compensating entries with a stated reason, in "
                "the same way an accounting ledger works.",

                "Collection and delivery carry additional proof: OTP "
                "verification, a signature, and a photograph of the sealed "
                "package. Above a declared-value threshold there is more still "
                "— dual signature, an insurance flag, and possibly an escort "
                "or a restricted carrier.",

                "The behavioural effect matters as much as the evidential one. "
                "People are careful when the record names them. A large part "
                "of the target loss and damage rate of under one tenth of one "
                "per cent is expected to come not from better packaging but "
                "from the simple fact that every handover has a name against "
                "it.",
            ],
            "features": [
                ["Custody handover",
                 "Requires a scan and an identity capture from both parties at "
                 "every handover, with location and time.",
                 "'I gave it to someone' stops being a thing anybody can say."],
                ["Proof of collection",
                 "Captures the customer's signature, a photograph of the "
                 "sealed package and OTP verification when the item is taken.",
                 "What was collected, in what condition, is settled at the "
                 "door."],
                ["Proof of delivery",
                 "Captures recipient identity, signature, photograph and OTP "
                 "at delivery.",
                 "A consignment cannot be closed without it, which is why "
                 "capture is targeted at 100 per cent."],
                ["Custody ledger",
                 "Keeps an unchangeable, searchable record per item of who "
                 "held it, when and where.",
                 "A claim is answered by reading rather than by arguing."],
                ["Tamper and discrepancy detection",
                 "Records seal breaks, weight differences and condition "
                 "changes, raises an incident and stops the consignment "
                 "moving.",
                 "A tampered package does not quietly continue to its "
                 "destination."],
                ["High-value handling",
                 "Applies extra controls above a declared-value threshold: "
                 "dual signature, insurance flag, escort or restricted "
                 "carrier.",
                 "A BDT 400,000 server does not travel like a keyboard."],
                ["Recipient authorisation",
                 "Lets a customer nominate somebody else to receive the item, "
                 "verified at delivery.",
                 "A device is released to the person the customer named, not "
                 "to whoever is home."],
                ["Restricted items",
                 "Flags lithium batteries, refrigerant and similar, and allows "
                 "only certified carriers to take them.",
                 "A battery consignment cannot be given to an uncertified "
                 "rider by accident."],
            ],
            "example": (
                "the laptop that was not lost",
                "A corporate customer reports that a laptop collected three "
                "weeks earlier has never been returned and claims BDT 118,000. "
                "Under the old way of working this would be a negotiation. "
                "Instead the coordinator opens the custody ledger for that "
                "serial. It shows: collected from the customer's office at "
                "10:14 on the 3rd with OTP verified and a photograph of the "
                "sealed package; handed to the Mirpur branch at 12:40, "
                "scanned by both rider and agent; despatched to the central "
                "workshop at 08:15 on the 4th; booked in by the workshop at "
                "09:50 with seal 4471 intact. And then nothing. The last named "
                "custodian is the workshop, and the device is found within the "
                "hour on a bench where it had been shelved after repair "
                "without being booked out. Elapsed time from claim to "
                "resolution: about ninety minutes, with no dispute and no "
                "settlement."),
            "mistakes": [
                "Accepting a device without scanning because the rider is in a "
                "hurry. That handover is now a gap, and the gap is yours.",
                "Scanning the consignment rather than the items when the "
                "manifest has several. Custody attaches per item for a reason.",
                "Passing a package with a broken seal onward and mentioning it "
                "later. The break has to stop the movement at the point it is "
                "noticed.",
                "Recording a discrepancy as a note rather than raising it. A "
                "note is not an incident and does not block anything.",
                "Signing for something on somebody else's behalf. Recipient "
                "authorisation exists precisely so that this never has to "
                "happen informally.",
            ],
            "caution":
                "The custody ledger is append-only. If something was recorded "
                "wrongly, the fix is a compensating entry with a stated "
                "reason, not a correction. Anybody who asks you to 'just "
                "change it' has misunderstood what the ledger is for.",
        },
        {
            "title": "Riders and scheduling",
            "who": [
                ("Mostly used by", "Logistics coordinators and riders"),
                ("Also relied on by", "Customers choosing a window"),
                ("Where it happens", "The dashboard, the hub and the road"),
            ],
            "intro": [
                "Ten functions covering the operational half of the module: "
                "offering windows a customer can plan around, building "
                "manifests, running hubs, planning loads and giving the rider "
                "an application that works without a signal.",

                "The design mirrors M02's field application deliberately. A "
                "rider has the same problem as a technician — they are outside, "
                "often without coverage, holding a phone and somebody else's "
                "property — so the same answers apply: work offline, queue "
                "everything, synchronise later, and never make the evidence "
                "optional.",
            ],
            "features": [
                ["Pickup and delivery scheduling",
                 "Offers time windows by area, honouring rider capacity and "
                 "cut-off times.",
                 "A customer is offered a window the operation can actually "
                 "keep."],
                ["Rider assignment",
                 "Chooses an internal rider or an external courier by area, "
                 "declared value, item size and cost.",
                 "A high-value item does not go on the cheapest option by "
                 "accident."],
                ["Route manifest",
                 "Builds the rider's daily list with an optimised sequence.",
                 "Fewer kilometres and more stops in the same day."],
                ["Rescheduling",
                 "Moves a collection or delivery at the customer's or the "
                 "operation's request, with notification and an SLA "
                 "adjustment.",
                 "A changed appointment does not silently become a breach."],
                ["Central or branch logistics",
                 "Supports a central team and branch-assigned riders, "
                 "configurable per area.",
                 "Dhaka can run centrally while a small district runs from its "
                 "branch."],
                ["Rider mobile application",
                 "Gives the rider the whole workflow offline, queueing "
                 "everything.",
                 "A collection in a coverage gap is still fully evidenced."],
                ["Hub operations",
                 "Manages sorting, staging and dispatch at logistics hubs.",
                 "A hub stops being a room where things accumulate."],
                ["Load planning",
                 "Plans loads by weight, volume and declared-value limits.",
                 "A rider is not sent out carrying more value than policy "
                 "allows."],
                ["Delivery windows",
                 "Offers and honours committed windows, and measures how often "
                 "they are kept.",
                 "On-time performance becomes a number instead of an "
                 "impression."],
                ["Address validation",
                 "Validates and geocodes addresses, learning from deliveries "
                 "that succeeded before.",
                 "The second delivery to the same flat finds it first time."],
            ],
            "example": (
                "a rider's Tuesday",
                "A rider's manifest loads at 08:30 with fourteen stops: six "
                "collections, seven deliveries and one inter-branch handover, "
                "sequenced to keep travel down while respecting three "
                "committed morning windows. Stop four is a high-value "
                "collection — a BDT 210,000 workstation — so the app requires "
                "a dual signature and shows the item as a value band rather "
                "than a figure. Stop nine, a delivery in Bashundhara, fails: "
                "nobody answers. He photographs the entrance with location "
                "enabled, records the failed attempt, and the customer is "
                "notified within the minute with a link to reschedule. The "
                "re-attempt policy schedules a second attempt for the "
                "following morning without the coordinator touching it. At "
                "17:40 he reconciles BDT 4,200 of cash on delivery against "
                "three jobs, and the shift closes."),
            "mistakes": [
                "Departing from the manifest sequence to do an easy stop "
                "first. The windows were committed to customers.",
                "Waiting for a signal before recording a handover. Everything "
                "queues; recording it later from memory is how evidence gets "
                "weaker.",
                "Accepting a load above the declared-value limit because it "
                "seems easier than a second run. The limit is a safety "
                "control.",
                "Recording a failed delivery from the road rather than at the "
                "door. The evidence is geotagged.",
            ],
        },
        {
            "title": "Working with couriers",
            "who": [
                ("Mostly used by", "Logistics coordinators and procurement"),
                ("Also relied on by", "Finance reconciling invoices"),
                ("Where it happens", "Mostly through interfaces, not screens"),
            ],
            "intro": [
                "1000FiX cannot carry everything itself, and outside couriers "
                "cover the areas and the volumes its own riders cannot. The "
                "difficulty with a courier is that custody passes to somebody "
                "whose systems the company does not control.",

                "The answer is to map their events into our chain. A partner's "
                "tracking updates arrive by webhook or polling, are translated "
                "into internal states, and are written into the same custody "
                "ledger. The chain has a different kind of link in it for that "
                "leg, but it is not broken.",
            ],
            "features": [
                ["Partner onboarding",
                 "Registers a courier with their service areas, rate card, "
                 "service levels, restricted-item certification and API "
                 "credentials.",
                 "A new partner is set up once and everything afterwards "
                 "follows the rules."],
                ["Booking",
                 "Books a consignment with a partner and takes back their "
                 "tracking reference.",
                 "No telephoning a courier and writing a number on a pad."],
                ["Status ingestion",
                 "Takes the partner's tracking events, maps them to our states "
                 "and writes custody events.",
                 "The customer sees one tracking story, not two."],
                ["Partner reconciliation",
                 "Reconciles their invoices against consignments actually "
                 "delivered and the contracted rate card.",
                 "Overbilling becomes visible instead of being paid."],
                ["Cross-border shipping",
                 "Handles international movements with customs documentation "
                 "and distance-based charging.",
                 "A part returning to a manufacturer abroad is a process, not "
                 "a project."],
                ["Carrier performance",
                 "Scores internal riders and external couriers on cost, "
                 "punctuality, damage rate and evidence completeness.",
                 "The cheapest courier stops looking cheap once damage is "
                 "counted."],
            ],
            "example": (
                "the invoice that was wrong",
                "A courier partner's monthly invoice arrives for BDT 186,400 "
                "covering 412 consignments. Reconciliation against the ledger "
                "finds 397 consignments actually delivered, eleven returned to "
                "origin after failed delivery — which the rate card charges at "
                "a lower rate — and four that appear on the invoice but have "
                "no record at all. The variance is BDT 21,900, about twelve "
                "per cent. It is flagged automatically and settled with the "
                "partner in a single conversation, with the consignment "
                "numbers attached. Under the old way of working the invoice "
                "would have been approved because there was no practical way "
                "to check it."),
            "mistakes": [
                "Booking a courier outside the system because it is faster. "
                "That consignment now has a gap in its chain and cannot be "
                "reconciled against the invoice.",
                "Ignoring unmappable partner status events. They are logged "
                "and alerted for a reason — an event nobody understands is a "
                "custody link nobody has.",
                "Assigning a restricted item to a courier whose certification "
                "has lapsed. The system checks and refuses, and working around "
                "it is a safety matter.",
                "Choosing a carrier on price alone. The performance scorecard "
                "exists because damage rate and evidence completeness are part "
                "of the price.",
            ],
        },
        {
            "title": "Charging, returns and things going wrong",
            "who": [
                ("Mostly used by", "Coordinators, finance and the quality "
                                   "manager"),
                ("Also relied on by", "Customers, who see the charge and the "
                                      "waiver"),
                ("Where it happens", "At booking, at delivery, and afterwards"),
            ],
            "intro": [
                "Eleven functions covering the commercial and the unhappy "
                "parts of logistics: what a movement costs, who pays for it, "
                "what happens when delivery fails, what comes back to whom, "
                "and how a loss is settled.",

                "The charging half closes a quiet revenue leak. Today a "
                "logistics charge is reconstructed at invoicing, if it is "
                "captured at all. Here it is calculated at the moment the "
                "movement is created, from zone, distance, weight, declared "
                "value and service level — and waived automatically where a "
                "contract, a warranty term or a Privilege tier entitles the "
                "customer to free collection.",

                "The unhappy half is where the custody ledger earns its keep. "
                "A loss or damage claim is managed through to settlement using "
                "the ledger as the evidence, which changes the conversation "
                "from what people remember to what was recorded.",
            ],
            "features": [
                ["Distance and zone charging",
                 "Calculates the customer's charge from zone, distance, "
                 "weight, declared value and service level.",
                 "The customer is told the price before they agree to the "
                 "collection."],
                ["Entitlement waiver",
                 "Waives the charge automatically where a contract, warranty "
                 "term or membership tier entitles the customer.",
                 "A Gold member is not charged for something their membership "
                 "already covers."],
                ["Return to vendor",
                 "Moves defective parts back to vendors with RMA references, "
                 "tracked through to the credit.",
                 "Credits that are currently written off silently get "
                 "recovered."],
                ["Recycling transfer",
                 "Moves end-of-life devices to certified partners, blocked "
                 "until the data destruction certificate exists.",
                 "A customer's data cannot leave the building on a machine "
                 "going to scrap."],
                ["Failed delivery",
                 "Applies the re-attempt policy, then returns to origin with "
                 "the charge rules applied.",
                 "A failed delivery resolves itself rather than sitting in a "
                 "hub."],
                ["Cash on delivery",
                 "Collects and reconciles cash per rider per shift.",
                 "Zero tolerance for unexplained variance, checked daily."],
                ["Insurance and declared value",
                 "Records the declared value and applies insurance where it "
                 "has been taken.",
                 "The insurance position on a lost item is known before it is "
                 "lost."],
                ["Loss and damage claims",
                 "Manages a claim through to settlement using the custody "
                 "ledger as the evidence.",
                 "A dispute becomes a reading exercise."],
                ["Customer rescheduling",
                 "Lets the customer move a collection or delivery from the "
                 "tracking link.",
                 "The customer who will not be in says so before the journey "
                 "is made."],
                ["Cost allocation",
                 "Attaches the cost of a movement to the job, contract or "
                 "business line that caused it.",
                 "The company finds out what pick and drop really costs."],
                ["Logistics analytics",
                 "Reports volume, cost per consignment, punctuality and "
                 "exception causes.",
                 "The fifteen per cent cost reduction is measured rather than "
                 "assumed."],
            ],
            "example": (
                "the recycling batch that did not move",
                "A corporate client decommissions thirty desktop machines and "
                "asks 1000FiX to dispose of them. A recycling consignment is "
                "created for the batch and a certified partner selected. When "
                "the coordinator tries to schedule it, the system blocks the "
                "movement: four of the thirty machines have no data "
                "destruction certificate from M06. Investigation shows those "
                "four were added to the batch after the wiping run and never "
                "went through it. They are removed from the consignment, wiped "
                "and certified, and travel with the following week's batch. "
                "What did not happen: four hard drives holding a client's "
                "commercial data leaving the building on a lorry to a scrap "
                "yard, with a certificate on file saying they had been "
                "cleared."),
            "mistakes": [
                "Reconstructing a logistics charge at invoicing. Calculate it "
                "at the movement or it will be forgotten.",
                "Applying a waiver manually because the customer complained. "
                "Waivers are entitlement-driven and the analysis of them is "
                "how the company sees what it is giving away.",
                "Sending a return to vendor without the RMA reference. The "
                "credit will not be traceable and it will be lost.",
                "Settling a loss claim without opening the ledger. The record "
                "usually names a custodian, and often finds the item.",
                "Depositing cash on delivery without reconciling it against "
                "the consignments. The variance tolerance is effectively "
                "zero.",
            ],
            "caution":
                "Nothing moves to a recycling partner without a valid data "
                "destruction certificate. That block cannot be overridden by a "
                "logistics role, and it should not be worked around by moving "
                "the item somewhere else first.",
        },
    ],

    # ============================================ 7. the journey
    "s6_title": "The journey of a consignment",
    "s6_lede":
        "Eleven states from 'this needs to move' to 'the record is closed', "
        "and the two handovers that need proof rather than permission.",

    "s6_intro": [
        "A consignment's life is short compared with a service order's — often "
        "a day, sometimes an hour — but it accumulates more evidence per hour "
        "than anything else in the system. Every transition below writes "
        "something to the ledger.",

        "Two states are worth noticing because they are not part of the normal "
        "path. 'Exception' is where a consignment goes when something has "
        "happened that needs a person. 'Blocked' is where it goes when a seal "
        "has been broken or a weight does not match, and it does not move "
        "again until somebody has looked at it.",
    ],

    "journey": [
        ("Requested", "Any module, or a person", None),
        ("Scheduled", "Coordinator or system", "gate"),
        ("Out for collection", "Coordinator", None),
        ("Collected", "Rider + customer", "proof"),
        ("In transit", "System", None),
        ("At hub", "Hub operative", None),
        ("Out for delivery", "Coordinator", None),
        ("Delivered", "Rider + recipient", "proof"),
        ("Closed", "System", None),
        ("Exception", "Rider", "evidence"),
        ("Blocked", "System", "stops"),
    ],
    "journey_title": "The path a consignment follows",
    "journey_sub": ("Nine states in the normal path, and two the module hopes "
                    "not to use"),
    "journey_caption": "The consignment lifecycle, in the order it happens",

    "s6_stages": [
        ["Requested", "Something needs to move; nothing is arranged yet.",
         "Any module, or a coordinator",
         "Nothing. A request can be abandoned freely."],
        ["Scheduled", "A window is agreed and capacity is reserved.",
         "Coordinator or system",
         "The charge calculated, the window agreed, capacity confirmed."],
        ["Out for collection", "A rider or courier is on the way to fetch it.",
         "Coordinator",
         "A carrier assigned and the manifest published."],
        ["Collected", "It is in our custody.", "Rider and customer",
         "A scan, both parties identified, OTP, signature and photograph. All "
         "of them."],
        ["In transit", "It is moving between two points.", "System",
         "A custody event written."],
        ["At hub", "It is being sorted or staged.", "Hub operative",
         "Scanned on arrival and custody transferred."],
        ["Out for delivery", "The last leg has started.", "Coordinator",
         "The next leg assigned."],
        ["Delivered", "The recipient has it.", "Rider and recipient",
         "A scan, recipient identity, OTP, signature and photograph."],
        ["Closed", "Everything is settled.", "System",
         "Proof of delivery complete, and cash on delivery reconciled if "
         "there was any."],
        ["Exception", "Something has gone wrong that needs a person.",
         "Rider",
         "A reason recorded with geotagged evidence."],
        ["Blocked", "A seal is broken or a weight does not match.", "System",
         "Nothing — it stops automatically and stays stopped until reviewed."],
    ],

    "s6_gates_intro":
        "Two of the transitions demand evidence rather than authority, and no "
        "role can grant them. A third stops a consignment outright. Together "
        "they are why the custody chain holds.",

    "gates": [
        ("Declared value recorded",
         "Every item must carry a declared value before collection. A zero "
         "value is not permitted", "Coordinator"),
        ("Collection proven",
         "A scan, both parties identified, an OTP, a signature and a "
         "photograph of the sealed package", "Rider and customer"),
        ("Certified carrier for restricted items",
         "Lithium batteries and similar may only be assigned to a carrier "
         "certified for them", "System"),
        ("Data destruction certificate for recycling",
         "Nothing moves to a recycling partner without a valid certificate "
         "from M06", "System"),
        ("Delivery proven",
         "Recipient identity, OTP, signature and photograph. A consignment "
         "cannot close without it", "Rider and recipient"),
        ("Cash reconciled",
         "Cash on delivery reconciled per rider per shift before the next "
         "shift starts", "Rider"),
        ("Seal intact",
         "A break or a weight discrepancy raises an incident and stops the "
         "consignment moving until it is reviewed", "System"),
    ],

    "s6_wrong_intro":
        "Consignments fail in a small number of ways and almost all of them "
        "show on the dashboard before a customer notices. This is what the "
        "exception column will actually contain.",

    "s6_wrong": [
        ["Requested",
         "It sits unscheduled because no window was acceptable to the "
         "customer.",
         "It stays in the pending column with no date.",
         "Offer a different area or day. Persistent gaps mean rider capacity "
         "is wrong for that zone."],
        ["Out for collection",
         "The customer is not there.",
         "An exception with geotagged evidence.",
         "The re-attempt policy handles it. Do not simply cancel."],
        ["Collected",
         "The rider records the handover without full evidence.",
         "The app will have refused, so in practice this means a collection "
         "that never got recorded.",
         "Investigate immediately. An unrecorded collection is a device "
         "nobody is accountable for."],
        ["In transit",
         "A seal is found broken at the next handover.",
         "The consignment goes to blocked and stops.",
         "Do not move it on. The incident is raised automatically; the "
         "logistics manager reviews."],
        ["At hub",
         "It is staged and forgotten.",
         "Overdue against its window, and an alert to the coordinator.",
         "Hub staging without a next leg assigned is the commonest cause. "
         "Assign the leg."],
        ["Out for delivery",
         "Repeated failed attempts.",
         "Exception, twice.",
         "After the policy limit it returns to origin automatically with the "
         "charge rules applied. Let it."],
        ["Delivered but not closed",
         "Cash on delivery has not been reconciled.",
         "The rider's next shift is blocked.",
         "Reconcile. This is not waivable at branch level."],
        ["Anywhere",
         "A weight discrepancy at book-in.",
         "Blocked, with an incident.",
         "Compare against the manifest. Most are a missing accessory, and the "
         "previous custodian is named."],
    ],

    "s6_note":
        "A consignment that reaches 'blocked' does not resume by itself. That "
        "is deliberate: the whole value of tamper detection is that somebody "
        "has to look before the item travels further.",

    # ============================================ 8. day in the life
    "s7_lede":
        "Five journeys, from a routine collection to a claim settled by "
        "reading the ledger.",

    "s7_intro": [
        "Each of these follows one consignment across everybody who touches "
        "it. Read the first if you are new to the module; read the fourth if "
        "you have ever had to settle a dispute about a missing device.",

        "Customers, places, values and reference numbers are illustrative. The "
        "thresholds, rules and states behind them are exactly as the "
        "specification states them.",
    ],

    "scenarios": [
        {
            "title": "A routine pick and drop",
            "narrative": [
                "The commonest movement in the company, and the one the growth "
                "of the service depends on. A laptop collected from a home, "
                "repaired, and returned three days later.",
            ],
            "lanes": [
                ("Customer", [(0, "Requests collection at intake"),
                              (1, "Signs and enters the OTP"),
                              (5, "Signs for the return")]),
                ("System", [(0, "Creates the consignment; prices the zone"),
                            (2, "Writes the custody event"),
                            (5, "Closes; allocates the cost")]),
                ("Rider", [(1, "Collects, seals, photographs"),
                           (5, "Delivers back")]),
                ("Branch", [(2, "Scans in from the rider")]),
                ("Workshop", [(3, "Books in against the consignment"),
                              (4, "Books out on completion")]),
            ],
            "columns": ["Requested", "Collected", "At branch", "In workshop",
                        "Returned", "Closed"],
            "exhibit_title": "A pick and drop, four legs and six handovers",
            "exhibit_sub": "Every handover writes a link in the chain",
            "caption": "The commonest journey, end to end",
            "table": [
                ["1", "Intake and system",
                 "A pick-and-drop request creates the consignment. The zone "
                 "charge is calculated at BDT 350; the customer's tier gives "
                 "no waiver, so it stands and is shown before booking. Windows "
                 "are offered and one is chosen."],
                ["2", "Rider and customer",
                 "The rider collects: scan, both identities, OTP, the "
                 "customer's signature, a photograph of the sealed package, "
                 "seal tag recorded. Declared value BDT 95,000."],
                ["3", "Rider and branch",
                 "Handed to the Mirpur branch. Both parties scan; a custody "
                 "event is written; the customer is notified that the device "
                 "has reached the branch."],
                ["4", "Branch and workshop",
                 "Despatched on the scheduled shuttle to the central workshop, "
                 "which books it in against the consignment with the seal "
                 "intact."],
                ["5", "Workshop, branch and rider",
                 "Repair completed. The workshop books out, the branch books "
                 "in, and the return leg is scheduled with the customer "
                 "choosing a window from the tracking link."],
                ["6", "Rider and customer",
                 "Delivered: recipient identity, OTP, signature and "
                 "photograph. The consignment closes and its cost is allocated "
                 "to the service order that caused it."],
            ],
            "outcome":
                "Six handovers, six custody events, and a customer who could "
                "see where their laptop was at every stage. The company also "
                "now knows what that collection and return actually cost, "
                "which it has never known before.",
        },
        {
            "title": "A rider's shift, including one that failed",
            "narrative": [
                "Fourteen stops, one high-value collection, one failed "
                "delivery, and a reconciliation that took five minutes.",
            ],
            "lanes": [
                ("System", [(0, "Publishes a sequenced manifest"),
                            (2, "Notifies the customer; schedules a "
                                "re-attempt"),
                            (3, "Reconciles cash against consignments")]),
                ("Rider", [(0, "Loads within the value limit"),
                           (1, "Collects a BDT 210,000 workstation"),
                           (2, "Records a failed delivery with evidence"),
                           (3, "Reconciles BDT 4,200 at shift end")]),
                ("Coordinator", [(1, "Sees the dual-signature requirement met")]),
                ("Customer", [(2, "Reschedules from the link")]),
            ],
            "columns": ["Manifest", "High value", "Failed stop", "Shift close"],
            "exhibit_title": "One rider, fourteen stops, two exceptions",
            "exhibit_sub": "What an ordinary shift actually contains",
            "caption": "A day on the road, including the parts that go wrong",
            "table": [
                ["1", "System and rider",
                 "The manifest publishes at 08:30 with fourteen stops in "
                 "optimised sequence, respecting three committed morning "
                 "windows. Load planning has kept the total declared value "
                 "inside policy."],
                ["2", "Rider",
                 "Stop four is a BDT 210,000 workstation. High-value handling "
                 "requires a dual signature and an insurance flag; the app "
                 "shows the rider a value band rather than the figure."],
                ["3", "Rider and system",
                 "Stop nine fails — nobody answers. The rider photographs the "
                 "entrance with location enabled and records the attempt. The "
                 "customer is notified within a minute with a reschedule "
                 "link."],
                ["4", "Customer",
                 "Reschedules for the following morning from the link. The "
                 "re-attempt appears on tomorrow's manifest without the "
                 "coordinator touching anything."],
                ["5", "Rider and system",
                 "At 17:40 the app prompts for cash reconciliation: BDT 4,200 "
                 "collected across three deliveries, matched against the "
                 "consignments and the deposit. Five minutes."],
            ],
            "outcome":
                "One failed delivery cost a photograph and a minute, rather "
                "than a telephone call, an argument and an unrecorded second "
                "journey. Cash on delivery closed at zero variance for that "
                "rider on that day, which is a number the company has never "
                "previously been able to produce.",
        },
        {
            "title": "A courier leg that stayed inside the chain",
            "narrative": [
                "A consignment to a district with no 1000FiX rider goes out "
                "with a courier partner. Custody passes to a company whose "
                "systems we do not control, and the chain does not break.",
            ],
            "lanes": [
                ("Coordinator", [(0, "Assigns the courier by area and value")]),
                ("System", [(0, "Books with the partner; takes their "
                                "reference"),
                            (2, "Maps their events to custody events"),
                            (3, "Reconciles the invoice at month end")]),
                ("Courier", [(1, "Collects and carries"),
                             (2, "Posts tracking events by webhook")]),
                ("Customer", [(2, "Sees one tracking story, not two")]),
            ],
            "columns": ["Assigned", "Carried", "Tracked", "Reconciled"],
            "exhibit_title": "A courier leg inside our own custody chain",
            "exhibit_sub": "Their events, our ledger",
            "caption": "How outside carriers are kept accountable",
            "table": [
                ["1", "Coordinator and system",
                 "No 1000FiX rider serves the district. A courier partner is "
                 "chosen on area, declared value and cost. The consignment is "
                 "booked through their interface and their tracking reference "
                 "is stored against ours."],
                ["2", "Courier",
                 "Collects from the branch. The handover is scanned by both "
                 "the branch and the courier's agent, so custody transfer is "
                 "recorded on our side too."],
                ["3", "System",
                 "The partner posts tracking events by webhook. Each is mapped "
                 "to an internal state and written as a custody event. The "
                 "customer's tracking link shows one continuous story."],
                ["4", "Courier and system",
                 "Delivery is completed with the partner's own proof, ingested "
                 "and attached. The consignment closes."],
                ["5", "Finance",
                 "At month end the partner's invoice is reconciled against "
                 "consignments actually delivered and the contracted rate "
                 "card. Variances are flagged with consignment numbers "
                 "attached."],
            ],
            "outcome":
                "Custody passed to a third party without a gap appearing in "
                "the ledger, and the invoice for the month could be checked "
                "line by line rather than approved on trust.",
        },
        {
            "title": "A claim settled by reading",
            "narrative": [
                "The walkthrough that justifies the whole module. A corporate "
                "customer claims a device was never returned, and the answer "
                "takes ninety minutes instead of six weeks.",
            ],
            "lanes": [
                ("Customer", [(0, "Claims BDT 118,000 for a lost laptop")]),
                ("Coordinator", [(1, "Opens the custody ledger for the "
                                     "serial"),
                                 (2, "Identifies the last named custodian")]),
                ("Workshop", [(2, "Finds the device on a bench, unbooked")]),
                ("System", [(3, "Records the correction as a compensating "
                                "entry")]),
            ],
            "columns": ["Claimed", "Ledger read", "Located", "Corrected"],
            "exhibit_title": "A loss claim answered from the record",
            "exhibit_sub": "The ledger names the last custodian",
            "caption": "How a dispute becomes a reading exercise",
            "table": [
                ["1", "Customer",
                 "Claims that a laptop collected three weeks earlier was never "
                 "returned, and asks for BDT 118,000."],
                ["2", "Coordinator",
                 "Opens the custody ledger for that serial. Collected at 10:14 "
                 "on the 3rd, OTP verified, sealed package photographed. "
                 "Handed to the Mirpur branch at 12:40, both parties scanned. "
                 "Despatched to the central workshop 08:15 on the 4th. Booked "
                 "in at 09:50 with seal 4471 intact."],
                ["3", "Coordinator",
                 "And then nothing. The last named custodian is the workshop, "
                 "which never booked it out."],
                ["4", "Workshop",
                 "The device is found within the hour on a bench, repaired but "
                 "shelved without being booked out of the workshop's custody."],
                ["5", "System",
                 "The gap is corrected with a compensating entry stating what "
                 "happened. The ledger is never edited; the correction is "
                 "itself part of the record."],
            ],
            "outcome":
                "Ninety minutes from claim to resolution, with no settlement "
                "paid and no relationship damaged. The specification puts each "
                "avoided high-value dispute at BDT 40,000 to 150,000, and that "
                "understates it — the customer in this case renewed their "
                "corporate contract.",
        },
        {
            "title": "A recycling batch that was stopped",
            "narrative": [
                "Thirty decommissioned desktops, four of which should not have "
                "been on the lorry.",
            ],
            "lanes": [
                ("Client", [(0, "Decommissions thirty machines")]),
                ("Coordinator", [(1, "Creates the recycling consignment"),
                                 (3, "Removes four; sends twenty-six")]),
                ("System", [(2, "Blocks: four have no destruction "
                                "certificate")]),
                ("Data services", [(3, "Wipes and certifies the four")]),
            ],
            "columns": ["Decommissioned", "Consignment", "Blocked", "Resolved"],
            "exhibit_title": "The movement the system refused to make",
            "exhibit_sub": "No destruction certificate, no transfer",
            "caption": "A hard block that prevented a data breach",
            "table": [
                ["1", "Client and coordinator",
                 "A corporate client decommissions thirty desktops for "
                 "disposal. A recycling consignment is created for the batch "
                 "and a certified partner selected."],
                ["2", "System",
                 "Scheduling is refused. Four of the thirty machines have no "
                 "valid data destruction certificate from M06."],
                ["3", "Coordinator",
                 "Investigation shows those four were added to the batch after "
                 "the wiping run and never went through it."],
                ["4", "Data services and coordinator",
                 "The four are removed from the consignment, wiped, certified, "
                 "and travel with the following week's batch. Twenty-six move "
                 "as planned."],
                ["5", "Quality",
                 "The near-miss is recorded. The batch-assembly process is "
                 "changed so that machines cannot be added after the wiping "
                 "run."],
            ],
            "outcome":
                "Four hard drives holding a client's commercial data did not "
                "leave the building on a lorry to a scrap yard with a "
                "certificate on file saying they had been cleared. This is the "
                "kind of event that never appears in a benefits case and would "
                "have ended a corporate relationship.",
        },
    ],

    "s9t_lede":
        "Five journeys, and the same four disciplines underneath all of them.",

    "s9t_intro": [
        "The walkthroughs covered a routine collection, an ordinary shift, an "
        "outside carrier, a claim and a near-miss. What they have in common is "
        "not a feature; it is a habit about evidence.",

        "In every case the useful information was captured at the moment of a "
        "handover, by the person doing it, in a few seconds. Nothing was "
        "reconstructed afterwards, and that is why the record held up when "
        "somebody needed it to.",
    ],

    "s9t_table": [
        ["Evidence at the handover, not afterwards",
         "Every walkthrough: scan, identity, OTP, signature, photograph, all "
         "at the moment the item changed hands.",
         "A custody record assembled later is a story. One captured at the "
         "time is evidence."],
        ["The chain survives leaving the company",
         "The courier walkthrough: their tracking events mapped into our "
         "ledger.",
         "Custody passing to a third party is the point at which most systems "
         "give up. This one does not."],
        ["Blocks are worth more than warnings",
         "The recycling batch, and every seal-break rule.",
         "A warning that a certificate is missing would have been dismissed. A "
         "block prevented a data breach."],
        ["The ledger names somebody",
         "The claim walkthrough: the last custodian was identifiable within "
         "minutes.",
         "People are careful when the record names them, which is most of the "
         "loss-rate improvement."],
        ["Close the day, every day",
         "The rider shift: cash reconciled before the next shift could start.",
         "Small daily reconciliations replace large monthly arguments."],
    ],

    "s9t_close":
        "Everything M03 offers rests on a few seconds of discipline at each "
        "handover, repeated thousands of times. The scan is the module. "
        "Everything else — the scheduling, the pricing, the courier "
        "integration — is arrangement around that one moment.",

    # ============================================ 10. rules
    "s8_lede":
        "Twelve rules, ten of them hard blocks. Logistics is the part of the "
        "system with the least discretion in it, and deliberately so.",

    "s8_intro": [
        "Custody rules cannot be soft. A chain with one optional link is not a "
        "chain, and a company holding a customer's business laptop cannot "
        "afford a record that is usually complete.",

        "That is why almost everything below is a hard block rather than a "
        "warning. The system does not ask whether you would like to record the "
        "handover; it declines to advance the consignment until you have.",
    ],

    "s8_rules": [
        ["Transfer custody without a scan and both parties identified",
         "A handover nobody recorded is a gap, and gaps are where devices "
         "disappear.",
         "Scan. It takes a few seconds and it protects whoever is handing over "
         "as much as whoever is receiving."],
        ["Close a consignment without proof of delivery",
         "Without proof, the company cannot say the customer received "
         "anything.",
         "Capture recipient identity, OTP, signature and photograph. Capture "
         "is targeted at 100 per cent, not 'usually'."],
        ["Move a high-value consignment without dual signature and insurance "
         "flagging",
         "The exposure on a single high-value item can exceed a month of "
         "logistics margin.",
         "Follow the high-value flow. It adds about a minute."],
        ["Continue after a seal break or weight discrepancy",
         "The whole point of a seal is that a break stops the journey.",
         "Nothing — the consignment blocks automatically and the incident "
         "raises itself. Do not move it on."],
        ["Give a restricted item to an uncertified carrier",
         "Lithium batteries and refrigerant are dangerous goods with legal "
         "handling requirements.",
         "Reassign to a certified carrier. The system checks at assignment."],
        ["Leave cash on delivery unreconciled at shift end",
         "Cash reconciled monthly is cash nobody can trace.",
         "Reconcile per shift. The tolerance for unexplained variance is "
         "effectively zero."],
        ["Charge a customer whose entitlement covers the movement",
         "It damages the value of the contract or membership they bought.",
         "Nothing — the waiver applies automatically from contract, warranty "
         "or tier."],
        ["Keep re-attempting a failed delivery indefinitely",
         "Each attempt costs a journey, and at some point the item has to go "
         "back.",
         "Nothing — the policy applies the re-attempts, then returns to origin "
         "with the charge rules."],
        ["Move an item to recycling without a data destruction certificate",
         "It would put a customer's data in a scrap yard.",
         "Get the certificate from M06 first. There is no override and there "
         "should not be one."],
        ["Assign restricted goods to a courier whose certification has lapsed",
         "The certification is what makes their carriage lawful.",
         "Nothing — they leave the eligible pool automatically. Renewal is a "
         "procurement matter."],
        ["Edit the custody ledger",
         "A record that can be changed is not evidence.",
         "Post a compensating entry with a stated reason. The correction "
         "becomes part of the record, which is the point."],
        ["Collect an item with no declared value",
         "The value drives the handling controls, the insurance and any later "
         "claim.",
         "Record a real value. Zero is not permitted and a nominal figure is "
         "worse than useless."],
    ],

    "s8_note":
        "If a rule here is genuinely obstructing legitimate work, raise it — "
        "see Appendix B. What must not happen is a workaround: an unscanned "
        "handover, a movement booked outside the system, or an item carried "
        "'just this once' by somebody uncertified. Each of those puts a hole "
        "in the only thing this module produces.",

    # ============================================ 11. automation
    "s9_lede":
        "Twelve behaviours that run without anybody asking. Three of them are "
        "blocks rather than actions.",

    "s9_intro": [
        "Most of these smooth the operation: a consignment created at intake, "
        "a rider chosen by area and value, a customer notified when their "
        "device reaches the branch. They are what let a coordinator handle "
        "many times the volume they can manage by telephone.",

        "Three are different in kind. When a seal break is detected, when a "
        "recycling movement lacks a destruction certificate, and when a "
        "restricted item meets an uncertified carrier, the automation's job is "
        "to stop something rather than to do something. Those three are the "
        "reason the exception column stays short.",
    ],

    "automation_groups": [
        ("When a movement is created or scheduled", 3,
         "Consignment created, charge calculated, carrier assigned, windows "
         "offered"),
        ("At a handover", 2,
         "Custody event written, parent order advanced, customer notified"),
        ("When something is wrong", 5,
         "Seal breaks, failed deliveries, overdue consignments, missing "
         "certificates, uncertified carriers"),
        ("At the end of a period", 2,
         "Rider cash reconciliation, and courier invoice reconciliation"),
    ],

    "s9_table": [
        ["Creates the consignment, calculates the charge, checks entitlement "
         "and offers windows",
         "Pick and drop is requested at intake",
         "The customer, before they leave the counter"],
        ["Assigns a rider or courier by area, value and cost, publishes the "
         "manifest and notifies the customer",
         "A consignment is scheduled",
         "The rider or courier, and the customer"],
        ["Writes the custody event, notifies the customer and advances the "
         "parent service order",
         "A collection is completed",
         "The customer and M01"],
        ["Raises an incident, blocks onward movement and notifies the "
         "logistics manager and the originating module",
         "A seal break or weight discrepancy is detected",
         "Logistics management and quality"],
        ["Records the exception with evidence, notifies the customer and "
         "schedules a re-attempt",
         "A delivery attempt fails",
         "The customer, immediately"],
        ["Returns the item to origin and applies the charge rules",
         "The re-attempt policy is exhausted",
         "The customer and the originating module"],
        ["Maps the event to an internal state, writes the custody event and "
         "updates tracking",
         "A courier partner posts a tracking update",
         "The customer, through their tracking link"],
        ["Reconciles cash on delivery and blocks the next shift until it is "
         "done",
         "A rider's shift ends",
         "The rider, then finance if it is not completed"],
        ["Verifies the data destruction certificate and blocks if it is absent",
         "A consignment is created for recycling",
         "The coordinator and the quality manager"],
        ["Verifies carrier certification and reassigns if it is missing",
         "A restricted item appears on a manifest",
         "The coordinator"],
        ["Alerts the coordinator and notifies the customer proactively",
         "A consignment is overdue against its window",
         "The customer, before they chase"],
        ["Reconciles the invoice against delivered consignments and the rate "
         "card, flagging variance",
         "A courier invoice is received",
         "Finance and the logistics manager"],
    ],

    # ============================================ 12. permissions
    "s10_lede":
        "Twelve roles, and one restriction that exists for the rider's "
        "physical safety rather than for confidentiality.",

    "s10_intro": [
        "Access here follows custody: you can see the consignments you are "
        "involved in. A branch sees its own, a workshop sees what is coming to "
        "and from it, a courier partner sees only what they have been given "
        "and only the minimum data needed to carry it.",

        "The restriction worth explaining is declared value. Riders see a "
        "value band rather than the exact figure. That is not about "
        "confidentiality; it is about not sending somebody onto the road "
        "knowing precisely how much the bag on their back is worth.",
    ],

    "permissions": {
        "roles": [
            "Operations Director", "Logistics Coordinator", "Branch Manager",
            "Service Centre Agent", "Workshop Supervisor", "Rider",
            "Inventory Manager", "Procurement Officer", "Finance Manager",
            "Quality Manager", "Customer", "Courier Partner",
        ],
        "actions": ["Create a consignment", "Schedule and assign",
                    "Record a handover", "See exact declared value",
                    "Release a blocked consignment", "Settle a claim"],
        "marks": [
            ["y", "y", "v", "y", "y", "y"],   # Operations Director
            ["y", "y", "v", "y", "a", "v"],   # Logistics Coordinator
            ["y", "y", "y", "y", "", "v"],    # Branch Manager
            ["y", "", "y", "", "", ""],       # Service Centre Agent
            ["", "", "y", "", "", ""],        # Workshop Supervisor
            ["", "", "y", "", "", ""],        # Rider
            ["y", "", "y", "", "", ""],       # Inventory Manager
            ["y", "", "", "", "", ""],        # Procurement Officer
            ["", "", "", "y", "", "y"],       # Finance Manager
            ["", "", "", "y", "a", "v"],      # Quality Manager
            ["", "", "", "", "", ""],         # Customer
            ["", "", "y", "", "", ""],        # Courier Partner
        ],
        "sub": "The six actions that decide who controls a movement",
    },

    "s10_roles": [
        ["Logistics coordinator", "Running the movement operation",
         "Scheduling, assigning carriers and handling exceptions across their "
         "area"],
        ["Rider", "Collecting, carrying and delivering",
         "Recording handovers on their own manifest"],
        ["Operations Director", "Movement performance across the estate",
         "Releasing a blocked consignment and settling a claim"],
        ["Branch manager", "Consignments attached to their branch",
         "Creating and scheduling movements for their own branch"],
        ["Service centre agent", "Handing devices in and out at the counter",
         "Nothing exclusive — but every handover they record is a link in the "
         "chain"],
        ["Workshop supervisor", "Booking devices in and out of the workshop",
         "Nothing exclusive; the book-in is where discrepancies surface"],
        ["Inventory manager", "Stock movements between locations",
         "Creating stock movement consignments"],
        ["Procurement officer", "Defective parts going back to vendors",
         "Creating return-to-vendor movements and tracking the credit"],
        ["Finance manager", "Charges, cash and courier invoices",
         "Settling loss and damage claims"],
        ["Quality manager", "Custody exceptions and restricted-item "
                            "compliance",
         "Reviewing and releasing blocked consignments"],
        ["Customer", "Knowing where their own device is",
         "Rescheduling their own collection or delivery"],
        ["Courier partner", "Carrying what they have been given",
         "Recording handovers on their own consignments only, with the "
         "minimum data"],
    ],

    "s10_restrictions_intro":
        "Three restrictions are enforced in the software. The first is a "
        "safety control and is the one people ask about most.",

    "s10_restrictions": [
        ["Exact declared value",
         "Coordinators, the Operations Director, branch managers, finance and "
         "quality. Riders see a band only.",
         "A rider should not be carrying precise knowledge of how much the bag "
         "on their back is worth. This is a physical safety control."],
        ["The custody ledger",
         "Readable by anyone with access to the consignment; writable by "
         "nobody.",
         "Evidence that can be edited is not evidence. Corrections are "
         "compensating entries."],
        ["Courier partner data",
         "The minimum needed to carry the consignment — not the customer's "
         "history, not the value, not the reason for the movement.",
         "An outside carrier needs an address and a package, not a "
         "relationship."],
        ["Releasing a blocked consignment",
         "The quality manager and the Operations Director, with the "
         "coordinator able to request it.",
         "The person under time pressure to move the item should not be the "
         "person who decides it is safe to."],
        ["Customer visibility",
         "Their own consignment's custody state and expected timing — not "
         "internal notes, not the rider's other stops, not cost.",
         "The customer is entitled to know where their property is."],
    ],

    "s10_note":
        "Courier partners are given the least data of any role in the system. "
        "If a partner is asking for more than an address and a package "
        "description, the question to answer is why the movement needs it, not "
        "how to grant it.",

    # ============================================ 13. measurement
    "s11_lede":
        "Nine reports and eleven measures, almost all of which start from a "
        "baseline of 'untracked'.",

    "s11_intro": [
        "Logistics is the least-measured part of the current operation. "
        "On-time collection and delivery are unmeasured. Loss and damage is "
        "untracked. Cost per consignment is untracked. Proof of delivery "
        "capture is effectively zero, because there is no mechanism to "
        "capture it.",

        "Two of the targets are worth calling out because they are absolute "
        "rather than aspirational. Chain-of-custody exceptions are targeted at "
        "zero, and proof-of-delivery capture at one hundred per cent. Those "
        "are not stretch goals; they are the definition of the module working. "
        "A ninety-eight per cent custody chain is a broken custody chain.",
    ],

    "s11_reports": [
        ["Logistics live dashboard",
         "What is pending, scheduled, in transit, delivered and in exception, "
         "right now",
         "The logistics coordinator, continuously"],
        ["Rider performance",
         "Stops completed, punctuality, evidence completeness, exceptions and "
         "cash variance",
         "The Logistics Manager, weekly"],
        ["Courier partner scorecard",
         "Punctuality, damage rate, cost per consignment and invoice accuracy",
         "Logistics and procurement, monthly"],
        ["Custody exception report",
         "Seal breaks, discrepancies and any unexplained gap in a chain",
         "Quality and logistics management, daily"],
        ["Loss and damage register",
         "Incidents, value, claim status and root cause",
         "Finance, legal and quality, monthly"],
        ["Cost per consignment",
         "What movement costs, by zone, service level, carrier type and "
         "business line",
         "Finance and logistics, monthly"],
        ["Charge waiver analysis",
         "How much logistics charging is being given away, and to whom",
         "The Chief Commercial Officer and finance, monthly"],
        ["On-time performance",
         "Whether committed collection and delivery windows are being kept",
         "The Operations Director, weekly"],
        ["Restricted-item compliance",
         "Movements of batteries and hazardous items, and carrier "
         "certification status",
         "The Quality Manager, monthly"],
    ],

    "s11_kpis": [
        ["On-time collection",
         "Whether we turn up when we said we would to fetch something",
         "93 per cent. Not currently measured"],
        ["On-time delivery",
         "Whether we turn up when we said we would to return it",
         "93 per cent. Not currently measured"],
        ["Chain-of-custody exceptions",
         "Handovers with a gap or a discrepancy in the chain",
         "Zero. This one is absolute"],
        ["Loss and damage rate",
         "Items lost or damaged as a share of consignments",
         "Under 0.1 per cent, from untracked"],
        ["Proof of delivery completeness",
         "Deliveries with full evidence captured",
         "100 per cent, from effectively nothing"],
        ["Cost per consignment",
         "What a movement actually costs",
         "15 per cent below the baseline, once a baseline exists"],
        ["Courier invoice reconciliation accuracy",
         "How much of a partner invoice can be matched to real deliveries",
         "99 per cent"],
        ["Cash on delivery variance",
         "The gap between collected and deposited",
         "Under 0.1 per cent, from untracked"],
        ["Customer self-service rescheduling",
         "Customers who move their own appointment rather than telephoning",
         "65 per cent, from none"],
        ["Restricted items with a certified carrier",
         "Compliance on dangerous goods",
         "100 per cent. Also absolute"],
        ["Rider app offline reliability",
         "Actions lost after working without a signal",
         "100 per cent reliable — no losses"],
    ],

    "dials": [
        ("Collections and deliveries on time", "93%", 0.93),
        ("Deliveries with complete proof captured", "100%", 1.0),
        ("Loss and damage rate, against a 0.1% ceiling", "<0.1%", 0.99),
        ("Customers rescheduling themselves", "65%", 0.65),
    ],

    "s11_reading_title": "Reading the logistics dashboard",
    "s11_reading": [
        "The dashboard has five columns — pending, scheduled, in transit, "
        "delivered and exception — and the Service App statement of work asked "
        "for exactly that. Four of them are informational. The fifth is the "
        "job.",

        "A useful discipline is to work the exception column to empty twice a "
        "day and otherwise leave the dashboard alone. Consignments in transit "
        "do not benefit from being watched, and the pending column resolves "
        "itself as customers choose windows.",
    ],
    "s11_reading_table": [
        ["Exceptions clustering in one area",
         "Usually address quality rather than customer behaviour.",
         "Check whether address validation has geocoded them. A district with "
         "poor addressing needs the learned-address feature, not more "
         "attempts."],
        ["Consignments overdue at a hub",
         "Staged and never assigned a next leg.",
         "Assign the leg. Recurring hub delays usually mean the shuttle "
         "schedule does not match arrival times."],
        ["A blocked consignment nobody has reviewed",
         "A seal break or discrepancy waiting on quality.",
         "It will not move until reviewed, and that is correct. Chase the "
         "review, not the release."],
        ["Rising failed deliveries in a time band",
         "Windows are being offered when people are not at home.",
         "Look at which windows are being offered, not at rider performance."],
        ["A courier's on-time rate falling",
         "Capacity or route changes at their end.",
         "The scorecard is the conversation. Damage rate matters more than "
         "punctuality when choosing whether to continue."],
        ["Cash variance on one rider, repeatedly",
         "Either a process problem or something worse.",
         "Look at the pattern before the person. Repeated small variances at "
         "the same stop are usually a change-giving problem."],
    ],

    # ============================================ 14. neighbours
    "s12_lede":
        "M03 is the physical layer under four business lines. Twelve modules "
        "supply it and ten depend on it.",

    "s12_intro": [
        "The dependency worth understanding first is not technical. Rental "
        "delivery and collection, trade-in intake, refurbishment movement and "
        "e-waste collection are four business lines that cannot operate at all "
        "without a movement capability. The specification attaches BDT 190 lac "
        "a year across M13, M14 and M18 to work that M03 makes physically "
        "possible.",

        "In the other direction, M03 needs to know what things are, what they "
        "are worth, where people are, and — for recycling — whether the data "
        "on them has been destroyed. It is the last of those that produces the "
        "module's most important dependency.",
    ],

    "s12_upstream": [
        ["M01 Service Request", "The parent context for pick and drop",
         "Collections have no reason and no customer promise"],
        ["M17 Asset Registry", "Which device this is",
         "Custody cannot attach to an identified item"],
        ["M15 Inventory", "What parts exist and what they are",
         "Part movements have no subject"],
        ["M33 Party Master", "Who the customer is and where they are",
         "There is nowhere to collect from or deliver to"],
        ["M13 Rental", "The rental agreement behind a delivery or collection",
         "Rental logistics loses its commercial context"],
        ["M06 Data Services", "The data destruction certificate",
         "Recycling movements are blocked, correctly, and stay blocked"],
        ["M18 Recycling", "Which partners are certified to receive what",
         "Disposal cannot be routed lawfully"],
        ["M42 Vendor Management", "The commercial relationship with couriers",
         "Rate cards and contracts have no source"],
        ["M11 Pricing", "The zone and distance rate card",
         "Logistics charges cannot be calculated"],
        ["M46 Fleet", "Which vehicles exist",
         "Vehicle usage cannot be attributed"],
        ["M29 Identity", "Who each person is at a handover",
         "Identity capture has nothing to check against"],
        ["M08 Contract", "Entitlement to free collection",
         "Waivers cannot be applied automatically"],
    ],

    "s12_downstream": [
        ["M01 Service Request", "Where the device is, at every step",
         "The customer's tracking view goes blank between collection and "
         "return"],
        ["M17 Asset Registry", "The current location and custodian of a device",
         "The asset record stops knowing where the asset is"],
        ["M15 Inventory", "Stock arriving and leaving locations",
         "Inter-location stock accuracy collapses"],
        ["M31 Workshop", "Devices arriving with a manifest to book in against",
         "The workshop receives things with no paperwork again"],
        ["M02 Field Service", "Collections arising from failed on-site repairs",
         "A device that must come back has no way to get there"],
        ["M13 Rental", "Delivery and collection of rental assets",
         "The rental business line cannot operate"],
        ["M14 Trade-in", "Movement of traded-in devices",
         "Trade-in intake cannot operate"],
        ["M18 Recycling", "Movement of end-of-life equipment to partners",
         "E-waste collection cannot operate"],
        ["M20 Receivables", "Logistics charges and cash collected on delivery",
         "Movement revenue leaks and field cash cannot be reconciled"],
        ["M23 Quality", "Custody exceptions, damage and near-misses",
         "Logistics quality becomes invisible"],
    ],

    "s12_close_up": [
        {
            "title": "The dependency that is a control: M03 and M06 Data "
                     "Services",
            "text": [
                "Most dependencies exist so that one module can do its work. "
                "This one exists so that it cannot. M03 will not move an item "
                "to a recycling partner unless M06 has issued a valid data "
                "destruction certificate for it, and no logistics role can "
                "override that.",

                "The separation is deliberate and it is worth understanding "
                "why. The module under pressure to move the batch — a "
                "coordinator with a lorry booked and a client expecting "
                "collection — is not the module that decides whether it is "
                "safe to move. A person who is behind schedule makes different "
                "decisions from a person who is not, and this control removes "
                "that possibility entirely.",

                "The practical effect is occasional friction of exactly the "
                "kind the fifth walkthrough describes: a batch that cannot go "
                "because four machines in it were never wiped. That friction "
                "is the control working. A customer's commercial data leaving "
                "the building on a lorry to a scrap yard is the kind of event "
                "that ends corporate relationships and appears in newspapers.",
            ],
        },
        {
            "title": "The dependency that enables four businesses: M03 and "
                     "Category D",
            "text": [
                "Rental, trade-in, refurbishment and recycling are four "
                "separate business lines with four separate modules, and all "
                "four are physically impossible without movement. A rental "
                "device has to be delivered and collected. A trade-in has to "
                "be brought in and graded. A refurbished machine has to reach "
                "a buyer. End-of-life equipment has to reach a certified "
                "partner.",

                "The specification attaches BDT 190 lac a year to those lines "
                "collectively, and none of it is realised in M03. That is "
                "worth stating plainly, because it changes how the module "
                "should be judged. M03 will never show a large direct return; "
                "it is infrastructure, and its value appears in other people's "
                "numbers.",

                "It also means the sequencing matters. Building the circular "
                "business lines before the logistics capability that carries "
                "them would produce four modules that work on screen and not "
                "in the world.",
            ],
        },
    ],

    "s12_note":
        "M03 is the only module in the system whose subject is the physical "
        "world rather than a record about it. When the ledger and reality "
        "disagree, reality is right and the ledger needs a compensating entry "
        "— never the other way round.",

    # ============================================ 15. troubleshooting
    "s13_lede":
        "What goes wrong with movements, what it usually means, and what to do "
        "about it.",

    "s13_intro": [
        "Almost every problem in this module is one of three things: a "
        "handover that was not scanned, a block doing its job, or a coverage "
        "gap on a rider's phone. The first is the only one that is genuinely a "
        "problem.",
    ],

    "s13_troubleshooting": [
        ["The app will not let me record the collection",
         "One of the required proofs is missing — usually the OTP or the "
         "photograph.",
         "Complete the missing one. The list is short and none of it is "
         "optional."],
        ["The customer will not give me the OTP",
         "Sometimes a wrong mobile number, sometimes suspicion.",
         "Check the number on the consignment. If it is wrong, the coordinator "
         "can re-issue to the correct one; do not proceed without it."],
        ["The consignment is blocked and I need it to move",
         "A seal break or a weight discrepancy has been detected.",
         "It stays blocked until quality reviews it. Chase the review. Moving "
         "the item another way is the one thing not to do."],
        ["Recycling will not schedule",
         "One or more items have no valid data destruction certificate.",
         "The system names them. Remove them from the batch, get them "
         "certified, and send them with the next one."],
        ["The declared value field will not accept what I entered",
         "Zero and blank are both refused.",
         "Enter a real value. If you genuinely do not know, ask — a guess "
         "is better than a zero and a zero is not permitted."],
        ["My phone has not synchronised",
         "Coverage, almost always.",
         "Keep working; everything queues. Handovers recorded offline are just "
         "as valid."],
        ["The workshop says a charger is missing",
         "A discrepancy at book-in, which is exactly where it should be found.",
         "Raise it as a discrepancy, not a note. The previous custodian is "
         "named in the ledger and can be asked while they still remember."],
        ["A courier's tracking has stopped updating",
         "Their webhook may have failed, or they may be posting an event we "
         "cannot map.",
         "Unmappable events are logged and alerted. Check the log before "
         "telephoning the partner."],
        ["The charge looks wrong to the customer",
         "It is calculated from zone, distance, weight, declared value and "
         "service level, and an entitlement waiver may or may not apply.",
         "Show them the breakdown. If a waiver should have applied and did "
         "not, the entitlement record is what to check."],
        ["The rider cannot find the address",
         "Address quality is a real problem in parts of the country.",
         "Address validation learns from successful deliveries. The second "
         "attempt to the same place is usually better; the first may need a "
         "telephone call."],
        ["Cash on delivery does not balance",
         "Usually change given at a stop and not recorded.",
         "Reconcile against the individual consignments rather than the total. "
         "The tolerance is effectively zero and the shift will not close."],
        ["Somebody has asked me to correct the ledger",
         "It cannot be corrected. It can only be added to.",
         "Post a compensating entry with a stated reason. If somebody is "
         "pressing for an edit, escalate rather than comply."],
    ],

    "s13_faq": [
        ["Why do both parties have to scan at a handover?",
         "Because a one-sided record is a claim rather than a proof. Two scans "
         "with two identities means neither party can later say the handover "
         "did not happen the way it was recorded."],
        ["Can I see how much the item I am carrying is worth?",
         "You will see a value band, not the figure. That is a safety control "
         "for riders and it is not adjustable."],
        ["What happens if a customer refuses to sign?",
         "Record the refusal and capture the alternative evidence the app asks "
         "for. Never sign on their behalf."],
        ["Who pays when a delivery fails and the item returns to origin?",
         "The charge rules in the policy decide, and they depend on why it "
         "failed. The system applies them; it is not a rider decision."],
        ["Can a customer send someone else to collect?",
         "Yes — through recipient authorisation, verified at delivery. Not by "
         "telling the rider at the door."],
        ["How long does a blocked consignment stay blocked?",
         "Until quality reviews it. There is no timeout and there should not "
         "be one."],
        ["Is the custody ledger really unchangeable?",
         "Yes. Corrections are compensating entries with a stated reason, in "
         "the same way an accounting ledger works. The correction is part of "
         "the record."],
        ["Why can I not book a courier directly?",
         "You can, through the system. Booking outside it creates a "
         "consignment with a gap in its chain and an invoice line nobody can "
         "reconcile."],
        ["What counts as a restricted item?",
         "Lithium batteries, refrigerant and similar dangerous goods. The "
         "manifest flags them and only certified carriers are offered."],
        ["Does the customer see the whole custody chain?",
         "They see the custody state and expected timing for their own "
         "consignment — where it is and what happens next — not internal "
         "notes, costs or other stops on the rider's manifest."],
    ],

    # ============================================ 16. worth
    "s14_lede":
        "M03 will never show a large direct return. Its value is that four "
        "business lines and one legal position depend on it.",

    "s14_intro": [
        "This is infrastructure, and infrastructure is judged differently. The "
        "specification attaches BDT 190 lac a year to rental, trade-in and "
        "recycling collectively — and none of it is realised in M03. What M03 "
        "does is make those movements physically possible and legally "
        "defensible.",

        "The direct benefits are real but modest: fifteen per cent off the "
        "cost per consignment, recovered vendor credits, and logistics charges "
        "that stop leaking because they are calculated at the movement rather "
        "than reconstructed at invoicing. The large value is in what does not "
        "happen — the disputes not had, the devices not lost, and the data "
        "that does not leave the building.",
    ],

    "benefits": [
        ("Business lines it makes possible", 190, "BDT 190 lac/yr, elsewhere"),
        ("Cost per consignment reduction", 15, "-15% by Wave 6"),
    ],
    "benefits_note": ("The larger figure is realised in M13, M14 and M18. M03 "
                      "is the precondition, not the beneficiary."),

    "s14_benefits": [
        ["Pick and drop can actually scale",
         "A telephone-coordinated service is limited by one person's memory; a "
         "system-run one grows linearly with capacity",
         "Turns pick and drop from a favour into a growth channel"],
        ["Loss and damage reduction",
         "Custody accountability changes behaviour — people are careful when "
         "the record names them",
         "Target loss and damage under 0.1 per cent of consignments"],
        ["Disputes avoided",
         "Evidence replaces argument, and the item is often simply found",
         "Each avoided high-value dispute saves BDT 40,000 to 150,000, plus "
         "the relationship"],
        ["Logistics cost reduction",
         "Route sequencing, consolidation, carrier selection by cost, and "
         "visibility of what each movement costs",
         "15 per cent lower cost per consignment by Wave 6"],
        ["Four business lines enabled",
         "Rental delivery and collection, trade-in intake, refurbishment "
         "movement and e-waste collection all depend on it",
         "A precondition for BDT 190 lac a year across M13, M14 and M18"],
        ["Vendor credit recovery",
         "Return-to-vendor movements tracked through to the credit note",
         "Recovers value currently written off silently"],
        ["Charge capture",
         "Logistics charges calculated at the movement rather than "
         "reconstructed at invoicing",
         "Closes a revenue leak nobody has been able to size"],
    ],

    "s14_soft": [
        ["Legal defensibility",
         "For a company holding other people's business laptops, being able to "
         "prove custody is a material risk control rather than an "
         "administrative nicety."],
        ["Data protection assurance",
         "A device in transit holds the customer's data. Documented custody is "
         "part of the ISO 27001 story and part of what a corporate client will "
         "ask about."],
        ["Regulatory compliance",
         "E-waste movement requires transfer documentation, and restricted "
         "items require certified handling. Both are enforced rather than "
         "hoped for."],
        ["A better insurance position",
         "Documented declared values and custody records materially improve "
         "both insurability and claim outcomes."],
        ["Corporate client confidence",
         "A client decommissioning three hundred assets will ask how custody "
         "is proven. It is a tender question, and today there is no good "
         "answer."],
        ["Operational discipline",
         "Scan-based handover removes the 'I gave it to someone' ambiguity "
         "that quietly erodes accountability everywhere it is tolerated."],
    ],

    "s14_close":
        "The honest summary is that M03 is a cost centre that makes other "
        "people's revenue possible and keeps the company out of arguments it "
        "would lose. Judge it on loss rate, proof-of-delivery completeness and "
        "custody exceptions — not on a return that will always appear "
        "somewhere else.",

    # ============================================ 17. learning it
    "s17_lede":
        "For most people this is a fifteen-minute module. For coordinators and "
        "riders it is a fortnight.",

    "s17_intro": [
        "Most of the people who touch M03 need to learn one thing: scan both "
        "ways at every handover, and raise a discrepancy the moment you see "
        "one. That is genuinely all, and it takes about fifteen minutes to "
        "learn and a week to become automatic.",

        "Coordinators and riders need more, and the plan below is written for "
        "them. Everybody else should read sections 1, 6.2 and 10 and stop "
        "there.",
    ],

    "s17_plan": [
        ["Everybody, before you start",
         "Read section 1, then section 6.2 on chain of custody, then the "
         "rules in section 10.",
         "15 minutes",
         "Record a handover correctly and know why it matters"],
        ["Day one — riders",
         "Do a real collection and a real delivery with somebody beside you. "
         "Scan, identify, OTP, sign, photograph.",
         "2 stops",
         "Complete both proofs without prompting"],
        ["Day one — coordinators",
         "Watch the dashboard for a morning. Do not touch it. Notice how much "
         "resolves itself.",
         "1 hour",
         "Know which columns need you"],
        ["Day two — riders",
         "Read section 6.3. Work one stop deliberately in aeroplane mode and "
         "watch it synchronise.",
         "30 minutes",
         "Trust the offline queue"],
        ["Day two — coordinators",
         "Read sections 6.1 and 6.3. Create a multi-leg consignment by hand "
         "and follow it through.",
         "45 minutes",
         "Model a journey properly"],
        ["Day three",
         "Read section 10 again, and deliberately trigger two of the blocks in "
         "a test consignment.",
         "30 minutes",
         "Recognise a block rather than assuming a fault"],
        ["End of week one",
         "Riders: practise a failed delivery and a high-value collection. "
         "Coordinators: work the exception column to empty, unaided.",
         "45 minutes",
         "Handle the exceptions"],
        ["Week two, early",
         "Read section 11 and section 6.4. Coordinators: watch a courier leg "
         "from booking to reconciliation.",
         "40 minutes",
         "Understand where the automation ends"],
        ["Week two, middle",
         "Read section 15. Riders: reconcile a shift unaided. Coordinators: "
         "read the custody exception report properly.",
         "40 minutes",
         "Diagnose before escalating"],
        ["End of week two",
         "Read section 18 and keep it.",
         "15 minutes",
         "Work unsupervised"],
    ],

    "s17_check_intro":
        "You have got it when you can do these without thinking. For riders "
        "that is usually about thirty stops.",

    "s17_checks": [
        "Record a handover completely in under thirty seconds",
        "Explain to a customer why you need the OTP",
        "Record a failed delivery properly, with evidence, at the door",
        "Handle a high-value collection without prompting",
        "Recognise a discrepancy at book-in and raise it as an incident rather "
        "than a note",
        "Reconcile a shift's cash on delivery unaided",
        "Read a custody ledger and say who held an item last",
        "Know the three things that must be reported immediately: an unscanned "
        "handover, a seal break moved past, and anybody asking you to change "
        "the ledger",
    ],

    "s17_note":
        "If you are training branch or workshop staff, teach only the "
        "handover. It is the only part of M03 they will ever use, and teaching "
        "them the rest guarantees they remember none of it.",

    # ============================================ 18. one page
    "s15_lede":
        "The module on one page, for a hub wall, a van door or a first day.",

    "s15_figures": [
        ("42", "things you can do"),
        ("11", "consignment states"),
        ("12", "rules enforced"),
        ("12", "automatic behaviours"),
        ("0", "tolerated custody gaps"),
        ("100%", "proof of delivery target"),
        ("9", "reports available"),
        ("10", "modules depend on it"),
    ],

    "s15_never": [
        "Transfer custody without a scan and both parties identified",
        "Close a consignment without proof of delivery",
        "Collect anything with a zero or blank declared value",
        "Move a consignment on after a seal break or weight discrepancy",
        "Give a restricted item to an uncertified carrier",
        "Move anything to recycling without a data destruction certificate",
        "Start your next shift with cash on delivery unreconciled",
        "Move a high-value consignment without dual signature and insurance",
        "Edit the custody ledger — post a compensating entry instead",
    ],

    "s15_where": CM.where_to_look("M03"),
}
