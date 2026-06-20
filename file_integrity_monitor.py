#!/usr/bin/env python3
"""
File Integrity Monitoring System

Features:
- Monitors folder "monitor_me"
- Creates a SHA-256 baseline saved to baseline.json
- Simple menu: 1=create baseline, 2=start monitoring
- Polls every 2 seconds and prints clear alerts for new/modified/deleted files

Only uses built-in libraries: os, hashlib, json, time
"""

import os
import hashlib
import json
import time

MONITOR_DIR = "monitor_me"
BASELINE_FILE = "baseline.json"
SAMPLE_FILE = "sample.txt"
POLL_INTERVAL = 2


def ensure_monitor_dir():
    """Create the monitor directory and add a sample file if needed."""
    os.makedirs(MONITOR_DIR, exist_ok=True)
    sample_path = os.path.join(MONITOR_DIR, SAMPLE_FILE)
    if not os.path.exists(sample_path):
        with open(sample_path, "w", encoding="utf-8") as f:
            f.write("This is a sample file for the File Integrity Monitoring mini-project.\n")


def compute_sha256(path):
    """Compute SHA-256 for a file, returning hex digest."""
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except (OSError, PermissionError):
        return None


def scan_directory():
    """Scan MONITOR_DIR and return a dict of relative_path -> sha256."""
    result = {}
    for root, dirs, files in os.walk(MONITOR_DIR):
        for name in files:
            full_path = os.path.join(root, name)
            rel_path = os.path.relpath(full_path, MONITOR_DIR)
            digest = compute_sha256(full_path)
            if digest is not None:
                # Normalize path to use forward slashes for JSON readability
                norm_path = rel_path.replace(os.path.sep, "/")
                result[norm_path] = digest
    return result


def save_baseline(baseline):
    with open(BASELINE_FILE, "w", encoding="utf-8") as f:
        json.dump(baseline, f, indent=2)


def load_baseline():
    if not os.path.exists(BASELINE_FILE):
        return {}
    try:
        with open(BASELINE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def create_baseline():
    ensure_monitor_dir()
    print("Creating baseline... Scanning files in '{}'".format(MONITOR_DIR))
    baseline = scan_directory()
    save_baseline(baseline)
    print("Baseline saved to '{}'. {} files recorded.".format(BASELINE_FILE, len(baseline)))


def timestamp():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def monitor():
    ensure_monitor_dir()
    baseline = load_baseline()
    if not baseline:
        print("No baseline found. Creating baseline now.")
        baseline = scan_directory()
        save_baseline(baseline)
        print("Baseline created with {} files.".format(len(baseline)))

    print("Starting monitoring on '{}' (poll every {}s). Press Ctrl-C to stop.".format(MONITOR_DIR, POLL_INTERVAL))

    alerted_new = set()
    alerted_deleted = set()
    alerted_modified = set()

    try:
        while True:
            current = scan_directory()

            # Detect new files
            for path in sorted(current.keys()):
                if path not in baseline and path not in alerted_new:
                    print("[NEW] [{}] New file detected: {}".format(timestamp(), path))
                    alerted_new.add(path)

            # Detect modified files
            for path in sorted(current.keys()):
                if path in baseline:
                    if current[path] != baseline[path]:
                        # Use tuple (path, hash) to allow alerting on new hash values
                        key = (path, current[path])
                        if key not in alerted_modified:
                            print("[MODIFIED] [{}] File modified: {}".format(timestamp(), path))
                            alerted_modified.add(key)

            # Detect deleted files
            for path in sorted(baseline.keys()):
                if path not in current and path not in alerted_deleted:
                    print("[DELETED] [{}] File deleted: {}".format(timestamp(), path))
                    alerted_deleted.add(path)

            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print('\nMonitoring stopped by user.')


def main():
    ensure_monitor_dir()
    while True:
        print("\nFile Integrity Monitoring System")
        print("1) Create baseline")
        print("2) Start monitoring")
        print("q) Quit")
        choice = input("Select an option: ").strip().lower()
        if choice == "1":
            create_baseline()
        elif choice == "2":
            monitor()
        elif choice == "q":
            print("Goodbye.")
            break
        else:
            print("Invalid option. Please choose 1, 2, or q.")


if __name__ == "__main__":
    main()
