# archimedes_lever

A starter kit for projects built with AI agents (Claude, GPT/Codex, Gemini and others). It gives each new project the same rules file, safety hooks, checks, decision record and project log, so every agent starts from the same ground and you do not re-teach it in each chat.

"Give me a place to stand, and I will move the world." The repo is the place to stand: the rules, decisions and history live in files that every agent reads, not in a chat that disappears.

## What you get

| Part | What it does for you |
|---|---|
| AGENTS.md | One rules file for every agent: order of authority, delivery, reporting, git safety, personal data, decisions, handoff, project log, delegation. Your project rules go at the end. |
| Safety hooks | `scripts/git-hooks/pre-push` blocks force-pushes and deleting main for every tool. The Claude Code Stop hook blocks the end of a turn while work is unsaved or unpushed. |
| Personal-data guard | `scripts/pii_guard.py` blocks emails, phone numbers, .internal addresses, ID-number shapes and names from your private denylist before they reach GitHub. |
| Memory in files | docs/DECISIONS.md (dated decisions), docs/NEXT_PROMPT.md (short handoff), docs/LOG.md (timeline of milestones, breakthroughs and misses). |
| Multi-agent pack | `.claude/orchestration.md`: scout, worker and reviewer roles, model tiers (fast, standard, strong) per host, and fallbacks for hosts without subagents or hooks. |
| Upkeep | `scripts/sync_baseline.py` brings a project up to the current kit; `scripts/drift.py` reports how far a project has drifted. |
| Example preferences | docs/claude-preferences.md, docs/gpt-preferences.md, docs/codex-agents.md: account-wide settings you can adapt. |

## Start a new project (3 steps)

1. Make the repo from this template:
   ```
   gh repo create YOUR_USER/NEW_NAME --private --template [old handle]/archimedes_lever --clone
   ```
   Or, on GitHub: **Use this template → Create a new repository**.
2. In the new repo, fill the placeholders, then commit and push:
   ```
   scripts/bootstrap.sh "Project Name" YOUR_USER/NEW_NAME "One-line purpose"
   ```
   A 4th argument sets the name agents use for you. The default is "the owner". A public repo uses a role, for example `"the maintainer"`; a private repo may use your first name.
3. Paste the Project text from `docs/host-prompts.md` into your claude.ai Project instructions (or the GPT / Gemini equivalent).

Or tell your agent: "Bootstrap a new project NEW_NAME from [old handle]/archimedes_lever. Purpose: …". It can do steps 1–2 and give you the text for step 3.

Then run `scripts/session_checkin.sh` once per clone. It installs the git hooks.

## Keep personal data out

1. Commit as your GitHub noreply address: GitHub **Settings → Emails**, turn on "Keep my email addresses private" and "Block command line pushes that expose my email". Then:
   ```
   git config --global user.email "ID+USER@users.noreply.github.com"
   ```
2. Make a name denylist on your computer, one entry per line (your names, username variants, employer). It never goes in a repo:
   ```
   mkdir -p ~/.config/pii-guard && nano ~/.config/pii-guard/denylist.txt
   ```
3. Add the same list as an Actions secret named `PII_GUARD_DENYLIST` (repo **Settings → Secrets and variables → Actions**), so the pull-request check also checks names.
4. Check: `python3 scripts/pii_guard.py --all`. It prints PII GUARD PASS or each finding, masked.

The guard runs only in a repo with a `.pii-guard` file at its root. That file also lists exact strings you allow. A private repo that names you on purpose can delete it.

## Files

| File | Job |
|---|---|
| AGENTS.md | Rules for every agent. Project rules go at its end. |
| CLAUDE.md | One line that imports AGENTS.md, because Claude Code reads CLAUDE.md. |
| GEMINI.md | One line that imports AGENTS.md, because Gemini CLI reads GEMINI.md. Codex, Copilot and Cursor read AGENTS.md directly. |
| docs/NEXT_PROMPT.md | Short handoff: state, open work, items that need the owner. |
| docs/DECISIONS.md | Dated decision log. Owner decisions vs agent recommendations. |
| docs/LOG.md | Project log for a timeline: milestones, breakthroughs, misses, decisions, grouped in arcs. A public repo keeps it in a private place named in Project rules. |
| docs/host-prompts.md | Pointer texts for the claude.ai Project, GPT, Gemini and any other chat. |
| docs/reviews/ | Detailed evidence. |
| CHANGELOG.md | Kit versions and decisions about the kit. Template repo only: bootstrap deletes it. |
| docs/claude-preferences.md, docs/gpt-preferences.md, docs/codex-agents.md | Example account-wide preferences for Claude, ChatGPT and Codex. Replace `<your role>` and `<your field>`. Template repo only: bootstrap deletes them. |
| .claude/settings.json | Claude Code deny list (force-push incl. --force-with-lease, hard reset, clean, reading .env files) and the Stop hook. Binds Claude Code only. |
| .claude/orchestration.md | Multi-agent rules: roles, model routing by tier, fallbacks, briefs, review and merge, lanes. Read only when delegating. |
| .claude/agents/ | Claude Code roles: `scout` (fast tier, read-only), `worker` (standard), `reviewer` (standard, read-only). |
| .github/workflows/pii-guard.yml | Pull-request and manual check: pii_guard self-test, all files, and the PR's commits. Never on push (Actions minutes). |
| .pii-guard | Turns the guard on; lists allowed exact strings. Only the owner edits it. |
| .baseline | The kit commit the project was made or last synced from. |
| .gitignore | Keeps .env files and CLAUDE.local.md out of git. |
| scripts/session_checkin.sh | Start and end check: branch, ahead/behind, uncommitted files. Installs scripts/git-hooks when no other hooks path is set. |
| scripts/git-hooks/pre-push | For every agent and tool: blocks force-pushes, non-fast-forward pushes and deleting main or master; runs pii_guard.py when `.pii-guard` exists. `--test`. |
| scripts/pii_guard.py | Personal-data guard (`--all`, `--range A..B`, `--push`, files). `--test`. |
| scripts/stop_check.py | Claude Code Stop hook: blocks the end of a turn while work is uncommitted or unpushed. `--test`. |
| scripts/worker_guard.py | PreToolUse hook that limits what `worker` and `reviewer` may do in git. `--test`. |
| scripts/log_check.py | Checks docs/LOG.md against the Project log rules. `--test`. |
| scripts/timeline.py | Renders one or more project logs as one self-contained HTML timeline. `--test`. |
| scripts/drift.py | Report only: how a project differs from this kit. `--project DIR`, `--owner NAME`, `--test`. |
| scripts/sync_baseline.py | Brings an existing project up to the current kit. Dry run by default; `--apply` writes. Keeps Project rules, Commands and docs/. |
| scripts/bootstrap.sh | Fills the placeholders once, then deletes itself. |

## Sync an existing project

In the project repo, with no uncommitted changes:

1. First time only (the project has no `scripts/sync_baseline.py` yet): clone this repo next to the project, then run its copy:
   ```
   python3 ../archimedes_lever/scripts/sync_baseline.py --name "Project Name" --repo YOUR_USER/NAME --purpose "One-line purpose"
   ```
   Later syncs: `python3 scripts/sync_baseline.py`. Add `--owner NAME` when the project AGENTS.md has no `- Owner:` line.
2. Read the diff. Nothing is written yet.
3. Run the same command with `--apply`, review `git diff`, then commit and push.

An old AGENTS.md without the kit layout moves under "Project rules" with a review note. Delete what the kit now covers.

## Limits

- A project does not update by itself. Run the sync after a kit change (see CHANGELOG.md).
- Your personal preferences reach only hosts that have a copy (Claude, GPT, Codex). Every agent gets the rules from AGENTS.md.
- Hooks are seat belts, not locks: Claude Code hooks bind Claude Code only, and `--no-verify` skips git hooks.
- The guard finds shapes and listed names. It does not find a name you did not list, or personal facts written in prose. Read before you publish.
- Model names in orchestration.md go stale; the tiers stay.
