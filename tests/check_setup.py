#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Runnable safety checks; no Xcode or changes to the real home directory."""
import importlib.util
import contextlib
import io
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("setup", Path(__file__).resolve().parents[1] / "scripts/setup.py")
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)


def rejected(operation):
    try:
        operation()
    except ValueError:
        return
    raise AssertionError("Unsafe operation was accepted")


with contextlib.redirect_stdout(io.StringIO()), tempfile.TemporaryDirectory() as temporary:
    root = Path(temporary)
    target = root / "skills"
    setup.install_skills(target, dry_run=True)
    assert not target.exists(), "Dry run wrote files"
    setup.install_skills(target)
    original = (target / setup.MANIFEST).read_bytes()
    setup.install_skills(target)
    assert (target / setup.MANIFEST).read_bytes() == original, "Repeat install changed ownership"
    user_file = target / "dev-workflow/SKILL.md"
    user_file.write_text(user_file.read_text() + "\nUser edits\n")
    rejected(lambda: setup.install_skills(target))
    rejected(lambda: setup.uninstall_skills(target))
    assert (target / "ship-feature/SKILL.md").exists(), "Partial uninstall removed unrelated skill"
    user_file.write_bytes((setup.ROOT / "skills/dev-workflow/SKILL.md").read_bytes())
    setup.uninstall_skills(target, dry_run=True)
    assert user_file.exists()
    setup.uninstall_skills(target)
    assert not user_file.exists()
    # An identical skill which predates this installer is never owned or removed.
    import shutil
    shutil.copytree(setup.ROOT / "skills/dev-workflow", target / "dev-workflow")
    setup.install_skills(target)
    setup.uninstall_skills(target)
    assert (target / "dev-workflow/SKILL.md").exists()
    # A symlink to another installation is never followed or replaced.
    external = root / "external"
    external.mkdir()
    (external / "important.txt").write_text("keep")
    (target / "ship-feature").symlink_to(external, target_is_directory=True)
    rejected(lambda: setup.install_skills(target))
    assert (external / "important.txt").read_text() == "keep"
    # Exercise the real stdio protocol reader against a small fake MCP bridge.
    bridge = root / "bridge.py"
    bridge.write_text('''import sys,json
for line in sys.stdin:
 r=json.loads(line)
 if 'id' not in r: continue
 result={}
 if r['method']=='tools/list':
  result={'tools':[{'name':n} for n in ['XcodeListWorkspaces','DeviceInteractionStartWorkspaceSession','DeviceInteractionInstallAndRun','DeviceInteractionSynthesize','DeviceInteractionEndSession']]}
 if r['method']=='tools/call':
  assert r['params']['name']=='XcodeListWorkspaces'
  result={'content':[{'type':'text','text':'test workspace'}]}
 print(json.dumps({'jsonrpc':'2.0','id':r['id'],'result':result}),flush=True)
''')
    real_popen = subprocess.Popen
    with patch.object(setup.subprocess, "Popen", side_effect=lambda args, **kwargs:
                      real_popen([sys.executable, str(bridge)], **kwargs)):
        assert "read-only workspace call passed" in setup.mcp_probe()
    # MCP configuration conflicts and access errors must not become overwrites.
    with patch.object(setup, "run", return_value=subprocess.CompletedProcess(
            [], 0, '{"enabled":true,"transport":{"command":"other","args":[]}}', '')):
        rejected(setup.configure_mcp)
    with patch.object(setup, "run", return_value=subprocess.CompletedProcess(
            [], 1, '', 'Permission denied')):
        rejected(setup.configure_mcp)

print("Installer safety checks passed")
