# -*- coding: utf-8 -*-
"""
M06 — Data Services & Secure Data Handling.

Recovering customers' data when they have lost it, and destroying it when the
device leaves the company. The most confidentiality-critical module in the ERP,
and the only one where a single failure is a regulatory incident rather than an
operational one.

Worked examples name clients, media and figures so the reader can picture the
work. Those details are illustrative; the standards, thresholds and rules come
from the specification.
"""

from bizcontent import common as CM

CONTENT = {
    # ============================================================== front
    "cover_line": "Recovering a customer's data when they have lost it, and destroying "
    "it when the device leaves our hands. The one module where a single "
    "failure is a regulatory incident rather than an operational one.",
    "cover_inside": [
        ("Part one", "What the module is for, who uses it, and where it stops"),
        (
            "Part two",
            "All thirty-four things it lets you do, with worked "
            "examples and five walkthroughs from a normal day",
        ),
        (
            "Part three",
            "The rules, the automatic work, the permissions, the "
            "measures and the troubleshooting",
        ),
        ("Appendix A", "The full technical register for builders and testers"),
    ],
    "about": CM.about("the Data Services and Secure Data Handling module, " "M06"),
    "audience": CM.AUDIENCE,
    "how_arranged": CM.HOW_ARRANGED,
    "parts_table": CM.parts_table("M06"),
    "reading_note": CM.READING_NOTE,
    "appendix_note": CM.APPENDIX_NOTE,
    "part1_blurb": CM.PART1_BLURB,
    "part2_blurb": CM.PART2_BLURB,
    "part3_blurb": CM.PART3_BLURB,
    "appendix_blurb": CM.APPENDIX_BLURB,
    "part1_sections": CM.part1_sections(
        "M06", "The kinds of data work it has to carry"
    ),
    "part2_sections": CM.part2_sections("The journey of a data case"),
    "part3_sections": CM.PART3_SECTIONS,
    "appendix_sections": CM.APPENDIX_SECTIONS,
    "change_control": CM.CHANGE_CONTROL,
    "change_table": CM.change_table("The Technical Services Head"),
    "change_note": CM.CHANGE_NOTE,
    # ============================================================ exhibits
    "headline": [
        ("18", "rules enforced", "seventeen of them hard blocks"),
        ("34", "things the module lets you do", None),
        ("0", "tolerated custody exceptions", "not low — zero"),
        ("100%", "certificates within 24 hours", None),
        ("2", "business lines it gates", "refurbishment and recycling"),
        ("BDT 30 lac", "a year of data services revenue", None),
        ("BDT 77 lac", "a year it unlocks elsewhere", "M14 and M18 combined"),
        ("5 yrs", "access logs retained", None),
    ],
    "volume": [
        ("7", "recovery specialisms", "hard drive through to email and " "database"),
        ("5", "backup service types", "cloud, on-site, hybrid, CDP, archive"),
        ("2", "gated business lines", "neither can operate without a " "certificate"),
        (
            "5",
            "of twelve targets are 0 or 100%",
            "a partial score is a control " "failure",
        ),
        ("0", "people with blanket case access", "not even the IT " "administrator"),
    ],
    "volume_title": "Why this module is different from the rest",
    "volume_sub": "Where every other module has performance targets, this one "
    "has absolutes",
    "volume_caption": "The shape of a confidentiality-critical module",
    "does": [
        "Data recovery cases across all seven specialisms",
        "Chain of custody for media, under seal and dual control",
        "A free evaluation that produces a firm quotation before any charge",
        "Logging the recovery method and every attempt made",
        "An inventory of what was recovered — without exposing any of it",
        "Secure handover, then verified purge with a certificate",
        "Backup plans, job monitoring and restore testing",
        "Metering backup capacity for billing",
        "Archival, retrieval and data migration as services",
        "Secure destruction: erasure, physical destruction, verification, "
        "certification",
        "Bulk corporate decommissioning projects",
        "Cleanroom and specialist equipment scheduling",
        "Partner laboratory referral without breaking custody",
        "The access control and audit regime that makes all of it defensible",
    ],
    "does_not": [
        "The customer-facing service order and tracking, which are M01",
        "Moving media between sites, which is M03 — custody in transit is " "logistics",
        "Refurbishing or grading a device, which is M14 — M06 only certifies",
        "Recycling and disposal certificates, which are M18",
        "Running backups on client infrastructure, which is M05",
        "Pricing and quotation, which are M11 and M36",
        "Billing, which is M20 and M39",
        "1000FiX's own internal backups, which are M30 and M60",
        "Encryption key management for the platform, which is M29",
        "Investigating a security incident, which is M60 — M06 detects and " "reports",
    ],
    "areas_map": [
        (
            "Recovering lost data",
            11,
            "Seven specialisms, a free evaluation, and a method log for every " "step.",
        ),
        (
            "Custody and who may look",
            5,
            "Sealed containers, dual signatures, named access and an immutable " "log.",
        ),
        (
            "Holding it no longer than agreed",
            2,
            "An automatic purge at the agreed date, and the only way to delay " "it.",
        ),
        (
            "Destroying data properly",
            6,
            "The right technique for the medium, verified, witnessed and " "certified.",
        ),
        (
            "Backup, archive and migration",
            10,
            "The services that keep data safe before anybody needs it back.",
        ),
    ],
    "area_bars": [
        ("Recovering lost data", 11),
        ("Backup, archive and migration", 10),
        ("Destroying data properly", 6),
        ("Custody and who may look", 5),
        ("Holding it no longer than agreed", 2),
    ],
    "channels": [
        "A customer with a failed hard drive at a counter",
        "A corporate client decommissioning a fleet",
        "A refurbishment job needing a certificate before it can start",
        "A recycling batch that cannot move without one",
        "A backup subscription being set up",
        "A restore request from a managed client",
        "A scheduled restore test falling due",
        "A migration project for a corporate customer",
    ],
    "channels_hub": "Data case",
    "channels_title": "Eight ways work reaches the data services lab",
    "channels_sub": (
        "Every one of them becomes a confidentiality-controlled "
        "case with restricted visibility from creation"
    ),
    "channels_note": "restricted from the first second",
    "channels_caption": "What generates work in a data services operation",
    # ============================================ 1. what it is for
    "s1_lede": "M06 does two things that look unrelated and are the same thing: it "
    "recovers customers' data when they have lost it, and it destroys "
    "customers' data when the device leaves 1000FiX's hands.",
    "s1_intro": [
        "Both are billable services and both put the company in temporary "
        "possession of information it must never read, copy, retain or lose. "
        "A failed drive brought to a counter might hold a law firm's case "
        "files, a hospital's patient records or somebody's family "
        "photographs. A laptop going for refurbishment holds whatever its "
        "previous owner left on it.",
        "That is what makes M06 the most confidentiality-critical module in "
        "the entire system, and it is the only one where a single failure is a "
        "regulatory incident rather than an operational one. Everywhere else "
        "in this library a mistake costs time or money. Here a mistake is a "
        "notifiable breach.",
        "The module also gates two other business lines outright. No device "
        "may be refurbished and resold, and no device may be sent for "
        "recycling, without a certified data destruction record produced here. "
        "That gate is a hard block with no override — not for a manager, not "
        "for a director, not when there is a lorry waiting.",
    ],
    "s1_problem": [
        "The business plan describes seven data recovery specialisms and five "
        "backup service types in detail. It describes data wiping and privacy "
        "protection as part of refurbishment, and data destruction as part of "
        "recycling. All of it is currently done — where it is done at all — on "
        "job cards, with no chain of custody, no access control, no retention "
        "limit and no certificate.",
        "For a company that is ISO 9001:2015 certified, holds an information "
        "security management policy, and publicly advertises that a customer's "
        "device and data are one hundred per cent secure, that is an exposure "
        "which grows with volume. Every additional device handled is another "
        "opportunity for the published promise to turn out to be untrue.",
        "There is also a legal position that has moved. The Personal Data "
        "Protection Act 2026 governs consent, transparency, data residency, "
        "retention and breach notification, and its enforcement mechanisms "
        "activate in 2027. The specification records that it was not "
        "referenced in any earlier version of the programme documentation. "
        "M06 is where most of its practical requirements land.",
    ],
    "s1_replaces": [
        [
            "A job card for a data recovery",
            "A confidentiality-controlled case with named access and an immutable "
            "log",
            "Who touched a customer's data, and when, becomes answerable.",
        ],
        [
            "Media handled like any other device",
            "Sealed-container control with two distinct signatures at every "
            "boundary",
            "Media cannot enter or leave the secure area on one person's word.",
        ],
        [
            "Recovery attempted on the customer's original disk",
            "Work performed on an image, never the original where technically "
            "possible",
            "A failed attempt does not destroy the last chance of recovery.",
        ],
        [
            "Recovered data kept until somebody remembers to delete it",
            "An automatic purge at the agreed date, with a certificate",
            "Data the company no longer needs stops being a liability it still "
            "holds.",
        ],
        [
            "Assuming a device was wiped before refurbishment",
            "A hard block: no certificate, no refurbishment, no exceptions",
            "A resold laptop containing somebody's data becomes impossible rather "
            "than unlikely.",
        ],
        [
            "A blanket assurance that a batch was cleared",
            "A serialised certificate per media item, bound to its serial number",
            "A corporate client can reconcile every device against their own "
            "asset list.",
        ],
        [
            "No answer to 'how do you handle our data?' in a tender",
            "A documented, auditable process with evidence for any period",
            "Removes a disqualifier from bids the company currently cannot win.",
        ],
        [
            "Backups that report success and have never been restored",
            "Scheduled restore tests with recorded evidence",
            "An untested backup stops being mistaken for a working one.",
        ],
    ],
    "s1_one_sentence": "M06 is the module that lets 1000FiX handle other people's data — "
    "recover it, hold it briefly, and destroy it completely — and prove "
    "afterwards exactly what happened to it.",
    # ============================================ 2. who uses it
    "s2_lede": "Very few people, deliberately. This is the strictest permission model "
    "in the entire system, and even the IT administrator has no way in.",
    "s2_intro": [
        "Most modules are designed to be widely usable. M06 is designed to be "
        "narrowly usable, and the narrowness is the control. Membership of a "
        "role never grants access to a case; access is granted per case, to a "
        "named individual who has recorded a confidentiality undertaking for "
        "that case, and every single access is logged and kept for five years.",
        "The list below is therefore shorter and more restricted than "
        "anywhere else in this library. A data services technician sees only "
        "their own assigned cases — never all of them. The quality manager "
        "sees custody, certificates and exceptions but never case content. The "
        "IT administrator, who can administer the platform itself, has no path "
        "into a case workspace at all.",
    ],
    "s2_roles": [
        [
            "Data services technician",
            "Evaluating, imaging, recovering and verifying",
            "Only the cases they have been assigned to, and nothing else",
        ],
        [
            "Technical Services Head",
            "Running the lab, quoting, prioritising and referring",
            "All cases — with every access logged",
        ],
        [
            "Quality manager",
            "Custody, certificates, exceptions and audit evidence",
            "Custody and certificate records, never case content",
        ],
        [
            "Service centre agent",
            "Opening a case at a counter and telling a customer where it is",
            "Case creation and status only. No workspace access",
        ],
        ["Contact centre agent", "Answering a status enquiry", "Status only"],
        [
            "Finance manager",
            "Billable events and case costing",
            "Costing and billing, with no case detail",
        ],
        [
            "Chief Technology Officer",
            "Investigation, with explicit approval",
            "Any case, only with approval, and always logged",
        ],
        [
            "IT administrator",
            "Keeping the platform running",
            "Nothing inside a case workspace. This is deliberate",
        ],
        [
            "Customer",
            "Knowing where their case is and getting their certificate",
            "Their own case status and certificates",
        ],
        [
            "Corporate portal user",
            "Reconciling a decommissioning project",
            "Their own organisation's project and certificates",
        ],
    ],
    "s2_days": [
        {
            "title": "If you are a data services technician",
            "text": [
                "Your working day happens inside a case workspace that you "
                "were granted access to individually, after recording a "
                "confidentiality undertaking for that specific case. You "
                "cannot browse other cases. You cannot see a list of them. "
                "That constraint is unusual and it takes about a week to stop "
                "feeling like an obstacle.",
                "The discipline that matters most is imaging. Recovery work is "
                "performed on an image and never on the original media "
                "wherever technically possible, because a failed attempt on an "
                "original is often the end of the only chance the customer "
                "has. Every technique you apply — logical, firmware, "
                "mechanical, chip-off, RAID reconstruction — is logged with "
                "your identity and every step recorded.",
                "The other thing to internalise early is that you build an "
                "inventory of what you recovered without ever recording what "
                "it is. Volumes, file counts, types and sizes go into the "
                "system. File names and content do not, and are not stored in "
                "the ERP at all.",
            ],
        },
        {
            "title": "If you run the lab",
            "text": [
                "Three things will occupy you. The first is the evaluation "
                "flow: a no-charge assessment producing a recoverability "
                "judgement and a firm quotation, which is what turns data "
                "recovery from an unquotable specialism into a service with a "
                "measurable success rate and a margin.",
                "The second is custody exceptions, which are reported daily "
                "and should be nil. A single-signature attempt, a seal break, "
                "unaccounted media or an overdue purge each mean something has "
                "slipped, and in this module a partial score is a control "
                "failure rather than a performance gap.",
                "The third is cases that have gone quiet. Media held without "
                "progress is a custody risk in its own right — the longer "
                "somebody else's drive sits in the lab, the more exposure the "
                "company carries for no revenue. Idle cases raise an alert for "
                "exactly that reason.",
            ],
        },
        {
            "title": "If you work in refurbishment or recycling",
            "text": [
                "Your relationship with M06 is a single gate, and it will stop "
                "you. A device cannot enter refurbishment and a batch cannot "
                "move to a recycling partner without a valid certificate of "
                "destruction bound to that media serial number. The system "
                "checks and refuses.",
                "That will occasionally be inconvenient — a batch assembled "
                "after the wiping run, a device added late, a lorry booked. "
                "Treat the refusal as the control working. A resold laptop or "
                "a scrapped drive containing a customer's data would cost more "
                "than any delay this gate has ever caused.",
            ],
        },
        {
            "title": "If you sell to corporate clients",
            "text": [
                "You gain an answer to a question you currently cannot answer. "
                "Corporate and government tenders increasingly ask how a "
                "supplier handles data, and today the honest response is a "
                "description of intentions. With M06 it is a documented "
                "process with custody records, access logs, retention limits "
                "and per-device certificates that can be shown for any "
                "period.",
                "There is also a service to sell that does not exist today. "
                "Bulk decommissioning — a client retires three hundred "
                "laptops and receives a serialised certificate for each one, "
                "reconciled against their own asset list — is a chargeable "
                "engagement for every corporate customer the company has.",
            ],
        },
    ],
    "s2_note": "Access is granted per case to a named individual, never by role. If "
    "you can open a case you were not assigned to, that is not a "
    "convenience — it is the most serious defect this system could have, "
    "and it should be reported within the hour.",
    # ============================================ 3. boundary
    "s3_lede": "M06 handles the data. Other modules handle the device, the movement, "
    "the money and the customer conversation.",
    "s3_intro": [
        "The boundary here is drawn around information rather than around a "
        "physical object, which takes a little getting used to. A failed drive "
        "in the lab is simultaneously an asset in M17, a consignment leg in "
        "M03, a service order in M01 and a case in M06 — and each of those "
        "modules knows a different thing about it.",
        "M06 knows what is on it, or rather knows precisely enough about what "
        "is on it to recover it and then to prove it is gone. It does not own "
        "the customer conversation: the customer-facing view stays in M01, and "
        "a data case is deliberately a confidentiality-controlled record "
        "linked to a service order rather than a replacement for one.",
        "Two boundaries are gates rather than divisions. M06 provides the "
        "destruction certificate that M14 refurbishment and M18 recycling "
        "cannot proceed without. And M03 will not move an item to a recycling "
        "partner without it. Those three modules together form a control that "
        "no single one of them could enforce alone.",
    ],
    "s3_shared_intro": "Several things exist in more than one module at once. This table says "
    "which part each owns.",
    "s3_shared": [
        [
            "The data case",
            "M06 — this module owns it",
            "Creates it, controls access to it, and closes it",
        ],
        [
            "The service order",
            "M01",
            "The parent, with restricted visibility. The customer-facing view "
            "stays there",
        ],
        [
            "The media item",
            "M17 owns the asset identity",
            "Owns it while it is in the lab, under seal and dual control",
        ],
        [
            "The destruction certificate",
            "M06 issues, M24 retains",
            "Issues it, serialised and bound to a media serial number",
        ],
        [
            "The custody event",
            "M03 owns the shared ledger",
            "Raises events into it. Custody in transit is logistics; custody in "
            "the lab is M06",
        ],
        [
            "The backup plan",
            "M06 defines, M05 monitors",
            "Owns the definition and the commercial service; M05 watches the jobs "
            "run",
        ],
        [
            "Physical destruction of the device",
            "M18 Recycling",
            "Destroys the data. M18 disposes of the device afterwards",
        ],
        [
            "Refurbishment",
            "M14",
            "Provides the certificate that M14 cannot start without. Does no "
            "bench work",
        ],
        [
            "Encryption keys",
            "M29 Identity",
            "Uses the platform's key service. Does not operate one",
        ],
        [
            "A security incident",
            "M60 and M29",
            "Detects and reports. Investigation belongs elsewhere",
        ],
    ],
    # ============================================ 4. kinds of work
    "s4k_title": "The kinds of data work it has to carry",
    "s4k_lede": "Seven recovery specialisms, five backup services, two destruction "
    "methods and one bulk project type — with one set of custody rules "
    "over all of them.",
    "s4k_intro": [
        "Recovering a photograph from a memory card and reconstructing a "
        "failed RAID array for a hospital are the same module and very nearly "
        "the same process. What changes is the technique, the equipment, the "
        "time and the price. What does not change is the custody, the access "
        "control, the retention limit and the certificate at the end.",
        "Destruction divides more sharply. Erasure is preferred where it can "
        "be verified, because the device survives and can be resold. Physical "
        "destruction — shredding, degaussing, crushing — is mandatory where "
        "erasure cannot be verified, and requires photographic evidence and a "
        "witness. The technique is selected by data confidentiality, media "
        "type and where the device is going next, under the company's "
        "documented sanitisation programme.",
    ],
    "kinds_columns": [
        (
            "Recovery",
            "Seven specialisms, one custody regime",
            [
                "Hard drive and SSD recovery",
                "RAID array reconstruction",
                "USB flash and memory card",
                "Mobile phone recovery",
                "Email and database recovery",
            ],
        ),
        (
            "Protection",
            "Five services, sold by subscription",
            [
                "Cloud backup",
                "On-site backup",
                "Hybrid backup",
                "Continuous data protection",
                "Long-term archival with retrieval",
            ],
        ),
        (
            "Destruction",
            "Two methods, one certificate",
            [
                "Verified erasure, where the device survives",
                "Cryptographic erase with key zeroization",
                "Physical destruction, witnessed and photographed",
                "Bulk corporate decommissioning",
            ],
        ),
    ],
    "kinds_title": "Three families of data work",
    "kinds_sub": "Recovering it, protecting it, and making certain it is gone",
    "s4k_header": [
        "The kind of work",
        "What is different about it",
        "What stays the same",
    ],
    "s4k_table": [
        [
            "Hard drive and SSD recovery",
            "The commonest case. Logical, firmware or mechanical technique "
            "depending on the failure, often requiring the cleanroom.",
            "Sealed custody, named access, work on an image, method logged, "
            "purge at the agreed date",
        ],
        [
            "RAID reconstruction",
            "Several drives, an unknown or damaged array configuration, and the "
            "highest value per case.",
            "As above",
        ],
        [
            "Flash, memory card and mobile",
            "Chip-off technique is common, which is destructive to the device and "
            "has to be consented to.",
            "As above",
        ],
        [
            "Email and database recovery",
            "Logical rather than physical. Often no media in the lab at all.",
            "As above, minus the physical custody",
        ],
        [
            "Backup subscription",
            "Recurring rather than one-off. Capacity is metered for billing, and "
            "restore tests are scheduled rather than requested.",
            "Access control, retention discipline, evidence",
        ],
        [
            "Data migration",
            "A project with a scope, a checklist and source-against-target "
            "verification signed off by the customer.",
            "As above",
        ],
        [
            "Verified erasure",
            "The technique is chosen by confidentiality, media type and "
            "disposition. Where cryptographic erase is used, the key material is "
            "zeroized and the evidence recorded.",
            "A serialised certificate bound to one media serial number",
        ],
        [
            "Physical destruction",
            "Mandatory where erasure cannot be verified. Requires photographic "
            "evidence and a witness who is not the operator.",
            "As above",
        ],
        [
            "Bulk decommissioning",
            "Hundreds of devices at once, reconciled against the client's own "
            "declared asset list, with a certificate per device.",
            "As above — no blanket certificates, ever",
        ],
    ],
    "s4k_caption": "The kinds of data work and what distinguishes each",
    "s4k_note": "Every certificate binds to a specific media serial number. Blanket "
    "certificates covering a batch are not permitted, because a batch "
    "certificate cannot prove anything about the one device a client asks "
    "about.",
    # ============================================ 5. vocabulary
    "s4_lede": "Fourteen words, several of them from information security and two of "
    "them from the law.",
    "s4_intro": [
        "Data services borrows its vocabulary from forensics and information "
        "security, and precision matters here more than anywhere else in this "
        "library. Erasure and destruction are different. A purge and a "
        "deletion are different. A hold is a legal instrument, not a delay.",
    ],
    "s4_glossary": [
        [
            "Data case",
            "The confidentiality-controlled record covering one piece of data "
            "work. Restricted from the moment it is created.",
            "The central record of this module",
        ],
        [
            "Case workspace",
            "The controlled area of the system where a case's material lives. "
            "Access is per case, per named individual, never by role.",
            "Where all the actual work happens",
        ],
        [
            "Sealed container control",
            "Media held in a sealed container with the seal number recorded, "
            "checked at every boundary.",
            "How physical custody is maintained inside the lab",
        ],
        [
            "Dual control",
            "Two distinct authenticated signatures required for an action. Media "
            "entering or leaving the secure area needs both.",
            "One person can never move media alone",
        ],
        [
            "Evaluation",
            "The free, no-charge assessment that produces a recoverability "
            "judgement and a firm quotation before any chargeable work.",
            "The stage that makes recovery quotable",
        ],
        [
            "Imaging",
            "Taking a copy of the media and working on the copy. Recovery is "
            "performed on an image, never the original, wherever possible.",
            "The single most important technical discipline in the lab",
        ],
        [
            "Methodology log",
            "The record of which technique was applied and every step taken, with "
            "the operator's identity.",
            "What makes a failed recovery explainable",
        ],
        [
            "Recovered-data inventory",
            "A list of what was recovered by type, count and size — with no file "
            "names and no content.",
            "The company knows how much it recovered, never what it was",
        ],
        [
            "Retention window",
            "The agreed period recovered data may be held before it must be " "purged.",
            "Starts at handover; the purge is automatic",
        ],
        [
            "Purge",
            "Verified destruction of the recovered data at the end of the "
            "retention window, with a certificate.",
            "Automatic. Missing one is a control failure",
        ],
        [
            "Hold",
            "A documented, approved, time-limited authorisation to retain data "
            "beyond the window. The only lawful way to delay a purge.",
            "Rare, and always temporary",
        ],
        [
            "Sanitisation technique",
            "The method used to make data unrecoverable, chosen by "
            "confidentiality, media type and where the device is going next.",
            "Selected under the company's documented sanitisation programme",
        ],
        [
            "Cryptographic erase",
            "Destroying the encryption key rather than the data, which makes the "
            "data unrecoverable. The key material must be zeroized and the "
            "evidence recorded.",
            "Fast, and only valid where the evidence exists",
        ],
        [
            "Certificate of destruction",
            "A serialised, verifiable record per media item stating method, "
            "standard, operator, date, witness and verification result.",
            "The thing two other business lines cannot proceed without",
        ],
    ],
    # ============================================ 6. what you can do
    "s5_lede": "Thirty-four things, in five areas. The second and third are why the "
    "other three are trusted.",
    "s5_intro": [
        "The areas below follow the two halves of the module and the "
        "discipline that spans both: recovering data, controlling who can "
        "touch it, holding it no longer than agreed, destroying it properly, "
        "and the protective services sold alongside.",
        "Read the second and third areas whatever your role. Custody, access "
        "control and retention are what make everything else in this module "
        "defensible, and they are the parts where a shortcut is a regulatory "
        "matter rather than an operational one.",
    ],
    "areas": [
        {
            "title": "Recovering lost data",
            "who": [
                (
                    "Mostly used by",
                    "Data services technicians and the " "Technical Services Head",
                ),
                (
                    "Also relied on by",
                    "Counter agents opening cases, and " "finance costing them",
                ),
                ("Where it happens", "The lab and the cleanroom"),
            ],
            "intro": [
                "Eleven functions covering the recovery half of the module. "
                "The business plan names seven specialisms — hard drive, solid "
                "state, RAID, USB flash, memory card, mobile phone, and email "
                "and database — and they run through one case flow with "
                "different techniques and equipment.",
                "The stage that changes the commercial character of the "
                "service is the free evaluation. A no-charge assessment "
                "producing a recoverability judgement and a firm quotation, "
                "before any chargeable work, is what turns recovery from an "
                "unquotable specialism into a service with a measurable "
                "success rate. It also supports no-recovery-no-fee pricing, "
                "which is what most customers expect.",
                "One function is quietly unusual. The recovered-data inventory "
                "records what was recovered by type, count and size — and "
                "never records file names or content. The company knows how "
                "much it recovered. It does not know, and does not store, what "
                "it was.",
            ],
            "features": [
                [
                    "Case intake",
                    "Opens a recovery case with media type, symptoms, "
                    "criticality, what the customer is hoping to get back, and "
                    "their declarations.",
                    "The anxious conversation at the counter becomes a "
                    "structured record.",
                ],
                [
                    "Free evaluation",
                    "Records a no-charge assessment producing a recoverability "
                    "judgement and a firm quotation before anything chargeable "
                    "starts.",
                    "The customer decides on a price, not on a hope.",
                ],
                [
                    "Methodology log",
                    "Records which technique was applied — logical, firmware, "
                    "mechanical, chip-off, RAID reconstruction — and every step, "
                    "with the operator's identity.",
                    "A failed recovery can be explained rather than merely "
                    "reported.",
                ],
                [
                    "Success-based pricing",
                    "Supports no-recovery-no-fee and tiered pricing by data "
                    "volume and complexity.",
                    "The customer's risk is bounded, which is why they agree at "
                    "all.",
                ],
                [
                    "Recovered-data inventory",
                    "Lists recovered volumes and file counts by type and size, "
                    "without exposing names or content.",
                    "We can prove what we recovered without ever knowing what it "
                    "was.",
                ],
                [
                    "Secure handover",
                    "Delivers the recovered data on approved media or by secure "
                    "transfer, with a signed receipt from a verified recipient.",
                    "The data reaches the person entitled to it and nobody else.",
                ],
                [
                    "Cleanroom scheduling",
                    "Schedules and logs cleanroom usage per case as a constrained "
                    "resource.",
                    "The most expensive facility in the lab is not idle and not "
                    "double-booked.",
                ],
                [
                    "Specialist equipment tracking",
                    "Tracks specialist equipment and consumables against the " "case.",
                    "A case's true cost includes the equipment time it consumed.",
                ],
                [
                    "Partner laboratory referral",
                    "Refers a case beyond internal capability to a partner lab, "
                    "with custody continuity and commercial terms.",
                    "A case we cannot do is passed on rather than attempted and "
                    "lost.",
                ],
                [
                    "Case prioritisation",
                    "Prioritises by criticality, contract and customer tier.",
                    "A hospital's server comes before a holiday photograph, "
                    "explicitly rather than tacitly.",
                ],
                [
                    "Case costing",
                    "Tracks labour, consumables, equipment time and partner cost "
                    "per case.",
                    "The margin on data recovery becomes knowable.",
                ],
            ],
            "example": (
                "a RAID array that came back",
                "A twelve-partner law firm loses a four-drive RAID array "
                "holding its document management system. Two drives have "
                "failed; the array will not rebuild. The case is opened at the "
                "Gulshan counter as a data recovery with criticality marked "
                "highest, and it is immediately confidentiality-controlled — "
                "the counter agent who opened it cannot see anything more "
                "about it than its status. The free evaluation takes two days: "
                "one drive has a head crash and needs the cleanroom, the other "
                "has a firmware fault. The assessment says recovery is "
                "probable and quotes BDT 145,000, no recovery no fee. The firm "
                "accepts. All four drives are imaged before any work is "
                "attempted, so nothing that follows can make things worse. The "
                "head crash is addressed in the cleanroom, the firmware fault "
                "logically, and the array is reconstructed from the images. "
                "The inventory records 4 volumes, 1.9 TB, 412,000 files by "
                "type — and no file names. Handover is to a verified partner "
                "of the firm on encrypted media with a signed receipt. Nine "
                "days from intake.",
            ),
            "mistakes": [
                "Attempting recovery on the original media because imaging "
                "will take another two hours. A failed attempt on an original "
                "is often the end of the customer's only chance.",
                "Recording file names in a case note to help a colleague. The "
                "inventory is metadata-only by design and content must never "
                "enter the system.",
                "Quoting before the evaluation is complete. The evaluation "
                "exists so that the quotation is firm, and a revised quotation "
                "after acceptance is a very difficult conversation.",
                "Letting a case sit while waiting for a part or a decision. "
                "Media held without progress is custody exposure with no "
                "revenue attached, and idle cases raise an alert.",
            ],
        },
        {
            "title": "Custody and who may look",
            "who": [
                ("Mostly used by", "Everybody who touches a case, at every " "step"),
                ("Also relied on by", "The quality manager and any auditor"),
                ("Where it happens", "Every boundary of the secure area"),
            ],
            "intro": [
                "Five functions, and they are the reason the rest of the "
                "module can be trusted. Media is tracked under sealed-container "
                "control through evaluation, cleanroom, imaging, recovery, "
                "verification and return. Two distinct authenticated "
                "signatures are required for media to enter or leave the "
                "secure area.",
                "Access to a case workspace is restricted to named, "
                "multi-factor-authenticated, case-assigned staff. Membership "
                "of a role grants nothing. A confidentiality undertaking is "
                "recorded per case before access is granted, and every access "
                "is logged immutably and retained for five years.",
                "This is the strictest permission model in the ERP, and the "
                "clearest illustration of it is that the IT administrator — "
                "who can administer the platform — has no path into a case "
                "workspace at all.",
            ],
            "features": [
                [
                    "Media chain of custody",
                    "Tracks physical media through every stage under "
                    "sealed-container control.",
                    "Where a customer's drive is, and who has it, is always "
                    "answerable.",
                ],
                [
                    "Access restriction",
                    "Limits case workspace access to named, "
                    "multi-factor-authenticated, case-assigned staff.",
                    "Nobody can browse other people's cases, including senior "
                    "people.",
                ],
                [
                    "Confidentiality undertaking",
                    "Captures a staff undertaking per case, and a customer "
                    "non-disclosure agreement where required.",
                    "The obligation is specific to the case rather than a general "
                    "policy nobody remembers signing.",
                ],
                [
                    "Communication controls",
                    "Restricts what case detail may be communicated, to whom, and "
                    "by which role.",
                    "A helpful remark to the wrong person stops being possible.",
                ],
                [
                    "Compliance reporting",
                    "Reports custody, access, retention and destruction for "
                    "internal and external audit.",
                    "An ISO audit becomes a report rather than a fortnight of "
                    "assembling paper.",
                ],
            ],
            "example": (
                "the access log that cleared a technician",
                "A customer alleges that photographs recovered from their "
                "phone six weeks earlier have appeared elsewhere, and names "
                "the technician who handled the case. The allegation is "
                "serious and, under the old way of working, unanswerable. "
                "Instead the access log for that case is produced: three "
                "individuals had access, each with a recorded confidentiality "
                "undertaking, and every access is timestamped with the action "
                "taken. The named technician accessed the workspace on four "
                "occasions totalling eleven hours, all within the recovery "
                "window, with no export and no egress attempt. The recovered "
                "data was purged automatically nine days after handover with a "
                "purge certificate issued. The inventory shows counts and "
                "sizes only; no file was ever named in the system. The "
                "allegation is answered in an afternoon with evidence rather "
                "than assurance, and an honest technician's reputation is "
                "protected — which is exactly what the logging is for.",
            ),
            "mistakes": [
                "Sharing your session with a colleague who needs to see "
                "something. Access is per named individual and the log will "
                "show your identity doing their work.",
                "Moving media out of the secure area on your own because the "
                "second signatory is at lunch. It is a hard block and "
                "attempting it is recorded as a custody exception.",
                "Discussing a case with a colleague who is not assigned to it. "
                "Communication controls exist because a helpful remark is the "
                "commonest way confidentiality actually fails.",
                "Treating the confidentiality undertaking as paperwork. It is "
                "per case, and it is what makes an obligation specific enough "
                "to be meaningful.",
            ],
            "caution": "Every access to a case workspace is logged immutably and kept "
            "for five years. That log exists to protect you as much as to "
            "monitor you — it is what answers an allegation, and it cannot "
            "do that if people share sessions.",
        },
        {
            "title": "Holding it no longer than agreed",
            "who": [
                ("Mostly used by", "The system, automatically"),
                (
                    "Also relied on by",
                    "The quality manager, watching for " "overdue purges",
                ),
                ("Where it happens", "At the end of every retention window"),
            ],
            "intro": [
                "Two functions, and they carry more legal weight than their "
                "number suggests. Recovered data is held only for the agreed "
                "window and then purged verifiably, with a purge certificate "
                "issued to the customer. The clock starts at handover and the "
                "purge is automatic.",
                "The second function is the only lawful way to delay it: a "
                "documented, approved and time-limited hold. Not an "
                "indefinite one, not a verbal one, and not one that anybody "
                "can apply. Data retained beyond its window without a "
                "documented hold is a control failure, and the target for it "
                "is zero.",
                "The reason this matters more than it looks is that held data "
                "is pure liability. Once the customer has their recovery, "
                "every additional day the company keeps a copy is risk with no "
                "revenue attached to it.",
            ],
            "features": [
                [
                    "Time-boxed retention",
                    "Holds recovered data only for the agreed window, then purges "
                    "verifiably and issues a purge certificate.",
                    "The company stops accumulating other people's data by "
                    "accident.",
                ],
                [
                    "Hold override",
                    "Permits retention beyond the window only under a documented, "
                    "approved and time-limited hold.",
                    "A genuine legal or operational need is accommodated without "
                    "opening a loophole.",
                ],
            ],
            "example": (
                "the purge that happened on time",
                "A customer's recovered data — 340 GB from a failed laptop "
                "drive — is handed over on the 12th on encrypted media with a "
                "signed receipt. The agreed retention window is thirty days, "
                "so the copy held in the controlled environment is scheduled "
                "for purge on the 11th of the following month. On that date "
                "the purge executes automatically, destruction is verified, "
                "and a purge certificate is issued to the customer and filed. "
                "Nobody had to remember. Nobody had to decide. The customer "
                "receives a message telling them their data no longer exists "
                "at 1000FiX, which — for a customer who was anxious enough to "
                "pay for recovery in the first place — is a more reassuring "
                "message than most companies ever send.",
            ),
            "mistakes": [
                "Extending a retention window informally because the customer "
                "might want another copy. Only a documented, approved, "
                "time-limited hold can delay a purge.",
                "Treating an overdue purge as an administrative backlog. It is "
                "a control failure with a target of zero, and it escalates "
                "immediately for that reason.",
                "Keeping a working copy outside the controlled environment "
                "'just in case'. Recovered data may not leave except through "
                "the approved handover path, and egress attempts are blocked "
                "and alerted.",
            ],
        },
        {
            "title": "Destroying data properly",
            "who": [
                ("Mostly used by", "Data services technicians and a witness"),
                (
                    "Also relied on by",
                    "Refurbishment, recycling and every " "corporate client",
                ),
                ("Where it happens", "The lab, and occasionally with a " "shredder"),
            ],
            "intro": [
                "Six functions, and they gate two entire business lines. A "
                "destruction request arrives from refurbishment, from "
                "recycling, from a customer directly, or from a corporate "
                "decommissioning project. The technique is selected by data "
                "confidentiality, media type and final disposition under the "
                "company's documented sanitisation programme.",
                "Where erasure can be verified, the device survives and can be "
                "resold — which is worth money. Where it cannot, physical "
                "destruction is mandatory, with photographic evidence and a "
                "witness who is not the operator. Where cryptographic erase is "
                "used, the key material must be zeroized and the "
                "key-destruction evidence recorded, because destroying a key "
                "you cannot prove you destroyed is not destruction.",
                "The output is a serialised, verifiable certificate per device "
                "recording method, standard, operator, date, witness and "
                "verification result. It binds to one media serial number. "
                "Blanket certificates covering a batch are not permitted, "
                "because a batch certificate cannot answer a question about "
                "one device.",
            ],
            "features": [
                [
                    "Wipe request",
                    "Accepts a destruction request from refurbishment, recycling, "
                    "a customer, or a corporate decommissioning project.",
                    "One route in, whoever is asking.",
                ],
                [
                    "Method and standard",
                    "Records the technique applied, selected by confidentiality, "
                    "media type and final disposition under the documented "
                    "programme.",
                    "The right method for the medium, chosen by rule rather than "
                    "by habit.",
                ],
                [
                    "Cryptographic erase",
                    "Where the key is destroyed rather than the data, applies "
                    "proper zeroization to the key material and records the "
                    "evidence.",
                    "A fast method that remains defensible.",
                ],
                [
                    "Vendor trust verification",
                    "Where a sanitisation tool or third-party service is used, "
                    "records the evidence establishing trust in that "
                    "implementation.",
                    "'The software said it worked' becomes an auditable claim.",
                ],
                [
                    "Physical destruction",
                    "Records shredding, degaussing or crushing where erasure is "
                    "not possible, with photographic evidence and a witness.",
                    "The last resort is evidenced rather than assumed.",
                ],
                [
                    "Certificate of destruction",
                    "Issues a serialised, verifiable certificate per device with "
                    "method, standard, operator, date, witness and verification "
                    "result.",
                    "The document two other business lines cannot proceed " "without.",
                ],
                [
                    "Bulk decommission projects",
                    "Manages corporate bulk decommissioning, reconciled against "
                    "the client's declared asset list.",
                    "Three hundred laptops become three hundred certificates and "
                    "one reconciliation.",
                ],
                [
                    "Exception handling",
                    "Handles media that cannot be erased or verified, with "
                    "escalation, physical destruction fallback and customer "
                    "notification.",
                    "The awkward cases have a defined path rather than a drawer.",
                ],
            ],
            "example": (
                "three hundred laptops, three hundred certificates",
                "A bank decommissions three hundred and twelve laptops across "
                "four offices. A bulk decommissioning project is opened with "
                "the client's declared asset list loaded into it. Collection "
                "runs over two weeks through M03 with sealed-container "
                "custody, and each machine is booked into the lab under dual "
                "signature. Two hundred and ninety-one drives take verified "
                "erasure and survive, which matters commercially because the "
                "machines can then be refurbished. Eighteen fail verification "
                "and go to physical destruction, each shredded with "
                "photographic evidence and a witness who is not the operator. "
                "Three drives are missing entirely. That is the finding the "
                "client most needs: reconciliation against their own asset "
                "list shows three serial numbers declared and never received, "
                "and the exception report says so plainly rather than quietly "
                "issuing three hundred and nine certificates and hoping. The "
                "client traces two to a different office and one to a member "
                "of staff who had left. Three hundred and eleven serialised "
                "certificates are issued; one exception is documented.",
            ),
            "mistakes": [
                "Issuing one certificate for a batch. Blanket certificates are "
                "not permitted, and a batch certificate cannot answer a "
                "question about one device.",
                "Acting as both operator and witness for a physical "
                "destruction. The certificate requires two distinct identities "
                "and the system will refuse.",
                "Recording a cryptographic erase without the key-destruction "
                "evidence. Destroying a key you cannot prove you destroyed is "
                "not destruction.",
                "Reconciling a bulk project by counting certificates. "
                "Reconciliation is against the client's declared asset list, "
                "and the discrepancies are the most valuable part of the "
                "report.",
                "Releasing a device for refurbishment when verification "
                "failed. Where erasure cannot be verified, physical "
                "destruction is mandatory — the device is lost, not the "
                "principle.",
            ],
            "caution": "No device proceeds to refurbishment, resale or recycling "
            "without a valid certificate bound to its own serial number. "
            "There is no override, and there should not be one. A resold "
            "laptop containing a customer's data would cost more than this "
            "gate has ever delayed.",
        },
        {
            "title": "Backup, archive and migration",
            "who": [
                (
                    "Mostly used by",
                    "The Technical Services Head and managed " "clients",
                ),
                ("Also relied on by", "M05, which watches the jobs run"),
                ("Where it happens", "Mostly on a schedule, mostly invisibly"),
            ],
            "intro": [
                "Ten functions covering the services sold to stop a recovery "
                "case ever being needed. The business plan names five backup "
                "types — cloud, on-site, hybrid, continuous data protection "
                "and archival — and M06 owns their definition and commercial "
                "shape while M05 monitors the jobs actually running.",
                "The function that earns the most trust is restore testing. A "
                "backup that reports success and has never been restored is a "
                "hope rather than a protection, and the specification is "
                "explicit that an untested backup is an unproven one. Tests "
                "are scheduled, executed and recorded, with the evidence "
                "supporting the customer's own continuity obligations.",
                "Migration sits here too, as a project with a scope, a "
                "checklist, and source-against-target verification signed off "
                "by the customer. Counting what went in and what came out "
                "sounds obvious and is the step most often skipped.",
            ],
            "features": [
                [
                    "Backup plan definition",
                    "Defines a customer's plan: scope, schedule, retention, "
                    "destination and encryption.",
                    "What is being protected is written down rather than assumed.",
                ],
                [
                    "Backup job monitoring",
                    "Monitors outcomes and raises an incident on failure or a "
                    "missed schedule.",
                    "A backup failing quietly for six weeks stops being " "possible.",
                ],
                [
                    "Restore testing",
                    "Schedules and records periodic restore tests with evidence.",
                    "The customer's continuity obligation is supported with " "proof.",
                ],
                [
                    "Capacity and usage billing",
                    "Meters storage consumed and provides the billing basis "
                    "against the subscription tier, with overage.",
                    "Growth in a customer's data becomes revenue rather than " "cost.",
                ],
                [
                    "Archival service",
                    "Manages long-term archival with retrieval service levels and "
                    "charging.",
                    "Old data is kept cheaply and can still be found.",
                ],
                [
                    "Continuous data protection",
                    "Tracks which assets are protected continuously and how much "
                    "they could lose.",
                    "The recovery point is a number rather than an assumption.",
                ],
                [
                    "Migration job",
                    "Manages device-to-device or platform migrations with scope, "
                    "checklist and verification.",
                    "A migration becomes a project rather than a weekend.",
                ],
                [
                    "Migration verification",
                    "Records source and target counts and integrity verification, "
                    "with customer sign-off.",
                    "Both parties agree that everything arrived.",
                ],
                [
                    "Backup storage provisioning",
                    "Provisions and tracks storage allocated per plan.",
                    "Capacity is planned rather than discovered.",
                ],
                [
                    "Restore request handling",
                    "Handles customer restore requests with a service level and "
                    "verification.",
                    "The moment the customer needs it is the moment it has to " "work.",
                ],
            ],
            "example": (
                "the restore test that found the gap",
                "A managed client's nightly backups have reported success for "
                "four months. The contract includes a quarterly restore test, "
                "which is scheduled and executed against a representative "
                "dataset. The restore fails. Investigation shows the backups "
                "were genuinely succeeding — but one of two database volumes "
                "was excluded from the job when the server was reconfigured in "
                "the spring, and nothing in a successful backup report reveals "
                "a volume that was never in scope. The job definition is "
                "corrected, a full backup is taken, and the restore test is "
                "repeated successfully the same week. The evidence goes to the "
                "client. Four months of backups had been worthless for that "
                "volume, and nothing except an actual restore would ever have "
                "shown it.",
            ),
            "mistakes": [
                "Reporting backup success as though it were protection. A "
                "successful job and a recoverable system are different "
                "claims.",
                "Letting a restore test slip because the client is busy. An "
                "untested backup is an unproven backup and the schedule exists "
                "because of it.",
                "Migrating without counting the source. Verification is "
                "source-against-target, and without a source count there is "
                "nothing to verify against.",
                "Provisioning storage informally as a customer grows. Metered "
                "capacity is the billing basis, and unmetered growth is "
                "unbilled revenue.",
            ],
        },
    ],
    # ============================================ 7. the journey
    "s6_title": "The journey of a data case",
    "s6_lede": "Twelve states from an anxious customer at a counter to a purge "
    "certificate — and one of them is the state most companies never "
    "reach.",
    "s6_intro": [
        "A data case runs longer than most records in this system and is "
        "watched more closely. It begins as soon as somebody hands over media "
        "and it does not end at handover — it ends when the company's copy has "
        "been destroyed and the destruction certified.",
        "That last part is the state most organisations never reach, because "
        "nobody remembers to delete anything. Here it is automatic, and "
        "reaching it is a measured target of one hundred per cent.",
    ],
    "journey": [
        ("Case opened", "Counter or a module", None),
        ("Media booked in", "Two signatories", "gate"),
        ("Evaluating", "Technician", None),
        ("Quoted", "System, from M36", None),
        ("Accepted", "Customer", "gate"),
        ("Imaging", "Technician", None),
        ("Recovering", "Technician", None),
        ("Verified", "Technician", None),
        ("Handed over", "Verified recipient", "gate"),
        ("Retention running", "System", None),
        ("Purged", "System", "certificate"),
        ("Closed", "System", None),
    ],
    "journey_title": "The path a data case follows",
    "journey_sub": (
        "Twelve states, and the case is not finished until the "
        "company's own copy is gone"
    ),
    "journey_caption": "The data case lifecycle, in the order it happens",
    "s6_stages": [
        [
            "Case opened",
            "A confidentiality-controlled record exists.",
            "A counter agent, or M14, M18 or a corporate project",
            "Nothing — but visibility is restricted from this moment.",
        ],
        [
            "Media booked in",
            "The physical media is in the lab.",
            "Two distinct authenticated signatories",
            "Dual signature. A single-signature attempt is rejected and " "recorded.",
        ],
        [
            "Evaluating",
            "A no-charge assessment is under way.",
            "Technician",
            "A recorded confidentiality undertaking and case-specific access.",
        ],
        [
            "Quoted",
            "The customer has a firm price.",
            "System, from M36",
            "The evaluation complete, with a recoverability judgement.",
        ],
        [
            "Accepted",
            "The customer has agreed.",
            "Customer",
            "Their acceptance. No chargeable work happens before it.",
        ],
        [
            "Imaging",
            "A copy is being taken.",
            "Technician",
            "Nothing — but work proceeds on the image, not the original.",
        ],
        [
            "Recovering",
            "The technique is being applied.",
            "Technician",
            "The methodology log recording each step and the operator.",
        ],
        [
            "Verified",
            "What was recovered has been checked.",
            "Technician",
            "An inventory by type, count and size. No names, no content.",
        ],
        [
            "Handed over",
            "The customer has their data.",
            "A verified recipient",
            "Identity verified and a signed receipt. The retention clock now "
            "starts.",
        ],
        [
            "Retention running",
            "We still hold a copy, for an agreed period.",
            "System",
            "Nothing — the purge date is already scheduled.",
        ],
        [
            "Purged",
            "Our copy is verifiably gone.",
            "System",
            "The window elapsing, with no documented hold in force.",
        ],
        [
            "Closed",
            "Everything is settled and certified.",
            "System",
            "A purge certificate issued. Case records are kept five years.",
        ],
    ],
    "s6_gates_intro": "Seven points refuse to proceed, and in this module every one of them "
    "is a hard block. There are no soft warnings in a "
    "confidentiality-critical process.",
    "gates": [
        (
            "Two signatures on the boundary",
            "Media entering or leaving the secure area requires two distinct "
            "authenticated signatures",
            "Two people",
        ),
        (
            "Undertaking before access",
            "A confidentiality undertaking is recorded per case before workspace "
            "access is granted",
            "Each individual",
        ),
        (
            "Work on an image",
            "Recovery is performed on an image, never the original media, "
            "wherever technically possible",
            "Technician",
        ),
        (
            "Acceptance before chargeable work",
            "The free evaluation and a firm quotation come before anything the "
            "customer pays for",
            "Customer",
        ),
        (
            "Verified recipient at handover",
            "Recovered data leaves only through the approved handover path, to a "
            "verified recipient with a signed receipt",
            "Technician",
        ),
        (
            "Purge unless a hold exists",
            "Data is purged automatically at the agreed date unless a documented, "
            "approved, time-limited hold applies",
            "System",
        ),
        (
            "Certificate before disposal",
            "No device proceeds to refurbishment, resale or recycling without a "
            "valid certificate bound to its serial number",
            "System",
        ),
    ],
    "s6_wrong_intro": "This module fails quietly or not at all. Every item below is "
    "something that would go unnoticed elsewhere and is surfaced here "
    "deliberately.",
    "s6_wrong": [
        [
            "Media booked in",
            "Somebody tries to move media alone because the second signatory is "
            "unavailable.",
            "The attempt is rejected and appears on the daily custody exception "
            "report.",
            "Find a second signatory. There is no version of this that works with "
            "one person.",
        ],
        [
            "Evaluating",
            "The case sits because the technician is on another job.",
            "The idle-case alert, and media held with no progress.",
            "Media in the lab with nothing happening is custody exposure with no "
            "revenue. Reassign or refer it out.",
        ],
        [
            "Imaging",
            "Work is attempted on the original to save time.",
            "The methodology log will show it.",
            "Nothing can undo it. This is the discipline that most determines "
            "whether a customer gets their data back.",
        ],
        [
            "Recovering",
            "The case is beyond internal capability.",
            "Attempts logged with no progress.",
            "Refer to a partner laboratory with custody continuity. Persisting is "
            "how originals get destroyed.",
        ],
        [
            "Handed over",
            "Data is copied somewhere convenient for the customer.",
            "An egress attempt outside the approved path is blocked, logged and "
            "alerted to security immediately.",
            "Use the approved handover path. This is one of the very few actions "
            "that alerts security in real time.",
        ],
        [
            "Retention running",
            "The window passes and the data is still held.",
            "The retention compliance report, daily.",
            "Purge it, or record a documented, approved, time-limited hold. The "
            "target for cases held past retention without a hold is zero.",
        ],
        [
            "Purged",
            "The automatic purge fails.",
            "It escalates immediately rather than retrying quietly.",
            "This is one of the few automations whose failure behaviour is "
            "immediate escalation. Treat it as an incident.",
        ],
        [
            "Destruction",
            "Erasure verification fails on a device due for refurbishment.",
            "The exception is routed automatically to physical destruction.",
            "Let it. The device is lost; releasing it unverified would lose "
            "something worth more.",
        ],
    ],
    "s6_note": "The case does not close at handover. It closes when 1000FiX's own "
    "copy has been purged and the purge certified — and that final state "
    "is the one that distinguishes a controlled process from a careful "
    "one.",
    # ============================================ 8. day in the life
    "s7_lede": "Five walkthroughs, from a law firm's failed array to three hundred "
    "laptops and a discrepancy nobody expected.",
    "s7_intro": [
        "Two of these describe money being earned and three describe risk "
        "being controlled. That ratio is roughly right for the module.",
        "Clients, media, figures and dates are illustrative. The standards, "
        "thresholds and rules behind them are exactly as the specification "
        "states them.",
    ],
    "scenarios": [
        {
            "title": "A RAID array recovered",
            "narrative": [
                "The highest-value case type in the lab, and the one that "
                "shows why imaging discipline matters more than technique.",
            ],
            "lanes": [
                (
                    "Customer",
                    [
                        (0, "Brings four drives to Gulshan"),
                        (2, "Accepts BDT 145,000, no recovery no fee"),
                        (4, "Verified partner signs for the data"),
                    ],
                ),
                ("Counter", [(0, "Opens a confidentiality-controlled case")]),
                (
                    "Technician",
                    [
                        (1, "Free evaluation over two days"),
                        (3, "Images all four; reconstructs the array"),
                    ],
                ),
                (
                    "System",
                    [
                        (0, "Restricts visibility from creation"),
                        (2, "Requests the quotation from M36"),
                        (4, "Starts the retention clock"),
                    ],
                ),
            ],
            "columns": ["Intake", "Evaluate", "Quote", "Recover", "Hand over"],
            "exhibit_title": "A RAID recovery, intake to handover in nine days",
            "exhibit_sub": "Imaged before anything was attempted",
            "caption": "The highest-value case the lab handles",
            "table": [
                [
                    "1",
                    "Customer and counter",
                    "A twelve-partner law firm loses a four-drive array holding "
                    "its document system. The case is opened at the counter with "
                    "criticality highest, and is confidentiality-controlled from "
                    "creation — the agent who opened it can see status and "
                    "nothing more.",
                ],
                [
                    "2",
                    "Technician",
                    "Free evaluation over two days: one drive has a head crash "
                    "needing the cleanroom, one has a firmware fault. "
                    "Recoverability assessed as probable.",
                ],
                [
                    "3",
                    "System and customer",
                    "A firm quotation of BDT 145,000 is issued on a no-recovery-"
                    "no-fee basis. The firm accepts. No chargeable work happened "
                    "before this point.",
                ],
                [
                    "4",
                    "Technician",
                    "All four drives are imaged before anything is attempted. The "
                    "head crash is addressed in the cleanroom, the firmware fault "
                    "logically, and the array is reconstructed from the images.",
                ],
                [
                    "5",
                    "Technician and customer",
                    "Inventory records four volumes, 1.9 TB and 412,000 files by "
                    "type — no file names. Handover on encrypted media to a "
                    "verified partner of the firm, with a signed receipt. Nine "
                    "days from intake.",
                ],
            ],
            "outcome": "The firm's document system came back. Just as importantly, "
            "nothing 1000FiX did during those nine days could have made "
            "the situation worse, because every attempt was made against "
            "an image. That discipline is the difference between a "
            "recovery service and an expensive gamble with somebody "
            "else's data.",
        },
        {
            "title": "The purge that nobody had to remember",
            "narrative": [
                "The least dramatic walkthrough in this library, and the one "
                "that most distinguishes a controlled process from a careful "
                "one.",
            ],
            "lanes": [
                (
                    "Customer",
                    [
                        (0, "Receives 340 GB on encrypted media"),
                        (3, "Receives the purge certificate"),
                    ],
                ),
                (
                    "System",
                    [
                        (0, "Starts a 30-day retention clock"),
                        (1, "Schedules the purge for the 11th"),
                        (2, "Executes; verifies destruction"),
                        (3, "Issues the certificate"),
                    ],
                ),
                (
                    "Quality manager",
                    [(2, "Sees it on the retention compliance " "report")],
                ),
            ],
            "columns": ["Handover", "Scheduled", "Purged", "Certified"],
            "exhibit_title": "A retention window that closed itself",
            "exhibit_sub": "Thirty days, then gone, with proof",
            "caption": "What happens after the customer has their data back",
            "table": [
                [
                    "1",
                    "Technician and customer",
                    "340 GB recovered from a failed laptop drive is handed over on "
                    "the 12th on encrypted media, to a verified recipient, with a "
                    "signed receipt.",
                ],
                [
                    "2",
                    "System",
                    "The agreed thirty-day retention window starts at handover. "
                    "The purge is scheduled for the 11th of the following month "
                    "at the moment of handover, not later.",
                ],
                [
                    "3",
                    "System",
                    "On that date the purge executes automatically. Destruction "
                    "is verified rather than assumed.",
                ],
                [
                    "4",
                    "System and customer",
                    "A purge certificate is issued to the customer and filed. The "
                    "customer receives a message telling them their data no "
                    "longer exists at 1000FiX.",
                ],
            ],
            "outcome": "Nobody remembered and nobody decided. For a customer who was "
            "anxious enough to pay for recovery, being told the copy is "
            "gone is a more reassuring message than most companies ever "
            "send — and for 1000FiX it is one fewer piece of somebody "
            "else's data sitting on a server for no reason.",
        },
        {
            "title": "Three hundred laptops and three that were missing",
            "narrative": [
                "A bulk decommissioning project, and the finding the client "
                "most needed was the one nobody was looking for.",
            ],
            "lanes": [
                (
                    "Client",
                    [
                        (0, "Declares 312 laptops across four offices"),
                        (4, "Traces the three missing machines"),
                    ],
                ),
                ("Logistics", [(1, "Collects under sealed custody over two " "weeks")]),
                (
                    "Lab",
                    [
                        (2, "291 erased and verified; 18 destroyed"),
                        (3, "311 serialised certificates issued"),
                    ],
                ),
                (
                    "System",
                    [
                        (3, "Reconciles against the declared list"),
                        (4, "Reports three unaccounted serials"),
                    ],
                ),
            ],
            "columns": [
                "Declared",
                "Collected",
                "Processed",
                "Certified",
                "Reconciled",
            ],
            "exhibit_title": "A bulk decommission and its exception report",
            "exhibit_sub": "Reconciliation against the client's own asset list",
            "caption": "Why the discrepancies are the valuable part",
            "table": [
                [
                    "1",
                    "Client",
                    "A bank decommissions three hundred and twelve laptops across "
                    "four offices. Their declared asset list is loaded into the "
                    "project.",
                ],
                [
                    "2",
                    "Logistics and lab",
                    "Collection runs over two weeks under sealed-container "
                    "custody. Each machine is booked into the lab under dual "
                    "signature.",
                ],
                [
                    "3",
                    "Lab",
                    "Two hundred and ninety-one drives take verified erasure and "
                    "survive, so the machines can be refurbished. Eighteen fail "
                    "verification and go to physical destruction, each with "
                    "photographic evidence and a witness who is not the "
                    "operator.",
                ],
                [
                    "4",
                    "System",
                    "Three hundred and eleven serialised certificates are issued, "
                    "each bound to one media serial number.",
                ],
                [
                    "5",
                    "System and client",
                    "Reconciliation against the declared list shows three serial "
                    "numbers declared and never received. The exception report "
                    "says so plainly. The client traces two to a different office "
                    "and one to a member of staff who had left.",
                ],
            ],
            "outcome": "The certificates were the deliverable; the exception report "
            "was the value. Three machines the bank believed had been "
            "decommissioned were still in circulation, and the only reason "
            "anybody found out is that reconciliation was against their "
            "declared list rather than against what happened to arrive.",
        },
        {
            "title": "An allegation answered in an afternoon",
            "narrative": [
                "The walkthrough that shows what the access logging is "
                "actually for, which is protecting honest people.",
            ],
            "lanes": [
                (
                    "Customer",
                    [(0, "Alleges recovered photographs have " "appeared elsewhere")],
                ),
                (
                    "Technical Services Head",
                    [(1, "Produces the access log for " "the case")],
                ),
                (
                    "System",
                    [
                        (1, "Three named individuals, every access " "timestamped"),
                        (2, "No export, no egress attempt, purged on day " "nine"),
                    ],
                ),
                (
                    "Quality manager",
                    [(3, "Files the evidence; closes the " "allegation")],
                ),
            ],
            "columns": ["Alleged", "Log produced", "Evidence", "Closed"],
            "exhibit_title": "An allegation of data misuse, answered from the "
            "record",
            "exhibit_sub": "Five years of immutable access logging, used once",
            "caption": "What the logging is really for",
            "table": [
                [
                    "1",
                    "Customer",
                    "Alleges that photographs recovered from their phone six "
                    "weeks earlier have appeared elsewhere, and names the "
                    "technician who handled the case.",
                ],
                [
                    "2",
                    "Technical Services Head",
                    "The access log for that case is produced. Three individuals "
                    "had access, each with a recorded confidentiality undertaking "
                    "for that specific case.",
                ],
                [
                    "3",
                    "System",
                    "Every access is timestamped with the action taken. The named "
                    "technician accessed the workspace four times, totalling "
                    "eleven hours, all within the recovery window, with no export "
                    "and no egress attempt.",
                ],
                [
                    "4",
                    "System",
                    "The recovered data was purged automatically nine days after "
                    "handover, with a purge certificate. The inventory shows "
                    "counts and sizes only; no file was ever named in the "
                    "system.",
                ],
                [
                    "5",
                    "Quality manager",
                    "The allegation is answered with evidence rather than "
                    "assurance, in an afternoon.",
                ],
            ],
            "outcome": "An honest technician's reputation was protected by a control "
            "that most people experience as an inconvenience. That is "
            "worth saying out loud when people find the access model "
            "restrictive: the log is the only thing standing between a "
            "serious allegation and a career.",
        },
        {
            "title": "A batch the system refused to release",
            "narrative": [
                "The gate doing its job, at the least convenient possible " "moment.",
            ],
            "lanes": [
                (
                    "Recycling",
                    [(0, "Assembles a batch of 30 machines"), (3, "Sends 26; holds 4")],
                ),
                ("Logistics", [(1, "Books a lorry for Thursday")]),
                ("System", [(2, "Blocks: 4 have no certificate")]),
                ("Data services", [(3, "Wipes and certifies the four")]),
            ],
            "columns": ["Assembled", "Booked", "Blocked", "Resolved"],
            "exhibit_title": "The transfer the gate would not allow",
            "exhibit_sub": "Four machines, no certificate, no movement",
            "caption": "A hard block preventing a data breach",
            "table": [
                [
                    "1",
                    "Recycling",
                    "Thirty decommissioned desktops are assembled into a batch "
                    "for a certified recycling partner.",
                ],
                ["2", "Logistics", "A collection is booked for Thursday morning."],
                [
                    "3",
                    "System",
                    "The movement is blocked. Four of the thirty have no valid "
                    "certificate of destruction. They were added to the batch "
                    "after the wiping run and never went through it.",
                ],
                [
                    "4",
                    "Data services and recycling",
                    "The four are removed from the consignment, wiped, verified "
                    "and certified, and travel with the following week's batch. "
                    "Twenty-six move as planned on Thursday.",
                ],
                [
                    "5",
                    "Quality",
                    "The near-miss is recorded, and the batch-assembly process is "
                    "changed so machines cannot be added after the wiping run.",
                ],
            ],
            "outcome": "Four hard drives holding a client's commercial data did not "
            "leave on a lorry to a scrap yard with a certificate on file "
            "saying they had been cleared. This is the kind of event that "
            "never appears in a benefits case, would have ended a "
            "corporate relationship, and is precisely why the gate has no "
            "override.",
        },
    ],
    "s9t_lede": "Five stories, and one idea running through all of them.",
    "s9t_intro": [
        "The walkthroughs covered a recovery, a purge, a bulk project, an "
        "allegation and a blocked transfer. Three of them describe something "
        "that did not happen, which is the honest shape of a "
        "confidentiality-critical module.",
        "The idea underneath all five is that the company should never have to "
        "rely on anybody's memory or good intentions about somebody else's "
        "data.",
    ],
    "s9t_table": [
        [
            "Prove it rather than assert it",
            "The allegation, the certificates, the purge certificate.",
            "'We handle data securely' is a claim. A five-year access log is "
            "evidence.",
        ],
        [
            "Automatic beats remembered",
            "The purge that happened without anybody deciding.",
            "Every organisation intends to delete data it no longer needs. Almost "
            "none actually does.",
        ],
        [
            "Blocks, not warnings",
            "The recycling batch, and the refurbishment gate.",
            "A warning about a missing certificate would have been dismissed by "
            "somebody with a lorry booked.",
        ],
        [
            "The discrepancy is the deliverable",
            "Three missing laptops in a bulk decommission.",
            "Reconciliation against the client's own list finds what "
            "reconciliation against arrivals never could.",
        ],
        [
            "Controls protect the controlled",
            "The technician cleared by the access log.",
            "The restrictions people find inconvenient are the same ones that "
            "answer an allegation in an afternoon.",
        ],
    ],
    "s9t_close": "Five of this module's twelve targets are zero or one hundred per "
    "cent, and that is deliberate: here a partial score is a control "
    "failure rather than a performance gap. Ninety-eight per cent of "
    "devices certified before disposal is not a good result — it is two "
    "per cent of devices leaving the building with somebody's data on "
    "them.",
    # ============================================ 10. rules
    "s8_lede": "Eighteen rules, seventeen of them hard blocks. This is the least "
    "discretionary module in the entire system.",
    "s8_intro": [
        "There is almost no judgement in this module, and that is the design. "
        "Where every other part of the ERP balances control against speed, "
        "here the balance is settled in advance and always the same way. A "
        "single failure is a regulatory incident.",
        "Three of the rules below deserve particular attention because they "
        "are absolute in ways people find surprising. Recovered customer data "
        "is never used as training data for any model. Recovered data and its "
        "index are held in a Bangladesh-resident store and may not be "
        "replicated abroad. And no device proceeds to refurbishment, resale or "
        "recycling without a valid certificate — with no override at any "
        "level.",
    ],
    "s8_rules": [
        [
            "Move media in or out of the secure area on one signature",
            "One person alone with somebody else's media is the situation the "
            "whole custody regime exists to prevent.",
            "Find a second signatory. There is no version of this that works "
            "otherwise.",
        ],
        [
            "Open a case you have not been assigned to",
            "Access by role would mean everybody in a job title could read "
            "everybody's data.",
            "Ask to be assigned. It takes a moment and it is recorded, which is "
            "the point.",
        ],
        [
            "Access a workspace without your access being logged",
            "The log is what answers an allegation, and it protects you.",
            "Nothing — it is automatic and immutable, and kept for five years.",
        ],
        [
            "Work on the original media when an image is possible",
            "A failed attempt on an original is often the end of the customer's "
            "only chance.",
            "Image first. The two hours it costs are the cheapest insurance in "
            "the lab.",
        ],
        [
            "Hold recovered data unencrypted",
            "Data at rest without a case-specific key is data anybody with "
            "storage access can read.",
            "Nothing — encryption with a case-specific key is applied "
            "automatically.",
        ],
        [
            "Keep recovered data past the agreed window",
            "Held data is pure liability once the customer has their copy.",
            "Let the automatic purge run, or record a documented, approved, "
            "time-limited hold.",
        ],
        [
            "Move recovered data out except through the approved handover path",
            "Any other route is an uncontrolled copy of somebody's information.",
            "Use the handover path. An egress attempt elsewhere is blocked, "
            "logged and alerts security immediately.",
        ],
        [
            "Choose a sanitisation technique by habit",
            "The right method depends on confidentiality, media type and where "
            "the device is going next.",
            "Follow the documented sanitisation programme. It is a matrix, not a "
            "preference.",
        ],
        [
            "Hold recovered data outside Bangladesh",
            "Data residency is a legal requirement under the Personal Data "
            "Protection Act 2026.",
            "Nothing — the store is resident by design. But never work around it "
            "with a personal copy.",
        ],
        [
            "Handle a breach informally",
            "A breach affecting customer data must be assessed and, above the "
            "threshold, notified to the regulator.",
            "Report it immediately. Assessment is not your judgement to make " "alone.",
        ],
        [
            "Destroy the case record when the data is purged",
            "The processing record is retained for five years independently of "
            "the data itself.",
            "Nothing — the two are separate by design.",
        ],
        [
            "Release a device for refurbishment, resale or recycling without a "
            "certificate",
            "A resold or scrapped device containing customer data is the failure "
            "this module exists to prevent.",
            "Get the certificate. There is no override at any level, including "
            "director.",
        ],
        [
            "Refurbish a device whose erasure could not be verified",
            "Unverified erasure is not erasure.",
            "Physical destruction is mandatory. The device is lost; the principle "
            "is not.",
        ],
        [
            "Issue a certificate covering a batch",
            "A batch certificate cannot answer a question about one device.",
            "Issue one per media serial number. Blanket certificates are not "
            "permitted.",
        ],
        [
            "Access a case before recording the confidentiality undertaking",
            "A general policy nobody remembers signing is not an obligation.",
            "Record the undertaking. It is per case and it takes seconds.",
        ],
        [
            "Discuss case detail with anybody outside the authorised path",
            "A helpful remark is the commonest way confidentiality actually " "fails.",
            "Communicate only through authorised roles, only to the verified "
            "customer contact.",
        ],
        [
            "Use recovered customer data to train a model",
            "It is somebody else's information and they did not consent to that.",
            "Nothing — it is prohibited absolutely and there is no legitimate "
            "exception.",
        ],
        [
            "Refer a case to a partner laboratory informally",
            "Custody has to be continuous even when the work leaves the " "building.",
            "Use the referral process: a signed confidentiality agreement and "
            "continuous custody documentation.",
        ],
    ],
    "s8_note": "There is one approved-override rule in this module and seventeen hard "
    "blocks. If a hard block is genuinely obstructing legitimate work, "
    "raise it through Appendix B — but be aware that in this module the "
    "answer is more often 'the work needs to change' than 'the rule needs "
    "to change'.",
    # ============================================ 11. automation
    "s9_lede": "Fourteen behaviours that run without anybody asking, and several of "
    "them exist to stop something rather than to do something.",
    "s9_intro": [
        "In most modules automation saves effort. Here a good deal of it "
        "removes the possibility of forgetting. The purge that happens at the "
        "agreed date, the block on a device with no certificate, the immediate "
        "alert on an egress attempt — none of those makes anybody's day "
        "easier, and all of them make the module trustworthy.",
        "Two of the failure behaviours are worth noting because they differ "
        "from the rest of the system. When the automatic purge fails, it "
        "escalates immediately rather than retrying quietly. And when a wipe "
        "request cannot be fulfilled, the source module is blocked rather than "
        "warned.",
    ],
    "automation_groups": [
        (
            "Controlling access and custody",
            3,
            "Classification applied, undertakings required, dual signature " "enforced",
        ),
        (
            "Moving the case along",
            4,
            "Evaluation to quotation, release to imaging, inventory, handover",
        ),
        (
            "Retention and destruction",
            4,
            "Retention clock, automatic purge, certificate issue, verification "
            "failure routing",
        ),
        (
            "Watching for trouble",
            3,
            "Idle cases, backup failures, restore tests and blocked egress",
        ),
    ],
    "s9_table": [
        [
            "Applies the confidentiality classification, restricts visibility and "
            "requires staff undertakings before access",
            "A data case is opened",
            "Nobody, which is the point — visibility is restricted from " "creation",
        ],
        [
            "Requires dual signature, generates a seal record and opens the "
            "custody ledger for the item",
            "Media is booked in",
            "Both signatories, and the custody record",
        ],
        [
            "Produces the recoverability assessment, requests a quotation and "
            "notifies the customer",
            "An evaluation completes",
            "The customer, with a firm price",
        ],
        [
            "Releases the case to imaging and schedules the cleanroom if it is "
            "needed",
            "The customer accepts the quotation",
            "The technician and the cleanroom schedule",
        ],
        [
            "Generates the inventory as metadata only and notifies the customer "
            "that data is ready",
            "Recovery completes",
            "The customer",
        ],
        [
            "Starts the retention clock and schedules the automatic purge",
            "Handover completes",
            "Nobody — but the purge date is now fixed",
        ],
        [
            "Executes the purge, verifies destruction, issues the certificate and "
            "notifies the customer",
            "The retention window elapses",
            "The customer. If it fails, it escalates immediately",
        ],
        [
            "Selects the method by confidentiality and disposition and queues the "
            "work",
            "A wipe request arrives from refurbishment or recycling",
            "The lab. If it cannot be fulfilled, the source module is blocked",
        ],
        [
            "Issues the serialised certificate, publishes it to the gate and "
            "files it",
            "Destruction is verified",
            "Refurbishment, recycling, and the client",
        ],
        [
            "Routes to physical destruction, notifies the requester and records "
            "the exception",
            "Erasure verification fails",
            "The quality manager and the requesting module",
        ],
        [
            "Raises a priority incident and notifies the customer and account "
            "manager",
            "A backup job fails twice consecutively",
            "The customer, immediately",
        ],
        [
            "Schedules, executes, records and publishes the evidence",
            "A restore test falls due",
            "The customer. An untested backup is an unproven backup",
        ],
        [
            "Alerts the Technical Services Head",
            "A case is idle beyond the threshold",
            "The lab — media held without progress is custody risk",
        ],
        [
            "Blocks, logs and alerts security immediately",
            "An attempt is made to move data outside the approved path",
            "Security, in real time",
        ],
    ],
    # ============================================ 12. permissions
    "s10_lede": "The strictest permission model in the ERP. Role membership grants "
    "nothing; access is per case, per person, and always logged.",
    "s10_intro": [
        "Everywhere else in this system, holding a role gives you access to a "
        "class of records. Here it does not. A data services technician holds "
        "a role that allows them to work on cases, and it gives them access to "
        "no cases at all until they are individually assigned to one and have "
        "recorded a confidentiality undertaking for it.",
        "The clearest illustration is the IT administrator. They can "
        "administer the platform — the servers, the storage, the "
        "configuration — and they have no path into a case workspace "
        "whatsoever. The Chief Technology Officer can gain access for an "
        "investigation, with explicit approval, and that access is logged like "
        "everybody else's.",
        "The other restriction worth understanding is that the "
        "recovered-data inventory records type, count and size only. File "
        "names and content are not stored in the ERP at all — not restricted, "
        "not encrypted, not stored. There is nothing to leak.",
    ],
    "permissions": {
        "roles": [
            "Technical Services Head",
            "Chief Technology Officer",
            "Data Services Technician",
            "Quality Manager",
            "Service Centre Agent",
            "Contact Centre Agent",
            "Finance Manager",
            "IT Administrator",
            "Customer",
            "Corporate Portal User",
        ],
        "actions": [
            "Open a case",
            "Enter a case workspace",
            "Sign media in or out",
            "Issue a certificate",
            "See custody and access records",
            "See case content",
        ],
        "marks": [
            ["y", "y", "y", "y", "y", "y"],  # Technical Services Head
            ["", "a", "", "", "y", "a"],  # Chief Technology Officer
            ["", "y", "y", "y", "", "y"],  # Data Services Technician
            ["", "", "", "", "y", ""],  # Quality Manager
            ["y", "", "", "", "", ""],  # Service Centre Agent
            ["", "", "", "", "", ""],  # Contact Centre Agent
            ["", "", "", "", "", ""],  # Finance Manager
            ["", "", "", "", "", ""],  # IT Administrator
            ["", "", "", "", "", ""],  # Customer
            ["", "", "", "", "", ""],  # Corporate Portal User
        ],
        "sub": "Note that a technician's access applies only to their own "
        "assigned cases",
    },
    "s10_roles": [
        [
            "Data services technician",
            "Doing the work in the lab",
            "Nothing exclusive — and access only to cases they are individually "
            "assigned to",
        ],
        [
            "Technical Services Head",
            "Running the lab",
            "Access to all cases, with every access logged like anybody else's",
        ],
        [
            "Quality manager",
            "Audit and control",
            "Seeing custody, certificates and exceptions — and never case " "content",
        ],
        [
            "Chief Technology Officer",
            "Investigation",
            "Access to a case with explicit approval, logged, for investigation "
            "only",
        ],
        [
            "Service centre agent",
            "Opening a case at the counter",
            "Creating a case and reading its status. No workspace access",
        ],
        ["Contact centre agent", "Answering a status enquiry", "Status only"],
        [
            "Finance manager",
            "Costing and billing",
            "Billable events and case costing, with no case detail",
        ],
        [
            "IT administrator",
            "Keeping the platform running",
            "Nothing inside a case workspace. This is the point",
        ],
        [
            "Customer",
            "Knowing where their case is",
            "Their own case status and their own certificates",
        ],
        [
            "Corporate portal user",
            "Reconciling a decommissioning project",
            "Their own organisation's project and certificates",
        ],
    ],
    "s10_restrictions_intro": "Five restrictions define this module. Three of them exist nowhere "
    "else in the system.",
    "s10_restrictions": [
        [
            "Case workspace access",
            "Named, case-assigned, multi-factor-authenticated individuals only. "
            "Role membership grants nothing.",
            "Access by role would mean everybody with a job title could read "
            "everybody's data. This is the central control of the module.",
        ],
        [
            "The IT administrator",
            "No access to any case workspace, at all.",
            "The person who can administer the platform is the person best placed "
            "to bypass its controls. Removing the path entirely is the only "
            "reliable answer.",
        ],
        [
            "File names and content",
            "Not stored in the ERP. The inventory records type, count and size "
            "only.",
            "The safest way to protect information is not to hold it. There is "
            "nothing to leak because there is nothing there.",
        ],
        [
            "Access logging",
            "Every access, immutably, retained for five years.",
            "It answers allegations, satisfies audits and protects honest "
            "technicians. It is not optional and it cannot be turned off.",
        ],
        [
            "Segregation on destruction",
            "The operator performing a destruction cannot be the witness.",
            "A certificate requires two distinct identities, because a witness "
            "who is also the operator is not a witness.",
        ],
    ],
    "s10_note": "If you can open a case you were not assigned to, or if you find you "
    "can read a file name anywhere in the system, stop and report it "
    "within the hour. Those are the two most serious defects this module "
    "could have.",
    # ============================================ 13. measurement
    "s11_lede": "Eleven reports and twelve measures — and five of the measures are "
    "zero or one hundred per cent, because a partial score here is a "
    "control failure.",
    "s11_intro": [
        "The specification is explicit about this and it is worth repeating. "
        "Five of the twelve targets in this module are absolutes. Chain of "
        "custody exceptions: zero. Certificates issued within twenty-four "
        "hours: one hundred per cent. Cases purged on schedule: one hundred "
        "per cent. Unauthorised access attempts: zero. Devices released to "
        "refurbishment or recycling without a certificate: zero.",
        "Those are not stretch targets. Ninety-eight per cent of devices "
        "certified before disposal means two per cent of devices left the "
        "building with somebody's data on them, which is not a good "
        "performance — it is a breach that has already happened and has not "
        "yet been noticed.",
    ],
    "s11_reports": [
        [
            "Case board",
            "Open cases by state, age, criticality and where the media physically "
            "is",
            "The data services team, continuously",
        ],
        [
            "Custody exception report",
            "Single-signature attempts, seal breaks, unaccounted media and "
            "overdue purges",
            "Quality and the Technical Services Head, daily",
        ],
        [
            "Access audit report",
            "Who accessed which case, when, and what they did, with anomaly flags",
            "The CTO and governance, weekly",
        ],
        [
            "Retention compliance",
            "Cases approaching or past their purge date",
            "The Quality Manager, daily",
        ],
        [
            "Destruction certificate register",
            "Every certificate by period, client, method and media serial",
            "Quality and corporate clients, on demand",
        ],
        [
            "Recovery success rate",
            "Success by media type, failure mode and technique",
            "The Technical Services Head, monthly",
        ],
        [
            "Case turnaround",
            "Evaluation-to-quotation and quotation-to-handover times",
            "The Technical Services Head, monthly",
        ],
        [
            "Case profitability",
            "Revenue against labour, consumables, equipment and partner cost",
            "The CFO and Technical Services Head, monthly",
        ],
        [
            "Backup service health",
            "Job success rates, consecutive failures and restore test currency",
            "Technical services, weekly",
        ],
        [
            "Bulk decommission reconciliation",
            "Declared assets against certificates issued, with the exceptions",
            "The corporate client and account manager, per project",
        ],
        [
            "ISO evidence pack",
            "Custody, access, retention, destruction and undertaking records for "
            "a period",
            "Quality and the auditor, per audit",
        ],
    ],
    "s11_kpis": [
        [
            "Recovery success rate on accepted cases",
            "How often the lab gets the data back",
            "Above 82 per cent. Not currently measured",
        ],
        [
            "Chain-of-custody exceptions",
            "Any break in the custody record",
            "Zero. Absolute",
        ],
        [
            "Average recovery turnaround",
            "How long a customer waits",
            "Under 7 days. Not currently measured",
        ],
        [
            "Certificates issued within 24 hours of destruction",
            "Whether the gate for other modules opens promptly",
            "100 per cent. Absolute",
        ],
        [
            "Cases purged on schedule",
            "Whether the company stops holding data it should not",
            "100 per cent. Absolute",
        ],
        [
            "Cases held past retention without a documented hold",
            "Data retained with no lawful basis",
            "Zero. Absolute",
        ],
        [
            "Unauthorised access attempts to a case workspace",
            "Whether anybody is trying doors that should be locked",
            "Zero. Absolute",
        ],
        [
            "Devices released to refurbishment or recycling without a certificate",
            "The failure this module exists to prevent",
            "Zero. Absolute",
        ],
        [
            "Backup job success rate for managed customers",
            "Whether the protection service works",
            "Above 99 per cent",
        ],
        [
            "Restore tests completed on schedule",
            "Whether the protection is proven rather than assumed",
            "100 per cent",
        ],
        [
            "Data services gross margin",
            "Whether the service line makes money",
            "Above 55 per cent",
        ],
        [
            "Bulk decommission reconciliation accuracy",
            "Whether a client's declared list matches what was certified",
            "100 per cent",
        ],
    ],
    "dials": [
        ("Certificates issued within 24 hours", "100%", 1.0),
        ("Cases purged on schedule", "100%", 1.0),
        ("Recovery success on accepted cases", ">82%", 0.82),
        ("Custody exceptions, against a ceiling of zero", "0", 1.0),
    ],
    "s11_reading_title": "Reading the custody exception report",
    "s11_reading": [
        "This is a daily report that should be empty, and the discipline is to "
        "read it every day precisely because it usually is. A report that is "
        "always blank stops being read, and the day it is not blank is the day "
        "it matters.",
        "Four things appear on it: single-signature attempts, seal breaks, "
        "unaccounted media and overdue purges. Each of them means something "
        "different and each has a different urgency.",
    ],
    "s11_reading_table": [
        [
            "A single-signature attempt",
            "Somebody tried to move media alone. Usually the second signatory was "
            "unavailable.",
            "Talk to the person the same day. Repeated attempts by the same "
            "individual are a different conversation from occasional ones across "
            "the team.",
        ],
        [
            "A seal break",
            "A container was opened outside a recorded step.",
            "Investigate before anything else on the report. This is the one that "
            "could mean something serious.",
        ],
        [
            "Unaccounted media",
            "An item is not where the ledger says it should be.",
            "Stop and find it. Nothing else on the report matters until this is "
            "resolved.",
        ],
        [
            "An overdue purge",
            "Data is being held past its window with no documented hold.",
            "Purge it today, or record a proper hold. The target is zero and "
            "there is no acceptable backlog.",
        ],
        [
            "An idle case alert",
            "Media is in the lab with nothing happening to it.",
            "Reassign, refer out, or return the media. Custody exposure with no "
            "revenue is the worst combination.",
        ],
        [
            "Several exceptions on the same day",
            "Usually a staffing gap rather than a discipline problem.",
            "Look at the rota before looking at the people. Dual control fails "
            "when there is nobody to be the second person.",
        ],
    ],
    # ============================================ 14. neighbours
    "s12_lede": "M06 gates two business lines and is trusted by every corporate "
    "client. Nine modules supply it and ten depend on it.",
    "s12_intro": [
        "The most important relationships here are the two gates. M14 "
        "refurbishment cannot start work on a device without a certificate "
        "from M06, and M18 recycling cannot transfer one to a partner without "
        "one. M03 logistics enforces the second gate physically by refusing to "
        "move the item.",
        "Those three modules together form a control no single one could "
        "enforce alone: the module that issues the certificate is not the "
        "module that wants to move the device, and the module that moves it "
        "cannot issue the certificate.",
    ],
    "s12_upstream": [
        [
            "M01 Service Request",
            "The parent service order and the customer " "relationship",
            "There is no customer-facing view of a data case",
        ],
        [
            "M17 Asset Registry",
            "The identity of the media and device",
            "Certificates cannot bind to a serial number",
        ],
        [
            "M03 Logistics",
            "Custody in transit, and the shared custody ledger",
            "The chain breaks the moment media leaves the lab",
        ],
        [
            "M33 Party Master",
            "Who the customer is and who may receive data",
            "Handover cannot verify a recipient",
        ],
        [
            "M29 Identity",
            "Authentication, multi-factor and the key service",
            "Access control and encryption both fail",
        ],
        [
            "M36 Quotation",
            "The firm price after evaluation",
            "Recovery cannot be quoted and no-recovery-no-fee has no basis",
        ],
        [
            "M24 Records",
            "Retention schedules and certificate filing",
            "Certificates and case records have no governed retention",
        ],
        [
            "M05 Managed Services",
            "Backup job execution outcomes",
            "Backup monitoring has nothing to monitor",
        ],
        [
            "M60 Security",
            "Incident response when something goes wrong",
            "A detected breach has nowhere to go",
        ],
    ],
    "s12_downstream": [
        [
            "M14 Refurbishment",
            "The certificate that lets work begin",
            "Refurbishment cannot lawfully operate at all",
        ],
        [
            "M18 Recycling",
            "The certificate that lets a device be transferred",
            "Recycling cannot lawfully operate at all",
        ],
        [
            "M03 Logistics",
            "The certificate check before a recycling movement",
            "The physical gate has nothing to check",
        ],
        [
            "M01 Service Request",
            "Case status for the customer-facing view",
            "The customer cannot be told where their data case is",
        ],
        [
            "M20 Receivables",
            "Billable events for recovery, backup and " "destruction",
            "Data services work is not billed",
        ],
        [
            "M39 Recurring Billing",
            "Metered backup capacity",
            "Subscription billing has no consumption basis",
        ],
        [
            "M24 Records",
            "Certificates and case records for retention",
            "Evidence is not governed or disposed of properly",
        ],
        [
            "M23 Quality",
            "Custody exceptions and control failures",
            "Data handling quality becomes invisible",
        ],
        [
            "P04 Corporate Portal",
            "Decommissioning projects and certificates",
            "Corporate clients cannot reconcile their own projects",
        ],
        [
            "M07 Sales",
            "The documented process a tender response needs",
            "Bids requiring evidenced data handling cannot be answered",
        ],
    ],
    "s12_close_up": [
        {
            "title": "The gate that makes two business lines lawful: M06, M14 "
            "and M18",
            "text": [
                "Refurbishment and recycling are both revenue lines, and both "
                "involve a device leaving 1000FiX's control with whatever its "
                "previous owner left on it. The specification attaches BDT 65 "
                "lac a year to refurbishment and BDT 12 lac to recycling, and "
                "neither figure is available without certified destruction.",
                "The control works because of who holds each piece. M06 issues "
                "the certificate and has no commercial interest in the device "
                "moving. M14 and M18 want the device to move and cannot issue "
                "the certificate. M03 physically carries it and will not do so "
                "without seeing one. No single module can complete the chain "
                "alone, and no single person's judgement under time pressure "
                "can shortcut it.",
                "That is why the block has no override. An override would mean "
                "the whole structure reduces to one person's decision at the "
                "moment they are least placed to make it — with a lorry "
                "booked, a client waiting, and a batch already assembled.",
            ],
        },
        {
            "title": "The separation that protects the technician: M06 and "
            "M29 Identity",
            "text": [
                "M06 does not operate its own authentication or key "
                "management; it uses the platform's. That sounds like a "
                "technical convenience and it is actually a control.",
                "If this module ran its own access control, the people who "
                "administer it would be able to grant themselves access to "
                "cases. Because it uses the platform service, and because the "
                "platform's own administrators are explicitly denied any path "
                "into a case workspace, there is no role anywhere in the "
                "company that can quietly acquire access to somebody's "
                "recovered data.",
                "The same separation is what makes the access log credible. A "
                "log maintained by the same system whose access it records is "
                "worth considerably less than one that is immutable and "
                "independently retained. When a technician is accused of "
                "misusing customer data, the thing that clears them is a "
                "record nobody in the lab could have altered.",
            ],
        },
    ],
    "s12_note": "M06 is the only module in the system where the correct answer to "
    "'can we make an exception?' is always no. Every other module has "
    "approved-override rules; this one has seventeen hard blocks and a "
    "single override, and that override only permits a documented, "
    "time-limited retention hold.",
    # ============================================ 15. troubleshooting
    "s13_lede": "What goes wrong with data work, what it usually means, and — in this "
    "module more than any other — what not to do about it.",
    "s13_intro": [
        "Almost every item below is a control working correctly. The right "
        "response is nearly always to satisfy the control rather than to find "
        "a way past it, and in several cases attempting the second is itself a "
        "reportable event.",
    ],
    "s13_troubleshooting": [
        [
            "I cannot get media out of the secure area",
            "The second signatory is unavailable.",
            "Find one. A single-signature attempt is recorded as a custody "
            "exception, so the attempt costs more than the wait.",
        ],
        [
            "I cannot open a case I need to work on",
            "You have not been assigned to it, or the confidentiality undertaking "
            "is not recorded.",
            "Ask to be assigned and record the undertaking. Both take seconds and "
            "both are the point.",
        ],
        [
            "A colleague needs to see something in my case",
            "Access is per named individual.",
            "Have them assigned. Never share a session — the log will show your "
            "identity doing their work.",
        ],
        [
            "The recovery is failing and I want to try on the original",
            "Working on the original is a hard rule wherever imaging is "
            "technically possible.",
            "If imaging genuinely is not possible, that is a decision for the "
            "Technical Services Head, recorded in the methodology log.",
        ],
        [
            "The case is beyond our capability",
            "Some failures need equipment 1000FiX does not have.",
            "Refer to a partner laboratory through the referral process, with a "
            "signed confidentiality agreement and continuous custody. Persisting "
            "risks the original.",
        ],
        [
            "The purge date has arrived and the customer wants more time",
            "Only a documented, approved, time-limited hold can delay it.",
            "Record the hold properly, or let the purge run. An informal "
            "extension has no lawful basis.",
        ],
        [
            "The automatic purge failed",
            "This escalates immediately rather than retrying quietly.",
            "Treat it as an incident, not a backlog item. It is one of the very "
            "few automations whose failure behaviour is immediate escalation.",
        ],
        [
            "Erasure verification failed on a device due for refurbishment",
            "Unverified erasure is not erasure.",
            "Physical destruction is mandatory. The device is lost; do not "
            "release it.",
        ],
        [
            "Refurbishment says they cannot start",
            "There is no valid certificate bound to that media serial.",
            "Issue one, or explain why it cannot be issued. There is no override "
            "at any level.",
        ],
        [
            "A bulk project's numbers do not add up",
            "Reconciliation is against the client's declared asset list, not "
            "against what arrived.",
            "That discrepancy is the most valuable output of the project. Report "
            "it plainly rather than reconciling to the arrivals.",
        ],
        [
            "I need to send recovered data to the customer's own cloud",
            "Recovered data may not leave except through the approved handover "
            "path.",
            "Use the approved path. An egress attempt elsewhere is blocked and "
            "alerts security in real time.",
        ],
        [
            "A customer alleges their recovered data has been misused",
            "The access log answers this.",
            "Escalate to the Technical Services Head. Do not investigate "
            "informally — the log is the evidence and it should be produced "
            "properly.",
        ],
    ],
    "s13_faq": [
        [
            "Why can I not see other cases?",
            "Because access by role would mean everybody with your job title "
            "could read everybody's recovered data. Access is per case, per "
            "person, and always logged.",
        ],
        [
            "Does the company know what is in the data it recovers?",
            "No. The inventory records type, count and size. File names and "
            "content are not stored in the ERP at all — there is nothing to "
            "leak.",
        ],
        [
            "What happens to my copy after the customer has theirs?",
            "It is purged automatically at the agreed date, verified, and a purge "
            "certificate is issued to the customer.",
        ],
        [
            "Can a director authorise a device to go for recycling without a "
            "certificate?",
            "No. There is no override at any level. The gate exists precisely "
            "because somebody under pressure would otherwise authorise it.",
        ],
        [
            "Why does physical destruction need a witness?",
            "Because a certificate requires two distinct identities. An operator "
            "who is also the witness has witnessed nothing.",
        ],
        [
            "Can recovered data be used to improve our recovery techniques?",
            "No. Recovered customer data is never used as training data for any "
            "model. There is no legitimate exception.",
        ],
        [
            "Where is recovered data physically held?",
            "In a Bangladesh-resident store. It may not be replicated to a "
            "foreign region, under the Personal Data Protection Act 2026.",
        ],
        [
            "How long are case records kept?",
            "Five years, as processing records — independently of the purge of "
            "the data itself. The two are deliberately separate.",
        ],
        [
            "What is the difference between erasure and destruction?",
            "Erasure makes the data unrecoverable and the device survives, so it "
            "can be resold. Destruction is physical and the device does not. "
            "Erasure is preferred where it can be verified.",
        ],
        [
            "Why is a batch certificate not acceptable?",
            "Because it cannot answer a question about one device, and a "
            "corporate client's question is always about one device.",
        ],
    ],
    # ============================================ 16. worth
    "s14_lede": "BDT 30 lac a year of its own, and BDT 77 lac a year that two other "
    "business lines cannot earn without it.",
    "s14_intro": [
        "The direct revenue is modest by the standards of this programme: "
        "about BDT 30 lac a year at steady state from data recovery, backup "
        "subscriptions and destruction services. The enabling value is larger. "
        "Refurbishment cannot lawfully operate without certified destruction, "
        "and neither can recycling, and between them the specification puts "
        "BDT 77 lac a year on those two lines.",
        "The third category of value cannot be quantified and is probably the "
        "largest. A single publicised incident of a resold device containing a "
        "customer's data would cost more than this module costs to build. The "
        "company already advertises that a customer's device and data are one "
        "hundred per cent secure; M06 is what makes that statement defensible "
        "rather than aspirational.",
    ],
    "benefits": [
        ("Business lines it makes lawful", 77, "BDT 77 lac/yr, elsewhere"),
        ("Data services revenue", 30, "BDT 30 lac/yr"),
    ],
    "benefits_note": (
        "Avoided breach cost is material and deliberately not "
        "quantified — a single incident would exceed both."
    ),
    "s14_benefits": [
        [
            "Data services revenue",
            "A deliverable, chargeable service line with consistent pricing and "
            "measured success",
            "BDT 30 lac a year at steady state",
        ],
        [
            "Backup subscription revenue",
            "Recurring revenue with metered capacity billing",
            "Included in the above, and it grows with the managed-services base",
        ],
        [
            "Refurbishment made lawful",
            "M14 cannot legally operate without certified destruction",
            "A precondition for BDT 65 lac a year",
        ],
        [
            "Recycling made lawful",
            "M18 cannot transfer to a recycler without it",
            "A precondition for BDT 12 lac a year",
        ],
        [
            "Corporate decommissioning contracts",
            "Bulk decommissioning with per-device certification is saleable to "
            "every corporate client",
            "A new revenue line, sized after Wave 6",
        ],
        [
            "Tender qualification",
            "Corporate and government tenders increasingly require documented "
            "data handling",
            "Removes a disqualifier from bids the company currently cannot win",
        ],
        [
            "Avoided breach cost",
            "A single publicised incident of a resold device containing customer "
            "data",
            "Would cost more than the module. Deliberately not quantified",
        ],
    ],
    "s14_soft": [
        [
            "It makes the published claim true",
            "The company already advertises '100 per cent secure — your device "
            "and data are secure'. M06 is what makes that defensible rather than "
            "aspirational, which matters because the claim is already being "
            "made.",
        ],
        [
            "ISO 27001 readiness",
            "Media handling, secure disposal, access control and logging are "
            "among the most heavily tested controls in the standard.",
        ],
        [
            "A defensible position under the data protection law",
            "Documented consent, access control, retention limits, residency and "
            "destruction evidence are the practical requirements of the Personal "
            "Data Protection Act 2026.",
        ],
        [
            "Trust at the highest-anxiety moment",
            "A customer handing over a failed drive with their business on it is "
            "at their most anxious. Visible process is what converts anxiety into "
            "loyalty.",
        ],
        [
            "Protection for honest staff",
            "Named access and immutable logging protect technicians from "
            "suspicion when a customer alleges misuse — which, at volume, will "
            "eventually happen.",
        ],
        [
            "Better insurance and liability terms",
            "A documented process materially improves professional indemnity " "terms.",
        ],
        [
            "A moat competitors will not casually copy",
            "Building this properly takes discipline rather than money, which is "
            "why most local competitors will not do it.",
        ],
    ],
    "s14_close": "This is the module where the right measure of success is that nothing "
    "happened. No device left the building uncertified, no case was held "
    "past its window, no unauthorised access was attempted, and every "
    "certificate was issued within a day. Five of the twelve targets are "
    "zero or one hundred per cent because, in this module, anything else "
    "is a failure that has already occurred.",
    # ============================================ 17. learning it
    "s17_lede": "A fortnight for a technician, and about twenty minutes for anybody "
    "who only needs to know why the gate will stop them.",
    "s17_intro": [
        "M06 has the smallest user population in Category A and the steepest "
        "requirements for the people inside it. A data services technician "
        "needs to understand custody, access discipline, imaging, methodology "
        "logging, retention and destruction standards.",
        "Almost everybody else needs one thing: an understanding of why a "
        "certificate is required before a device can be refurbished, recycled "
        "or resold, and that there is no way around it. That is section 1 and "
        "section 6.4, and it takes twenty minutes.",
    ],
    "s17_plan": [
        [
            "Everybody, before you start",
            "Read section 1, then section 6.4 on destruction, then the rules in "
            "section 10.",
            "20 minutes",
            "Understand the gate and why it has no override",
        ],
        [
            "Technicians, day one",
            "Read sections 6.2 and 6.3 in full — custody, access and retention. "
            "These come before any technical training.",
            "1 hour",
            "Know what you may and may not touch",
        ],
        [
            "Technicians, day one, afternoon",
            "Shadow a media book-in under dual signature and a case workspace "
            "session.",
            "1 hour",
            "Handle media correctly",
        ],
        [
            "Technicians, day two",
            "Read section 6.1. Observe a full evaluation, from intake to firm "
            "quotation.",
            "1 hour",
            "Understand what the customer is agreeing to",
        ],
        [
            "Technicians, day three",
            "Image one piece of media end to end. Do not attempt recovery yet.",
            "Half a day",
            "Image before you recover, always",
        ],
        [
            "End of week one",
            "Perform one supervised recovery with full methodology logging. Then "
            "read section 15.",
            "1 case",
            "Log a method properly",
        ],
        [
            "Week two, early",
            "Read section 6.4 again and witness one physical destruction. Then "
            "perform one erasure with verification.",
            "Half a day",
            "Certify a device correctly",
        ],
        [
            "Week two, middle",
            "Read sections 11 and 12. Read one week of the custody exception "
            "report, even though it should be empty.",
            "45 minutes",
            "Recognise a control failure",
        ],
        [
            "End of week two",
            "Read section 18 and keep it.",
            "15 minutes",
            "Work unsupervised",
        ],
    ],
    "s17_check_intro": "You have got it when these are automatic. For a technician that is "
    "usually about fifteen cases, and the custody habits arrive well "
    "before the technical ones.",
    "s17_checks": [
        "Book media in and out under dual signature without prompting",
        "Explain to a colleague why they cannot see your case",
        "Image before attempting anything, every time, without needing to be " "asked",
        "Log a methodology so that somebody else could explain a failed " "recovery",
        "Build an inventory without ever recording a file name",
        "Select a sanitisation technique from the programme rather than from " "habit",
        "Issue a certificate bound to one media serial, with a witness who is "
        "not you",
        "Know the three things to report within the hour: access to a case you "
        "were not assigned, a file name visible anywhere, and anybody asking "
        "you to release a device without a certificate",
    ],
    "s17_note": "Teach custody and access before technique. A technician who is "
    "brilliant at recovery and casual about custody is the single largest "
    "risk this module carries, and the habits are much harder to install "
    "afterwards.",
    # ============================================ 18. one page
    "s15_lede": "The module on one page, for a lab wall.",
    "s15_figures": [
        ("34", "things you can do"),
        ("12", "case states"),
        ("18", "rules enforced"),
        ("14", "automatic behaviours"),
        ("5", "targets that are 0 or 100%"),
        ("5 yrs", "access log retention"),
        ("11", "reports available"),
        ("10", "modules depend on it"),
    ],
    "s15_never": [
        "Move media in or out of the secure area on one signature",
        "Open a case you have not been individually assigned to",
        "Work on original media when imaging is possible",
        "Record a file name or any content anywhere in the system",
        "Move recovered data out except through the approved handover path",
        "Hold data past its retention window without a documented, approved, "
        "time-limited hold",
        "Release a device for refurbishment, resale or recycling without a "
        "certificate",
        "Act as both operator and witness for a physical destruction",
        "Issue one certificate covering a batch",
    ],
    "s15_where": CM.where_to_look("M06"),
}
