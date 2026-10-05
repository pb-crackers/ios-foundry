# Third-party notices

The root Apache-2.0 license applies to original iOS Foundry workflow adaptations,
installer, integration guide, tests, and documentation. It does not replace the
licenses of the following bundled components.

| Directory | Author / source | License |
| --- | --- | --- |
| `skills/swiftui-pro` | Paul Hudson — [SwiftUI-Agent-Skill](https://github.com/twostraws/SwiftUI-Agent-Skill) | [MIT](skills/swiftui-pro/LICENSE) |
| `skills/swiftui-expert-skill` | Antoine van der Lee — [SwiftUI-Agent-Skill](https://github.com/AvdLee/SwiftUI-Agent-Skill) | [MIT](skills/swiftui-expert-skill/LICENSE) |
| `skills/ponytail` | DietrichGebert — [Ponytail](https://github.com/DietrichGebert/ponytail), installed version 4.13.0 | [MIT](skills/ponytail/LICENSE) |

These are snapshots copied from the author's installed skills on 2026-10-05,
not downloads of an unpinned moving branch. Original entrypoint hashes are in
`sources.json`; exact packaged file hashes are checked during installation.
SwiftUI Pro's duplicate plugin copy was omitted. Its deployment-target rules
were adapted to respect the consuming project. SwiftUI Expert's existing local
guidance and Instruments scripts are included; its entrypoint matches the topic
coverage of the upstream skill checked during preparation. Both retain their
MIT notices. Ponytail's host-specific argument-hint metadata was removed for
Codex skill-validator compatibility; its instructions are retained. Logos and upstream plugin metadata were omitted.

The workflow originated in Phillip Dougherty's personal configuration and was
adapted for portable task storage, host-neutral delegation, Xcode integration,
and explicit merge policy. Copies are independent of that personal installation.

`skills/xcode-device-interaction` is newly written integration guidance based on
the exposed tool interface. Apple's Xcode binaries and bundled skill documents
are not copied into this repository. Users can export their own bundled Apple
skills from a compatible installed Xcode subject to Apple's terms.

The README cover is original AI-generated artwork prepared for this project;
no third-party logos or upstream skill artwork are included. Generation details
are in `assets/cover-prompt.txt`.
