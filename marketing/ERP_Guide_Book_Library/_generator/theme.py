# -*- coding: utf-8 -*-
"""
1000FiX ERP Guide Book Library — Design System
==============================================
Single source of truth for typography, colour, spacing and exhibit styling
across the entire guide-book library. Every document and every exhibit
imports from here so the library reads as one designed system.

Palette extends the palette already established in the programme's
Marketing & Technical Catalogue (navy 0B2545 / steel 2A628F / ochre D96A29)
so the guide books sit visually alongside the existing collateral.
"""

# ---------------------------------------------------------------- typography
FONT_BODY = "Calibri"
FONT_MONO = "Consolas"
SIZE_BODY = 9.5  # mandated house body size
SIZE_TABLE = 9.5
SIZE_TABLE_DENSE = 8.5  # tables with 7+ columns, to guarantee fit on A4
SIZE_SMALL = 8.0
SIZE_MICRO = 7.0
SIZE_CAPTION = 8.5

SIZE_H1 = 19.0
SIZE_H2 = 13.5
SIZE_H3 = 11.0
SIZE_H4 = 9.5
SIZE_PART = 26.0
SIZE_COVER_ID = 54.0
SIZE_COVER_TITLE = 24.0

# --------------------------------------------------------------------- house
NAVY = "0B2545"  # primary — headings, cover band, rules
NAVY_DEEP = "081B33"
BLUE = "134074"  # secondary
STEEL = "2A628F"  # tertiary / chart series 1
SKY = "5BA3C6"  # chart series 2
SKY_PALE = "A8CFE4"
BG_TINT = "E8EEF6"  # table header tint, callout ground
BG_PAPER = "F4F7FB"  # banded row / panel ground
BG_PAPER_2 = "FAFCFE"
RULE = "C9D6E5"  # hairline rules and table borders
RULE_SOFT = "E2EAF3"

INK = "1A2433"  # body text
INK_SOFT = "44536B"
GREY = "6B7280"  # secondary text, captions
GREY_LIGHT = "9AA5B4"
WHITE = "FFFFFF"

# --------------------------------------------------------------- accent set
OCHRE = "D96A29"  # accent / attention
OCHRE_PALE = "FCF2EC"
GREEN = "2E8B57"  # positive / done
GREEN_PALE = "EFF6F1"
TEAL = "1F7A8C"
TEAL_PALE = "EDF4F6"
PLUM = "6C4A7E"
PLUM_PALE = "F3EFF6"
GOLD = "E8A33D"  # caution
GOLD_PALE = "FDF6E9"
RED = "B03A2E"  # blocking / risk
RED_PALE = "FBF0EE"

# --------------------------------------------------------- priority colours
PRIORITY = {
    "P0": RED,
    "P1": OCHRE,
    "P2": STEEL,
    "P3": GREY_LIGHT,
}
PRIORITY_PALE = {
    "P0": RED_PALE,
    "P1": OCHRE_PALE,
    "P2": BG_TINT,
    "P3": BG_PAPER,
}

# ------------------------------------------------------- rule-class colours
RULE_CLASS = {
    "H": RED,  # hard block
    "A": OCHRE,  # approved override
    "S": GOLD,  # soft warning
    "C": TEAL,  # computed
}
RULE_CLASS_NAME = {
    "H": "Hard block",
    "A": "Approved override",
    "S": "Soft warning",
    "C": "Computed",
}

# ------------------------------------------------------- delivery-layer set
LAYER_COLOUR = {
    "L1": NAVY,  # Odoo 19 Community
    "L2": STEEL,  # OCA
    "L3": SKY,  # free third-party
    "L4": TEAL,  # standalone open source
    "L5": OCHRE,  # custom development
    "L6": PLUM,  # commercial component
}
LAYER_NAME = {
    "L1": "Odoo 19 Community Edition",
    "L2": "OCA community modules",
    "L3": "Free third-party Odoo modules",
    "L4": "Standalone open-source systems",
    "L5": "Custom development (SPSL build)",
    "L6": "Commercial component",
}

# --------------------------------------------------------- category accents
# Every category owns an accent hue so the library is navigable by colour
# on a shelf, on screen and in a printed binder.
CATEGORY = {
    "A": {
        "name": "Service Delivery & Operations",
        "colour": "1F7A8C",
        "pale": "EDF4F6",
    },
    "B": {
        "name": "Customer Engagement & Experience",
        "colour": "C2571A",
        "pale": "FCF1E9",
    },
    "C": {
        "name": "Commercial, Pricing & Revenue",
        "colour": "6C4A7E",
        "pale": "F3EFF6",
    },
    "D": {
        "name": "Circular & Asset-Based Business",
        "colour": "2E8B57",
        "pale": "EDF6F1",
    },
    "E": {"name": "Supply Chain & Inventory", "colour": "2A628F", "pale": "EAF1F7"},
    "F": {
        "name": "Asset, Equipment & Facilities",
        "colour": "8A6D3B",
        "pale": "F7F3EA",
    },
    "G": {"name": "Finance & Treasury", "colour": "0B4F6C", "pale": "E9F1F5"},
    "H": {"name": "People & Workforce", "colour": "A63A50", "pale": "F9EDEF"},
    "I": {
        "name": "Governance, Risk, Quality & Knowledge",
        "colour": "55606E",
        "pale": "EFF1F4",
    },
    "J": {
        "name": "Data, Analytics & Intelligence",
        "colour": "7A3E9D",
        "pale": "F4EEF9",
    },
    "K": {"name": "Platform & Technology", "colour": "0B2545", "pale": "E8EEF6"},
    "P": {"name": "Portals & Applications", "colour": "D96A29", "pale": "FCF2EC"},
}

CATEGORY_ORDER = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"]

# --------------------------------------------------------- ordered chart set
SERIES = [
    NAVY,
    OCHRE,
    TEAL,
    STEEL,
    PLUM,
    GREEN,
    GOLD,
    SKY,
    RED,
    "8A6D3B",
    "55606E",
    "7A3E9D",
    "A8CFE4",
    "C2571A",
    "0B4F6C",
]

# ------------------------------------------------------------------ geometry
PAGE_W_MM = 210.0
PAGE_H_MM = 297.0
MARGIN_TOP_MM = 18.0
MARGIN_BOTTOM_MM = 17.0
MARGIN_LEFT_MM = 19.0
MARGIN_RIGHT_MM = 17.0
CONTENT_W_MM = PAGE_W_MM - MARGIN_LEFT_MM - MARGIN_RIGHT_MM  # 174 mm
CONTENT_W_IN = CONTENT_W_MM / 25.4  # 6.85 in

DPI = 300  # verified free of Calibri glyph dropout across 5-26 pt

# ------------------------------------------------------------------ strings
PROGRAMME = "1000FiX ERP System v2.0"
CLIENT = "1000FiX Services Limited"
DELIVERY_ORG = "SPSL"
LIBRARY = "ERP Guide Book Library"
CLASSIFICATION = "CONFIDENTIAL — Internal Use Only"
EDITION = "Edition 1.0"
ISSUE_DATE = "22 August 2026"
HOTLINE = "16743"


def cat_colour(cat_letter: str) -> str:
    return CATEGORY.get(cat_letter, CATEGORY["K"])["colour"]


def cat_pale(cat_letter: str) -> str:
    return CATEGORY.get(cat_letter, CATEGORY["K"])["pale"]


def cat_name(cat_letter: str) -> str:
    return CATEGORY.get(cat_letter, CATEGORY["K"])["name"]


def hexc(h: str) -> str:
    """matplotlib-friendly '#rrggbb'."""
    return "#" + h.lstrip("#")
