---
name: xcode-device-interaction
description: Build and verify Apple apps with Xcode MCP, simulator interactions, screenshots, UI hierarchy, and runtime logs. Use for runtime UI verification and debugging, not unit-test-only tasks.
license: Apache-2.0
---

# Xcode runtime verification

This is iOS Foundry's original integration guide for Apple's Xcode MCP interface.
Use the live tool schemas; availability differs between Xcode releases. Run the
package doctor before diagnosing missing tools. Read `references/setup.md`
for setup and the optional export of Apple's bundled skills.

## Candidate and device

The parent agent owns workspace selection, evidence, cleanup, and user approval.
Delegation is optional; give each session one owner. Never control the same
simulator concurrently with the user or another agent.

Open the intended `.xcodeproj` or `.xcworkspace` with XcodeOpenWorkspace.
Discover schemes, test plans, and eligible destinations before building. If
Xcode requests approval, let the user approve the agent and project folder;
never grant blanket permissions or change the host's approval policy.

For workflow UI checks, create a dedicated simulator with `xcrun simctl create`
using an installed, compatible device type and runtime. Record its UUID and
creation ownership immediately. Never erase or delete a pre-existing device.
Pass that UUID to DeviceInteractionStartWorkspaceSession with the explicit
workspace. Check that its returned deviceUUID equals the requested UUID and
deviceIsSimulator is true. If it differs, end the session before proceeding.

DeviceInteractionInstallAndRun builds, installs, and launches the workspace app.
Repeat it after source changes. Use existing per-run launch arguments or
environment variables to stage data; preserve scheme values with the supported
`$(inherited)` placeholders. Do not alter product behavior just to stage a test.
For an already-installed candidate, DeviceInteractionStartSession can reconnect
without rebuilding. A new build must return to Build validation before UAT.

## Observe, interact, verify

Capture the current screen and hierarchy with DeviceInteractionSynthesize before
acting. Use the most recent hierarchy's hitPoint for taps. After each action,
inspect the returned screenshot and hierarchy and confirm the intended result.
Use screenshot-estimated coordinates only for inaccessible remote placeholders
or after a hierarchy-based hit point fails and recapture confirms no change.

The current interface accepts commands such as `t 100 200` (tap),
`t 200 600 f 200 200 0.3` (swipe), `sender keyboard kbd hello` (type), and
`orientation landscapeLeft`. Keyboard text consumes the remainder of a command.
For overlapping apps, activate the hierarchy element's activationBundleId first.
Use supported tools or simulator Settings for appearance, Dynamic Type,
accessibility, and location. Do not claim an unconfigured condition was tested.

The returned key is interactionSessionKey. Synthesize currently calls its input
interactSessionKey; InstallAndRun and EndSession use interactionSessionKey.
Follow the live schema instead of assuming the names match. Keep keys in runtime
context, not durable task records.

Cover each changed flow and relevant empty, loading, error, and success states.
Distinguish expected disabled controls and transient loading from actual bugs.
Report crashes, unresponsive actions, missing content, overlapping or clipped
text, accessibility problems, and mockup differences with evidence. Recapture
after animations; retry a failed action once after checking the updated target.
Inspect applicationState and logs when behavior fails; stop unbounded retries.

## Evidence and handoff

Copy screenshots, hierarchy, and logs needed for acceptance into the project's
chosen evidence directory before ending a session. Record candidate source
revision including uncommitted changes, scheme, runtime, UUID, setup, tested
criteria, results, and limitations. Avoid putting sensitive app data into a
public repository.

DeviceInteractionEndSession releases the automation session; it is separate
from deleting a simulator. End idle sessions. Before handoff, leave the exact
candidate at the first UAT state in the visible Simulator app. Verify session
closure did not stop it; if necessary relaunch the same installed candidate and
restore the state. Retain the dedicated simulator while the user tests.

After approval, requested changes, or a run ending without handoff, close the
remaining sessions and shut down/delete only the recorded task-created UUID.
Record cleanup failures and resolve them before advancing the workflow.

If the MCP or interaction tools are unavailable, use the project's existing
`xcodebuild` and simulator path. Report incomplete checks. Builds, tests,
Previews, screenshots, and automated verification never constitute user UAT
approval.
