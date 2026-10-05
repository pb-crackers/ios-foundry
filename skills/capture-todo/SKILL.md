---
name: capture-todo
description: >
  Todo intake phase used by dev-workflow. Accepts a required name and
  description and records a concise undiscussed item in the project's workflow
  feature index.
---

# Capture Todo

Use this when the user wants to record an idea or bug without discussing or
building it yet.

## Input

Require:

- **Name:** a short human-readable title.
- **Description:** a concise explanation of the desired outcome or problem.

Ask for whichever value is missing. Derive a lowercase hyphenated slug from the
name; do not make the user provide one.

## Record

Resolve the feature index through `dev-workflow`. Record the item under
`Feature Ideas` or `Bugs`:

```markdown
- [ ] **Offline mode** (`offline-mode`) — Let users access saved content without a connection.
```

When the vault is unavailable, queue the complete update in
`WORKFLOW_OUTBOX.md`. Keep each item on one line and preserve the user's meaning.
Do not create a task record yet.

If the slug already exists, show the existing entry and ask whether to update
its name or description; never add a silent duplicate.

## Finish

Show the exact recorded or queued entry. If the user already authorized a
commit or push, act within that authority; otherwise ask once. Todo capture does
not require implementation, UAT, a changelog entry, or subagents.
