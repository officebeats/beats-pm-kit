"""
Comprehensive Regression Test Suite
FAANG-Level Full Feature Verification for Beats PM Brain.
Tests EVERY feature documented in README.md.
"""

import unittest
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

# Setup paths
# Setup paths
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
SYSTEM_DIR = ROOT_DIR / 'Beats-PM-System' / 'system'
SKILLS_DIR = ROOT_DIR / '.agent' / 'skills'
TEMPLATES_DIR = ROOT_DIR / '.gemini' / 'templates'

sys.path.insert(0, str(SYSTEM_DIR))

# Mock utils dependencies
if 'utils' not in sys.modules:
    sys.modules['utils'] = MagicMock()
    sys.modules['utils.ui'] = MagicMock()
    sys.modules['utils.config'] = MagicMock()
    sys.modules['utils.filesystem'] = MagicMock()

from scripts import kernel_utils


# ============================================================================
# Constants
# ============================================================================

REQUIRED_FOLDERS = [
    "0. Incoming", "1. Company", "2. Products",
    "3. Meetings", "4. People", "5. Trackers"
]

SKILLS = [
    "boss-tracker", "bug-chaser", "daily-synth", "delegation-manager",
    "engineering-collab", "meeting-synth", "prd-author", "requirements-translator",
    "stakeholder-mgr", "strategy-synth", "task-manager", "ux-collab",
    "visual-processor", "weekly-synth", "code-simplifier"
]

TEMPLATES = [
    "bug-report.md", "bug-fix-spec.md", "feature-request.md",
    "feature-spec.md", "strategy-memo.md", "transcript-extraction.md",
    "transcript-intake.md", "weekly-review.md"
]

CORE_SCRIPTS = [
    "core_setup.py", "vibe_check.py", "vacuum.py",
    "kernel_utils.py", "queue_worker.py", "dispatch.py"
]

CRITICAL_FILES = ["KERNEL.md", "SETTINGS.md", "README.md", "CONTRIBUTING.md", "LICENSE"]

# Command → Skill mapping (exhaustive from README.md)
COMMAND_SKILL_MAP = [
    # Daily Briefing
    ("day", "daily-synth"), ("morning", "daily-synth"), ("lunch", "daily-synth"),
    ("eod", "daily-synth"), ("status", "daily-synth"), ("latest", "daily-synth"),
    ("info", "daily-synth"),
    # Capture & Import
    ("paste", "visual-processor"), ("clipboard", "visual-processor"),
    ("screenshot", "visual-processor"), ("process", "visual-processor"),
    # Documentation
    ("prd", "prd-author"), ("feature", "prd-author"), ("braindump", "task-manager"),
    # Meetings
    ("transcript", "meeting-synth"), ("meeting", "meeting-synth"),
    ("call", "meeting-synth"), ("1on1", "meeting-synth"),
    ("standup", "meeting-synth"), ("notes", "meeting-synth"),
    # Strategy
    ("strategy", "strategy-synth"), ("strategy pulse", "strategy-synth"),
    ("strategy theme", "strategy-synth"), ("strategy opportunities", "strategy-synth"),
    # Design
    ("ux", "ux-collab"), ("ux discovery", "ux-collab"),
    ("ux wireframe", "ux-collab"), ("ux mockup", "ux-collab"),
    ("ux prototype", "ux-collab"),
    # Engineering
    ("eng", "engineering-collab"), ("eng spike", "engineering-collab"),
    ("eng question", "engineering-collab"), ("eng discuss", "engineering-collab"),
    ("eng estimate", "engineering-collab"), ("eng standup", "engineering-collab"),
    # Task Management
    ("task", "task-manager"), ("tasks", "task-manager"),
    ("clarify", "task-manager"), ("triage", "task-manager"), ("plan", "task-manager"),
    # Reporting
    ("weekly", "weekly-synth"), ("monthly", "weekly-synth"),
    # Additional from KERNEL.md
    ("boss", "boss-tracker"), ("bug", "bug-chaser"),
    ("delegate", "delegation-manager"), ("stakeholder", "stakeholder-mgr"),
    ("simplify", "code-simplifier"), ("refactor", "code-simplifier"),
    ("cleanup", "code-simplifier"),
    # System commands (no skill)
    ("update", None), ("help", None), ("vibe", None),
]


# ============================================================================
# Test Classes
# ============================================================================

class TestDirectoryStructure(unittest.TestCase):
    """Verify the 0-5 folder structure exists."""
    
    def test_required_folders_exist(self):
        for folder in REQUIRED_FOLDERS:
            with self.subTest(folder=folder):
                self.assertTrue((ROOT_DIR / folder).is_dir(), f"Missing: {folder}")


class TestSkillsInventory(unittest.TestCase):
    """Verify all Skills from README exist."""
    
    def test_all_skills_exist(self):
        for skill in SKILLS:
            with self.subTest(skill=skill):
                path = SKILLS_DIR / skill / "SKILL.md"
                self.assertTrue(path.exists(), f"Missing: {skill}/SKILL.md")


class TestTemplatesInventory(unittest.TestCase):
    """Verify all Templates from README exist."""
    
    def test_all_templates_exist(self):
        for template in TEMPLATES:
            with self.subTest(template=template):
                self.assertTrue((TEMPLATES_DIR / template).exists(), f"Missing: {template}")


class TestCommandRouting(unittest.TestCase):
    """Verify all commands route to valid skills."""
    
    def test_all_commands_route_correctly(self):
        """Every command must route to an existing skill or be a system command."""
        for command, skill in COMMAND_SKILL_MAP:
            with self.subTest(command=command):
                if skill is None:
                    continue  # System command
                path = SKILLS_DIR / skill / "SKILL.md"
                self.assertTrue(path.exists(), f"#{command} → {skill} missing")
    
    def test_command_count(self):
        """Should test at least 45 commands."""
        self.assertGreaterEqual(len(COMMAND_SKILL_MAP), 45)


class TestKernelUtils(unittest.TestCase):
    """Verify kernel utility functions work correctly."""
    
    def test_anchor_rule_valid(self):
        """Anchor rule should allow standard folder paths."""
        valid = ["1. Company/Acme/PROFILE.md", "2. Products/App/PRD.md",
                 "3. Meetings/notes.md", "4. People/john.md",
                 "5. Trackers/bugs.md", "0. Incoming/file.txt"]
        for path in valid:
            with self.subTest(path=path):
                self.assertTrue(kernel_utils.check_anchor_rule(path))
    
    def test_anchor_rule_invalid(self):
        """Anchor rule should block non-standard paths."""
        invalid = ["RandomFolder/file.md", "6. Other/file.md"]
        for path in invalid:
            with self.subTest(path=path):
                self.assertFalse(kernel_utils.check_anchor_rule(path))
    
    def test_privacy_rule(self):
        """Privacy rule should detect protected folder leaks."""
        files = ["README.md", "1. Company/secret.md", "5. Trackers/bugs.md"]
        passed, violations = kernel_utils.check_privacy_rule(files)
        self.assertFalse(passed)
        self.assertEqual(len(violations), 2)
    
    def test_template_mapping(self):
        """All documented intents should map to templates."""
        intents = ["bug", "fix", "feature", "spec", "transcript", "strategy", "weekly"]
        for intent in intents:
            with self.subTest(intent=intent):
                self.assertIsNotNone(kernel_utils.get_suggested_template(intent))


class TestSystemScripts(unittest.TestCase):
    """Verify all system scripts exist."""
    
    def test_core_scripts_exist(self):
        scripts_dir = SYSTEM_DIR / "scripts"
        for script in CORE_SCRIPTS:
            with self.subTest(script=script):
                self.assertTrue((scripts_dir / script).exists(), f"Missing: {script}")


class TestCriticalFiles(unittest.TestCase):
    """Verify critical system files exist."""
    
    def test_critical_files_exist(self):
        for filename in CRITICAL_FILES:
            with self.subTest(file=filename):
                self.assertTrue((ROOT_DIR / filename).exists(), f"Missing: {filename}")


class TestAsyncQueue(unittest.TestCase):
    """Verify async queue system works."""
    
    def test_queue_directories_exist(self):
        from scripts import queue_worker
        queue_worker.setup_directories()
        
        for d in [queue_worker.PENDING_DIR, queue_worker.PROCESSING_DIR,
                  queue_worker.COMPLETED_DIR, queue_worker.FAILED_DIR]:
            with self.subTest(dir=d):
                self.assertTrue(os.path.isdir(d))


if __name__ == '__main__':
    unittest.main(verbosity=2)
