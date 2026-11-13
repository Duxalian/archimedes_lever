# Kit files

Every file in the archimedes_lever kit and what it does. Kit only: `scripts/bootstrap.sh` deletes this file, because a project gets its own README.

| File | What it does |
|---|---|
| AGENTS.md | Rules for every agent. Project rules go at the end. |
| CLAUDE.md | One line that imports AGENTS.md, because Claude Code reads CLAUDE.md. |
| GEMINI.md | One line that imports AGENTS.md, because Gemini CLI reads GEMINI.md. Codex, Copilot and Cursor read AGENTS.md directly. |
| docs/NEXT_PROMPT.md | Short handoff: where things stand, open work, and what needs the owner. |
| docs/DECISIONS.md | Dated decision log, separating owner decisions from agent recommendations. |
| docs/WORKING_WITH_AGENTS.md | For people new to agents: the working loop, clean context, how to ask, what to check. |
| docs/LOG.md | Full only. Project log for a timeline and a story deck: milestones, breakthroughs, misses and decisions, grouped into arcs. Each arc has a Problem, Turning point, Outcome and Lesson. A public repo keeps the log in a private place named in Project rules. |
| docs/host-prompts.md | Short pointer texts for a claude.ai Project, ChatGPT, Gemini and any other chat. |
| docs/FILES.md | This list. Kit only: bootstrap deletes it. |
| docs/reviews/ | Detailed evidence. Bootstrap deletes the kit's own reports, so a project starts with only docs/reviews/README.md. |
| .bloat-audit.json | The kit's own audit state and timing baselines (scripts/bloat_check.py). Template repo only: bootstrap deletes it, and a project's first audit creates its own. |
| PREFERENCES.md | The maintainer's personal preferences for Claude, ChatGPT and Codex, as a template ready to fill in and paste: a core for everyone, plus Builder, Data and Agent work modules. Template repo only: bootstrap deletes it. |
| LICENSE | The kit's license (MIT). Bootstrap moves it to docs/archimedes_lever-LICENSE.txt; each project picks its own LICENSE. |
| .claude/settings.json | Claude Code deny list (force-push including --force-with-lease, `--no-verify`, changing core.hooksPath, hard reset, clean, stash, restore, `branch -D`, reading .env and key files), a sandbox with a network allowlist (GitHub, PyPI, npm), and the Stop hook. Applies to Claude Code only. |
| .claude/orchestration.md | Full only. Multi-agent rules: roles, model choice by tier, fallbacks, briefs, review and merge, lanes. Read only when delegating. |
| .claude/bloat-audit.md | Full only. The periodic bloat, drift and assumption audit (AGENTS.md "Bloat, drift and assumptions"). Read only when an audit is due. |
| .claude/rule-tests.md | Full only. 11 scenarios that check whether an agent follows the written rules in AGENTS.md (hooks check the rest). Run after a rule change or a model change. |
| .claude/project-log.md | Full only. How to write a project log row: columns, types, arcs, story fields (AGENTS.md "Project log"). Read only when writing a row. |
| scripts/bloat_check.py | Full only. Quick measurements at each check-in: start-up reading size in tokens, duplicate lines, big files, audit due date. `--time` compares timed operations with their baseline. Settings and state: `.bloat-audit.json`. `--test`. |
| .claude/agents/ | Claude Code roles: `reviewer` (standard, read-only); full only: `scout` (fast tier, read-only), `worker` (standard). |
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
| scripts/log_check.py | Full only. Checks docs/LOG.md against the project log rules. `--test`. |
| scripts/timeline.py | Full only. Turns one or more project logs into a single self-contained HTML timeline, or a Markdown story outline per arc for a deck (`--outline FILE`). `--test`. |
| scripts/drift.py | Kit only. Reports how a project differs from this kit; changes nothing. `--project DIR`, `--owner NAME`, `--test`. |
| scripts/sync_baseline.py | Kit only. Brings an existing project up to the current kit. Dry run by default; `--apply` writes. Keeps Project rules, Commands and docs/. `--tier full` adds the advanced parts to a starter project. Holds the `ADVANCED_FILES` list. |
| scripts/bootstrap.sh | Fills in the placeholders once, then deletes itself. |
