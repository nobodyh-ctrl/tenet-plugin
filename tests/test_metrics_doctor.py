"""Tests for scripts/session_metrics.py and scripts/doctor.py.

tenet:synthetic-fixture - transcripts and secrets in this file are fake test data.
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
METRICS = os.path.join(ROOT, "scripts", "session_metrics.py")
DOCTOR = os.path.join(ROOT, "scripts", "doctor.py")
FAKE_SECRET = "sk-ant-FAKE-SECRET-should-never-be-printed-123"


def assistant(message_id, usage=None, tools=(), sidechain=False):
    content = [{"type": "text", "text": "thinking about " + FAKE_SECRET}]
    content += [{"type": "tool_use", "id": tid, "name": name, "input": tool_input} for tid, name, tool_input in tools]
    message = {"id": message_id, "role": "assistant", "content": content}
    if usage is not None:
        message["usage"] = usage
    return {"type": "assistant", "sessionId": "s1", "isSidechain": sidechain, "message": message}


class Metrics(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="tenet-metrics-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def transcript(self, records, name="session.jsonl"):
        path = os.path.join(self.tmp, name)
        with open(path, "w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record) + "\n")
        return path

    def run_metrics(self, *args):
        return subprocess.run([sys.executable, METRICS] + list(args), capture_output=True, text=True, timeout=60)

    def test_exact_totals(self):
        usage1 = {"input_tokens": 10, "output_tokens": 100, "cache_creation_input_tokens": 1000, "cache_read_input_tokens": 5000}
        usage2 = {"input_tokens": 3, "output_tokens": 50, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 6000}
        records = [
            {"type": "user", "message": {"content": "hello " + FAKE_SECRET}},
            assistant("m1", usage1, [("t1", "Read", {"file_path": "a.py"}), ("t2", "Grep", {"pattern": "x"})]),
            assistant("m1", usage1, [("t1", "Read", {"file_path": "a.py"})]),  # streamed duplicate line
            assistant("m2", usage2, [("t3", "Read", {"file_path": "a.py"}), ("t4", "Agent", {"subagent_type": "explorer"})]),
            assistant("m3", None, [("t5", "Read", {"file_path": "b.py"})], sidechain=True),
        ]
        path = self.transcript(records)
        result = self.run_metrics("--session", path, "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["tokens"], {"input_tokens": 13, "output_tokens": 150, "cache_creation_input_tokens": 1000,
                                            "cache_read_input_tokens": 11000})
        self.assertEqual(report["tool_calls"], {"Read": 3, "Grep": 1, "Agent": 1})
        self.assertEqual((report["files_read"], report["files_read_repeatedly"], report["redundant_reads"]), (2, 1, 1))
        self.assertEqual(report["subagents_by_type"], {"explorer": 1})
        self.assertEqual(report["sidechain_messages"], 1)

    def test_missing_usage_reports_proxy(self):
        path = self.transcript([assistant("m1", None, [("t1", "Bash", {"command": "ls"})])])
        report = json.loads(self.run_metrics("--session", path, "--json").stdout)
        self.assertIsNone(report["tokens"])
        self.assertIn("unavailable", report["tokens_source"])
        self.assertEqual(report["tool_calls_total"], 1)

    def test_no_content_or_paths_leak(self):
        path = self.transcript([assistant("m1", {"input_tokens": 1, "output_tokens": 1}, [("t1", "Read", {"file_path": "secret-dir/x.py"})])])
        for flags in ([], ["--json"]):
            result = self.run_metrics("--session", path, *flags)
            self.assertNotIn(FAKE_SECRET, result.stdout + result.stderr)
            self.assertNotIn("secret-dir", result.stdout)

    def test_read_only_without_out(self):
        path = self.transcript([assistant("m1", {"input_tokens": 1, "output_tokens": 1})])
        before = sorted(os.listdir(self.tmp))
        self.run_metrics("--session", path)
        self.assertEqual(sorted(os.listdir(self.tmp)), before)


class Doctor(unittest.TestCase):
    def test_doctor_is_read_only(self):
        tmp = tempfile.mkdtemp(prefix="tenet-doctor-")
        try:
            config = os.path.join(tmp, "cfg")
            os.makedirs(os.path.join(config, "rules", "x"))
            with open(os.path.join(config, "settings.json"), "w") as handle:
                handle.write('{"model": "opus"}')
            with open(os.path.join(config, "rules", "x", "a.md"), "w") as handle:
                handle.write("# a")

            def snapshot():
                result = {}
                for folder, _, files in os.walk(tmp):
                    for name in files:
                        with open(os.path.join(folder, name), "rb") as handle:
                            result[os.path.join(folder, name)] = hashlib.sha256(handle.read()).hexdigest()
                return result

            before = snapshot()
            env = dict(os.environ, CLAUDE_CONFIG_DIR=config)
            result = subprocess.run([sys.executable, DOCTOR, "--config-dir", config], capture_output=True, text=True, env=env, timeout=120)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("installation", result.stdout)
            self.assertIn("not installed", result.stdout)
            self.assertEqual(snapshot(), before)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
