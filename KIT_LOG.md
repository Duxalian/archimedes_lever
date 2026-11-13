# Project log: archimedes_lever (kit)

Source for a timeline of milestones, breakthroughs and narratives about the kit itself. Rules: AGENTS.md, "Project log". Template repo only: bootstrap deletes it. Newest last. Times are America/Chicago.

## Arcs

| Arc | Span | Summary | Problem | Turning point | Outcome | Lesson |
|---|---|---|---|---|---|---|
| bloat-control | 2026-11-13 07:34–07:35 | The bloat audit proposes removals instead of making them. | A grep for callers cannot see tools run by hand or requests that live only in chat, so requested features could look dead. | #1 | Removals need the owner's approval in the kit and 4 projects. | - |
| project-story | 2026-11-13 07:50– | The project log becomes the source for a narrative deck. | - | - | Open: story columns and outline on a branch. | - |

## Log

| # | When | Type | Arc | Topic | Raised by | What the other missed | Evidence | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | 2026-11-13 07:34–07:35 | decision | bloat-control | Bloat audit removals need the owner's approval | Claude (explaining the audit to the owner) | The audit's "safe fixes" deleted unreferenced files without asking | Commits f8675a8, bccc1f2; merge 1ce04a8 | Rule on main in the kit and 4 projects |
| 2 | 2026-11-13 07:50 | decision | project-story | Arcs table gets Problem, Turning point, Lesson; KIT_LOG.md starts | the owner | CHANGELOG lists changes only, without misses or context | Commit 246c557 | On branch claude/story-arcs |
