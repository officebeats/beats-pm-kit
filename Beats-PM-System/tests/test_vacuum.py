"""
Tests for vacuum.py script.
"""

import unittest
import sys
import os
import shutil
import tempfile
import time
from datetime import datetime, timedelta

# Add system path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
system_path = os.path.join(repo_root, "Beats-PM-System", "system")
sys.path.insert(0, system_path)

# Mock config and utils before importing vacuum
from unittest.mock import MagicMock, patch
import types

# Create a dummy package for utils
utils = types.ModuleType("utils")
sys.modules["utils"] = utils

# Create submodules
utils.ui = MagicMock()
utils.config = MagicMock()
utils.filesystem = MagicMock()
utils.subprocess_helper = MagicMock()

# helper to mock specific functions within those modules if needed
# But vacuum imports them directly: "from utils.filesystem import ensure_directory"
# So we need to make sure those attributes exist on the mocks.
# We will do that by just assigning them to the modules in sys.modules, 
# or letting the MagicMock handle it (which it does by default).

# We also need to ensure that subsequent imports of "utils.filesystem" work.
sys.modules["utils.ui"] = utils.ui
sys.modules["utils.config"] = utils.config
sys.modules["utils.filesystem"] = utils.filesystem

# Define methods on the mock filesystem module so they can be imported
utils.filesystem.file_exists = MagicMock(return_value=True)
utils.filesystem.directory_exists = MagicMock(return_value=True)
utils.filesystem.ensure_directory = MagicMock(return_value=True)
utils.filesystem.read_file = MagicMock(return_value="")
utils.filesystem.write_file = MagicMock(return_value=True)
utils.filesystem.append_file = MagicMock(return_value=True)
utils.filesystem.copy_file = MagicMock(return_value=True)
utils.filesystem.delete_file = MagicMock(return_value=True)

sys.modules["utils.subprocess_helper"] = utils.subprocess_helper

# Import the script to be tested
import scripts.vacuum as vacuum

class TestVacuum(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        
        # Override constants for testing
        self.original_trackers_dir = vacuum.TRACKERS_DIR
        self.original_archive_dir = vacuum.ARCHIVE_DIR
        
        vacuum.TRACKERS_DIR = self.test_dir
        vacuum.ARCHIVE_DIR = os.path.join(self.test_dir, "archive")
        
        # Ensure archive dir exists
        os.makedirs(vacuum.ARCHIVE_DIR)

    def tearDown(self):
        vacuum.TRACKERS_DIR = self.original_trackers_dir
        vacuum.ARCHIVE_DIR = self.original_archive_dir
        shutil.rmtree(self.test_dir)

    def test_vacuum_tracker_file(self):
        """Test that completed items are moved to archive."""
        filename = "test_tasks.md"
        filepath = os.path.join(self.test_dir, filename)
        
        content = """# Tasks
- [ ] Active task 1
- [x] Completed task 1
- [ ] Active task 2
- [x] Completed task 2
"""
        with open(filepath, 'w') as f:
            f.write(content)
            
        # Mock dependencies that vacuum uses
        with patch('scripts.vacuum.read_file', side_effect=lambda x: open(x).read()), \
             patch('scripts.vacuum.write_file', side_effect=lambda x, y: open(x, 'w').write(y)), \
             patch('scripts.vacuum.append_file', return_value=True) as mock_append, \
             patch('scripts.vacuum.file_exists', return_value=True):
             
            vacuum.vacuum_file(filename)
            
            # Verify active file content
            with open(filepath, 'r') as f:
                new_content = f.read()
            
            self.assertIn("- [ ] Active task 1", new_content)
            self.assertNotIn("- [x] Completed task 1", new_content)
            
            # Verify usage of append to archive (since we mocked it)
            self.assertTrue(mock_append.called)
            args, _ = mock_append.call_args
            self.assertIn("- [x] Completed task 1", args[1])

    def test_archive_transcripts(self):
        """Test transcript archiving logic."""
        # Setup mock directories
        meetings_dir = os.path.join(self.test_dir, "3. Meetings")
        transcripts_dir = os.path.join(meetings_dir, "transcripts")
        archive_dir = os.path.join(meetings_dir, "archive")
        
        os.makedirs(transcripts_dir)
        os.makedirs(archive_dir)
        
        # Override vacuum's ROOT_DIR to point to our test dir logic
        # vacuum.ROOT_DIR is determined at import time. We need to patch it or the os.path.join usage.
        # vacuum.archive_transcripts uses ROOT_DIR.
        
        with patch('scripts.vacuum.ROOT_DIR', self.test_dir):
            # Create old and new files
            now = time.time()
            one_day_ago = now - (24 * 60 * 60)
            four_hundred_days_ago = now - (400 * 24 * 60 * 60)
            
            # New file
            new_file = os.path.join(transcripts_dir, "new.txt")
            with open(new_file, 'w') as f: f.write("new")
            os.utime(new_file, (one_day_ago, one_day_ago))
            
            # Old file
            old_file = os.path.join(transcripts_dir, "old.txt")
            with open(old_file, 'w') as f: f.write("old")
            os.utime(old_file, (four_hundred_days_ago, four_hundred_days_ago))
            
            # Run archive
            # We need to use Real filesystem functions for this specific test because we are testing file movement on disk
            # But the vacuum script imports them. 
            # We already MOCKED them in setUp Module level... this is tricky.
            
            # Strategy: We mocked the MODULE imports. 
            # vacuum.read_file is correct because we patched it in the previous test method, but here we want to run archive_transcripts.
            # archive_transcripts imports copy_file, delete_file, directory_exists etc from utils.filesystem.
            
            # We need to mock those to simulate the actions OR unpatch them.
            # Since we did sys.modules["utils..."] = MagicMock(), we can't easily unpatch.
            # So we must mock valid returns.
            
            with patch('scripts.vacuum.directory_exists', return_value=True), \
                 patch('scripts.vacuum.ensure_directory', return_value=True), \
                 patch('scripts.vacuum.copy_file', return_value=True) as mock_copy, \
                 patch('scripts.vacuum.delete_file', return_value=True) as mock_delete, \
                 patch('os.listdir', return_value=["new.txt", "old.txt"]), \
                 patch('os.path.isfile', return_value=True), \
                 patch('os.path.getmtime') as mock_mtime:
                 
                def side_effect_mtime(path):
                    if "new.txt" in path: return one_day_ago
                    if "old.txt" in path: return four_hundred_days_ago
                    return now
                mock_mtime.side_effect = side_effect_mtime
                
                vacuum.archive_transcripts()
                
                # Assertions
                # old.txt should be copied then deleted
                mock_copy.assert_called()
                args_copy, _ = mock_copy.call_args
                self.assertIn("old.txt", args_copy[0])
                self.assertIn("archive", args_copy[1])
                
                mock_delete.assert_called()
                args_delete, _ = mock_delete.call_args
                self.assertIn("old.txt", args_delete[0])

if __name__ == '__main__':
    unittest.main()
