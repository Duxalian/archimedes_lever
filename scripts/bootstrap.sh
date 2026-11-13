#!/usr/bin/env bash
# Fill the template placeholders in a new project made from rhope-ops/archimedes_lever.
# Usage: scripts/bootstrap.sh "Project Name" Owner/repo "One-line purpose" ["Owner name"] ["Time zone"]
# Owner name: what agents call the decider (default "the owner"). A private repo may use your name; a public repo uses a role,
# for example "the maintainer".
# Time zone: an IANA name for project log times, for example Europe/Berlin or America/New_York (default UTC).
# The script deletes itself when it finishes. Review the result, then commit and push.
set -euo pipefail

if [ $# -lt 3 ] || [ $# -gt 5 ]; then
  echo 'usage: scripts/bootstrap.sh "Project Name" Owner/repo "One-line purpose" ["Owner name"] ["Time zone"]' >&2
  exit 1
fi

owner_re='^[A-Za-z0-9 ._,()-]+$'
if [ $# -ge 4 ] && ! [[ "$4" =~ $owner_re ]]; then
  echo 'error: owner name: use letters, digits, space . _ , ( ) - only' >&2
  exit 1
fi

BS_TZ="${5:-UTC}"
if ! [[ "$BS_TZ" =~ ^[A-Za-z0-9_+/-]+$ ]] || { [ "$BS_TZ" != UTC ] && ! python3 -c 'import sys, zoneinfo; zoneinfo.ZoneInfo(sys.argv[1])' "$BS_TZ" 2>/dev/null; }; then
  echo "error: time zone '$BS_TZ' is not a known IANA name (for example UTC, Europe/Berlin, America/New_York)" >&2
  exit 1
fi

cd "$(git rev-parse --show-toplevel)"

export BS_NAME="$1" BS_REPO="$2" BS_PURPOSE="$3" BS_OWNER="${4:-the owner}" BS_TZ BS_DATE BS_TIME
# One clock read in the project time zone, so the date and time agree (project log times use it).
BS_STAMP="$(TZ="$BS_TZ" date '+%F %H:%M')"
BS_DATE="${BS_STAMP% *}"
BS_TIME="${BS_STAMP#* }"

files=(AGENTS.md docs/NEXT_PROMPT.md docs/DECISIONS.md docs/host-prompts.md docs/LOG.md)
for f in "${files[@]}"; do
  perl -pi -e 's/\{\{PROJECT_NAME\}\}/$ENV{BS_NAME}/g; s/\{\{REPO\}\}/$ENV{BS_REPO}/g; s/\{\{PURPOSE\}\}/$ENV{BS_PURPOSE}/g; s/\{\{DATE\}\}/$ENV{BS_DATE}/g; s/\{\{TIME\}\}/$ENV{BS_TIME}/g; s/\{\{TIMEZONE\}\}/$ENV{BS_TZ}/g; s/\{\{OWNER\}\}/the owner/g' "$f"
done

# Replace the role word "the owner" / "The owner" (sync_baseline.py keeps the literal: it needs it).
if [ "$BS_OWNER" != "the owner" ]; then
  # The same files sync_baseline.py renames (its COPY_FILES), so a sync right after bootstrap changes nothing.
  # Not renamed on purpose: docs/FIRST_USE.md, scripts/first_use_check.py and scripts/sync_baseline.py, whose
  # "the owner" is an option, a role or a literal the script needs.
  owner_files=("${files[@]}" .claude/orchestration.md .claude/bloat-audit.md .claude/project-log.md scripts/bloat_check.py scripts/session_checkin.sh scripts/stop_check.py scripts/worker_guard.py
    scripts/log_check.py scripts/drift.py scripts/timeline.py scripts/pii_guard.py scripts/check.sh scripts/git-hooks/pre-push)
  for f in "${owner_files[@]}"; do
    perl -pi -e 'my $c = ucfirst $ENV{BS_OWNER}; s/\b([Tt])he owner\b/$1 eq "T" ? $c : $ENV{BS_OWNER}/ge' "$f"
  done
fi

cat > README.md <<EOF
# $BS_NAME

$BS_PURPOSE

Agents: read [AGENTS.md](AGENTS.md) first. Status: [docs/NEXT_PROMPT.md](docs/NEXT_PROMPT.md). Decisions: [docs/DECISIONS.md](docs/DECISIONS.md). Log: [docs/LOG.md](docs/LOG.md).
EOF

if grep -rIn '{{[A-Z_]*}}' "${files[@]}" README.md; then
  echo "error: placeholders remain (listed above)" >&2
  exit 1
fi

# Record the baseline commit this project starts from (sync_baseline.py updates it later).
base_sha="$(git ls-remote https://github.com/rhope-ops/archimedes_lever HEAD 2>/dev/null | cut -f1)" || base_sha=""
echo "rhope-ops/archimedes_lever ${base_sha:-unknown (ls-remote failed)}" > .baseline

# The kit's changelog, story log (KIT_LOG.md), owner preferences (PREFERENCES.md) and audit state (.bloat-audit.json) live only in the template repo. The kit's license moves next to the docs: the copied scripts
# stay under it, and the root LICENSE is the project's own choice (docs/FIRST_USE.md, question 6).
rm -f -- CHANGELOG.md KIT_LOG.md PREFERENCES.md .bloat-audit.json
if [ -f LICENSE ]; then mv -- LICENSE docs/archimedes_lever-LICENSE.txt; fi

rm -- "$0"
if [ "$BS_OWNER" != "the owner" ] && [ -f .pii-guard ]; then
  echo "Note: .pii-guard is on. If \"$BS_OWNER\" is a real name in your denylist, the guard blocks it: remove .pii-guard in a private repo."
fi
echo "Done. Next: review with 'git diff', then commit and push."
echo "Then paste the Project text from docs/host-prompts.md into the claude.ai Project instructions."
