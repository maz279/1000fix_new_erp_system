# P03 generic model API — the read/action endpoints behind the in-workspace
# model_list screens for the A08 finance modules (M52/M50/M51/M53/M49/M54).
#
# Two endpoints only, both strictly whitelisted:
#   /p03/model/records (read)  — configurable columns, safe domains
#   /p03/model/action  (write) — ONLY the headless workflow actions that
#                                already exist on the models, each wrapped in
#                                a savepoint (a refusal leaves nothing behind
#                                — the M19 leaked-draft rule).
#
# Nothing here invents data: rows are live reads of the real models; actions
# are the SAME methods the Odoo forms would call. Internal-user only (NVR-22).
import logging

from odoo import fields, http
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.http import request

from . import a02, a03, a04, a05, a06, a07, a08, a09, a10, a11, a12
from .a02 import SURFACES as _A02_SURFACES
from .a03 import SURFACES as _A03_SURFACES
from .a04 import SURFACES as _A04_SURFACES
from .a05 import SURFACES as _A05_SURFACES
from .a06 import SURFACES as _A06_SURFACES
from .a07 import SURFACES as _A07_SURFACES
from .a08 import SURFACES as _A08_SURFACES
from .a09 import SURFACES as _A09_SURFACES
from .a10 import SURFACES as _A10_SURFACES
from .a11 import SURFACES as _A11_SURFACES
from .a12 import SURFACES as _A12_SURFACES
from .p03_service_order_api import _require_internal, _user_error

_logger = logging.getLogger(__name__)


def _log_report_export(module, report, fmt, out, params):
    """A11 audit E6 / BRU-BID-11: every pack download is logged — who, what,
    which scope, how many rows. The audit row itself is append-only (see
    fix.bi.export.log). A logging failure must never block the download."""
    try:
        env = request.env
        if "fix.bi.export.log" not in env:
            return
        env["fix.bi.export.log"].sudo().create(
            {
                "user_id": env.user.id,
                "pack": "%s:%s" % (module or "?", report or "?"),
                "channel": "download",
                "format": fmt,
                "company_ids": ", ".join(env.companies.mapped("name")),
                "row_count": len(out.get("rows") or []),
                "params_json": repr(params or {})[:2000],
            }
        )
    except Exception:
        _logger.exception("export log write failed for %s:%s", module, report)


def _readonly_changed(rec, field, value) -> bool:
    """Would writing `value` change read-only `field` on `rec`?

    The form posts every field it shows, read-only ones included, so an
    unchanged echo must pass. The comparison is deliberately lenient about
    representation (a datetime-local input drops the seconds; many2one
    arrives as an id) and strict about meaning."""
    current = rec[field.name]
    kind = field.type
    if kind == "many2one":
        return (value or False) != (current.id or False)
    if kind in ("one2many", "many2many", "binary", "properties", "json"):
        return False  # not editable through the generic form; dropped below
    if kind in ("float", "monetary", "integer"):
        try:
            return abs(float(value or 0) - float(current or 0)) > 0.005
        except (TypeError, ValueError):
            return True
    if kind == "datetime":
        return str(value or "").replace("T", " ")[:16] != str(current or "")[:16]
    if kind == "date":
        return str(value or "")[:10] != str(current or "")[:10]
    if kind == "boolean":
        return bool(value) != bool(current)
    return (value or "") != (current or "")


def _locked_fields(records) -> set:
    """Workflow-locked fields for these records (an empty recordset = a new
    one): fix.guarded.mixin's guarded fields plus whatever the model freezes
    by state. Models without the guard lock nothing beyond `readonly`."""
    hook = getattr(records, "_fix_form_locked_fields", None)
    return set(hook()) if hook else set()


# A08 (finance) + A02 (service operations) + A03 (customer experience) + A11
# (insights) surfaces, merged: the generic endpoints serve exactly what the
# per-module files declare.
SURFACES = dict(_A08_SURFACES)
for _model, _conf in _A02_SURFACES.items():
    if _model in SURFACES:
        raise ValueError("surface %s is declared by two areas" % _model)
    SURFACES[_model] = _conf
for _model, _conf in _A03_SURFACES.items():
    if _model in SURFACES:
        raise ValueError("surface %s is declared by two areas" % _model)
    SURFACES[_model] = _conf
for _model, _conf in _A04_SURFACES.items():
    if _model in SURFACES:
        raise ValueError("surface %s is declared by two areas" % _model)
    SURFACES[_model] = _conf
for _model, _conf in _A05_SURFACES.items():
    if _model in SURFACES:
        raise ValueError("surface %s is declared by two areas" % _model)
    SURFACES[_model] = _conf
for _model, _conf in _A06_SURFACES.items():
    if _model in SURFACES:
        raise ValueError("surface %s is declared by two areas" % _model)
    SURFACES[_model] = _conf
for _model, _conf in _A07_SURFACES.items():
    if _model in SURFACES:
        raise ValueError("surface %s is declared by two areas" % _model)
    SURFACES[_model] = _conf
for _model, _conf in _A09_SURFACES.items():
    if _model in SURFACES:
        raise ValueError("surface %s is declared by two areas" % _model)
    SURFACES[_model] = _conf
for _model, _conf in _A10_SURFACES.items():
    if _model in SURFACES:
        raise ValueError("surface %s is declared by two areas" % _model)
    SURFACES[_model] = _conf
for _model, _conf in _A12_SURFACES.items():
    if _model in SURFACES:
        raise ValueError("surface %s is declared by two areas" % _model)
    SURFACES[_model] = _conf
for _model, _conf in _A11_SURFACES.items():
    if _model in SURFACES:
        raise ValueError("surface %s is declared by two areas" % _model)
    SURFACES[_model] = _conf

# fields never returned over the generic endpoint
_BLOCKED_FIELDS = {"access_token", "write_uid", "create_uid"}
_FAILED = "The request could not be completed — try again or contact Finance support."


class P03GenericApiController(http.Controller):
    """Whitelisted generic reads + workflow actions for the A08 model screens."""

    # allowed UI-language codes the workspace may request labels in (audit D3)
    _LANGS = {"en": "en_US", "en_US": "en_US", "bn": "bn_BD", "bn_BD": "bn_BD"}

    @http.route("/p03/model/records", type="jsonrpc", auth="user", readonly=True)
    def model_records(self, model=None, cols=None, domain=None, state_filter=None, lang=None, **kw):
        _require_internal(request.env)
        env = request.env
        conf = SURFACES.get(model)
        if not conf:
            return {"error": "Model not served by the workspace screens"}
        try:
            # bilingual headers: labels follow the workspace UI language when
            # the module ships a translation (Odoo falls back to English).
            # Odoo 19: Environment has no with_context — env(context=...).
            lang_code = self._LANGS.get(lang)
            if lang_code and lang_code != env.context.get("lang"):
                env = env(context={**env.context, "lang": lang_code})
            # The company-wide read below runs sudo (an accountant sees every
            # operating unit), so the caller must first hold READ access on the
            # model itself: finance/payroll ACL groups still decide who sees it.
            env[model].check_access("read")
            fields_meta = env[model].fields_get(
                [c for c in (cols or []) if c not in _BLOCKED_FIELDS],
                attributes=["string", "type", "selection"],
            )
            # drop unknown columns defensively
            cols = [c for c in (cols or []) if c in fields_meta]
            if "id" not in cols:
                cols = ["id", *cols]
            search_domain = list(domain or [])
            if state_filter:
                state_field = kw.get("state_field")
                if state_field and state_filter not in ("__all", "__all__", "all", ""):
                    search_domain.append((state_field, "=", state_filter))
            # Finance list screens are COMPANY-wide reads (an accountant sees
            # every operating unit's bills — the M19 CoA sudo-read pattern).
            # A surface that declares `caller_scoped` (A11 audit M26 X03: the
            # PdM prediction list) reads AS THE CALLER instead — the caller's
            # OU record rules apply, so one operating unit's rows never leak
            # onto another unit's screen through the list endpoint. Writes
            # below keep the calling user's context (SoD/permissions apply).
            rec_model = env[model] if conf.get("caller_scoped") else env[model].sudo()
            if "company_id" in env[model]._fields:
                search_domain.append(("company_id", "in", env.companies.ids))
            records = rec_model.search(search_domain, order=conf["order"], limit=conf["limit"])
            raw = records.read(cols) if records else []
            rows = []
            for rec in raw:
                row = {}
                for c in cols:
                    v = rec.get(c)
                    meta = fields_meta.get(c, {})
                    if meta.get("type") in ("many2one",) and isinstance(v, list | tuple):
                        row[c] = {"id": v[0], "name": v[1]} if v else None
                    elif meta.get("type") == "selection":
                        labels = dict(meta.get("selection") or [])
                        # an unset selection is an EMPTY cell, not the literal
                        # "false" (the label lookup returns False and the grid
                        # printed it — M13 turnaround regrade, audit D4 class)
                        row[c] = {"key": v, "label": labels.get(v, v)} if v else ""
                    elif meta.get("type") == "datetime" and v:
                        row[c] = str(v)[:16]
                    elif v is False and meta.get("type") != "boolean":
                        # Odoo returns `false` for EVERY empty field; only a
                        # BOOLEAN false is a real ✗ — an empty phone/name is
                        # a blank, never "✗" (audit D16, user's PDF)
                        row[c] = ""
                    else:
                        row[c] = v
                rows.append(row)
            # total beyond the page: "200 of 15,413" — a bare "200 records"
            # reads as the whole base when the limit clipped it
            total = (
                rec_model.search_count(search_domain) if len(rows) >= conf["limit"] else len(rows)
            )
            return {
                "model": model,
                "rows": rows,
                "count": len(rows),
                "total": total,
                "labels": {c: fields_meta[c]["string"] for c in cols if c in fields_meta},
                # column types so the grid formats by FIELD TYPE, never by
                # magnitude (a ৳800 damage figure must not read as "800", and
                # a 1,500 count must not gain a ৳ prefix)
                "kinds": {c: fields_meta[c]["type"] for c in cols if c in fields_meta},
            }
        except (UserError, AccessError) as exc:
            return {"error": _user_error(exc)}
        except Exception:
            _logger.exception("p03 model_records failed for %s", model)
            return {"error": _FAILED}

    @http.route("/p03/model/report", type="jsonrpc", auth="user", readonly=True)
    def model_report(self, module=None, report=None, params=None, **kw):
        """A module's declared report: controllers/a08/<module>.py REPORTS
        maps name -> fn(env, **params) returning {cols, labels, rows,
        totals?, notes?, title?, empty?}. The function reads with the
        caller's env, so the models' own access rules apply."""
        _require_internal(request.env)
        mod = (
            a08.MODULES.get(module)
            or a02.MODULES.get(module)
            or a03.MODULES.get(module)
            or a04.MODULES.get(module)
            or a05.MODULES.get(module)
            or a06.MODULES.get(module)
            or a07.MODULES.get(module)
            or a09.MODULES.get(module)
            or a10.MODULES.get(module)
            or a12.MODULES.get(module)
            or a11.MODULES.get(module)
        )
        fn = getattr(mod, "REPORTS", {}).get(report) if mod else None
        if not fn:
            return {"error": "Report not available on this surface"}
        try:
            out = fn(request.env, **(params or {}))
            out.setdefault("rows", [])
            out.setdefault("cols", [])
            return out
        except (UserError, AccessError) as exc:
            return {"error": _user_error(exc)}
        except Exception:
            _logger.exception("p03 model_report %s.%s failed", module, report)
            return {"error": _FAILED}

    @http.route("/p03/model/report/export", type="http", auth="user")
    def model_report_export(self, module=None, report=None, format="csv", **params):
        """Download any whitelisted module report as CSV or Excel.

        The payload is EXACTLY the one /p03/model/report serves (same function,
        same caller ACL) — the export cannot drift from the screen. CSV values
        are written raw (numbers unformatted) so spreadsheets can compute; the
        XLSX workbook is the presentation artefact: brand header, report meta
        (company, period, filters, generated by/at), styled header row, data,
        totals and notes — the professional format users forward.
        """
        _require_internal(request.env)
        mod = (
            a08.MODULES.get(module)
            or a02.MODULES.get(module)
            or a03.MODULES.get(module)
            or a04.MODULES.get(module)
            or a05.MODULES.get(module)
            or a06.MODULES.get(module)
            or a07.MODULES.get(module)
            or a09.MODULES.get(module)
            or a10.MODULES.get(module)
            or a12.MODULES.get(module)
            or a11.MODULES.get(module)
        )
        fn = getattr(mod, "REPORTS", {}).get(report) if mod else None
        if not fn:
            return request.make_response(
                "Report not available on this surface",
                status=404,
                headers=[("Content-Type", "text/plain; charset=utf-8")],
            )
        out = fn(request.env, **(params or {}))
        cols = out.get("cols") or []
        labels = out.get("labels") or {}
        labels = labels if isinstance(labels, dict) else {}
        base_name = "%s_%s" % (module or "report", (report or "export").replace("/", "_"))
        _log_report_export(module, report, format, out, params or {})

        if format == "xlsx":
            return self._report_xlsx(out, cols, labels, base_name, params or {})

        import csv
        import io as _io

        buf = _io.StringIO()
        # UTF-8 BOM: Excel opens Bengali text correctly (repo i18n rule)
        buf.write("\ufeff")
        writer = csv.writer(buf)
        writer.writerow([labels.get(c, c) for c in cols])
        for row in out.get("rows") or []:
            writer.writerow([row.get(c, "") for c in cols])
        totals = out.get("totals")
        if totals:
            writer.writerow([totals.get(c, "") for c in cols])
        return request.make_response(
            buf.getvalue(),
            headers=[
                ("Content-Type", "text/csv; charset=utf-8"),
                ("Content-Disposition", 'attachment; filename="%s.csv"' % base_name),
            ],
        )

    # brand-60 (tokens.json color.brand.60) — the workbook accent
    _XLSX_BRAND = "0E7A6E"
    _XLSX_INK = "242424"
    _XLSX_GREY = "F5F5F5"

    def _report_meta(self, params):
        """Shared export header: company, period, filters, generated by/at —
        every artefact states what it is and what it covers (UX-001)."""
        env = request.env
        meta = [
            ("Company", env.company.name or ""),
        ]
        if params.get("date_from") or params.get("date_to"):
            meta.append(
                (
                    "Period",
                    "%s → %s" % (params.get("date_from") or "…", params.get("date_to") or "…"),
                )
            )
        for key, value in sorted(
            (k, v) for k, v in params.items() if k not in ("date_from", "date_to") and v
        ):
            meta.append((key.replace("_", " ").title(), value))
        meta.append(("Generated", fields.Datetime.now().strftime("%Y-%m-%d %H:%M")))
        meta.append(("Generated by", env.user.name or ""))
        return meta

    def _report_xlsx(self, out, cols, labels, base_name, params):
        """Presentation workbook: brand + meta block, styled header, data,
        totals, notes. Generic over every module report — one professional
        format for the whole estate."""
        from openpyxl import Workbook
        from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
        from openpyxl.utils import get_column_letter

        wb = Workbook()
        # openpyxl forbids [ ] : * ? / \ in sheet titles — sanitise
        import re as _re

        safe_title = (
            _re.sub(r"[\[\]:*?/\\]+", "-", (out.get("title") or base_name)).strip("- ")[:31]
            or base_name[:31]
        )
        ws = wb.active
        ws.title = safe_title
        rows = out.get("rows") or []
        totals = out.get("totals") or {}

        brand_font = Font(bold=True, size=14, color=self._XLSX_BRAND)
        meta_font = Font(size=10, color=self._XLSX_INK)
        meta_label_font = Font(bold=True, size=10, color=self._XLSX_INK)
        head_font = Font(bold=True, color="FFFFFF")
        head_fill = PatternFill("solid", fgColor=self._XLSX_BRAND)
        totals_font = Font(bold=True)
        totals_top = Border(top=Side(style="thin", color=self._XLSX_BRAND))

        ws.cell(row=1, column=1, value="1000 FiX ERP").font = brand_font
        r = 2
        for label, value in self._report_meta(params):
            ws.cell(row=r, column=1, value=label).font = meta_label_font
            ws.cell(row=r, column=2, value=value).font = meta_font
            r += 1
        r += 1

        head_row = r
        for c, col in enumerate(cols, 1):
            cell = ws.cell(row=head_row, column=c, value=labels.get(col, col))
            cell.font = head_font
            cell.fill = head_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
        r += 1

        for row in rows:
            for c, col in enumerate(cols, 1):
                value = row.get(col, "")
                cell = ws.cell(
                    row=r,
                    column=c,
                    value=value if isinstance(value, int | float) else str(value or ""),
                )
                if c % 2 == 0:
                    cell.fill = PatternFill("solid", fgColor=self._XLSX_GREY)
                if isinstance(value, int | float):
                    cell.number_format = "#,##0.##"
                    cell.alignment = Alignment(horizontal="right")
            r += 1

        if totals:
            for c, col in enumerate(cols, 1):
                cell = ws.cell(row=r, column=c, value=totals.get(col, ""))
                cell.font = totals_font
                cell.border = totals_top
                if isinstance(totals.get(col), int | float):
                    cell.number_format = "#,##0.##"
                    cell.alignment = Alignment(horizontal="right")
            r += 1

        r += 1
        for note in out.get("notes") or []:
            ws.cell(row=r, column=1, value="Note: %s" % note).font = Font(
                size=9, italic=True, color="616161"
            )
            r += 1

        for c, col in enumerate(cols, 1):
            width = max(
                [len(str(labels.get(col, col)))] + [len(str(row.get(col, ""))) for row in rows]
                or [8]
            )
            ws.column_dimensions[get_column_letter(c)].width = min(max(width + 2, 10), 42)
        ws.freeze_panes = ws.cell(row=head_row + 1, column=1)
        ws.auto_filter.ref = "A%d:%s%d" % (
            head_row,
            get_column_letter(len(cols)),
            head_row + len(rows),
        )

        import io as _io

        buf = _io.BytesIO()
        wb.save(buf)
        return request.make_response(
            buf.getvalue(),
            headers=[
                (
                    "Content-Type",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                ),
                ("Content-Disposition", 'attachment; filename="%s.xlsx"' % base_name),
            ],
        )

    @http.route("/p03/model/form", type="jsonrpc", auth="user", readonly=True)
    def model_form(self, model=None, fields=None, record_id=None, lang=None, lines=None, **kw):
        """Schema + values for a D365 in-workspace form screen.

        fields: [{name, type?, label?, required?, readonly?}] declared by the
        module fragment (order preserved). Returns per-field metadata from the
        model (labels/types/selection) and, when record_id is given, the
        record's values plus the choices for many2one fields.

        lines (optional): {field, fields:[{name,label,type?}]} — a declared
        one2many child grid (allocation targets, template lines). Returns the
        child field metadata and, for an existing record, its rows.
        """
        _require_internal(request.env)
        env = request.env
        lang_code = self._LANGS.get(lang)
        if lang_code and lang_code != env.context.get("lang"):
            env = env(context={**env.context, "lang": lang_code})
        conf = SURFACES.get(model)
        if not conf:
            return {"error": "Model not served by the workspace screens"}
        try:
            env[model].check_access("read")
            rec = env[model].sudo().browse(int(record_id)).exists() if record_id else None
            out_fields = self._form_field_meta(env, model, fields, rec or None)
            record = None
            if rec:
                record = self._form_record(rec, out_fields)
            line_payload = None
            if lines and lines.get("field"):
                line_payload = self._form_lines(env, model, lines, record_id)
            return {
                "model": model,
                "fields": out_fields,
                "record": record,
                "lines": line_payload,
                "title": conf.get("form_title") or env[model]._description,
            }
        except (UserError, AccessError) as exc:
            return {"error": _user_error(exc)}
        except Exception:
            _logger.exception("p03 model_form failed for %s", model)
            return {"error": "The form data could not be loaded — see the server log."}

    def _form_field_meta(self, env, model, fields, record=None):
        """Per-field metadata (label, type, required, choices) preserving the
        fragment's declared order. many2one choices come from the comodel.

        A field the model locks for this record (state, an approval stamp, a
        posted ledger line's points) is served read-only, so the form never
        offers an input the save would refuse (A03 workflow audit, R3/R5)."""
        names = [f.get("name") for f in (fields or []) if f.get("name")]
        meta = env[model].fields_get(
            names, attributes=["string", "type", "selection", "required", "readonly"]
        )
        locked = _locked_fields(record if record is not None else env[model])
        out_fields = []
        for spec in fields or []:
            name = spec.get("name")
            m = meta.get(name)
            if not m:
                continue
            field_type = spec.get("type") or m["type"]
            entry = {
                "name": name,
                "label": spec.get("label") or m["string"],
                "type": field_type,
                "required": bool(spec.get("required") or m.get("required")),
                "readonly": bool(spec.get("readonly") or m.get("readonly") or name in locked),
            }
            if field_type == "selection":
                entry["choices"] = [
                    {"key": k, "label": v}
                    for k, v in (spec.get("choices") or m.get("selection") or [])
                ]
            if field_type == "many2one":
                comodel = env[model]._fields[name].comodel_name
                entry["comodel"] = comodel
                entry["choices"] = [
                    {"id": r["id"], "label": r["display_name"]}
                    for r in env[comodel].sudo().search_read([], ["display_name"], limit=300)
                ]
            out_fields.append(entry)
        return out_fields

    def _form_record(self, rec, out_fields):
        record = {"id": rec.id}
        for entry in out_fields:
            value = rec[entry["name"]]
            if entry["type"] == "many2one":
                record[entry["name"]] = (
                    {"id": value.id, "label": value.display_name} if value else None
                )
            elif entry["type"] in ("date",):
                record[entry["name"]] = str(value) if value else ""
            elif entry["type"] == "datetime":
                record[entry["name"]] = str(value)[:19] if value else ""
            elif entry["type"] == "monetary":
                record[entry["name"]] = float(value or 0.0)
            else:
                record[entry["name"]] = value if value is not False else ""
        return record

    def _form_lines(self, env, model, lines, record_id):
        """A declared one2many child grid: field meta + existing rows."""
        field_name = lines.get("field")
        field = env[model]._fields.get(field_name)
        if not field or field.type != "one2many":
            raise UserError("This form's child grid is not a one2many")
        comodel = field.comodel_name
        out_fields = self._form_field_meta(env, comodel, lines.get("fields"))
        rows = []
        if record_id:
            rec = env[model].sudo().browse(int(record_id)).exists()
            if rec:
                for child in rec[field_name]:
                    rows.append(self._form_record(child, out_fields))
        return {"field": field_name, "model": comodel, "fields": out_fields, "rows": rows}

    @http.route("/p03/model/write", type="jsonrpc", auth="user")
    def model_write(self, model=None, record_id=None, values=None, lines=None, **kw):
        """Create/update one record from a D365 in-workspace form.

        The caller's own ACL applies (no sudo on write); the whole write runs
        in a savepoint so a refusal leaves nothing behind — the M19 leaked-
        draft rule. Only models declared in SURFACES are accepted.

        lines (optional): {field, rows:[{id?, values}], removed:[id]} — the
        declared one2many child grid, applied in the SAME write as the header
        so a rule refusal (targets must total 100%) leaves nothing behind.
        """
        _require_internal(request.env)
        env = request.env
        conf = SURFACES.get(model)
        if not conf:
            return {"error": "Model not served by the workspace screens"}
        vals = self._coerce_vals(values)
        # What the form may not set (A03 audit: this endpoint wrote
        # dofa_approved, released_by, executed_by... as sent):
        #  - read-only fields and fields the model locks for this record
        #    (fix.guarded.mixin), which change only through an action;
        #  - on a surface that declares `writable` (R3), any field no
        #    workspace form offers for editing.
        # The form posts every field it shows, so on edit an unchanged echo
        # is dropped and only a CHANGE is refused. On create they are dropped
        # so the model's defaults and computes apply.
        fields_meta = env[model]._fields
        current = env[model].browse(int(record_id)).exists() if record_id else env[model]
        if record_id and not current:
            return {"error": "Record not found"}
        locked = _locked_fields(current)
        workflow = [
            k for k in vals if k in fields_meta and (fields_meta[k].readonly or k in locked)
        ]
        writable = conf.get("writable")
        off_screen = (
            [] if writable is None else [k for k in vals if k not in writable and k not in workflow]
        )
        if lines and lines.get("field") and writable is not None and lines["field"] not in writable:
            return {"error": "This screen does not edit %s." % lines["field"]}
        if record_id:
            for names, why in (
                (workflow, "is read-only and changes only through its workflow action."),
                (off_screen, "is not editable on this screen."),
            ):
                changed = [
                    k
                    for k in names
                    if k not in fields_meta or _readonly_changed(current, fields_meta[k], vals[k])
                ]
                if changed:
                    return {
                        "error": "%s %s"
                        % (
                            ", ".join(
                                (fields_meta[k].string if k in fields_meta else k) or k
                                for k in changed
                            ),
                            why,
                        )
                    }
        for k in workflow + off_screen:
            vals.pop(k)
        if not record_id:
            # On CREATE an unset many2one must be OMITTED, not sent as NULL: the
            # model's own default (usually the current company) then applies.
            # Sending an explicit NULL hit a NOT NULL company column and turned a
            # plain create into a NotNullViolation. On write the key is kept so a
            # user can still clear a relation.
            fields_meta = env[model]._fields
            vals = {
                k: v
                for k, v in vals.items()
                if not (
                    getattr(fields_meta.get(k), "type", "") == "many2one"
                    and v in (False, None, "", 0)
                )
            }
        try:
            with env.cr.savepoint():
                if lines and lines.get("field"):
                    field = env[model]._fields.get(lines.get("field"))
                    if not field or field.type != "one2many":
                        return {"error": "This form's child grid is not a one2many"}
                    commands = [(2, int(i)) for i in (lines.get("removed") or [])]
                    for row in lines.get("rows") or []:
                        row_vals = self._coerce_vals(row.get("values"))
                        if not row_vals:
                            continue
                        if row.get("id"):
                            commands.append((1, int(row["id"]), row_vals))
                        else:
                            commands.append((0, 0, row_vals))
                    vals[lines["field"]] = commands
                if record_id:
                    env[model].check_access("write")
                    rec = env[model].browse(int(record_id)).exists()
                    if not rec:
                        return {"error": "Record not found"}
                    rec.write(vals)
                else:
                    env[model].check_access("create")
                    rec = env[model].create(vals)
                return {"id": rec.id, "display_name": rec.display_name}
        except (UserError, AccessError, ValidationError) as exc:
            return {"error": _user_error(exc)}
        except Exception as exc:
            # IntegrityError (a UNIQUE/check constraint) is a RULE refusal, not
            # a server fault: say so instead of the generic support message.
            # A CHECK constraint carries an authored message (e.g. "a channel
            # conflict must name two different partners") — surface it as-is;
            # a UNIQUE violation names internal columns, so stay generic.
            if type(exc).__name__ == "CheckViolation":
                # Odoo registers the authored models.Constraint message on
                # ir.model.constraint — use it instead of Postgres' raw text
                # (which names internal tables and constraint ids).
                cname = (getattr(getattr(exc, "diag", None), "constraint_name", "") or "").strip()
                message = False
                if cname:
                    message = (
                        env["ir.model.constraint"]
                        .sudo()
                        .search([("name", "=", cname)], limit=1)
                        .message
                    )
                if message:
                    return {"error": "This record breaks a data rule — %s" % message}
            if "Integrity" in type(exc).__name__ or "constraint" in str(exc).lower():
                return {
                    "error": "This record breaks a data rule — a duplicate or a "
                    "required relation is missing (%s)" % type(exc).__name__
                }
            _logger.exception("p03 model_write failed for %s", model)
            return {"error": "The save could not be completed: %s" % exc}

    @staticmethod
    def _coerce_vals(values):
        vals = {}
        for key, value in (values or {}).items():
            # many2one arrives as {id,label} or a bare id
            if isinstance(value, dict) and "id" in value:
                vals[key] = value["id"] or False
            elif (
                isinstance(value, str)
                and len(value) >= 16
                and value[4:5] == "-"
                and value[10:11] == "T"
            ):
                # <input type="datetime-local"> sends 2026-10-27T12:00; the
                # ORM's datetime converter rejects the T separator (surfaces
                # as a generic save failure). Normalise to Odoo's format.
                iso = value.replace("T", " ", 1)
                if len(iso) == 16:
                    iso += ":00"
                vals[key] = iso
            elif isinstance(value, str) and value.startswith("data:"):
                vals[key] = value.split(",", 1)[1] if "," in value else value
            else:
                vals[key] = value
        return vals

    @http.route("/p03/model/action", type="jsonrpc", auth="user")
    def model_action(self, model=None, ids=None, method=None, kwargs=None, **kw):
        _require_internal(request.env)
        env = request.env
        allowed = SURFACES.get(model, {}).get("actions", set())
        if method not in allowed:
            return {"success": False, "error": "Action not available for this surface"}
        try:
            with env.cr.savepoint():
                records = env[model].browse([int(i) for i in (ids or [])]).exists()
                if not records:
                    return {"success": False, "error": "Record not found"}
                result = getattr(records, method)(**(kwargs or {}))
                payload = result if isinstance(result, dict) else {}
                return {"success": True, "result": payload}
        except (UserError, AccessError) as exc:
            return {"success": False, "error": _user_error(exc)}
        except Exception:
            _logger.exception("p03 model_action %s.%s failed", model, method)
            return {"success": False, "error": _FAILED}
