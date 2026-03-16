"""
Core Component Tests
FAANG-Level Unit Tests for Beats PM System Core Scripts.
"""

import unittest
import sys
import os
import shutil
import tempfile
import hashlib

# Add system path to import modules
# Path: .../tests/test.py -> .../tests -> .../ -> .../Beats-PM-System/system
from pathlib import Path
CURRENT_FILE = Path(__file__).resolve()
SYSTEM_ROOT = CURRENT_FILE.parent.parent # Beats-PM-System/
SYSTEM_DIR = SYSTEM_ROOT / "system"
sys.path.insert(0, str(SYSTEM_DIR))

# Mocking utils for universal_clipboard import side-effects
from unittest.mock import MagicMock
sys.modules["utils"] = MagicMock()
sys.modules["utils.ui"] = MagicMock()
sys.modules["utils.platform"] = MagicMock()
sys.modules["utils.filesystem"] = MagicMock()
sys.modules["utils.subprocess_helper"] = MagicMock()

# Now import the scripts under test
# universal_clipboard does relative imports "from utils.ui", so with system_path in sys.path, it should work IF we are careful.
# However, universal_clipboard actually does:
# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# calculated from its OWN location.

# Let's import directly using the added path.
try:
    import scripts.universal_clipboard as universal_clipboard
    import scripts.context_loader as context_loader
    MODULES_AVAILABLE = True
except ImportError as e:
    MODULES_AVAILABLE = False
    IMPORT_ERROR = str(e)

# Mock output to avoid cluttering console during tests
from io import StringIO
from unittest.mock import patch

@unittest.skipUnless(MODULES_AVAILABLE, f"Required modules not available")
class TestUniversalClipboard(unittest.TestCase):
    
    def test_hash_calculation(self):
        """Test that hashing is deterministic and accurate."""
        content = "Hello World"
        expected = hashlib.md5(content.encode('utf-8')).hexdigest()
        self.assertEqual(universal_clipboard.calculate_hash(content), expected)
        
    def test_transcript_detection_positive(self):
        """Test transcript detection logic on valid transcripts."""
        
        # Case 1: Timestamps and Speaker
        sample_1 = """
        [00:00:15] John: Welcome to the meeting.
        [00:00:20] Alice: Thanks John.
        """ * 20 # Make it long enough
        self.assertTrue(universal_clipboard.detect_transcript(sample_1), "Should detect timestamps and speakers")
        
        # Case 2: Keywords
        sample_2 = """
        Meeting Transcript
        Date: 2025-01-01
        Attendees: John, Alice
        
        John: Let's discuss the roadmap.
        """ * 20
        self.assertTrue(universal_clipboard.detect_transcript(sample_2), "Should detect transcript keywords")

    def test_transcript_detection_negative(self):
        """Test that normal code or text is NOT detected as transcript."""
        sample = """
        def main():
            print("Hello")
            return [1, 2, 3]
        """ * 20
        self.assertFalse(universal_clipboard.detect_transcript(sample), "Code should not be transcript")
        
        sample_short = "Just a short text msg."
        self.assertFalse(universal_clipboard.detect_transcript(sample_short), "Short text should be ignored")

@unittest.skipUnless(MODULES_AVAILABLE, f"Required modules not available")
class TestContextLoader(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.test_dir)
        
    def test_loader_filtering(self):
        """Test that context loader respects ignore rules."""
        
        # Create dummy structure
        os.makedirs(os.path.join(self.test_dir, ".git"))
        os.makedirs(os.path.join(self.test_dir, "src"))
        
        # Ignored file in .git
        with open(os.path.join(self.test_dir, ".git", "HEAD.md"), 'w') as f:
            f.write("ignored")
            
        # Valid file
        with open(os.path.join(self.test_dir, "src", "README.md"), 'w') as f:
            f.write("valid content")
            
        # Output capture
        captured_output = StringIO()
        sys.stdout = captured_output
        
        context_loader.load_context(self.test_dir)
        
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        
        self.assertIn("src/README.md", output.replace(os.path.sep, "/"))
        self.assertNotIn(".git/HEAD.md", output.replace(os.path.sep, "/"))
            
if __name__ == '__main__':
    unittest.main()
