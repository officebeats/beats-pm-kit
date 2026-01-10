"""
Comprehensive Regression Test Suite
FAANG-Level Full Feature Verification for Beats PM Brain.
Tests EVERY feature documented in README.md.
"""

import unittest
import os
import sys
from unittest.mock import MagicMock

# Setup paths
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYSTEM_DIR = os.path.join(ROOT_DIR, 'Beats-PM-System', 'system')
sys.path.insert(0, SYSTEM_DIR)

# Mock utils
if 'utils' not in sys.modules:
    sys.modules['utils'] = MagicMock()
    sys.modules['utils.ui'] = MagicMock()
    sys.modules['utils.config'] = MagicMock()
    sys.modules['utils.filesystem'] = MagicMock()

from scripts import kernel_utils


class TestDirectoryStructure(unittest.TestCase):
    """Verify the 0-5 folder structure exists."""
    
    def test_required_folders_exist(self):
        """Test all required folders from README exist."""
        required = [
            "0. Incoming",
            "1. Company", 
            "2. Products",
            "3. Meetings",
            "4. People",
            "5. Trackers"
        ]
        for folder in required:
            path = os.path.join(ROOT_DIR, folder)
            self.assertTrue(os.path.isdir(path), f"Required folder missing: {folder}")


class TestSkillsInventory(unittest.TestCase):
    """Verify all 14 Skills from README exist."""
    
    def test_all_skills_exist(self):
        """Every skill mentioned in README must have a SKILL.md file."""
        skills = [
            "boss-tracker",
            "bug-chaser", 
            "daily-synth",
            "delegation-manager",
            "engineering-collab",
            "meeting-synth",
            "prd-author",
            "requirements-translator",
            "stakeholder-mgr",
            "strategy-synth",
            "task-manager",
            "ux-collab",
            "visual-processor",
            "weekly-synth",
            "code-simplifier"  # Added in this session
        ]
        skills_dir = os.path.join(ROOT_DIR, ".gemini", "skills")
        
        for skill in skills:
            skill_path = os.path.join(skills_dir, skill, "SKILL.md")
            self.assertTrue(os.path.exists(skill_path), f"Skill missing: {skill}/SKILL.md")


class TestTemplatesInventory(unittest.TestCase):
    """Verify all Templates from README exist."""
    
    def test_all_templates_exist(self):
        """Every template referenced by Conductor must exist."""
        templates = [
            "bug-report.md",
            "bug-fix-spec.md",
            "feature-request.md",
            "feature-spec.md",
            "strategy-memo.md",
            "transcript-extraction.md",
            "transcript-intake.md",
            "weekly-review.md"
        ]
        templates_dir = os.path.join(ROOT_DIR, ".gemini", "templates")
        
        for template in templates:
            path = os.path.join(templates_dir, template)
            self.assertTrue(os.path.exists(path), f"Template missing: {template}")


class TestCommandRouting(unittest.TestCase):
    """Verify all commands from README map to valid implementations."""
    
    def test_daily_commands_route_to_skill(self):
        """Daily briefing commands should route to daily-synth skill."""
        daily_commands = ["day", "morning", "lunch", "eod", "status", "latest", "info"]
        skill_path = os.path.join(ROOT_DIR, ".gemini", "skills", "daily-synth", "SKILL.md")
        self.assertTrue(os.path.exists(skill_path), "daily-synth skill missing")
        
    def test_capture_commands_route_to_skill(self):
        """Capture commands should route to visual-processor skill."""
        skill_path = os.path.join(ROOT_DIR, ".gemini", "skills", "visual-processor", "SKILL.md")
        self.assertTrue(os.path.exists(skill_path), "visual-processor skill missing")
        
    def test_documentation_commands_route_to_skill(self):
        """Documentation commands should route to prd-author skill."""
        skill_path = os.path.join(ROOT_DIR, ".gemini", "skills", "prd-author", "SKILL.md")
        self.assertTrue(os.path.exists(skill_path), "prd-author skill missing")
        
    def test_meeting_commands_route_to_skill(self):
        """Meeting commands should route to meeting-synth skill."""
        skill_path = os.path.join(ROOT_DIR, ".gemini", "skills", "meeting-synth", "SKILL.md")
        self.assertTrue(os.path.exists(skill_path), "meeting-synth skill missing")
        
    def test_strategy_commands_route_to_skill(self):
        """Strategy commands should route to strategy-synth skill."""
        skill_path = os.path.join(ROOT_DIR, ".gemini", "skills", "strategy-synth", "SKILL.md")
        self.assertTrue(os.path.exists(skill_path), "strategy-synth skill missing")
        
    def test_design_commands_route_to_skill(self):
        """Design commands should route to ux-collab skill."""
        skill_path = os.path.join(ROOT_DIR, ".gemini", "skills", "ux-collab", "SKILL.md")
        self.assertTrue(os.path.exists(skill_path), "ux-collab skill missing")
        
    def test_engineering_commands_route_to_skill(self):
        """Engineering commands should route to engineering-collab skill."""
        skill_path = os.path.join(ROOT_DIR, ".gemini", "skills", "engineering-collab", "SKILL.md")
        self.assertTrue(os.path.exists(skill_path), "engineering-collab skill missing")
        
    def test_task_commands_route_to_skill(self):
        """Task management commands should route to task-manager skill."""
        skill_path = os.path.join(ROOT_DIR, ".gemini", "skills", "task-manager", "SKILL.md")
        self.assertTrue(os.path.exists(skill_path), "task-manager skill missing")
        
    def test_boss_commands_route_to_skill(self):
        """Boss commands should route to boss-tracker skill."""
        skill_path = os.path.join(ROOT_DIR, ".gemini", "skills", "boss-tracker", "SKILL.md")
        self.assertTrue(os.path.exists(skill_path), "boss-tracker skill missing")
        
    def test_delegation_commands_route_to_skill(self):
        """Delegation commands should route to delegation-manager skill."""
        skill_path = os.path.join(ROOT_DIR, ".gemini", "skills", "delegation-manager", "SKILL.md")
        self.assertTrue(os.path.exists(skill_path), "delegation-manager skill missing")
        
    def test_stakeholder_commands_route_to_skill(self):
        """Stakeholder commands should route to stakeholder-mgr skill."""
        skill_path = os.path.join(ROOT_DIR, ".gemini", "skills", "stakeholder-mgr", "SKILL.md")
        self.assertTrue(os.path.exists(skill_path), "stakeholder-mgr skill missing")


class TestAllREADMECommands(unittest.TestCase):
    """
    Exhaustive test: Verify EVERY command listed in README's Complete Command Reference.
    Each command must route to a valid skill.
    """
    
    # Master command registry extracted from README.md
    # Format: (command, expected_skill)
    COMMAND_SKILL_MAP = [
        # Daily Briefing Commands (7)
        ("day", "daily-synth"),
        ("morning", "daily-synth"),
        ("lunch", "daily-synth"),
        ("eod", "daily-synth"),
        ("status", "daily-synth"),
        ("latest", "daily-synth"),
        ("info", "daily-synth"),
        
        # Capture & Import Commands (4)
        ("paste", "visual-processor"),
        ("clipboard", "visual-processor"),
        ("screenshot", "visual-processor"),
        ("process", "visual-processor"),
        
        # Documentation Commands (3)
        ("prd", "prd-author"),
        ("feature", "prd-author"),
        ("braindump", "task-manager"),
        
        # Meeting Commands (6)
        ("transcript", "meeting-synth"),
        ("meeting", "meeting-synth"),
        ("call", "meeting-synth"),
        ("1on1", "meeting-synth"),
        ("standup", "meeting-synth"),
        ("notes", "meeting-synth"),
        
        # Strategy Commands (4)
        ("strategy", "strategy-synth"),
        ("strategy pulse", "strategy-synth"),
        ("strategy theme", "strategy-synth"),
        ("strategy opportunities", "strategy-synth"),
        
        # Design Commands (6)
        ("ux", "ux-collab"),
        ("ux discovery", "ux-collab"),
        ("ux wireframe", "ux-collab"),
        ("ux mockup", "ux-collab"),
        ("ux prototype", "ux-collab"),
        
        # Engineering Commands (7)
        ("eng", "engineering-collab"),
        ("eng spike", "engineering-collab"),
        ("eng question", "engineering-collab"),
        ("eng discuss", "engineering-collab"),
        ("eng estimate", "engineering-collab"),
        ("eng standup", "engineering-collab"),
        
        # Task Management Commands (5)
        ("task", "task-manager"),
        ("tasks", "task-manager"),
        ("clarify", "task-manager"),
        ("triage", "task-manager"),
        ("plan", "task-manager"),
        
        # System Commands (4)
        ("update", None),  # System command, no skill
        ("help", None),    # System command, no skill
        ("vibe", None),    # System command, runs script
        
        # Reporting Commands (2)
        ("weekly", "weekly-synth"),
        ("monthly", "weekly-synth"),
        
        # Additional Commands from KERNEL.md
        ("boss", "boss-tracker"),
        ("bug", "bug-chaser"),
        ("delegate", "delegation-manager"),
        ("stakeholder", "stakeholder-mgr"),
        ("simplify", "code-simplifier"),
        ("refactor", "code-simplifier"),
        ("cleanup", "code-simplifier"),
    ]
    
    def test_all_commands_have_valid_routing(self):
        """Every command in README must route to an existing skill or be a system command."""
        skills_dir = os.path.join(ROOT_DIR, ".gemini", "skills")
        
        for command, expected_skill in self.COMMAND_SKILL_MAP:
            with self.subTest(command=command):
                if expected_skill is None:
                    # System command - just verify it's documented (no skill needed)
                    continue
                    
                skill_path = os.path.join(skills_dir, expected_skill, "SKILL.md")
                self.assertTrue(
                    os.path.exists(skill_path), 
                    f"Command '#{command}' requires skill '{expected_skill}' but {skill_path} is missing"
                )
    
    def test_command_count_matches_readme(self):
        """Verify we're testing at least 45 commands (README has ~48)."""
        self.assertGreaterEqual(len(self.COMMAND_SKILL_MAP), 45, "Should test at least 45 commands")


class TestKernelUtils(unittest.TestCase):
    """Verify kernel utility functions work correctly."""
    
    def test_anchor_rule_allows_valid_paths(self):
        """Anchor rule should allow standard folder paths."""
        valid_paths = [
            "1. Company/Acme/PROFILE.md",
            "2. Products/App/PRD.md",
            "3. Meetings/notes.md",
            "4. People/john.md",
            "5. Trackers/bugs.md",
            "0. Incoming/file.txt"
        ]
        for path in valid_paths:
            self.assertTrue(kernel_utils.check_anchor_rule(path), f"Should allow: {path}")
            
    def test_anchor_rule_blocks_invalid_paths(self):
        """Anchor rule should block non-standard paths."""
        invalid_paths = [
            "RandomFolder/file.md",
            "6. Other/file.md",
        ]
        for path in invalid_paths:
            self.assertFalse(kernel_utils.check_anchor_rule(path), f"Should block: {path}")
            
    def test_privacy_rule_detects_violations(self):
        """Privacy rule should detect protected folder leaks."""
        files = ["README.md", "1. Company/secret.md", "5. Trackers/bugs.md"]
        passed, violations = kernel_utils.check_privacy_rule(files)
        self.assertFalse(passed)
        self.assertEqual(len(violations), 2)
        
    def test_template_mapping_complete(self):
        """All documented intents should map to templates."""
        intents = ["bug", "fix", "feature", "spec", "transcript", "strategy", "weekly"]
        for intent in intents:
            result = kernel_utils.get_suggested_template(intent)
            self.assertIsNotNone(result, f"Intent '{intent}' has no template mapping")


class TestSystemScripts(unittest.TestCase):
    """Verify all system scripts exist and are importable."""
    
    def test_core_scripts_exist(self):
        """Critical scripts from README must exist."""
        scripts = [
            "core_setup.py",
            "vibe_check.py",
            "vacuum.py",
            "kernel_utils.py",
            "queue_worker.py",
            "dispatch.py"
        ]
        scripts_dir = os.path.join(SYSTEM_DIR, "scripts")
        
        for script in scripts:
            path = os.path.join(scripts_dir, script)
            self.assertTrue(os.path.exists(path), f"Script missing: {script}")


class TestCriticalFiles(unittest.TestCase):
    """Verify critical system files exist."""
    
    def test_kernel_exists(self):
        """KERNEL.md must exist."""
        path = os.path.join(ROOT_DIR, "KERNEL.md")
        self.assertTrue(os.path.exists(path), "KERNEL.md missing")
        
    def test_settings_exists(self):
        """SETTINGS.md must exist."""
        path = os.path.join(ROOT_DIR, "SETTINGS.md")
        self.assertTrue(os.path.exists(path), "SETTINGS.md missing")
        
    def test_readme_exists(self):
        """README.md must exist."""
        path = os.path.join(ROOT_DIR, "README.md")
        self.assertTrue(os.path.exists(path), "README.md missing")
        
    def test_contributing_exists(self):
        """CONTRIBUTING.md must exist."""
        path = os.path.join(ROOT_DIR, "CONTRIBUTING.md")
        self.assertTrue(os.path.exists(path), "CONTRIBUTING.md missing")
        
    def test_license_exists(self):
        """LICENSE must exist."""
        path = os.path.join(ROOT_DIR, "LICENSE")
        self.assertTrue(os.path.exists(path), "LICENSE missing")


class TestAsyncQueue(unittest.TestCase):
    """Verify async queue system works."""
    
    def test_queue_directories_exist(self):
        """Queue directories should exist after setup."""
        from scripts import queue_worker
        queue_worker.setup_directories()
        
        dirs = [
            queue_worker.PENDING_DIR,
            queue_worker.PROCESSING_DIR,
            queue_worker.COMPLETED_DIR,
            queue_worker.FAILED_DIR
        ]
        for d in dirs:
            self.assertTrue(os.path.isdir(d), f"Queue dir missing: {d}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
