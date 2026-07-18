import unittest
from pathlib import Path

from system.scripts import markdown_title_guard


ROOT = Path(__file__).resolve().parents[2]


class TestMarkdownTitleGuard(unittest.TestCase):
    def test_all_tracked_markdown_has_a_human_title(self):
        self.assertEqual(markdown_title_guard.problems(ROOT), [])


if __name__ == "__main__":
    unittest.main()
