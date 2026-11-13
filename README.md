# archimedes_lever

A starter kit for projects built with AI agents (Claude, GPT/Codex, Gemini and others). It gives each new project the same rules file, safety hooks, checks, decision record and project log, so every agent starts from the same ground and you do not re-teach it in each chat.

"Give me a place to stand, and I will move the world." The repo is the place to stand: the rules, decisions and history live in files that every agent reads, not in a chat that disappears.

## What you need

- A free [GitHub account](https://github.com/signup).
- An AI agent that can run commands and edit files: Claude Code (in the browser at claude.ai/code, or the app), Codex, Cursor, Gemini CLI, or another tool that reads AGENTS.md. A chat with no file access (for example a plain ChatGPT or claude.ai chat) cannot set up the project; use the steps "by hand" below with it.
- For way B only, on your computer: git, Python 3.9 or later, bash and perl. macOS and Linux have bash and perl; on Windows, use Git Bash or WSL. If one is missing, the agent tells you how to install it.

## Start here

You do not need to know git: the agent does that part. Pick one way.

**A. In your browser, nothing to install** (Claude Code on the web)

1. On this page, click **Use this template → Create a new repository**. Type your project's name and choose **Private**.
2. Open [claude.ai/code](https://claude.ai/code), connect GitHub when it asks, and start a session on your new repository.
3. Type:
   ```
   Please read the repo and initiate.
   ```

**B. With an agent app on your computer** (Claude Code, Codex, Cursor, Gemini CLI)

1. Open the app in the folder where you keep projects (your Documents folder is fine).
2. Type:
   ```
   Please set up a new project from https://github.com/rhope-ops/archimedes_lever: get the repo, read it, and initiate.
   ```

Either way, the agent asks 4 questions: the name, what it is for, your time zone, and whether to use the recommended settings. It explains each one; when you are not sure, take the answer it marks as recommended. Then it makes your own GitHub repository, fills in the project files and tells you what is left to do.

One step is yours: the agent asks you to type your own names into a private list (the personal-data guard checks every push against it, so your names never land on GitHub by mistake). You never type them into the chat. In the browser (way A), this means you add a setting and start one new session; the agent gives you a prompt to paste there, so you do not answer the questions again.

If you know git: `git clone https://github.com/rhope-ops/archimedes_lever my-project`, open the folder with your agent and type `Please read the repo and initiate.`

Details for agents: [docs/FIRST_USE.md](docs/FIRST_USE.md).

## After setup

Open the project with any agent and say what you want to do next. The agent reads AGENTS.md (the rules) and docs/NEXT_PROMPT.md (where the work stands) first, so you do not have to explain the project again in each chat.

## What you get

| Part | What it does for you |
|---|---|
| AGENTS.md | One rules file for every agent: order of authority, delivery, reporting, git safety, personal data, decisions, handoff, project log, delegation. Your project rules go at the end. |
| Safety hooks | `scripts/git-hooks/pre-push` blocks force-pushes, deleting main and pushes that fail `scripts/check.sh`, for every tool. The Claude Code Stop hook blocks the end of a turn while work is unsaved or unpushed. |
| Personal-data and secret guard | `scripts/pii_guard.py` blocks emails, phone numbers, ID-number shapes, API tokens, private keys and names from your private denylist before they reach GitHub (.internal addresses too, if you turn that on). |
| One check command | `scripts/check.sh` runs every self-test, the project log check and the personal-data scan, plus your own tests in `scripts/check.local.sh`. It is the default Test command in AGENTS.md and runs on each pull request. |
| Memory in files | docs/DECISIONS.md (dated decisions), docs/NEXT_PROMPT.md (short handoff), docs/LOG.md (timeline of milestones, breakthroughs and misses). |
| Multi-agent pack | `.claude/orchestration.md`: scout, worker and reviewer roles, model tiers (fast, standard, strong) per host, and fallbacks for hosts without subagents or hooks. |
| Upkeep | `scripts/sync_baseline.py` brings a project up to the current kit; `scripts/drift.py` reports how far a project has drifted. |

## Start a new project by hand

For people who use git and want no agent in the setup, or who use a chat with no file access.

1. Make the repo from this template:
   ```
   gh repo create YOUR_USER/NEW_NAME --private --template rhope-ops/archimedes_lever --clone
   ```
   Or, on GitHub: **Use this template → Create a new repository**, then clone it.
2. In the new repo, fill the placeholders:
   ```
   scripts/bootstrap.sh "Project Name" YOUR_USER/NEW_NAME "One-line purpose" "the owner" "Europe/Berlin"
   ```
   The 4th argument is the name agents use for you (default "the owner"). A public repo uses a role, for example `"the maintainer"`; a private repo may use your first name. The 5th is the time zone for project log times, as an IANA name (default UTC).
   Bootstrap moves the kit's MIT license to docs/archimedes_lever-LICENSE.txt (keep it: it covers the kit's scripts). Add your own `LICENSE` if you want one.
3. Set up the name denylist (next section), run `scripts/session_checkin.sh` (it installs the git hooks), then commit and push.
4. Paste the Project text from `docs/host-prompts.md` into your claude.ai Project instructions (or the GPT / Gemini equivalent).

## Keep personal data out

0. With the guard on, every push and pull-request check with no denylist fails, so set each place you use: your computer (step 2), GitHub (step 3), and the cloud environment variable `PII_GUARD_DENYLIST` for Claude cloud sessions. `python3 scripts/pii_guard.py --status` prints where the list comes from and how many entries, never the names.
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
| docs/LOG.md | Project log for a timeline and a narrative deck: milestones, breakthroughs, misses, decisions, grouped in arcs; each arc has Problem, Turning point, Outcome and Lesson. A public repo keeps it in a private place named in Project rules. |
| docs/host-prompts.md | Pointer texts for the claude.ai Project, GPT, Gemini and any other chat. |
| docs/reviews/ | Detailed evidence. |
| CHANGELOG.md | Kit versions and decisions about the kit. Template repo only: bootstrap deletes it. |
| .bloat-audit.json | The kit's own audit state and timing baselines (scripts/bloat_check.py). Template repo only: bootstrap deletes it; a project's first audit makes its own. |
| KIT_LOG.md | The kit's own project log (story of how the kit got here; same format as docs/LOG.md). Template repo only: bootstrap deletes it. |
| PREFERENCES.md | The owner's personal preferences for Claude, ChatGPT and Codex, ready to paste. Template repo only: bootstrap deletes it. |
| LICENSE | The kit's license (MIT). Bootstrap moves it to docs/archimedes_lever-LICENSE.txt; the project picks its own LICENSE. |
| .claude/settings.json | Claude Code deny list (force-push incl. --force-with-lease, hard reset, clean, reading .env and key files), a sandbox with a network allowlist (GitHub, PyPI, npm), and the Stop hook. Binds Claude Code only. |
| .claude/orchestration.md | Multi-agent rules: roles, model routing by tier, fallbacks, briefs, review and merge, lanes. Read only when delegating. |
| .claude/bloat-audit.md | The periodic bloat, drift and assumption audit (AGENTS.md "Bloat, drift and assumptions"). Read only when an audit is due. |
| scripts/bloat_check.py | Cheap metrics each check-in: start-read tokens, duplicate lines, big files, audit due date; `--time` compares timed operations with their baseline. Settings and state: `.bloat-audit.json`. `--test`. |
| .claude/agents/ | Claude Code roles: `scout` (fast tier, read-only), `worker` (standard), `reviewer` (standard, read-only). |
| .github/workflows/pii-guard.yml | Pull-request and manual check: `scripts/check.sh`, then the guard on all files and the PR's commits. Never on push (Actions minutes). |
| .pii-guard | Turns the guard on; lists allowed exact strings, `skip:` paths and opt-in `check: internal`. Only the owner edits it. |
| docs/FIRST_USE.md | The first-use questions and what the agent does with the answers. |
| scripts/first_use_check.py | Session-start check (Claude Code SessionStart hook): KIT in the kit itself (a plain clone), FIRST USE when placeholders remain, DENYLIST when the guard is on and the session has no denylist. `--test`. |
| .baseline | The kit commit the project was made or last synced from. |
| .gitignore | Keeps .env files and CLAUDE.local.md out of git. |
| scripts/check.sh | The one check command (AGENTS.md "Commands": Test). Runs `scripts/check.local.sh` last when it exists. |
| scripts/session_checkin.sh | Start and end check: branch, ahead/behind, uncommitted files. Installs scripts/git-hooks when no other hooks path is set. |
| scripts/git-hooks/pre-push | For every agent and tool: blocks force-pushes, non-fast-forward pushes and deleting main or master; runs scripts/check.sh, and pii_guard.py when `.pii-guard` exists. `--test`. |
| scripts/pii_guard.py | Personal-data and secret guard (`--all`, `--range A..B`, `--push`, files; `--require-denylist`; `--status`). `--test`. |
| scripts/stop_check.py | Claude Code Stop hook: blocks the end of a turn while work is uncommitted or unpushed. `--test`. |
| scripts/worker_guard.py | PreToolUse hook that limits what `worker` and `reviewer` may do in git. `--test`. |
| scripts/log_check.py | Checks docs/LOG.md against the Project log rules. `--test`. |
| scripts/timeline.py | Renders one or more project logs as one self-contained HTML timeline, or a Markdown story outline per arc for a deck (`--outline FILE`). `--test`. |
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
- Setup needs an agent with file access. A chat that cannot run commands can only give you text to paste: use "Start a new project by hand".
- Hooks are seat belts, not locks: Claude Code hooks bind Claude Code only, and `--no-verify` skips git hooks.
- The guard finds shapes and listed names. It does not find a name you did not list, or personal facts written in prose. Read before you publish.
- Model names in orchestration.md go stale; the tiers stay.
