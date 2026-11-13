# Decisions: archimedes_lever (kit)

The maintainer's own decisions (the owner, 2026-11-13). Public. The reason for each preference rule is in [PREFERENCES.md](../PREFERENCES.md#why-each-rule-exists). A new project does not get this file: bootstrap gives it the blank copy in docs/templates/DECISIONS.md. Rules in AGENTS.md give their reason inline, in brackets. Times are America/Chicago. Story behind each entry: [docs/LOG.md](LOG.md).

## Decisions

Newest first. "By" = the owner for a decision; "Agent" for a recommendation the owner has not approved yet.

| Date | Decision | By | Replaces |
|---|---|---|---|
| 2026-11-13 | Claude deletes remote branches whose work is already on main, stale ones included; a branch with unmerged work is kept and listed with a recommendation. | the owner | Deletion only of the branch just merged |
| 2026-11-13 | A fresh review covers the head commit that is merged; a fix made after a review gets its own review (AGENTS.md "Delegation"). | the owner | The reading that an earlier review covers later fixes (log #34) |
| 2026-11-13 | Question rule clarified: one dialog holds up to 4 questions, the rest go in Decide; Decide asks in the dialog when the tool exists. | the owner | — |
| 2026-11-13 | No rule-test run for the 2026-11-13 rule changes (PR 4 to PR 6). | the owner | — |
| 2026-11-13 | Merge without per-PR approval: a PR merges when its checks pass and a fresh review finds no MAJOR finding; the owner is asked only for UI changes, live or irreversible effects, or a MAJOR finding. Applies to the account Git rules and to the AGENTS.md no-tests exception. | the owner | Approval per PR (also in the row "Git rules split by repo"); a new commit needs a new approval |
| 2026-11-13 | Claude only: the kit, its templates and PREFERENCES.md name no other AI host; GEMINI.md and the ChatGPT, Codex and Gemini texts are removed. History rows in docs/LOG.md and docs/reviews/ keep their names. | the owner | Model-agnostic kit (log #4, #26) |
| 2026-11-13 | PREFERENCES.md is one block, synced to the owner's new account text; no modules, no Source line; "Production = …", large-query dry run, "Assume I am away", "no token counts" and the UI measuring line leave the preferences (the kit skills keep the data and UI steps). The reason table moves from this file to PREFERENCES.md. | the owner | Core + 4 modules (2026-11-13); the Source line |
| 2026-11-13 | Fewer limits on Claude: AUDIT DUE is reported and asked, never run unasked; rule tests run only for the changed rule, or all after a new model family; the project log takes story events only (decision, milestone, breakthrough, miss), never one row per change, because git log is the change log; worker branches use the host's required branch, else claude/<topic>. | the owner | Forced audit in session; rule tests after every rule change; a row per event; cc/ prefix |
| 2026-11-13 | De-duplication: AGENTS.md points to the owner's preferences for the question, summary and assumption formats, with a one-line fallback; README links to FILES.md, FIRST_USE.md and PREFERENCES.md instead of restating them; orchestration.md keeps Claude hosts only. | the owner | Restated text in AGENTS.md, README and orchestration.md |
| 2026-11-13 | The kit is the living, public source of the owner's rules: PREFERENCES.md is current, each rule has a reason below, the log is public, and the repo is the source for the account settings (change here first, then paste). New projects get blank DECISIONS.md and LOG.md with a link here. | the owner | The erased kit log (commit 44569f4); for the kit only, the AGENTS.md rule that a public repo keeps its log private |
| 2026-11-13 | Git rules split by repo: a repo with AGENTS.md follows its "Delivery"; other repos follow the Git rules in PREFERENCES.md (branch, PR, approval per PR). | the owner | The account Git rule that applied everywhere |
| 2026-11-13 | Procedures that only some tasks need live in kit skills (`.claude/skills/data-change`, `.claude/skills/ui-verify`), synced to projects. | the owner | The UI measuring detail in AGENTS.md "Verification" |
| 2026-11-13 | Preference fixes: "small turn" defined; each account copy names its source; save drafts at once, publish after the batch; approved work runs while the owner is away; confidence on claims the owner would act on; unnamed data targets count as production; dry run before large queries. | Agent (approved when the owner merges the PR that adds it) | 5 conflicting or vague rules (log #31) |
