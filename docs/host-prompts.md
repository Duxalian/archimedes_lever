# Host prompts: {{PROJECT_NAME}}
> Template: first use fills in the {{...}} values and deletes this line.

Text for places outside the repo. Keep each text a pointer. Put rules in AGENTS.md, not here.

## claude.ai Project instructions

```
{{PROJECT_NAME}}. Before repo work, attach the GitHub repo {{REPO}} and follow its AGENTS.md. The repo overrides this text and this Project's chats. If you cannot attach the repo, say so and stop. Keep this text a pointer: put new rules in the repo.
```

## GPT project instructions

```
{{PROJECT_NAME}}. The source of truth is the GitHub repo {{REPO}}. Before work, read its AGENTS.md and docs/NEXT_PROMPT.md and follow them. The repo overrides this text.
```

## Gemini CLI

Nothing to paste: GEMINI.md in the repo imports AGENTS.md. Check with `/memory show`.

## Any other chat or agent (no repo access)

```
{{PROJECT_NAME}}. The source of truth is the GitHub repo {{REPO}}. If you can read it, read AGENTS.md and docs/NEXT_PROMPT.md first and follow them. If you cannot, say so, and give every change as full text for me to paste, with the file path. The repo overrides this text.
```
