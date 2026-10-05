---
name: ship-feature
description: >
  Shipping phase used by dev-workflow after UAT approval. Runs the project's
  headless gate, opens a pull request, follows the configured merge policy,
  and records completion.
---

# Ship Feature

Require a task record with `Status: approved-to-ship`, `shipping`, or
`awaiting-merge` and recorded UAT approval. That approval grants shipping authority.
Merge authority follows the project policy in `.ios-foundry.json`; `auto_merge` defaults to false.

1. Inspect the final diff and status; preserve unrelated work and confirm every
   approved criterion and visual state.
2. Set `Status: shipping`, commit only approved task files, and run every
   project-defined headless shipping command before each push, including any
   app-specific validation script named in project instructions. Do not open
   Device Hub merely to ship and never bypass a tracked hook.
3. When the gate passes, push and open the pull request without asking. Record
   the command, result, UAT approval, commits, and PR URL in the task record or
   outbox.
4. Wait for required remote checks. If none exist, the successful local gate is
   the build evidence. Never ignore a failed check without explicit approval.
5. If shipping uncovers a required code change, set `Status: building`, return
   to `build-feature`, and repeat UAT before shipping again.
6. When required checks pass, merge automatically only with `auto_merge: true`
   or explicit user merge approval. Otherwise present the PR and await approval.
   If checks are pending, wait;
   if the workflow must stop, set `Status: awaiting-merge` so a later invocation
   resumes here. Ask for required merge approval or blockers. Release or deployment requires separate
   authority.
7. After merge, record completion evidence and set `Status: done`. Move the item
   from the feature index to `bugs-log.md` for a bug or
   `implementation-log.md` for a feature or improvement, with its completion
   date, task-record link, and PR. Commit any remaining approved repository
   documentation through the same headless gate.

Report the branch, commits, PR, checks, merge status, approval evidence, and any
remaining risk. Never claim completion for an unapproved or blocked step.
