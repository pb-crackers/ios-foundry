---
name: discuss-feature
description: >
  Discussion phase used by dev-workflow for intentionally started new or
  unclear work. Defines the product brief, success criteria, and visual states
  before implementation planning.
---

# Discuss Feature

Use only after `dev-workflow` intentionally enters tracked work. An ordinary
question or brainstorming request does not create a task record. The parent
owns user-facing decisions; do not implement during this phase.

## Understand

1. Read the request, project instructions, feature index and task
   record, and relevant code.
2. Use a subagent only for a concrete context gap or material independent
   challenge that should save time.
3. Read load-bearing files, resolve conflicting evidence, and ask only the
   remaining product, scope, naming, risk, or visual questions.

## Record

Create or update `<records_dir>/Tasks/<slug>.md` through `dev-workflow` and link it
from the feature index. When offline, queue both mutations in
`WORKFLOW_OUTBOX.md`. Record:

```markdown
# Feature name

Status: discussing
Created: YYYY-MM-DD

## Outcome

## Scope
### Included
### Excluded

## Success criteria
- [ ] Observable behavior

## Visual states
- [ ] Every changed user-visible state, or `Not applicable`

## Decisions

## Completion
- PR:
- Merge:
- Changelog:
```

Keep the brief about outcomes and constraints, not implementation details. When
discussion starts from a captured item, preserve its description.

## Planning gate

Present the outcome, scope, success criteria, and visual states. Ask whether the
user approves the brief for planning.

- On approval, set `Status: planning` and continue to `plan-feature`.
- On requested changes, revise the brief and ask again.
- On pause, leave `Status: discussing`.
