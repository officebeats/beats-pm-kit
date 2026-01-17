"""
Skill Optimizer & Indexer (Centrifuge Protocol)

1. Migrates SKILL.md files to include 'triggers' in YAML frontmatter.
2. Generates 'skills.json' for fast lookup (Kernel Decapitation).
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

def parse_frontmatter(content: str) -> Dict[str, Any]:
    """Extract YAML frontmatter from markdown."""
    match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
    if match:
        return yaml.safe_load(match.group(1))
    return {}

def extract_keywords_from_body(content: str) -> List[str]:
    """Legacy extraction: Scrape 'Keywords' from Inputs."""
    match = re.search(r"\*\*Keywords\*\*: (.*?)(\n|$)", content)
    if match:
        raw = match.group(1)
        # Find all hashtags or words
        return re.findall(r"(#[a-zA-Z0-9_-]+)", raw)
    return []

def update_frontmatter(filepath: Path, triggers: List[str]) -> None:
    """Rewrite SKILL.md with new triggers in frontmatter."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Split frontmatter
    parts = re.split(r"^---\n", content, maxsplit=2)
    if len(parts) < 3:
        print(f"Skipping {filepath.name} (No frontmatter detected)")
        return

    # Parse and Update
    frontmatter_yaml = parts[1]
    body = parts[2]
    
    data = yaml.safe_load(frontmatter_yaml)
    if "triggers" not in data:
        data["triggers"] = triggers
        
        # Reconstruct
        new_yaml = yaml.dump(data, sort_keys=False).strip()
        new_content = f"---\n{new_yaml}\n---{body}"
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated: {filepath.name} with triggers {triggers}")

def index_skills():
    """Generate skills.json from FRONTMATTER."""
    index = {}
    
    if not SKILLS_DIR.exists():
        print("Skills directory not found.")
        return

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
            
        index[skill_id] = {
            "path": str(skill_file.relative_to(BRAIN_ROOT)).replace("\\", "/"),
            "description": meta.get("description", ""),
            "triggers": triggers
        }

    with open(SKILLS_JSON, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)
    
    print(f"\n✅ Index Generated: {SKILLS_JSON}")
    print(f"Total Skills: {len(index)}")

def migrate_all():
    """Bulk update all SKILL.md files."""
    print("--- Starting Migration ---")
    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue
            
        with open(skill_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        triggers = extract_keywords_from_body(content)
        if triggers:
            update_frontmatter(skill_file, triggers)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--migrate":
        migrate_all()
    
    index_skills()
