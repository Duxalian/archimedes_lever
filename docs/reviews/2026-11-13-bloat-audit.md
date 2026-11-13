# Bloat, drift and assumption audit: the kit (2026-11-13)

First full audit of the kit (`.claude/bloat-audit.md`), asked for by the owner on 2026-11-13. Audited commit: 6f5f4f1. Machine: cloud container, 4 vCPU Intel Xeon 2.10 GHz. Removals are proposals only (the owner, 2026-11-13); nothing was removed.

## Before and after

| Measure | Before | After | Budget |
|---|---|---|---|
| Start read (~tokens) | 3,740 | 3,799 (+59: host-limit rule in AGENTS.md "Delivery") | 12,000 (warn 6,000) |
| AGENTS.md words | 2,387 | 2,421 | - |
| Duplicate lines (80+ chars, 2+ files) | 2 | 2 | 20 |
| Tracked files / size | 38 / 252 KB | 40 / ~262 KB (this report, `.bloat-audit.json`) | - |
| Big files | 0 | 0 | 500 KB |
| Timing: `check` (scripts/check.sh) | not measured | 2.9 s (baseline) | +25% |
| Timing: `checkin` (scripts/session_checkin.sh) | not measured | 0.9 s (baseline) | +25% |
| Timing: `bloat-brief` | not measured | 0.1 s (baseline) | +25% |
| Removals proposed / approved / made | - | 6 / 0 / 0 | - |
| Rules removed or merged | - | 0 (1 added, owner request) | - |
| Key assumptions: high / medium / low / untraced | - | 3 / 3 / 1 / 0 | - |

Commands: `python3 scripts/bloat_check.py --time --record`; `wc -w AGENTS.md`; `git ls-files | xargs wc -c`.

## AGENTS.md cost by section (words)

| Section | Words | Note |
|---|---|---|
| Project log | 412 | 17% of the file; needed only when a log row is written |
| Bloat, drift and assumptions | 212 | |
| Personal data | 211 | half restates README "Keep personal data out" and pii_guard.py |
| Delivery | 163 → 197 | host-limit rule added |
| Git safety | 160 | 2 bullets describe what pre-push and settings.json enforce |
| Others (14 sections) | 1,229 | |

## Fixes made (exceptions list only)

1. `.bloat-audit.json` created (exception a): audit state and 3 timing baselines. `scripts/bootstrap.sh` deletes it with the other kit-only files, so a new project does not inherit the kit's audit date; README "Files" lists it.

## Proposals for the owner (nothing changed yet)

| # | What | Where | Why it exists | Evidence | Saving | Risk | REC |
|---|---|---|---|---|---|---|---|
| P1 | Move the Project log detail (Type list, story fields, outline command) to the header of docs/LOG.md or a read-on-demand file; keep 2 lines in AGENTS.md | AGENTS.md "Project log" | Owner decisions 2026-11-11 and 2026-11-13 (log feeds a timeline and a deck) | 412 words read at every session start; log_check.py already enforces columns, Type values and Arcs fields | ~330 words, ~14% of AGENTS.md | An agent writes a row without reading the detail; log_check.py catches format, not story quality | Yes |
| P2 | Shorten the `.pii-guard` and denylist bullets to a pointer to README "Keep personal data out" and `pii_guard.py --status` | AGENTS.md "Personal data", lines 74–76 | Guard added 2026-11-11 (privacy-guard arc) | Same block list and denylist places in README and pii_guard.py docstring; pre-push and the Action enforce it | ~110 words | Low: the hook blocks regardless | Yes |
| P3 | Shorten the 2 enforcement bullets to one pointer ("enforced by scripts/git-hooks/pre-push and .claude/settings.json; README Files lists what each blocks") | AGENTS.md "Git safety" | Gap review 2026-11-13, gap 3 | README "Files" lists the same blocks; the hook enforces them | ~90 words | Low | Yes |
| P4 | Move the GitHub Actions minutes bullet from "Verification" to "Commands" (it is about CI triggers, not verification) | AGENTS.md line 90 | Owner decision 2026-11-11 | Wrong section: a reader looking for CI rules does not find it | 0 words; findability | None | Yes |
| P5 | New project reports "AUDIT DUE (never audited)" on day one | scripts/bloat_check.py `audit_due` | Design: the first audit creates the file | Trial first use (KIT_LOG row 28): fresh bootstrap prints AUDIT DUE at the first check-in, before any project code | One false alarm per new project | Changes a check: a project could go 14 days without an audit | Option A: count days and commits from the project's first commit when there is no `last_audit` (rec). Option B: keep as is |
| P6 | Make CLAUDE.md (`@AGENTS.md`) and GEMINI.md (`@./AGENTS.md`) use one import form | CLAUDE.md, GEMINI.md | not found | 2 forms for one job | 0 | Low; each host's docs accept its form (not tested here) | Keep as is unless tested on Gemini CLI |

Total if P1–P3 are approved: ~530 words, ~22% of AGENTS.md, ~700 start-read tokens per session.

## Findings with no action

- Duplicates (2): the Log header in KIT_LOG.md, docs/LOG.md and log_check.py is the template and its checker (intended). The env-var helper in the self-tests of first_use_check.py and pii_guard.py: each script is copied alone by sync_baseline.py, so a shared module would break standalone copies. Accepted as tech debt.
- Dead files: none. Every script is called by check.sh, a hook, sync_baseline.py or README. No file is older than 3 days.
- Broken relative links: 0 (README, docs/, .claude/, AGENTS.md).
- TODO or FIXME: 0.
- CI: one workflow, on `pull_request` and `workflow_dispatch` only.
- Kit-only files (PREFERENCES.md 16.6 KB, CHANGELOG.md 17.3 KB, KIT_LOG.md 11.7 KB) are not start-read and are deleted by bootstrap.

## Assumptions

| Assumption | Used in | Source | Confidence |
|---|---|---|---|
| A fresh clone bootstraps, checks and pushes with no error | docs/FIRST_USE.md | Trial 2026-11-13 (KIT_LOG row 28): bootstrap 1.3 s, check.sh 12/12 pass, push through pre-push and the guard pass | high |
| The settings.json deny list blocks force-push and hard reset | .claude/settings.json | Observed 2026-11-13: a command with `git push -f` and `git reset --hard` was denied in this session | high |
| Pre-push blocks force-push, delete main, unfetched remote | scripts/git-hooks/pre-push | `--test`, 9 cases pass | high |
| The sandbox runs and keeps the hooks path writable for session_checkin.sh | .claude/settings.json | Not tested: this container has no bubblewrap (gap review, Limits) | medium |
| Codex, Cursor and Copilot read AGENTS.md; Gemini CLI follows the GEMINI.md import | README, AGENTS.md header | Vendor docs, not tested here | medium |
| The human part of first use takes one dialog and 1–3 denylist places | docs/FIRST_USE.md | Trial ran the agent steps only; no person timed | medium |
| GitHub redirects the old account URL | this clone's `origin` (`[old handle]/archimedes_lever`) | GitHub keeps a redirect until someone takes the old name; then the URL points to their repo | low: question for the owner |

## Tech-debt register

| Item | Owner | Review date |
|---|---|---|
| Duplicate env-var helper in 2 self-tests | the owner | 2026-12-13 |
| Sandbox untested on a machine with bubblewrap | the owner | 2026-12-13 |
