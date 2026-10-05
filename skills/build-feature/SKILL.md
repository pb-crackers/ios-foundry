---
name: build-feature
description: >
  Implementation phase used by dev-workflow after an implementation or debug
  fix plan is approved. Builds the approved scope, reviews and validates it,
  and prepares the current candidate for UAT.
---

# Build Feature

Require an approved implementation or debug plan. Set it to `building`
before implementation.

## Implement

1. Read the complete task record, approved plan, affected flow, project
   instructions, and current diff.
2. For UI work, open every approved repository mockup linked from the task
   record and give those paths to any implementing writer.
3. Use the approved plan to guide each implementation slice and its checks;
   verify dependent behavior and flag any newly discovered impact or scope
   change before departing from the plan.
4. State the validation contract: success criteria, commands, user flows,
   required visual states, and evidence. Cover failure paths as well as success:
   validate inputs, handle API errors without hiding them, and show actionable
   user-facing error, retry, or empty states where applicable. Follow project
   naming and response conventions; for greenfield work, establish consistent
   API names and request/response/error shapes rather than inventing them per
   endpoint.
5. Load `../ponytail/SKILL.md` at full intensity.
6. Use a writer only when delegation should save time. Every implementation or
   review-fix writer prompt must explicitly require that child to load and
   follow `ponytail` at full intensity in its own context.
7. Keep writes single-threaded in the existing checkout. Create a worktree only
   if the user explicitly requests one. The parent owns scope, decisions,
   verification, and Git operations.

## Review and validation

Use a fresh-context reviewer before UAT when independent review is useful. Add a
specialist review only for a specific concern. Route accepted fixes through the
sole writer and re-review only substantial or high-risk fixes.

Run focused checks after logical slices and broader project-defined checks when
warranted. For SwiftUI implementation, load `../swiftui-expert-skill/SKILL.md`;
for review, load only relevant references from `../swiftui-pro/SKILL.md`.

For Apple projects, discover the intended workspace, scheme, test plan, and run
destination with Xcode MCP. Use BuildProject and RunSomeTests (or RunAllTests
when warranted), recording results and logs. Prefer existing project scripts or
`xcodebuild` when a headless check is required. A Preview helps inspect layout
but does not replace exercising the installed candidate. Do not change a test
plan or scheme silently; restore any temporary selection after checks.

For iOS UI changes, create a fresh, dedicated simulator with a task-specific
name and the required device/runtime using `xcrun simctl`. Record its device ID
and that this task created it; never use a shared
or pre-existing simulator for this workflow. Keep it for UAT rather than
cleaning it up at Build handoff.

For every iOS UI change:

1. Load `../xcode-device-interaction/SKILL.md`. With Xcode MCP available, start a
   workspace-backed session targeting the dedicated simulator's exact UUID;
   verify the returned UUID matches before installing or interacting.
2. Produce a fresh build from current source, install, and launch it with
   `DeviceInteractionInstallAndRun`. Repeat after source changes. If Xcode MCP
   is unavailable or authorization is declined, use the project's existing
   build/install path and an available simulator interaction surface, recording
   the fallback and any checks that could not be completed.
3. Configure required device conditions such as appearance, text size,
   accessibility, location, and orientation with supported tools, simulator
   settings, or Device Hub when available.
4. Prepare app data with an existing launch argument, environment variable,
   fixture, debug seed path, UI automation, or the normal user path.
5. Exercise changed user flows and required success/failure states. Use current
   hierarchy hit points for Xcode interactions and inspect the resulting
   screenshots, hierarchy, app state, and logs. Compare screenshots with the
   approved mockup. Fix meaningful differences and repeat after UI fixes.
6. Prepare the first UAT state and expose the dedicated device in Simulator or
   Device Hub for direct user testing. End idle MCP interaction sessions and
   verify the app remains open in that state; if ending the session stops the
   app, relaunch the same candidate and restore the state before handoff.

Never edit product source or create alternate product behavior solely to force
a UAT state. Propose reusable debug-only seed support as separate approved scope
when repeated setup justifies it. If Build ends without a UAT handoff, end its
MCP interaction sessions, then shut down and delete only the dedicated simulator
it created using its recorded UUID.

## Handoff

1. Record commands, results, candidate build, source revision and uncommitted
   source changes, workspace, scheme, simulator UUID and creation ownership,
   device/runtime, conditions, state setup, evidence paths (screenshots,
   hierarchy, and logs where available), session closure, presentation surface,
   and limitations in the task record or outbox. Preserve evidence
   needed for acceptance outside temporary session files before ending sessions.
2. Set the task to `awaiting-uat`.
3. Continue directly to `uat-feature`; do not ask whether to begin UAT.

Build validation is evidence, not user approval.
