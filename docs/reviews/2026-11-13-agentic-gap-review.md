# Agentic-practice gap review (2026-11-13)

Question from the maintainer: what industry-standard agentic practice is missing from this kit, per Andrej Karpathy, Anthropic and AI researchers, using only sources dated 2026-09-01 or later.

Method: web search (2026-11-13), then direct reads of anthropic.com/engineering and claude.com/blog. arxiv.org and karpathy.bearblog.dev were not reachable from the session network, so the arXiv items below come from search-engine abstracts, not from the papers. Repo coverage: `git grep -il` for each topic on commit d38ce06.

## Sources in the window

| ID | Source | Date | Read directly |
|---|---|---|---|
| A1 | Anthropic, "The components of agent memory" (anthropic.com/research/components-of-agent-memory) | 2026-11-06 | yes |
| A2 | Anthropic, "Redesigning source control at Anthropic" (anthropic.com/research/redesigning-source-control) | 2026-10-13 | yes |
| A3 | Anthropic, "Operate Claude Managed Agents inside your security perimeter" (claude.com/resources/articles/self-hosted-claude-managed-agents) | 2026-11-12 | yes |
| A4 | Anthropic customer story, JPMorganChase and Claude Code (claude.com/resources/articles/jpmorganchase-expands-claude-code) | 2026-11-09 | yes |
| R1 | arXiv 2610.09264, PackHallu: prompt injection in coding rule files | 2026-10 | abstract via search |
| R2 | arXiv 2610.20776, INFUSE: indirect prompt injection benchmark for terminal agents | 2026-10 | abstract via search |
| R3 | arXiv 2610.38867, "Where You Inject Matters" | 2026-10 | abstract via search |
| R4 | arXiv 2610.03448, re-evaluating prompt-injection detectors | 2026-10 | abstract via search |
| R5 | arXiv 2610.04838, MemTrace: file/symbol/test-anchored memory | 2026-10 | abstract via search |

Karpathy: no primary statement dated 2026-09-01 or later was found. His agentic-engineering talk (April 2026) and autoresearch (March 2026) are outside the window and are not used.

## Gaps, ranked

| # | Gap | Evidence | Repo today | Confidence |
|---|---|---|---|---|
| 1 | No rule that repo text, tool output and fetched pages are untrusted data, not instructions; no review gate on instruction-file changes | R1: malicious text in rule files steers agents; detectors miss it. R3: injections in README/TODO files followed 2.6x more than in code. R2: prompt-level hardening cut attack success 58.2% to 14.3%. R4: detectors overstate accuracy. | `untrusted`, `injection`: 0 hits. A kit that is copied into every project is a rule-file supply chain. | high on the risk, medium on the numbers |
| 2 | No sandbox / egress / credential-isolation baseline | A3: allowlist egress (for example only the git host and package registry); credentials injected by a proxy outside the sandbox; full audit trail. A4: containerized runs, no direct access to credentials. | settings.json denies `.env` reads and destructive git only. `sandbox`: 0 hits. | high |
| 3 | No gate the agent cannot pass by itself; Build/Test/Lint are "not set yet" by default | A4: an automated gate returns pass or halt, "so Claude can't sign off on its own work". A2: invest in post-merge and pre-deploy automated tests; human review checks intent, not every line. | Stop hook checks git state, not tests. `check.sh` is not enforced at Stop or pre-push. Reviewer subagent exists. | high |
| 4 | No audit trail of agent sessions | A3: every session record exports over OpenTelemetry. | `telemetry`, `transcript`: 0 hits. LOG.md is a narrative, not an audit trail. | medium (more useful for teams than solo) |
| 5 | Instruction length and style not tested against adherence | A1: "longer instruction files reduce adherence"; the top memory layer must stay small; for stronger models, judgment beat fixed rules (a "record only failures" rule cut the gain). | AGENTS.md ~3,366 start-read tokens against a 12,000 budget; mostly fixed rules. No eval of whether a rule changes behavior. | medium |
| 6 | Shared append tables lose facts under parallel writes | A1: shared table kept 41 of 57 facts; one page per item kept 57 of 57. | DECISIONS.md and LOG.md are single tables. Git surfaces textual conflicts, so the loss risk is lower than in A1. | low-medium |
| 7 | Memory anchored to code locations | R5: traces anchored to files, symbols and tests improved long-horizon pass rates. | Not present. Research stage; no file convention to copy yet. | low |

## Already covered (no action)

Handoff file with a size cap; dated decision record; separate reviewer with diff-only brief; pre-push block on force-push; Stop hook; personal-data and secret guard; model routing; bloat budget and audit.

## Limits

- arXiv numbers are not verified against the papers (network block on arxiv.org).
- claude.com/blog: only the first page (11 of 318 items) was read.
- The date filter removes the most cited earlier sources (ETH AGENTS.md study, Feb 2026; Anthropic evals guide, Jan 2026; Karpathy, Mar-Apr 2026).
