"""
Comprehensive tests for gps_indexer.py script.

Tests the Antigravity GPS Content Indexer that scans Brain folders (1-5)
to build a high-speed lookup table for O(1) document retrieval.
"""

import unittest
import sys
import os
import json
import shutil
import tempfile
import time
from pathlib import Path
from unittest.mock import patch, mock_open

# Handle imports from the hyphenated directory structure
CURRENT_FILE = Path(__file__).resolve()
SYSTEM_ROOT = CURRENT_FILE.parent.parent  # Beats-PM-System/
SYSTEM_DIR = SYSTEM_ROOT / "system"
sys.path.insert(0, str(SYSTEM_DIR))

# Import the script to be tested
from scripts import gps_indexer


class TestExtractTitle(unittest.TestCase):
    """Tests for the extract_title function."""

    def test_extract_title_with_h1_title(self):
        """Test extraction when H1 title exists."""
        content = "# My Document Title\n\nThis is some content."
        filename = "test-file.md"

        result = gps_indexer.extract_title(content, filename)

        self.assertEqual(result, "My Document Title")

    def test_extract_title_with_h1_and_extra_whitespace(self):
        """Test extraction with extra whitespace around H1."""
        content = "#    Whitespace Title   \n\nContent here."
        filename = "test-file.md"

        result = gps_indexer.extract_title(content, filename)

        self.assertEqual(result, "Whitespace Title")

    def test_extract_title_with_multiple_h1_titles(self):
        """Test that first H1 is extracted when multiple exist."""
        content = """# First Title

Some content here.

# Second Title

More content.
"""
        filename = "test-file.md"

        result = gps_indexer.extract_title(content, filename)

        self.assertEqual(result, "First Title")

    def test_extract_title_no_h1_fallback_to_filename(self):
        """Test fallback to filename when no H1 exists."""
        content = "## This is H2\n\nNo H1 here."
        filename = "my-test-file.md"

        result = gps_indexer.extract_title(content, filename)

        # Should convert "my-test-file.md" to "My Test File"
        self.assertEqual(result, "My Test File")

    def test_extract_title_empty_content(self):
        """Test with empty content."""
        content = ""
        filename = "empty-document.md"

        result = gps_indexer.extract_title(content, filename)

        self.assertEqual(result, "Empty Document")

    def test_extract_title_filename_without_extension(self):
        """Test filename processing without .md extension."""
        content = "No H1 here"
        filename = "filename-without-extension"

        result = gps_indexer.extract_title(content, filename)

        self.assertEqual(result, "Filename Without Extension")

    def test_extract_title_with_h1_at_end_of_content(self):
        """Test H1 extraction when title is not at the beginning."""
        content = """Some preamble text.

# Actual Title

Content follows.
"""
        filename = "test.md"

        result = gps_indexer.extract_title(content, filename)

        self.assertEqual(result, "Actual Title")

    def test_extract_title_with_markdown_in_h1(self):
        """Test H1 with markdown formatting inside."""
        content = "# My **Bold** Title with _Italic_\n\nContent."
        filename = "test.md"

        result = gps_indexer.extract_title(content, filename)

        self.assertEqual(result, "My **Bold** Title with _Italic_")

    def test_extract_title_h2_not_extracted(self):
        """Test that H2 is not mistaken for H1."""
        content = "## This is H2\n\nContent here."
        filename = "h2-test.md"

        result = gps_indexer.extract_title(content, filename)

        # Should fall back to filename, not use H2
        self.assertEqual(result, "H2 Test")


class TestScanFiles(unittest.TestCase):
    """Tests for the scan_files function."""

    def setUp(self):
        """Set up test environment with temporary directories."""
        self.test_dir = tempfile.mkdtemp()
        self.index_file = os.path.join(self.test_dir, "content_index.json")

        # Save original values
        self.original_brain_root = gps_indexer.BRAIN_ROOT
        self.original_index_file = gps_indexer.INDEX_FILE

        # Override for testing
        gps_indexer.BRAIN_ROOT = Path(self.test_dir)
        gps_indexer.INDEX_FILE = Path(self.index_file)

        # Create scan directories
        for folder in gps_indexer.SCAN_DIRS:
            os.makedirs(os.path.join(self.test_dir, folder))

    def tearDown(self):
        """Clean up test environment."""
        gps_indexer.BRAIN_ROOT = self.original_brain_root
        gps_indexer.INDEX_FILE = self.original_index_file
        shutil.rmtree(self.test_dir)

    def test_scan_files_creates_index(self):
        """Test that scan_files creates the index file."""
        # Create a simple markdown file
        company_dir = os.path.join(self.test_dir, "1. Company")
        test_file = os.path.join(company_dir, "test.md")
        with open(test_file, 'w') as f:
            f.write("# Test Document\n\nContent here.")

        gps_indexer.scan_files()

        # Check that index file was created
        self.assertTrue(os.path.exists(self.index_file))

    def test_scan_files_indexes_markdown_files(self):
        """Test that markdown files are properly indexed."""
        # Create markdown files in different folders
        company_dir = os.path.join(self.test_dir, "1. Company")
        products_dir = os.path.join(self.test_dir, "2. Products")

        company_file = os.path.join(company_dir, "company-doc.md")
        with open(company_file, 'w') as f:
            f.write("# Company Document\n\nCompany info.")

        products_file = os.path.join(products_dir, "product-spec.md")
        with open(products_file, 'w') as f:
            f.write("# Product Spec\n\nProduct details.")

        gps_indexer.scan_files()

        # Read and verify index
        with open(self.index_file, 'r') as f:
            index = json.load(f)

        self.assertEqual(len(index), 2)

        # Verify entries
        titles = [entry['title'] for entry in index]
        self.assertIn("Company Document", titles)
        self.assertIn("Product Spec", titles)

    def test_scan_files_index_structure(self):
        """Test that index entries have correct structure."""
        company_dir = os.path.join(self.test_dir, "1. Company")
        test_file = os.path.join(company_dir, "test.md")
        test_content = "# Test Title\n\nTest content."

        with open(test_file, 'wb') as f:
            f.write(test_content.encode('utf-8'))

        gps_indexer.scan_files()

        with open(self.index_file, 'r') as f:
            index = json.load(f)

        self.assertEqual(len(index), 1)
        entry = index[0]

        # Verify all required fields
        self.assertIn('title', entry)
        self.assertIn('path', entry)
        self.assertIn('filename', entry)
        self.assertIn('folder', entry)
        self.assertIn('mtime', entry)
        self.assertIn('size', entry)

        # Verify values
        self.assertEqual(entry['title'], "Test Title")
        self.assertEqual(entry['filename'], "test.md")
        self.assertEqual(entry['folder'], "1. Company")
        self.assertEqual(entry['size'], len(test_content.encode('utf-8')))
        self.assertIsInstance(entry['mtime'], float)

    def test_scan_files_ignores_directories(self):
        """Test that ignored directories are skipped."""
        company_dir = os.path.join(self.test_dir, "1. Company")

        # Create file in normal directory
        normal_file = os.path.join(company_dir, "normal.md")
        with open(normal_file, 'w') as f:
            f.write("# Normal File\n\nContent.")

        # Create files in ignored directories
        for ignored_dir in gps_indexer.IGNORE_DIRS:
            ignored_path = os.path.join(company_dir, ignored_dir)
            os.makedirs(ignored_path, exist_ok=True)
            ignored_file = os.path.join(ignored_path, "ignored.md")
            with open(ignored_file, 'w') as f:
                f.write("# Ignored File\n\nThis should be ignored.")

        gps_indexer.scan_files()

        with open(self.index_file, 'r') as f:
            index = json.load(f)

        # Should only have the normal file
        self.assertEqual(len(index), 1)
        self.assertEqual(index[0]['title'], "Normal File")

    def test_scan_files_recursive_scanning(self):
        """Test that subdirectories are scanned recursively."""
        company_dir = os.path.join(self.test_dir, "1. Company")
        sub_dir = os.path.join(company_dir, "subdirectory", "nested")
        os.makedirs(sub_dir)

        # Create file in nested directory
        nested_file = os.path.join(sub_dir, "nested.md")
        with open(nested_file, 'w') as f:
            f.write("# Nested Document\n\nNested content.")

        gps_indexer.scan_files()

        with open(self.index_file, 'r') as f:
            index = json.load(f)

        self.assertEqual(len(index), 1)
        self.assertEqual(index[0]['title'], "Nested Document")
        self.assertIn("subdirectory/nested", index[0]['path'])

    def test_scan_files_sorts_by_mtime(self):
        """Test that files are sorted by modification time (newest first)."""
        company_dir = os.path.join(self.test_dir, "1. Company")

        # Create files with different modification times
        now = time.time()

        old_file = os.path.join(company_dir, "old.md")
        with open(old_file, 'w') as f:
            f.write("# Old File\n\nOld content.")
        os.utime(old_file, (now - 1000, now - 1000))

        new_file = os.path.join(company_dir, "new.md")
        with open(new_file, 'w') as f:
            f.write("# New File\n\nNew content.")
        os.utime(new_file, (now, now))

        middle_file = os.path.join(company_dir, "middle.md")
        with open(middle_file, 'w') as f:
            f.write("# Middle File\n\nMiddle content.")
        os.utime(middle_file, (now - 500, now - 500))

        gps_indexer.scan_files()

        with open(self.index_file, 'r') as f:
            index = json.load(f)

        # Verify order: newest first
        self.assertEqual(len(index), 3)
        self.assertEqual(index[0]['title'], "New File")
        self.assertEqual(index[1]['title'], "Middle File")
        self.assertEqual(index[2]['title'], "Old File")

    def test_scan_files_handles_nonexistent_folders(self):
        """Test that nonexistent folders are handled gracefully."""
        # Remove one of the scan directories
        shutil.rmtree(os.path.join(self.test_dir, "1. Company"))

        # Create file in existing directory
        products_dir = os.path.join(self.test_dir, "2. Products")
        test_file = os.path.join(products_dir, "test.md")
        with open(test_file, 'w') as f:
            f.write("# Test\n\nContent.")

        # Should not raise an error
        gps_indexer.scan_files()

        with open(self.index_file, 'r') as f:
            index = json.load(f)

        self.assertEqual(len(index), 1)

    def test_scan_files_handles_read_errors(self):
        """Test that file read errors are handled gracefully."""
        company_dir = os.path.join(self.test_dir, "1. Company")

        # Create a good file
        good_file = os.path.join(company_dir, "good.md")
        with open(good_file, 'w') as f:
            f.write("# Good File\n\nContent.")

        # Create a bad file and mock read error
        bad_file = os.path.join(company_dir, "bad.md")
        with open(bad_file, 'w') as f:
            f.write("# Bad File\n\nContent.")

        # Patch builtins.open to raise exception for bad file
        original_open = open

        def mock_open_func(file, *args, **kwargs):
            if "bad.md" in str(file):
                raise IOError("Mock read error")
            return original_open(file, *args, **kwargs)

        with patch('builtins.open', side_effect=mock_open_func):
            gps_indexer.scan_files()

        with open(self.index_file, 'r') as f:
            index = json.load(f)

        # Should only have the good file
        self.assertEqual(len(index), 1)
        self.assertEqual(index[0]['title'], "Good File")

    def test_scan_files_only_indexes_md_files(self):
        """Test that only .md files are indexed."""
        company_dir = os.path.join(self.test_dir, "1. Company")

        # Create various file types
        md_file = os.path.join(company_dir, "document.md")
        with open(md_file, 'w') as f:
            f.write("# Markdown File\n\nContent.")

        txt_file = os.path.join(company_dir, "notes.txt")
        with open(txt_file, 'w') as f:
            f.write("Text file content")

        py_file = os.path.join(company_dir, "script.py")
        with open(py_file, 'w') as f:
            f.write("# Python comment\nprint('hello')")

        gps_indexer.scan_files()

        with open(self.index_file, 'r') as f:
            index = json.load(f)

        # Should only index the .md file
        self.assertEqual(len(index), 1)
        self.assertEqual(index[0]['filename'], "document.md")

    def test_scan_files_handles_unicode(self):
        """Test that unicode content is handled correctly."""
        company_dir = os.path.join(self.test_dir, "1. Company")
        unicode_file = os.path.join(company_dir, "unicode.md")

        unicode_content = "# 文档标题 (Document Title) 🚀\n\nContent with émojis and spëcial çharacters."

        with open(unicode_file, 'wb') as f:
            f.write(unicode_content.encode('utf-8'))

        gps_indexer.scan_files()

        with open(self.index_file, 'r', encoding='utf-8') as f:
            index = json.load(f)

        self.assertEqual(len(index), 1)
        self.assertEqual(index[0]['title'], "文档标题 (Document Title) 🚀")
        self.assertEqual(index[0]['size'], len(unicode_content.encode('utf-8')))

    def test_scan_files_empty_directories(self):
        """Test scanning when all directories are empty."""
        gps_indexer.scan_files()

        with open(self.index_file, 'r') as f:
            index = json.load(f)

        # Should create empty index
        self.assertEqual(len(index), 0)
        self.assertIsInstance(index, list)

    def test_scan_files_path_format(self):
        """Test that paths are formatted correctly (forward slashes)."""
        company_dir = os.path.join(self.test_dir, "1. Company")
        sub_dir = os.path.join(company_dir, "subfolder")
        os.makedirs(sub_dir)

        test_file = os.path.join(sub_dir, "test.md")
        with open(test_file, 'w') as f:
            f.write("# Test\n\nContent.")

        gps_indexer.scan_files()

        with open(self.index_file, 'r') as f:
            index = json.load(f)

        # Path should use forward slashes
        self.assertIn('/', index[0]['path'])
        self.assertNotIn('\\', index[0]['path'])

    def test_scan_files_counts_files_correctly(self):
        """Test that the file count is accurate."""
        # Create files across multiple folders
        for i, folder in enumerate(gps_indexer.SCAN_DIRS[:3], 1):
            folder_path = os.path.join(self.test_dir, folder)
            for j in range(i):
                file_path = os.path.join(folder_path, f"file{j}.md")
                with open(file_path, 'w') as f:
                    f.write(f"# File {j}\n\nContent.")

        # Capture output to verify count
        with patch('builtins.print') as mock_print:
            gps_indexer.scan_files()

            # Check that success message was printed with correct count
            calls = [str(call) for call in mock_print.call_args_list]
            success_call = [c for c in calls if '✅' in c or 'Indexed' in c]
            self.assertTrue(len(success_call) > 0)

        # Verify actual count in index
        with open(self.index_file, 'r') as f:
            index = json.load(f)

        # 1 + 2 + 3 = 6 files total
        self.assertEqual(len(index), 6)

    def test_scan_files_json_format(self):
        """Test that the JSON output is properly formatted."""
        company_dir = os.path.join(self.test_dir, "1. Company")
        test_file = os.path.join(company_dir, "test.md")
        with open(test_file, 'w') as f:
            f.write("# Test\n\nContent.")

        gps_indexer.scan_files()

        # Verify JSON is valid and formatted
        with open(self.index_file, 'r') as f:
            content = f.read()
            index = json.loads(content)

        # Verify it's indented (formatted)
        self.assertIn('\n', content)  # Should have newlines
        self.assertIn('  ', content)  # Should have indentation

        # Verify structure
        self.assertIsInstance(index, list)


class TestIntegration(unittest.TestCase):
    """Integration tests for the entire GPS indexer workflow."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.index_file = os.path.join(self.test_dir, "content_index.json")

        self.original_brain_root = gps_indexer.BRAIN_ROOT
        self.original_index_file = gps_indexer.INDEX_FILE

        gps_indexer.BRAIN_ROOT = Path(self.test_dir)
        gps_indexer.INDEX_FILE = Path(self.index_file)

        for folder in gps_indexer.SCAN_DIRS:
            os.makedirs(os.path.join(self.test_dir, folder))

    def tearDown(self):
        """Clean up test environment."""
        gps_indexer.BRAIN_ROOT = self.original_brain_root
        gps_indexer.INDEX_FILE = self.original_index_file
        shutil.rmtree(self.test_dir)

    def test_realistic_brain_structure(self):
        """Test with a realistic brain folder structure."""
        # Create realistic folder structure
        files_data = [
            ("1. Company/vision.md", "# Company Vision 2026\n\nOur strategic vision."),
            ("1. Company/okrs/q1-okrs.md", "# Q1 OKRs\n\nObjectives and key results."),
            ("2. Products/mobile-app/spec.md", "# Mobile App Spec\n\nProduct requirements."),
            ("2. Products/api/endpoints.md", "# API Endpoints\n\nAPI documentation."),
            ("3. Meetings/2026-01-15-standup.md", "# Daily Standup\n\nMeeting notes."),
            ("4. People/stakeholders.md", "# Key Stakeholders\n\nStakeholder map."),
            ("5. Trackers/bugs.md", "# Bug Tracker\n\n- [ ] Fix login issue"),
        ]

        for rel_path, content in files_data:
            full_path = os.path.join(self.test_dir, rel_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)

        gps_indexer.scan_files()

        with open(self.index_file, 'r') as f:
            index = json.load(f)

        # Verify all files indexed
        self.assertEqual(len(index), 7)

        # Verify diverse folder representation
        folders = set(entry['folder'] for entry in index)
        self.assertEqual(len(folders), 5)

        # Verify titles extracted correctly
        titles = [entry['title'] for entry in index]
        self.assertIn("Company Vision 2026", titles)
        self.assertIn("Mobile App Spec", titles)
        self.assertIn("Bug Tracker", titles)


if __name__ == '__main__':
    unittest.main()
