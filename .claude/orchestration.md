# Orchestration: more than one agent

Read this file when you delegate work or run more than one agent. AGENTS.md "Delegation" points here. The owner's decisions (2026-11-10): the orchestrator stays on the strongest model; models are chosen per task with the routing table below. Model-agnostic since 2026-11-11 (the owner): routing names tiers, and each host maps the tiers to its own models.

## Agents (.claude/agents/)

| Agent | Model | Tools | Use |
|---|---|---|---|
| `scout` | haiku | Read, Grep, Glob | Searches, file lists, summaries of test or log output |
| `worker` | sonnet | Read, Edit, Write, Bash, Grep, Glob; guard hook | One brief-ready task on its own branch |
| `reviewer` | sonnet | Read, Grep, Glob, Bash; guard hook | Fresh review: diff and brief only |

`scripts/worker_guard.py` (PreToolUse hook) blocks push to main or master, every force-push form, rebase, reset --hard, clean and branch deletes for `worker`; with `--readonly` it also blocks every git verb that changes the repo, for `reviewer`. It is a seat belt for honest mistakes, not a security boundary: it cannot see file writes or commands built at run time.

## Model routing

Route by tier. Pass a model on the call only where this table says "strong" for a role whose default is lower.

| Work | Role | Tier |
|---|---|---|
| Search, file lists, summaries of test or log output | `scout` | fast |
| Task from a brief | `worker` | standard |
| Worker task that failed its checks 2 times, a refactor over 5+ files, a performance fix | `worker` | strong (model on the call) |
| Fresh review of a routine diff | `reviewer` | standard |
| Fresh review of data or save migrations, git or hook tools, security, or a refactor that must not change behavior | `reviewer` | strong (model on the call) |
| Merges, conflict choices, design, artifacts, deploys | orchestrator | strong |

Tiers by host. Model names change often: when a name here is gone, use the host's current model of that tier and update this table.

| Host | fast | standard | strong | Subagents | Hooks |
|---|---|---|---|---|---|
| Claude Code | haiku | sonnet | opus | `.claude/agents/` | Stop, PreToolUse, deny list, git |
| claude.ai chat | Haiku | Sonnet | Opus | Agent tool when offered | git only |
| Claude Code cloud sessions (claude.ai/code) | haiku | sonnet | opus | `.claude/agents/` | same as Claude Code (.claude/settings.json) |
| Codex (CLI, IDE, cloud) | the account's mini model | default model | highest reasoning setting | agent roles if the version has them | git only |
| Gemini CLI | Flash | Pro | Pro, high thinking | none assumed | git only |
| ChatGPT or any other chat | smaller model | default model | strongest model | none | none (no repo access: give text to paste) |

If the routed tier is not available (not offered, usage limit): for `scout` and `worker` work use the next lower tier and say so in the report; for `reviewer` and orchestrator work use the next higher tier, or wait; never review with a lower tier than the author used.

Log the model with each delegated task (in the handoff or the project's task log), so first-attempt pass rates can be compared by model.

## Fallbacks (hosts without a Claude Code feature)

| Feature | Fallback, in order |
|---|---|
| Subagent (`scout`, `worker`) | 1. The host's own subagent or agent role, with the brief below. 2. A new session or chat with only the brief; paste its result back. 3. Do the task yourself, one at a time. |
| Fresh `reviewer` | 1. A subagent with only the diff and the brief. 2. A new session with a different model or tier, given only the diff and the brief. 3. Review it yourself and label it "self-review", never "independent review". |
| `worker_guard.py` (PreToolUse) | Partial: `scripts/git-hooks/pre-push` blocks force-pushes and deleting main for every tool, but not a fast-forward push to main, rebase, reset --hard or clean. The brief forbids those; give each worker its own branch, and the orchestrator checks the branch (`git log origin/main..<branch>`, `git diff --stat`) before it merges. |
| Stop hook | Before the end of each turn: `echo '{}' \| python3 scripts/stop_check.py`; exit 2 = commit or push first. |
| Worktree isolation | A separate clone or `git worktree add ../<repo>-<topic> -b <branch>`. |
| claude.ai artifacts and docs | Repo files (Markdown, HTML) and links to them; say that the artifact step needs Claude. |
| Personal preferences | AGENTS.md "Reporting" gives the summary format; it is enough without them. |

Branch prefix per agent: `cc/` Claude worker, `gpt/` Codex or GPT, `gem/` Gemini, `agent/` any other. Log the host and model with each delegated task.

## When to delegate

- Size rule: AGENTS.md "Delegation". A subagent spends tokens loading its context before it starts, so do smaller tasks yourself.
- Keep for the orchestrator: merges, conflict choices, design and open decisions, artifacts, deploys, release versions.
- One worker at a time by default. Two only when their allowed files do not overlap. Start each worker in its own worktree (`isolation: "worktree"` in Claude Code; Fallbacks for other hosts).

## Brief (put it in the Agent prompt)

- Goal and why, with the doc sections it implements.
- Branch name (`cc/<topic>`) and base commit.
- Allowed files: name every file it may touch.
- Done criteria that can be measured (numbers, test names, PASS lines).
- Checks to run.
- "No design decisions: list candidates with trade-offs."
- The tier (and the host's model name), when the routing table says strong.

## Review and merge

1. Scope: `git diff --stat origin/main...origin/<branch>`. Flag files outside the brief.
2. Update by merge, never rebase: `git checkout -B review/<branch> origin/<branch> && git merge origin/main`. When intents conflict, stop and list the choice for the owner.
3. Fresh review: `reviewer` with only the diff and the brief. Verify each finding before you report it.
4. Checks: the commands in AGENTS.md "Commands". Report before and after numbers.
5. Merge: `git checkout main && git merge --no-ff review/<branch>`, confirm `git merge-base --is-ancestor origin/main HEAD`, push, verify origin/main. UI or design changes the owner has not approved wait for the owner's yes (AGENTS.md "Delivery").

## Lanes (fill in per project, in AGENTS.md "Project rules")

| Lane | Owner | Files | May push to |
|---|---|---|---|
| Orchestrator | strongest available model (default: Claude Opus) | Everything not in another lane | main |
| Worker | `worker` subagent | Only its brief's files | its own `cc/<topic>` branch |
| GPT / Codex (if used) | Codex | Per brief | its own `gpt/<topic>` branch |
| Gemini or another agent (if used) | that agent | Per brief | its own `gem/<topic>` or `agent/<topic>` branch |
