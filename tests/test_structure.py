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
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
system_path = os.path.join(repo_root, "Beats-PM-System", "system")
sys.path.insert(0, system_path)

# Import real config module
# We need to make sure utils is importable.
# The folder structure is Beats-PM-System/system/utils/config.py
# So if we are in 'system', we import 'utils.config'.

from utils import config

class TestSystemStructure(unittest.TestCase):
    
    def setUp(self):
        # Ensure we are testing the actual repo root
        self.root = repo_root
        
        # Inject the root into config so it doesn't try to guess or use CWD incorrectly if we ran from elsewhere
        # config.py has a default logic, but we can override path resolution if needed.
        # But for now, let's rely on config.py's detection or relative paths.
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
        """Verify KERNEL, SETTINGS, and Mesh exist."""
        crit_files = [
            "KERNEL.md",
            "SETTINGS.md",
            "Beats-PM-System/system/agents/mesh.toml",
            "Beats-PM-System/requirements.txt"
        ]
        
        missing = []
        for f in crit_files:
            full_path = os.path.join(self.root, f)
            if not os.path.exists(full_path):
                missing.append(f)
                
        self.assertEqual(len(missing), 0, f"Missing critical files: {missing}")

    def test_mesh_validity(self):
        """Verify mesh.toml is valid TOML (if toml lib installed) or basic parsing."""
        mesh_path = os.path.join(self.root, "Beats-PM-System", "system", "agents", "mesh.toml")
        
        with open(mesh_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Basic validation: Check for [agents.*] sections
        self.assertIn("[agents.task_manager]", content)
        self.assertIn("[agents.meeting_synthesizer]", content)
        self.assertIn("prompt_file =", content)

    def test_agent_prompts_exist(self):
        """Verify that every agent defined in mesh.toml has a corresponding .md file."""
        mesh_path = os.path.join(self.root, "Beats-PM-System", "system", "agents", "mesh.toml")
        
        with open(mesh_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line in lines:
            if "prompt_file =" in line:
                # Extract path: prompt_file = "Beats-PM-System/system/agents/task-manager.md"
                path_str = line.split('=')[1].strip().strip('"')
                full_path = os.path.join(self.root, path_str)
                self.assertTrue(os.path.exists(full_path), f"Agent Prompt missing: {path_str}")

if __name__ == '__main__':
    unittest.main()
