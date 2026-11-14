# The New User form's per-module permission checklist (M29 capture audit
# 2026-11-14). cd_rbac_ext owns the event and the lines; this module knows the
# workspace's modules (controllers/<area>.MODULES -> the models each serves)
# and computes, from the REAL access rules, what the chosen roles allow per
# module. Saving the event with its roles fills the checklist; the requester
# then narrows it (fix_module_permission.py explains the model).
import json
from pathlib import Path

from odoo import api, models

REGISTRY_PATH = Path(__file__).resolve().parents[4] / "contracts" / "nav" / "registry.json"
AREAS = ("a02", "a03", "a04", "a05", "a06", "a07", "a08", "a09", "a10", "a11", "a12")
_CATALOGUE = None


def module_catalogue():
    """[(code, name, area label, frozenset(models))] for every workspace module,
    in registry order. Read once per process."""
    global _CATALOGUE
    if _CATALOGUE is not None:
        return _CATALOGUE
    import importlib

    served = {}
    for area in AREAS:
        pkg = importlib.import_module("odoo.addons.cd_p03_portal.controllers.%s" % area)
        for code, mod in getattr(pkg, "MODULES", {}).items():
            served.setdefault(code, set()).update(getattr(mod, "SURFACES", {}).keys())
    try:
        registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        registry = {"modules": [], "areas": []}
    area_names = {
        a.get("id"): a.get("en") or a.get("id")
        for a in registry.get("areas", [])
        if isinstance(a, dict)
    }
    out = []
    for entry in registry.get("modules", []):
        code = entry.get("id")
        if code in served:
            area = entry.get("area") or ""
            out.append(
                (
                    code,
                    "%s · %s" % (code, entry.get("en") or code),
                    "%s · %s" % (area, area_names.get(area, area)),
                    frozenset(served[code]),
                )
            )
    known = {c for c, *_ in out}
    for code in sorted(set(served) - known):
        out.append((code, code, "", frozenset(served[code])))
    _CATALOGUE = out
    return out


def model_module_map():
    """{model: module code} - the module whose workspace serves the model."""
    out = {}
    for code, _name, _area, models_ in module_catalogue():
        for model in models_:
            out.setdefault(model, code)
    return out


class FixJmlEventPermissions(models.Model):
    _inherit = "fix.jml.event"

    @api.model
    def _fix_role_allowance(self, roles):
        """{module code: (level, label)} - what these roles (plus the internal
        user base every login has) allow, read from ir.model.access."""
        groups = roles.sudo().mapped("group_ids") | self.env.ref("base.group_user")
        groups = groups.all_implied_ids
        catalogue = module_catalogue()
        all_models = sorted({m for *_x, ms in catalogue for m in ms})
        rows = (
            self.env["ir.model.access"]
            .sudo()
            .search(
                [
                    ("active", "=", True),
                    ("model_id.model", "in", all_models),
                    "|",
                    ("group_id", "=", False),
                    ("group_id", "in", groups.ids),
                ]
            )
        )
        perms = {}
        for acl in rows:
            p = perms.setdefault(acl.model_id.model, [False, False, False])
            p[0] |= acl.perm_read
            p[1] |= acl.perm_create
            p[2] |= acl.perm_write
        out = {}
        for code, _name, _area, models_ in catalogue:
            read = any(perms.get(m, [0, 0, 0])[0] for m in models_)
            create = any(perms.get(m, [0, 0, 0])[1] for m in models_)
            write = any(perms.get(m, [0, 0, 0])[2] for m in models_)
            if write:
                level, label = "edit", "Edit + Approve"
                if not create:
                    level, label = "view", "View"
            elif create:
                level, label = "create", "Create"
            elif read:
                level, label = "view", "View"
            else:
                continue
            out[code] = (level, label)
        return out

    def _fix_refresh_permission_lines(self):
        """Fill the checklist from the roles. A module the requester already
        narrowed keeps that choice (capped to what the roles now allow); a module
        the roles no longer reach drops out."""
        Line = self.env["fix.jml.permission.line"].sudo()
        rank = {"none": 0, "view": 1, "create": 2, "edit": 3}
        names = {c: (n, a) for c, n, a, _m in module_catalogue()}
        for rec in self.sudo():
            if rec.event_type == "leaver" or rec.state != "pending":
                continue
            allowed = rec._fix_role_allowance(rec._fix_roles()) if rec.role_id else {}
            current = {line.module_code: line for line in rec.permission_line_ids}
            (
                rec.permission_line_ids
                - Line.browse([line.id for code, line in current.items() if code in allowed])
            ).unlink()
            for code, (level, label) in allowed.items():
                name, area = names.get(code, (code, ""))
                line = current.get(code)
                if line:
                    keep = line.level if rank[line.level] <= rank[level] else level
                    line.write(
                        {
                            "allowed_level": level,
                            "allowed_label": label,
                            "level": keep,
                            "can_approve": line.can_approve and rank[level] >= 3,
                        }
                    )
                    continue
                Line.create(
                    {
                        "event_id": rec.id,
                        "module_code": code,
                        "module_name": name,
                        "area": area,
                        "allowed_level": level,
                        "allowed_label": label,
                        "level": level,
                        "can_approve": rank[level] >= 3,
                        "can_print": True,
                        "can_export": True,
                        "can_email": True,
                    }
                )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._fix_refresh_permission_lines()
        for rec, vals in zip(records, vals_list, strict=True):
            if vals.get("permission_bulk"):
                rec._fix_apply_bulk(vals["permission_bulk"])
        return records

    def write(self, vals):
        res = super().write(vals)
        if {"role_id", "extra_role_ids", "event_type"} & set(vals):
            self._fix_refresh_permission_lines()
        # the one-click preset applies after the checklist is (re)filled
        if vals.get("permission_bulk"):
            self._fix_apply_bulk(vals["permission_bulk"])
        return res
