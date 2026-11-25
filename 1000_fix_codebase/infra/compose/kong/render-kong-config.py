#!/usr/bin/env python3
"""Render infra/compose/kong/kong.prod.yml into a Kong declarative config.

Kong does not expand environment variables inside a declarative file, so the
staging/production deploy renders the `${NAME}` placeholders first:

    render-kong-config.py <template> <output>

* Each `${NAME}` takes its value from the environment variable NAME, or - when
  NAME_FILE is set - from the file it names (docker / Kubernetes secrets).
* Full-line YAML comments are copied verbatim (they document the placeholders).
* Fail closed (exit 1, nothing written) when any placeholder is missing/empty
  or a value would change the YAML structure:
    - single-line values must match a conservative character allowlist
      (host names, URLs: letters, digits, `.` `-` `_` `:` `/`);
    - only names ending in _PUBLIC_KEY may be multi-line, and must be an RSA
      public key: a PEM block, or the bare base64 body Keycloak's realm "Keys"
      tab shows (wrapped into a PEM block here). Continuation lines are
      indented like the placeholder line, so a `|` block scalar stays valid.
* The output is written atomically, mode 0644 (Kong reads it as a non-root user).

Stdlib only (runs in the pinned python:3.12-slim image as a compose one-shot
service / Kubernetes initContainer). Contains no secrets and prints none.
"""

from __future__ import annotations

import base64
import binascii
import os
import re
import sys
import tempfile
import textwrap
from pathlib import Path

PLACEHOLDER = re.compile(r"\$\{([A-Z][A-Z0-9_]*)\}")
SAFE_VALUE = re.compile(r"^[A-Za-z0-9._:/\-]+$")
PEM_BLOCK = re.compile(r"^-----BEGIN PUBLIC KEY-----\n[A-Za-z0-9+/=\n]+\n-----END PUBLIC KEY-----$")


class RenderError(Exception):
    pass


def lookup(name: str, env: dict[str, str]) -> str:
    file_var = env.get(f"{name}_FILE", "").strip()
    if file_var:
        try:
            value = Path(file_var).read_text(encoding="utf-8")
        except OSError as exc:
            raise RenderError(f"{name}_FILE={file_var!r} is not readable: {exc.strerror}") from exc
    else:
        value = env.get(name, "")
    value = value.strip().replace("\r\n", "\n")
    if not value:
        raise RenderError(f"{name} is not set (set {name} or {name}_FILE)")
    return value


def normalise_public_key(name: str, value: str) -> str:
    if value.startswith("-----BEGIN"):
        if not PEM_BLOCK.match(value):
            raise RenderError(f"{name} is not a PEM 'PUBLIC KEY' block")
        body = "".join(value.splitlines()[1:-1])
    else:
        body = "".join(value.split())
    try:
        base64.b64decode(body, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise RenderError(f"{name} is not valid base64 key material") from exc
    return (
        "-----BEGIN PUBLIC KEY-----\n"
        + "\n".join(textwrap.wrap(body, 64))
        + "\n-----END PUBLIC KEY-----"
    )


def checked_value(name: str, env: dict[str, str]) -> str:
    value = lookup(name, env)
    if name.endswith("_PUBLIC_KEY"):
        return normalise_public_key(name, value)
    if not SAFE_VALUE.match(value):
        raise RenderError(
            f"{name} contains characters outside [A-Za-z0-9._:/-] (refused: could alter the YAML)"
        )
    return value


def render(template: str, env: dict[str, str]) -> str:
    errors: list[str] = []
    cache: dict[str, str] = {}
    out: list[str] = []
    for line in template.splitlines(keepends=True):
        stripped = line.lstrip()
        if stripped.startswith("#"):
            out.append(line)
            continue
        indent = line[: len(line) - len(stripped)]

        def substitute(match: re.Match[str], indent: str = indent) -> str:
            name = match.group(1)
            if name not in cache:
                try:
                    cache[name] = checked_value(name, env)
                except RenderError as exc:
                    errors.append(str(exc))
                    cache[name] = ""
            return cache[name].replace("\n", "\n" + indent)

        out.append(PLACEHOLDER.sub(substitute, line))
    if errors:
        raise RenderError("; ".join(sorted(set(errors))))
    if not cache:
        raise RenderError("template contains no ${NAME} placeholders - wrong file?")
    rendered = "".join(out)
    leftover = [
        ln for ln in rendered.splitlines() if "${" in ln and not ln.lstrip().startswith("#")
    ]
    if leftover:
        raise RenderError(f"unrendered placeholder syntax remains: {leftover[0].strip()!r}")
    return rendered


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: render-kong-config.py <template> <output>", file=sys.stderr)
        return 2
    template, output = Path(argv[0]), Path(argv[1])
    try:
        rendered = render(template.read_text(encoding="utf-8"), dict(os.environ))
    except (OSError, RenderError) as exc:
        print(f"render-kong-config: refusing to write {output}: {exc}", file=sys.stderr)
        return 1
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=output.parent, prefix=".kong-", suffix=".yml")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(rendered)
    os.chmod(tmp, 0o644)
    os.replace(tmp, output)
    print(f"render-kong-config: wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
