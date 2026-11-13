# Bloat, drift and assumption audit: the kit (2026-11-13)

First full audit of the kit (`.claude/bloat-audit.md`), asked for by the owner on 2026-11-13. Audited commit: 6f5f4f1. Machine: cloud container, 4 vCPU Intel Xeon 2.10 GHz. Removals are proposals only (the owner, 2026-11-13); nothing was removed.

## Before and after

| Measure | Before | After | Budget |
|---|---|---|---|
| Start read (~tokens) | 3,740 | 3,799 (+59: host-limit rule in AGENTS.md "Delivery") | 12,000 (warn 6,000) |
| AGENTS.md words | 2,342 | 2,387 (+45) | - |
| Duplicate lines (80+ chars, 2+ files) | 2 | 2 | 20 |
| Tracked files / size | 37 / 246 KB | 39 / 255 KB (this report, `.bloat-audit.json`) | - |
| Big files | 0 | 0 | 500 KB |
| Timing: `check` (scripts/check.sh) | 2.9 s (baseline, first record) | 3.0 s | +25% |
| Timing: `checkin` (scripts/session_checkin.sh) | 0.9 s (baseline, first record) | 1.1 s (+22%, in limit) | +25% |
| Timing: `bloat-brief` | 0.1 s (baseline, first record) | 0.1 s | +25% |
| Removals proposed / approved / made | - | 6 / 5 / 5 (P1–P5, the owner, 2026-11-13) | - |
| Rules removed or merged | - | 0 (1 added, owner request) | - |
| Key assumptions: high / medium / low / untraced | - | 3 / 3 / 1 / 0 | - |

Commands: `python3 scripts/bloat_check.py --time --record` (before), `--time` (after); `git show 6f5f4f1:AGENTS.md | wc -w`; `git ls-tree -r -l 6f5f4f1` and `git ls-files | xargs cat | wc -c` for sizes. Section words exclude the heading line. Numbers corrected after the fresh review (wc ran after the AGENTS.md edit).

## AGENTS.md cost by section (words)

| Section | Words | Note |
|---|---|---|
| Project log | 412 | 17% of the file; needed only when a log row is written |
| Bloat, drift and assumptions | 212 | |
| Personal data | 211 | half restates README "Keep personal data out" and pii_guard.py |
| Delivery | 118 → 163 | host-limit rule added |
| Git safety | 160 | 2 bullets describe what pre-push and settings.json enforce |
| Others (14 sections) | 1,229 | |

## After the owner approved P1–P5 (2026-11-13)

| Measure | After the audit | After P1–P5 |
|---|---|---|
| Start read (~tokens) | 3,799 | 3,256 (−543, −14%) |
| AGENTS.md words / bytes | 2,387 / 15,197 start read | 2,024 (−363, −15%) / 12,370 |
| Tracked files / size | 39 / 255 KB | 40 / 257 KB (+ .claude/project-log.md) |
| Timing: check / checkin / bloat-brief (s) | 2.9 / 0.9 / 0.1 | 3.2 / 0.6 / 0.1 (all within +25%) |

- P1: the detail moved to `.claude/project-log.md`, not to docs/LOG.md: sync_baseline.py keeps a project's docs/, so existing projects would not get it. sync_baseline.py and bootstrap.sh copy and rename it.
- P2, P3: pointers go to the file headers of `scripts/pii_guard.py` and the enforcing files, not to README: bootstrap replaces README in projects.
- P4: the rule moved to "Checks", not "Commands": sync_baseline.py keeps a project's own Commands section, so the rule would not reach existing projects.
- P5: `audit_due` counts from the first commit when there is no `last_audit`; a shallow clone stays due (its oldest commit is a cut); 5 new self-test cases.
- Found on the way: bootstrap.sh did not rename the owner in `.claude/bloat-audit.md` and `scripts/bloat_check.py`, which sync_baseline.py renames, so the first sync after a bootstrap with an owner name changed them. Fixed; a bootstrap with owner "Sam" followed by a sync now changes only `.baseline`.
- Verified: kit check.sh 11 pass, 1 skip; new trial project (owner "Sam") check.sh 11 of 11, audit not due on day one; a project made from 6f5f4f1 and synced with `--apply` gets `.claude/project-log.md` and passes check.sh 11 of 11.

## Fixes made (exceptions list only)

1. `.bloat-audit.json` created (exception a): audit state and 3 timing baselines. `scripts/bootstrap.sh` deletes it with the other kit-only files, so a new project does not inherit the kit's audit date; README "Files" lists it.

## Proposals for the owner (nothing changed yet)

| # | What | Where | Why it exists | Evidence | Saving | Risk | REC |
|---|---|---|---|---|---|---|---|
| P1 | Move the Project log detail (Type list, story fields, outline command) to the header of docs/LOG.md or a read-on-demand file; keep 2 lines in AGENTS.md | AGENTS.md "Project log" | Owner decisions 2026-11-11 and 2026-11-13 (log feeds a timeline and a deck) | 412 words read at every session start; log_check.py already enforces columns, Type values and Arcs fields | ~330 words, ~14% of AGENTS.md | An agent writes a row without reading the detail; log_check.py catches format, not story quality | Yes |
| P2 | Shorten the `.pii-guard` and denylist bullets to a pointer to README "Keep personal data out" and `pii_guard.py --status` | AGENTS.md "Personal data", lines 74–76 | Guard added 2026-11-11 (privacy-guard arc) | Same block list and denylist places in README and pii_guard.py docstring; pre-push and the Action enforce it | ~110 words | Low: the hook blocks regardless | Yes |
| P3 | Shorten the 2 enforcement bullets to one pointer ("enforced by scripts/git-hooks/pre-push and .claude/settings.json; README Files lists what each blocks") | AGENTS.md "Git safety" | Gap review 2026-11-13, gap 3 | README "Files" lists the same blocks; the hook enforces them | ~90 words | Low | Yes |
| P4 | Move the GitHub Actions minutes bullet from "Verification" to "Commands" (it is about CI triggers, not verification) | AGENTS.md line 90 | Owner decision 2026-11-11 | Wrong section: a reader looking for CI rules does not find it | 0 words; findability | None | Yes |
| P5 | New project reports "AUDIT DUE (never audited)" on day one | scripts/bloat_check.py `audit_due` | Design: the first audit creates the file | Trial first use (trial run 2026-11-13; KIT_LOG.md, now in git history only): fresh bootstrap prints AUDIT DUE at the first check-in, before any project code | One false alarm per new project | Changes a check: a project could go 14 days without an audit | Option A: count days and commits from the project's first commit when there is no `last_audit` (rec). Option B: keep as is |
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
| A fresh clone bootstraps, checks and pushes with no error | docs/FIRST_USE.md | Trial 2026-11-13 (trial run 2026-11-13; KIT_LOG.md, now in git history only): bootstrap 1.3 s, check.sh 12/12 pass, push through pre-push and the guard pass | high |
| The settings.json deny list blocks force-push and hard reset | .claude/settings.json | Observed 2026-11-13: a command with `git push -f` and `git reset --hard` was denied in this session | high |
| Pre-push blocks force-push, delete main, unfetched remote | scripts/git-hooks/pre-push | `--test`, 9 cases pass | high |
| The sandbox runs and keeps the hooks path writable for session_checkin.sh | .claude/settings.json | Not tested: this container has no bubblewrap (gap review, Limits) | medium |
| Codex, Cursor and Copilot read AGENTS.md; Gemini CLI follows the GEMINI.md import | README, AGENTS.md header | Vendor docs, not tested here | medium |
| The human part of first use takes one dialog and 1–3 denylist places | docs/FIRST_USE.md | Trial ran the agent steps only; no person timed | medium |
| GitHub redirects the old account URL | this clone's `origin` (`Duxalian/archimedes_lever`) | GitHub keeps a redirect until someone takes the old name; then the URL points to their repo | low: question for the owner |

## Tech-debt register

| Item | Owner | Review date |
|---|---|---|
| Duplicate env-var helper in 2 self-tests | the owner | 2026-12-13 |
| Sandbox untested on a machine with bubblewrap | the owner | 2026-12-13 |

## Fresh reviews

- Audit commit (eab8b98): 0 MAJOR, 5 MINOR (wrong before/after numbers, last_audit commit, no after-timings), 2 NIT. All 5 MINOR fixed in abf8055.
- P1–P5 (abf8055..7a307b7): 0 MAJOR, 3 MINOR, 2 NIT. Fixed: the settings.json pointer wording; a shallow clone is now due (it understated the age). No change: a project cloned with the kit's full history counts from the kit's first commit, but docs/FIRST_USE.md step 2 and "Use this template" both start a fresh one-commit history.
