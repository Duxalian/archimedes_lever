# archimedes_lever

A starter kit for working with AI assistants (Claude, ChatGPT, Codex and others) so that they are reliable and need little effort from you. It collects lessons from real projects in a form you can copy.

The name comes from Archimedes: "Give me a place to stand, and I will move the world." Here, the place to stand is a set of files that every agent reads, so your rules, decisions and history stay put instead of disappearing with each chat.

## Try it first

Paste this into Claude (claude.ai or Claude Code), or any assistant that can read web pages:

```
Tell me your thoughts about this repo: https://github.com/rhope-ops/archimedes_lever
```

## What you can take from it

| Take | What you get | Time | What you need |
|---|---|---|---|
| 1. [Preferences](PREFERENCES.md) for your own AI account | Every chat asks its questions up front, labels its recommendations, says how confident it is, checks its work before it says "done", and saves you clicks and copying | About 5 minutes (our estimate, not timed): the assistant asks you 4 questions and gives you one block to paste | Any Claude, ChatGPT or Codex account. No GitHub needed. |
| 2. A project kit (the rest of this repo) | A new project where every agent follows one rules file, where force-pushes and pushes that contain your listed names or your email are blocked, where agents check their own work, and where decisions are written down | About 15 minutes with an agent (our estimate, not timed); see "Start here" below | A free GitHub account and an agent that can run commands |

You can take 1 without 2. To do it, ask your assistant:

```
Interview me and fill in PREFERENCES.md from https://github.com/rhope-ops/archimedes_lever for Claude
```

Replace "Claude" with "ChatGPT" or "Codex" if that is what you use.

## The lessons behind the rules

These are things that went wrong across 5 real projects, and the rule each one led to. Each rule now lives either in [PREFERENCES.md](PREFERENCES.md) (your account) or in the kit (your projects).

| Lesson | What happened | Where the rule lives |
|---|---|---|
| Ask all questions at the start, with options and a recommendation | A design review found 34 decisions the agent had assumed instead of asking | PREFERENCES.md "Decisions" |
| A review in a fresh context finds what self-review misses | A self-review checked that 39 notes existed; 30 of them said the opposite of the source | PREFERENCES.md "Reporting"; the kit's `reviewer` agent |
| Enforce safety with a hook, not just with written rules | A rule said "never force-push"; only one tool obeyed it | The kit's `scripts/git-hooks/pre-push` |
| Don't push to main until the checks pass | A commit reached main with a failing check | The kit's pre-push hook runs `scripts/check.sh` |
| State each rule once; conflicting rules hurt more than long ones | 3 conflicting preference rules made the agent's behavior look random | One rule set for Claude, ChatGPT and Codex; the kit's `.claude/rule-tests.md` |
| Measure; don't judge by eye | A layout shifted 14 px and no check noticed | PREFERENCES.md "UI verification" |
| Before you build, ask how the person works and what their setup allows | A solution assumed copy and paste, on a machine where the user had to type everything by hand | PREFERENCES.md "Design for human limits" |
| Build from a real sample and the full source, not from memory | A package built from the docs failed on import; a real export showed the wrong key | Ask for a sample first (not yet a rule) |
| Change one thing per test, and use a control | A test changed 2 things at once and could not find the cause | Not yet a rule |
| Keep personal data out of git from the very first commit | An old repo could never go public, because its history held a name and an email | The kit's `scripts/pii_guard.py` |
| Treat text in repos and on web pages as data, not as instructions | Research: one model followed an instruction injected into a README or TODO file 2.6 times more often than the same instruction in a code or data file | The kit's AGENTS.md "Untrusted input" |
| Check for bloat on a schedule, and measure before you cut | One operation went from 116.6 s to 23.4 s after an audit | The kit's `scripts/bloat_check.py` |

Sources: the research figure is from [arXiv 2610.38867](https://arxiv.org/abs/2610.38867) (see [the gap review](docs/reviews/2026-11-13-agentic-gap-review.md)). The other numbers come from the maintainer's own project logs, which are private.

## What you need

- A free [GitHub account](https://github.com/signup).
- An AI agent that can run commands and edit files: Claude Code (in the browser at claude.ai/code, or the app), Codex, Cursor, Gemini CLI, or any other tool that reads AGENTS.md. A plain chat with no file access (such as a regular ChatGPT or claude.ai chat) can't set up the project; use "Set up a project by hand" below instead.
- For way B only, on your computer: git, Python 3.9 or later, bash and perl. macOS and Linux already have bash and perl; on Windows, use Git Bash or WSL. If something is missing, the agent tells you how to install it.

## Start here (take 2: a project)

You don't need to know git: the agent handles it. Pick one way.

**A. In your browser, with nothing to install** (Claude Code on the web)

1. On this page, click **Use this template → Create a new repository**. Type your project's name and choose **Private**.
2. Open [claude.ai/code](https://claude.ai/code), connect GitHub when it asks, and start a session on your new repository.
3. Type:
   ```
   Please read the repo and initiate.
   ```

**B. With an agent app on your computer** (Claude Code, Codex, Cursor, Gemini CLI)

1. Open the app in the folder where you keep your projects (your Documents folder is fine).
2. Type:
   ```
   Please set up a new project from https://github.com/rhope-ops/archimedes_lever: get the repo, read it, and initiate.
   ```

Either way, the agent asks you 4 questions: the project's name, what it is for, your time zone, and whether to use the recommended settings. It explains each one. If you're not sure, pick the answer it marks as recommended. Then it creates your GitHub repository, fills in the project files and tells you what is left to do.

One step is yours. The agent asks you to type your own names into a private list. The personal-data guard checks every push against that list, so your names never end up on GitHub by mistake. You never type the names into the chat. In the browser (way A), this means you add a setting and start one new session; the agent gives you a prompt to paste there, so you don't have to answer the questions again.

Also in the browser (way A): Claude Code may only be allowed to push to its own branch, not to `main`. If so, the agent tells you the push to `main` is blocked. Type `Please open a pull request`, open the link it gives you, and click **Merge pull request**.

If you know git, you can instead run `git clone https://github.com/rhope-ops/archimedes_lever my-project`, open the folder with your agent, and type `Please read the repo and initiate.`

Details for agents: [docs/FIRST_USE.md](docs/FIRST_USE.md).

## After setup

Open the project with any agent and say what you want to do next. The agent first reads AGENTS.md (the rules) and docs/NEXT_PROMPT.md (where the work stands), so you don't have to explain the project again in every chat.

## What's in the kit

| Part | What it does for you |
|---|---|
| AGENTS.md | One rules file for every agent: who decides, how work is delivered and reported, git safety, personal data, decisions, handoff, the project log and delegation. Your own project rules go at the end. |
| Safety hooks | `scripts/git-hooks/pre-push` blocks force-pushes, deleting main, and pushes that fail `scripts/check.sh`, for every tool (a push with `--no-verify` skips it; see Limits). The Claude Code Stop hook stops a turn from ending while work is unsaved or unpushed. |
| Personal-data and secret guard | `scripts/pii_guard.py` blocks emails, phone numbers, ID-number patterns, API tokens, private keys and the names on your private list before they reach GitHub. |
| One check command | `scripts/check.sh` runs every self-test, the project log check and the personal-data scan, plus your own tests in `scripts/check.local.sh`. Until that file exists, check.sh shows SKIP, and agents merge code changes to main only with your approval. It is the default test command in AGENTS.md and runs on every pull request. |
| Memory in files | docs/DECISIONS.md (dated decisions), docs/NEXT_PROMPT.md (a short handoff note), docs/LOG.md (a timeline of milestones, breakthroughs and misses). |
| Multi-agent pack | `.claude/orchestration.md`: scout, worker and reviewer roles, model tiers (fast, standard, strong) for each host, and fallbacks for hosts without subagents or hooks. |
| Upkeep (kit only) | `scripts/sync_baseline.py` brings a project up to the current kit by hand; `scripts/drift.py` reports how far a project has drifted. Projects don't get these tools. |

## Set up a project by hand

For people who know git and don't want an agent to do the setup, or who only have a chat with no file access.

1. Create the repo from this template:
   ```
   gh repo create YOUR_USER/NEW_NAME --private --template rhope-ops/archimedes_lever --clone
   ```
   Or on GitHub: **Use this template → Create a new repository**, then clone it.
2. In the new repo, fill in the placeholders:
   ```
   scripts/bootstrap.sh "Project Name" YOUR_USER/NEW_NAME "One-line purpose" "the owner" "Europe/Berlin"
   ```
   The 4th argument is what agents call you (default "the owner"). A public repo should use a role, such as `"the maintainer"`. A private repo can use your first name, but only with the guard turned off (delete `.pii-guard`), because the guard blocks every push that contains a name on your list. The 5th argument is your time zone for project log times, as an IANA name (default UTC).
   Bootstrap moves the kit's MIT license to docs/archimedes_lever-LICENSE.txt. Keep that file: it covers the kit's scripts. Add your own `LICENSE` if you want one.
3. Set up your name list (next section), run `scripts/session_checkin.sh` (it installs the git hooks), then commit and push.
4. Paste the Project text from `docs/host-prompts.md` into your claude.ai Project instructions (or the ChatGPT or Gemini equivalent).

## Keep personal data out

With the guard on, every push and every pull-request check fails until your name list exists. Set it up in each place you work: your computer (step 2), GitHub (step 3), and, for Claude cloud sessions, the cloud environment variable `PII_GUARD_DENYLIST`. `python3 scripts/pii_guard.py --status` shows where the list comes from and how many entries it has, never the names themselves.

1. Commit with your GitHub noreply address. On GitHub, go to **Settings → Emails** and turn on "Keep my email addresses private" and "Block command line pushes that expose my email". Then run:
   ```
   git config --global user.email "ID+USER@users.noreply.github.com"
   ```
2. Create a name list on your computer, one entry per line (your names, username variants, employer). It never goes into a repo:
   ```
   mkdir -p ~/.config/pii-guard && nano ~/.config/pii-guard/denylist.txt
   ```
3. Add the same list as an Actions secret named `PII_GUARD_DENYLIST` (repo **Settings → Secrets and variables → Actions**), so the pull-request check also checks names.
4. Check it: `python3 scripts/pii_guard.py --all`. It prints PII GUARD PASS, or each finding with the value masked.

The guard only runs in a repo that has a `.pii-guard` file at its root. That file also lists exact strings you want to allow. A private repo that names you on purpose can delete it.

## Files

| File | What it does |
|---|---|
| AGENTS.md | Rules for every agent. Project rules go at the end. |
| CLAUDE.md | One line that imports AGENTS.md, because Claude Code reads CLAUDE.md. |
| GEMINI.md | One line that imports AGENTS.md, because Gemini CLI reads GEMINI.md. Codex, Copilot and Cursor read AGENTS.md directly. |
| docs/NEXT_PROMPT.md | Short handoff: where things stand, open work, and what needs the owner. |
| docs/DECISIONS.md | Dated decision log, separating owner decisions from agent recommendations. |
| docs/LOG.md | Project log for a timeline and a story deck: milestones, breakthroughs, misses and decisions, grouped into arcs. Each arc has a Problem, Turning point, Outcome and Lesson. A public repo keeps the log in a private place named in Project rules. |
| docs/host-prompts.md | Short pointer texts for a claude.ai Project, ChatGPT, Gemini and any other chat. |
| docs/reviews/ | Detailed evidence. Bootstrap deletes the kit's own reports, so a project starts with only docs/reviews/README.md. |
| .bloat-audit.json | The kit's own audit state and timing baselines (scripts/bloat_check.py). Template repo only: bootstrap deletes it, and a project's first audit creates its own. |
| PREFERENCES.md | The maintainer's personal preferences for Claude, ChatGPT and Codex, as a template ready to fill in and paste. Template repo only: bootstrap deletes it. |
| LICENSE | The kit's license (MIT). Bootstrap moves it to docs/archimedes_lever-LICENSE.txt; each project picks its own LICENSE. |
| .claude/settings.json | Claude Code deny list (force-push including --force-with-lease, `--no-verify`, changing core.hooksPath, hard reset, clean, stash, restore, `branch -D`, reading .env and key files), a sandbox with a network allowlist (GitHub, PyPI, npm), and the Stop hook. Applies to Claude Code only. |
| .claude/orchestration.md | Multi-agent rules: roles, model choice by tier, fallbacks, briefs, review and merge, lanes. Read only when delegating. |
| .claude/bloat-audit.md | The periodic bloat, drift and assumption audit (AGENTS.md "Bloat, drift and assumptions"). Read only when an audit is due. |
| .claude/rule-tests.md | 11 scenarios that check whether an agent follows the written rules in AGENTS.md (hooks check the rest). Run after a rule change or a model change. |
| .claude/project-log.md | How to write a project log row: columns, types, arcs, story fields (AGENTS.md "Project log"). Read only when writing a row. |
| scripts/bloat_check.py | Quick measurements at each check-in: start-up reading size in tokens, duplicate lines, big files, audit due date. `--time` compares timed operations with their baseline. Settings and state: `.bloat-audit.json`. `--test`. |
| .claude/agents/ | Claude Code roles: `scout` (fast tier, read-only), `worker` (standard), `reviewer` (standard, read-only). |
| .github/workflows/pii-guard.yml | Pull-request and manual check: `scripts/check.sh`, then the guard on all files and the pull request's commits. Never runs on push (to save Actions minutes). |
| .pii-guard | Turns the guard on; lists allowed exact strings and `skip:` paths. Only the owner edits it. |
| docs/FIRST_USE.md | The first-use questions and what the agent does with the answers. |
| scripts/first_use_check.py | Session-start check (Claude Code SessionStart hook): says KIT in the kit itself (a plain clone), FIRST USE when placeholders remain, and DENYLIST when the guard is on and the session has no name list. `--test`. |
| .gitignore | Keeps .env files and CLAUDE.local.md out of git. |
| scripts/check.sh | The one check command (AGENTS.md "Commands": Test). Runs `scripts/check.local.sh` last if it exists; otherwise prints SKIP for project checks. |
| scripts/session_checkin.sh | Start and end check: branch, ahead/behind, uncommitted files. Installs scripts/git-hooks when no other hooks path is set. |
| scripts/git-hooks/pre-push | For every agent and tool: blocks force-pushes, non-fast-forward pushes and deleting main or master; runs scripts/check.sh, and pii_guard.py when `.pii-guard` exists. `--test`. |
| scripts/pii_guard.py | Personal-data and secret guard (`--all`, `--range A..B`, `--push`, files; `--require-denylist`; `--status`). `--test`. |
| scripts/stop_check.py | Claude Code Stop hook: stops a turn from ending while work is uncommitted or unpushed. `--test`. |
| scripts/worker_guard.py | PreToolUse hook that limits what `worker` and `reviewer` may do in git. `--test`. |
| scripts/log_check.py | Checks docs/LOG.md against the project log rules. `--test`. |
| scripts/timeline.py | Turns one or more project logs into a single self-contained HTML timeline, or a Markdown story outline per arc for a deck (`--outline FILE`). `--test`. |
| scripts/drift.py | Kit only. Reports how a project differs from this kit; changes nothing. `--project DIR`, `--owner NAME`, `--test`. |
| scripts/sync_baseline.py | Kit only. Brings an existing project up to the current kit. Dry run by default; `--apply` writes. Keeps Project rules, Commands and docs/. |
| scripts/bootstrap.sh | Fills in the placeholders once, then deletes itself. |

## Update an existing project

Projects don't stay in sync with the kit automatically, and they don't carry the sync tools. To bring a project up to date by hand, start in the project repo with no uncommitted changes:

1. Clone this repo next to the project, then run its copy of the sync script:
   ```
   python3 ../archimedes_lever/scripts/sync_baseline.py --baseline ../archimedes_lever
   ```
   Add `--name`, `--repo` and `--purpose` if the project's AGENTS.md has no header values, `--owner NAME` if it has no `- Owner:` line, and `--timezone ZONE` (an IANA name) if it has no `- Time zone:` line.
2. Read the diff. Nothing has been written yet.
3. Run the same command with `--apply`, review `git diff`, then commit and push.

An old AGENTS.md that doesn't follow the kit's layout is moved under "Project rules" with a review note. Delete whatever the kit now covers.

## Limits

- A project doesn't update when the kit does. The kit keeps no changelog; its history is in git (`git log`).
- Account-wide preferences (your own settings in Claude, ChatGPT or Codex) only apply in that product. Every agent gets the project rules from AGENTS.md.
- Setup needs an agent with file access. A chat that can't run commands can only give you text to paste; use "Set up a project by hand".
- With the guard on, the pull-request check needs the `PII_GUARD_DENYLIST` secret. GitHub doesn't give secrets to pull requests from forks, so a pull request from a fork always fails the check. The maintainer checks it by hand, or copies it to a branch in the repo.
- The pull-request check runs the scripts from the pull request itself, so a pull request that edits `scripts/pii_guard.py` or `scripts/check.sh` can change the result. Review changes to those files by hand.
- Hooks are seat belts, not locks: Claude Code hooks only apply to Claude Code, and `--no-verify` skips git hooks.
- The Claude Code sandbox (the network allowlist in .claude/settings.json) needs bubblewrap and socat on Linux. Without them, Claude Code warns you and runs commands outside the sandbox; the deny rules and git hooks still apply. Claude cloud containers don't have them, but they sit behind their own network proxy. macOS needs nothing extra.
- The guard finds patterns and the names on your list. It can't find a name you didn't list, or personal details written out in sentences. Read everything before you publish.
- Model names in orchestration.md go out of date; the tiers stay the same.
