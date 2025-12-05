#!/usr/bin/env python3
"""
version 1.

NotSoStrict - Preflight Dependency Checker
------------------------------------------

This script verifies that all required components are installed
before running the main NotSoStrict environment.

It performs ONLY environment and dependency checks.
It does NOT modify the system, network state, or run any test environment.
"""

import os
import sys
import re
import shutil
import subprocess


MIN_BETTERCAP_VERSION = (2, 41, 0)


# ------------------------------
# Version Parsing
# ------------------------------
def parse_version(version_str):
    """Extract semantic version numbers from a string."""
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", version_str)
    if not match:
        return None
    return tuple(map(int, match.groups()))


# ------------------------------
# Core Checks
# ------------------------------
def check_root():
    if os.geteuid() != 0:
        print("[✗] Must run as root (sudo required).")
        return False
    print("[✓] Running as root")
    return True


def check_binary(name):
    """Simple binary lookup."""
    return shutil.which(name) is not None


def check_and_report_binary(name):
    """Binary lookup with logging."""
    if check_binary(name):
        print(f"[✓] Found: {name}")
        return True
    else:
        print(f"[✗] Missing: {name}")
        return False


def check_chromium():
    """Check for Chromium regardless of distro naming."""
    if check_binary("chromium-browser"):
        print("[✓] Found Chromium (chromium-browser)")
        return True
    
    if check_binary("chromium"):
        print("[✓] Found Chromium (chromium)")
        return True

    print("[✗] Chromium not found. Install 'chromium' or 'chromium-browser'.")
    return False


def check_bettercap_version():
    """Ensure bettercap exists and meets the minimum required version."""
    if shutil.which("bettercap") is None:
        print("[✗] bettercap is not installed.")
        return False

    try:
        result = subprocess.run(
            ["bettercap", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        output = result.stdout.strip() or result.stderr.strip()
        version = parse_version(output)

        if version is None:
            print(f"[✗] Unable to parse bettercap version from: {output}")
            return False

        if version < MIN_BETTERCAP_VERSION:
            print(f"[✗] bettercap version {version} is too old.")
            print(f"    Requires ≥ {'.'.join(map(str, MIN_BETTERCAP_VERSION))}")
            return False

        print(f"[✓] bettercap version OK: {version}")
        return True

    except Exception as e:
        print(f"[✗] Failed to check bettercap version: {e}")
        return False


def check_display():
    """Check that a DISPLAY environment is available for Chromium."""
    display = os.environ.get("DISPLAY")
    if display:
        print(f"[✓] DISPLAY detected: {display}")
        return True
    else:
        print("[✗] DISPLAY is not set. Cannot launch Chromium.")
        return False


# ------------------------------
# Main Logic
# ------------------------------
def preflight_check():
    print("==========================================")
    print("      NotSoStrict - Preflight Check       ")
    print("==========================================\n")

    checks = [
        check_root(),
        check_and_report_binary("ip"),
        check_and_report_binary("iptables"),
        check_and_report_binary("xhost"),
        check_and_report_binary("x-terminal-emulator"),
        check_chromium(),
        check_bettercap_version(),
        check_display(),
    ]

    print("\n-------------------------------------------")

    if all(checks):
        print("[✓] All dependencies satisfied. You are good to go!\n")
        return True
    else:
        print("[✗] One or more requirements are missing or outdated.\n")
        return False


# ------------------------------
# Entry Point
# ------------------------------
if __name__ == "__main__":
    ok = preflight_check()
    sys.exit(0 if ok else 1)
