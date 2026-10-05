# Contributing

Keep changes small and portable. Respect the project's deployment target,
preserve existing skills and settings, and never automate blanket permissions.

Run `python3 tests/check_setup.py` and `python3 scripts/validate.py` before a PR.
Setup changes need a check that proves the affected behavior. Simulator changes
need the live check in `docs/smoke-test.md`, with results and limitations reported.
Document third-party sources and retain their license notices.

Contributions to original project files are under Apache-2.0. Changes to bundled
MIT components retain those components' licenses. Do not commit secrets, account
configuration, real app data, or private task records.
