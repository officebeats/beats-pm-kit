import sys
import yaml
from pathlib import Path
from typing import List

def get_skill_paths() -> List[Path]:
    """
    Retrieve all SKILL.md files from the .agent/skills directory.

    Returns:
        List[Path]: A list of paths to SKILL.md files.
    """
    base_path = Path(__file__).resolve().parent.parent.parent
    skills_dir = base_path / ".agent" / "skills"
    
    if not skills_dir.exists():
        return []

    return [
        p / "SKILL.md" 
        for p in skills_dir.iterdir() 
        if p.is_dir() and (p / "SKILL.md").exists()
    ]

def validate_skill(skill_path: Path) -> bool:
    """
    Validate a single SKILL.md file against the v2.0 Gamma-Class schema.

    Args:
        skill_path (Path): Path to the SKILL.md file.

    Returns:
        bool: True if valid, False otherwise.
    """
    print(f"Testing {skill_path.parent.name}...", end=" ")
    
    try:
        content = skill_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"❌ FAIL: Read Error - {e}")
        return False
    
    # 1. Parse Frontmatter
    try:
        if not content.startswith("---"):
            print("❌ FAIL: Missing YAML frontmatter start")
            return False
            
        end_frontmatter = content.find("---", 3)
        if end_frontmatter == -1:
            print("❌ FAIL: Missing YAML frontmatter end")
            return False
            
        frontmatter = yaml.safe_load(content[3:end_frontmatter])
        
        required_keys = ["name", "description", "version", "author"]
        for key in required_keys:
            if key not in frontmatter:
                print(f"❌ FAIL: Missing YAML key '{key}'")
                return False
                
        if frontmatter.get("version") != "2.0.0":
             print(f"⚠️ WARN: Version is {frontmatter.get('version')}, expected 2.0.0")
             
    except Exception as e:
        print(f"❌ FAIL: YAML Error - {e}")
        return False

    # 2. Check for Sections (Simple String Matching)
    required_sections = [
        "# ", # Title
        "## 1. Interface Definition",
        "### Inputs",
        "### Outputs",
        "### Tools",
        "## 2. Cognitive Protocol",
        "### Step 1: Context Loading",
        "### Step 2:",
        "## 3. Cross-Skill Routing"
    ]
    
    for section in required_sections:
        if section not in content:
            print(f"❌ FAIL: Missing section '{section}'")
            return False
            
    print("✅ PASS")
    return True

if __name__ == "__main__":
    print("--- Verifying Skills v2.0 Schema ---")
    
    skills = get_skill_paths()
    results = []
    
    for skill in skills:
        results.append(validate_skill(skill))
        
    print("-" * 30)
    passed = results.count(True)
    total = len(results)
    
    print(f"Status: {passed}/{total} Skills Valid")
    
    if passed < total:
        sys.exit(1)

