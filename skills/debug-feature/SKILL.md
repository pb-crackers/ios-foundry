---
name: debug-feature
description: >
  Diagnosis phase used by dev-workflow for reported bugs. Produces a concise,
  evidence-backed root cause analysis and fix plan before implementation.
---

# Debug Feature

Do not edit product code, commit, or begin Build during this phase. Set the
task record to `Status: debugging`. If none exists, create
`<records_dir>/Tasks/<slug>.md`, link it from the feature index, or queue both
mutations in `WORKFLOW_OUTBOX.md` when offline.

## Report

Ask only for missing information:

- What should happen?
- What happens instead?
- How can it be reproduced, if known?

## Investigate

1. Reproduce the bug when practical. For runtime UI bugs, load
   `../xcode-device-interaction/SKILL.md`; use a task-created simulator and close
   sessions and delete that simulator when diagnosis ends.
2. Trace the relevant flow directly. Delegate an independent trace only when it should save time.
3. Use available research or review tools only when an external behavior,
   competing explanation, or material risk needs resolution.
4. Do not claim a root cause without evidence.

## Record

Add or update this section in the task record:

```markdown
## Debug

### Report

### Root cause
- Symptom:
- Root cause:
- Evidence:

### Fix plan
- Smallest fix:
- Validation:
```

Keep the fix within the reported scope and include a check that proves the bug
is fixed. For UI bugs, include the required user-facing state and visual
validation.

## Approval gate

Present the root cause analysis and fix plan. Ask whether to approve it for
Build.

- On approval, set `Status: approved` and continue to `build-feature`.
- On requested changes or unresolved evidence, remain `debugging`.

Build owns implementation, review, fresh-build validation, and UAT handoff.
