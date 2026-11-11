# archimedes_lever

A starter kit for projects built with AI agents (Claude, GPT/Codex, Gemini and others). It gives each new project the same rules file, safety hooks, checks, decision record and project log, so every agent starts from the same ground and you do not re-teach it in each chat.

"Give me a place to stand, and I will move the world." The repo is the place to stand: the rules, decisions and history live in files that every agent reads, not in a chat that disappears.

## Start here

1. Clone the kit into a folder named for your project:
   ```
   git clone https://github.com/Duxalian/archimedes_lever my-project
   ```
2. Open the folder with your agent (Claude Code, Codex, Gemini CLI or another tool that reads AGENTS.md) and say:
   ```
   Please read the repo and initiate.
   ```

The agent asks up to 10 questions, moves the clone to your own GitHub repo, fills in the project files and tells you what is left to do. Details: [docs/FIRST_USE.md](docs/FIRST_USE.md). Before you start, check [What you need](#what-you-need).

## What you get

| Part | What it does for you |
|---|---|
| AGENTS.md | One rules file for every agent: order of authority, delivery, reporting, git safety, personal data, decisions, handoff, project log, delegation. Your project rules go at the end. |
| Safety hooks | `scripts/git-hooks/pre-push` blocks force-pushes and deleting main for every tool. The Claude Code Stop hook blocks the end of a turn while work is unsaved or unpushed. |
| Personal-data and secret guard | `scripts/pii_guard.py` blocks emails, phone numbers, ID-number shapes, API tokens, private keys and names from your private denylist before they reach GitHub (.mil addresses too, if you turn that on). |
| One check command | `scripts/check.sh` runs every self-test, the project log check and the personal-data scan, plus your own tests in `scripts/check.local.sh`. It is the default Test command in AGENTS.md and runs on each pull request. |
| Memory in files | docs/DECISIONS.md (dated decisions), docs/NEXT_PROMPT.md (short handoff), docs/LOG.md (timeline of milestones, breakthroughs and misses). |
| Multi-agent pack | `.claude/orchestration.md`: scout, worker and reviewer roles, model tiers (fast, standard, strong) per host, and fallbacks for hosts without subagents or hooks. |
| Upkeep | `scripts/sync_baseline.py` brings a project up to the current kit; `scripts/drift.py` reports how far a project has drifted. |

## What you need

| Tool | Used by | Check |
|---|---|---|
| git 2.28 or later | everything | `git --version` |
| Python 3.9 or later (standard library only) | all checks and hooks | `python3 --version` |
| bash and perl | `scripts/bootstrap.sh`, `scripts/check.sh` (macOS and Linux have both; on Windows use Git Bash or WSL) | `perl -v` |
| GitHub CLI `gh` (optional) | step 1 from the command line; the web page works without it | `gh --version` |

An agent host is optional: Claude Code, Codex, Gemini CLI or another tool that reads AGENTS.md. Without one, follow the steps below by hand.

## Start a new project by hand (3 steps)

1. Make the repo from this template:
   ```
   gh repo create YOUR_USER/NEW_NAME --private --template Duxalian/archimedes_lever --clone
   ```
   Or, on GitHub: **Use this template → Create a new repository**.
2. In the new repo, fill the placeholders, then commit and push:
   ```
   scripts/bootstrap.sh "Project Name" YOUR_USER/NEW_NAME "One-line purpose" "the owner" "Europe/Berlin"
   ```
   The 4th argument is the name agents use for you (default "the owner"). A public repo uses a role, for example `"the maintainer"`; a private repo may use your first name. The 5th is the time zone for project log times, as an IANA name (default UTC).
   Then add a `LICENSE` if you want one: bootstrap moves the kit's MIT license to docs/archimedes_lever-LICENSE.txt (keep it: it covers the kit's scripts), so the root LICENSE is your choice.
3. Paste the Project text from `docs/host-prompts.md` into your claude.ai Project instructions (or the GPT / Gemini equivalent).

Or tell your agent: "Bootstrap a new project NEW_NAME from Duxalian/archimedes_lever. Purpose: …". It can do steps 1–2 and give you the text for step 3.

Then run `scripts/session_checkin.sh` once per clone. It installs the git hooks.

## First use

Open the new repo in an agent session. On the first session the agent asks 9 questions in 3 rounds, 10 from a plain clone (Claude Code shows clickable dialogs): project name, purpose, public or private, license, what agents call you, the personal-data guard, where you push from, time zone, and which other agents you use. It then fills the placeholders, commits, and gives you a short list of the places where your name denylist must go. The questions and steps are in [docs/FIRST_USE.md](docs/FIRST_USE.md); `scripts/first_use_check.py` (a SessionStart hook in Claude Code) says when first use is due, and when a session has no denylist.

## Keep personal data out

0. With the guard on, every push and pull-request check with no denylist fails, so set each place you use (steps 2 and 3, plus the cloud environment variable `PII_GUARD_DENYLIST` for Claude cloud sessions). `python3 scripts/pii_guard.py --status` prints where the list comes from and how many entries, never the names.
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
| LICENSE | The kit's license (MIT). Bootstrap moves it to docs/archimedes_lever-LICENSE.txt; the project picks its own LICENSE. |
| .claude/settings.json | Claude Code deny list (force-push incl. --force-with-lease, hard reset, clean, reading .env files) and the Stop hook. Binds Claude Code only. |
| .claude/orchestration.md | Multi-agent rules: roles, model routing by tier, fallbacks, briefs, review and merge, lanes. Read only when delegating. |
| .claude/agents/ | Claude Code roles: `scout` (fast tier, read-only), `worker` (standard), `reviewer` (standard, read-only). |
| .github/workflows/pii-guard.yml | Pull-request and manual check: `scripts/check.sh`, then the guard on all files and the PR's commits. Never on push (Actions minutes). |
| .pii-guard | Turns the guard on; lists allowed exact strings, `skip:` paths and opt-in `check: mil`. Only the owner edits it. |
| docs/FIRST_USE.md | The first-use questions and what the agent does with the answers. |
| scripts/first_use_check.py | Session-start check (Claude Code SessionStart hook): FIRST USE when placeholders remain, DENYLIST when the guard is on and the session has no denylist. `--test`. |
| .baseline | The kit commit the project was made or last synced from. |
| .gitignore | Keeps .env files and CLAUDE.local.md out of git. |
| scripts/check.sh | The one check command (AGENTS.md "Commands": Test). Runs `scripts/check.local.sh` last when it exists. |
| scripts/session_checkin.sh | Start and end check: branch, ahead/behind, uncommitted files. Installs scripts/git-hooks when no other hooks path is set. |
| scripts/git-hooks/pre-push | For every agent and tool: blocks force-pushes, non-fast-forward pushes and deleting main or master; runs pii_guard.py when `.pii-guard` exists. `--test`. |
| scripts/pii_guard.py | Personal-data and secret guard (`--all`, `--range A..B`, `--push`, files; `--require-denylist`; `--status`). `--test`. |
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
   Later syncs: `python3 scripts/sync_baseline.py`. Add `--owner NAME` when the project AGENTS.md has no `- Owner:` line, and `--timezone ZONE` (IANA name) when it has no `- Time zone:` line.
2. Read the diff. Nothing is written yet.
3. Run the same command with `--apply`, review `git diff`, then commit and push.

An old AGENTS.md without the kit layout moves under "Project rules" with a review note. Delete what the kit now covers.

## Limits

- A project does not update by itself. Run the sync after a kit change (see CHANGELOG.md).
- Account-wide preferences (your own settings in Claude, ChatGPT or Codex) reach only that host. Every agent gets the rules from AGENTS.md.
- Hooks are seat belts, not locks: Claude Code hooks bind Claude Code only, and `--no-verify` skips git hooks.
- The guard finds shapes and listed names. It does not find a name you did not list, or personal facts written in prose. Read before you publish.
- Model names in orchestration.md go stale; the tiers stay.
