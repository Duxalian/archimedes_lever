# {{PROJECT_NAME}}: agent instructions

This file is the source of truth for every agent on this repo: Claude, GPT/Codex, Gemini, any other model, and sub-agents. Codex, Copilot, Cursor and most other tools read AGENTS.md directly; CLAUDE.md (Claude Code) and GEMINI.md (Gemini CLI) import it. If your tool reads none of these, read this file first. Where a rule names a Claude-only feature, use the fallback in `.claude/orchestration.md` "Fallbacks". Put rules specific to this project in "Project rules" at the end. "Owner" is the name agents use for the person who decides; a public repo uses a role (for example "the maintainer") instead of a real name.

- Repo: {{REPO}}
- Purpose: {{PURPOSE}}
- Owner: {{OWNER}}

## Order of authority

1. The owner's current request.
2. The owner's decisions in docs/DECISIONS.md. A newer decision overrides older text.
3. This file.
4. The owner's personal preferences for the host you run in (Claude, GPT and Codex have copies; other hosts may have none).
5. docs/NEXT_PROMPT.md (the handoff).

Chat history, Project files and remembered copies are not authority. If you cannot read this repo, say so and stop.

## Start of session

- Run `scripts/session_checkin.sh`. Report the branch, uncommitted files, and the ahead/behind count against origin/main.
- Read docs/NEXT_PROMPT.md and docs/DECISIONS.md.
- Find the tools you have and read the environment docs before you say a capability is not available.

## Authority

- Make routine decisions yourself.
- Ask the owner only about: source authority, content approval, irreversible effects, costs, and security or privacy risk.
- When you ask: give 2–3 options with trade-offs, mark one as your recommendation, and ask all open questions together.
- Your recommendation is not a decision until the owner approves it.

## Delivery

- Deliver every change without being asked: commit, merge to main, push, verify that origin/main has the commit, and republish the affected artifacts.
- Exception: for a UI or design change that the owner has not approved, show a preview first (a preview artifact or a branch). Merge after the owner approves. Delete previews after they ship.
- For changes that are not UI or design, this rule overrides the personal "preview first" rule.
- If a step is blocked, name the step and the cause. If permissions block a step, give the exact commands to paste, one code block for each command.
- Put every deliverable where it survives (repo, doc, artifact) as soon as it exists.

## Reporting

- Report actual checks, counts and limits.
- Keep these states separate: done, published, verified; self-review and independent review; delivery state and checkout state.
- Give full clickable links to files on main, to artifacts and to pull requests. Never give a bare path.
- Give text that the owner must paste in full, in a code block. Never tell the owner to find it in git.
- End each work turn with a summary: Decide (lettered options, your recommendation marked **Rec:**), Copy (full text for the owner to paste), then a table with Step (X of Y), Status (done / published / verified), Risks, Running, Not running, Next step (one recommendation), Links. Leave out empty rows, except Step. An agent that has the owner's personal preferences follows them for the exact format.

## Git safety

- Never force-push, rewrite published history, reset, clean, stash or discard work to make the state look synchronized. Update branches by merge.
- Pull just before you edit a shared doc. Use small edits. Never rewrite a whole file from an old copy.
- Never commit secrets, tokens or credentials.
- Enforcement for every agent: `scripts/git-hooks/pre-push` blocks force-pushes, pushes that are not a fast-forward, and deleting main. `scripts/session_checkin.sh` installs it (core.hooksPath). Never push with `--no-verify`.
- Claude Code also has .claude/settings.json: a deny list, and a Stop hook (scripts/stop_check.py) that blocks the end of a turn while work is uncommitted or unpushed. Agents without a Stop hook run `echo '{}' | python3 scripts/stop_check.py` before they end a turn and fix what it reports (exit 2 = not done).
- Do not weaken a hook or its settings to get past a block: ask the owner.

## Personal data

- Never commit personal data: real names, email addresses, phone numbers, home or work addresses, ID numbers, or the owner's job details. Use a role (for example "the maintainer") and fake sample data. A private repo may put its owner's real name in the `- Owner:` line (or pass `sync_baseline.py --owner`).
- Commit with a GitHub noreply address (`ID+USER@users.noreply.github.com`) or the agent's own noreply identity, never a personal email.
- A repo with a `.pii-guard` file at its root runs `scripts/pii_guard.py` in the pre-push hook and in the pull-request Action (.github/workflows/pii-guard.yml). It blocks emails, phone numbers, .mil addresses, ID-number shapes, and names from a denylist kept outside the repo (`~/.config/pii-guard/denylist.txt`, and the Actions secret `PII_GUARD_DENYLIST`). Never commit the denylist.
- When the guard blocks: remove the data, fix the unpushed commit, and push again. Only the owner adds allow entries to `.pii-guard`. Never push with `--no-verify`.

## Commands

<!-- Fill in when the project has them. Give exact commands. -->
- Build: not set yet.
- Test: not set yet.
- Lint: not set yet.

## Verification

- Before you report "verified", run the checks in Commands and report the results.
- For UI work, verify by measuring, not by looking: screenshots at 375 px and 1440 px width, light and dark, measured spacing, and contrast against WCAG AA (4.5:1 text, 3:1 large text and UI parts). Report the numbers.

- GitHub Actions (the owner, 2026-11-11): private repos share 2,000 Actions minutes a month. Trigger workflows on `pull_request` and `workflow_dispatch` only, never on `push`. Agents run the checks in Commands in their own workspace before they report; CI is a second check, not the first. Public repos run Actions free.

## Checks

- Never repin an approval, add an exemption, skip a test or edit a generated report to make a check pass.
- Never hand-edit generated files. Change the source and rebuild.

## Decisions

- Record each decision by the owner, with its date, in docs/DECISIONS.md or its canonical document.
- Mark agent recommendations as recommendations, not as the owner's decisions.
- Do not silently change approved decisions or sources. Raise open items with options. Never invent values.

## Handoff

- The current request overrides an older handoff.
- Keep status in repo files, never only in chat.
- Keep docs/NEXT_PROMPT.md short (40 lines or fewer). Put detailed evidence in docs/reviews/.

## Project log

The project log feeds a timeline of milestones, breakthroughs and narratives for readers outside the project (the owner, 2026-11-11). Decisions alone go in docs/DECISIONS.md; the log records how the project got there.

- Location: docs/LOG.md, unless "Project rules" names another place. Check it with `python3 scripts/log_check.py`. A public repo must name a private place (for example a private Claude doc), because entries can hold environment or security detail.
- Append an entry in the same turn the event happens. Backfill the same turn if you missed one.
- One row per event. Columns, in this order: # | When (CT) | Type | Arc | Topic | Raised by | What the other missed | Evidence | Result.
- When: `YYYY-MM-DD HH:MM` in America/Chicago. A range: `YYYY-MM-DD HH:MM–HH:MM`. Mark an estimate with `~` before the date or the time.
- Type, one of:
  - `milestone`: a deliverable exists or a goal is met (first import works, v1 published).
  - `breakthrough`: a test or idea removes a blocker or changes direction.
  - `miss`: a wrong assumption, failed test or dead end. Record it honestly for both sides.
  - `decision`: the owner decides, or overrules a recommendation. Also record it in docs/DECISIONS.md.
- Arc: a short kebab-case name for the narrative thread (for example `email-delivery`). Each arc has one row in the Arcs table: Arc | Span | Summary (one sentence) | Outcome.
- Raised by: who first said it (the owner, Claude, a named agent or person). "What the other missed": the gap on the other side, or `-`.
- Evidence: a commit, file, test or measurement. Never chat text alone.
- If you cannot write to the log (no tool for it), put the full entry in your turn summary under Copy, with "Paste into: project log".

## Delegation

- When you delegate or run more than one agent, read `.claude/orchestration.md` first: agents (`scout`, `worker`, `reviewer`), model routing, briefs, review and merge, lanes.
- Delegate only substantial independent work (about 30 minutes or more) with bounded files and measurable done criteria. Give parallel agents disjoint files.
- Ask for concise findings with evidence paths.
- Before a merge of changes to code, checks or scripts, a fresh reviewer gets only the diff and the brief, not the author's conclusions: the `reviewer` subagent where the host has subagents, else the next step in `.claude/orchestration.md` "Fallbacks" (model tier per that file). Docs-only changes skip this review.
- Check delegated output (diff, touched files, no approval or exemption changes) before you report it as done.

## Unattended work

- Work the owner expects done while away needs a running owner before the turn ends: a started agent or a one-time scheduled task.
- A scheduled task needs a prompt that stands alone and permission to commit, push to main and republish without a person.
- Background work stops at the usage limit. Say when that can interrupt it.

## Boundaries

- Do not change account-wide settings, plugins or skills as a side effect of project work.

## Project rules

<!-- Add rules for this project below. Date each decision by the owner, for example "(the owner, 2026-11-09)". -->
