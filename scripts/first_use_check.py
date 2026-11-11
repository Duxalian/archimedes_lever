#!/usr/bin/env python3
"""Session-start check: is this repo set up, and can the personal-data guard check names here?

Usage:
    python3 scripts/first_use_check.py         # prints what the agent must do first; prints nothing when all is set
    python3 scripts/first_use_check.py --test  # self-test; prints FIRST USE TEST PASS

Claude Code runs it as a SessionStart hook (.claude/settings.json); its output goes into the session's context.
Other agents run it at the start of a session (AGENTS.md "Start of session").

It reports:
    FIRST USE       the repo still has template placeholders (a new project made from the template, not set up):
                    follow docs/FIRST_USE.md before any other work.
    DENYLIST        the repo has a .pii-guard file but this session has no name denylist, so pushes will be blocked.
The template repo itself (origin named archimedes_lever) keeps its placeholders on purpose and is skipped.
Exit 0 always: a session-start hook informs, it never blocks. Standard library only.
"""
import os
import pathlib
import re
import subprocess
import sys
import tempfile

TEMPLATE_NAME = "archimedes_lever"
PLACEHOLDER = re.compile(r"\{\{(PROJECT_NAME|REPO|PURPOSE|OWNER)\}\}")


def origin_name(root):
    r = subprocess.run(["git", "remote", "get-url", "origin"], cwd=root, capture_output=True, text=True)
    url = r.stdout.strip() if r.returncode == 0 else ""
    return re.sub(r"\.git$", "", url.rstrip("/")).rsplit("/", 1)[-1].lower()


def has_denylist():
    """Same rule as pii_guard.py (shared helper): the first source with at least one entry."""
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import pii_guard
    return pii_guard.denylist_source()[1] is not None


def messages(root):
    root = pathlib.Path(root)
    out = []
    try:
        agents = root / "AGENTS.md"
        text = agents.read_text(errors="replace") if agents.is_file() else ""
        first_use = PLACEHOLDER.search(text) and origin_name(root) != TEMPLATE_NAME
    except Exception as e:  # each check on its own: one failure must not hide the other
        first_use, text = False, ""
        out.append(f"first_use_check: placeholder check skipped ({e})")
    if first_use:
        out.append("FIRST USE: this repo was made from the template and is not set up yet. Before any other work, "
                   "follow docs/FIRST_USE.md: ask the owner its questions (in Claude Code, with the clickable "
                   "question dialog), then run scripts/bootstrap.sh with the answers.")
    try:
        guard_without_list = (root / ".pii-guard").is_file() and not has_denylist()
    except Exception as e:
        guard_without_list = False
        out.append(f"first_use_check: denylist check skipped ({e})")
    if guard_without_list:
        out.append("DENYLIST: this repo has the personal-data guard on, but this session has no name denylist, so "
                   "pushes will be blocked. Ask the owner to add the environment variable PII_GUARD_DENYLIST to this "
                   "cloud environment (environment menu in the session title bar > Edit > Environment variables; "
                   "names comma separated; a new session picks it up), or, on their own computer, the file "
                   "~/.config/pii-guard/denylist.txt. Never ask for the names in chat. Details: docs/FIRST_USE.md.")
    return out


def self_test():
    ok = True

    def expect(name, got, want):
        nonlocal ok
        good = got == want
        print(("ok   " if good else "FAIL ") + f"{name}: {got}")
        ok = ok and good

    saved = {k: os.environ.pop(k, None) for k in ("PII_GUARD_DENYLIST", "PII_GUARD_DENYLIST_FILE")}
    os.environ["PII_GUARD_DENYLIST_FILE"] = os.devnull + ".missing"
    try:
        with tempfile.TemporaryDirectory() as d:
            run = lambda *a: subprocess.run(["git", *a], cwd=d, check=True, capture_output=True)
            run("init", "-q", "-b", "main")
            agents = pathlib.Path(d, "AGENTS.md")
            agents.write_text("# {{PROJECT_NAME}}: agent instructions\n")
            run("remote", "add", "origin", "https://github.com/someone/new-project.git")
            kinds = lambda: [m.split(":")[0] for m in messages(d)]
            expect("new project with placeholders", kinds(), ["FIRST USE"])
            run("remote", "set-url", "origin", "https://github.com/someone/Archimedes_Lever.git")
            expect("template repo skipped", kinds(), [])
            pathlib.Path(d, ".pii-guard").write_text("# on\n")
            expect("guard on, no denylist", kinds(), ["DENYLIST"])
            os.environ["PII_GUARD_DENYLIST"] = "Sam"
            expect("guard on, denylist in environment", kinds(), [])
            os.environ.pop("PII_GUARD_DENYLIST")
            agents.write_text("# Demo: agent instructions\n")
            run("remote", "set-url", "origin", "https://github.com/someone/demo")
            expect("set-up project, guard on, no denylist", kinds(), ["DENYLIST"])
            pathlib.Path(d, ".pii-guard").unlink()
            expect("set-up project, guard off", kinds(), [])
    finally:
        for k, v in saved.items():
            os.environ.pop(k, None)
            if v is not None:
                os.environ[k] = v
    print("FIRST USE TEST " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main():
    if "--test" in sys.argv[1:]:
        return self_test()
    r = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    root = r.stdout.strip() if r.returncode == 0 else os.environ.get("CLAUDE_PROJECT_DIR", ".")
    for m in messages(root):
        print(m)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # a session-start hook must never break the session
        print(f"first_use_check: skipped ({e})")
        sys.exit(0)
