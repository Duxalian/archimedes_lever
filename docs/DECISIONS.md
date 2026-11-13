# Decisions: archimedes_lever (kit)

The maintainer's own decisions and the reason for each rule in [PREFERENCES.md](../PREFERENCES.md) (the owner, 2026-11-13). Public. A new project does not get this file: bootstrap gives it the blank copy in docs/templates/DECISIONS.md. Rules in AGENTS.md give their reason inline, in brackets. Times are America/Chicago. Story behind each entry: [docs/LOG.md](LOG.md).

## Decisions

Newest first. "By" = the owner for a decision; "Agent" for a recommendation the owner has not approved yet.

| Date | Decision | By | Replaces |
|---|---|---|---|
| 2026-11-13 | The kit is the living, public source of the owner's rules: PREFERENCES.md is current, each rule has a reason below, the log is public, and the repo is the source for the account settings (change here first, then paste). New projects get blank DECISIONS.md and LOG.md with a link here. | the owner | The erased kit log (commit 44569f4); for the kit only, the AGENTS.md rule that a public repo keeps its log private |
| 2026-11-13 | Git rules split by repo: a repo with AGENTS.md follows its "Delivery"; other repos follow the Git module (branch, PR, approval per PR). | the owner | The account Git rule that applied everywhere |
| 2026-11-13 | Procedures that only some tasks need live in kit skills (`.claude/skills/data-change`, `.claude/skills/ui-verify`), synced to projects. | the owner | The UI measuring detail in AGENTS.md "Verification" |
| 2026-11-13 | Preference fixes: one place for questions (dialog, else Decide); "small turn" defined; save drafts at once, publish after the batch; approved work runs while the owner is away; confidence on claims the owner would act on; unnamed data targets count as production; dry run before large queries. | Agent (approved when the owner merges the PR that adds it) | 5 conflicting or vague rules (log #31) |

## Why each preference rule exists

"Reason by": a README lesson or log row is a sourced reason; "Agent draft" waits for the owner's approval. Rule names follow the PREFERENCES.md headings.

| Rule | Why | Reason by |
|---|---|---|
| Style: expert level in my field, plain terms elsewhere | Skips basics the owner knows; keeps other fields readable. | Agent draft |
| Style: show times in my time zone | Times compare without conversion, in chat and in logs. | Agent draft |
| Style: my current message overrides; follow a rule's intent if it gives an absurd result | No rule set foresees every case; a literal result that hurts is worse than a stated exception. | Agent draft |
| Style: STE, concise, numbers, answer first | Short sentences with one meaning per word are faster to scan and harder to misread. | Agent draft |
| Style: be critical; hold position under pushback | An agent that gives way to pressure, not to evidence, hides its own errors. | Agent draft |
| Style: confidence marks and cited sources | The owner can tell what to check before acting on it. | Agent draft |
| Style: state key assumptions before 3+ steps | A design review found 34 decisions that the agent had assumed, not asked. | README lesson |
| Decisions: REC vs DECIDED labels | Keeps a proposal apart from an approval, so nothing ships on a recommendation alone; "REC" and "Rec" had both been in use. | log #22 |
| Decisions: ask all questions at the start, in the dialog | 34 assumed decisions (README lesson); the dialog was skipped for 2 turns when the wording allowed a list instead (log #23). | README lesson, log #23 |
| Least effort: count clicks, copies, pastes, typing | A solution assumed copy and paste where the person had to type by hand; "least effort" became countable rules. | README lesson, log #22 |
| Changes: make the change in a preview; ship after approval | The owner reviews a working result, not a description of one. | Agent draft |
| Changes: ask which place when a thing exists in more than one | A change to the wrong copy (live, preview, repo) is a silent miss. | Agent draft |
| Changes: out-of-scope findings | Small, verifiable fixes go in; anything larger needs a decision, so scope does not creep. | log #24 |
| Changes: fix the cause everywhere; one meaning per colour or label | A fix in one place leaves the same fault elsewhere. | Agent draft |
| Changes: save drafts at once; batch, then publish | Chats end and containers are reclaimed; each publish costs the owner a review. | Agent draft |
| Changes: one place per fact | 3 conflicting rules made agent behaviour look random. | README lesson, log #22 |
| Reporting: done, published, verified; self-review is not independent review | A self-review checked that 39 notes existed; 30 of them said the opposite of the source. | README lesson |
| Reporting: if blocked, name the step, the cause and the unblock | Agents guessed when a host blocked a step that AGENTS.md required. | log #27 |
| Where to save: one home per kind of file; Drive under "Claude Projects/" | Files are found in one known place; nothing lands in the Drive root. | Agent draft |
| End-of-turn summary | Decisions and paste text are in the same place every turn; the resume prompt carries state to a new chat, which cannot see this one. | Agent draft |
| Builder: no setup, defaults, keyboard, all states, accessibility | Part of "Design for human limits": every click and unclear state costs the person effort. | log #24 |
| Builder: measure UI at 375 and 1440 px, light and dark, WCAG AA | A layout shifted 14 px and no check noticed. | README lesson |
| Data: dry run, counts and approval before a write | A data write can be irreversible; counts before and after prove what changed. | log #24 |
| Data: no raw personal data; mask or aggregate | Personal data that leaves its system cannot be called back. | log #24 |
| Data: the query and the as-of time for each number | A number without its source cannot be checked or rerun. | log #24 |
| Data: unnamed targets count as production; dry run before large queries | Guessing the environment from a name is unsafe; a large scan costs money before anyone sees it. | Agent draft |
| Agent work: "away", safe steps, a running owner | Work expected to finish while the owner is away must not depend on a chat staying open. | log #24 |
| Agent work: models, agent count and hours before heavy work; no token counts | A usage status line and hook was a dead end; the owner estimates usage from these 3 numbers. | log #25 |
| Agent work: fresh review for 100+ lines, data writes or anything going live | A fresh context finds what self-review misses. | README lesson |
| Agent work: parallel only on disjoint files | Parallel edits to one file conflict at merge. | Agent draft |
| Git: branch, PR, approval per PR, checks pass, no force-push | A rule said "never force-push" and only one tool obeyed it; a commit reached main with a failing check. Enable branch protection where possible: a written rule is not a control. | README lesson |
