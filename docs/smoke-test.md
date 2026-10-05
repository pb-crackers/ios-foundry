# Live release check

Use a disposable app project and a task-created simulator, not a user's active
development app or simulator. Keep real accounts and sensitive data out of test
screenshots. This is a manual acceptance check, not a claim that it has passed.

1. Install into a fresh temporary skill directory with `--skills-dir`, keeping
   the host's existing skills intact. Confirm repeat installation is harmless.
2. Run doctor, then `doctor --probe-mcp` with Xcode open. From the coding agent,
   list the intended workspace and verify agent/folder approval.
3. Ask dev-workflow to discuss a small SwiftUI UI change. Confirm it records the
   brief in the configured storage, asks for scope/plan approval, and loads the
   relevant SwiftUI references without changing the deployment target.
4. Approve implementation. Confirm Xcode BuildProject and the relevant tests
   pass against the intended scheme and destination. Record actual results.
5. Confirm Build creates one dedicated simulator and records its UUID. Exercise
   the changed UI, one failure or empty state, and a relevant accessibility
   condition. Inspect screenshots, hierarchy, and logs against the criterion.
6. Confirm ending the MCP session leaves the same candidate available in the
   visible Simulator at the first UAT state. If closure stops it, verify that
   restoring the installed candidate works without an unvalidated rebuild.
7. Request a change once. Confirm only the task-created device is cleaned up,
   then a fresh candidate is validated and presented again.
8. Approve UAT. Confirm shipping runs the project's headless gate, creates the
   PR, and stops for merge approval with `auto_merge: false`. No deployment
   should occur. Do not merge a disposable test PR unless explicitly intended.
9. Uninstall the test copies. Confirm modified or pre-existing skills are
   preserved and simulator/session cleanup is recorded.

Record Xcode build, Codex version, simulator/runtime, source revision, commands,
results, and limitations in the release notes. The automated package tests run
without Xcode; live device behavior and plugin-host installation need this check.
