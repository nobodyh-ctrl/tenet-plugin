# Spec Delta

## Purpose

Measure real token and tool usage from Claude Code session transcripts so token-efficiency changes are evaluated against a baseline instead of assumptions.

## ADDED Requirements

### Requirement: Metrics from real transcripts
`scripts/session_metrics.py` SHALL read Claude Code JSONL transcripts for a given project or session and report input, output and cache tokens as recorded, tool calls by tool, repeated reads of the same file, and subagent invocations.

#### Scenario: Fixture transcript
- **WHEN** the script runs on a synthetic transcript fixture with known usage values
- **THEN** it reports exactly those totals

### Requirement: No invented numbers
When usage fields are absent the script SHALL report them as unavailable and name the proxy used, and MUST NOT estimate tokens silently.

#### Scenario: Missing usage
- **WHEN** a transcript lacks usage data
- **THEN** the report marks tokens unavailable and shows tool-call counts as the proxy

### Requirement: Read-only and private
The script SHALL only read transcripts, print aggregate numbers without message content, and write nothing unless `--out` is given.

#### Scenario: No content leak
- **WHEN** the script runs on a fixture containing a fake secret in a message
- **THEN** the output does not contain that string
