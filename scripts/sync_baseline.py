#!/usr/bin/env python3
"""Sync a project repo to the current Duxalian/archimedes_lever baseline.

Run it from inside the project repo:
    python3 scripts/sync_baseline.py            # dry run: show the diff, write nothing
    python3 scripts/sync_baseline.py --apply    # write the files (commit them yourself)

Options:
    --baseline PATH_OR_URL   Baseline repo (default: https://github.com/Duxalian/archimedes_lever)
    --name, --repo, --purpose   Header values, needed only when the project AGENTS.md has none.
    --owner NAME             Name agents use for the decider (default: the project's "- Owner:" line, else "the owner").
                             A public repo sets a role, for example --owner "the maintainer", so no real name is synced in.

What it changes:
    AGENTS.md              Baseline text above "## Project rules", with this project's header values.
                           Keeps this project's "## Commands" section and everything from "## Project rules" on.
                           An AGENTS.md without the baseline layout goes under "## Project rules" as it is.
    CLAUDE.md              Adds "@AGENTS.md" at the top if it is missing. Keeps the rest.
    scripts/session_checkin.sh, scripts/sync_baseline.py, scripts/stop_check.py, scripts/worker_guard.py,
    .claude/orchestration.md   Replaced with the baseline copies.
    .claude/agents/worker.md, scout.md, reviewer.md, GEMINI.md   Added only when missing (a project may tune them).
    scripts/log_check.py, scripts/drift.py, scripts/timeline.py, scripts/pii_guard.py, scripts/git-hooks/pre-push
                           Replaced with the baseline copies. (.pii-guard is not copied: a project opts in itself.)
    .claude/settings.json  Adds the baseline deny rules, and each baseline hook event the project has no hook for.
                           Keeps all other settings.
    .gitignore             Adds the baseline lines. Keeps all other lines.
    .baseline              Records the baseline commit that was used.
    Owner name             In baseline text only (AGENTS.md above "## Project rules" and the copied files, not this
                           script), "the owner" becomes the project owner ("The owner" becomes the owner with a capital
                           first letter). Project text is never renamed. A private repo may keep a real name
                           (--owner NAME); a public repo uses a role. Owner: letters, digits, space . _ , ( ) -
What it never changes: docs/, README.md and all other files.
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

DEFAULT_BASELINE = "https://github.com/Duxalian/archimedes_lever"
RULES_HEADING = "## Project rules"
COMMANDS_HEADING = "## Commands"
COPY_FILES = ["scripts/session_checkin.sh", "scripts/sync_baseline.py", "scripts/stop_check.py",
              "scripts/worker_guard.py", "scripts/log_check.py", "scripts/drift.py", "scripts/timeline.py", "scripts/pii_guard.py",
              "scripts/git-hooks/pre-push",
              ".claude/orchestration.md"]
# Agent definitions: copied only when the project has no file with that name (projects may tune them).
COPY_IF_MISSING = [".claude/agents/worker.md", ".claude/agents/scout.md", ".claude/agents/reviewer.md", "GEMINI.md"]
BASELINE_OWNER = "the owner"  # role word in baseline text; no real name lives in the baseline
# Never rename the owner inside this script: it holds BASELINE_OWNER as a literal.
NO_OWNER_RENAME = {"scripts/sync_baseline.py"}
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


def header_owner(text):
    owner = re.search(r"^- Owner: (.+?)\s*$", text or "", re.M)
    return owner and owner.group(1)


def apply_owner(text, owner):
    """Replace the baseline role word ("the owner", "The owner") with the project owner."""
    if owner == BASELINE_OWNER:
        return text
    cap = owner[:1].upper() + owner[1:]
    return text.replace(BASELINE_OWNER, owner).replace(BASELINE_OWNER[:1].upper() + BASELINE_OWNER[1:], cap)


def build_agents(base_text, proj_text, args, owner):
    found = header_values(proj_text) if proj_text else (None, None, None)
    name = args.name or found[0]
    repo = args.repo or found[1]
    purpose = args.purpose or found[2]
    missing = [k for k, v in (("--name", name), ("--repo", repo), ("--purpose", purpose)) if not v]
    if missing:
        die("the project AGENTS.md has no baseline header; give " + ", ".join(missing))

    cut = find_heading(base_text, RULES_HEADING)
    if cut < 0:
        die(f"the baseline AGENTS.md has no '{RULES_HEADING}' heading")
    head = base_text[:cut]
    for key, val in (("PROJECT_NAME", name), ("REPO", repo), ("PURPOSE", purpose)):
        head = head.replace("{{" + key + "}}", val)
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
    args = ap.parse_args()

    try:
        root = Path(git("rev-parse", "--show-toplevel"))
    except subprocess.CalledProcessError:
        die("run this inside the project git repo")

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

        for f in [root / "AGENTS.md", root / "README.md", *sorted(root.glob("docs/*.md"))]:
            rel = f.relative_to(root)
            if f.is_file() and re.search(r"\{\{[A-Z_]+\}\}", f.read_text(errors="replace")):
                die(f"{rel} still has template placeholders; run scripts/bootstrap.sh first")

        proj_agents = root / "AGENTS.md"
        owner = args.owner or header_owner(proj_agents.read_text() if proj_agents.exists() else "") or BASELINE_OWNER
        if not re.fullmatch(OWNER_RE, owner):
            die(f"owner {owner!r}: use letters, digits, space . _ , ( ) - only")
        new = {}
        new["AGENTS.md"] = build_agents(
            (base / "AGENTS.md").read_text(),
            proj_agents.read_text() if proj_agents.exists() else None,
            args,
            owner,
        )
        claude = root / "CLAUDE.md"
        old_claude = claude.read_text() if claude.exists() else ""
        if not any(l.strip() == "@AGENTS.md" for l in old_claude.splitlines()):
            new["CLAUDE.md"] = "@AGENTS.md\n" + ("\n" + old_claude if old_claude.strip() else "")
        for rel in COPY_FILES:
            if (base / rel).exists():
                text = (base / rel).read_text()
                new[rel] = text if rel in NO_OWNER_RENAME else apply_owner(text, owner)
        for rel in COPY_IF_MISSING:
            if (base / rel).exists() and not (root / rel).exists():
                new[rel] = apply_owner((base / rel).read_text(), owner)
        if (base / ".claude/settings.json").exists():
            new[".claude/settings.json"] = merge_settings(base / ".claude/settings.json", root / ".claude/settings.json")
        if (base / ".gitignore").exists():
            new[".gitignore"] = merge_lines(base / ".gitignore", root / ".gitignore")
        new[".baseline"] = f"Duxalian/archimedes_lever {base_sha}\n"


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
