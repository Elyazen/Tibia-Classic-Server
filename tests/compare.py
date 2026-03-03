#!/usr/bin/env python3
import json
import sys
import os
import re

def normalize_line(line):
    """Normalize timestamp, pid, tid, and absolute paths to make logs deterministic."""
    line = re.sub(r'Pid=\d+', 'Pid=<PID>', line)
    line = re.sub(r'Tid=\d+', 'Tid=<TID>', line)
    line = re.sub(r'Socket \d+', 'Socket <FD>', line)
    line = re.sub(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', '<TIMESTAMP>', line)
    line = re.sub(r'\d+ \w+ \d{4} \d{2}:\d{2}:\d{2}', '<TIMESTAMP>', line)
    line = re.sub(r'/opt/tibia/[^\s]+', '<PATH>', line)
    line = re.sub(r'/tmp/[^\s]+', '<TMPDIR>', line)
    return line

def compare_logs(baseline_file, target_file):
    with open(baseline_file, 'r') as f:
        baseline_lines = [normalize_line(line) for line in f.readlines()]
    with open(target_file, 'r') as f:
        target_lines = [normalize_line(line) for line in f.readlines()]

    diffs = []
    max_len = max(len(baseline_lines), len(target_lines))

    for i in range(max_len):
        b = baseline_lines[i] if i < len(baseline_lines) else "<MISSING>"
        t = target_lines[i] if i < len(target_lines) else "<MISSING>"
        if b != t:
            diffs.append(f"Line {i+1}:\n- {b.strip()}\n+ {t.strip()}")

    return diffs

def normalize_trace_event(event):
    """Normalizes a single trace event dictionary by masking dynamic fields."""
    normalized = dict(event)
    # Mask out fields that are environment or time-dependent to prevent flakiness
    for key in ['timestamp', 'fd', 'pid', 'time']:
        if key in normalized:
            normalized[key] = f"<{key.upper()}>"
    return normalized

def compare_traces(baseline_file, target_file):
    with open(baseline_file, 'r') as f:
        baseline_trace = json.load(f)
    with open(target_file, 'r') as f:
        target_trace = json.load(f)

    diffs = []
    if len(baseline_trace) != len(target_trace):
        diffs.append(f"Event count mismatch: {len(baseline_trace)} != {len(target_trace)}")

    for i in range(min(len(baseline_trace), len(target_trace))):
        b = normalize_trace_event(baseline_trace[i])
        t = normalize_trace_event(target_trace[i])

        if b != t:
            diffs.append(f"Event {i} mismatch:\n- {b}\n+ {t}")

    return diffs

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <baseline_dir> <target_dir>")
        sys.exit(1)

    baseline_dir = sys.argv[1]
    target_dir = sys.argv[2]

    failures = 0

    baseline_log = os.path.join(baseline_dir, "startup.log")
    target_log = os.path.join(target_dir, "startup.log")

    if os.path.exists(baseline_log) and os.path.exists(target_log):
        print("Comparing logs...")
        diffs = compare_logs(baseline_log, target_log)
        if diffs:
            failures += 1
            print("LOG DIFFERENCES FOUND:")
            for d in diffs: print(d)
        else:
            print("Logs match.")
    else:
        print(f"Skipping log comparison (files missing: {baseline_log} or {target_log})")

    baseline_trace = os.path.join(baseline_dir, "trace.json")
    target_trace = os.path.join(target_dir, "trace.json")

    if os.path.exists(baseline_trace) and os.path.exists(target_trace):
        print("Comparing traces...")
        diffs = compare_traces(baseline_trace, target_trace)
        if diffs:
            failures += 1
            print("TRACE DIFFERENCES FOUND:")
            for d in diffs: print(d)
        else:
            print("Traces match.")

    if failures > 0:
        print("Comparison failed.")
        sys.exit(1)
    else:
        print("All comparisons passed.")
        sys.exit(0)
