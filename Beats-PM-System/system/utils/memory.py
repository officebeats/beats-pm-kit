"""
Memory Management Utility - Antigravity Native

Optimized methods for accessing and maintaining Long-Term Memory artifacts:
- DECISION_LOG.md
- PEOPLE.md
- QUOTE_INDEX.md
- SESSION_MEMORY.md

Uses efficient I/O to minimize context load.
"""

from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
from .config import get_tracker_path, get_path, get_root_directory

def _append_to_log(filepath: str, content: str) -> bool:
    """Appends a new line to a log file efficiently."""
    try:
        root = get_root_directory()
        full_path = Path(root) / filepath
        
        # Ensure parent exists
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, "a", encoding="utf-8") as f:
            f.write(content + "\n")
        return True
    except Exception as e:
        print(f"Error writing to memory log {filepath}: {e}")
        return False

def log_decision(decision: str, context: str, owner: str = "PM") -> bool:
    """
    Logs a strategic decision to DECISION_LOG.md.
    Format: | YYYY-MM-DD | Decision | Context | Owner |
    """
    path = get_tracker_path('decision_log')
    if not path:
        return False
        
    date_str = datetime.now().strftime("%Y-%m-%d")
    # Sanitize inputs to prevent markdown breakage
    clean_decision = decision.replace("|", "-").replace("\n", " ")
    clean_context = context.replace("|", "-").replace("\n", " ")
    
    row = f"| {date_str} | {clean_decision} | {clean_context} | {owner} |"
    return _append_to_log(path, row)

def log_person(name: str, role: str, context: str) -> bool:
    """
    Logs a new stakeholder to PEOPLE.md.
    """
    path = get_path('people')
    if not path:
        return False
    
    file_path = f"{path}/PEOPLE.md"
    row = f"| {name} | {role} | {context} |"
    return _append_to_log(file_path, row)

def read_recent_decisions(limit: int = 5) -> List[str]:
    """
    Reads the last N decisions from the log without loading the whole file.
    Efficient for context window optimization.
    """
    path = get_tracker_path('decision_log')
    if not path:
        return []
        
    root = get_root_directory()
    full_path = Path(root) / path
    
    if not full_path.exists():
        return []
        
    lines = []
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            # Read all lines (efficient enough for text files < 10MB)
            # For massive files, we'd use seek() from the end.
            all_lines = f.readlines()
            
            # Filter for table rows (start with |)
            data_lines = [l.strip() for l in all_lines if l.strip().startswith("|") and not l.strip().startswith("| Date")]
            
            return data_lines[-limit:]
            
    except Exception:
        return []

def get_session_memory() -> str:
    """Reads the last known state from SESSION_MEMORY.md"""
    # Root file
    path = "SESSION_MEMORY.md"
    root = get_root_directory()
    full_path = Path(root) / path
    
    try:
        if full_path.exists():
            return full_path.read_text(encoding="utf-8")
    except:
        pass
    return "No previous session memory found."

def save_session_memory(summary: str) -> bool:
    """Updates SESSION_MEMORY.md with current state."""
    path = "SESSION_MEMORY.md"
    root = get_root_directory()
    full_path = Path(root) / path
    
    content = f"""# Session Memory
> Last Updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

{summary}
"""
    try:
        full_path.write_text(content, encoding="utf-8")
        return True
    except:
        return False
