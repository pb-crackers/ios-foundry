#!/usr/bin/env python3
# Copyright 2026 Phillip Dougherty. SPDX-License-Identifier: Apache-2.0
"""Install isolated skill copies, check prerequisites, and undo unchanged installs."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import selectors
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ".ios-foundry-install.json"


def run(args, timeout=30):
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout)


def hashes(directory):
    # Refuse symlinks rather than following them into another installation.
    result = {}
    for p in directory.rglob("*"):
        if p.is_symlink():
            raise ValueError(f"Symlink inside skill: {p}")
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc":
            result[p.relative_to(directory).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return result


def install_skills(target, dry_run=False):
    target = target.expanduser().resolve()
    marker = target / MANIFEST
    owned = json.loads(marker.read_text()) if marker.exists() else {}
    pending = []
    for source in sorted((ROOT / "skills").iterdir()):
        if not source.is_dir():
            continue
        dest = target / source.name
        expected = hashes(source)
        if dest.is_symlink() or (dest.exists() and (not dest.is_dir() or hashes(dest) != expected)):
            raise ValueError(f"Existing skill differs: {dest}. Choose another --skills-dir; nothing was copied.")
        if not dest.exists():
            pending.append((source, dest, expected))
        else:
            print(f"KEEP {source.name} (identical)")
    if dry_run:
        for source, _, _ in pending:
            print(f"WOULD COPY {source.name} to {target}")
        return
    target.mkdir(parents=True, exist_ok=True)
    for source, dest, expected in pending:
        shutil.copytree(source, dest)
        owned[source.name] = expected
        # Persist ownership after each copy so interrupted installation is recoverable.
        marker.write_text(json.dumps(owned, indent=2) + "\n")
        print(f"COPY {source.name}")


def uninstall_skills(target, dry_run=False):
    target = target.expanduser().resolve()
    marker = target / MANIFEST
    if not marker.exists():
        print("No installation ownership record; nothing removed.")
        return
    owned = json.loads(marker.read_text())
    removable = []
    for name, expected in owned.items():
        if Path(name).name != name or name in (".", ".."):
            raise ValueError("Invalid installation ownership record")
        dest = target / name
        if dest.is_symlink() or (dest.exists() and (not dest.is_dir() or hashes(dest) != expected)):
            raise ValueError(f"Modified skill retained: {dest}. Nothing was removed.")
        if dest.exists():
            removable.append(dest)
    for dest in removable:
        print(f"{'WOULD REMOVE' if dry_run else 'REMOVE'} {dest}")
        if not dry_run:
            shutil.rmtree(dest)
    if not dry_run:
        marker.unlink()


def mcp_probe():
    """Perform an actual read-only MCP call with a bounded stdio session."""
    proc = subprocess.Popen(["xcrun", "mcpbridge"], stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    selector = selectors.DefaultSelector()
    selector.register(proc.stdout, selectors.EVENT_READ)
    buffer = b""

    def request(ident, method, params):
        nonlocal buffer
        proc.stdin.write((json.dumps({"jsonrpc": "2.0", "id": ident,
                                     "method": method, "params": params}) + "\n").encode())
        proc.stdin.flush()
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                message = json.loads(line)
                if message.get("id") == ident:
                    if "error" in message:
                        raise ValueError(str(message["error"]))
                    return message.get("result", {})
            if selector.select(max(0, deadline - time.monotonic())):
                chunk = os.read(proc.stdout.fileno(), 65536)
                if not chunk:
                    raise ValueError("Xcode bridge closed before replying")
                buffer += chunk
        raise ValueError("Xcode MCP timed out; check Xcode permission prompts")

    try:
        request(1, "initialize", {"protocolVersion": "2024-11-05", "capabilities": {},
                                 "clientInfo": {"name": "ios-foundry-doctor", "version": "0.1.0"}})
        proc.stdin.write(b'{"jsonrpc":"2.0","method":"notifications/initialized"}\n')
        proc.stdin.flush()
        available = request(2, "tools/list", {})
        names = {t["name"] for t in available.get("tools", [])}
        if "XcodeListWorkspaces" not in names:
            raise ValueError("Connected server lacks XcodeListWorkspaces")
        result = request(3, "tools/call", {"name": "XcodeListWorkspaces", "arguments": {}})
        if result.get("isError"):
            raise ValueError("; ".join(c.get("text", "") for c in result.get("content", [])))
        interaction = {"DeviceInteractionStartWorkspaceSession", "DeviceInteractionInstallAndRun",
                       "DeviceInteractionSynthesize", "DeviceInteractionEndSession"}
        if not interaction <= names:
            raise ValueError("MCP responds, but this Xcode lacks required device interaction tools")
        return "read-only workspace call passed; device tools advertised"
    finally:
        selector.close()
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()


def doctor(target, probe=False):
    problems = []
    def check(label, passed, detail):
        print(f"{'PASS' if passed else 'FAIL'} {label}: {detail}")
        if not passed:
            problems.append(label)
    check("macOS", platform.system() == "Darwin", platform.system())
    check("Python", sys.version_info >= (3, 10), platform.python_version() + " (3.10+ required)")
    for tool in ["git", "codex", "xcrun", "xcodebuild"]:
        check(tool, bool(shutil.which(tool)), shutil.which(tool) or "not installed")
    if shutil.which("xcrun") and platform.system() == "Darwin":
        for tool in ["mcpbridge", "simctl"]:
            result = run(["xcrun", "--find", tool])
            check(tool, result.returncode == 0, result.stdout.strip() or result.stderr.strip())
        result = run(["xcodebuild", "-version"])
        check("Xcode version", result.returncode == 0, result.stdout.strip() or result.stderr.strip())
        result = run(["xcrun", "simctl", "list", "runtimes", "--json"])
        try:
            runtimes = json.loads(result.stdout)["runtimes"]
            usable = [r["name"] for r in runtimes if r.get("isAvailable") and "iOS" in r["name"]]
        except (ValueError, KeyError):
            usable = []
        detail = ", ".join(usable) or (result.stderr.strip() if result.returncode else
                    "install an iOS runtime in Xcode Settings > Components")
        check("iOS runtime", bool(usable), detail)
    check("skill copies", all((target / p.name / "SKILL.md").exists()
          for p in (ROOT / "skills").iterdir() if p.is_dir()), str(target))
    if shutil.which("codex"):
        result = run(["codex", "mcp", "get", "xcode", "--json"])
        try:
            cfg = json.loads(result.stdout)
            transport = cfg.get("transport", {})
            configured = (cfg.get("enabled", True) and transport.get("command") == "xcrun"
                          and transport.get("args") == ["mcpbridge"])
        except ValueError:
            configured = False
        check("Codex Xcode connection", configured, "configured" if configured else "run codex mcp add xcode -- xcrun mcpbridge (or inspect an existing plugin connection)")
    print("INFO GitHub PR shipping requires gh and gh auth login; local builds do not.")
    print("INFO Xcode approvals and account sign-in are user-controlled; installation does not grant them.")
    if probe and platform.system() == "Darwin":
        try:
            check("live MCP", True, mcp_probe())
        except (ValueError, OSError) as error:
            check("live MCP", False, str(error))
    else:
        print("NOT TESTED live MCP: run doctor --probe-mcp with your project open in Xcode.")
    print("INFO Simulator app handoff and app-specific tests require a real project; see docs/smoke-test.md.")
    return 1 if problems else 0


def install_tools(download_runtime=False):
    if platform.system() != "Darwin":
        raise ValueError("Tool installation requires macOS")
    if not shutil.which("codex"):
        if not shutil.which("npm"):
            if not shutil.which("brew"):
                raise ValueError("Install Node.js or Homebrew, then rerun --install-tools")
            subprocess.run(["brew", "install", "node"], check=True)
        subprocess.run(["npm", "install", "--global", "@openai/codex"], check=True)
    if download_runtime:
        subprocess.run(["xcodebuild", "-downloadPlatform", "iOS"], check=True)
    if not shutil.which("gh"):
        if shutil.which("brew"):
            subprocess.run(["brew", "install", "gh"], check=True)
        else:
            print("INFO Install GitHub CLI from cli.github.com when you want PR shipping.")


def configure_mcp():
    result = run(["codex", "mcp", "get", "xcode", "--json"])
    if result.returncode == 0:
        cfg = json.loads(result.stdout)
        transport = cfg.get("transport", {})
        if transport.get("command") != "xcrun" or transport.get("args") != ["mcpbridge"] or not cfg.get("enabled", True):
            raise ValueError("Existing xcode MCP configuration differs or is disabled; retained unchanged. Resolve it manually.")
        print("KEEP existing xcode MCP configuration")
        return
    # Missing connection only; unreadable config is not permission to replace it.
    if "No MCP server named" not in result.stderr:
        raise ValueError("Could not inspect Codex MCP configuration; retained unchanged: " + result.stderr.strip())
    subprocess.run(["codex", "mcp", "add", "xcode", "--", "xcrun", "mcpbridge"], check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["install", "doctor", "uninstall"])
    parser.add_argument("--skills-dir", type=Path)
    parser.add_argument("--project", type=Path, help="install in this project's .agents/skills")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--install-tools", action="store_true", help="install missing Codex/Node using npm/Homebrew")
    parser.add_argument("--download-runtime", action="store_true", help="download Apple's iOS runtime (large)")
    parser.add_argument("--skip-mcp", action="store_true", help="copy skills without changing Codex MCP config")
    parser.add_argument("--probe-mcp", action="store_true", help="make a read-only MCP call; may show Xcode approval")
    args = parser.parse_args()
    if sys.version_info < (3, 10):
        parser.error("Python 3.10+ required; install Python or rerun install.sh --install-tools")
    if args.project and args.skills_dir:
        parser.error("Choose --project or --skills-dir")
    if args.project and not args.project.expanduser().is_dir():
        parser.error("--project must name an existing project directory")
    target = args.skills_dir or ((args.project / ".agents/skills") if args.project else Path.home() / ".agents/skills")
    if args.command == "doctor":
        return doctor(target.expanduser().resolve(), args.probe_mcp)
    if args.command == "uninstall":
        uninstall_skills(target, args.dry_run)
        print("Codex MCP configuration and project records are retained.")
        return 0
    if args.dry_run:
        install_skills(target, True)
        print("WOULD check tools and configure Xcode MCP unless --skip-mcp; no host settings changed.")
        return 0
    install_skills(target, True)  # Check every conflict before installing tools or configuring MCP.
    if args.install_tools or args.download_runtime:
        install_tools(args.download_runtime)
    if not args.skip_mcp:
        if not shutil.which("codex"):
            raise ValueError("Codex missing: rerun with --install-tools, or use --skip-mcp")
        configure_mcp()
    install_skills(target)
    if args.project:
        config = args.project.expanduser().resolve() / ".ios-foundry.json"
        if not config.exists():
            config.write_text((ROOT / "examples/ios-foundry.json").read_text())
    print("Skill copies installed. Restart the agent if needed. Follow skills/xcode-device-interaction/references/setup.md to approve Xcode access.")
    return doctor(target.expanduser().resolve())


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        sys.exit(1)
