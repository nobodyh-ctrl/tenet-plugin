#!/usr/bin/env python3
"""Aggregate token and tool usage from Claude Code session transcripts (read-only).

Reads `<config>/projects/<project>/*.jsonl` (and subagent transcripts in session subfolders),
reporting recorded token usage, tool calls, repeated file reads and subagent invocations.
Prints aggregates only - never message content or file paths. Writes nothing unless --out is given.

Usage:
  python scripts/session_metrics.py                     # current directory's project
  python scripts/session_metrics.py --session FILE.jsonl
  python scripts/session_metrics.py --project-dir DIR [--json] [--out FILE]
"""
import argparse
import collections
import glob
import json
import os
import re
import sys

USAGE_FIELDS = ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
SUBAGENT_TOOLS = {"Agent", "Task"}


def project_dir_for(cwd, config):
    # Claude Code names project folders after the cwd with every non-alphanumeric character replaced by "-".
    return os.path.join(config, "projects", re.sub(r"[^A-Za-z0-9]", "-", cwd))


def transcript_files(project_dir=None, session=None):
    if session:
        files = [session]
        stem = os.path.splitext(session)[0]
        files += sorted(glob.glob(os.path.join(stem, "**", "*.jsonl"), recursive=True))
        return files
    return sorted(glob.glob(os.path.join(project_dir, "**", "*.jsonl"), recursive=True))


def analyze(files):
    usage = collections.Counter()
    usage_messages = set()
    tool_calls = collections.Counter()
    tool_ids = set()
    reads = collections.Counter()
    subagents = collections.Counter()
    sessions = set()
    sidechain_messages = 0
    assistant_messages = set()
    for path in files:
        with open(path, encoding="utf-8") as handle:
            for line in handle:
                try:
                    record = json.loads(line)
                except ValueError:
                    continue
                if record.get("type") != "assistant":
                    continue
                message = record.get("message") or {}
                message_id = message.get("id") or record.get("uuid")
                sessions.add(record.get("sessionId"))
                if record.get("isSidechain"):
                    sidechain_messages += 1
                assistant_messages.add(message_id)
                # Streaming writes one line per content block with the same message id and usage; count once.
                if message.get("usage") and message_id not in usage_messages:
                    usage_messages.add(message_id)
                    for field in USAGE_FIELDS:
                        value = message["usage"].get(field)
                        if isinstance(value, int):
                            usage[field] += value
                for block in message.get("content") or []:
                    if not isinstance(block, dict) or block.get("type") != "tool_use":
                        continue
                    if block.get("id") in tool_ids:
                        continue
                    tool_ids.add(block.get("id"))
                    name = block.get("name", "unknown")
                    tool_calls[name] += 1
                    tool_input = block.get("input") or {}
                    if name == "Read" and tool_input.get("file_path"):
                        reads[os.path.normcase(tool_input["file_path"])] += 1
                    if name in SUBAGENT_TOOLS:
                        subagents[tool_input.get("subagent_type") or "general-purpose"] += 1
    repeated = {path: count for path, count in reads.items() if count > 1}
    return {
        "transcripts": len(files),
        "sessions": len(sessions - {None}),
        "assistant_messages": len(assistant_messages),
        "sidechain_messages": sidechain_messages,
        "tokens": dict(usage) if usage_messages else None,
        "tokens_source": "recorded message.usage" if usage_messages else "unavailable; proxy: tool_calls_total",
        "tool_calls_total": sum(tool_calls.values()),
        "tool_calls": dict(tool_calls.most_common()),
        "files_read": len(reads),
        "files_read_repeatedly": len(repeated),
        "redundant_reads": sum(count - 1 for count in repeated.values()),
        "subagent_invocations": sum(subagents.values()),
        "subagents_by_type": dict(subagents),
    }


def render(report):
    lines = ["transcripts: %(transcripts)d  sessions: %(sessions)d  assistant messages: %(assistant_messages)d" % report]
    if report["tokens"]:
        tokens = report["tokens"]
        lines.append("tokens (%s):" % report["tokens_source"])
        for field in USAGE_FIELDS:
            lines.append("  %-28s %12d" % (field, tokens.get(field, 0)))
    else:
        lines.append("tokens: %s" % report["tokens_source"])
    lines.append("tool calls: %d" % report["tool_calls_total"])
    for name, count in report["tool_calls"].items():
        lines.append("  %-28s %12d" % (name, count))
    lines.append("files read: %(files_read)d  read more than once: %(files_read_repeatedly)d  redundant reads: %(redundant_reads)d" % report)
    lines.append("subagent invocations: %d %s" % (report["subagent_invocations"], report["subagents_by_type"] or ""))
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Aggregate Claude Code session usage (read-only).")
    parser.add_argument("--config-dir", default=os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(os.path.expanduser("~"), ".claude"))
    parser.add_argument("--project-dir", help="transcript folder (default: derived from the current directory)")
    parser.add_argument("--session", help="a single session .jsonl file")
    parser.add_argument("--json", action="store_true", help="print JSON instead of text")
    parser.add_argument("--out", help="also write the JSON report to this file")
    args = parser.parse_args(argv)
    project_dir = args.project_dir or project_dir_for(os.getcwd(), args.config_dir)
    files = transcript_files(project_dir, args.session)
    if not files:
        print("no transcripts found in %s" % (args.session or project_dir), file=sys.stderr)
        return 1
    report = analyze(files)
    print(json.dumps(report, indent=2) if args.json else render(report))
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
