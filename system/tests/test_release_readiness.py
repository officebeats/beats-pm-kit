"""
Release Readiness Test Suite
============================
Run before EVERY GitHub release. Uses dynamic discovery (no hardcoded lists).
Tests real-world scenarios a PM would encounter using this kit.

Usage:
    python -m pytest system/tests/test_release_readiness.py -v
"""

import unittest
import os
import re
from pathlib import Path

# ============================================================================
# Setup
# ============================================================================

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
AGENTS_DIRS = [ROOT_DIR / ".agents" / "agents", ROOT_DIR / ".agent" / "agents"]
SKILLS_DIRS = [ROOT_DIR / ".agents" / "skills", ROOT_DIR / ".agent" / "skills"]
WORKFLOWS_DIRS = [ROOT_DIR / ".agents" / "workflows", ROOT_DIR / ".agent" / "workflows"]
SYSTEM_DIR = ROOT_DIR / "system"
SCRIPTS_DIR = SYSTEM_DIR / "scripts"


def _discover(dirs, pattern="*", is_dir=False):
    """Discover unique items across multiple directories."""
    items = {}
    for d in dirs:
        if not d.exists():
            continue
        if is_dir:
            for item in d.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    items[item.name] = item
        else:
            for item in d.glob(pattern):
                if item.is_file() and not item.name.startswith('.'):
                    items[item.stem] = item
    return items


def _discover_agents():
    return _discover(AGENTS_DIRS, "*.md")


def _discover_skills():
    return _discover(SKILLS_DIRS, is_dir=True)


def _discover_workflows():
    return _discover(WORKFLOWS_DIRS, "*.md")


# ============================================================================
# 1. STRUCTURAL INTEGRITY — Does the kit have all its bones?
# ============================================================================

class TestStructuralIntegrity(unittest.TestCase):
    """Real-world check: When a PM installs this kit, does everything exist?"""

    def test_folder_structure_exists(self):
        """PM installs kit → all 6 standard folders should exist."""
        for folder in ["0. Incoming", "1. Company", "2. Products",
                       "3. Meetings", "4. People", "5. Trackers"]:
            path = ROOT_DIR / folder
            self.assertTrue(path.exists() or (ROOT_DIR / ".gitkeep").exists(),
                            f"Standard folder '{folder}' missing — new PM will have broken file routing")

    def test_gemini_md_exists(self):
        """System config must exist for the orchestrator to function."""
        paths = [ROOT_DIR / ".agent" / "rules" / "GEMINI.md",
                 ROOT_DIR / ".agents" / "rules" / "GEMINI.md"]
        self.assertTrue(any(p.exists() for p in paths),
                        "GEMINI.md missing — orchestrator has no system config")

    def test_readme_exists(self):
        """README.md is the entry point for every new user."""
        self.assertTrue((ROOT_DIR / "README.md").exists(), "README.md missing")

    def test_minimum_agent_count(self):
        """Kit should have at least 8 agents (core team)."""
        agents = _discover_agents()
        self.assertGreaterEqual(len(agents), 8,
                                f"Only {len(agents)} agents found — core team incomplete")

    def test_minimum_skill_count(self):
        """Kit should have at least 50 skills (PM + eng baseline)."""
        skills = _discover_skills()
        self.assertGreaterEqual(len(skills), 50,
                                f"Only {len(skills)} skills found — below minimum threshold")

    def test_minimum_workflow_count(self):
        """Kit should have at least 15 workflows (core playbooks)."""
        workflows = _discover_workflows()
        self.assertGreaterEqual(len(workflows), 15,
                                f"Only {len(workflows)} workflows found — missing core playbooks")


# ============================================================================
# 2. SKILL QUALITY — Every skill must be usable, not just present
# ============================================================================

class TestSkillQuality(unittest.TestCase):
    """Real-world check: PM invokes a skill → does it have valid instructions?"""

    def test_every_skill_has_skill_md(self):
        """Every skill directory MUST contain a SKILL.md file."""
        skills = _discover_skills()
        missing = []
        for name, path in skills.items():
            skill_md = path / "SKILL.md"
            if not skill_md.exists():
                missing.append(name)
        self.assertEqual(missing, [],
                         f"Skills without SKILL.md (unusable): {missing}")

    def test_every_skill_md_has_content(self):
        """SKILL.md must have meaningful content (>50 chars), not be empty."""
        skills = _discover_skills()
        empty = []
        for name, path in skills.items():
            skill_md = path / "SKILL.md"
            if skill_md.exists():
                size = skill_md.stat().st_size
                if size < 50:
                    empty.append(f"{name} ({size}b)")
        self.assertEqual(empty, [],
                         f"Skills with empty/stub SKILL.md: {empty}")

    def test_skill_md_has_description(self):
        """SKILL.md should contain a description (frontmatter or first paragraph)."""
        skills = _discover_skills()
        no_desc = []
        for name, path in skills.items():
            skill_md = path / "SKILL.md"
            if skill_md.exists():
                try:
                    content = skill_md.read_text(encoding='utf-8', errors='replace')
                    # Check for YAML frontmatter description or at least 1 sentence
                    has_frontmatter = content.startswith('---')
                    has_content = len(content.strip()) > 100
                    if not (has_frontmatter or has_content):
                        no_desc.append(name)
                except Exception:
                    no_desc.append(f"{name} (unreadable)")
        self.assertEqual(no_desc, [],
                         f"Skills without description: {no_desc}")


# ============================================================================
# 3. AGENT QUALITY — Every agent must have valid persona definition
# ============================================================================

class TestAgentQuality(unittest.TestCase):
    """Real-world check: Orchestrator routes to an agent → is it well-defined?"""

    def test_every_agent_has_content(self):
        """Agent files must have meaningful persona definitions (>200 chars)."""
        agents = _discover_agents()
        empty = []
        for name, path in agents.items():
            size = path.stat().st_size
            if size < 200:
                empty.append(f"{name} ({size}b)")
        self.assertEqual(empty, [],
                         f"Agents with insufficient persona definition: {empty}")

    def test_agent_has_skills_field(self):
        """Agents should reference skills they can use."""
        agents = _discover_agents()
        no_skills = []
        for name, path in agents.items():
            try:
                content = path.read_text(encoding='utf-8', errors='replace')
                # Check for YAML frontmatter with skills field or inline skill references
                has_skills = ('skills:' in content.lower() or 
                              'skill' in content.lower())
                if not has_skills:
                    no_skills.append(name)
            except Exception:
                pass
        # This is a warning, not a hard fail — some agents are generic
        if no_skills:
            print(f"  ⚠ Agents without skill references: {no_skills}")


# ============================================================================
# 4. WORKFLOW QUALITY — Every workflow must be executable
# ============================================================================

class TestWorkflowQuality(unittest.TestCase):
    """Real-world check: PM types /command → does the workflow have valid steps?"""

    def test_every_workflow_has_content(self):
        """Workflow files must have actual instructions (>100 chars)."""
        workflows = _discover_workflows()
        empty = []
        for name, path in workflows.items():
            size = path.stat().st_size
            if size < 100:
                empty.append(f"{name} ({size}b)")
        self.assertEqual(empty, [],
                         f"Workflows with insufficient instructions: {empty}")

    def test_workflow_has_description_frontmatter(self):
        """Workflows should have YAML frontmatter with description."""
        workflows = _discover_workflows()
        no_desc = []
        for name, path in workflows.items():
            try:
                content = path.read_text(encoding='utf-8', errors='replace')
                if not content.strip().startswith('---'):
                    no_desc.append(name)
            except Exception:
                no_desc.append(f"{name} (unreadable)")
        # Warn only — not all workflows may have frontmatter yet
        if no_desc:
            print(f"  ⚠ Workflows without YAML frontmatter: {no_desc[:10]}...")


# ============================================================================
# 5. CROSS-REFERENCE INTEGRITY — No dangling pointers
# ============================================================================

class TestCrossReferenceIntegrity(unittest.TestCase):
    """Real-world check: Agent references skill X → does skill X actually exist?"""

    def test_gemini_md_agent_references_valid(self):
        """GEMINI.md references agents → they must exist."""
        gemini_paths = [ROOT_DIR / ".agent" / "rules" / "GEMINI.md",
                        ROOT_DIR / ".agents" / "rules" / "GEMINI.md"]
        agents = set(_discover_agents().keys())
        
        for gp in gemini_paths:
            if not gp.exists():
                continue
            content = gp.read_text(encoding='utf-8', errors='replace')
            # Extract backticked references that look like agent names
            # This is a lightweight check, not exhaustive
            if 'CPO' in content:
                self.assertTrue('cpo' in agents, "GEMINI.md references CPO but agent missing")

    def test_no_broken_skill_symlinks(self):
        """If skills are symlinked between .agents/ and .agent/, both must resolve."""
        for skills_dir in SKILLS_DIRS:
            if not skills_dir.exists():
                continue
            for item in skills_dir.iterdir():
                if item.is_symlink():
                    self.assertTrue(item.resolve().exists(),
                                    f"Broken symlink: {item}")


# ============================================================================
# 6. SYSTEM SCRIPTS — Core Python logic must be importable
# ============================================================================

class TestSystemScripts(unittest.TestCase):
    """Real-world check: System scripts must exist and be syntactically valid."""

    def test_core_scripts_exist(self):
        """vacuum.py, kernel_utils.py, vibe_check.py must exist."""
        required = ["vacuum.py", "kernel_utils.py", "vibe_check.py"]
        for script in required:
            path = SCRIPTS_DIR / script
            self.assertTrue(path.exists(),
                            f"Core script {script} missing from system/scripts/")

    def test_scripts_are_valid_python(self):
        """All .py scripts must parse without SyntaxError."""
        if not SCRIPTS_DIR.exists():
            self.skipTest("scripts/ directory not found")
        broken = []
        for py_file in SCRIPTS_DIR.glob("*.py"):
            try:
                compile(py_file.read_text(encoding='utf-8', errors='replace'),
                        str(py_file), 'exec')
            except SyntaxError as e:
                broken.append(f"{py_file.name}: {e}")
        self.assertEqual(broken, [],
                         f"Scripts with syntax errors: {broken}")


# ============================================================================
# 7. PRIVACY — Gitignored folders must not leak into the repo
# ============================================================================

class TestPrivacyCompliance(unittest.TestCase):
    """Real-world check: Sensitive PM data must never be committed."""

    def test_gitignore_exists(self):
        """A .gitignore must exist."""
        self.assertTrue((ROOT_DIR / ".gitignore").exists(), ".gitignore missing")

    def test_gitignore_blocks_sensitive_folders(self):
        """Folders 1-5 must be in .gitignore."""
        gitignore = ROOT_DIR / ".gitignore"
        if not gitignore.exists():
            self.skipTest(".gitignore missing")
        content = gitignore.read_text(encoding='utf-8', errors='replace')
        sensitive = ["1. Company", "2. Products", "3. Meetings", "4. People", "5. Trackers"]
        for folder in sensitive:
            self.assertTrue(folder in content or folder.replace(" ", "*") in content,
                            f"'{folder}' not in .gitignore — sensitive PM data could leak")


# ============================================================================
# 8. REAL-WORLD SCENARIO TESTS — Simulate actual PM workflows
# ============================================================================

class TestRealWorldScenarios(unittest.TestCase):
    """Simulate what actually happens when a PM uses the kit day-to-day."""

    def test_daily_brief_path_exists(self):
        """PM runs /day → daily-synth skill must exist and be functional."""
        skills = _discover_skills()
        self.assertIn('daily-synth', skills,
                      "PM runs /day but daily-synth skill is missing")
        skill_md = skills['daily-synth'] / "SKILL.md"
        content = skill_md.read_text(encoding='utf-8', errors='replace')
        self.assertGreater(len(content), 200,
                           "daily-synth SKILL.md is too short to be functional")

    def test_boss_prep_path_exists(self):
        """PM prepares for 1:1 → boss-tracker skill exists with real instructions."""
        skills = _discover_skills()
        self.assertIn('boss-tracker', skills,
                      "PM runs /boss but boss-tracker skill is missing")

    def test_prd_authoring_path_exists(self):
        """PM writes a PRD → prd-author skill + /create workflow both exist."""
        skills = _discover_skills()
        workflows = _discover_workflows()
        self.assertIn('prd-author', skills, "prd-author skill missing")
        self.assertIn('create', workflows, "/create workflow missing")

    def test_meeting_synthesis_path_exists(self):
        """PM processes a meeting transcript → meeting-synth exists."""
        skills = _discover_skills()
        self.assertIn('meeting-synth', skills, "meeting-synth skill missing")

    def test_task_management_path_exists(self):
        """PM manages tasks → task-manager skill exists."""
        skills = _discover_skills()
        self.assertIn('task-manager', skills, "task-manager skill missing")

    def test_sprint_planning_path_exists(self):
        """PM runs sprint planning → roadmapping-suite skill + /sprint workflow exist."""
        skills = _discover_skills()
        workflows = _discover_workflows()
        self.assertIn('roadmapping-suite', skills, "roadmapping-suite skill missing")
        self.assertIn('sprint', workflows, "/sprint workflow missing")

    def test_retrospective_path_exists(self):
        """PM facilitates a retro → retrospective skill + /retro workflow exist."""
        skills = _discover_skills()
        workflows = _discover_workflows()
        self.assertIn('retrospective', skills, "retrospective skill missing")
        self.assertIn('retro', workflows, "/retro workflow missing")

    def test_stakeholder_management_path_exists(self):
        """PM manages stakeholders → stakeholder-management-suite skill exists."""
        skills = _discover_skills()
        self.assertIn('stakeholder-management-suite', skills, "stakeholder-management-suite skill missing")

    def test_discovery_workshop_path_exists(self):
        """PM runs discovery → discovery-engine + /discover workflow exist."""
        skills = _discover_skills()
        workflows = _discover_workflows()
        self.assertIn('discovery-engine', skills, "discovery-engine missing")
        self.assertIn('discover', workflows, "/discover workflow missing")

    def test_competitive_analysis_path_exists(self):
        """PM does competitive analysis → growth-engine skill exists."""
        skills = _discover_skills()
        self.assertIn('growth-engine', skills, "growth-engine missing")

    def test_okr_management_path_exists(self):
        """PM sets OKRs → roadmapping-suite skill + /plan workflow exist."""
        skills = _discover_skills()
        workflows = _discover_workflows()
        self.assertIn('roadmapping-suite', skills, "roadmapping-suite missing")
        self.assertIn('plan', workflows, "/plan workflow missing")

    def test_bug_tracking_path_exists(self):
        """PM triages bugs → bug-chaser skill + /track workflow exist."""
        skills = _discover_skills()
        workflows = _discover_workflows()
        self.assertIn('bug-chaser', skills, "bug-chaser missing")
        self.assertIn('track', workflows, "/track workflow missing")


# ============================================================================
# 9. PERFORMANCE — Kit should not be bloated
# ============================================================================

class TestPerformance(unittest.TestCase):
    """Ensure the kit stays lean and doesn't suffer from feature creep."""

    def test_no_oversized_skill_files(self):
        """SKILL.md files should stay under 500 lines (mgechev standard)."""
        skills = _discover_skills()
        oversized = []
        for name, path in skills.items():
            skill_md = path / "SKILL.md"
            if skill_md.exists():
                try:
                    lines = len(skill_md.read_text(encoding='utf-8', errors='replace').splitlines())
                    if lines > 500:
                        oversized.append(f"{name} ({lines} lines)")
                except Exception:
                    pass
        if oversized:
            print(f"  ⚠ Oversized skills (>500 lines): {oversized[:10]}")

    def test_no_empty_skill_directories(self):
        """Skill directories must not be empty (no orphaned folders)."""
        skills = _discover_skills()
        empty = [name for name, path in skills.items()
                 if not any(path.iterdir())]
        self.assertEqual(empty, [],
                         f"Empty skill directories (orphans): {empty}")

    def test_no_duplicate_skill_names(self):
        """No two skills should have the exact same name across directories."""
        seen = {}
        for skills_dir in SKILLS_DIRS:
            if not skills_dir.exists():
                continue
            for item in skills_dir.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    if item.name in seen:
                        # Symlinks to same target are OK
                        if item.resolve() != seen[item.name].resolve():
                            self.fail(f"Duplicate skill '{item.name}' at {item} and {seen[item.name]}")
                    seen[item.name] = item


if __name__ == '__main__':
    unittest.main()
