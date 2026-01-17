"""
Initialize Memory Modules

Ensures that the Long-Term Memory (LTM) files exist with proper headers.
Run this during core_setup or on demand.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import get_tracker_path, get_path, get_root_directory
from utils.filesystem import ensure_directory

def init_memory_files():
    root = get_root_directory()
    
    # 1. DECISION_LOG.md
    dec_path = get_tracker_path('decision_log')
    if dec_path:
        full_dec_path = Path(root) / dec_path
        if not full_dec_path.exists():
            ensure_directory(str(full_dec_path.parent))
            header = ("# Strategic Decision Log\n\n"
                      "> Immutable record of key product and architectural decisions.\n\n"
                      "| Date | Decision | Context | Owner |\n"
                      "|:---|:---|:---|:---|\n")
            full_dec_path.write_text(header, encoding="utf-8")
            print(f"✅ Created {dec_path}")
        else:
            print(f"🔹 {dec_path} exists")

    # 2. PEOPLE.md
    people_dir = get_path('people')
    if people_dir:
        people_file = Path(root) / people_dir / "PEOPLE.md"
        if not people_file.exists():
            ensure_directory(str(people_file.parent))
            header = ("# People & Stakeholders\n\n"
                      "> The Human Context. Who does what?\n\n"
                      "| Name | Role | Context |\n"
                      "|:---|:---|:---|\n")
            people_file.write_text(header, encoding="utf-8")
            print(f"✅ Created {people_dir}/PEOPLE.md")
        else:
            print(f"🔹 {people_dir}/PEOPLE.md exists")


    # 3. quote-index.md
    quote_dir = get_path('meetings')
    if quote_dir:
        quote_file = Path(root) / quote_dir / "quote-index.md"
        if not quote_file.exists():
            ensure_directory(str(quote_file.parent))
            header = ("# Quote Index\n\n"
                      "> Grep-friendly archive of key verbatim quotes.\n\n"
                      "| Date | Speaker | Quote | Source |\n"
                      "|:---|:---|:---|:---|\n")
            quote_file.write_text(header, encoding="utf-8")
            print(f"✅ Created {quote_dir}/quote-index.md")
        else:
            print(f"🔹 {quote_dir}/quote-index.md exists")

    # 4. SESSION_MEMORY.md (Root)
    session_file = Path(root) / "SESSION_MEMORY.md"
    if not session_file.exists():
        header = ("# Session Memory\n"
                  "> Last Known State registry.\n\n"
                  "System Initialized. No previous session data.\n")
        session_file.write_text(header, encoding="utf-8")
        print("✅ Created SESSION_MEMORY.md")
    else:
        print("🔹 SESSION_MEMORY.md exists")

if __name__ == "__main__":
    init_memory_files()
