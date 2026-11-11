#!/usr/bin/env python3
"""Block personal data before it reaches the remote: emails, phone numbers, .internal addresses, ID-number shapes, and
names from a denylist that is kept outside the repo.

Usage:
    python3 scripts/pii_guard.py --all             # every tracked file (working tree)
    python3 scripts/pii_guard.py --range A..B      # commits in A..B: added lines, messages, author and committer
    python3 scripts/pii_guard.py --push            # pre-push hook mode: reads the hook's stdin lines
    python3 scripts/pii_guard.py FILE ...          # these files
    python3 scripts/pii_guard.py --test            # self-test; prints PII GUARD TEST PASS

Opt-in: the guard runs only in a repo with a `.pii-guard` file at its root (the hook and the Action check for it).
That file lists exact strings that are allowed (one per line, `#` comments). Only the owner adds entries;
agents never add one to get past a block (AGENTS.md "Personal data").

Name denylist (never committed): one name or word per line, `#` comments, matched whole-word, any case.
    - env PII_GUARD_DENYLIST: the list itself (newline or comma separated); the GitHub Action reads it from the
      Actions secret of the same name.
    - env PII_GUARD_DENYLIST_FILE, else ~/.config/pii-guard/denylist.txt
With no denylist, names are not checked and the guard says so (exit code unchanged).

Checks:
    email      any address, except *@users.noreply.github.com, noreply@ / no-reply@ addresses, and the
               reserved example domains (example.com/.org/.net, *.example, *.invalid, *.test, *.localhost)
    internal        any .internal address or host name (email or web)
    phone      US numbers (NNN-NNN-NNNN, (NNN) NNN-NNNN, NNN.NNN.NNNN), +country numbers, ORG numbers
    id         SSN shape (NNN-NN-NNNN); a 10-digit number next to ORGID / ORG ID / BADGE
    name       denylist words
Matches are printed masked, so CI logs do not repeat them. Exit 1 when anything is found.
Standard library only. Needs git (except for FILE mode).
"""
import argparse
import os
import pathlib
import re
import subprocess
import sys
import tempfile

ZERO = re.compile(r"^0+$")
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
INTERNAL = re.compile(r"(?i)\b[A-Za-z0-9._%+-]*[A-Za-z0-9-]\.internal\b(?![.-][A-Za-z0-9])")
PHONE = [
    re.compile(r"(?<![\w.-])\(?\d{3}\)?[-. ]\d{3}[-.]\d{4}(?![\w-])"),
    re.compile(r"(?<![\w.-])\(\d{3}\) ?\d{3}[-. ]\d{4}(?![\w-])"),
    re.compile(r"(?<![\w+])\+\d{1,3}[ -]\(?\d{1,4}\)?[ -]\d{2,4}[ -]\d{3,4}(?![\w-])"),
    re.compile(r"(?i)\bDSN:?\s*\d{3}[-. ]\d{4}\b"),
]
SSN = re.compile(r"(?<![\w-])\d{3}-\d{2}-\d{4}(?![\w-])")
ORGID = re.compile(r"(?i)\b(?:ORGID|ORG ?ID|ORGID|BADGE)\b\D{0,20}(\d{10})\b")
ALLOWED_EMAIL = re.compile(
    r"(?i)(@users\.noreply\.github\.com$|^(no-?reply)@|@example\.(com|org|net)$|\.(example|invalid|test|localhost)$)")
SKIP_SUFFIX = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip", ".gz", ".woff", ".woff2", ".ttf")
MAX_BYTES = 2_000_000


def mask(s):
    return s if len(s) <= 4 else s[:2] + "*" * (len(s) - 4) + s[-2:]


def load_denylist():
    raw = os.environ.get("PII_GUARD_DENYLIST", "")
    path = os.environ.get("PII_GUARD_DENYLIST_FILE") or os.path.expanduser("~/.config/pii-guard/denylist.txt")
    if not raw and os.path.isfile(path):
        raw = pathlib.Path(path).read_text(errors="replace")
    words = []
    for line in re.split(r"[\n,]", raw):
        w = line.split("#", 1)[0].strip()
        if w:
            words.append(w)
    return words


def load_allow(root):
    f = pathlib.Path(root) / ".pii-guard"
    if not f.is_file():
        return set()
    return {l.split("#", 1)[0].strip() for l in f.read_text().splitlines() if l.split("#", 1)[0].strip()}


def scan_text(text, where, deny, allow):
    """Return findings (where, line_no, kind, masked) for one text."""
    found = []
    name_re = re.compile(r"(?i)(?<![A-Za-z0-9])(" + "|".join(re.escape(w) for w in deny) + r")(?![A-Za-z0-9])") if deny else None
    for n, line in enumerate(text.splitlines(), 1):
        hits = []
        for m in EMAIL.finditer(line):
            if not ALLOWED_EMAIL.search(m.group()):
                hits.append(("email", m.group()))
        hits += [("internal", m.group()) for m in INTERNAL.finditer(line)]
        for rx in PHONE:
            hits += [("phone", m.group()) for m in rx.finditer(line)]
        hits += [("id", m.group()) for m in SSN.finditer(line)]
        hits += [("id", m.group(1)) for m in ORGID.finditer(line)]
        if name_re:
            hits += [("name", m.group(1)) for m in name_re.finditer(line)]
        seen = set()
        for kind, val in hits:
            if val in allow or any(val in a for a in allow if kind != "name") or (kind, val) in seen:
                continue
            seen.add((kind, val))
            found.append((where, n, kind, mask(val)))
    return found


def git(*args, root="."):
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True,
                          errors="replace").stdout


def scan_files(paths, root, deny, allow):
    found = []
    for p in paths:
        f = pathlib.Path(root) / p
        if not f.is_file() or f.suffix.lower() in SKIP_SUFFIX or f.stat().st_size > MAX_BYTES:
            continue
        data = f.read_bytes()
        if b"\0" in data[:8192]:
            continue
        found += scan_text(data.decode("utf-8", "replace"), str(p), deny, allow)
    return found


def scan_commits(revs, root, deny, allow):
    """revs: arguments for git rev-list. Scan each commit's identity, message and added lines."""
    found = []
    shas = git("rev-list", *revs, root=root).split()
    for sha in shas:
        short = sha[:7]
        meta = git("show", "-s", "--format=%an%n%ae%n%cn%n%ce%n%B", sha, root=root)
        lines = meta.split("\n")
        ident = "\n".join(lines[:4])
        found += [(f"commit {short} author/committer", n, k, v) for _, n, k, v in scan_text(ident, "", deny, allow)]
        found += [(f"commit {short} message", n, k, v) for _, n, k, v in scan_text("\n".join(lines[4:]), "", deny, allow)]
        patch = git("show", "--format=", "--unified=0", "--no-color", "--no-ext-diff", sha, root=root)
        cur = "?"
        for line in patch.splitlines():
            if line.startswith("+++ "):
                cur = line[6:] if line.startswith("+++ b/") else line[4:]
            elif line.startswith("+") and not cur.endswith(SKIP_SUFFIX):
                found += [(f"commit {short} {cur}", "+", k, v) for _, _, k, v in scan_text(line[1:], "", deny, allow)]
    return found, len(shas)


def push_revs(stdin_text, root):
    """Turn pre-push stdin lines into rev-list argument lists (one per pushed ref)."""
    out = []
    for line in stdin_text.splitlines():
        parts = line.split()
        if len(parts) != 4 or ZERO.match(parts[1]):
            continue
        lsha, rsha = parts[1], parts[3]
        known = not ZERO.match(rsha) and subprocess.run(
            ["git", "cat-file", "-e", rsha + "^{commit}"], cwd=root, capture_output=True).returncode == 0
        out.append([f"{rsha}..{lsha}"] if known else [lsha, "--not", "--remotes"])
    return out


def report(found, what, deny):
    for where, n, kind, val in found:
        print(f"pii-guard: {where}:{n}: {kind}: {val}")
    names = f"names checked ({len(deny)} denylist entries)" if deny else "names NOT checked (no denylist)"
    print(f"PII GUARD {'FAIL' if found else 'PASS'}: {len(found)} finding(s) in {what}; {names}")
    return 1 if found else 0


def self_test():
    at, dot = "@", "."
    ok = True

    def expect(name, text, kinds, deny=(), allow=()):
        nonlocal ok
        got = sorted({k for _, _, k, _ in scan_text(text, "t", list(deny), set(allow))})
        good = got == sorted(kinds)
        print(("ok   " if good else "FAIL ") + f"{name}: {got}")
        ok = ok and good

    expect("personal email", "mail jane" + at + "corp" + dot + "io", ["email"])
    expect("github noreply allowed", "123+x" + at + "users.noreply.github" + dot + "com", [])
    expect("noreply allowed", "noreply" + at + "anthropic" + dot + "com", [])
    expect("example domain allowed", "a" + at + "example" + dot + "com", [])
    expect("placeholder t@t ignored", "t" + at + "t", [])
    expect(".internal email", "x" + dot + "y" + at + "example" + dot + "internal", ["email", "internal"])
    expect(".internal host", "see example" + dot + "internal today", ["internal"])
    expect("phone dashes", "call 555-123-" + "4567", ["phone"])
    expect("phone parens", "call (555) 123-" + "4567", ["phone"])
    expect("phone intl", "call +44 20 7946 " + "0958", ["phone"])
    expect("ORG", "ORG 312-" + "5550", ["phone"])
    expect("SSN shape", "id 123-45-" + "6789", ["id"])
    expect("ORGID", "ORGID: 12345" + "67890", ["id"])
    expect("date not a phone", "2026-11-11 10:00", [])
    expect("version not a phone", "v2.1.41 and 1.2.3.4", [])
    expect("unix time not an id", "ts 17312" + "34567", [])
    expect("sha not an id", "commit 0123456789abcdef0123456789abcdef01234567", [])
    expect("denylist name", "ask Alex" + "andra first", ["name"], deny=["Alexandra"])
    expect("denylist any case", "ALEX" + "ANDRA", ["name"], deny=["alexandra"])
    expect("denylist whole word", "Alexandra" + "s", [], deny=["Alexandra"])
    expect("allow list", "see example" + dot + "internal", [], allow=["example" + dot + "internal"])
    with tempfile.TemporaryDirectory() as d:
        env = {**os.environ, "GIT_AUTHOR_NAME": "Sam", "GIT_COMMITTER_NAME": "Sam",
               "GIT_AUTHOR_EMAIL": "1+s" + at + "users.noreply.github" + dot + "com",
               "GIT_COMMITTER_EMAIL": "1+s" + at + "users.noreply.github" + dot + "com"}
        for k in [k for k in env if k.startswith("GIT_") and k not in (
                "GIT_AUTHOR_NAME", "GIT_COMMITTER_NAME", "GIT_AUTHOR_EMAIL", "GIT_COMMITTER_EMAIL")]:
            env.pop(k)
        run = lambda *a: subprocess.run(["git", *a], cwd=d, env=env, check=True, capture_output=True)
        run("init", "-q", "-b", "main")
        pathlib.Path(d, "a.txt").write_text("clean\n")
        run("add", "."); run("commit", "-q", "-m", "clean")
        base = git("rev-parse", "HEAD", root=d).strip()
        pathlib.Path(d, "a.txt").write_text("clean\nmail bob" + at + "corp" + dot + "io\n")
        run("add", "."); run("commit", "-q", "-m", "ask Alexandra")
        found, n = scan_commits([f"{base}..HEAD"], d, ["Alexandra"], set())
        kinds = sorted(k for _, _, k, _ in found)
        good = n == 1 and kinds == ["email", "name"]
        print(("ok   " if good else "FAIL ") + f"commit range: {n} commit(s), {kinds}")
        ok = ok and good
        env["GIT_AUTHOR_EMAIL"] = "me" + at + "home" + dot + "net"
        run("commit", "-q", "--allow-empty", "-m", "x")
        found, _ = scan_commits(["HEAD~1..HEAD"], d, [], set())
        good = [k for _, _, k, _ in found] == ["email"]
        print(("ok   " if good else "FAIL ") + f"author email: {[k for _, _, k, _ in found]}")
        ok = ok and good
        z = "0" * 40
        head = git("rev-parse", "HEAD", root=d).strip()
        revs = push_revs(f"refs/heads/main {head} refs/heads/main {z}\n(delete) {z} refs/heads/x {head}\n", d)
        good = revs == [[head, "--not", "--remotes"]]
        print(("ok   " if good else "FAIL ") + f"push lines: {revs}")
        ok = ok and good
    print("PII GUARD TEST " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("files", nargs="*")
    ap.add_argument("--all", action="store_true", help="scan every tracked file")
    ap.add_argument("--range", help="scan commits in this range (A..B)")
    ap.add_argument("--push", action="store_true", help="pre-push mode: read the hook's stdin")
    ap.add_argument("--test", action="store_true")
    a = ap.parse_args()
    if a.test:
        return self_test()
    if not (a.files or a.all or a.range or a.push):
        ap.error("give --all, --range, --push or files")
    try:
        root = git("rev-parse", "--show-toplevel").strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        root = "."
    deny, allow = load_denylist(), load_allow(root)
    found, what = [], []
    if a.all:
        files = git("ls-files", "-z", root=root).split("\0")
        found += scan_files([f for f in files if f], root, deny, allow)
        what.append(f"{len([f for f in files if f])} tracked files")
    if a.files:
        found += scan_files(a.files, ".", deny, allow)
        what.append(f"{len(a.files)} file(s)")
    revsets = [[a.range]] if a.range else []
    if a.push:
        revsets += push_revs(sys.stdin.read(), root)
    n = 0
    for revs in revsets:
        f, k = scan_commits(revs, root, deny, allow)
        found += f
        n += k
    if revsets:
        what.append(f"{n} commit(s)")
    return report(found, ", ".join(what) or "nothing", deny)


if __name__ == "__main__":
    sys.exit(main())
