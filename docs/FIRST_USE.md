# First use

The agent runs this once, before any other work, in one of three starts:

- The user asks you to set up a project from the kit's URL (https://github.com/[old handle]/archimedes_lever), and you are not in a clone of it yet. Ask questions 1 and 2 first, then run `git clone https://github.com/[old handle]/archimedes_lever <name>`, where `<name>` is the project name in lower case with hyphens for spaces. Work inside that folder from now on, read its AGENTS.md, and continue at step 0 (do not ask 1 and 2 again). If git is missing, tell the user how to install it for their system (https://git-scm.com/downloads), or suggest way A in README.md "Start here".
- A plain clone of the kit, and the user asks to "initiate" (or start, or set up) a project. `scripts/first_use_check.py` (the Claude Code SessionStart hook, or the first step of "Start of session") says KIT. Start at step 0.
- A repo made with GitHub's "Use this template". The check says FIRST USE: AGENTS.md still has template placeholders. Start at step 1.

If the check did not run, look at `git remote get-url origin`: a URL that ends in `archimedes_lever` is the kit itself.

## 0. Move a clone of the kit to its own repo (KIT only)

Ask round 1 below first, then ask question 10 with round 2.

| # | Question | Options |
|---|---|---|
| 10 | Where does the new repo go? | A I create it on GitHub now, public or private as in answer 3 (rec; needs a GitHub tool on this host or a signed-in `gh`) · B you create an empty repo on GitHub (no README, no license) and paste its URL · C local only for now (the Stop hook then reminds you at each turn end until a remote exists) |

Then, before step 2:

1. `git remote rename origin kit`. The kit stays as a second remote; nothing is deleted.
2. For 10A: create the repo with the host's GitHub tool, or `gh repo create <user>/<name> --private` (or `--public`), then `git remote add origin https://github.com/<user>/<name>.git`. For 10B: `git remote add origin <URL>`. For 10C: no remote; use `<user>/<name>` as planned for bootstrap's repo argument.
3. Start a fresh history, as GitHub's "Use this template" does: `git branch -m main kit-main`, then `git checkout --orphan main`. The files stay as they are; the bootstrap commit in step 2 becomes the project's first commit. Nothing is deleted: the kit's history stays on the local branch `kit-main` and the `kit` remote, and is never pushed to the new repo.
4. The folder keeps the name it was cloned as; the user can rename it after the session.

## 1. Ask the questions

Ask all questions of a round together (3 rounds, 9 questions; 10 with step 0). In Claude Code, use the clickable question dialog (4 questions at most per dialog). On other hosts, write them as a numbered list with lettered options. Mark your recommendation. A free-text answer comes through "Other".

Round 1: the project

| # | Question | Options |
|---|---|---|
| 1 | What is the project called? | Free text |
| 2 | What is it for, in one line? | Free text |
| 3 | Is the repo public or private? | A private (rec) · B public |
| 8 | Which license for the project? | A MIT (rec for a public repo) · B Apache-2.0 · C none: all rights reserved (rec for a private repo) |

Round 2: you and personal data (step 0 adds question 10 here)

| # | Question | Options |
|---|---|---|
| 4 | What should agents call you in the repo files? | A "the owner" (rec) · B a role, for example "the maintainer" · C your first name (private repos only; with the guard on, a name on your denylist blocks every push, so choose C only with the guard off) |
| 5 | Turn on the personal-data guard? It blocks emails, phone numbers, ID numbers, API tokens, private keys and your listed names before a push. | A on (rec) · B on, and also block .internal addresses (for US government or org-specific work) · C off |
| 6 | Where will you push from? | A Claude cloud sessions · B your own computer · C both |

Round 3: time and tools

| # | Question | Options |
|---|---|---|
| 9 | Which time zone for project log times? | A your local time zone (rec; give its IANA name, for example Europe/Berlin or America/New_York) · B UTC |
| 7 | Which other agents will you use? (several allowed) | A none · B ChatGPT or Codex · C Gemini · D another tool |

Rules for the asking agent:
- A public repo never uses a real name (question 4, option C is refused).
- Never ask for the names on the denylist. The owner types them only in the settings pages in step 3. If the owner pastes names into the chat, do not repeat them, and tell the owner that they are now in the chat history.

## 2. Apply the answers

1. Run `scripts/bootstrap.sh "<1>" <owner/repo from git remote get-url origin> "<2>" "<4>" "<9>"`. Give "the owner" as the 4th argument when that is the answer. The 5th argument is the IANA time zone name (UTC for 9B). The script deletes itself when done; keep this file, because step 3 is also what an agent shows when a session reports DENYLIST. It moves the kit's license to docs/archimedes_lever-LICENSE.txt: keep that file, because it covers the kit's scripts.
2. Public repo: add to AGENTS.md "Project rules" a line that names a private place for the project log (for example a private Claude doc), because the log can hold environment detail. Write the date and "(the owner, YYYY-MM-DD)".
3. Guard: for 5B, remove the "# " in front of the line `# check: internal` in `.pii-guard`. For 5C, delete `.pii-guard`; the hook and the Action then skip the guard.
4. License (answer 8): for A, copy docs/archimedes_lever-LICENSE.txt to `LICENSE` and change the copyright line to the current year and the GitHub account or organization from `<owner/repo>`, unless the owner names another holder (a public repo never uses a real name the owner has not given). For B, save the text from https://www.apache.org/licenses/LICENSE-2.0.txt, unchanged, as `LICENSE`. For C, add no LICENSE.
5. Record the answers as the owner's decisions in docs/DECISIONS.md, and add one `decision` row to the project log.
6. Commit with a noreply identity, run `scripts/session_checkin.sh` (it installs the git hooks), and push (`git push -u origin main`; for 10C, skip the push).

## 3. The denylist places (guard on)

The owner adds the names, comma or newline separated, in each place the answers need. Give the owner this list with the links filled in. The guard blocks every push and every pull request check where no denylist is found (decision 2A, 2026-11-11).

| Answer 6 | Place | Where the owner adds it |
|---|---|---|
| A or C | Each Claude cloud environment the repo uses | Environment menu in the session title bar > Edit > Environment variables: `PII_GUARD_DENYLIST=Name1,Name2,...`. A new session picks it up |
| B or C | The owner's computer | The file `~/.config/pii-guard/denylist.txt` (Windows: `C:\Users\<user>\.config\pii-guard\denylist.txt`), one name per line |
| Always | GitHub pull-request check | `https://github.com/<owner/repo>/settings/secrets/actions` > New repository secret > Name `PII_GUARD_DENYLIST` |

## 4. Verify

Run `python3 scripts/pii_guard.py --status` in each place you can reach. It prints `denylist: N entries from <source>`, never the names. Then `python3 scripts/pii_guard.py --all` must print `PII GUARD PASS`. Report both lines. A cloud environment edited during this session is verified in the next session: the SessionStart check says so if it is still missing.

Answer 7: paste the matching texts from docs/host-prompts.md for the owner, under Copy.
