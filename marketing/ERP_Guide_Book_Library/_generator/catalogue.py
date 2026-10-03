# -*- coding: utf-8 -*-
"""
catalogue — discovers every specification and builds the programme-wide index
the guide books cross-reference against.
"""
import os
import glob
from collections import OrderedDict, defaultdict

import theme as T
from spec import Spec

SRC_MODULES = (r"D:\sofrware_project_5\1000 fix\1000fix_new_erp_system"
               r"\1000fix_ERP_Module\03_Modules")
SRC_ROOT = (r"D:\sofrware_project_5\1000 fix\1000fix_new_erp_system"
            r"\1000fix_ERP_Module")

CATEGORY_FOLDER = OrderedDict([
    ("A", "A_Service_Delivery_and_Operations"),
    ("B", "B_Customer_Engagement_and_Experience"),
    ("C", "C_Commercial_Pricing_and_Revenue"),
    ("D", "D_Circular_and_Asset_Based_Business"),
    ("E", "E_Supply_Chain_and_Inventory"),
    ("F", "F_Asset_Equipment_and_Facilities"),
    ("G", "G_Finance_and_Treasury"),
    ("H", "H_People_and_Workforce"),
    ("I", "I_Governance_Risk_Quality_and_Knowledge"),
    ("J", "J_Data_Analytics_and_Intelligence"),
    ("K", "K_Platform_and_Technology"),
])

# Output folder names — grouped by category for modules, one folder for portals
OUT_CATEGORY_FOLDER = OrderedDict([
    ("A", "A_Service_Delivery_and_Operations"),
    ("B", "B_Customer_Engagement_and_Experience"),
    ("C", "C_Commercial_Pricing_and_Revenue"),
    ("D", "D_Circular_and_Asset_Based_Business"),
    ("E", "E_Supply_Chain_and_Inventory"),
    ("F", "F_Asset_Equipment_and_Facilities"),
    ("G", "G_Finance_and_Treasury"),
    ("H", "H_People_and_Workforce"),
    ("I", "I_Governance_Risk_Quality_and_Knowledge"),
    ("J", "J_Data_Analytics_and_Intelligence"),
    ("K", "K_Platform_and_Technology"),
])


def discover():
    """Load every module and portal specification once."""
    files = sorted(glob.glob(os.path.join(SRC_MODULES, "*", "M*.md")) +
                   glob.glob(os.path.join(SRC_MODULES, "*", "P*.md")))
    specs = []
    for f in files:
        base = os.path.basename(f)
        if base.startswith("_"):
            continue
        specs.append(Spec(f))
    specs.sort(key=lambda s: (0 if not s.is_portal else 1,
                              s.category, s.uid))
    return specs


def build_index(specs):
    """uid -> summary dict, used for every cross-reference in the library."""
    idx = {}
    for s in specs:
        idx[s.uid] = {
            "uid": s.uid,
            "name": s.name,
            "code": s.code,
            "category": s.category,
            "cat_name": T.cat_name(s.category),
            "is_portal": s.is_portal,
            "priority": s.priority,
            "wave": s.wave,
            "reqs": s.req_count,
            "effort": s.effort_pw,
            "rules": len(s.rules),
            "entities": len(s.owned_entities),
            "events": len(s.events),
            "roles": len(s.roles),
            "kpis": len(s.kpis),
            "automations": len(s.automations),
            "business_owner": s.business_owner,
            "system_owner": s.system_owner,
            "one_liner": s.one_liner(),
            "depends_on": s.depends_on,
            "depended_by": s.depended_by,
            "layer_alloc": s.layer_alloc,
            "areas": len(s.areas),
            "questions": len(s.questions),
            "acceptance": len(s.acceptance),
            "api": len(s.api),
            "externals": len(s.externals),
            "filename": s.filename,
        }
    return idx


def peers_for(specs, spec):
    """Sibling components in the same category, for the comparison exhibit."""
    group = [s for s in specs
             if s.is_portal == spec.is_portal and s.category == spec.category]
    return [{"uid": s.uid, "name": s.name, "reqs": s.req_count,
             "effort": s.effort_pw or 0} for s in group]


def category_groups(specs):
    """OrderedDict letter -> [Spec] for modules; 'P' -> [Spec] for portals."""
    g = OrderedDict()
    for letter in CATEGORY_FOLDER:
        g[letter] = [s for s in specs if not s.is_portal and s.category == letter]
    g["P"] = [s for s in specs if s.is_portal]
    return g
