# Xcode setup

1. Install full Xcode and an iOS simulator runtime. Select the intended Xcode
   developer directory if multiple versions are installed.
2. In Xcode Settings → Intelligence, enable **Allow external agents to use Xcode tools**.
3. The direct installer registers `codex mcp add xcode -- xcrun mcpbridge`.
   If you use the plugin path, use its bundled connection instead.
4. Open the intended project. Approve only the agent and project folder you
   intend to use when Xcode requests access.
5. Run `python3 scripts/setup.py doctor --probe-mcp` from the package checkout.
   The probe is read-only but identifies itself as `ios-foundry-doctor`; Apple
   may request separate approval for it. It does not prove your coding agent has
   the same approval. Ask the agent to list workspaces as a final connection check.

## Three distinct resources

- The skill provides instructions.
- `xcrun mcpbridge` connects the agent to Xcode's MCP tools.
- Xcode or its background MCP service executes actions. Permission grants and
  a running service are separate from the bridge's configuration.

For Xcode versions with a background server, inspect `xcrun mcp-server --help`.
The currently targeted version supports:

```sh
sudo xcrun mcp-server enable
xcrun mcp-server open /path/to/MyApp.xcodeproj
xcrun mcp-server status
sudo xcrun mcp-server approve <pending-request-id> --for-24-hours
```

Run administrative commands yourself after reviewing them. The installer never
enables blanket agent access, supplies your password, accepts Apple terms, or
changes the coding host's approval policy. GUI Xcode access and headless-server
access are different modes; a stopped background server alone does not prove
the GUI bridge cannot work. Use an actual tool call to verify.

If a tool says approval is required but the host cannot request it, configure
that agent session to permit approval prompts or grant the specific tool through
the host's supported UI. Xcode approval and host tool approval are separate.

If Xcode cannot launch or reports that it is corrupt, repair/reinstall Xcode
through Apple's supported installation path. The package does not remove
quarantine attributes or disable macOS security controls.

## Optional Apple skills

Compatible Xcode versions can export their own skill bundle:

```sh
mkdir -p "$HOME/xcode-skills"
xcrun agent skills export "$HOME/xcode-skills"
```

Inspect the exported skills and their terms before installing them. The exact
skill set varies by Xcode. iOS Foundry includes its own runtime integration guide;
it does not redistribute Apple's bundled skill text or install every exported
skill automatically. Exporting requires a working Xcode installation.

Sources: [Apple external-agent setup](https://developer.apple.com/documentation/xcode/giving-external-agents-access-to-xcode),
the selected Xcode's `xcrun mcpbridge --help`, and `xcrun mcp-server --help`.
