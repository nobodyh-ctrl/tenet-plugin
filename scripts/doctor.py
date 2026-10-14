#!/usr/bin/env python3
"""Read-only environment diagnostics for facundo-agent-config.

Reports tool versions, whether the guard hook can run, and the install state of rules, plugin,
permissions and the Engram MCP entry. Never writes, and never runs commands that change state.
Usage: python scripts/doctor.py [--config-dir DIR]
"""
import argparse
import importlib.util
import json
import os
import platform
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("agentcfg", os.path.join(HERE, "agentcfg.py"))
agentcfg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agentcfg)


def version(binary, args=("--version",)):
    if not binary:
        return None
    return agentcfg.tool_version(binary, args)


def line(label, value, ok=True):
    print("  [%s] %-22s %s" % ("ok" if ok else "!!", label, value))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Read-only diagnostics.")
    parser.add_argument("--config-dir", help="Claude config dir (default: $CLAUDE_CONFIG_DIR or ~/.claude)")
    args = parser.parse_args(argv)
    try:
        config = agentcfg.resolve_config_dir(args.config_dir)
    except agentcfg.InstallError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1
    problems = 0

    print("environment")
    line("os", "%s %s (%s)" % (platform.system(), platform.release(), "WSL" if "microsoft" in platform.release().lower() else "native"))
    line("python", sys.version.split()[0], sys.version_info >= (3, 9))
    for name, binary, flags, required in (
        ("claude", agentcfg.find_claude(), ("--version",), True),
        ("engram", agentcfg.find_engram(), ("version",), False),
        ("openspec", shutil.which("openspec"), ("--version",), False),
        ("gga", shutil.which("gga"), ("version",), False),
        ("git", shutil.which("git"), ("--version",), False),
        ("bash", shutil.which("bash"), ("--version",), True),
        ("powershell", shutil.which("pwsh") or shutil.which("powershell"), None, False),
    ):
        if binary and flags:
            value = version(binary, flags)
        else:
            value = binary or "not found"
        ok = bool(binary) or not required
        problems += 0 if ok else 1
        line(name, value + ("" if binary else (" (required)" if required else " (optional)")), ok)

    print("guard hook")
    guard_ok = bool(shutil.which("bash")) and sys.version_info >= (3, 9)
    problems += 0 if guard_ok else 1
    line("runnable", "bash + python available" if guard_ok else "inactive: needs bash and Python 3.9+ (fails open)", guard_ok)

    print("installation (%s)" % config)
    manifest = agentcfg.read_json(os.path.join(config, agentcfg.MANIFEST_REL), None)
    if manifest:
        modified = [rel for rel, digest in manifest.get("files", {}).items()
                    if not os.path.isfile(os.path.join(config, rel)) or agentcfg.sha256(os.path.join(config, rel)) != digest]
        line("rules", "version %s, %d files%s" % (manifest.get("version"), len(manifest.get("files", {})),
                                                 ", modified/missing: %s" % ", ".join(modified) if modified else ""), not modified)
        line("permissions", "%d ask, %d deny (forge-owned)" % (len(manifest["permissions"].get("ask", [])), len(manifest["permissions"].get("deny", []))))
    else:
        line("rules", "not installed", False)
        problems += 1
    profile = os.path.join(config, agentcfg.PROFILE_REL)
    line("profile", "present" if os.path.isfile(profile) else "missing", os.path.isfile(profile))
    settings = agentcfg.read_json(os.path.join(config, agentcfg.SETTINGS_REL), {})
    enabled = (settings.get("enabledPlugins") or {}).get(agentcfg.PLUGIN_ID) if isinstance(settings, dict) else None
    line("plugin", "%s enabled in settings" % agentcfg.PLUGIN_ID if enabled else "not enabled in settings.json", bool(enabled))
    engram_entry = agentcfg.mcp_entry(config, "engram")
    if engram_entry:
        line("engram mcp", "%s %s" % (os.path.basename(engram_entry.get("command", "?")), " ".join(engram_entry.get("args", []))))
    else:
        line("engram mcp", "not registered (memory tools unavailable)", False)

    print("result: %s" % ("no blocking problems" if problems == 0 else "%d problem(s) - see [!!] lines" % problems))
    return 0


if __name__ == "__main__":
    sys.exit(main())
