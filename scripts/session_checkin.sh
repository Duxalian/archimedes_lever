#!/usr/bin/env bash
# Session check-in: run at the start and the end of each session.
set -uo pipefail
cd "$(git rev-parse --show-toplevel)" || exit 1  # paths below are repo-relative; a run from a subfolder must still find them

git fetch --quiet origin main 2>/dev/null || echo "warning: fetch of origin/main failed"

# Git hooks for every agent (scripts/git-hooks/pre-push blocks force-pushes). Set only when no other hooks path is set.
# core.hooksPath hides .git/hooks; our pre-push chains to an old .git/hooks/pre-push (Git LFS). Other old hooks: warned below.
hooks=$(git config --get core.hooksPath || true)
installed=""
if [ -d scripts/git-hooks ] && [ -z "$hooks" ]; then
  git config core.hooksPath scripts/git-hooks && hooks=scripts/git-hooks && installed=" (installed now)"
fi
echo "hooks:       ${hooks:-none}${installed:-}"
if [ "$hooks" = scripts/git-hooks ]; then
  for h in "$(git rev-parse --git-common-dir)"/hooks/*; do
    case "$h" in *.sample|*/pre-push) continue ;; esac
    [ -x "$h" ] && echo "warning: $(basename "$h") in .git/hooks is not run while core.hooksPath=scripts/git-hooks; copy it to scripts/git-hooks or unset core.hooksPath"
  done
fi
echo "branch:      $(git rev-parse --abbrev-ref HEAD)"
echo "head:        $(git rev-parse --short HEAD)"
echo "origin/main: $(git rev-parse --short origin/main 2>/dev/null || echo unknown)"

if counts=$(git rev-list --left-right --count HEAD...origin/main 2>/dev/null); then
  read -r ahead behind <<<"$counts"
  echo "ahead:       $ahead"
  echo "behind:      $behind"
else
  echo "ahead/behind: unknown (shallow clone or no origin/main)"
fi

uncommitted=$(git status --porcelain | wc -l | tr -d ' ')
echo "uncommitted: $uncommitted"
[ "$uncommitted" -gt 0 ] && git status --short

[ -f scripts/bloat_check.py ] && python3 scripts/bloat_check.py --brief

if grep -rIl '{{[A-Z_]*}}' --exclude-dir=.git --exclude=bootstrap.sh --exclude=session_checkin.sh --exclude=sync_baseline.py --exclude=first_use_check.py --exclude=drift.py --exclude=check.sh --exclude=README.md . >/dev/null 2>&1; then
  echo "warning: template placeholders remain; run scripts/bootstrap.sh"
fi
exit 0
