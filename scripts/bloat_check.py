#!/usr/bin/env python3
"""Cheap bloat and drift metrics for a project repo, and the bloat-audit due date. Report only, unless --record.

Usage:
    python3 scripts/bloat_check.py            # full report
    python3 scripts/bloat_check.py --brief    # one line (scripts/session_checkin.sh runs this)
    python3 scripts/bloat_check.py --time     # also run each timed command in .bloat-audit.json and compare
    python3 scripts/bloat_check.py --time --record   # run them and store the new seconds as the baseline
    python3 scripts/bloat_check.py --strict   # exit 1 when a budget is over or the audit is due
    python3 scripts/bloat_check.py --test     # self-test; prints BLOAT TEST PASS

It measures:
    start read    lines, bytes and ~tokens (bytes / 4) of the files every session reads first
                  (AGENTS.md, CLAUDE.md, GEMINI.md, docs/NEXT_PROMPT.md, docs/DECISIONS.md, plus "start_read" in the config)
    handoff       docs/NEXT_PROMPT.md lines
    duplicates    normalized text lines of 80+ characters found in 2 or more tracked files
    big files     tracked files over the size budget
    audit due     days and commits on main since the last full audit (.bloat-audit.json "last_audit")
    timings       (--time) wall time of each named command against its recorded baseline

.bloat-audit.json (project-owned; the full audit in .claude/bloat-audit.md writes it). All keys are optional:
    {"last_audit": {"date": "YYYY-MM-DD", "commit": "<sha>", "report": "<path>"},
     "every_days": 14, "every_commits": 30,
     "budgets": {"start_read_tokens": 12000, "start_read_warn_tokens": 6000, "handoff_lines": 40, "file_kb": 500, "duplicate_lines": 20},
     "start_read": [], "ignore": ["ref/**"],
     "timings": {"tests": {"cmd": "tests/run.sh", "seconds": 20.8, "max_slowdown": 0.25}}}
start_read_warn_tokens only warns (never "over", never fails --strict); set it to the cap to turn the warning off.
A repo with no .bloat-audit.json (for example right after its first sync) reports AUDIT DUE (never audited): the first
audit creates the file. Exit 0, unless --strict and something is over (exit 1). Standard library only. Needs git.
"""
import argparse
import contextlib
import datetime
import io
import fnmatch
import json
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

CONFIG = ".bloat-audit.json"
START_READ = ["AGENTS.md", "CLAUDE.md", "GEMINI.md", "docs/NEXT_PROMPT.md", "docs/DECISIONS.md"]
DEFAULTS = {"every_days": 14, "every_commits": 30,
            "budgets": {"start_read_tokens": 12000, "start_read_warn_tokens": 6000, "handoff_lines": 40, "file_kb": 500, "duplicate_lines": 20}}
TEXT_EXT = {".md", ".txt", ".py", ".sh", ".ps1", ".psm1", ".js", ".ts", ".json", ".yml", ".yaml", ".html", ".css",
            ".toml", ".ini", ".cfg", ".csv", ""}
MIN_DUP = 80          # characters in a normalized line before it counts as a duplicate
MAX_SCAN = 1_000_000  # bytes; larger files are not scanned for duplicates


def git(root, *args):
    try:
        r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    except OSError:
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def load_config(root):
    cfg = json.loads(json.dumps(DEFAULTS))
    p = root / CONFIG
    if p.exists():
        data = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("top level is not an object")
        budgets = {**cfg["budgets"], **data.get("budgets", {})}
        cfg.update(data)
        cfg["budgets"] = budgets
    return cfg


def ignored(rel, cfg):
    return any(fnmatch.fnmatch(rel, g) for g in cfg.get("ignore", []))


def start_read(root, cfg):
    lines = size = 0
    files = []
    for rel in START_READ + cfg.get("start_read", []):
        p = root / rel
        if p.is_file():
            b = p.read_bytes()
            lines += b.count(b"\n")
            size += len(b)
            files.append((rel, len(b)))
    return lines, size, size // 4, sorted(files, key=lambda f: -f[1])


def norm(line):
    line = re.sub(r"^[\s>#|*\-+0-9.]+", "", line)
    return re.sub(r"\s+", " ", line).strip().lower()


def scan_files(root, cfg):
    out = git(root, "ls-files")
    return [rel for rel in (out.splitlines() if out else []) if not ignored(rel, cfg) and (root / rel).is_file()]


def duplicates(root, files):
    seen = {}
    for rel in files:
        p = root / rel
        if p.suffix.lower() not in TEXT_EXT or p.stat().st_size > MAX_SCAN:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for line in text.splitlines():
            n = norm(line)
            if len(n) >= MIN_DUP:
                seen.setdefault(n, set()).add(rel)
    dups = [(n, sorted(fs)) for n, fs in seen.items() if len(fs) > 1]
    return sorted(dups, key=lambda d: -len(d[1]))


def big_files(root, files, kb):
    return sorted(((rel, (root / rel).stat().st_size // 1024) for rel in files
                   if (root / rel).stat().st_size > kb * 1024), key=lambda f: -f[1])


def audit_due(root, cfg, today):
    last = cfg.get("last_audit") or {}
    if not last.get("date"):
        return "never audited"
    reasons = []
    days = (today - datetime.date.fromisoformat(last["date"])).days
    if days >= int(cfg["every_days"]):
        reasons.append(f"{days} days since {last['date']}")
    if last.get("commit"):
        n = git(root, "rev-list", "--count", f"{last['commit']}..HEAD")
        if n is not None and int(n) >= int(cfg["every_commits"]):
            reasons.append(f"{n} commits since {last['commit'][:7]}")
    return "; ".join(reasons)


def run_timings(root, cfg, record):
    rows, slow = [], []
    for name, t in cfg.get("timings", {}).items():
        t0 = time.monotonic()
        rc = subprocess.run(t["cmd"], shell=True, cwd=root, capture_output=True).returncode
        secs = round(time.monotonic() - t0, 1)
        base = t.get("seconds")
        limit = t.get("max_slowdown", 0.25)
        verdict = "FAILED" if rc else "new" if base is None else ("SLOWER" if secs > base * (1 + limit) else "ok")
        if verdict in ("SLOWER", "FAILED"):
            slow.append(name)
        rows.append(f"  {name}: {secs} s (baseline {base or '-'} s, limit +{int(limit * 100)}%, exit {rc}) {verdict}")
        if record and not rc:
            t["seconds"] = secs
    return rows, slow


def report(root, args, today=None):
    today = today or datetime.date.today()
    try:
        cfg = load_config(root)
        due = audit_due(root, cfg, today)
    except (ValueError, TypeError, KeyError) as e:
        print(f"bloat:       {CONFIG} unreadable ({e}); fix it, then run scripts/bloat_check.py")
        return 1 if args.strict else 0
    b = cfg["budgets"]
    files = scan_files(root, cfg)
    s_lines, s_bytes, s_tok, s_files = start_read(root, cfg)
    hp = root / "docs/NEXT_PROMPT.md"
    h_lines = hp.read_bytes().count(b"\n") if hp.exists() else 0
    dups = duplicates(root, files)
    big = big_files(root, files, b["file_kb"])
    over = []
    if s_tok > b["start_read_tokens"]:
        over.append("start read")
    # Early warning only (never fails --strict): rule growth shows before the hard cap (the owner, 2026-11-13).
    warn = "start read over warning" if b.get("start_read_warn_tokens", 0) < s_tok <= b["start_read_tokens"] else ""
    if h_lines > b["handoff_lines"]:
        over.append("handoff")
    if len(dups) > b["duplicate_lines"]:
        over.append("duplicates")
    if big:
        over.append("big files")
    t_rows, slow = run_timings(root, cfg, args.record) if args.time else ([], [])
    over += [f"timing {n}" for n in slow]
    if args.record and args.time:
        data = json.loads((root / CONFIG).read_text(encoding="utf-8")) if (root / CONFIG).exists() else {}
        data["timings"] = cfg.get("timings", {})
        (root / CONFIG).write_text(json.dumps(data, indent=2) + "\n")

    tail = f"AUDIT DUE ({due}): follow .claude/bloat-audit.md" if due else "audit not due"
    if args.brief:
        print(f"bloat:       start read ~{s_tok:,} tokens (budget {b['start_read_tokens']:,}) · duplicate lines "
              f"{len(dups)} · big files {len(big)} · over: {', '.join(over) or 'none'}{' · ' + warn if warn else ''} · {tail}")
    else:
        print(f"start read:  {s_lines} lines, {s_bytes:,} bytes, ~{s_tok:,} tokens (budget {b['start_read_tokens']:,})")
        for rel, size in s_files:
            print(f"  {rel}: {size:,} bytes")
        print(f"handoff:     docs/NEXT_PROMPT.md {h_lines} lines (budget {b['handoff_lines']})")
        print(f"duplicates:  {len(dups)} lines of {MIN_DUP}+ characters in 2+ files (budget {b['duplicate_lines']})")
        for n, fs in dups[:10]:
            print(f"  {len(fs)} files: {', '.join(fs[:4])}{' ...' if len(fs) > 4 else ''} :: {n[:70]}")
        print(f"big files:   {len(big)} over {b['file_kb']} KB" + "".join(f"\n  {r}: {k} KB" for r, k in big[:10]))
        if t_rows:
            print("timings:\n" + "\n".join(t_rows))
        print(f"over budget: {', '.join(over) or 'none'}")
        if warn:
            print(f"warning:     {warn} ({b['start_read_warn_tokens']:,} tokens); trim rules before the cap")
        print(tail)
    return 1 if args.strict and (over or due) else 0


def self_test():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        long = "This line is long enough to count as a duplicate when it shows up in two different files of a repo."
        (root / "AGENTS.md").write_text(f"# A\n- {long}\n")
        (root / "docs").mkdir()
        (root / "docs/NEXT_PROMPT.md").write_text(f"{long.upper()}\n" + "x\n" * 45)
        (root / "big.txt").write_text("y" * 3000)
        (root / CONFIG).write_text(json.dumps({"budgets": {"file_kb": 2, "start_read_tokens": 10},
                                               "last_audit": {"date": "2026-01-01"},
                                               "timings": {"t": {"cmd": "true", "seconds": 5}}}))
        subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
        cfg = load_config(root)
        files = scan_files(root, cfg)
        assert len(duplicates(root, files)) == 1, "duplicate across files, case and bullets ignored"
        assert [f for f, _ in big_files(root, files, 2)] == ["big.txt"], "big file"
        assert "days since" in audit_due(root, cfg, datetime.date(2026, 2, 1)), "due by days"
        assert audit_due(root, cfg, datetime.date(2026, 1, 5)) == "", "not due"
        assert audit_due(root, {**cfg, "last_audit": None}, datetime.date(2026, 1, 5)) == "never audited"
        rows, slow = run_timings(root, cfg, record=False)
        assert not slow and "ok" in rows[0], "fast command is ok"
        a = argparse.Namespace(brief=False, time=False, record=False, strict=True)
        with contextlib.redirect_stdout(io.StringIO()):
            assert report(root, a, datetime.date(2026, 1, 5)) == 1, "strict fails when over budget"
        (root / CONFIG).write_text(json.dumps({"budgets": {"start_read_warn_tokens": 1, "start_read_tokens": 99999},
                                               "last_audit": {"date": "2026-01-01"}}))
        w = io.StringIO()
        with contextlib.redirect_stdout(w):
            report(root, argparse.Namespace(brief=True, time=False, record=False, strict=False), datetime.date(2026, 1, 5))
        assert "over warning" in w.getvalue() and "over: start read" not in w.getvalue(), "warning, not over"
        with contextlib.redirect_stdout(io.StringIO()):
            assert audit_due(root, {**cfg, "last_audit": {"date": "2026-01-01", "commit": "f" * 40}},
                             datetime.date(2026, 1, 5)) == "", "unknown commit alone is not due"
            (root / CONFIG).write_text("{bad")
            assert report(root, a, datetime.date(2026, 1, 5)) == 1, "bad config: message, no traceback"
            (root / CONFIG).write_text(json.dumps({"timings": {"f": {"cmd": "false"}, "t": {"cmd": "true"}}}))
            report(root, argparse.Namespace(brief=True, time=True, record=True, strict=False))
        saved = json.loads((root / CONFIG).read_text())["timings"]
        assert "seconds" not in saved["f"] and saved["t"]["seconds"] is not None, "record skips failed commands"
    print("BLOAT TEST PASS")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--brief", action="store_true")
    ap.add_argument("--time", action="store_true")
    ap.add_argument("--record", action="store_true")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--test", action="store_true")
    ap.add_argument("--project", default=".")
    args = ap.parse_args()
    if args.test:
        self_test()
        return 0
    root = Path(git(Path(args.project), "rev-parse", "--show-toplevel") or args.project)
    return report(root, args)


if __name__ == "__main__":
    sys.exit(main())
