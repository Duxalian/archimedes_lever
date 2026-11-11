#!/usr/bin/env python3
"""Check a project log (docs/LOG.md) against the AGENTS.md "Project log" rules.

Usage:
    python3 scripts/log_check.py [FILE ...]        # default: docs/LOG.md
    python3 scripts/log_check.py --test            # self-test; prints LOG CHECK TEST PASS

Checks (each failure prints FILE:LINE: message):
- A "## Arcs" table with the columns Arc | Span | Summary | Outcome.
- A "## Log" table with the columns # | When (CT) | Type | Arc | Topic | Raised by | What the other missed | Evidence | Result.
- Every row has 9 cells; # is a whole number, unique, and rows are in # order.
- When: YYYY-MM-DD HH:MM, or a range YYYY-MM-DD HH:MM-HH:MM (en dash or hyphen), or a range across days
  YYYY-MM-DD HH:MM-YYYY-MM-DD HH:MM; "~" before the date or a time marks an estimate. Dates and times must exist.
- Type is milestone, breakthrough, miss or decision.
- Arc is kebab-case and has a row in the Arcs table; every Arcs row is used at least once.
- Evidence is not empty and not "-" (AGENTS.md: never chat text alone).
Exit 0 and "LOG CHECK PASS: N rows" when clean, exit 1 with the findings otherwise.
It does not judge whether a row's type or text is right; that stays a human review.
Standard library only. It reads files only; it never writes.
"""
import argparse
import datetime as dt
import pathlib
import re
import sys
import tempfile

LOG_COLS = ["#", "When (CT)", "Type", "Arc", "Topic", "Raised by", "What the other missed", "Evidence", "Result"]
ARC_COLS = ["Arc", "Span", "Summary", "Outcome"]
TYPES = {"milestone", "breakthrough", "miss", "decision"}
ARC_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DATE = r"\d{4}-\d{2}-\d{2}"
TIME = r"~?\d{2}:\d{2}"
WHEN_RE = re.compile(rf"^~?({DATE}) ({TIME})(?:\s?[–-]\s?(?:({DATE}) )?({TIME}))?$")


def cells(line):
    """Split a Markdown table row into stripped cells (escaped pipes stay in the cell)."""
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|") and not body.endswith("\\|"):
        body = body[:-1]
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", body)]


def tables(text):
    """Return {heading: (header_line_no, header_cells, [(line_no, cells), ...])} for the first table under each ## heading."""
    out, heading, i = {}, None, 0
    lines = text.splitlines()
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            heading = m.group(1)
        elif heading and heading not in out and line.strip().startswith("|"):
            head = cells(line)
            rows, j = [], i + 1
            if j < len(lines) and re.match(r"^\s*\|?\s*:?-{3,}", lines[j]):
                j += 1
            while j < len(lines) and lines[j].strip().startswith("|"):
                rows.append((j + 1, cells(lines[j])))
                j += 1
            out[heading] = (i + 1, head, rows)
            i = j
            continue
        i += 1
    return out


def valid_when(value):
    m = WHEN_RE.match(value)
    if not m:
        return False
    d1, t1, d2, t2 = m.groups()
    try:
        start = dt.datetime.strptime(f"{d1} {t1.lstrip('~')}", "%Y-%m-%d %H:%M")
        if t2:
            end = dt.datetime.strptime(f"{d2 or d1} {t2.lstrip('~')}", "%Y-%m-%d %H:%M")
            if end < start:
                return False
    except ValueError:
        return False
    return True


def check(path):
    """Return (row_count, [finding, ...]) for one log file."""
    p = pathlib.Path(path)
    found = []
    try:
        text = p.read_text(encoding="utf-8")
    except OSError as e:
        return 0, [f"{p}: cannot read ({e.strerror})"]
    t = tables(text)
    if "Arcs" not in t:
        found.append(f"{p}: no table under '## Arcs'")
    if "Log" not in t:
        found.append(f"{p}: no table under '## Log'")
        return 0, found
    arcs = {}
    if "Arcs" in t:
        ln, head, rows = t["Arcs"]
        if head != ARC_COLS:
            found.append(f"{p}:{ln}: Arcs columns must be {' | '.join(ARC_COLS)}")
        for ln, c in rows:
            if not c or not ARC_RE.match(c[0]):
                found.append(f"{p}:{ln}: arc name {c[0] if c else ''!r} is not kebab-case")
            elif c[0] in arcs:
                found.append(f"{p}:{ln}: arc {c[0]!r} listed twice")
            else:
                arcs[c[0]] = ln
    ln, head, rows = t["Log"]
    if head != LOG_COLS:
        found.append(f"{p}:{ln}: Log columns must be {' | '.join(LOG_COLS)}")
        return len(rows), found
    used, last = set(), None
    for ln, c in rows:
        if len(c) != len(LOG_COLS):
            if len(c) > 3:
                used.add(c[3])
            found.append(f"{p}:{ln}: {len(c)} cells, need {len(LOG_COLS)}")
            continue
        num, when, typ, arc, *_rest = c
        evidence = c[7]
        if not num.isdigit():
            found.append(f"{p}:{ln}: # {num!r} is not a whole number")
        else:
            n = int(num)
            if last is not None and n <= last:
                found.append(f"{p}:{ln}: # {n} is not after # {last} (unique, in order)")
            last = n
        if not valid_when(when):
            found.append(f"{p}:{ln}: When {when!r} is not YYYY-MM-DD HH:MM (or a range; ~ marks an estimate)")
        if typ not in TYPES:
            found.append(f"{p}:{ln}: Type {typ!r} is not one of {', '.join(sorted(TYPES))}")
        if not ARC_RE.match(arc):
            found.append(f"{p}:{ln}: Arc {arc!r} is not kebab-case")
        elif arc not in arcs:
            found.append(f"{p}:{ln}: Arc {arc!r} has no row in the Arcs table")
        used.add(arc)
        if evidence in ("", "-"):
            found.append(f"{p}:{ln}: Evidence is empty (a commit, file, test or measurement)")
    for arc, aln in arcs.items():
        if arc not in used:
            found.append(f"{p}:{aln}: arc {arc!r} is not used by any log row")
    return len(rows), found


GOOD = """# Project log: Demo

## Arcs

| Arc | Span | Summary | Outcome |
|---|---|---|---|
| setup | 2026-11-10 | Start. | Ready |
| flow-import | 2026-11-11 07:39–08:36 | Import. | Works |

## Log

| # | When (CT) | Type | Arc | Topic | Raised by | What the other missed | Evidence | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | 2026-11-10 22:11 | milestone | setup | Repo | Owner | - | Commit 63ae6e2 | Made |
| 1 | 2026-11-11 ~06:40 | miss | flow-import | A \\| B | Claude | gap | Test x | ok |
| 2 | 2026-11-11 07:57–08:20 | breakthrough | flow-import | T | Owner | - | Commit 8375b2e | ok |
| 3 | 2026-11-11 23:50–2026-11-12 00:10 | decision | flow-import | T | Owner | - | Commit abc | ok |
"""


def self_test():
    ok = True

    def expect(name, text, want):
        nonlocal ok
        with tempfile.TemporaryDirectory() as d:
            f = pathlib.Path(d, "LOG.md")
            f.write_text(text, encoding="utf-8")
            _, found = check(f)
        joined = "\n".join(found)
        good = (not found) if want is None else (want in joined)
        print(("ok   " if good else "FAIL ") + name + ("" if good else f"\n     got: {found}"))
        ok = ok and good

    expect("clean log passes", GOOD, None)
    expect("bad type", GOOD.replace("| miss |", "| oops |"), "Type 'oops'")
    expect("bad time", GOOD.replace("2026-11-10 22:11", "2026-11-10 25:11"), "When '2026-11-10 25:11'")
    expect("estimate before date ok", GOOD.replace("2026-11-11 ~06:40", "~2026-11-11 06:40"), None)
    expect("no date", GOOD.replace("2026-11-11 ~06:40", "~06:40"), "When '~06:40'")
    expect("range backwards", GOOD.replace("07:57–08:20", "08:20–07:57"), "When")
    expect("unknown arc", GOOD.replace("| breakthrough | flow-import |", "| breakthrough | other |"), "Arc 'other' has no row")
    expect("unused arc", GOOD.replace("| 0 | 2026-11-10 22:11 | milestone | setup |", "| 0 | 2026-11-10 22:11 | milestone | flow-import |"), "arc 'setup' is not used")
    expect("duplicate #", GOOD.replace("| 2 | 2026", "| 1 | 2026"), "# 1 is not after # 1")
    expect("empty evidence", GOOD.replace("Commit 8375b2e", "-"), "Evidence is empty")
    expect("missing cell", GOOD.replace("| Repo | Owner | - |", "| Repo | Owner |"), "8 cells")
    expect("wrong columns", GOOD.replace("| Evidence | Result |", "| Test / evidence | Result |"), "Log columns")
    expect("no arcs table", GOOD.split("## Arcs")[0] + "## Log" + GOOD.split("## Log")[1], "no table under '## Arcs'")
    print("LOG CHECK TEST " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("files", nargs="*", default=["docs/LOG.md"])
    ap.add_argument("--test", action="store_true", help="run the self-test")
    a = ap.parse_args()
    if a.test:
        return self_test()
    total, found = 0, []
    for f in a.files:
        n, fs = check(f)
        total += n
        found += fs
    for f in found:
        print(f)
    if found:
        print(f"LOG CHECK FAIL: {len(found)} finding(s)")
        return 1
    print(f"LOG CHECK PASS: {total} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
