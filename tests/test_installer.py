"""Tests for scripts/agentcfg.py and the installer wrappers. Everything runs in temp dirs.

forge:synthetic-fixture - paths and settings in this file are fake test data.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENTCFG = os.path.join(ROOT, "scripts", "agentcfg.py")
FAKE_CLAUDE = os.path.join(ROOT, "tests", "fixtures", "fake_claude.py")
RULES = os.path.join("rules", "forge")
FAKE_FILES = {"calls.log", "fake-claude-state.json"}


def make_dir_link(target, link):
    """Symlink, or an NTFS junction on Windows when symlinks need privileges."""
    try:
        os.symlink(target, link, target_is_directory=True)
        return True
    except (OSError, NotImplementedError):
        if os.name != "nt":
            return False
    result = subprocess.run(["cmd", "/c", "mklink", "/J", link, target], capture_output=True, text=True)
    return result.returncode == 0


def tree(root, skip_backups=True):
    """Map of relative path -> sha256 for every file, excluding backups and fake-CLI bookkeeping."""
    result = {}
    for folder, dirs, files in os.walk(root):
        if skip_backups:
            dirs[:] = [d for d in dirs if d != "backups"]
        for name in files:
            if name in FAKE_FILES:
                continue
            path = os.path.join(folder, name)
            with open(path, "rb") as handle:
                result[os.path.relpath(path, root).replace("\\", "/")] = hashlib.sha256(handle.read()).hexdigest()
    return result


class InstallerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="forge-installer-")
        self.config = os.path.join(self.tmp, "claude-config")
        os.makedirs(self.config)
        self.engram = os.path.join(self.tmp, "engram-bin", "engram.exe")
        os.makedirs(os.path.dirname(self.engram))
        with open(self.engram, "w") as handle:
            handle.write("fake engram")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def env(self, claude=FAKE_CLAUDE, engram=None):
        env = dict(os.environ)
        env.update({"CLAUDE_CONFIG_DIR": self.config, "FORGE_CLAUDE_BIN": claude, "FORGE_ENGRAM_BIN": engram or self.engram})
        return env

    def run_cfg(self, *args, claude=FAKE_CLAUDE, engram=None, config=None):
        command = [sys.executable, AGENTCFG] + list(args) + ["--config-dir", config or self.config]
        return subprocess.run(command, capture_output=True, text=True, env=self.env(claude, engram), timeout=120)

    def write(self, rel, text):
        path = os.path.join(self.config, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)
        return path

    def read(self, rel):
        with open(os.path.join(self.config, rel), encoding="utf-8") as handle:
            return handle.read()

    def calls(self):
        path = os.path.join(self.config, "calls.log")
        if not os.path.exists(path):
            return []
        with open(path, encoding="utf-8") as handle:
            return [json.loads(line) for line in handle]

    def backups(self):
        folder = os.path.join(self.config, "backups", "forge")
        return sorted(os.listdir(folder)) if os.path.isdir(folder) else []

    def seed_foreign(self):
        self.write("rules/my-team/style.md", "# foreign rule\n")
        self.write("skills/custom/SKILL.md", "---\nname: custom\n---\n")
        self.write("settings.json", json.dumps({"model": "opus", "permissions": {"allow": ["Bash(npm test)"], "ask": ["Bash(git push *)"]}}, indent=2))
        self.write(".claude.json", json.dumps({"mcpServers": {"github": {"command": "gh-mcp", "args": []}}, "numStartups": 3}))


class Version(unittest.TestCase):
    def test_version_matches_plugin_manifest(self):
        with open(os.path.join(ROOT, "plugins", "forge", ".claude-plugin", "plugin.json"), encoding="utf-8") as handle:
            expected = json.load(handle)["version"]
        result = subprocess.run([sys.executable, AGENTCFG, "--version"], capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "forge %s" % expected)


class DryRun(InstallerTest):
    def test_dry_run_writes_nothing_and_runs_no_cli(self):
        self.seed_foreign()
        before = tree(self.config, skip_backups=False)
        result = self.run_cfg("install", "--dry-run", "--with-permissions", "--with-plugin", "--with-engram")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("create   rules/forge/core.md", result.stdout)
        self.assertEqual(tree(self.config, skip_backups=False), before)
        self.assertEqual(self.calls(), [])

    def test_uninstall_dry_run_writes_nothing(self):
        self.assertEqual(self.run_cfg("install", "--with-permissions").returncode, 0)
        before = tree(self.config, skip_backups=False)
        result = self.run_cfg("uninstall", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("delete", result.stdout)
        self.assertEqual(tree(self.config, skip_backups=False), before)


class InstallBehavior(InstallerTest):
    def test_install_is_idempotent(self):
        self.seed_foreign()
        first = self.run_cfg("install", "--with-permissions", "--with-plugin", "--with-engram")
        self.assertEqual(first.returncode, 0, first.stderr)
        state = tree(self.config)
        backups = self.backups()
        calls = len(self.calls())
        second = self.run_cfg("install", "--with-permissions", "--with-plugin", "--with-engram")
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn("already up to date", second.stdout)
        self.assertEqual(tree(self.config), state)
        self.assertEqual(self.backups(), backups)
        new_calls = self.calls()[calls:]
        self.assertTrue(all(c[:2] == ["plugin", "list"] or c == ["--version"] for c in new_calls), new_calls)
        settings = json.loads(self.read("settings.json"))
        self.assertEqual(settings["permissions"]["ask"].count("Bash(git push *)"), 1)

    def test_profile_created_once_and_preserved(self):
        self.run_cfg("install")
        profile = os.path.join(RULES, "profile.md")
        self.write(profile, "# my edited profile\n")
        self.run_cfg("install")
        self.assertEqual(self.read(profile), "# my edited profile\n")
        self.run_cfg("uninstall")
        self.assertEqual(self.read(profile), "# my edited profile\n")
        self.run_cfg("install")
        self.run_cfg("uninstall", "--purge")
        self.assertFalse(os.path.exists(os.path.join(self.config, profile)))

    def test_uninstall_preserves_foreign_configuration(self):
        self.seed_foreign()
        foreign = {k: v for k, v in tree(self.config).items() if k not in ("settings.json", ".claude.json")}
        settings_before = self.read("settings.json")
        self.assertEqual(self.run_cfg("install", "--with-permissions", "--with-plugin", "--with-engram").returncode, 0)
        self.assertIn("engram", json.loads(self.read(".claude.json"))["mcpServers"])
        result = self.run_cfg("uninstall")
        self.assertEqual(result.returncode, 0, result.stderr)
        after = tree(self.config)
        for rel, digest in foreign.items():
            self.assertEqual(after.get(rel), digest, rel)
        self.assertEqual(json.loads(self.read("settings.json")), json.loads(settings_before))
        claude_json = json.loads(self.read(".claude.json"))
        self.assertEqual(set(claude_json["mcpServers"]), {"github"})
        self.assertEqual(claude_json["numStartups"], 3)
        self.assertFalse(any(k.startswith("rules/forge/") and not k.endswith("profile.md") for k in after))
        self.assertIn(["plugin", "uninstall", "forge@forge", "--scope", "user"], self.calls())

    def test_restore_is_byte_identical(self):
        self.seed_foreign()
        with open(os.path.join(self.config, "settings.json"), "rb") as handle:
            original = handle.read()
        self.run_cfg("install", "--with-permissions")
        backup_id = self.backups()[0]
        self.assertNotEqual(self.read("settings.json").encode(), original)
        result = self.run_cfg("restore", backup_id)
        self.assertEqual(result.returncode, 0, result.stderr)
        with open(os.path.join(self.config, "settings.json"), "rb") as handle:
            self.assertEqual(handle.read(), original)
        self.assertFalse(os.path.exists(os.path.join(self.config, RULES, "core.md")))
        self.assertIn("previous state saved as backup id", result.stdout)

    def test_modified_owned_file_is_backed_up_before_removal(self):
        self.run_cfg("install")
        self.write(os.path.join(RULES, "core.md"), "# customized\n")
        self.run_cfg("uninstall")
        latest = self.backups()[-1]
        saved = os.path.join(self.config, "backups", "forge", latest, "files", RULES, "core.md")
        with open(saved, encoding="utf-8") as handle:
            self.assertEqual(handle.read(), "# customized\n")


class Safety(InstallerTest):
    def test_config_dir_is_a_file(self):
        target = os.path.join(self.tmp, "a-file")
        with open(target, "w") as handle:
            handle.write("x")
        result = self.run_cfg("install", config=target)
        self.assertEqual(result.returncode, 1)
        self.assertIn("not a directory", result.stderr)

    def test_config_dir_parent_missing(self):
        result = self.run_cfg("install", config=os.path.join(self.tmp, "missing", "deeper"))
        self.assertEqual(result.returncode, 1)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "missing")))

    def test_symlinked_config_dir_refused(self):
        link = os.path.join(self.tmp, "linked-config")
        if not make_dir_link(self.config, link):
            self.skipTest("cannot create symlinks or junctions here")
        result = self.run_cfg("install", config=link)
        self.assertEqual(result.returncode, 1)
        self.assertIn("symlink or junction", result.stderr)
        self.assertEqual(tree(self.config), {})

    def test_symlinked_rules_dir_refused(self):
        outside = os.path.join(self.tmp, "outside")
        os.makedirs(outside)
        os.makedirs(os.path.join(self.config, "rules"))
        if not make_dir_link(outside, os.path.join(self.config, RULES)):
            self.skipTest("cannot create symlinks or junctions here")
        result = self.run_cfg("install")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(os.listdir(outside), [])

    def test_foreign_file_conflict_aborts(self):
        self.write(os.path.join(RULES, "core.md"), "# someone else's core\n")
        before = tree(self.config)
        result = self.run_cfg("install")
        self.assertEqual(result.returncode, 1)
        self.assertIn("not owned", result.stderr)
        self.assertEqual(tree(self.config), before)

    def test_corrupt_settings_aborts_before_writing(self):
        self.write("settings.json", "{ not json")
        result = self.run_cfg("install", "--with-permissions")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(sorted(tree(self.config)), ["settings.json"])

    def test_restore_unknown_backup(self):
        result = self.run_cfg("restore", "20000101-000000-000000")
        self.assertEqual(result.returncode, 1)
        self.assertIn("not found", result.stderr)


class ExternalTools(InstallerTest):
    def test_missing_claude_prints_manual_commands(self):
        result = self.run_cfg("install", "--with-plugin", "--with-engram", claude="none")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("claude plugin install forge@forge --scope user", result.stdout)
        self.assertIn("claude mcp add --scope user engram", result.stdout)
        self.assertTrue(os.path.exists(os.path.join(self.config, RULES, "core.md")))
        manifest = json.loads(self.read("forge/manifest.json"))
        self.assertFalse(manifest["plugin"])
        self.assertFalse(manifest["engram_mcp"])

    def test_missing_engram_reported(self):
        result = self.run_cfg("install", "--with-engram", engram="none")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("engram binary not found", result.stdout)
        self.assertEqual([c for c in self.calls() if c[:1] == ["mcp"]], [])

    def test_engram_fresh_wiring_exact_command(self):
        self.run_cfg("install", "--with-engram")
        self.assertIn(["mcp", "add", "--scope", "user", "engram", "--", self.engram, "mcp", "--tools=agent"], self.calls())
        self.assertTrue(json.loads(self.read("forge/manifest.json"))["engram_mcp"])
        self.run_cfg("uninstall")
        self.assertIn(["mcp", "remove", "engram", "--scope", "user"], self.calls())

    def test_engram_conflict_left_untouched(self):
        self.write(".claude.json", json.dumps({"mcpServers": {"engram": {"command": "/opt/other/engram", "args": ["mcp"]}}}))
        before = self.read(".claude.json")
        result = self.run_cfg("install", "--with-engram")
        self.assertIn("CONFLICT", result.stdout)
        self.assertEqual([c for c in self.calls() if c[:1] == ["mcp"]], [])
        self.assertFalse(json.loads(self.read("forge/manifest.json"))["engram_mcp"])
        self.run_cfg("uninstall")
        self.assertEqual(self.read(".claude.json"), before)


@unittest.skipUnless(shutil.which("bash"), "bash not available")
class BashWrapper(InstallerTest):
    def test_bash_wrapper_dry_run(self):
        script = os.path.join(ROOT, "installers", "install.sh")
        result = subprocess.run(["bash", script, "--dry-run", "--config-dir", self.config], capture_output=True, text=True,
                                env=self.env(), timeout=120)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("install plan (dry run)", result.stdout)
        self.assertEqual(tree(self.config), {})

    def test_bash_wrapper_rejects_unknown_option(self):
        script = os.path.join(ROOT, "installers", "install.sh")
        result = subprocess.run(["bash", script, "--bogus"], capture_output=True, text=True, env=self.env(), timeout=60)
        self.assertEqual(result.returncode, 2)


@unittest.skipUnless(os.name == "nt" and shutil.which("powershell"), "Windows PowerShell not available")
class PowerShellWrapper(InstallerTest):
    def test_powershell_wrapper_dry_run(self):
        script = os.path.join(ROOT, "installers", "install.ps1")
        result = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script, "-DryRun",
                                 "-ConfigDir", self.config], capture_output=True, text=True, env=self.env(), timeout=120)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("install plan (dry run)", result.stdout)
        self.assertEqual(tree(self.config), {})


if __name__ == "__main__":
    unittest.main()
