import os
from pathlib import Path

# --- Centralized System Constants ---

# Root Paths
# Assumes this script is in system/scripts/
CURRENT_FILE = Path(__file__).resolve()
SYSTEM_ROOT = CURRENT_FILE.parent.parent  # system/
BRAIN_ROOT = SYSTEM_ROOT.parent           # brain root/

# Standard Folders
INCOMING_DIR = BRAIN_ROOT / "0. Incoming"
COMPANY_DIR = BRAIN_ROOT / "1. Company"
PRODUCTS_DIR = BRAIN_ROOT / "2. Products"
MEETINGS_DIR = BRAIN_ROOT / "3. Meetings"
PEOPLE_DIR = BRAIN_ROOT / "4. People"
TRACKERS_DIR = BRAIN_ROOT / "5. Trackers"

# Sub-Directories
PROCESSED_DIR = INCOMING_DIR / "processed"
TRANSCRIPTS_DIR = MEETINGS_DIR / "transcripts"
ARCHIVE_DIR = TRACKERS_DIR / "archive"

# Key Files
TASK_MASTER = TRACKERS_DIR / "TASK_MASTER.md"
STATUS_FILE = BRAIN_ROOT / "STATUS.md"
SESSION_MEMORY = BRAIN_ROOT / "SESSION_MEMORY.md"

if __name__ == "__main__":
    print(f"System Configuration Loaded.")
    print(f"Brain Root: {BRAIN_ROOT}")
