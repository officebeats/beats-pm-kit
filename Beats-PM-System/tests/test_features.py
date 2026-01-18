import unittest
import os
import sys
from unittest.mock import MagicMock

# Handle imports
from pathlib import Path

# Handle imports
CURRENT_FILE = Path(__file__).resolve()
TESTS_DIR = CURRENT_FILE.parent
SYSTEM_ROOT = TESTS_DIR.parent # Beats-PM-System
ROOT_DIR = SYSTEM_ROOT.parent # beats-pm-antigravity-brain

SYSTEM_DIR = SYSTEM_ROOT / 'system'
sys.path.insert(0, str(SYSTEM_DIR))

# Mock utils 
if 'utils' not in sys.modules:
    sys.modules['utils'] = MagicMock()
    sys.modules['utils.ui'] = MagicMock()
    sys.modules['utils.config'] = MagicMock()
    sys.modules['utils.filesystem'] = MagicMock()

from scripts import kernel_utils

class TestFeatureParity(unittest.TestCase):
    
    def test_full_command_inventory(self):
        """
        Regression Test: Verify EVERY SINGLE command in README maps to a concrete implementation.
        Source: README.md "Complete Command Reference" tables.
        """
        
        # 1. Skill Mappings (Command -> Skill Directory)
        # These commands rely on the 'Universal Orchestration' to route to a skill.
        skill_map = {
            # Daily Briefing
            "day": "daily-synth",
            "morning": "daily-synth",
            "lunch": "daily-synth",
            "eod": "daily-synth",
            "status": "daily-synth",
            
            # Meeting
            "transcript": "meeting-synth",
            "meeting": "meeting-synth",
            "call": "meeting-synth",
            "1on1": "meeting-synth",
            "standup": "meeting-synth",
            "notes": "meeting-synth",
            
            # Strategy
            "strategy": "chief-strategy-officer",
            
            # Design
            "ux": "ux-collab",
            
            # Eng
            "eng": "engineering-collab",
            
            # Task Management
            "task": "task-manager",
            "triage": "task-manager",
            "clarify": "task-manager",
            "plan": "task-manager",
            
            # Boss
            "boss": "boss-tracker",
            
            # Capture
            "paste": "visual-processor", # Or requirements-translator depending on content
            "screenshot": "visual-processor",
            
            # People
            "delegate": "delegation-manager",
            "stakeholder": "stakeholder-mgr",
        }
        
        skills_dir = os.path.join(ROOT_DIR, ".agent", "skills")
        for command, skill in skill_map.items():
            skill_path = os.path.join(skills_dir, skill, "SKILL.md")
            self.assertTrue(os.path.exists(skill_path), f"Command '#{command}' requires skill '{skill}', but {skill}/SKILL.md is missing.")

    def test_conductor_template_mapping(self):
        """
        Regression Test: Verify commands that trigger Templates via Conductor-First Protocol.
        """
        # Mapping from README "Template Enforcement Table" & Command Ref
        # Intent -> Template File
        template_map = {
            "bug": "bug-report.md",
            "fix": "bug-fix-spec.md",
            "feature": "feature-request.md",
            "spec": "feature-spec.md",
            "transcript": "transcript-extraction.md",
            "strategy": "strategy-memo.md",
            "weekly": "weekly-review.md" 
        }
        
        templates_dir = os.path.join(ROOT_DIR, ".agent", "templates")
        
        # 1. Check Files Exist on Disk
        for intent, filename in template_map.items():
            path = os.path.join(templates_dir, filename)
            self.assertTrue(os.path.exists(path), f"Intent '{intent}' needs template '{filename}'")

        # 2. Check Logic Mapping in kernel_utils
        # Ensure our python code actually knows about these mappings
        for intent, filename in template_map.items():
            mapped_path = kernel_utils.get_suggested_template(intent)
            expected_suffix = f".agent/templates/{filename}"
            self.assertTrue(mapped_path.replace("\\", "/").endswith(expected_suffix), 
                            f"kernel_utils.get_suggested_template('{intent}') returned {mapped_path}, expected to end with {expected_suffix}")

    def test_verify_scripts_existence(self):
        """Verify that critical scripts mentioned in README exist."""
        script_dir = os.path.join(SYSTEM_DIR, 'scripts')
        required_scripts = [
            'core_setup.py',
            'vibe_check.py',
            'vacuum.py',
            'kernel_utils.py'
        ]
        
        for script in required_scripts:
            path = os.path.join(script_dir, script)
            self.assertTrue(os.path.exists(path), f"Critical script {script} missing from {script_dir}")

if __name__ == '__main__':
    unittest.main()
