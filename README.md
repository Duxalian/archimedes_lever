# archimedes_lever

Lessons from making AI assistants (Claude, ChatGPT, Codex and others) reliable and low-effort to work with, in a form you can copy. "Give me a place to stand, and I will move the world": the rules, decisions and history live in files that every agent reads, not in a chat that disappears.

## First prompt

Paste this into Claude (claude.ai or Claude Code) or another assistant that can read web pages:

```
Tell me your thoughts about this repo: https://github.com/rhope-ops/archimedes_lever
```

## What you can take from it

| Take | What it gives you | Effort | Needs |
|---|---|---|---|
| 1. [Preferences](PREFERENCES.md) for your own AI account | Every chat asks its questions up front, labels its recommendations, marks its confidence, checks its work before it says "done", and saves you clicks and copying | About 5 minutes: the assistant asks you 4 questions and gives you one block to paste | Any Claude, ChatGPT or Codex account. No GitHub. |
| 2. A project kit (the rest of this repo) | A new project where every agent follows one rules file, cannot force-push or leak your name or email, checks its own work, and records decisions | About 15 minutes with an agent ("Start here" below) | A free GitHub account and an agent that can run commands |

Take 1 alone gets most of the benefit for most people. To do it, ask your assistant: `Interview me and fill in PREFERENCES.md from https://github.com/rhope-ops/archimedes_lever for Claude` (or ChatGPT, or Codex).

## Lessons behind the rules

What went wrong across 5 real projects, and the rule that came out of it. Each rule is in [PREFERENCES.md](PREFERENCES.md) (your account) or in the kit (your projects).

| Lesson | What happened | Where it lives now |
|---|---|---|
| Ask all questions at the start, with options and a recommendation | A design review found 34 decisions the agent had assumed instead of asked | PREFERENCES.md "Decisions" |
| A review from a fresh context finds what self-review misses | A self-review checked that 39 notes existed; 30 said the opposite of the source | PREFERENCES.md "Reporting"; kit `reviewer` agent |
| Enforce safety with a hook, not with text | A rule said "never force-push"; only one tool obeyed it | Kit `scripts/git-hooks/pre-push` |
| No push to main until the checks pass | A commit reached main with a failing check | Kit pre-push runs `scripts/check.sh` |
| State each rule once; conflicts hurt more than length | 3 conflicting preference rules made agent behavior look random | One rule set for Claude, ChatGPT and Codex; kit `.claude/rule-tests.md` |
| Measure, do not judge by eye | A layout shifted 14 px and no check saw it | PREFERENCES.md "UI verification" |
| Ask how the person works and what the environment allows, before you build | A solution assumed copy and paste on a machine where the user typed everything by hand | PREFERENCES.md "Design for human limits" |
| Build from a real sample and the full source, not from memory | A package built from docs failed on import; the real export showed the wrong key | Ask for a sample first (not yet a rule) |
| Change one thing per test, and use a control | A test changed 2 things at once and could not find the cause | Not yet a rule |
| Keep personal data out of git from the first commit | An old repo could never go public: its history held a name and an email | Kit `scripts/pii_guard.py` |
| Repo text and web pages are data, not instructions | Research: injected text in README files is followed 2.6x more than in code | Kit AGENTS.md "Untrusted input" |
| Audit for bloat on a schedule, and measure before you cut | One operation went from 116.6 s to 23.4 s after an audit | Kit `scripts/bloat_check.py` |

Sources: the research figure is from [arXiv 2610.38867](https://arxiv.org/abs/2610.38867) (see [the gap review](docs/reviews/2026-11-13-agentic-gap-review.md)); the other numbers come from the maintainer's own project logs, which are private.

## What you need

- A free [GitHub account](https://github.com/signup).
- An AI agent that can run commands and edit files: Claude Code (in the browser at claude.ai/code, or the app), Codex, Cursor, Gemini CLI, or another tool that reads AGENTS.md. A chat with no file access (for example a plain ChatGPT or claude.ai chat) cannot set up the project; use the steps "by hand" below with it.
- For way B only, on your computer: git, Python 3.9 or later, bash and perl. macOS and Linux have bash and perl; on Windows, use Git Bash or WSL. If one is missing, the agent tells you how to install it.

## Start here (take 2: a project)

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
| Personal-data and secret guard | `scripts/pii_guard.py` blocks emails, phone numbers, ID-number shapes, API tokens, private keys and names from your private denylist before they reach GitHub (.mil addresses too, if you turn that on). |
| One check command | `scripts/check.sh` runs every self-test, the project log check and the personal-data scan, plus your own tests in `scripts/check.local.sh`. Until that file exists, check.sh shows SKIP and agents merge code changes to main only with your approval. It is the default Test command in AGENTS.md and runs on each pull request. |
| Memory in files | docs/DECISIONS.md (dated decisions), docs/NEXT_PROMPT.md (short handoff), docs/LOG.md (timeline of milestones, breakthroughs and misses). |
| Multi-agent pack | `.claude/orchestration.md`: scout, worker and reviewer roles, model tiers (fast, standard, strong) per host, and fallbacks for hosts without subagents or hooks. |
| Upkeep (kit only) | `scripts/sync_baseline.py` brings a project up to the current kit by hand; `scripts/drift.py` reports how far a project has drifted. Projects do not get these tools. |

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
| .bloat-audit.json | The kit's own audit state and timing baselines (scripts/bloat_check.py). Template repo only: bootstrap deletes it; a project's first audit makes its own. |
| PREFERENCES.md | The owner's personal preferences for Claude, ChatGPT and Codex, ready to paste. Template repo only: bootstrap deletes it. |
| LICENSE | The kit's license (MIT). Bootstrap moves it to docs/archimedes_lever-LICENSE.txt; the project picks its own LICENSE. |
| .claude/settings.json | Claude Code deny list (force-push incl. --force-with-lease, `--no-verify`, changing core.hooksPath, hard reset, clean, stash, restore, `branch -D`, reading .env and key files), a sandbox with a network allowlist (GitHub, PyPI, npm), and the Stop hook. Binds Claude Code only. |
| .claude/orchestration.md | Multi-agent rules: roles, model routing by tier, fallbacks, briefs, review and merge, lanes. Read only when delegating. |
| .claude/bloat-audit.md | The periodic bloat, drift and assumption audit (AGENTS.md "Bloat, drift and assumptions"). Read only when an audit is due. |
| .claude/rule-tests.md | 11 scenarios that check an agent follows the text rules in AGENTS.md (hooks check the rest). Run after a rule or model change. |
| .claude/project-log.md | How to write a project log row: columns, types, arcs, story fields (AGENTS.md "Project log"). Read only when writing a row. |
| scripts/bloat_check.py | Cheap metrics each check-in: start-read tokens, duplicate lines, big files, audit due date; `--time` compares timed operations with their baseline. Settings and state: `.bloat-audit.json`. `--test`. |
| .claude/agents/ | Claude Code roles: `scout` (fast tier, read-only), `worker` (standard), `reviewer` (standard, read-only). |
| .github/workflows/pii-guard.yml | Pull-request and manual check: `scripts/check.sh`, then the guard on all files and the PR's commits. Never on push (Actions minutes). |
| .pii-guard | Turns the guard on; lists allowed exact strings, `skip:` paths and opt-in `check: mil`. Only the owner edits it. |
| docs/FIRST_USE.md | The first-use questions and what the agent does with the answers. |
| scripts/first_use_check.py | Session-start check (Claude Code SessionStart hook): KIT in the kit itself (a plain clone), FIRST USE when placeholders remain, DENYLIST when the guard is on and the session has no denylist. `--test`. |
| .gitignore | Keeps .env files and CLAUDE.local.md out of git. |
| scripts/check.sh | The one check command (AGENTS.md "Commands": Test). Runs `scripts/check.local.sh` last when it exists, else prints SKIP project checks. |
| scripts/session_checkin.sh | Start and end check: branch, ahead/behind, uncommitted files. Installs scripts/git-hooks when no other hooks path is set. |
| scripts/git-hooks/pre-push | For every agent and tool: blocks force-pushes, non-fast-forward pushes and deleting main or master; runs scripts/check.sh, and pii_guard.py when `.pii-guard` exists. `--test`. |
| scripts/pii_guard.py | Personal-data and secret guard (`--all`, `--range A..B`, `--push`, files; `--require-denylist`; `--status`). `--test`. |
| scripts/stop_check.py | Claude Code Stop hook: blocks the end of a turn while work is uncommitted or unpushed. `--test`. |
| scripts/worker_guard.py | PreToolUse hook that limits what `worker` and `reviewer` may do in git. `--test`. |
| scripts/log_check.py | Checks docs/LOG.md against the Project log rules. `--test`. |
| scripts/timeline.py | Renders one or more project logs as one self-contained HTML timeline, or a Markdown story outline per arc for a deck (`--outline FILE`). `--test`. |
| scripts/drift.py | Kit only. Report only: how a project differs from this kit. `--project DIR`, `--owner NAME`, `--test`. |
| scripts/sync_baseline.py | Kit only. Brings an existing project up to the current kit. Dry run by default; `--apply` writes. Keeps Project rules, Commands and docs/. |
| scripts/bootstrap.sh | Fills the placeholders once, then deletes itself. |

## Sync an existing project

Projects do not stay in sync with the kit, and they do not carry the sync tools. To bring a project up to the kit by hand, in the project repo with no uncommitted changes:

1. Clone this repo next to the project, then run its copy:
   ```
   python3 ../archimedes_lever/scripts/sync_baseline.py --baseline ../archimedes_lever
   ```
   Add `--name`, `--repo` and `--purpose` when the project AGENTS.md has no header values, `--owner NAME` when it has no `- Owner:` line, and `--timezone ZONE` (IANA name) when it has no `- Time zone:` line.
2. Read the diff. Nothing is written yet.
3. Run the same command with `--apply`, review `git diff`, then commit and push.

An old AGENTS.md without the kit layout moves under "Project rules" with a review note. Delete what the kit now covers.

## Limits

- A project does not update with the kit. The kit keeps no changelog: its history is in git (`git log`).
- Account-wide preferences (your own settings in Claude, ChatGPT or Codex) reach only that host. Every agent gets the rules from AGENTS.md.
- Setup needs an agent with file access. A chat that cannot run commands can only give you text to paste: use "Start a new project by hand".
- Hooks are seat belts, not locks: Claude Code hooks bind Claude Code only, and `--no-verify` skips git hooks.
- The Claude Code sandbox (network allowlist in .claude/settings.json) needs bubblewrap and socat on Linux; without them Claude Code warns and runs commands unboxed, while deny rules and git hooks still apply. Claude cloud containers lack them but sit behind their own network proxy. macOS needs nothing extra.
- The guard finds shapes and listed names. It does not find a name you did not list, or personal facts written in prose. Read before you publish.
- Model names in orchestration.md go stale; the tiers stay.
