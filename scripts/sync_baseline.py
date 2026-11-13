#!/usr/bin/env python3
"""Sync a project repo to the current rhope-ops/archimedes_lever baseline.

Run it from inside the project repo:
    python3 scripts/sync_baseline.py            # dry run: show the diff, write nothing
    python3 scripts/sync_baseline.py --apply    # write the files (commit them yourself)

Options:
    --baseline PATH_OR_URL   Baseline repo (default: https://github.com/rhope-ops/archimedes_lever)
    --name, --repo, --purpose   Header values, needed only when the project AGENTS.md has none.
    --timezone ZONE          IANA time zone for project log times, needed only when the project AGENTS.md has no
                             "- Time zone:" line (projects synced before 2026-11-11 have none).
    --owner NAME             Name agents use for the decider (default: the project's "- Owner:" line, else "the owner").
                             A public repo sets a role, for example --owner "the maintainer", so no real name is synced in.
    --tier starter|full      Kit tier (default: the project's "- Tier:" line, else "full", the only tier before 2026-11-13).
                             --tier full on a starter project adds the advanced parts (ADVANCED_FILES below, docs/LOG.md).
                             --tier starter on a full project keeps the advanced files and lists them for you to delete.
    --set-tier starter|full  Bootstrap only: apply the tier to THIS repo in place (AGENTS.md blocks; in starter, delete
                             ADVANCED_FILES). No baseline, no diff.

Tiers (the owner, 2026-11-13): a starter project has the core rules, hooks and checks only. AGENTS.md marks text
for one tier with lines "<!-- full -->" ... "<!-- /full -->" and "<!-- starter -->" ... "<!-- /starter -->";
apply_tier() keeps the blocks for the project's tier and drops the marker lines.

What it changes:
    AGENTS.md              Baseline text above "## Project rules", with this project's header values.
                           Keeps this project's "## Commands" section and everything from "## Project rules" on.
                           An AGENTS.md without the baseline layout goes under "## Project rules" as it is.
    CLAUDE.md              Adds "@AGENTS.md" at the top if it is missing. Keeps the rest.
    scripts/session_checkin.sh, scripts/stop_check.py, scripts/worker_guard.py,
    .claude/orchestration.md   Replaced with the baseline copies.
    .claude/agents/worker.md, scout.md, reviewer.md, GEMINI.md, docs/FIRST_USE.md   Added only when missing (a project
                           may tune them; FIRST_USE.md holds the denylist places that the session-start check names).
    scripts/log_check.py, scripts/timeline.py, scripts/pii_guard.py, scripts/first_use_check.py,
    scripts/check.sh, scripts/bloat_check.py, scripts/git-hooks/pre-push, .claude/bloat-audit.md, .claude/project-log.md,
    .claude/rule-tests.md
                           Replaced with the baseline copies. A starter project gets none of ADVANCED_FILES. (.pii-guard is not copied: a project opts in itself.)
    .claude/settings.json  Adds the baseline deny rules, each baseline hook event the project has no hook for, and the
                           baseline "sandbox" block when the project has none. Keeps all other settings.
    .gitignore             Adds the baseline lines. Keeps all other lines.
    docs/LOG.md            An Arcs table with the old columns (Arc | Span | Summary | Outcome) gets the story columns
                           Problem, Turning point and Lesson, each "-" (.claude/project-log.md). Rows are kept.
    docs/archimedes_lever-LICENSE.txt   The kit's license (MIT), which covers the copied files.
    Owner name             In baseline text only (AGENTS.md above "## Project rules" and the copied files, not this
                           script), "the owner" becomes the project owner ("The owner" becomes the owner with a capital
                           first letter). Project text is never renamed. A private repo may keep a real name
                           (--owner NAME); a public repo uses a role. Owner: letters, digits, space . _ , ( ) -
What it never changes: README.md, docs/ (except adding a missing docs/FIRST_USE.md and updating the kit license),
.pii-guard and all other files.
Standard library only. Needs git.
"""
import argparse
import difflib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_BASELINE = "https://github.com/rhope-ops/archimedes_lever"
RULES_HEADING = "## Project rules"
COMMANDS_HEADING = "## Commands"
COPY_FILES = ["scripts/session_checkin.sh", "scripts/stop_check.py",
              "scripts/worker_guard.py", "scripts/log_check.py", "scripts/timeline.py", "scripts/pii_guard.py", "scripts/first_use_check.py",
              "scripts/check.sh", "scripts/bloat_check.py", "scripts/git-hooks/pre-push",
              ".claude/orchestration.md", ".claude/bloat-audit.md", ".claude/project-log.md", ".claude/rule-tests.md", ".github/workflows/pii-guard.yml"]
# Agent definitions: copied only when the project has no file with that name (projects may tune them).
COPY_IF_MISSING = [".claude/agents/worker.md", ".claude/agents/scout.md", ".claude/agents/reviewer.md", "GEMINI.md",
                   "docs/FIRST_USE.md"]
BASELINE_OWNER = "the owner"  # role word in baseline text; no real name lives in the baseline
# Never rename the owner inside this script: it holds BASELINE_OWNER as a literal.
# first_use_check.py and docs/FIRST_USE.md use "the owner" as an answer option and a role: keep them as written
# (bootstrap.sh skips them too).
# Advanced parts: a starter project has none of these (one list for bootstrap, sync and drift).
ADVANCED_FILES = [".claude/orchestration.md", ".claude/agents/scout.md", ".claude/agents/worker.md",
                  ".claude/project-log.md", "docs/LOG.md", "scripts/log_check.py", "scripts/timeline.py",
                  ".claude/bloat-audit.md", "scripts/bloat_check.py", ".claude/rule-tests.md"]
TIERS = ("starter", "full")
NO_OWNER_RENAME = {"scripts/sync_baseline.py", "scripts/first_use_check.py", "docs/FIRST_USE.md"}
OWNER_RE = r"[A-Za-z0-9 ._,()-]+"  # safe inside Python strings, JSON and Markdown


def die(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def git(*args, cwd=None):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def get_baseline(src, tmp):
    path = Path(src)
    if path.is_dir():
        return path.resolve()
    dest = Path(tmp) / "baseline"
    try:
        git("clone", "--quiet", "--depth", "1", src, str(dest))
    except subprocess.CalledProcessError as e:
        die(f"cannot clone baseline {src}: {e.stderr.strip()}")
    return dest


def headings(text):
    """Yield (offset, line) for each '## ' heading line outside ``` code fences."""
    pos, fenced = 0, False
    for line in text.splitlines(True):
        if line.lstrip().startswith("```"):
            fenced = not fenced
        elif not fenced and line.startswith("## "):
            yield pos, line.rstrip()
        pos += len(line)


def find_heading(text, heading):
    """Offset of the heading line `heading` outside code fences, or -1."""
    for pos, line in headings(text):
        if line == heading:
            return pos
    return -1


def section(text, heading):
    """Return the block from `heading` to the next '## ' heading (outside code fences), or None."""
    start = find_heading(text, heading)
    if start < 0:
        return None
    for pos, _ in headings(text):
        if pos > start:
            return text[start:pos]
    return text[start:]


def header_values(text):
    name = re.search(r"^# (.+?): agent instructions\s*$", text, re.M)
    repo = re.search(r"^- Repo: (.+?)\s*$", text, re.M)
    purpose = re.search(r"^- Purpose: (.+?)\s*$", text, re.M)
    return (name and name.group(1), repo and repo.group(1), purpose and purpose.group(1))


def valid_timezone(name):
    """An IANA name the system knows (UTC always passes, also where the time zone database is missing)."""
    if name == "UTC":
        return True
    if not re.fullmatch(r"[A-Za-z0-9_+/-]+", name):
        return False
    try:
        import zoneinfo
        zoneinfo.ZoneInfo(name)
        return True
    except Exception:
        return False


def header_timezone(text):
    tz = re.search(r"^- Time zone: (.+?)\s*$", text or "", re.M)
    return tz and tz.group(1)


def header_tier(text):
    """The project's "- Tier:" value; "full" for projects made before tiers existed."""
    tier = re.search(r"^- Tier: (starter|full)\s*$", text or "", re.M)
    return tier.group(1) if tier else "full"


def apply_tier(text, tier):
    """Keep the marked blocks for `tier`, drop the other tier's blocks, and drop every marker line."""
    other = "starter" if tier == "full" else "full"
    text = re.sub(rf"(?ms)^<!-- {other} -->\n.*?^<!-- /{other} -->\n", "", text)
    return re.sub(rf"(?m)^<!-- /?{tier} -->\n", "", text)


def tier_files(tier):
    """Files the kit copies for this tier."""
    skip = set(ADVANCED_FILES) if tier == "starter" else set()
    return [f for f in COPY_FILES if f not in skip], [f for f in COPY_IF_MISSING if f not in skip]


def set_tier(root, tier):
    """Bootstrap step: apply the tier to this repo in place."""
    agents = root / "AGENTS.md"
    agents.write_text(apply_tier(agents.read_text(), tier).replace("{{TIER}}", tier))
    if tier == "starter":
        for rel in ADVANCED_FILES:
            (root / rel).unlink(missing_ok=True)
    print(f"Tier: {tier}" + (f" ({len(ADVANCED_FILES)} advanced files removed)" if tier == "starter" else ""))


def log_stamp(zone):
    """'YYYY-MM-DD HH:MM' now, in the project time zone (UTC when the zone database is missing)."""
    import datetime
    try:
        import zoneinfo
        tz = zoneinfo.ZoneInfo(zone)
    except Exception:
        tz = datetime.timezone.utc
    return datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M")


def header_owner(text):
    owner = re.search(r"^- Owner: (.+?)\s*$", text or "", re.M)
    return owner and owner.group(1)


def apply_owner(text, owner):
    """Replace the baseline role word ("the owner", "The owner") with the project owner."""
    if owner == BASELINE_OWNER:
        return text
    cap = owner[:1].upper() + owner[1:]
    # One pass with word boundaries: "the ownership" stays, and an owner that contains the role word is not re-replaced.
    return re.sub(r"\b([Tt])he owner\b", lambda m: cap if m.group(1) == "T" else owner, text)


def build_agents(base_text, proj_text, args, owner, tier="full"):
    found = header_values(proj_text) if proj_text else (None, None, None)
    name = args.name or found[0]
    repo = args.repo or found[1]
    purpose = args.purpose or found[2]
    timezone = args.timezone or header_timezone(proj_text)
    missing = [k for k, v in (("--name", name), ("--repo", repo), ("--purpose", purpose), ("--timezone", timezone)) if not v]
    if missing:
        die("the project AGENTS.md header lacks a value; give " + ", ".join(missing))

    cut = find_heading(base_text, RULES_HEADING)
    if cut < 0:
        die(f"the baseline AGENTS.md has no '{RULES_HEADING}' heading")
    head = base_text[:cut]
    for key, val in (("PROJECT_NAME", name), ("REPO", repo), ("PURPOSE", purpose), ("TIMEZONE", timezone), ("TIER", tier)):
        head = head.replace("{{" + key + "}}", val)
    head = apply_tier(head, tier)
    if "{{OWNER}}" in head:
        head = head.replace("{{OWNER}}", BASELINE_OWNER)

    head = apply_owner(head, owner)  # baseline text only; the project's own Commands and rules stay as written

    rules_at = find_heading(proj_text, RULES_HEADING) if proj_text else -1
    legacy = proj_text is not None and rules_at < 0
    if proj_text and not legacy:
        own_commands = section(proj_text, COMMANDS_HEADING)
        base_commands = section(head, COMMANDS_HEADING)
        if own_commands and base_commands:
            if not own_commands.endswith("\n\n"):
                own_commands = own_commands.rstrip("\n") + "\n\n"
            head = head.replace(base_commands, own_commands)
        tail = proj_text[rules_at:]
    else:
        tail = RULES_HEADING + "\n\n"
        if legacy and proj_text.strip():
            tail += "<!-- Migrated from the old AGENTS.md by sync_baseline.py. Review it: delete what the baseline now covers. -->\n\n"
            tail += proj_text.strip() + "\n"
    return head + tail


def merge_settings(base_path, proj_path):
    base = json.loads(base_path.read_text())
    try:
        proj = json.loads(proj_path.read_text()) if proj_path.exists() else {}
    except json.JSONDecodeError as e:
        die(f".claude/settings.json is not valid JSON ({e}); fix it first")
    if not isinstance(proj, dict):
        die(".claude/settings.json must be a JSON object; fix it first")
    if not isinstance(proj.get("permissions"), dict):
        if proj.get("permissions") not in (None,):
            die('.claude/settings.json "permissions" must be an object; fix it first')
        proj["permissions"] = {}
    deny = proj["permissions"].get("deny")
    if deny is None:
        deny = proj["permissions"]["deny"] = []
    if not isinstance(deny, list):
        die('.claude/settings.json "permissions.deny" must be a list; fix it first')
    for rule in base.get("permissions", {}).get("deny", []):
        if rule not in deny:
            deny.append(rule)
    # Sandbox: add the baseline block only when the project has none (a project's own block is kept whole).
    if "sandbox" in base and "sandbox" not in proj:
        proj["sandbox"] = base["sandbox"]
    # Hooks: add a baseline hook event only when the project has no hook for that event.
    base_hooks = base.get("hooks") or {}
    if base_hooks:
        hooks = proj.get("hooks")
        if hooks is None:
            hooks = proj["hooks"] = {}
        if not isinstance(hooks, dict):
            die('.claude/settings.json "hooks" must be an object; fix it first')
        for event, entries in base_hooks.items():
            if not hooks.get(event):
                hooks[event] = entries
    return json.dumps(proj, indent=2, ensure_ascii=False) + "\n"


NEW_ARCS = "| Arc | Span | Summary | Problem | Turning point | Outcome | Lesson |"


def migrate_arcs(text):
    """Add the story columns to an old 4-column Arcs table; return the text unchanged when there is none."""
    lines = text.split("\n")
    for i, line in enumerate(lines):
        head = [c.strip().lower() for c in line.strip().strip("|").split("|")]
        if head != [c.lower() for c in ("Arc", "Span", "Summary", "Outcome")]:
            continue
        lines[i] = NEW_ARCS
        j = i + 1
        if j < len(lines) and re.fullmatch(r"\s*\|(\s*:?-+:?\s*\|){4}\s*", lines[j]):
            lines[j] = "|---|---|---|---|---|---|---|"
            j += 1
        while j < len(lines) and lines[j].strip().startswith("|"):
            cells = re.split(r"(?<!\\)\|", lines[j].strip())[1:-1]
            if len(cells) == 4:
                a, span, summary, outcome = (c.strip() for c in cells)
                lines[j] = f"| {a} | {span} | {summary} | - | - | {outcome} | - |"
            j += 1
        break
    return "\n".join(lines)


def merge_lines(base_path, proj_path):
    lines = proj_path.read_text().splitlines() if proj_path.exists() else []
    add = [l for l in base_path.read_text().splitlines() if l.strip() and l not in lines]
    # Baseline lines go first, so a later project exception (for example "!.env.example") still wins.
    return "\n".join(add + lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description="Sync this project to the archimedes_lever baseline.")
    ap.add_argument("--apply", action="store_true", help="write the files (default: dry run)")
    ap.add_argument("--baseline", default=DEFAULT_BASELINE)
    ap.add_argument("--name")
    ap.add_argument("--repo")
    ap.add_argument("--purpose")
    ap.add_argument("--owner")
    ap.add_argument("--timezone", help="IANA time zone for project log times, for example Europe/Berlin")
    ap.add_argument("--tier", choices=TIERS, help="kit tier (default: the project's - Tier: line, else full)")
    ap.add_argument("--set-tier", choices=TIERS, help="bootstrap only: apply the tier to this repo in place")
    args = ap.parse_args()
    if args.timezone and not valid_timezone(args.timezone):
        die(f"time zone {args.timezone!r} is not a known IANA name (for example UTC, Europe/Berlin)")

    try:
        root = Path(git("rev-parse", "--show-toplevel"))
    except subprocess.CalledProcessError:
        die("run this inside the project git repo")
    if args.set_tier:
        set_tier(root, args.set_tier)
        return

    with tempfile.TemporaryDirectory() as tmp:
        base = get_baseline(args.baseline, tmp)
        if base.resolve() == root.resolve():
            die("this is the baseline repo itself; run the script in a project repo")
        try:
            if Path(git("rev-parse", "--show-toplevel", cwd=base)).resolve() != base.resolve():
                raise subprocess.CalledProcessError(1, "git")
            base_sha = git("rev-parse", "HEAD", cwd=base)
            if git("status", "--porcelain", cwd=base):
                base_sha += " (with uncommitted baseline changes)"
        except subprocess.CalledProcessError:
            base_sha = "unknown (baseline folder is not a git repo)"
        print(f"Kit baseline: {base_sha}. Projects do not keep the sync tools or a .baseline pin (the owner, 2026-11-13).")

        for f in [root / "AGENTS.md", root / "README.md", *sorted(root.glob("docs/*.md"))]:
            rel = f.relative_to(root)
            if f.is_file() and re.search(r"\{\{[A-Z_]+\}\}", f.read_text(errors="replace")):
                die(f"{rel} still has template placeholders; run scripts/bootstrap.sh first")

        proj_agents = root / "AGENTS.md"
        owner = args.owner or header_owner(proj_agents.read_text() if proj_agents.exists() else "") or BASELINE_OWNER
        if not re.fullmatch(OWNER_RE, owner):
            die(f"owner {owner!r}: use letters, digits, space . _ , ( ) - only")
        tier = args.tier or header_tier(proj_agents.read_text() if proj_agents.exists() else "")
        copy_files, copy_if_missing = tier_files(tier)
        new = {}
        new["AGENTS.md"] = build_agents(
            (base / "AGENTS.md").read_text(),
            proj_agents.read_text() if proj_agents.exists() else None,
            args,
            owner,
            tier,
        )
        claude = root / "CLAUDE.md"
        old_claude = claude.read_text() if claude.exists() else ""
        if not any(l.strip() == "@AGENTS.md" for l in old_claude.splitlines()):
            new["CLAUDE.md"] = "@AGENTS.md\n" + ("\n" + old_claude if old_claude.strip() else "")
        for rel in copy_files:
            if (base / rel).exists():
                text = (base / rel).read_text()
                new[rel] = text if rel in NO_OWNER_RENAME else apply_owner(text, owner)
        for rel in copy_if_missing:
            if (base / rel).exists() and not (root / rel).exists():
                text = (base / rel).read_text()
                new[rel] = text if rel in NO_OWNER_RENAME else apply_owner(text, owner)
        if (base / ".claude/settings.json").exists():
            new[".claude/settings.json"] = merge_settings(base / ".claude/settings.json", root / ".claude/settings.json")
        if (base / ".gitignore").exists():
            new[".gitignore"] = merge_lines(base / ".gitignore", root / ".gitignore")
        log = root / "docs/LOG.md"
        rules = section(proj_agents.read_text(), RULES_HEADING) if proj_agents.exists() else ""
        if tier == "full" and not log.is_file() and not re.search(r"(?i)project log", rules or "") and (base / "docs/LOG.md").exists():
            zone = header_timezone(new["AGENTS.md"]) or "UTC"
            stamp = log_stamp(zone)
            text = (base / "docs/LOG.md").read_text()
            name, _, _ = header_values(new["AGENTS.md"])
            for key, val in (("PROJECT_NAME", name or "Project"), ("TIMEZONE", zone),
                             ("DATE", stamp[:10]), ("TIME", stamp[11:])):
                text = text.replace("{{" + key + "}}", val)
            new["docs/LOG.md"] = apply_owner(text, owner)
        if log.is_file():
            migrated = migrate_arcs(log.read_text())
            if migrated != log.read_text():
                new["docs/LOG.md"] = migrated
        if (base / "LICENSE").exists():
            new["docs/archimedes_lever-LICENSE.txt"] = (base / "LICENSE").read_text()


        changed = []
        for rel, text in new.items():
            path = root / rel
            old = path.read_text() if path.exists() else ""
            if old == text:
                continue
            changed.append(rel)
            sys.stdout.writelines(difflib.unified_diff(
                old.splitlines(True), text.splitlines(True), f"a/{rel}", f"b/{rel}"))
            if not text.endswith("\n"):
                print()

        if tier == "starter":
            extra = [f for f in ADVANCED_FILES if (root / f).exists()]
            if extra:
                print(f"Tier starter: these advanced files are not synced; delete them by hand if you want: {', '.join(extra)}")
        if not changed:
            print("No changes: the project already matches the baseline.")
            return
        print(f"\n{len(changed)} file(s) to change: {', '.join(changed)}")
        if not args.apply:
            print("Dry run: nothing written. Run again with --apply to write.")
            return
        if git("status", "--porcelain", cwd=root):
            die("the project has uncommitted changes; commit them first")
        for rel in changed:
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(new[rel])
            if rel.endswith((".sh", ".py")) or rel.startswith("scripts/git-hooks/"):
                shutil.copymode(base / rel, path) if (base / rel).exists() else None
        print("Written. Review with 'git diff', then commit and push.")


if __name__ == "__main__":
    main()
