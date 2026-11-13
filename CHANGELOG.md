# Baseline changelog

Template repo only: scripts/bootstrap.sh deletes this file in new projects. Newest first. "Decided" = decision by the owner. "Rec" = agent recommendation that the owner has not approved.

## 2026-11-13: bloat, drift and assumption checks

- Decided (the owner): every project runs periodic checks against bloat, drift and duplication. Evidence: two audits of one project found layered bloat; one simple operation went from 116.6 s to 23.4 s after the fix.
- Added: AGENTS.md section "Bloat, drift and assumptions" (one place per fact; a change removes what it makes obsolete; state key assumptions with source and confidence, ask on low confidence); `scripts/bloat_check.py` (run by the check-in, self-test in check.sh); `.claude/bloat-audit.md` (the full audit prompt, general and agentic-AI categories). sync_baseline.py copies both.
- Decided (the owner): when the host has a clickable question tool, agents also ask with it for 1–4 open questions (AGENTS.md "Authority").
- Decided (1A, 2026-11-13): audit every 14 days or 30 commits to main; start-read budget 12,000 tokens; timing alarm at +25%. Fresh review: 0 MAJOR, 9 MINOR; 8 fixed (bad config, encoding, shallow clone, no git, 0.0 s and failed-command baselines, quiet self-test, first-sync note), 1 needed no change (sync carries the new AGENTS.md section).

## 2026-11-11: beginner start

- Decided: README "Start here" has two ways with no git for the user: A, "Use this template" plus Claude Code on the web; B, an agent app that clones the kit from its URL. `git clone` stays as one line for people who know git.
- Decided (1A): the denylist comes before the first push. FIRST_USE.md step 4: on a computer the user creates the file in the same session; in a cloud session the agent stops before bootstrap and gives a prompt with all answers for a new session. The pre-push hook now says "no name denylist" when that is the cause, not "personal data".
- Decided (2A): fast path. Round 1 asks name, purpose, time zone, and "use the recommended settings?"; the other questions only on "choose each one".
- Decided (3A): questions numbered 1 to 12 in the order they are asked.
- Decided (5A): question 12 asks a public repo where the project log goes (private Claude doc, in the repo, or none).
- Decided (4A): README order: What you need, Start here, After setup, What you get, by hand; the "First use" section and the "Or tell your agent" line are gone.

## 2026-11-11: a starter for anyone

- Decided: the kit is a starter for one new project, for the owner or anyone else; managing many projects from one place is out of scope.
- Decided (1B): added `scripts/check.sh` (one check command: every self-test, the project log check, the personal-data scan, then `scripts/check.local.sh`), set as the default Test command in AGENTS.md "Commands" and run by the pull-request workflow; a secret scan in `scripts/pii_guard.py` (GitHub, GitLab, AWS, Anthropic, OpenAI, Google, Slack and Stripe tokens, private-key headers; printed as a length only); a "What you need" section in README.md; first-use question 8 (license) and 9 (time zone).
- Decided (1B): the time zone is a project setting: `- Time zone:` line in AGENTS.md, bootstrap 5th argument (default UTC), `sync_baseline.py --timezone` for projects without the line. The log column is now "When"; log_check.py still accepts an older "When (CT)" header. timeline.py reads the zone from each log.
- Decided (1B): the .internal check is opt-in (`check: internal` in .pii-guard; first-use question 5 option B). sync_baseline.py prints a note for a project whose .pii-guard has no such line, because the next sync turns its .internal check off.
- Decided (2A): the 3 preference files moved to a private Claude doc. Replaces 3A of the "archimedes_lever" entry below.
- Decided: a plain clone works as a start. `first_use_check.py` reports KIT for the kit repo; on "initiate" the agent follows docs/FIRST_USE.md step 0 (question 10: where the repo goes). README "Start here" is the QR-code target.
- Decided (3B): a clone-started project gets a fresh history (orphan `main`); the kit's history stays on the local `kit-main` branch and is never pushed.
- Decided (2A): the LICENSE copyright holder is the GitHub handle "[old handle]". Decided (4B): the repo stays private until the owner has read the merged README; then the owner makes it public.
- Decided (3A): the kit is MIT licensed (LICENSE). Bootstrap moves it to docs/archimedes_lever-LICENSE.txt, which sync keeps current; the project chooses its own LICENSE.

## 2026-11-11: skip rule and PII scan

- Fixed: denylist entries copied as `<Name>` (from a placeholder) matched nothing, so names were not checked. The guard now drops one wrapping pair of `<>` or quotes, and drops entries under 2 characters or with no letter or digit. A name inside an allowed string on the same line (for example a host name) is not flagged; allowed strings match in any case. Fresh review: 0 MAJOR, 3 MINOR (2 fixed; accepted: an allowed string that contains a name hides it).
- Added: a `skip: <path or glob>` line in `.pii-guard` excludes a path from the file and commit scans (for a public reference text that quotes office contacts). A bare `*` or `**` is ignored; the report line lists the skip rules. Fresh review: 0 MAJOR, 4 MINOR, all fixed (quoted and spaced paths in commit scans, `#` inside a path, `./` file arguments).
- Fixed: sync_baseline.py keeps scripts/first_use_check.py and docs/FIRST_USE.md as written (no owner rename), as bootstrap does.

## 2026-11-11: first use

- Decided (1A): first use is agent-driven. `scripts/first_use_check.py` (Claude Code SessionStart hook; other agents run it first) reports FIRST USE while AGENTS.md has placeholders (the template repo itself is skipped), and DENYLIST when `.pii-guard` is on and the session has no denylist. docs/FIRST_USE.md holds 7 questions in 2 rounds and the steps. The agent never asks for the denylist names; the owner types them in each settings page.
- Decided (2A): with `.pii-guard` on, the pre-push hook and the pull-request Action fail when no denylist is found (`pii_guard.py --require-denylist`). `--status` prints the source and the count, never the names. The denylist can also come from the environment variable `PII_GUARD_DENYLIST` (comma or newline separated), for Claude cloud environments.
- Decided (3A): the owner adds `PII_GUARD_DENYLIST` to each cloud environment the owner's projects use.
- Fresh review (0 MAJOR, 9 MINOR): fixed: one shared denylist rule in both scripts (a comment-only variable no longer hides the file); each session-start check fails on its own; a push of branch deletes only needs no denylist; sync adds docs/FIRST_USE.md when missing; question 4 option C warns about the guard; tests for `--require-denylist`, `--status` and deletes. Accepted: a stale guard copy without `--require-denylist` blocks the push (fails closed); the hook needs `python3` on PATH.

## 2026-11-11: archimedes_lever

- Decided (1A): this repo replaces [old handle]/standard_project as the baseline, with a fresh history (one clean first commit). The old history is not copied: it holds a personal email address and a real name in commit messages.
- Decided: baseline text names no person. "the owner" (and "The owner") replaces the old real name. bootstrap.sh and sync_baseline.py replace it with the project owner; a private repo may keep a real name (`--owner NAME`), a public repo uses a role. drift.py gained `--owner` for repos with no `- Owner:` line.
- Decided (3A): the 3 preference files stay as examples; the job title is now `<your role>` / `<your field>`.
- Decided (4A): the repo starts private; the owner reviews it, then makes it public.
- Decided (2A): [old handle]/standard_project is archived after the projects point here; it is not deleted.
- Added scripts/pii_guard.py: blocks emails (except GitHub noreply and no-reply placeholders), phone numbers, .internal addresses, ID-number shapes and names from a denylist kept outside the repo. Runs in scripts/git-hooks/pre-push and in a pull_request GitHub Action. AGENTS.md "Personal data" rule.
- Example role in docs and tests: "the maintainer".
- Fresh review (2026-11-11, 2 MAJOR, 8 MINOR): fixed: the Action reads .pii-guard from the PR base; names print as a length only and emails as ***@domain; the hook finds the guard in scripts/ or tools/ and blocks if it is missing; owner rename uses one word-boundary pass; keyword-gated phone and SSN forms; URL paths are not phones; allow entries match exactly. Accepted: noreply@ on any domain; fork PRs have no secret, so names are not checked there.

## 2026-11-11

- Decided (1A): timeline.py approved from the preview (contrast min 5.22:1 light, 7.49:1 dark; no overflow at 375 and 1440 px); sync copies it.
- Decided (2A): the earlier baseline repo stays private. A public copy would tie the owner's name and role to the account, and history cannot be rewritten. Replaced on 2026-11-11 by this repo (fresh history, see above).
- Decided (1B): add scripts/log_check.py (project log check) and scripts/drift.py (report-only baseline drift). Timeline renderer waits for a preview approval.
- Decided: model-agnostic orchestration. Routing names tiers (fast, standard, strong) with a model table per host; "Fallbacks" covers hosts without subagents, hooks, worktrees or artifacts; GEMINI.md imports AGENTS.md; scripts/git-hooks/pre-push blocks force-pushes for every tool and session_checkin.sh installs it. AGENTS.md wording no longer assumes Claude.
- Decided: owner name. AGENTS.md has a `- Owner:` header line. A public repo sets a role: bootstrap 4th argument, or `sync_baseline.py --owner "<role>"` once. Sync and bootstrap rename the owner in baseline text only (AGENTS.md above Project rules, copied scripts and orchestration); project text is never renamed; sync_baseline.py keeps the literal. (Changed 2026-11-11: the baseline word is now "the owner".)
- Decided: add the project log (AGENTS.md "Project log", template docs/LOG.md) as the source for a timeline of milestones, breakthroughs and narratives. Columns: # | When (CT) | Type | Arc | Topic | Raised by | What the other missed | Evidence | Result, plus an Arcs table. Types: milestone, breakthrough, miss, decision. A public repo keeps the log in a private place named in Project rules. Existing projects get the rule with scripts/sync_baseline.py (it does not copy docs/LOG.md). Claude preferences v3 add a one-line pointer.
- Decided: scripts/stop_check.py blocks a detached HEAD (also a rebase that is not finished) that has commits not on origin/main (else origin/master). With no such ref, a detached HEAD still passes. `--test`: 13 cases.
- Decided: scripts/stop_check.py passes a clean read-only checkout: no changes (untracked files included), no stash, and HEAD on origin/main (else origin/master) or behind it. Before, an unpushed session branch with no work of its own blocked the stop. A stash now blocks on every path. Added `--test` (11 cases). Projects get it with scripts/sync_baseline.py.

## 2026-11-10

- Decided: add the orchestration pack, adapted from an earlier project: .claude/agents/ (scout haiku, worker sonnet, reviewer sonnet), scripts/worker_guard.py, .claude/orchestration.md with the model routing table. The orchestrator stays on Opus. Sync adds agent files only when missing.
- Added docs/codex-agents.md v1: Codex global instructions from preferences v2.
- Decided: bootstrap writes .baseline (baseline commit from git ls-remote).
- Decided: add a generic Stop hook (scripts/stop_check.py), adapted from an earlier project's Stop hook. Status files per workstream: not added.
- Added docs/gpt-preferences.md v1: ChatGPT version of preferences v2 (3,597 of 5,000 characters). Claude-only items left out: clickable dialog, task-list widget, parallel-file rule, running owner for unattended work.
- Decided: build the sync script now (scripts/sync_baseline.py), before the first project sync.
- Decided: AGENTS.md delivery rules win over the personal "preview first" rule for changes that are not UI or design. Personal preferences rank below AGENTS.md.
- Decided: the fresh reviewer before a merge applies only to changes to code, checks or scripts. Docs-only changes skip it.
- Decided: add enforcement: .claude/settings.json deny list and .gitignore.
- Decided: add "Commands" and "Verification" sections to AGENTS.md. Verification carries the UI measuring rule, so GPT and Codex get it.
- Decided: the reporting line follows summary format C (Decide, Copy, then Step, Status, Risks, Running, Not running, Next step, Links).
- Decided: keep this changelog in the template repo only. Build a sync script for older projects later. Rec: build the sync script before the first sync.
- Decided: keep a versioned copy of the owner's claude.ai personal preferences in docs/claude-preferences.md (template repo only). Current version: v2.
