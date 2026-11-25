# -*- coding: utf-8 -*-
"""
mdparse — block + inline parser for the 1000FiX specification markdown.

The source specifications conform to a tightly controlled house dialect
(YAML front matter, ATX headings, GFM pipe tables, block quotes, fenced
ASCII state machines, hairline rules). This parser targets that dialect
precisely rather than being a general CommonMark implementation.
"""

import re

# ------------------------------------------------------------------ patterns
RE_FM = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
RE_H = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
RE_HR = re.compile(r"^\s{0,3}(-{3,}|\*{3,}|_{3,})\s*$")
RE_ROW = re.compile(r"^\s*\|(.+)\|\s*$")
RE_SEP = re.compile(r"^\s*\|[\s:|-]+\|\s*$")
RE_BQ = re.compile(r"^>\s?(.*)$")
RE_FENCE = re.compile(r"^\s*```+\s*([A-Za-z0-9_+-]*)\s*$")
RE_UL = re.compile(r"^(\s*)[-*+]\s+(.*)$")
RE_OL = re.compile(r"^(\s*)(\d+)[.)]\s+(.*)$")

RE_INLINE = re.compile(
    r"(\*\*\*(?P<bi>[^*]+)\*\*\*"
    r"|\*\*(?P<b>(?:[^*]|\*(?!\*))+)\*\*"
    r"|(?<![*\w])\*(?P<i>[^*\n]+)\*(?![*\w])"
    r"|`(?P<c>[^`]+)`"
    r"|\[(?P<lt>[^\]]+)\]\((?P<lu>[^)]+)\))"
)


def parse_frontmatter(text):
    m = RE_FM.match(text)
    if not m:
        return {}, text
    fm, body = {}, text[m.end() :]
    key = None
    for line in m.group(1).split("\n"):
        if not line.strip():
            continue
        mm = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", line)
        if mm:
            key = mm.group(1).strip()
            val = mm.group(2).strip().strip('"').strip("'")
            fm[key] = val
        elif key:
            fm[key] += " " + line.strip()
    return fm, body


def split_row(line):
    inner = RE_ROW.match(line).group(1)
    cells, buf, esc = [], "", False
    for ch in inner:
        if esc:
            buf += ch
            esc = False
        elif ch == "\\":
            esc = True
        elif ch == "|":
            cells.append(buf.strip())
            buf = ""
        else:
            buf += ch
    cells.append(buf.strip())
    return cells


def _align_from_sep(line):
    out = []
    for c in split_row(line):
        c = c.strip()
        if c.startswith(":") and c.endswith(":"):
            out.append("center")
        elif c.endswith(":"):
            out.append("right")
        else:
            out.append("left")
    return out


def parse_blocks(text):
    """Return a flat list of block dicts."""
    lines = text.split("\n")
    blocks, i, n = [], 0, len(lines)

    while i < n:
        line = lines[i]

        if not line.strip():
            i += 1
            continue

        # fenced block ------------------------------------------------------
        mf = RE_FENCE.match(line)
        if mf:
            lang = mf.group(1) or ""
            i += 1
            buf = []
            while i < n and not RE_FENCE.match(lines[i]):
                buf.append(lines[i])
                i += 1
            i += 1
            while buf and not buf[0].strip():
                buf.pop(0)
            while buf and not buf[-1].strip():
                buf.pop()
            blocks.append({"t": "code", "lang": lang, "lines": buf})
            continue

        # heading -----------------------------------------------------------
        mh = RE_H.match(line)
        if mh:
            blocks.append(
                {"t": "h", "level": len(mh.group(1)), "text": mh.group(2).strip()}
            )
            i += 1
            continue

        # rule ----------------------------------------------------------------
        if RE_HR.match(line):
            blocks.append({"t": "hr"})
            i += 1
            continue

        # table ---------------------------------------------------------------
        if RE_ROW.match(line) and i + 1 < n and RE_SEP.match(lines[i + 1]):
            header = split_row(line)
            align = _align_from_sep(lines[i + 1])
            i += 2
            rows = []
            while i < n and RE_ROW.match(lines[i]):
                rows.append(split_row(lines[i]))
                i += 1
            width = max([len(header)] + [len(r) for r in rows]) if rows else len(header)
            header = (header + [""] * width)[:width]
            rows = [(r + [""] * width)[:width] for r in rows]
            align = (align + ["left"] * width)[:width]
            blocks.append(
                {"t": "table", "header": header, "rows": rows, "align": align}
            )
            continue

        # block quote ---------------------------------------------------------
        if RE_BQ.match(line):
            buf = []
            while i < n and (
                RE_BQ.match(lines[i])
                or (
                    lines[i].strip()
                    and buf
                    and not RE_H.match(lines[i])
                    and not RE_ROW.match(lines[i])
                    and lines[i].startswith(" ")
                )
            ):
                m = RE_BQ.match(lines[i])
                buf.append(m.group(1) if m else lines[i].strip())
                i += 1
            blocks.append({"t": "quote", "children": parse_blocks("\n".join(buf))})
            continue

        # list ----------------------------------------------------------------
        mu, mo = RE_UL.match(line), RE_OL.match(line)
        if mu or mo:
            ordered = bool(mo)
            items = []
            while i < n:
                m2 = RE_OL.match(lines[i]) if ordered else RE_UL.match(lines[i])
                if m2:
                    indent = len(m2.group(1))
                    txt = m2.group(3) if ordered else m2.group(2)
                    items.append({"level": indent // 2, "text": txt})
                    i += 1
                elif (
                    lines[i].strip()
                    and lines[i].startswith(("   ", "\t"))
                    and items
                    and not RE_UL.match(lines[i])
                    and not RE_OL.match(lines[i])
                    and not RE_ROW.match(lines[i])
                ):
                    items[-1]["text"] += " " + lines[i].strip()
                    i += 1
                elif (
                    lines[i].strip()
                    and items
                    and not RE_H.match(lines[i])
                    and not RE_HR.match(lines[i])
                    and not RE_ROW.match(lines[i])
                    and not RE_BQ.match(lines[i])
                    and not RE_FENCE.match(lines[i])
                    and not RE_UL.match(lines[i])
                    and not RE_OL.match(lines[i])
                ):
                    break
                else:
                    break
            blocks.append({"t": "list", "ordered": ordered, "items": items})
            continue

        # paragraph -------------------------------------------------------------
        buf = [line.strip()]
        i += 1
        while i < n and lines[i].strip():
            if (
                RE_H.match(lines[i])
                or RE_HR.match(lines[i])
                or RE_ROW.match(lines[i])
                or RE_BQ.match(lines[i])
                or RE_FENCE.match(lines[i])
                or RE_UL.match(lines[i])
                or RE_OL.match(lines[i])
            ):
                break
            buf.append(lines[i].strip())
            i += 1
        blocks.append({"t": "p", "text": " ".join(buf)})

    return blocks


# --------------------------------------------------------------------- inline
def inline_runs(text, _inherit=None, _depth=0):
    """Split markdown inline into [(text, {'b','i','code','link'}), ...].

    Recursive: `**bold with `code` inside**` and `**bold [link](x)**` both
    resolve correctly, which the house dialect uses freely.
    """
    inherit = dict(_inherit or {})
    out, pos = [], 0

    def emit(chunk, flags):
        f = dict(inherit)
        f.update(flags)
        out.append((chunk, f))

    def descend(chunk, flags):
        if _depth >= 4 or not RE_INLINE.search(chunk):
            emit(chunk, flags)
            return
        merged = dict(inherit)
        merged.update(flags)
        out.extend(inline_runs(chunk, merged, _depth + 1))

    for m in RE_INLINE.finditer(text):
        if m.start() > pos:
            emit(text[pos : m.start()], {})
        if m.group("bi") is not None:
            descend(m.group("bi"), {"b": True, "i": True})
        elif m.group("b") is not None:
            descend(m.group("b"), {"b": True})
        elif m.group("i") is not None:
            descend(m.group("i"), {"i": True})
        elif m.group("c") is not None:
            emit(m.group("c"), {"code": True})
        elif m.group("lt") is not None:
            emit(m.group("lt"), {"link": m.group("lu")})
        pos = m.end()
    if pos < len(text):
        emit(text[pos:], {})
    return [(t, f) for t, f in out if t != ""]


def plain(text):
    """Strip inline markup, keep the words."""
    return "".join(t for t, _ in inline_runs(text)).strip()


# --------------------------------------------------------------- section view
def sectionise(blocks):
    """Group blocks under their '## n. Title' heading.

    Returns [(number:int|None, title:str, [blocks]), ...] plus a preamble
    entry with number None for anything before the first '##'.
    """
    out, cur = [], {"num": None, "title": "Preamble", "blocks": []}
    for b in blocks:
        if b["t"] == "h" and b["level"] == 2:
            out.append(cur)
            m = re.match(r"^(\d+)\.\s*(.*)$", plain(b["text"]))
            if m:
                cur = {
                    "num": int(m.group(1)),
                    "title": m.group(2).strip(),
                    "blocks": [],
                }
            else:
                cur = {"num": None, "title": plain(b["text"]), "blocks": []}
        else:
            cur["blocks"].append(b)
    out.append(cur)
    return [s for s in out if s["blocks"] or s["num"] is not None]


def tables_in(blocks):
    return [b for b in blocks if b["t"] == "table"]


def find_table(blocks, *header_keys, min_hits=1):
    """First table whose header row contains all/most of the given keys."""
    keys = [k.lower() for k in header_keys]
    best, best_hits = None, 0
    for b in blocks:
        if b["t"] != "table":
            continue
        hdr = " | ".join(plain(h).lower() for h in b["header"])
        hits = sum(1 for k in keys if k in hdr)
        if hits > best_hits:
            best, best_hits = b, hits
    return best if best_hits >= min_hits else None


def col_index(table, *names):
    for i, h in enumerate(table["header"]):
        hp = plain(h).lower().strip()
        for nm in names:
            if hp == nm.lower() or nm.lower() in hp:
                return i
    return None
