import subprocess
import sys
import argparse
import os

def run_cmd(cmd):
    """Run a system script and return output."""
    try:
        print(f"--- Executing Beats PM Script: {cmd} ---")
        result = subprocess.run(cmd, shell=True, check=True)
        return True
    except Exception as e:
        print(f"Error executing {cmd}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Beats PM Kit - Universal CLI Gateway")
    parser.add_argument("command", choices=["day", "transcript", "outlook", "vibe", "track", "vacuum"])
    parser.add_argument("--args", help="Additional arguments for the command", default="")
    
    args = parser.parse_args()
    
    scripts = {
        "day": "python3 system/scripts/daily_synth.py",
        "transcript": "python3 system/scripts/transcript_fetcher.py && python3 system/scripts/quill_mcp_client.py",
        "outlook": "python3 system/scripts/outlook_bridge.py",
        "vibe": "python3 system/scripts/vibe_check.py",
        "track": "python3 system/scripts/inbox_processor.py",
        "vacuum": "python3 system/scripts/vacuum.py"
    }
    
    if args.command in scripts:
        cmd = f"{scripts[args.command]} {args.args}"
        run_cmd(cmd)
    else:
        print(f"Unknown command: {args.command}")

if __name__ == "__main__":
    main()
