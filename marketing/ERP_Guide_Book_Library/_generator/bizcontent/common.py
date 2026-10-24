# -*- coding: utf-8 -*-
"""
common — the framing text every business-reader guide book shares.

Written once, applied to all of them, so the set reads as one document rather
than seven. Anything specific to a module belongs in that module's own file.
"""

PART1_BLURB = (
    "Before you can use a module you have to know what it is for, "
    "who else is using it, and where it stops. Five short sections. "
    "Read them once and the rest of the book will make sense."
)

PART2_BLURB = (
    "The heart of the guide book. Everything the module lets you "
    "do, written as what you can do rather than what the software "
    "contains, with a worked example in each area and a set of "
    "walkthroughs at the end."
)

PART3_BLURB = (
    "Living with it. The rules it will enforce, the work it does "
    "on its own, who is allowed to do what, what you can measure, "
    "how it connects to the rest of the system, and what to do when "
    "something looks wrong."
)

APPENDIX_BLURB = (
    "The technical register: every requirement identifier, "
    "business rule, state transition, data entity, interface and "
    "acceptance criterion, exactly as the specification states "
    "them. Nothing in here is needed to use the module."
)


def about(module_word):
    return (
        "This guide book explains %s in ordinary English. It is written "
        "for the people who will work with it every day — counter staff, "
        "technicians, dispatchers, branch and workshop managers, "
        "supervisors and the managers who have to answer for the numbers. "
        "It assumes no knowledge of the ERP, of Odoo, or of how the "
        "software is built." % module_word
    )


AUDIENCE = (
    "Everybody who uses the module or manages someone who does. No "
    "technical background assumed."
)

HOW_ARRANGED = (
    "The book is in three parts and an appendix. The parts move from why the "
    "module exists, to what it lets you do, to how to live with it well. Each "
    "part opens with a divider page saying what is in it, and each section "
    "opens with a one-line summary in italics so you can decide in two seconds "
    "whether you need to read on."
)


def parts_table(module_short):
    return [
        [
            "Part one — Understanding this module",
            "What %s is for, the problem it solves, who uses it, where it stops, "
            "and the words it uses." % module_short,
            "First. Before your first day on the system.",
        ],
        [
            "Part two — What you can do with it",
            "Every feature grouped into areas of work, with a worked example in "
            "each. Then the journey of a job from start to finish, and a set of "
            "walkthroughs from a normal working day.",
            "During training, and afterwards whenever you meet something new.",
        ],
        [
            "Part three — Working with it well",
            "The rules the system enforces, what it does automatically, who may "
            "do what, what you can measure, how it links to other modules, and "
            "what to do when something goes wrong.",
            "In your first weeks, and again when you take on supervision.",
        ],
        [
            "Appendix A — Technical reference",
            "The complete specification register: requirement identifiers, rule "
            "classes, state transitions, data entities, interfaces, roles and "
            "acceptance criteria.",
            "Only if you are configuring, building, testing or auditing it.",
        ],
        [
            "Appendix B — Change control and feedback",
            "How to get something in this book corrected.",
            "The moment you find something wrong.",
        ],
    ]


READING_NOTE = (
    "Read section 1, then find your own role in section 2, then read the "
    "walkthrough in section 8 that matches the work you actually do. That is "
    "about twenty minutes and it will carry you through your first week. "
    "Everything else can wait until you need it."
)

APPENDIX_NOTE = (
    "Appendix A holds every requirement identifier, delivery layer, state "
    "guard, data entity and interface contract from the specification. It is "
    "there so that developers, testers and auditors have one document rather "
    "than two, and so that anything asserted in the body of this book can be "
    "traced. If you are not building or testing the module you will never need "
    "to open it, and nothing in the first three parts depends on it."
)

CHANGE_CONTROL = (
    "This guide book is generated, not typed. That means a correction has to "
    "go back to the source it came from, or the next build will undo it. It "
    "also means a correction, once made in the right place, appears in every "
    "document that draws on the same source. Please do report things: a "
    "sentence that reads wrongly to somebody doing the job is a real defect, "
    "not a matter of taste."
)


def change_table(owner):
    return [
        [
            "A feature is described in a way that does not match how the work "
            "actually gets done",
            "%s, copying the guide book editor" % owner,
            "The specification section is corrected and the book is rebuilt. "
            "This is the most valuable kind of report.",
        ],
        [
            "A number is wrong — a count, a target, a value",
            "The guide book editor",
            "Traced back to the register it came from. If the register is wrong "
            "it is corrected there, which fixes every document at once.",
        ],
        [
            "A worked example or walkthrough does not reflect real practice",
            "%s" % owner,
            "The example is rewritten with the operation that raised it.",
        ],
        [
            "Something is missing entirely",
            "%s" % owner,
            "Raised as a change against the module specification, which is where "
            "scope is decided.",
        ],
        [
            "A typographical or layout fault",
            "The guide book editor",
            "Fixed in the generator, which corrects it across the whole library.",
        ],
    ]


def part1_sections(module_short, kinds_title):
    return [
        (
            "1",
            "What this module is for",
            "The job it does, the problem it replaces, and the one sentence to "
            "take into a meeting",
        ),
        (
            "2",
            "Who uses it, and what changes for them",
            "Every role that touches it, and what their day looks like before "
            "and after",
        ),
        (
            "3",
            "Where this module starts and stops",
            "What %s owns, what it hands to somebody else, and who owns the "
            "concepts it shares" % module_short,
        ),
        (
            "4",
            kinds_title,
            "The different shapes of work the module has to carry, and how it "
            "keeps them on one record",
        ),
        (
            "5",
            "The words we use",
            "The vocabulary of the module, defined once so that everybody means "
            "the same thing",
        ),
    ]


def part2_sections(journey_title):
    return [
        (
            "6",
            "Everything this module lets you do",
            "Every function, grouped into areas of work, each with a worked " "example",
        ),
        (
            "7",
            journey_title,
            "The stages a job passes through, and the points it cannot get past",
        ),
        (
            "8",
            "A day in the life",
            "Walkthroughs following single jobs across everybody who touches " "them",
        ),
        (
            "9",
            "What the walkthroughs have in common",
            "The habits the module builds in, drawn out of the five stories",
        ),
    ]


PART3_SECTIONS = [
    (
        "10",
        "The rules the system will enforce",
        "What you will not be able to do, why, and what to do instead",
    ),
    (
        "11",
        "What happens without anyone asking",
        "The work the system does on its own, and who it reaches",
    ),
    (
        "12",
        "Who may do what",
        "Roles, permissions and the separations that are enforced absolutely",
    ),
    (
        "13",
        "What you can see and measure",
        "The reports available and the numbers the module is judged on",
    ),
    (
        "14",
        "Where this module meets the others",
        "What it cannot work without, and what cannot work without it",
    ),
    (
        "15",
        "When something goes wrong",
        "The common problems, what they usually mean, and the questions people " "ask",
    ),
    (
        "16",
        "What this module is worth",
        "The value the specification attributes to it, and what it declines to "
        "put a number on",
    ),
    ("17", "Learning it", "A first fortnight, and how to tell when you have got it"),
    (
        "18",
        "The one page to keep",
        "The whole module condensed to a single printable page",
    ),
]

APPENDIX_SECTIONS = [
    ("A.1", "Module register entry", "The permanent registry record"),
    (
        "A.2",
        "Requirement index",
        "Every function with its identifier, priority and delivery layer",
    ),
    ("A.3", "Technical functions", "Engineering behaviours no user will ever see"),
    (
        "A.4",
        "Business rules as specified",
        "The rules with their identifiers and enforcement classes",
    ),
    ("A.5", "State model and transition guards", "The lifecycle as a state machine"),
    ("A.6", "Data entities", "What the module owns and what it references"),
    ("A.7", "Interfaces", "Consumed, provided, events published and the API surface"),
    (
        "A.8",
        "Roles and permissions as specified",
        "The access matrix in house notation",
    ),
    ("A.9", "Automations as specified", "Triggers, actions and failure behaviour"),
    ("A.10", "Reports and measures as specified", "The report and measure registers"),
    (
        "A.11",
        "How this compares with the big suites",
        "SAP, Oracle, Dynamics, IFS and Odoo — what was adopted and rejected",
    ),
    ("A.12", "Acceptance criteria", "What must be true before it is accepted"),
    ("A.13", "Open questions", "Decisions the specification records as open"),
    (
        "A.14",
        "How it will be delivered",
        "Layer allocation, custom build items, sequence and migration",
    ),
    ("A.15", "Where this came from", "The specification and its measurements"),
]


def where_to_look(module_short):
    return [
        (
            "A rule is blocking you",
            "Section 10 — the plain reading of every " "enforced rule",
        ),
        (
            "A screen is refusing something",
            "Section 15 — the common problems " "and what they mean",
        ),
        ("You need a number", "Section 13 — the reports and what each one " "answers"),
        (
            "Somebody cannot see something",
            "Section 12 — permissions are by " "role, never by person",
        ),
        (
            "Another team says it is your job",
            "Section 3 — the boundary, and " "who owns each shared concept",
        ),
        (
            "You are configuring or testing",
            "Appendix A — the full technical " "register for %s" % module_short,
        ),
        ("Something in this book is wrong", "Appendix B — how to get it " "corrected"),
    ]


CHANGE_NOTE = (
    "Do not edit the Word file. Any change made in it is lost the next time "
    "the library is rebuilt, and in the meantime two versions of the truth are "
    "in circulation, which is exactly the problem this programme exists to "
    "remove."
)
