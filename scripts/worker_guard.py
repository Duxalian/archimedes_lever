#!/usr/bin/env python3
"""PreToolUse hook for the worker and reviewer subagents (.claude/agents/): blocks git commands they must never run.

Adapted from an earlier project's worker guard (tested parser).

Usage (wired in the .claude/agents/ frontmatter `hooks:`; runs only while that subagent is active):
  python3 scripts/worker_guard.py            # reads the hook JSON on stdin
  python3 scripts/worker_guard.py --readonly # reviewer: also blocks git verbs that change the repo
  python3 scripts/worker_guard.py --test     # self-test of the block rules; prints GUARD TEST PASS

Blocks Bash commands that push to main or master (also a bare push or HEAD while on one), rebase, git clean, branch deletes, force-push (--force, -f in
grouped flags, +refspec, --force-with-lease), --mirror/--all, reset --hard or delete remote branches. It parses each
simple command into words (quotes respected), so "main" inside a branch name or a commit message is not a match.
Exit 2 with the reason on stderr blocks the call; exit 0 lets the normal permission flow decide. A command built at run
time (eval, a script file) is not seen: it is a seat belt for honest mistakes, not a security boundary.
"""
import argparse
import json
import re
import shlex
import subprocess
import sys

SEPARATORS = {';', '&&', '||', '|', '&', '(', ')'}
GIT_OPTS_WITH_VALUE = {'-C', '-c', '--git-dir', '--work-tree', '--namespace'}
# --readonly (reviewer): also block git verbs that change the repo.
WRITE_VERBS = {'commit', 'add', 'rm', 'mv', 'merge', 'checkout', 'switch', 'restore', 'stash', 'tag', 'apply', 'am',
               'cherry-pick', 'revert', 'reset', 'push', 'pull', 'clean'}


def segments(cmd):
    """Yield the word lists of each simple command (split on newlines and ; && || | &, quotes respected)."""
    for line in cmd.splitlines():
        try:
            lex = shlex.shlex(line, posix=True, punctuation_chars=True)
            lex.whitespace_split = True
            words = list(lex)
        except ValueError:          # unbalanced quotes: fall back to a plain split
            words = line.split()
        seg = []
        for w in words:
            if w in SEPARATORS:
                if seg:
                    yield seg
                seg = []
            else:
                seg.append(w)
        if seg:
            yield seg


def current_branch():
    r = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], capture_output=True, text=True)
    return r.stdout.strip()


def check_git(args, branch, readonly=False):
    """args: the words after `git`. Returns a reason to block, or None."""
    i = 0
    while i < len(args) and args[i].startswith('-'):
        i += 2 if args[i] in GIT_OPTS_WITH_VALUE else 1
    if i >= len(args):
        return None
    sub, rest = args[i], args[i + 1:]
    if readonly and sub in WRITE_VERBS:
        return f'reviewers are read-only: no git {sub}'
    if sub == 'rebase':
        return 'no rebase; update a branch by merging (AGENTS.md "Git safety")'
    if sub == 'reset' and '--hard' in rest:
        return 'no reset --hard; ask the orchestrator'
    if sub == 'clean':
        return 'no git clean; ask the orchestrator'
    if sub == 'branch' and any(w in ('-D', '-d', '--delete') or (w.startswith('-') and not w.startswith('--') and 'D' in w) for w in rest):
        return 'no branch deletes; the orchestrator or the owner deletes branches'
    if sub != 'push':
        return None
    pos = []
    for w in rest:
        if w.startswith('--'):
            if w in ('--force', '--mirror', '--all', '--delete', '--prune') or w.startswith('--force-with-lease'):
                return f'workers may not push with {w} (AGENTS.md "Git safety")'
        elif w.startswith('-') and len(w) > 1:
            if 'f' in w[1:] or 'd' in w[1:]:
                return f'workers may not push with {w} (force or delete)'
        else:
            pos.append(w)
    refspecs = pos[1:]               # pos[0] is the remote
    if not refspecs:
        refspecs = ['HEAD']
    for ref in refspecs:
        if ref.startswith('+'):
            return 'no force-push (+refspec)'
        src, _, dst = ref.partition(':')
        if _ and not src:
            return 'workers do not delete remote branches'
        target = dst or (branch if src == 'HEAD' else src)
        if target in ('main', 'master', 'refs/heads/main', 'refs/heads/master'):
            return 'workers never push main or master; push your own branch'
    return None


def reason(cmd, branch=None, readonly=False):
    for seg in segments(cmd):
        for k, w in enumerate(seg):
            if w == 'git' or w.endswith('/git'):
                why = check_git(seg[k + 1:], branch if branch is not None else current_branch(), readonly)
                if why:
                    return why
                break
    return None


def selftest():
    block = ['git push origin main', 'git push -u origin HEAD:main', 'git push origin cc/x:main', 'git push --force origin cc/x',
             'git push -f', 'git push -fu origin cc/x', 'git push origin "+cc/x"', 'git push origin +cc/x',
             'git rebase origin/main', 'cd x && git rebase -i HEAD~2', 'git -C sub rebase main', 'git reset --hard origin/main',
             'git push origin --delete cc/x', 'git push origin :cc/x', 'git push --mirror origin', 'git push --all',
             'git push --force-with-lease origin cc/x', 'git status; git push origin main',
             'git push origin master', 'git clean -fd', 'git branch -D x', '(git push origin main)', 'git --no-pager -C r push --force',
             'git push --prune origin']
    allow = ['git push -u origin cc/t40-slc', 'git push -u origin cc/main-menu', 'git push origin cc/fix-main',
             'git merge origin/main', 'git status', 'python3 tools/check.py --no-perf', 'git log --oneline main..HEAD',
             'git fetch origin main', 'git commit -m "push main menu fix"', 'git commit -m "fix rebase of main"',
             'git push', 'git push origin HEAD', 'git commit -m "note; git rebase later"', 'git branch -a']
    bad = [c for c in block if not reason(c, 'cc/x')] + [c for c in allow if reason(c, 'cc/x')]
    for c in ['git push', 'git push origin HEAD']:     # on main these must block
        if not reason(c, 'main'):
            bad.append(c + ' (on main)')
    for c in ['git commit -m x', 'git checkout -b y', 'git add .', 'cd a && git merge origin/main']:
        if not reason(c, 'cc/x', readonly=True):
            bad.append(c + ' (readonly)')
    for c in ['git diff origin/main...HEAD', 'git log -p', 'git show HEAD:x', 'git status', 'git fetch origin']:
        if reason(c, 'cc/x', readonly=True):
            bad.append(c + ' (readonly allow)')
    for c in bad:
        print('WRONG:', c)
    print('GUARD TEST PASS' if not bad else 'GUARD TEST FAIL')
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--test', action='store_true', help='run the self-test')
    ap.add_argument('--readonly', action='store_true', help='also block git verbs that change the repo (reviewer)')
    opts = ap.parse_args()
    if opts.test:
        return selftest()
    try:
        hook = json.load(sys.stdin)
    except ValueError:
        return 0
    if hook.get('tool_name') != 'Bash':
        return 0
    why = reason(hook.get('tool_input', {}).get('command', ''), readonly=opts.readonly)
    if why:
        print(f'Blocked by scripts/worker_guard.py: {why}. Report the need to the orchestrator instead.', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
