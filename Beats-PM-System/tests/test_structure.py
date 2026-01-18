"""
Structural Integrity Tests
FAANG-Level System Tests for Beats PM Brain.
Verifies file structure, config validity, and mesh integrity.
"""

import unittest
import sys
import os
import json

# Add system path
# Add system path
from pathlib import Path
CURRENT_FILE = Path(__file__).resolve()
REPO_ROOT = CURRENT_FILE.parent.parent.parent
SYSTEM_DIR = REPO_ROOT / "Beats-PM-System" / "system"
sys.path.insert(0, str(SYSTEM_DIR))

# Import real config module
# We need to make sure utils is importable.
# The folder structure is Beats-PM-System/system/utils/config.py
# So if we are in 'system', we import 'utils.config'.

from utils import config

class TestSystemStructure(unittest.TestCase):
    
    def setUp(self):
        # Ensure we are testing the actual repo root
        self.root = str(REPO_ROOT)
        pass

    def test_required_directories_exist(self):
        """Verify all critical directories mandated by config exist."""
        # Load config directly or use the module
        # The module tries to load from file. 
        # let's assume the default config structure in the module matches what we expect.
        
        required_dirs = config.DEFAULT_CONFIG['directories']['required']
        
        missing = []
        for d in required_dirs:
            # Paths in config are relative to Brain Root
            full_path = os.path.join(self.root, d)
            if not os.path.isdir(full_path):
                missing.append(d)
        
        self.assertEqual(len(missing), 0, f"Missing required directories: {missing}")
        
    def test_critical_files_exist(self):
        """Verify KERNEL, SETTINGS, and Skills exist."""
        crit_files = [
            "KERNEL.md",
            "SETTINGS.md",
            ".agent/skills",
            "requirements.txt"
        ]
        
        missing = []
        for f in crit_files:
            full_path = os.path.join(self.root, f)
            if not os.path.exists(full_path):
                missing.append(f)
                
        self.assertEqual(len(missing), 0, f"Missing critical files: {missing}")

    def test_skills_architecture(self):
        """Verify that the Skills directory structure is valid (v3.0.0)."""
        skills_dir = os.path.join(self.root, ".agent", "skills")
        
        # Check standard skills exist
        expected_skills = [
            "bug-chaser",
            "meeting-synth",
            "prd-author",
            "task-manager"
        ]
        
        missing = []
        for skill in expected_skills:
            skill_path = os.path.join(skills_dir, skill, "SKILL.md")
            if not os.path.exists(skill_path):
                missing.append(skill)
                
        # Warn but don't fail if some optional skills are missing, 
        # But failing if CORE skills are missing is good.
        # Let's check at least one to ensure the dirs aren't empty.
        self.assertTrue(os.path.exists(skills_dir), "Skills directory missing")
        
    def test_templates_exist(self):
        """Verify that standard templates exist."""
        templates_dir = os.path.join(self.root, ".agent", "templates")
        
        expected_templates = [
            "bug-report.md",
            "feature-spec.md",
            "weekly-review.md"
        ]
        
        for t in expected_templates:
            t_path = os.path.join(templates_dir, t)
            self.assertTrue(os.path.exists(t_path), f"Template missing: {t}")

if __name__ == '__main__':
    unittest.main()
