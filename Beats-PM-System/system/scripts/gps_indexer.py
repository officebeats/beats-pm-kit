"""
Antigravity GPS (Content Indexer)
Native Optimization Protocol

Scans the "Brain Processed Files" (Folders 1-5) to build a high-speed
lookup table (`content_index.json`).

Enables O(1) retrieval of documents by Title, Filename, or Date.
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Any

# Paths
CURRENT_FILE = Path(__file__).resolve()
SYSTEM_ROOT = CURRENT_FILE.parent.parent.parent # Beats-PM-System
BRAIN_ROOT = SYSTEM_ROOT.parent 
INDEX_FILE = SYSTEM_ROOT / "system/content_index.json"

# Configuration
SCAN_DIRS = [
    "1. Company",
    "2. Products",
    "3. Meetings",
    "4. People",
    "5. Trackers"
]

IGNORE_DIRS = [
    "archive",
    "node_modules",
    ".git",
    "__pycache__"
]

def extract_title(content: str, filename: str) -> str:
    """Extracts the H1 title or falls back to filename."""
    # Try finding # Title
    match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return filename.replace(".md", "").replace("-", " ").title()

def scan_files():
    """Scans and indexes valid markdown files."""
    index: List[Dict[str, Any]] = []
    
    print(f"GPS Scanning Brain via Antigravity...")
    
    count = 0
    for folder_name in SCAN_DIRS:
        folder_path = BRAIN_ROOT / folder_name
        if not folder_path.exists():
            continue
            
        # Recursive scan
        for file in folder_path.rglob("*.md"):
            # Skip ignored directories
            if any(part in file.parts for part in IGNORE_DIRS):
                continue
                
            try:
                # Optimized Head-Only Read (First 500 chars) for Title
                with open(file, 'r', encoding="utf-8", errors="ignore") as f:
                    head = f.read(500)
                
                title = extract_title(head, file.name)
                
                # Metadata
                stat = file.stat()
                mtime = stat.st_mtime
                size = stat.st_size
                rel_path = str(file.relative_to(BRAIN_ROOT)).replace("\\", "/")
                
                entry = {
                    "title": title,
                    "path": rel_path,
                    "filename": file.name,
                    "folder": folder_name,
                    "mtime": mtime,
                    "size": size
                }
                index.append(entry)
                count += 1
            except Exception as e:
                # Silently fail for locked files
                pass
                
    # Sort by recent modification
    index.sort(key=lambda x: x["mtime"], reverse=True)
    
    # Save
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)
        
    print(f"GPS Locked. Indexed {count} artifacts.")

if __name__ == "__main__":
    scan_files()
