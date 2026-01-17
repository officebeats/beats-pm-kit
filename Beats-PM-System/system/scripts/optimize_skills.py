"""
Skill Optimizer & Indexer (Centrifuge Protocol)

1. Migrates SKILL.md files to include 'triggers' in YAML frontmatter.
2. Generates 'skills.json' for fast lookup (Native Antigravity Mode).
3. REMOVES routing table from KERNEL.md to prevent Context Bloat.

Refactored for clarity: separate classes for parsing, scanning, indexing, and kernel cleaning.
"""

import re
import yaml
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# Paths
CURRENT_FILE = Path(__file__).resolve()
SYSTEM_ROOT = CURRENT_FILE.parent.parent.parent  # Beats-PM-System
BRAIN_ROOT = SYSTEM_ROOT.parent  # beats-pm-antigravity-brain
SKILLS_DIR = BRAIN_ROOT / ".agent/skills"
SKILLS_JSON = SYSTEM_ROOT / "system/skills.json"
KERNEL_FILE = BRAIN_ROOT / "KERNEL.md"


@dataclass
class SkillMetadata:
    """Represents metadata for a single skill."""
    skill_id: str
    description: str
    triggers: List[str]
    relative_path: str


class FrontmatterParser:
    """Handles parsing of YAML frontmatter and keyword extraction from skill files."""

    @staticmethod
    def parse(content: str) -> Dict[str, Any]:
        """Extract YAML frontmatter from markdown."""
        match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
        if match:
            try:
                return yaml.safe_load(match.group(1))
            except yaml.YAMLError:
                return {}
        return {}

    @staticmethod
    def extract_keywords_from_body(content: str) -> List[str]:
        """Legacy extraction: Scrape 'Keywords' from Inputs section."""
        match = re.search(r"\*\*Keywords\*\*: (.*?)(\n|$)", content)
        if match:
            raw = match.group(1)
            # Find all hashtags
            return re.findall(r"(#[a-zA-Z0-9_-]+)", raw)
        return []


class SkillScanner:
    """Scans skills directory and collects skill metadata."""

    def __init__(self, skills_dir: Path, brain_root: Path):
        self.skills_dir = skills_dir
        self.brain_root = brain_root
        self.parser = FrontmatterParser()

    def scan(self) -> List[SkillMetadata]:
        """Scan skills directory and return list of skill metadata."""
        skills = []

        if not self.skills_dir.exists():
            return skills

        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue

            skill_metadata = self._process_skill_directory(skill_dir)
            if skill_metadata:
                skills.append(skill_metadata)

        return skills

    def _process_skill_directory(self, skill_dir: Path) -> Optional[SkillMetadata]:
        """Process a single skill directory and extract metadata."""
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            return None

        try:
            with open(skill_file, "r", encoding="utf-8") as f:
                content = f.read()
        except (IOError, UnicodeDecodeError):
            return None

        meta = self.parser.parse(content)
        skill_id = meta.get("name", skill_dir.name)

        # Use frontmatter triggers, or fall back to body extraction
        triggers = meta.get("triggers", [])
        if not triggers:
            triggers = self.parser.extract_keywords_from_body(content)

        # Truncate long descriptions
        description = meta.get("description", "No description")
        if len(description) > 80:
            description = description[:77] + "..."

        relative_path = str(skill_file.relative_to(self.brain_root)).replace("\\", "/")

        return SkillMetadata(
            skill_id=skill_id,
            description=description,
            triggers=triggers,
            relative_path=relative_path
        )


class SkillIndexBuilder:
    """Builds and saves the skills index as JSON."""

    @staticmethod
    def build_index(skills: List[SkillMetadata]) -> Dict[str, Dict[str, Any]]:
        """Build index dictionary from skill metadata."""
        index = {}
        for skill in skills:
            index[skill.skill_id] = {
                "path": skill.relative_path,
                "description": skill.description,
                "triggers": skill.triggers
            }
        return index

    @staticmethod
    def save_to_file(index: Dict[str, Dict[str, Any]], output_path: Path) -> None:
        """Save index to JSON file."""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2)


class KernelCleaner:
    """Handles cleaning and optimization of KERNEL.md file."""

    SKILL_SECTION_MARKER = "### 🛠️ Core Skills Inventory"
    LEAN_CONTENT = (
        "\n\n> **Note**: This kernel runs in **Native Mode**. "
        "Skill definitions are indexed in `Beats-PM-System/system/skills.json` "
        "to save context tokens. The Agent automatically accesses this index "
        "to resolve commands.\n\n"
    )

    def __init__(self, kernel_path: Path):
        self.kernel_path = kernel_path

    def clean(self) -> bool:
        """Remove skill table from KERNEL.md to reduce context bloat.

        Returns:
            True if content was modified, False if already clean or file doesn't exist.
        """
        if not self.kernel_path.exists():
            return False

        try:
            with open(self.kernel_path, "r", encoding="utf-8") as f:
                kernel_content = f.read()
        except (IOError, UnicodeDecodeError):
            return False

        # Check if already in lean/native mode
        if "This kernel runs in **Native Mode**" in kernel_content:
            return False

        # Match the skill inventory section from marker to next "---"
        pattern = re.compile(
            r"(### 🛠️ Core Skills Inventory)(.*?)(---)",
            re.DOTALL
        )

        if pattern.search(kernel_content):
            new_kernel = pattern.sub(f"\\1{self.LEAN_CONTENT}\\3", kernel_content)

            try:
                with open(self.kernel_path, "w", encoding="utf-8") as f:
                    f.write(new_kernel)
                return True
            except IOError:
                return False

        return False


def index_skills():
    """Generate skills.json AND clean KERNEL.md.

    This is the main orchestrator function that coordinates all components.
    """
    # Scan skills directory
    scanner = SkillScanner(SKILLS_DIR, BRAIN_ROOT)
    skills = scanner.scan()

    if not skills and not SKILLS_DIR.exists():
        print("Skills directory not found.")
        return

    # Build and save index
    index = SkillIndexBuilder.build_index(skills)
    SkillIndexBuilder.save_to_file(index, SKILLS_JSON)

    # Clean KERNEL.md
    cleaner = KernelCleaner(KERNEL_FILE)
    was_cleaned = cleaner.clean()

    if was_cleaned:
        print("✅ Removed Skill Table from KERNEL.md (Native Optimization)")
    else:
        print("🔹 KERNEL.md is already clean.")

    print(f"\n✅ Index Generated: {SKILLS_JSON}")
    print(f"Total Skills: {len(index)}")

if __name__ == "__main__":
    index_skills()
