---
name: dev-workflow
description: >
  Parent-controlled workflow for discussing, planning, building, validating,
  and shipping development work. Preserves task records, prepares UI for direct
  user testing, and requires approval at product, plan, and UAT gates.
---

# Development Workflow

Load only the active phase skill. The parent owns decisions, user questions,
record reconciliation, and final verification.
Load supporting skills only when the active phase requires them.

## Intent gate

Questions, reviews, and brainstorming stay conversational. Do not create a task
record, branch, edit, or subagent run unless the user asks to capture, debug,
plan, build, or ship work.

## Preflight

After work is requested:

1. Read project instructions, relevant code, Git status, branch, recent commits,
   and existing conventions.
2. Preserve uncommitted work. Never stash, discard, reset, or overwrite it
   without permission.
3. Resolve project task storage and reconcile its outbox.
4. Before the first repository edit, create or reuse a non-default feature
   branch. Ask first when the working tree makes branching unsafe.
5. Load `../ponytail/SKILL.md` at full intensity for code changes.

## Task storage

Read the project's `.ios-foundry.json` when present. Resolve `records_dir`
relative to the project root; default to `docs/workflow`. An explicitly configured
external directory can point at an Obsidian vault, but Obsidian and iCloud are
not required. Never infer a personal vault path.

Use `<records_dir>/Features.md` for open work, `Tasks/<task-slug>.md` for task
records, and `bugs-log.md` / `implementation-log.md` for completed work. Keep
feature index headings `Bugs`, `Feature Ideas`, `Improvements`, `Brain Dump`,
and `Roadmap`. Link records with relative paths. Move completed items from the
index to the appropriate completion log after merge.

If storage is unavailable, queue complete intended updates in repository-root
`WORKFLOW_OUTBOX.md` with timestamp, target path, operation, and content. Reconcile
in order when storage returns; preserve conflicting versions and ask before
resolving a conflict. Delete the queue only once all entries are applied.

## Task records

Create one task record when intentional discussion begins. It is the source of
truth for the brief, success criteria, decisions, implementation plan,
validation, approvals, and completion evidence. Keep HTML mockups in the
repository at `mockups/<task-slug>/` and link them from the task record.

## Routing

Load the matching sibling skill with `read` and follow it in this parent
session:

| Task state | Skill |
| --- | --- |
| Capture a named idea and description | `../capture-todo/SKILL.md` |
| Reported bug or `debugging` | `../debug-feature/SKILL.md` |
| New, unclear, or `discussing` | `../discuss-feature/SKILL.md` |
| `planning` | `../plan-feature/SKILL.md` |
| `approved` or `building` | `../build-feature/SKILL.md` |
| `awaiting-uat` | `../uat-feature/SKILL.md` |
| `approved-to-ship`, `shipping`, or `awaiting-merge` | `../ship-feature/SKILL.md` |
| `done` | Report the recorded outcome; do not restart work |

For Apple UI work requiring device verification, Build loads
`../xcode-device-interaction/SKILL.md` and owns automated runtime checks. UAT
inherits the verified candidate and evidence, loading the device skill again
only when interaction is needed. The parent can use it directly; delegation is
optional. UAT still requires the user's acceptance.

## Gates

1. Discussion → planning: confirm the brief, scope, and success criteria.
2. Debugging → build: approve the root cause analysis and fix plan.
3. Planning → build: approve the implementation plan and every UI mockup.
4. Build → UAT: automatic after review and validation. Build owns internal
   checks; UAT owns presenting the current candidate ready for user testing.
5. UAT → ship: behavior and visual approval grants authority to commit, run
   the project-defined gate, push, and open a pull request. Continue directly to
   `ship-feature`. Merge automatically only when the project explicitly sets
   `auto_merge: true`; otherwise present the PR and request merge approval.
6. Ship → merge: follow the configured merge policy after required checks pass.
   Ask only when blocked or when separate release or deployment authority is
   required.

On a later invocation, resume from `Status` rather than repeating completed
work.

## Subagents

Default to the parent. Delegate only for a concrete context gap, implementation
slice, external question, or independent review that should reduce elapsed time.
Parallelize only independent bounded work. Do not launch subagents for simple
questions or ordinary discussion.

Use the host agent's available delegation tools. Keep one writer per checkout.
Do not create Git worktrees unless the user explicitly requests one. Give each
child a bounded assignment; ordinary children must not delegate further. Every
implementation or review-fix writer must load `../ponytail/SKILL.md` at full
intensity. The parent owns Git, external mutations, and final verification.

If a run reports `running` without child activity or a live route, inspect it
once, then stop and relaunch it fresh rather than waiting indefinitely. The
parent inspects all changes and evidence directly. Authenticated remote commands
and hosted-service mutations remain parent-only.
