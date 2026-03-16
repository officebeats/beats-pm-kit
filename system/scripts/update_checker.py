"""
Update Checker — Run on every new session.
Compares local VERSION against latest GitHub release.
Prints actionable update instructions if behind.

Usage:
    python system/scripts/update_checker.py
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
VERSION_FILE = ROOT_DIR / "VERSION"
REPO = "officebeats/beats-pm-kit"


def get_local_version():
    """Read the local VERSION file."""
    if not VERSION_FILE.exists():
        return "unknown"
    return VERSION_FILE.read_text(encoding='utf-8').strip()


def get_remote_version():
    """Query GitHub for the latest release tag via gh CLI."""
    try:
        result = subprocess.run(
            ["gh", "api", f"repos/{REPO}/releases/latest", "--jq", ".tag_name"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Fallback: try git ls-remote
    try:
        result = subprocess.run(
            ["git", "ls-remote", "--tags", "--sort=-v:refname",
             f"https://github.com/{REPO}.git"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            for line in result.stdout.strip().splitlines():
                ref = line.split("refs/tags/")[-1].replace("^{}", "")
                if ref.startswith("v"):
                    return ref
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return None


def parse_version(v):
    """Parse 'v9.6.0' or '9.6.0' into a tuple of ints for comparison."""
    v = v.lstrip("v").strip()
    parts = v.split(".")
    try:
        return tuple(int(p) for p in parts)
    except ValueError:
        return (0, 0, 0)


def check_for_updates():
    """Compare local and remote versions, print results."""
    local = get_local_version()
    remote = get_remote_version()

    if remote is None:
        print("⚠ Could not check for updates (no network or gh CLI not found)")
        return False

    local_tuple = parse_version(local)
    remote_tuple = parse_version(remote)

    if remote_tuple > local_tuple:
        print(f"")
        print(f"  ╔══════════════════════════════════════════════════════╗")
        print(f"  ║  🔄 UPDATE AVAILABLE: v{local} → {remote}          ║")
        print(f"  ╠══════════════════════════════════════════════════════╣")
        print(f"  ║  Run: /update                                      ║")
        print(f"  ║  Or manually:                                      ║")
        print(f"  ║  git pull origin main && pip install -r             ║")
        print(f"  ║  system/requirements.txt                           ║")
        print(f"  ╚══════════════════════════════════════════════════════╝")
        print(f"")
        return True
    else:
        print(f"✅ Kit is up to date (v{local})")
        return False


if __name__ == "__main__":
    has_update = check_for_updates()
    sys.exit(1 if has_update else 0)
