"""Tests for scripts/build_release.py and .github/workflows/release.yml."""
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "scripts", "build_release.py")
spec = importlib.util.spec_from_file_location("build_release", SCRIPT)
build_release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_release)
VERSION = build_release.plugin_version()


class Assets(unittest.TestCase):
    def setUp(self):
        self.out = tempfile.mkdtemp(prefix="tenet-release-")

    def tearDown(self):
        shutil.rmtree(self.out, ignore_errors=True)

    def run_script(self, *args):
        return subprocess.run([sys.executable, SCRIPT, "--out", self.out] + list(args), capture_output=True, text=True, timeout=300)

    def test_builds_assets_with_matching_checksums(self):
        result = self.run_script("--tag", "tenet--v" + VERSION)
        self.assertEqual(result.returncode, 0, result.stderr)
        plugin_zip = "tenet-plugin-%s.zip" % VERSION
        full_zip = "tenet-%s.zip" % VERSION
        self.assertEqual(sorted(os.listdir(self.out)), sorted([plugin_zip, full_zip, "checksums.txt"]))
        with open(os.path.join(self.out, "checksums.txt"), encoding="utf-8") as handle:
            listed = dict(reversed(line.split("  ")) for line in handle.read().splitlines())
        for name in (plugin_zip, full_zip):
            with open(os.path.join(self.out, name), "rb") as handle:
                self.assertEqual(listed[name], hashlib.sha256(handle.read()).hexdigest())

    def test_plugin_zip_is_loadable_layout(self):
        self.assertEqual(self.run_script().returncode, 0)
        with zipfile.ZipFile(os.path.join(self.out, "tenet-plugin-%s.zip" % VERSION)) as archive:
            names = archive.namelist()
            self.assertIn(".claude-plugin/plugin.json", names)
            self.assertIn("hooks/hooks.json", names)
            self.assertIn("skills/version/SKILL.md", names)
            self.assertFalse(any("__pycache__" in n or n.startswith("plugins/") for n in names))
            self.assertEqual(json.loads(archive.read(".claude-plugin/plugin.json"))["version"], VERSION)

    def test_full_zip_contains_installers_under_prefix(self):
        self.assertEqual(self.run_script().returncode, 0)
        with zipfile.ZipFile(os.path.join(self.out, "tenet-%s.zip" % VERSION)) as archive:
            names = archive.namelist()
        prefix = "tenet-%s/" % VERSION
        self.assertTrue(all(n.startswith(prefix) for n in names))
        for required in ("installers/install.ps1", "installers/install.sh", "scripts/agentcfg.py", "README.md"):
            self.assertIn(prefix + required, names)
        self.assertFalse(any("/local/" in n for n in names))

    def test_deterministic(self):
        self.assertEqual(self.run_script().returncode, 0)
        with open(os.path.join(self.out, "checksums.txt"), encoding="utf-8") as handle:
            first = handle.read()
        self.assertEqual(self.run_script().returncode, 0)
        with open(os.path.join(self.out, "checksums.txt"), encoding="utf-8") as handle:
            self.assertEqual(handle.read(), first)

    def test_tag_mismatch_rejected_without_writing(self):
        result = self.run_script("--tag", "tenet--v9.9.9")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not match", result.stderr)
        self.assertEqual(os.listdir(self.out), [])


class Prerelease(unittest.TestCase):
    def test_semver_prerelease_detection(self):
        self.assertTrue(build_release.is_prerelease("0.1.0-beta.1"))
        self.assertTrue(build_release.is_prerelease("1.0.0-rc.1+build.5"))
        self.assertFalse(build_release.is_prerelease("1.0.0"))
        self.assertFalse(build_release.is_prerelease("1.0.0+build.5"))

    def test_print_prerelease_for_current_version(self):
        result = subprocess.run([sys.executable, SCRIPT, "--print-prerelease"], capture_output=True, text=True, timeout=60)
        self.assertEqual(result.stdout.strip(), "true" if "-" in VERSION else "false")


class WorkflowContract(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, ".github", "workflows", "release.yml"), encoding="utf-8") as handle:
            self.text = handle.read()

    def test_trigger_only_on_tenet_tags(self):
        self.assertRegex(self.text, r"on:\s*\n\s*push:\s*\n\s*tags:\s*\n\s*- \"tenet--v\*\"")
        self.assertNotIn("branches:", self.text)
        self.assertNotIn("pull_request", self.text)

    def test_checks_run_before_build_and_publish(self):
        order = [self.text.index(step) for step in ("scripts/validate.py", "unittest discover", "scripts/build_release.py", "gh release create")]
        self.assertEqual(order, sorted(order))
        self.assertIn("--notes-file docs/releases/", self.text)
        self.assertIn("--print-prerelease", self.text)

    def test_only_github_token(self):
        self.assertEqual(set(re.findall(r"secrets\.(\w+)", self.text)), {"GITHUB_TOKEN"})
        self.assertIn("contents: write", self.text)


if __name__ == "__main__":
    unittest.main()
