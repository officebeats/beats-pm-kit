"""
Context Health Check (v1.0.0)

Combined startup script that:
1. Checks for kit updates (replaces update_checker.py at startup)
2. Measures active conversation size and reports health status

Returns a single health report the agent can act on automatically.
"""

import sys
import os
import json
from pathlib import Path

# Path setup
SCRIPT_DIR = Path(__file__).resolve().parent
SYSTEM_ROOT = SCRIPT_DIR.parent
BRAIN_ROOT = SYSTEM_ROOT.parent

# Antigravity conversation storage
ANTIGRAVITY_DIR = Path.home() / ".gemini" / "antigravity"
CONVERSATIONS_DIR = ANTIGRAVITY_DIR / "conversations"

# Thresholds (in MB)
WARNING_MB = 2.0
CRITICAL_MB = 3.0


def check_conversation_health():
    """Measure the active conversation size and return health status."""
    try:
        if not CONVERSATIONS_DIR.exists():
            return {"status": "GREEN", "size_kb": 0, "message": "No active conversations."}

        pb_files = sorted(
            CONVERSATIONS_DIR.glob("*.pb"),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )

        if not pb_files:
            return {"status": "GREEN", "size_kb": 0, "message": "No active conversations."}

        # Get the most recent (active) conversation
        active = pb_files[0]
        size_bytes = active.stat().st_size
        size_kb = size_bytes / 1024
        size_mb = size_bytes / (1024 * 1024)

        if size_mb > CRITICAL_MB:
            return {
                "status": "RED",
                "size_kb": round(size_kb),
                "size_mb": round(size_mb, 2),
                "message": f"CRITICAL: Active conversation is {size_mb:.1f}MB. Flush recommended to prevent 429 errors."
            }
        elif size_mb > WARNING_MB:
            return {
                "status": "YELLOW",
                "size_kb": round(size_kb),
                "size_mb": round(size_mb, 2),
                "message": f"WARNING: Active conversation is {size_mb:.1f}MB. Consider wrapping up soon."
            }
        else:
            return {
                "status": "GREEN",
                "size_kb": round(size_kb),
                "message": "Conversation size is healthy."
            }
    except Exception as e:
        return {"status": "UNKNOWN", "size_kb": 0, "message": f"Could not check: {e}"}


def check_for_updates():
    """Quick update check — delegates to update_checker.py logic."""
    try:
        # Import and run the existing checker
        sys.path.insert(0, str(SCRIPT_DIR))
        from update_checker import main as check_update
        check_update()
    except Exception:
        # If update check fails, skip silently
        pass


def check_dotcontext():
    """Verify dotcontext dependency and configure headlessly if missing."""
    try:
        import subprocess
        
        # Check if .context dir exists as a signal that it's been initialized
        context_dir = BRAIN_ROOT / ".context"
        
        # Check if npx is available
        try:
            # We use shell=True on Windows to resolve npx, or just call npx directly
            subprocess.run("npx --version", shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            has_npx = True
        except subprocess.CalledProcessError:
            has_npx = False

        if has_npx and not context_dir.exists():
            print("  → Dotcontext dependency missing. Installing headlessly...")
            subprocess.run("npx -y @dotcontext/mcp@latest install all --local", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run("npx -y @dotcontext/cli@latest reverse-sync", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run("npx -y @dotcontext/cli@latest sync -p all --force", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("  → Dotcontext installation and sync complete.")
    except Exception as e:
        print(f"  → Warning: Dotcontext dependency check failed: {e}")


def main():
    # 1. Update check (silent unless update available)
    check_for_updates()

    # 2. Check Dotcontext dependency (headless install if needed)
    check_dotcontext()

    # 3. Conversation health (always report)
    health = check_conversation_health()

    status_icon = {"GREEN": "🟢", "YELLOW": "🟡", "RED": "🔴", "UNKNOWN": "⚪"}.get(health["status"], "⚪")
    print(f"\n{status_icon} Context Health: {health['message']}")

    if health["status"] == "RED":
        print("  → Recommend: Flush this session and start fresh.")
        print(f"  → Active conversation size: {health.get('size_mb', '?')}MB")

    return 0 if health["status"] in ("GREEN", "UNKNOWN") else 1


if __name__ == "__main__":
    sys.exit(main())
