from __future__ import annotations

import unittest
from pathlib import Path

from system.scripts import trello_bridge


class TestTrelloBridgeBoundedSync(unittest.TestCase):
    def classification(self, local_id: str, name: str, path: str = "5. Trackers/tasks/PLAN-001.md"):
        return {
            "card": {"name": name, "desc": "", "id": "card-1"},
            "lane": "today",
            "classification": "linked_existing",
            "local_id": local_id,
            "local_path": Path(path),
        }

    def test_filter_classifications_matches_task_id(self):
        rows = [
            self.classification("PLAN-001", "Guideline exception intake"),
            self.classification("PLAN-002", "Developer portal path"),
        ]

        filtered = trello_bridge.filter_classifications(rows, only_tasks=["PLAN-002"])

        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["local_id"], "PLAN-002")

    def test_filter_classifications_matches_workstream_title(self):
        rows = [
            self.classification("PLAN-001", "Guideline exception intake"),
            self.classification("PLAN-002", "Developer portal path"),
        ]

        filtered = trello_bridge.filter_classifications(rows, only_workstreams=["developer portal"])

        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["card"]["name"], "Developer portal path")

    def test_fail_on_unrelated_requires_bounded_filter(self):
        # This exercises the pure refusal branch before TrelloAPI/network is initialized.
        result = trello_bridge.run_sync(apply=True, fail_on_unrelated=True)

        self.assertEqual(result, 2)


if __name__ == "__main__":
    unittest.main()
