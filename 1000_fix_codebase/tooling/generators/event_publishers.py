#!/usr/bin/env python3
"""event_publishers.py — statically derive published domain events from the code (AS-08).

Reads addons/ (never executes it) and finds every event the code publishes through
``libs.py.fix_events.publish(env, "<type>", aggregate, aggregate_id, payload)``:

* direct calls with a literal event type;
* wrapper helpers that forward a parameter as the event type
  (``def _emit(self, event_type, rec): publish(self.env, event_type, ...)``) - resolved
  through every call of the helper in the same addon with a literal argument;
* local variables bound to literals (``event_name = "a.b" if x else "a.c"``).

Event types composed at run time (f-strings) are reported, not guessed into the registry.

For each site the payload argument is turned into a JSON-schema fragment: the dict
literal's keys (closed object, ``additionalProperties: false``) and, per value, the JSON
type(s) inferred from the expression - Python literals/builtins, and Odoo field
declarations parsed from the addon models (Char/Selection/Date/... read back as
``False`` when empty unless the field is ``required``; an empty many2one yields ``False``
for every attribute read through it). Values whose type cannot be derived statically keep
the key but carry no type, with a description saying why.
"""

from __future__ import annotations

import ast
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

JSON_TYPES_ORDER = ("string", "integer", "number", "boolean", "null", "array", "object")

# Odoo field class -> (JSON types, json format). `default=str` serialisation in the outbox
# turns dates/datetimes into strings and recordsets into "model(ids)" strings.
_ODOO_FIELD_TYPES: dict[str, tuple[set[str], str | None]] = {
    "Char": ({"string"}, None),
    "Text": ({"string"}, None),
    "Html": ({"string"}, None),
    "Selection": ({"string"}, None),
    "Reference": ({"string"}, None),
    "Binary": ({"string"}, None),
    "Image": ({"string"}, None),
    "Date": ({"string"}, "date"),
    "Datetime": ({"string"}, None),
    "Integer": ({"integer"}, None),
    "Float": ({"number"}, None),
    "Monetary": ({"number"}, None),
    "Boolean": ({"boolean"}, None),
    "Json": ({"object"}, None),
    "Properties": ({"object"}, None),
    "Many2one": ({"string"}, None),
    "One2many": ({"string"}, None),
    "Many2many": ({"string"}, None),
}
# Types Odoo never reads back as False (numeric defaults to 0, boolean is a boolean).
_NEVER_FALSE = {"Integer", "Float", "Monetary", "Boolean"}

_CALL_TYPES: dict[str, set[str]] = {
    "float": {"number"},
    "round": {"number"},
    "abs": {"number"},
    "sum": {"number"},
    "int": {"integer"},
    "len": {"integer"},
    "str": {"string"},
    "repr": {"string"},
    "bool": {"boolean"},
    "any": {"boolean"},
    "all": {"boolean"},
    "isinstance": {"boolean"},
    "list": {"array"},
    "sorted": {"array"},
    "tuple": {"array"},
    "set": {"array"},
    "dict": {"object"},
}
_METHOD_TYPES: dict[str, set[str]] = {
    "isoformat": {"string"},
    "strftime": {"string"},
    "to_string": {"string"},
    "lower": {"string"},
    "upper": {"string"},
    "strip": {"string"},
    "title": {"string"},
    "capitalize": {"string"},
    "join": {"string"},
    "format": {"string"},
    "replace": {"string"},
    "hexdigest": {"string"},
    "mapped": {"array"},
    "ids": {"array"},
    "copy": {"object"},
}


@dataclass
class OdooField:
    ftype: str
    required: bool
    comodel: str | None


@dataclass
class FieldIndex:
    """Odoo field declarations parsed from addons/ model classes."""

    by_model: dict[str, dict[str, OdooField]] = field(default_factory=lambda: defaultdict(dict))
    by_class: dict[int, str] = field(default_factory=dict)  # id(ClassDef) -> model name
    #: method name -> JSON types of its return annotation (None when ambiguous / absent)
    returns: dict[str, set[str] | None] = field(default_factory=dict)

    def lookup(self, model: str | None, name: str) -> OdooField | None:
        if model and name in self.by_model.get(model, {}):
            return self.by_model[model][name]
        return None

    def lookup_any(self, name: str) -> OdooField | None:
        """A field name declared with ONE consistent Odoo type across all models."""
        found = [f for fields_ in self.by_model.values() for n, f in fields_.items() if n == name]
        ftypes = {f.ftype for f in found}
        if len(ftypes) == 1:
            comodels = {f.comodel for f in found}
            return OdooField(
                ftypes.pop(),
                all(f.required for f in found),
                comodels.pop() if len(comodels) == 1 else None,
            )
        return None


@dataclass
class Ctx:
    """Inference context: the function the expression lives in and its parameter bindings."""

    func: ast.AST | None
    model: str | None
    index: FieldIndex
    bindings: dict[str, tuple[ast.AST, Ctx]] = field(default_factory=dict)
    depth: int = 0


@dataclass
class PublishSite:
    event_type: str
    module: str
    path: str
    line: int
    payload: dict[str, Any]
    keys: list[str] | None


@dataclass
class ScanResult:
    sites: dict[str, list[PublishSite]]
    composed: list[str]
    unresolved: list[str]


# ----------------------------------------------------------------------------- helpers


def _call_name(call: ast.Call) -> str | None:
    func = call.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _str_const(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _module_of(path: Path, module_dirs: dict[Path, str]) -> str | None:
    for parent in path.parents:
        if parent in module_dirs:
            return module_dirs[parent]
    return None


def _parse(path: Path) -> ast.Module | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return None


def _source_files(addons_dir: Path) -> list[Path]:
    return sorted(p for p in addons_dir.rglob("*.py") if "tests" not in p.parts)


def _class_model(cls: ast.ClassDef) -> str | None:
    """`_name`, else the (first) `_inherit` of an Odoo model class."""
    found: dict[str, Any] = {}
    for stmt in cls.body:
        if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1:
            target = stmt.targets[0]
            if isinstance(target, ast.Name) and target.id in ("_name", "_inherit"):
                value = stmt.value
                if isinstance(value, ast.List | ast.Tuple) and value.elts:
                    value = value.elts[0]
                if _str_const(value):
                    found[target.id] = _str_const(value)
    return found.get("_name") or found.get("_inherit")


def build_field_index(trees: dict[Path, ast.Module]) -> FieldIndex:
    index = FieldIndex()
    for tree in trees.values():
        for fn in (
            n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef)
        ):
            ret = _annotation_types(fn.returns)
            if fn.name in index.returns and index.returns[fn.name] != ret:
                index.returns[fn.name] = None
            else:
                index.returns.setdefault(fn.name, ret)
        for cls in (n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)):
            model = _class_model(cls)
            if not model:
                continue
            index.by_class[id(cls)] = model
            for stmt in cls.body:
                if not (isinstance(stmt, ast.Assign) and len(stmt.targets) == 1):
                    continue
                target, value = stmt.targets[0], stmt.value
                if not (isinstance(target, ast.Name) and isinstance(value, ast.Call)):
                    continue
                func = value.func
                if not (
                    isinstance(func, ast.Attribute)
                    and isinstance(func.value, ast.Name)
                    and func.value.id == "fields"
                    and func.attr in _ODOO_FIELD_TYPES
                ):
                    continue
                kwargs = {k.arg: k.value for k in value.keywords if k.arg}
                required = isinstance(kwargs.get("required"), ast.Constant) and bool(
                    kwargs["required"].value
                )
                comodel = _str_const(kwargs.get("comodel_name")) or (
                    _str_const(value.args[0])
                    if func.attr in ("Many2one", "One2many", "Many2many") and value.args
                    else None
                )
                index.by_model[model][target.id] = OdooField(func.attr, required, comodel)
    return index


# ----------------------------------------------------------------------------- type inference


def _union(*parts: tuple[set[str], str | None] | None) -> tuple[set[str], str | None] | None:
    types: set[str] = set()
    formats: set[str | None] = set()
    for part in parts:
        if part is None:
            return None
        types |= part[0]
        formats.add(part[1])
    return types, (formats.pop() if len(formats) == 1 else None)


def _assignments(func: ast.AST | None, name: str) -> list[ast.AST]:
    if func is None:
        return []
    values: list[ast.AST] = []
    for node in ast.walk(func):
        if isinstance(node, ast.Assign):
            if any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
                values.append(node.value)
        elif (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == name
            and node.value is not None
        ):
            values.append(node.value)
    return values


def _field_type(f: OdooField, through_optional_m2o: bool) -> tuple[set[str], str | None]:
    types, fmt = _ODOO_FIELD_TYPES[f.ftype]
    types = set(types)
    if through_optional_m2o or (f.ftype not in _NEVER_FALSE and not f.required):
        types.add("boolean")  # Odoo reads an unset value (or anything via an empty m2o) as False
    return types, fmt


_CHAINING_METHODS = {
    "browse",
    "search",
    "create",
    "sudo",
    "with_context",
    "with_company",
    "with_user",
    "filtered",
    "filtered_domain",
    "exists",
    "ensure_one",
    "new",
    "sorted",
    "copy",
}
_ANNOTATION_TYPES = {
    "int": "integer",
    "float": "number",
    "Decimal": "number",
    "str": "string",
    "bool": "boolean",
    "dict": "object",
    "list": "array",
    "tuple": "array",
    "None": "null",
}


_ENV_RECORDS = {"user": "res.users", "company": "res.company"}


def _is_env(node: ast.AST) -> bool:
    return isinstance(node, ast.Attribute) and node.attr == "env"


def _expr_model(expr: ast.AST, ctx: Ctx, depth: int = 0) -> str | None:
    """The Odoo model a record-valued expression holds, when statically evident."""
    if depth > 5:
        return None
    if isinstance(expr, ast.Name):
        return _name_model(expr.id, ctx, depth + 1)
    if isinstance(expr, ast.Subscript):
        value = expr.value
        if isinstance(value, ast.Attribute) and value.attr == "env":
            return _str_const(expr.slice)
        return _expr_model(value, ctx, depth + 1)
    if isinstance(expr, ast.Attribute) and _is_env(expr.value):
        return _ENV_RECORDS.get(expr.attr)
    if isinstance(expr, ast.Attribute):
        base = _expr_model(expr.value, ctx, depth + 1)
        f = ctx.index.lookup(base, expr.attr)
        return f.comodel if f else None
    if (
        isinstance(expr, ast.Call)
        and isinstance(expr.func, ast.Attribute)
        and expr.func.attr in _CHAINING_METHODS
    ):
        return _expr_model(expr.func.value, ctx, depth + 1)
    if isinstance(expr, ast.IfExp):
        return _expr_model(expr.body, ctx, depth + 1)
    return None


def _name_model(name: str, ctx: Ctx, depth: int = 0) -> str | None:
    if name == "self":
        return ctx.model
    if name in ctx.bindings:
        expr, caller = ctx.bindings[name]
        return _expr_model(expr, caller, depth + 1)
    if ctx.func is not None:
        for value in _assignments(ctx.func, name):
            model = _expr_model(value, ctx, depth + 1)
            if model:
                return model
        for node in ast.walk(ctx.func):
            if (
                isinstance(node, ast.For | ast.comprehension)
                and isinstance(node.target, ast.Name)
                and node.target.id == name
            ):
                model = _expr_model(node.iter, ctx, depth + 1)
                if model:
                    return model
    return ctx.model if name in ("rec", "record") else None


def _annotation_types(node: ast.AST | None) -> set[str] | None:
    if node is None:
        return None
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        left, right = _annotation_types(node.left), _annotation_types(node.right)
        return None if left is None or right is None else left | right
    name = node.id if isinstance(node, ast.Name) else _str_const(node)
    if isinstance(node, ast.Constant) and node.value is None:
        name = "None"
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name):
        name = node.value.id
    mapped = _ANNOTATION_TYPES.get(name or "")
    return {mapped} if mapped else None


def _param_type(name: str, ctx: Ctx) -> tuple[set[str], str | None] | None:
    """A parameter's JSON type from its annotation, else from its literal default."""
    func = ctx.func
    if not isinstance(func, ast.FunctionDef | ast.AsyncFunctionDef):
        return None
    args = func.args
    positional = [*args.posonlyargs, *args.args]
    names = [a.arg for a in positional]
    defaults = dict(zip(names[len(names) - len(args.defaults) :], args.defaults, strict=True))
    defaults.update(
        {a.arg: d for a, d in zip(args.kwonlyargs, args.kw_defaults, strict=True) if d is not None}
    )
    for arg in [*positional, *args.kwonlyargs]:
        if arg.arg != name:
            continue
        annotated = _annotation_types(arg.annotation)
        if annotated:
            return annotated, None
        if name in defaults:
            return infer(defaults[name], Ctx(None, ctx.model, ctx.index))
        return None
    return None


def infer(node: ast.AST, ctx: Ctx) -> tuple[set[str], str | None] | None:
    """JSON types (+format) the expression serialises to, or None when not derivable."""
    if ctx.depth > 6:
        return None
    if isinstance(node, ast.Constant):
        value = node.value
        if isinstance(value, bool):
            return {"boolean"}, None
        if isinstance(value, int):
            return {"integer"}, None
        if isinstance(value, float):
            return {"number"}, None
        if isinstance(value, str):
            return {"string"}, None
        if value is None:
            return {"null"}, None
        return None
    if isinstance(node, ast.JoinedStr):
        return {"string"}, None
    if isinstance(node, ast.Compare):
        return {"boolean"}, None
    if isinstance(node, ast.UnaryOp):
        if isinstance(node.op, ast.Not):
            return {"boolean"}, None
        return infer(node.operand, ctx)
    if isinstance(node, ast.BoolOp):
        return _union(*(infer(v, ctx) for v in node.values))
    if isinstance(node, ast.IfExp):
        return _union(infer(node.body, ctx), infer(node.orelse, ctx))
    if isinstance(node, ast.BinOp):
        if isinstance(node.op, ast.Mod) and isinstance(node.left, ast.Constant | ast.JoinedStr):
            return {"string"}, None
        left, right = infer(node.left, ctx), infer(node.right, ctx)
        if left is None or right is None:
            return None
        both = left[0] | right[0]
        if both <= {"integer"} and not isinstance(node.op, ast.Div):
            return {"integer"}, None
        if both <= {"integer", "number"}:
            return {"number"}, None
        if both == {"string"} and isinstance(node.op, ast.Add):
            return {"string"}, None
        return None
    if isinstance(node, ast.List | ast.ListComp | ast.Tuple | ast.Set | ast.SetComp):
        return {"array"}, None
    if isinstance(node, ast.GeneratorExp):
        return {"array"}, None
    if isinstance(node, ast.Dict | ast.DictComp):
        return {"object"}, None
    if isinstance(node, ast.Call):
        name = _call_name(node)
        if isinstance(node.func, ast.Name) and name in _CALL_TYPES:
            return set(_CALL_TYPES[name]), None
        if isinstance(node.func, ast.Attribute) and name in _METHOD_TYPES:
            return set(_METHOD_TYPES[name]), None
        returns = ctx.index.returns.get(name or "")
        return (set(returns), None) if returns else None
    if isinstance(node, ast.Name):
        if node.id in ctx.bindings:
            expr, caller = ctx.bindings[node.id]
            return infer(
                expr, Ctx(caller.func, caller.model, caller.index, caller.bindings, ctx.depth + 1)
            )
        values = _assignments(ctx.func, node.id)
        if not values:
            return _param_type(node.id, ctx)
        sub = Ctx(ctx.func, ctx.model, ctx.index, ctx.bindings, ctx.depth + 1)
        return _union(*(infer(v, sub) for v in values))
    if isinstance(node, ast.Attribute):
        return _infer_attribute(node, ctx)
    return None


def _infer_attribute(node: ast.Attribute, ctx: Ctx) -> tuple[set[str], str | None] | None:
    attr, receiver = node.attr, node.value
    if attr == "ids":
        return {"array"}, None
    if isinstance(receiver, ast.Name):
        if attr == "id":
            return {"integer"}, None
        f = ctx.index.lookup(_name_model(receiver.id, ctx), attr) or ctx.index.lookup_any(attr)
        if f is not None:
            return _field_type(f, False)
        if attr == "display_name":
            return {"string"}, None
        return ({"string", "boolean"}, None) if attr == "name" else None
    if isinstance(receiver, ast.Attribute):
        if _is_env(receiver.value):  # self.env.user / self.env.company: always set
            link, optional = None, False
        else:
            base_model = _expr_model(receiver.value, ctx)
            link = ctx.index.lookup(base_model, receiver.attr) or ctx.index.lookup_any(
                receiver.attr
            )
            optional = link is None or not link.required
        if attr == "id":
            return ({"integer", "boolean"} if optional else {"integer"}), None
        comodel = _expr_model(receiver, ctx) or (link.comodel if link else None)
        target = ctx.index.lookup(comodel, attr)
        if target is not None:
            return _field_type(target, optional)
        if attr == "display_name":
            return ({"string", "boolean"} if optional else {"string"}), None
        if attr in ("name", "code", "ref"):
            return {"string", "boolean"}, None
        return None
    return None


def property_schema(expr: ast.AST, ctx: Ctx, where: str) -> dict[str, Any]:
    inferred = infer(expr, ctx)
    if inferred is None:
        return {
            "description": (
                f"Type not statically derivable from `{ast.unparse(expr)[:100]}` ({where})."
            )
        }
    types, fmt = inferred
    ordered = [t for t in JSON_TYPES_ORDER if t in types]
    schema: dict[str, Any] = {"type": ordered[0] if len(ordered) == 1 else ordered}
    if fmt and "string" in types:
        schema["format"] = fmt
    return schema


def _dict_for(expr: ast.AST, ctx: Ctx) -> tuple[ast.Dict | None, Ctx]:
    """The dict literal a payload expression denotes (following names / bindings)."""
    for _ in range(4):
        if isinstance(expr, ast.Dict):
            return expr, ctx
        if isinstance(expr, ast.Name) and expr.id in ctx.bindings:
            expr, ctx = ctx.bindings[expr.id]
            continue
        if isinstance(expr, ast.Name):
            values = [v for v in _assignments(ctx.func, expr.id) if isinstance(v, ast.Dict)]
            if len(values) == 1:
                return values[0], ctx
        break
    return None, ctx


def payload_schema(
    expr: ast.AST | None, ctx: Ctx, where: str
) -> tuple[dict[str, Any], list[str] | None]:
    if expr is None:
        return {"type": "object", "description": f"no payload argument ({where})"}, None
    literal, lctx = _dict_for(expr, ctx)
    if literal is None:
        return (
            {
                "type": "object",
                "additionalProperties": True,
                "description": (
                    f"Payload built dynamically (`{ast.unparse(expr)[:100]}`, {where}); "
                    "its keys are not statically derivable."
                ),
            },
            None,
        )
    props: dict[str, Any] = {}
    keys: list[str] = []
    spread = False
    for key, value in zip(literal.keys, literal.values, strict=True):
        name = _str_const(key)
        if key is None or name is None:
            spread = True
            continue
        keys.append(name)
        props[name] = property_schema(value, lctx, where)
    schema: dict[str, Any] = {
        "type": "object",
        "required": list(keys),
        "properties": props,
        "additionalProperties": spread,
    }
    if spread:
        schema["description"] = (
            f"Payload spreads a mapping into the literal ({where}); keys beyond those listed "
            "are open."
        )
    return schema, keys


# ----------------------------------------------------------------------------- scanning


#: fix_events publishing calls -> (event-type argument index, payload argument index):
#: ``publish(env, type, aggregate, id, payload)`` from Odoo code, and
#: ``get_dual_bus().publish_dual(type, aggregate, id, payload)`` from L5 services.
PUBLISH_CALLS: dict[str, tuple[int, int]] = {"publish": (1, 4), "publish_dual": (0, 3)}


def _payload_arg(call: ast.Call, index: int = 4) -> ast.AST | None:
    if len(call.args) > index:
        return call.args[index]
    return next((k.value for k in call.keywords if k.arg == "payload"), None)


def _bind_call(fn: ast.FunctionDef, call: ast.Call) -> dict[str, ast.AST]:
    params = [a.arg for a in fn.args.args]
    if params and params[0] in ("self", "cls") and isinstance(call.func, ast.Attribute):
        params = params[1:]
    bound = dict(zip(params, call.args, strict=False))
    bound.update({k.arg: k.value for k in call.keywords if k.arg})
    return bound


def scan_publishers(addons_dir: Path, services_dir: Path | None = None) -> ScanResult:
    """Publishers in the Odoo addons and (optionally) the L5 services under services/."""
    repo_root = addons_dir.parent
    module_dirs = {p.parent: p.parent.name for p in addons_dir.rglob("__manifest__.py")}
    files = _source_files(addons_dir)
    if services_dir is not None and services_dir.is_dir():
        module_dirs.update({d: d.name for d in services_dir.iterdir() if d.is_dir()})
        files += _source_files(services_dir)
    trees = {p: t for p in files if (t := _parse(p)) is not None}
    index = build_field_index(trees)

    # enclosing function / class for every node, per file
    sites: dict[str, list[PublishSite]] = defaultdict(list)
    composed: list[str] = []
    unresolved: list[str] = []
    wrappers: list[tuple[str, str, ast.FunctionDef, Ctx, ast.Call, str, int]] = []
    functions_by_module: dict[str, list[tuple[Path, ast.FunctionDef, str | None]]] = defaultdict(
        list
    )

    for path, tree in trees.items():
        module = _module_of(path, module_dirs) or path.parent.name
        rel = path.relative_to(repo_root).as_posix()
        for cls_or_mod in [tree, *(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef))]:
            model = (
                index.by_class.get(id(cls_or_mod)) if isinstance(cls_or_mod, ast.ClassDef) else None
            )
            body = cls_or_mod.body
            for fn in (n for n in body if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef)):
                functions_by_module[module].append((path, fn, model))
                ctx = Ctx(fn, model, index)
                for call in (n for n in ast.walk(fn) if isinstance(n, ast.Call)):
                    spec = PUBLISH_CALLS.get(_call_name(call) or "")
                    if spec is None or len(call.args) <= spec[0]:
                        continue
                    type_index, payload_index = spec
                    where = f"{rel}:{call.lineno}"
                    etype_node = call.args[type_index]
                    literal = _str_const(etype_node)
                    params = [a.arg for a in fn.args.args]
                    if literal:
                        payload, keys = payload_schema(
                            _payload_arg(call, payload_index), ctx, where
                        )
                        sites[literal].append(
                            PublishSite(literal, module, rel, call.lineno, payload, keys)
                        )
                    elif isinstance(etype_node, ast.Name) and etype_node.id in params:
                        wrappers.append((module, rel, fn, ctx, call, etype_node.id, payload_index))
                    elif isinstance(etype_node, ast.Name):
                        values = _assignments(fn, etype_node.id)
                        names = [
                            s
                            for v in values
                            for s in (
                                [_str_const(v)]
                                if _str_const(v)
                                else [_str_const(v.body), _str_const(v.orelse)]
                                if isinstance(v, ast.IfExp)
                                else []
                            )
                            if s
                        ]
                        if not names:
                            unresolved.append(
                                f"{where}: event type `{etype_node.id}` not resolvable"
                            )
                        payload, keys = payload_schema(
                            _payload_arg(call, payload_index), ctx, where
                        )
                        for name in names:
                            sites[name].append(
                                PublishSite(name, module, rel, call.lineno, payload, keys)
                            )
                    elif isinstance(etype_node, ast.JoinedStr):
                        composed.append(f"{where}: `{ast.unparse(etype_node)}`")
                    else:
                        unresolved.append(f"{where}: event type `{ast.unparse(etype_node)}`")

    # wrapper helpers: every call of the helper in the same addon with a literal event type
    for module, rel, fn, wctx, pcall, param, payload_index in wrappers:
        found = False
        for path, caller_fn, caller_model in functions_by_module[module]:
            caller_rel = path.relative_to(repo_root).as_posix()
            caller_ctx = Ctx(caller_fn, caller_model, index)
            for call in (n for n in ast.walk(caller_fn) if isinstance(n, ast.Call)):
                if _call_name(call) != fn.name or call is pcall:
                    continue
                bound = _bind_call(fn, call)
                etype = _str_const(bound.get(param))
                if not etype:
                    continue
                found = True
                where = f"{caller_rel}:{call.lineno} via {fn.name}() at {rel}:{pcall.lineno}"
                bindings = {k: (v, caller_ctx) for k, v in bound.items()}
                ctx = Ctx(fn, wctx.model, index, bindings)
                payload, keys = payload_schema(_payload_arg(pcall, payload_index), ctx, where)
                sites[etype].append(
                    PublishSite(etype, module, caller_rel, call.lineno, payload, keys)
                )
        if not found:
            unresolved.append(f"{rel}:{pcall.lineno}: wrapper {fn.name}() has no literal callers")
    return ScanResult(dict(sites), sorted(set(composed)), sorted(set(unresolved)))


# ----------------------------------------------------------------------------- merging


def merge_payloads(event_sites: list[PublishSite]) -> dict[str, Any]:
    """One payload schema for all publish sites of an event type."""
    if len(event_sites) == 1:
        return event_sites[0].payload
    closed = [s for s in event_sites if s.keys is not None]
    if len(closed) != len(event_sites):
        return next(s.payload for s in event_sites if s.keys is None)
    required = set(closed[0].keys or [])
    for s in closed[1:]:
        required &= set(s.keys or [])
    props: dict[str, Any] = {}
    for s in closed:
        for key, prop in s.payload["properties"].items():
            if key not in props:
                props[key] = dict(prop)
            elif props[key] != prop:
                a, b = props[key].get("type"), prop.get("type")
                if a is None or b is None:
                    props[key] = {
                        "description": "Type not statically derivable at every publish site."
                    }
                else:
                    merged = {
                        *([a] if isinstance(a, str) else a),
                        *([b] if isinstance(b, str) else b),
                    }
                    ordered = [t for t in JSON_TYPES_ORDER if t in merged]
                    props[key] = {"type": ordered[0] if len(ordered) == 1 else ordered}
    order = list(dict.fromkeys(k for s in closed for k in (s.keys or [])))
    open_ = any(s.payload.get("additionalProperties") for s in closed)
    return {
        "type": "object",
        "required": [k for k in order if k in required],
        "properties": {k: props[k] for k in order},
        "additionalProperties": open_,
    }


def producer_of(event_sites: list[PublishSite]) -> str:
    counts = Counter(s.module for s in event_sites)
    return sorted(counts, key=lambda m: (-counts[m], m))[0]
