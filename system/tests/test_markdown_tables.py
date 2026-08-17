from __future__ import annotations

import unittest

from system.utils.markdown_tables import split_cells, strip_wikilinks


class TestSplitCells(unittest.TestCase):
    def test_escaped_pipe_wikilink_keeps_cell_intact(self):
        cells = split_cells("| [[a\\|b]] | Owner | 2026-04-12 | active |")
        self.assertEqual(cells, ["[[a\\|b]]", "Owner", "2026-04-12", "active"])

    def test_separator_row_yields_empty(self):
        self.assertEqual(split_cells("|:---|:---|:---|"), [])
        self.assertEqual(split_cells("| --- | --- |"), [])

    def test_non_table_line_yields_empty(self):
        self.assertEqual(split_cells("just prose with a | pipe"), [])
        self.assertEqual(split_cells(""), [])

    def test_plain_row_splits_and_strips(self):
        self.assertEqual(split_cells("| a | b | c |"), ["a", "b", "c"])


class TestStripWikilinks(unittest.TestCase):
    def test_escaped_alias_form(self):
        self.assertEqual(
            strip_wikilinks("see [[P1-008\\|Review Peter's Weekly Report]] today"),
            "see Review Peter's Weekly Report today",
        )

    def test_unescaped_alias_form(self):
        self.assertEqual(strip_wikilinks("[[tasks/P1-008|Review]]"), "Review")

    def test_alias_less_form_keeps_target(self):
        self.assertEqual(strip_wikilinks("[[P1-008]]"), "P1-008")

    def test_plain_text_untouched(self):
        self.assertEqual(strip_wikilinks("no links here"), "no links here")


if __name__ == "__main__":
    unittest.main()
