# Agentic-practice gap review (2026-11-13)

Question from the maintainer: what industry-standard agentic practice is missing from this kit, per Andrej Karpathy, Anthropic and AI researchers, using only sources dated 2026-08-01 or later (window widened from 2026-09-01 by the maintainer, 2026-11-13).

Method: web search (2026-11-13), then direct reads of anthropic.com/engineering, claude.com/blog and the arXiv abstract pages (arxiv.org was added to the environment allowlist for this). Numbers below are from the abstracts, not the full papers. Repo coverage: `git grep -il` for each topic on commit d38ce06.

## Sources in the window

| ID | Source | Date | Read directly |
|---|---|---|---|
| A1 | Anthropic, "The components of agent memory" (anthropic.com/research/components-of-agent-memory) | 2026-11-06 | yes |
| A2 | Anthropic, "Redesigning source control at Anthropic" (anthropic.com/research/redesigning-source-control) | 2026-10-13 | yes |
| A3 | Anthropic, "Operate Claude Managed Agents inside your security perimeter" (claude.com/resources/articles/self-hosted-claude-managed-agents) | 2026-11-12 | yes |
| A4 | Anthropic customer story, JPMorganChase and Claude Code (claude.com/resources/articles/jpmorganchase-expands-claude-code) | 2026-11-09 | yes |
| R1 | arXiv 2610.09264, PackHallu: prompt injection in coding rule files | 2026-10-07 | abstract |
| R2 | arXiv 2610.20776, INFUSE: indirect prompt injection benchmark (40 tasks, 19 LLMs) | 2026-10-14 | abstract |
| R3 | arXiv 2610.38867, "Where You Inject Matters" | 2026-10-28 | abstract |
| R4 | arXiv 2610.03448, re-evaluating prompt-injection detectors | 2026-10-02 | abstract |
| R5 | arXiv 2610.04838, MemTrace: file/symbol/test-anchored memory | 2026-10-04 | abstract |
| R6 | arXiv 2608.25817, SkillShield: security skills in the system prompt | 2026-08-26 | abstract |
| R7 | arXiv 2608.13867, "Engineering Reliable Coding Agents" (monograph, 164 papers reviewed) | 2026-08-14 | abstract |
| R8 | arXiv 2608.11386, "The Devil Is in the Interface": tool architecture, 11,700 trajectories | 2026-08-11 | abstract |

Karpathy: no primary statement dated 2026-08-01 or later was found. karpathy.bearblog.dev returns HTTP 404 on every page (2026-11-13); x.com needs a login. The only in-window item is a secondary profile (startuphub.ai, 2026-08-16) that restates his April 2026 talk, so it is not used.

## Gaps, ranked

| # | Gap | Evidence | Repo today | Confidence |
|---|---|---|---|---|
| 1 | No rule that repo text, tool output and fetched pages are untrusted data, not instructions; no review gate on instruction-file changes | R1: malicious text in rule files steers agents; detectors miss it. R3: injections in README/TODO files followed 2.6x more than in code. R2: prompt-level hardening cut mean attack success 58.2% to 14.3%; guard models gave limited protection. R4: best BIPIA detector caught 2% of AgentDojo injections at 1% false positives. R6: one security skill in the system prompt cut malware-generation severity 3.37 to 0.58. | `untrusted`, `injection`: 0 hits. A kit that is copied into every project is a rule-file supply chain. | high |
| 2 | No sandbox / egress / credential-isolation baseline | R7: many apparent model failures come from the harness, permissions and environment. A3: allowlist egress (for example only the git host and package registry); credentials injected by a proxy outside the sandbox; full audit trail. A4: containerized runs, no direct access to credentials. | settings.json denies `.env` reads and destructive git only. `sandbox`: 0 hits. | high |
| 3 | No gate the agent cannot pass by itself; Build/Test/Lint are "not set yet" by default | A4: an automated gate returns pass or halt, "so Claude can't sign off on its own work". A2: invest in post-merge and pre-deploy automated tests; human review checks intent, not every line. | Stop hook checks git state, not tests. `check.sh` is not enforced at Stop or pre-push. Reviewer subagent exists. | high |
| 4 | No audit trail of agent sessions | A3: every session record exports over OpenTelemetry. | `telemetry`, `transcript`: 0 hits. LOG.md is a narrative, not an audit trail. | medium (more useful for teams than solo) |
| 5 | Instruction length and style not tested against adherence | A1: "longer instruction files reduce adherence"; the top memory layer must stay small; for stronger models, judgment beat fixed rules (a "record only failures" rule cut the gain). | AGENTS.md ~3,366 start-read tokens against a 12,000 budget; mostly fixed rules. No eval of whether a rule changes behavior. | medium |
| 6 | Shared append tables lose facts under parallel writes | A1: shared table kept 41 of 57 facts; one page per item kept 57 of 57. | DECISIONS.md and LOG.md are single tables. Git surfaces textual conflicts, so the loss risk is lower than in A1. | low-medium |
| 7 | Memory anchored to code locations | R5: traces anchored to files, symbols and tests improved long-horizon pass rates. | Not present. Research stage; no file convention to copy yet. | low |

## Considered, not a gap

- R8: structured or CodeAct-style tools change agent behavior (up to 4.7x more consistent; 41.6% fewer steps). This is a host and tool choice, not a repo-kit setting.
- arXiv 2608.19263 (Evaluation Context Protocol): early-stage, no validation yet.

## Built (2026-11-13, branch claude/gallant-cray-qkt6hy)

- Gap 1: AGENTS.md "Untrusted input" section; reviewer flags instruction-file changes, new dependencies and injected text.
- Gap 2: .claude/settings.json sandbox on, network allowlist (GitHub, PyPI, npm), deny reads of key files; sync_baseline.py adds the sandbox block to projects that have none.
- Gap 3: pre-push runs scripts/check.sh and blocks on failure (delete-only pushes skip it).

## Already covered (no action)

Handoff file with a size cap; dated decision record; separate reviewer with diff-only brief; pre-push block on force-push; Stop hook; personal-data and secret guard; model routing; bloat budget and audit.

## Limits

- arXiv numbers come from abstracts, not full papers.
- The sandbox write-protects git config and hooks, so `scripts/session_checkin.sh` (it sets core.hooksPath) is in `sandbox.excludedCommands`; not yet tested on a machine where the sandbox runs (medium confidence).
- Bash `cat` of a key file is blocked only when the sandbox runs; the Read deny rules cover the Read tool only.
- The sandbox does not start where bubblewrap and socat are missing (this cloud container); Claude Code then warns and runs commands unsandboxed.
- claude.com/blog: only the first page (11 of 318 items) was read.
- The date filter removes the most cited earlier sources (ETH AGENTS.md study, Feb 2026; Anthropic evals guide, Jan 2026; Karpathy, Mar-Apr 2026).
