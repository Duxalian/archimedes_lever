#!/usr/bin/env python3
"""Report how a project repo differs from the archimedes_lever baseline. Report only: it never writes.

Usage:
    python3 scripts/drift.py [--project DIR] [--baseline PATH_OR_URL] [--owner NAME] [--strict]
    python3 scripts/drift.py --test        # self-test; prints DRIFT TEST PASS

For each "## " section of the baseline AGENTS.md above "## Project rules" (owner name and header placeholders
applied as sync_baseline.py would; --owner NAME for a repo with no "- Owner:" line, as for sync), it prints one of:
    same       the project has the section with the same text (whitespace ignored)
    changed    the project has a section with that heading but other text; NN% = text similarity,
               "missing lines" = baseline lines not found anywhere in the project AGENTS.md
    missing    no section with that heading
"## Commands" is project-owned and only checked for presence.
For each file sync_baseline.py copies: same, differs or missing. It also checks the .claude/settings.json deny rules
and hook events, the .baseline pin, and docs/LOG.md (present, and "LOG CHECK PASS" from scripts/log_check.py).

The numbers say where a repo has drifted, not which side is right: a project may keep its own wording on purpose
(for example a repo whose rules predate the baseline). Use the report to choose hand edits or a sync.
Exit 0 always, unless --strict and something is not "same" (exit 1).
Standard library only; it imports sync_baseline.py from this folder for the shared parsing.
"""
import argparse
import difflib
import json
import pathlib
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sync_baseline as sb  # noqa: E402

PROJECT_OWNED = {sb.COMMANDS_HEADING}


def norm(text):
    return re.sub(r"\s+", " ", text).strip()


def sections(text, stop=None):
    """Return {heading_line: section_text} for '## ' headings outside code fences, up to `stop` if given."""
    marks = list(sb.headings(text))
    out = {}
    for i, (pos, line) in enumerate(marks):
        if stop and line == stop:
            break
        end = marks[i + 1][0] if i + 1 < len(marks) else len(text)
        out.setdefault(line, text[pos:end])
    return out


def baseline_head(base_text, proj_text, owner):
    cut = sb.find_heading(base_text, sb.RULES_HEADING)
    head = base_text[:cut] if cut >= 0 else base_text
    name, repo, purpose = sb.header_values(proj_text or "")
    for key, val in (("PROJECT_NAME", name), ("REPO", repo), ("PURPOSE", purpose), ("OWNER", sb.BASELINE_OWNER),
                     ("TIMEZONE", sb.header_timezone(proj_text or ""))):
        if val:
            head = head.replace("{{" + key + "}}", val)
    return sb.apply_owner(head, owner)


def report(project, base, owner=None):
    """Return (rows, not_same_count). rows = list of (area, item, status, detail)."""
    rows = []
    proj_agents = project / "AGENTS.md"
    proj_text = proj_agents.read_text() if proj_agents.exists() else ""
    owner = owner or sb.header_owner(proj_text) or sb.BASELINE_OWNER
    base_text = (base / "AGENTS.md").read_text()
    head = baseline_head(base_text, proj_text, owner)
    proj_secs = sections(proj_text)
    proj_lines = {norm(l) for l in proj_text.splitlines() if norm(l)}
    if not proj_text:
        rows.append(("AGENTS.md", "file", "missing", ""))
    for heading, body in sections(head).items():
        name = heading[3:]
        if heading not in proj_secs:
            rows.append(("AGENTS.md", name, "missing", ""))
            continue
        if heading in PROJECT_OWNED:
            rows.append(("AGENTS.md", name, "same", "project-owned; presence only"))
            continue
        a, b = norm(body), norm(proj_secs[heading])
        if a == b:
            rows.append(("AGENTS.md", name, "same", ""))
            continue
        ratio = difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()
        lines = [norm(l) for l in body.splitlines()[1:] if norm(l)]
        gone = sum(1 for l in lines if l not in proj_lines)
        rows.append(("AGENTS.md", name, "changed", f"{ratio:.0%} similar; {gone}/{len(lines)} baseline lines missing"))
    if sb.find_heading(proj_text, sb.RULES_HEADING) < 0 and proj_text:
        rows.append(("AGENTS.md", "Project rules", "missing", "no baseline layout; sync would migrate the whole file"))

    for rel in sb.COPY_FILES + sb.COPY_IF_MISSING:
        src, dst = base / rel, project / rel
        if not src.exists():
            continue
        if not dst.exists():
            rows.append(("file", rel, "missing", ""))
            continue
        want = src.read_text()
        if rel not in sb.NO_OWNER_RENAME:
            want = sb.apply_owner(want, owner)
        rows.append(("file", rel, "same" if want == dst.read_text() else "differs",
                     "may be tuned per project" if rel in sb.COPY_IF_MISSING and want != dst.read_text() else ""))

    bset, pset = base / ".claude/settings.json", project / ".claude/settings.json"
    if bset.exists():
        try:
            b = json.loads(bset.read_text())
            p = json.loads(pset.read_text()) if pset.exists() else {}
            deny_missing = [r for r in b.get("permissions", {}).get("deny", [])
                            if r not in (p.get("permissions") or {}).get("deny", [])]
            rows.append(("settings", "deny rules", "same" if not deny_missing else "differs",
                         f"{len(deny_missing)} missing: {', '.join(deny_missing)}" if deny_missing else ""))
            for event in (b.get("hooks") or {}):
                have = event in (p.get("hooks") or {})
                rows.append(("settings", f"hook {event}", "same" if have else "missing",
                             "project has its own hook for this event" if have else ""))
        except (ValueError, AttributeError) as e:
            rows.append(("settings", ".claude/settings.json", "differs", f"not valid JSON ({e})"))

    pin = project / ".baseline"
    try:
        base_sha = sb.git("rev-parse", "HEAD", cwd=base)
    except subprocess.CalledProcessError:
        base_sha = None
    if not pin.exists():
        rows.append(("pin", ".baseline", "missing", "never synced"))
    else:
        got = pin.read_text().split()
        sha = got[1] if len(got) > 1 else ""
        same = bool(base_sha) and base_sha.startswith(sha[:7]) and sha[:7] != ""
        rows.append(("pin", ".baseline", "same" if same else "differs",
                     f"pinned {sha[:7] or '?'}, baseline {base_sha[:7] if base_sha else '?'}"))

    log = project / "docs/LOG.md"
    checker = base / "scripts/log_check.py"
    rules = sb.section(proj_text, sb.RULES_HEADING) or ""
    if not log.exists() and re.search(r"(?i)project log location", rules):
        rows.append(("log", "docs/LOG.md", "same", "kept elsewhere, named in Project rules"))
    elif not log.exists():
        rows.append(("log", "docs/LOG.md", "missing", "Project rules name no other place"))
    elif checker.exists():
        r = subprocess.run([sys.executable, str(checker), str(log)], capture_output=True, text=True)
        last = (r.stdout.strip().splitlines() or ["?"])[-1]
        rows.append(("log", "docs/LOG.md", "same" if r.returncode == 0 else "differs", last))
    not_same = sum(1 for r in rows if r[2] != "same")
    return rows, not_same


def print_report(project, rows, not_same):
    print(f"Drift report: {project}")
    width = max(len(f"{a}: {i}") for a, i, _, _ in rows) if rows else 10
    for area, item, status, detail in rows:
        print(f"  {status:8} {(area + ': ' + item):<{width}}  {detail}".rstrip())
    print(f"DRIFT: {not_same} of {len(rows)} item(s) not the same as the baseline")


def self_test():
    ok = True
    base = pathlib.Path(__file__).resolve().parent.parent
    if "{{PROJECT_NAME}}" not in (base / "AGENTS.md").read_text():
        print("DRIFT TEST SKIP: the self-test needs the baseline repo ([old handle]/archimedes_lever); run it there")
        return 0
    with tempfile.TemporaryDirectory() as d:
        proj = pathlib.Path(d)

        def get(item):
            rows, _ = report(proj, base)
            return {(a, i): (s, det) for a, i, s, det in rows}.get(item, ("absent", ""))

        def expect(name, got, want):
            nonlocal ok
            good = got[0] == want
            print(("ok   " if good else "FAIL ") + f"{name}: {got[0]} {got[1]}".rstrip())
            ok = ok and good

        (proj / "AGENTS.md").write_text("# Old rules\n\n## Git safety\n\nBe careful.\n")
        expect("legacy file: Project rules missing", get(("AGENTS.md", "Project rules")), "missing")
        expect("changed section", get(("AGENTS.md", "Git safety")), "changed")
        expect("missing section", get(("AGENTS.md", "Delegation")), "missing")
        expect("missing copied file", get(("file", "scripts/stop_check.py")), "missing")
        expect("never synced", get(("pin", ".baseline")), "missing")
        text = (base / "AGENTS.md").read_text()
        for k, v in (("PROJECT_NAME", "Demo"), ("REPO", "D/d"), ("PURPOSE", "P"), ("OWNER", "the maintainer"),
                     ("TIMEZONE", "Europe/Berlin")):
            text = text.replace("{{" + k + "}}", v)
        (proj / "AGENTS.md").write_text(sb.apply_owner(text, "the maintainer"))
        expect("synced section, owner renamed", get(("AGENTS.md", "Delegation")), "same")
        expect("Project rules present", get(("AGENTS.md", "Project rules")), "absent")
        (proj / "scripts").mkdir()
        (proj / "scripts/stop_check.py").write_text(sb.apply_owner((base / "scripts/stop_check.py").read_text(), "the maintainer"))
        expect("copied file, owner renamed", get(("file", "scripts/stop_check.py")), "same")
        text = (base / "AGENTS.md").read_text().replace("- Owner: {{OWNER}}\n", "")
        for k, v in (("PROJECT_NAME", "Demo"), ("REPO", "D/d"), ("PURPOSE", "P"), ("TIMEZONE", "UTC")):
            text = text.replace("{{" + k + "}}", v)
        (proj / "AGENTS.md").write_text(sb.apply_owner(text, "Sam"))
        rows, _ = report(proj, base, "Sam")
        expect("no Owner line, --owner Sam", {(a, i): (s, d) for a, i, s, d in rows}[("AGENTS.md", "Order of authority")], "same")
    print("DRIFT TEST " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--project", default=".", help="project repo folder (default: current folder)")
    ap.add_argument("--baseline", default=sb.DEFAULT_BASELINE, help="baseline folder or git URL")
    ap.add_argument("--owner", help="owner name for a project AGENTS.md without a \"- Owner:\" line")
    ap.add_argument("--strict", action="store_true", help="exit 1 when anything is not the same")
    ap.add_argument("--test", action="store_true", help="run the self-test")
    a = ap.parse_args()
    if a.test:
        return self_test()
    project = pathlib.Path(a.project).resolve()
    with tempfile.TemporaryDirectory() as tmp:
        base = sb.get_baseline(a.baseline, tmp)
        rows, not_same = report(project, base, a.owner)
        print_report(project, rows, not_same)
    return 1 if a.strict and not_same else 0


if __name__ == "__main__":
    sys.exit(main())
