#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check package metadata and loadable references without dependencies."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
names = set()
for folder in sorted((ROOT / "skills").iterdir()):
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
assert len(names) == 12
assert json.loads((ROOT / "plugin.json").read_text())["license"] == "Apache-2.0"
assert (ROOT / "LICENSE").is_file() and (ROOT / "NOTICE").is_file()
for name in ["swiftui-pro", "swiftui-expert-skill", "ponytail"]:
    assert "MIT License" in (ROOT / "skills" / name / "LICENSE").read_text()
for p in (ROOT / "skills").rglob("*"):
    assert not p.is_symlink(), f"Non-portable symlink: {p}"
print(f"Validated {len(names)} skills, references, licenses, scripts, and package metadata")
