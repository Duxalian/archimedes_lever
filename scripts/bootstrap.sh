#!/usr/bin/env bash
# Fill the template placeholders in a new project made from [old handle]/archimedes_lever.
# Usage: scripts/bootstrap.sh "Project Name" Owner/repo "One-line purpose" ["Owner name"]
# Owner name: what agents call the decider (default "the owner"). A private repo may use your name; a public repo uses a role,
# for example "the maintainer".
# The script deletes itself when it finishes. Review the result, then commit and push.
set -euo pipefail

if [ $# -lt 3 ] || [ $# -gt 4 ]; then
  echo 'usage: scripts/bootstrap.sh "Project Name" Owner/repo "One-line purpose" ["Owner name"]' >&2
  exit 1
fi

owner_re='^[A-Za-z0-9 ._,()-]+$'
if [ $# -eq 4 ] && ! [[ "$4" =~ $owner_re ]]; then
  echo 'error: owner name: use letters, digits, space . _ , ( ) - only' >&2
  exit 1
fi

cd "$(git rev-parse --show-toplevel)"

export BS_NAME="$1" BS_REPO="$2" BS_PURPOSE="$3" BS_OWNER="${4:-the owner}" BS_DATE BS_TIME
# One clock read in America/Chicago, so the date and time agree (project log times are CT).
BS_STAMP="$(TZ=America/Chicago date '+%F %H:%M')"
BS_DATE="${BS_STAMP% *}"
BS_TIME="${BS_STAMP#* }"

files=(AGENTS.md docs/NEXT_PROMPT.md docs/DECISIONS.md docs/host-prompts.md docs/LOG.md)
for f in "${files[@]}"; do
  perl -pi -e 's/\{\{PROJECT_NAME\}\}/$ENV{BS_NAME}/g; s/\{\{REPO\}\}/$ENV{BS_REPO}/g; s/\{\{PURPOSE\}\}/$ENV{BS_PURPOSE}/g; s/\{\{DATE\}\}/$ENV{BS_DATE}/g; s/\{\{TIME\}\}/$ENV{BS_TIME}/g; s/\{\{OWNER\}\}/the owner/g' "$f"
done

# Replace the role word "the owner" / "The owner" (sync_baseline.py keeps the literal: it needs it).
if [ "$BS_OWNER" != "the owner" ]; then
  owner_files=("${files[@]}" .claude/orchestration.md scripts/stop_check.py scripts/worker_guard.py)
  for f in "${owner_files[@]}"; do
    perl -pi -e 'my $c = ucfirst $ENV{BS_OWNER}; s/the owner/$ENV{BS_OWNER}/g; s/The owner/$c/g' "$f"
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
base_sha="$(git ls-remote https://github.com/[old handle]/archimedes_lever HEAD 2>/dev/null | cut -f1)" || base_sha=""
echo "[old handle]/archimedes_lever ${base_sha:-unknown (ls-remote failed)}" > .baseline

# The owner's account-wide preference files live only in the template repo.
rm -f -- docs/claude-preferences.md docs/gpt-preferences.md docs/codex-agents.md CHANGELOG.md

rm -- "$0"
if [ "$BS_OWNER" != "the owner" ] && [ -f .pii-guard ]; then
  echo "Note: .pii-guard is on. If \"$BS_OWNER\" is a real name in your denylist, the guard blocks it: remove .pii-guard in a private repo."
fi
echo "Done. Next: review with 'git diff', then commit and push."
echo "Then paste the Project text from docs/host-prompts.md into the claude.ai Project instructions."
