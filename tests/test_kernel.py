import unittest
import os
import sys
from unittest.mock import MagicMock

# Handle imports from the hyphenated directory structure
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYSTEM_DIR = os.path.join(ROOT_DIR, 'Beats-PM-System', 'system')
sys.path.insert(0, SYSTEM_DIR)

# Mock utils dependencies before importing scripts
if 'utils' not in sys.modules:
    sys.modules['utils'] = MagicMock()
    sys.modules['utils.ui'] = MagicMock()
    sys.modules['utils.config'] = MagicMock()
    sys.modules['utils.filesystem'] = MagicMock()

from scripts import kernel_utils

class TestKernelUtils(unittest.TestCase):
    
    def test_check_anchor_rule_valid(self):
        """Test that a valid company anchor passes."""
        self.assertTrue(kernel_utils.check_anchor_rule("1. Company/Acme/ProjectX"))
        self.assertTrue(kernel_utils.check_anchor_rule("1. Company/Startup/PROFILE.md"))
        self.assertTrue(kernel_utils.check_anchor_rule("2. Products/MyApp/PRD.md"))
        self.assertTrue(kernel_utils.check_anchor_rule("5. Trackers/bugs.md"))

    def test_check_anchor_rule_invalid(self):
        """Test that invalid paths fail the anchor rule."""
        self.assertFalse(kernel_utils.check_anchor_rule("6. Random/Project"))
        self.assertFalse(kernel_utils.check_anchor_rule("MyProject/README.md"))
        # Root files are allowed
        self.assertTrue(kernel_utils.check_anchor_rule("README.md"))

    def test_check_privacy_rule_clean(self):
        """Test that safe files pass privacy check."""
        passed, violations = kernel_utils.check_privacy_rule(["README.md", "scripts/setup.py"])
        self.assertTrue(passed)
        self.assertEqual(len(violations), 0)

    def test_check_privacy_rule_violation(self):
        """Test that protected folders trigger privacy violation."""
        files = ["README.md", "1. Company/Secret.md", "5. Trackers/bugs.md"]
        passed, violations = kernel_utils.check_privacy_rule(files)
        self.assertFalse(passed)
        self.assertIn("1. Company/Secret.md", violations)
        self.assertIn("5. Trackers/bugs.md", violations)

    def test_get_suggested_template(self):
        """Test that intents map to correct templates."""
        self.assertEqual(kernel_utils.get_suggested_template("bug"), ".gemini/templates/bug-report.md")
        self.assertEqual(kernel_utils.get_suggested_template("BUG"), ".gemini/templates/bug-report.md")
        self.assertEqual(kernel_utils.get_suggested_template("weekly"), ".gemini/templates/weekly-review.md")
        self.assertIsNone(kernel_utils.get_suggested_template("random_intent"))

if __name__ == '__main__':
    unittest.main()
