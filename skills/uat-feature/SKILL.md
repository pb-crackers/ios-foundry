---
name: uat-feature
description: >
  User acceptance phase used by dev-workflow after Build validates the current
  candidate. Presents the running app in the required state, records user
  approval, and returns failed work to implementation.
---

# UAT Feature

Require a task record with `Status: awaiting-uat`. The parent owns the
running app, evidence, and user questions.

## Prepare

1. Confirm Build recorded the candidate build, source revision including
   uncommitted changes, workspace, scheme, dedicated simulator UUID and creation
   ownership, conditions, state setup, commands, evidence, and required visual
   states.
2. Confirm the candidate still matches current source. If the candidate is stale
   or the dedicated simulator is missing, close remaining interaction sessions,
   clean up any surviving task-created simulator, and return to Build for a
   fresh candidate and dedicated simulator; do not use a shared simulator.
   A closed MCP interaction session alone does not invalidate the candidate.
3. Reuse the dedicated simulator and Build evidence. If automation is needed,
   load `../xcode-device-interaction/SKILL.md` and reopen a session targeting its
   exact UUID. Restore required conditions and app state through supported tools,
   existing runtime seed or automation, or the normal user path. Do not alter
   product source merely to stage UAT. If a rebuild is needed, return to Build
   for validation of that candidate before acceptance.
4. Leave the app open at the first required test state in Simulator or Device
   Hub when available. End idle interaction sessions and confirm the app remains
   available; restore the same candidate and state if necessary. Tell the user
   which simulator to use and provide the test steps and expected results.

## Acceptance gate

Exercise each success criterion through the real user-facing path where
practical. Present every criterion with its evidence, the captured screenshots,
and the running app. Ask the user to approve, request changes, or state that
they cannot verify it. A build, test, review, or screenshot is not approval.

- If approved, first end remaining MCP interaction sessions, then use
  `xcrun simctl` to shut down and delete the task-created dedicated simulator by
  its recorded UUID, removing its data. Record cleanup and approval, set
  `Status: approved-to-ship`, then load `ship-feature` and continue shipping
  through the configured merge gate without asking to begin shipping.
- If changes are requested, end remaining MCP interaction sessions, shut down
  and delete the task-created dedicated simulator by its recorded UUID with
  `xcrun simctl`, record cleanup and the failed criterion, set
  `Status: building`, then return to `build-feature` for a fresh simulator,
  validation, and UAT.
- If the user cannot verify required behavior, remain `awaiting-uat`, keep the
  simulator available, end idle interaction sessions, and report the blocker.

Never erase or delete a shared or pre-existing simulator. If cleanup fails,
report the blocker and retry; do not advance to shipping or a new Build with
that simulator left behind.

UAT approval grants authority to commit, run the project-defined shipping gate,
push, and open a pull request. Merge after required checks pass only when
`auto_merge: true` or explicit user merge approval grants that authority.
Those actions belong to `ship-feature`, not UAT. Ask again only for required merge approval, a blocker, failed gate, or separate
release or deployment.
