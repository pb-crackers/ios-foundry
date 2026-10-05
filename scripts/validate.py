#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check package metadata and loadable references without dependencies."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
names = set()
core = sorted((ROOT / "skills").iterdir())
addons = sorted((ROOT / "addons").iterdir())
for folder in core + addons:
    entry = folder / "SKILL.md"
    text = entry.read_text()
    assert text.startswith("---\n"), entry
    header = text.split("---", 2)[1]
    name = re.search(r"^name:\s*(\S+)", header, re.M).group(1)
    assert name == folder.name and name not in names, entry
    assert re.search(r"^description:\s*\S+", header, re.M), entry
    names.add(name)
    for ref in set(re.findall(r"`((?:\.\./|references/|scripts/)[^`\s]+\.(?:md|py))`", text)):
        assert (folder / ref).is_file(), f"Missing skill reference {entry}: {ref}"
    for f in folder.rglob("*.py"):
        compile(f.read_text(), str(f), "exec")
for f in [ROOT / "plugin.json", ROOT / "mcp.json", ROOT / "sources.json",
          ROOT / ".agents/plugins/marketplace.json", ROOT / "examples/ios-foundry.json"]:
    json.loads(f.read_text())
assert len(core) == 12 and len(addons) == 1 and len(names) == 13
assert json.loads((ROOT / "plugin.json").read_text())["license"] == "Apache-2.0"
assert (ROOT / "LICENSE").is_file() and (ROOT / "NOTICE").is_file()
for name in ["swiftui-pro", "swiftui-expert-skill", "ponytail"]:
    assert "MIT License" in (ROOT / "skills" / name / "LICENSE").read_text()
addon = ROOT / "addons/app-store-screenshots"
assert "MIT License" in (addon / "LICENSE").read_text()
for required in ["template/package.json", "template/public/mockup.png", "style-prompts.md", "copy-ideas.md"]:
    assert (addon / required).is_file(), f"Missing add-on resource: {required}"
json.loads((addon / "template/package.json").read_text())
for directory in [ROOT / "skills", ROOT / "addons"]:
    for p in directory.rglob("*"):
        assert not p.is_symlink(), f"Non-portable symlink: {p}"
print(f"Validated {len(core)} core skills, {len(addons)} optional skill, references, licenses, and package metadata")
