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
from pathlib import Path

# Add system path
# Add system path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
system_path = os.path.join(repo_root, "system")
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
        
        vacuum.TRACKERS_DIR = Path(self.test_dir)
        vacuum.ARCHIVE_DIR = Path(os.path.join(self.test_dir, "archive"))
        
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
        
        # We need to simulate the file existing and having content, then reading it back.
        # Since vacuum uses open(), we should ideally create the real file in test_dir (which we do in setUp + write)
        # BUT the previous test implementation tried to mock everything.
        
        # Let's use REAL file operations for the target file, but mock the archive writing if needed.
        # vacuum.vacuum_tracker actually uses open() for everything.
        
        content = """# Tasks
- [ ] Active task 1
- [x] Completed task 1
- [ ] Active task 2
- [x] Completed task 2
"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
        # We want vacuum to run on this real file.
        # vacuum.vacuum_tracker prints stuff, maybe silence it?
        
        with patch('builtins.print'):
             # We assume vacuum works on real files now, since we removed the mock imports in previous logic thoughts
             # But wait, vacuum writes to ARCHIVE_DIR.
             count = vacuum.vacuum_tracker(filename)
             
             self.assertEqual(count, 2)
            
            # Verify active file content
             with open(filepath, 'r', encoding='utf-8') as f:
                new_content = f.read()
            
             self.assertIn("- [ ] Active task 1", new_content)
             self.assertNotIn("- [x] Completed task 1", new_content)
            
            # Verify archive exists
             archive_files = os.listdir(vacuum.ARCHIVE_DIR)
             self.assertTrue(len(archive_files) > 0)
             archive_content = open(os.path.join(vacuum.ARCHIVE_DIR, archive_files[0]), encoding='utf-8').read()
             self.assertIn("- [x] Completed task 1", archive_content)

    def test_archive_transcripts(self):
        """Test transcript archiving logic."""
        # Setup mock directories (real ones in temp dir)
        meetings_dir = os.path.join(self.test_dir, "3. Meetings")
        transcripts_dir = os.path.join(meetings_dir, "transcripts")
        summaries_dir = os.path.join(meetings_dir, "summaries")
        archive_dir = os.path.join(meetings_dir, "archive")
        
        os.makedirs(transcripts_dir)
        os.makedirs(summaries_dir)
        os.makedirs(archive_dir)
        
        # Override vacuum's MEETINGS_DIR to point to our test dir
        # Override vacuum's MEETINGS_DIR to point to our test dir
        with patch('scripts.vacuum.MEETINGS_DIR', Path(meetings_dir)), \
             patch('scripts.vacuum.update_index') as mock_update_index:
             
            # Create old and new files
            now = time.time()
            one_day_ago = now - (24 * 60 * 60)
            four_hundred_days_ago = now - (400 * 24 * 60 * 60)
            
            # New file (Hot -> Warm?) No, logic is > 30 days
            # Hot file (New)
            new_file = os.path.join(transcripts_dir, "new.md")
            with open(new_file, 'w') as f: f.write("new")
            # Touch time
            
            # Old file (Hot -> Warm, > 30 days)
            old_file = os.path.join(transcripts_dir, "old.md")
            with open(old_file, 'w') as f: f.write("old")
            os.utime(old_file, (four_hundred_days_ago, four_hundred_days_ago))
            
            # Run archive
            vacuum.manage_tiered_memory()
            
            # Assertions
            # old.md is 400 days old, so it moves Hot -> Warm -> Cold (Archive)
            self.assertTrue(os.path.exists(os.path.join(archive_dir, "old.md")), "old.md not found in archive (Cold Storage)!")
            
            # new.md should still be in transcripts
            self.assertTrue(os.path.exists(new_file))

if __name__ == '__main__':
    unittest.main()
