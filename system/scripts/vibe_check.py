"""
Vibe Check Script (Centrifuge Protocol)

Validates the Beats PM System environment and configuration.
Checks toolchain, file structure, critical files, and AI model configuration.
"""

import sys
import os
import json
import datetime
from pathlib import Path
from typing import List

# Path setup
CURRENT_FILE = Path(__file__).resolve()
SYSTEM_ROOT = CURRENT_FILE.parent.parent      # system/
BRAIN_ROOT = SYSTEM_ROOT.parent               # beats-pm-kit/
REPORTS_DIR = SYSTEM_ROOT / "reports"

# Add BRAIN_ROOT to path for 'system.*' imports
sys.path.insert(0, str(BRAIN_ROOT))

from system.utils.ui import (
    print_cyan,
    print_success,
    print_warning,
    print_error,
)
from system.utils.platform import (
    get_system,
    get_python_executable,
    get_npm_executable,
)
from system.utils.subprocess_helper import (
    check_command_exists,
    check_extension_installed,
)
from system.utils.config import get_config
from system.scripts import harness_telemetry

class Logger:
    """Redirects stdout to both console and a log file."""
    def __init__(self):
        self.terminal = sys.stdout
        self.log_file = None
        self.log_path = self._init_log_file()

    def _init_log_file(self):
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = REPORTS_DIR / f"vibe_report_{timestamp}.txt"
        self.log_file = open(filename, "a", encoding="utf-8")
        return filename

    def write(self, message):
        self.terminal.write(message)
        self.log_file.write(message)

    def flush(self):
        self.terminal.flush()
        self.log_file.flush()
    
    @property
    def encoding(self):
        return "utf-8"

def check_toolchain() -> None:
    """Check if required development tools are installed."""
    print_cyan("\nToolchain:")

    # Check Python
    python_cmd = get_python_executable()
    if check_command_exists(python_cmd):
        print_success("Python: Installed")
    else:
        print_error("Python: Missing")

    # Check Git
    if check_command_exists("git"):
        print_success("Git: Installed")
    else:
        print_error("Git: Missing")

    # Check GitHub CLI
    if check_command_exists("gh"):
        print_success("GitHub CLI: Installed")
    else:
        print_error("GitHub CLI: Missing")

    # Check Node/NPM
    npm_cmd = get_npm_executable()
    if check_command_exists(npm_cmd):
        print_success("Node/NPM: Installed")
    else:
        print_error("Node/NPM: Missing")


def check_file_structure() -> None:
    """Check if required directory structure exists."""
    print_cyan("\nCore Infrastructure:")

    folders = get_config("directories.required", [])
    
    # Fallback default folders if config is empty
    if not folders:
        folders = [
            "0. Incoming/staging",
            "1. Company",
            "2. Products",
            "3. Meetings/transcripts",
            "4. People",
            "5. Trackers"
        ]

    for folder in folders:
        folder_path = BRAIN_ROOT / folder
        if folder_path.is_dir():
            print_success(f"/{folder}: Found")
        else:
            print_warning(f"/{folder}: Missing (Run #update)")


def check_critical_files() -> None:
    """Check if critical system files exist."""
    print_cyan("\nSystem Files:")

    critical_files = [
        get_config("files.kernel", ".agent/rules/GEMINI.md"),
        get_config("files.settings", "SETTINGS.md"),
        get_config("files.readme", "README.md"),
    ]

    for filename in critical_files:
        filepath = BRAIN_ROOT / filename
        if filepath.is_file():
            print_success(f"{filename}: Found")
        else:
            print_error(f"{filename}: CRITICAL MISSING")


def check_skills_configuration() -> None:
    """Check if the Skills directory and content exist."""
    print_cyan("\nAI Agent Skills (Gamma-Class v2.0):")

    skills_dir = BRAIN_ROOT / ".agent/skills"

    if skills_dir.is_dir():
        print_success("Skills Directory: Found")
        
        # Dynamic Scan
        found_skills = [
            d.name for d in skills_dir.iterdir() 
            if d.is_dir() and (d / "SKILL.md").exists()
        ]
        
        found_skills.sort()
        
        for skill in found_skills:
            print_success(f" Skill: {skill} (Loaded)")
            
        if not found_skills:
             print_warning(" No skills found in directory!")
             
    else:
        print_error("Skills Directory Missing! (Run #update)")


def check_extensions() -> None:
    """Check if optional extensions are installed."""
    print_cyan("\nOptional Power-Ups:")

    extensions = get_config("extensions", [])

    for ext in extensions:
        ext_id = ext.get("id")
        ext_name = ext.get("name", ext_id)

        if check_extension_installed(ext_id):
            print_success(f"Ext: {ext_name}: Installed")
        else:
            print_warning(f"Ext: {ext_name}: Not Installed")


# MCP config drift audit
MCP_ALLOWLIST_REL = "system/config/mcp-allowlist.json"
DEFAULT_MCP_CONFIG_FILES = (
    ".mcp.json",
    ".vscode/mcp.json",
    ".cursor/mcp.json",
    "system/config/mcp.template.json",
)


def _mcp_server_map(config: dict) -> dict:
    """Return the server-name -> spec map from either client config shape."""
    servers = config.get("mcpServers")
    if not isinstance(servers, dict):
        servers = config.get("servers")
    return servers if isinstance(servers, dict) else {}


def collect_mcp_servers(root: Path, config_files) -> List[dict]:
    """Collect {name, source_file, command} for every server in every readable config."""
    observed = []
    for relative in config_files:
        path = root / relative
        if not path.is_file():
            continue
        try:
            config = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(config, dict):
            continue
        for name, spec in sorted(_mcp_server_map(config).items()):
            command = ""
            if isinstance(spec, dict):
                command = spec.get("command") or spec.get("url") or ""
            observed.append({"name": name, "source_file": relative, "command": command})
    return observed


def mcp_config_drift(observed: List[dict], allowlisted: List[dict]) -> dict:
    """Compare observed servers against the allowlist by (name, source_file)."""
    observed_keys = {(item["name"], item["source_file"]) for item in observed}
    allowed_keys = {(item["name"], item["source_file"]) for item in allowlisted}
    return {
        "unknown": [item for item in observed if (item["name"], item["source_file"]) not in allowed_keys],
        "missing": [item for item in allowlisted if (item["name"], item["source_file"]) not in observed_keys],
    }


def check_token_hotspots() -> None:
    """Report the commands with the highest mean source bytes per resolution."""
    print_cyan("\nToken Hotspots:")

    ledger = BRAIN_ROOT / harness_telemetry.USAGE_LEDGER_REL
    entries = harness_telemetry.load_usage(ledger)
    if not entries:
        print_success("No usage ledger yet (.beats/usage.jsonl); resolve a command to start recording")
        return

    for row in harness_telemetry.usage_hotspots(entries, top=5):
        print_success(
            f"/{row['command']}: {row['mean_source_bytes']:,} mean source bytes over {row['runs']} run(s)"
        )


def check_mcp_config_drift() -> None:
    """Audit every known MCP config against the committed allowlist baseline."""
    print_cyan("\nMCP Config Drift:")

    allowlist_path = BRAIN_ROOT / MCP_ALLOWLIST_REL
    if not allowlist_path.is_file():
        print_warning(f"{MCP_ALLOWLIST_REL}: Missing (no MCP audit baseline)")
        return
    try:
        allowlist = json.loads(allowlist_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print_error(f"{MCP_ALLOWLIST_REL}: Unreadable ({exc})")
        return

    config_files = allowlist.get("config_files") or list(DEFAULT_MCP_CONFIG_FILES)
    allowlisted = allowlist.get("servers") or []
    observed = collect_mcp_servers(BRAIN_ROOT, config_files)
    drift = mcp_config_drift(observed, allowlisted)

    for item in drift["unknown"]:
        print_warning(f"UNKNOWN MCP server '{item['name']}' in {item['source_file']} (not allowlisted)")
    for item in drift["missing"]:
        print_warning(f"MISSING MCP server '{item['name']}' expected in {item['source_file']} (allowlisted but absent)")
    if not drift["unknown"] and not drift["missing"]:
        print_success(
            f"MCP configs match allowlist ({len(observed)} server entries across {len(config_files)} config files)"
        )



def main() -> None:
    """Main entry point for vibe check."""
    # Hijack stdout
    logger = Logger()
    sys.stdout = logger
    
    system = get_system()
    print_cyan(f"--- Antigravity Vibe Check ({system}) ---")
    print_cyan(f"Report saved to: {logger.log_path}")

    # Run all checks
    check_toolchain()
    check_file_structure()
    check_critical_files()
    check_skills_configuration()
    check_extensions()
    check_token_hotspots()
    check_mcp_config_drift()

    print_cyan("\n--- Check Complete ---")


if __name__ == "__main__":
    main()
