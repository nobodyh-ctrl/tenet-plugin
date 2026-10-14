"""Tests for scripts/validate.py.

forge:synthetic-fixture - secrets and paths in this file are fake test data.
"""
import importlib.util
import json
import os
import re
import shutil
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("forge_validate", os.path.join(ROOT, "scripts", "validate.py"))
validate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate)

IGNORE = shutil.ignore_patterns(".git", "local", "__pycache__", "node_modules")


class RepoCopy(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="forge-validate-")
        self.root = os.path.join(self.tmp, "repo")
        shutil.copytree(ROOT, self.root, ignore=IGNORE)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def path(self, *parts):
        return os.path.join(self.root, *parts)

    def edit(self, rel, transform):
        path = self.path(*rel.split("/"))
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(transform(text))

    def errors(self):
        return validate.run(self.root).errors

    def assertError(self, fragment):
        errors = self.errors()
        self.assertTrue(any(fragment in e for e in errors), "expected %r in %s" % (fragment, errors))


class ValidRepository(RepoCopy):
    def test_copy_of_repository_is_valid(self):
        self.assertEqual(self.errors(), [])


class BrokenCopies(RepoCopy):
    def test_skill_without_description(self):
        self.edit("plugins/forge/skills/plan-work/SKILL.md", lambda t: re.sub(r"^description:.*\n", "", t, flags=re.M))
        self.assertError("plugins/forge/skills/plan-work/SKILL.md: missing description")

    def test_skill_reading_plugin_without_preapproval(self):
        self.edit("plugins/forge/skills/devops-iac/SKILL.md", lambda t: t.replace("allowed-tools: Read(${CLAUDE_PLUGIN_ROOT}/**)\n", ""))
        self.assertError("does not pre-approve")

    def test_skill_with_broader_preapproval(self):
        self.edit("plugins/forge/skills/plan-work/SKILL.md", lambda t: t.replace("allowed-tools: Read(${CLAUDE_PLUGIN_ROOT}/**)", "allowed-tools: Bash, Read"))
        self.assertError("allowed-tools may only be")

    def test_version_skill_must_not_auto_invoke(self):
        self.edit("plugins/forge/skills/version/SKILL.md", lambda t: t.replace("disable-model-invocation: true\n", ""))
        self.assertError("version skill must set disable-model-invocation: true")

    def test_release_notes_required_for_current_version(self):
        os.remove(self.path("docs", "releases", "v0.1.0-beta.1.md"))
        self.assertError("missing release notes for version 0.1.0-beta.1")

    def test_changelog_section_required(self):
        self.edit("CHANGELOG.md", lambda t: t.replace("## [0.1.0-beta.1]", "## [0.0.9]"))
        self.assertError("missing '## [0.1.0-beta.1]' section")

    def test_marketplace_name_mismatch(self):
        def rename(text):
            data = json.loads(text)
            data["plugins"][0]["name"] = "other-name"
            return json.dumps(data)
        self.edit(".claude-plugin/marketplace.json", rename)
        self.assertError("differs from marketplace entry")

    def test_parent_traversal_in_source(self):
        def traverse(text):
            data = json.loads(text)
            data["plugins"][0]["source"] = "./plugins/../plugins/forge"
            return json.dumps(data)
        self.edit(".claude-plugin/marketplace.json", traverse)
        self.assertError("contains '..'")

    def test_non_implementer_with_edit(self):
        self.edit("plugins/forge/agents/reviewer.md", lambda t: t.replace("tools: Read, Grep, Glob, Bash", "tools: Read, Grep, Glob, Bash, Edit"))
        self.assertError("only implementer may have write tools")

    def test_ignored_agent_field(self):
        self.edit("plugins/forge/agents/tutor.md", lambda t: t.replace("model: inherit", "model: inherit\npermissionMode: plan"))
        self.assertError("'permissionMode' is ignored for plugin agents")

    def test_oversize_rules(self):
        self.edit("global-config/rules/tokens.md", lambda t: t + "\n".join("- filler %d" % i for i in range(120)) + "\n")
        self.assertError("budget is 120")

    def test_release_without_stop(self):
        self.edit("plugins/forge/skills/release/SKILL.md", lambda t: t.replace("STOP", "Continue"))
        self.assertError("release/SKILL.md: missing required content")

    def test_openspec_reference_removed(self):
        self.edit("plugins/forge/skills/verify-changes/SKILL.md", lambda t: t.replace("openspec validate", "spec check"))
        self.assertError("must delegate to OpenSpec")

    def test_unmarked_standard(self):
        self.edit("plugins/forge/manual/core/quality.md", lambda t: t.replace("## Standards\n\n", "## Standards\n\n- Write good code.\n", 1))
        self.assertError("standard without MUST/SHOULD/EXPERIMENTAL marker")

    def test_provider_term_in_principles(self):
        self.edit("plugins/forge/manual/core/architecture.md", lambda t: t + "\nUse AWS Lambda.\n")
        self.assertError("provider-specific term outside providers/")

    def test_catalog_entry_missing_field(self):
        self.edit("plugins/forge/manual/catalog/technologies.md", lambda t: t.replace("- **Cost:** None.\n", "", 1))
        self.assertError("missing field 'Cost'")

    def test_unknown_engram_tool(self):
        self.edit("global-config/rules/memory.md", lambda t: t + "Call `mem_teleport` first.\n")
        self.assertError("unknown Engram tool mem_teleport")

    def test_plugin_root_claude_md(self):
        with open(self.path("plugins", "forge", "CLAUDE.md"), "w", encoding="utf-8") as handle:
            handle.write("# not loaded\n")
        self.assertError("must not contain CLAUDE.md")

    def test_ci_with_secrets(self):
        os.makedirs(self.path(".github", "workflows"), exist_ok=True)
        with open(self.path(".github", "workflows", "ci.yml"), "w", encoding="utf-8") as handle:
            handle.write("env:\n  TOKEN: ${{ secrets.TOKEN }}\n")
        self.assertError("CI must not reference secrets")

    def test_private_term_from_local_list(self):
        os.makedirs(self.path("local"), exist_ok=True)
        with open(self.path("local", "private-terms.txt"), "w", encoding="utf-8") as handle:
            handle.write("# terms\nAcmeSecretApp\n")
        with open(self.path("docs", "leak.md"), "w", encoding="utf-8") as handle:
            handle.write("Notes about AcmeSecretApp roadmap.\n")
        self.assertError("docs/leak.md: line 1: possible private-term")


class ContinuousIntegration(unittest.TestCase):
    def test_workflow_is_credential_free_and_complete(self):
        with open(os.path.join(ROOT, ".github", "workflows", "ci.yml"), encoding="utf-8") as handle:
            workflow = handle.read()
        self.assertNotIn("secrets.", workflow)
        for required in ("ubuntu-latest", "windows-latest", "scripts/validate.py", "unittest discover",
                         "shellcheck", "claude plugin validate", "openspec validate --all --strict"):
            self.assertIn(required, workflow)
        self.assertRegex(workflow, r"permissions:\s*\n\s*contents: read")


class SecretScanner(unittest.TestCase):
    def kinds(self, text, terms=()):
        return {kind for kind, _ in validate.scan_text(text, terms)}

    def test_detects_secrets(self):
        self.assertIn("private-key", self.kinds("-----BEGIN PRIVATE KEY-----"))
        self.assertIn("private-key", self.kinds("-----BEGIN OPENSSH PRIVATE KEY-----"))
        self.assertIn("aws-access-key", self.kinds("key = AKIAABCDEFGHIJKLMNOP"))
        self.assertIn("github-token", self.kinds("ghp_" + "a" * 36))
        self.assertIn("anthropic-key", self.kinds("sk-ant-api03-abcdefghijklmnopqrstuvwxyz"))
        self.assertIn("windows-user-path", self.kinds(r"C:\Users\jdoe\project"))
        self.assertIn("unix-home-path", self.kinds("/home/jdoe/project"))
        self.assertIn("private-term", self.kinds("about Zephyrine", ["Zephyrine"]))

    def test_ignores_placeholders(self):
        self.assertEqual(self.kinds(r"C:\Users\<name>\x and /home/<name>/x and C:\Users\Public\x"), set())
        self.assertEqual(self.kinds("~/.claude/rules and ${HOME}/x"), set())


if __name__ == "__main__":
    unittest.main()
