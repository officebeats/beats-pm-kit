"""
Skill Optimizer & Indexer (Centrifuge Protocol)

1. Migrates SKILL.md files to include 'triggers' in YAML frontmatter.
2. Generates 'skills.json' for fast lookup (Native Antigravity Mode).
3. REMOVES routing table from KERNEL.md to prevent Context Bloat.
"""

import os
import re
import yaml
import json
from pathlib import Path
from typing import List, Dict, Any

# Paths
CURRENT_FILE = Path(__file__).resolve()
SYSTEM_ROOT = CURRENT_FILE.parent.parent.parent # Beats-PM-System
BRAIN_ROOT = SYSTEM_ROOT.parent # beats-pm-antigravity-brain
SKILLS_DIR = BRAIN_ROOT / ".agent/skills"
SKILLS_JSON = SYSTEM_ROOT / "system/skills.json"
KERNEL_FILE = BRAIN_ROOT / "KERNEL.md"

def parse_frontmatter(content: str) -> Dict[str, Any]:
    """Extract YAML frontmatter from markdown."""
    match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
    if match:
        try:
            return yaml.safe_load(match.group(1))
        except:
            return {}
    return {}

def extract_keywords_from_body(content: str) -> List[str]:
    """Legacy extraction: Scrape 'Keywords' from Inputs."""
    match = re.search(r"\*\*Keywords\*\*: (.*?)(\n|$)", content)
    if match:
        raw = match.group(1)
        # Find all hashtags or words
        return re.findall(r"(#[a-zA-Z0-9_-]+)", raw)
    return []

def index_skills():
    """Generate skills.json AND clean KERNEL.md."""
    index = {}
    
    if not SKILLS_DIR.exists():
        print("Skills directory not found.")
        return

    # 1. Build Index
    
    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue
            
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue
            
        with open(skill_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        meta = parse_frontmatter(content)
        skill_id = meta.get("name", skill_dir.name)
        
        # Use frontmatter triggers, or body fallback
        triggers = meta.get("triggers", [])
        if not triggers:
            triggers = extract_keywords_from_body(content)

        # Ensure we have a description, truncated if necessary
        desc = meta.get("description", "No description")
        if len(desc) > 80:
            desc = desc[:77] + "..."

        index[skill_id] = {
            "path": str(skill_file.relative_to(BRAIN_ROOT)).replace("\\", "/"),
            "description": desc,
            "triggers": triggers
        }

    # 2. Save JSON
    with open(SKILLS_JSON, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)
    
    # 3. Clean KERNEL.md (Context Bloat Removal)
    if KERNEL_FILE.exists():
        with open(KERNEL_FILE, "r", encoding="utf-8") as f:
            kernel_content = f.read()
        
        # We look for the "Core Skills Inventory" section and replace it with a minimal pointer.
        marker_start = "### 🛠️ Core Skills Inventory"
        
        # We want to replace everything from the marker to the next "---"
        pattern = re.compile(r"(### 🛠️ Core Skills Inventory)(.*?)(---)", re.DOTALL)
        
        lean_content = """\n\n> **Note**: This kernel runs in **Native Mode**. Skill definitions are indexed in `Beats-PM-System/system/skills.json` to save context tokens. The Agent automatically accesses this index to resolve commands.\n\n"""
        
        # Replace
        if pattern.search(kernel_content):
            new_kernel = pattern.sub(f"\\1{lean_content}\\3", kernel_content)
            
            with open(KERNEL_FILE, "w", encoding="utf-8") as f:
                f.write(new_kernel)
            print(f"✅ Removed Skill Table from KERNEL.md (Native Optimization)")
        else:
            print("🔹 KERNEL.md is already clean.")

    print(f"\n✅ Index Generated: {SKILLS_JSON}")
    print(f"Total Skills: {len(index)}")

if __name__ == "__main__":
    index_skills()
