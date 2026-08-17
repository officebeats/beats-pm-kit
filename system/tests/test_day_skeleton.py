import datetime as dt
import tempfile
import unittest
from pathlib import Path

from system.scripts import day_skeleton

ROOT = Path(__file__).resolve().parents[2]


def write_task(root: Path, task_id: str, title: str, *, status: str, lane: str, due: str = "", owner: str = "Ernesto", workstream: str = "Pricing") -> Path:
    path = root / "5. Trackers" / "tasks" / f"{task_id}.md"
    lines = [
        "---",
        f"task_id: {task_id}",
        f"title: '{title}'",
        f"status: {status}",
        f"lane: {lane}",
        f"owner: {owner}",
        f"workstream: {workstream}",
    ]
    if due:
        lines.append(f"due: '{due}'")
    lines.extend(["---", "", f"# {title}", ""])
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


class TestDaySkeleton(unittest.TestCase):
    def setUp(self):
        self.today = dt.date(2026, 8, 17)
        self.yesterday = (self.today - dt.timedelta(days=1)).isoformat()
        self.tomorrow = (self.today + dt.timedelta(days=1)).isoformat()

    def make_root(self, *, with_workstreams: bool = True, with_boss: bool = True) -> Path:
        root = Path(tempfile.mkdtemp())
        (root / "5. Trackers" / "tasks").mkdir(parents=True)
        (root / "5. Trackers" / "critical").mkdir(parents=True)
        (root / ".beats").mkdir(parents=True)

        write_task(root, "PLAN-101", "Draft pricing brief", status="in-progress", lane="Today", due=self.yesterday)
        write_task(root, "PLAN-102", "Review partner deck", status="inbox", lane="This Week", due=self.tomorrow)
        write_task(root, "PLAN-103", "Send launch update", status="active", lane="Today", due=self.today.isoformat())
        write_task(root, "PLAN-104", "Old finished chore", status="done", lane="Today")

        if with_workstreams:
            (root / "5. Trackers" / "WORKSTREAMS.md").write_text(
                "# Workstreams\n\n"
                "| Workstream | Latest Outcome | Completed | Open Items | Recommended Next 3 | Status |\n"
                "|:---|:---|:---|:---|:---|:---|\n"
                "| [[workstreams/pricing\\|Pricing Push]] | Draft shared | None | 2 open | Do A; Do B | Active |\n",
                encoding="utf-8",
            )
        if with_boss:
            (root / "5. Trackers" / "critical" / "boss-requests.md").write_text(
                "# Boss Asks\n\n"
                "| ID | Request | Source | Due | Status | Notes |\n"
                "|:---|:---|:---|:---|:---|:---|\n"
                "| BOSS-001 | **Ship the sandbox stories** | email | Apr 9 | 🟡 In Progress | note |\n"
                "| BOSS-002 | **Old onboarding thing** | email | Apr 6 | ✅ Done | note |\n",
                encoding="utf-8",
            )
        return root

    def test_generate_writes_sections_and_counts(self):
        root = self.make_root()

        summary = day_skeleton.generate(root, today=self.today)

        self.assertTrue(summary["ok"])
        self.assertEqual(summary["path"], ".beats/day_skeleton.md")
        self.assertEqual(summary["task_count"], 3)
        self.assertEqual(summary["sections"], ["active-tasks", "due-rollup", "workstreams", "boss-requests"])

        path = root / ".beats" / "day_skeleton.md"
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8")
        first_line = text.splitlines()[0]
        self.assertTrue(first_line.startswith("<!-- generated: "))
        self.assertTrue(first_line.endswith("by nightly_consolidate -->"))

        self.assertIn("## Active Tasks by Lane", text)
        self.assertIn("### Today (2)", text)
        self.assertIn("### This Week (1)", text)
        self.assertIn("Draft pricing brief", text)
        self.assertNotIn("Old finished chore", text)

        # Wikilinks are rendered as plain text, never raw link syntax.
        self.assertIn("Pricing Push", text)
        self.assertNotIn("[[", text)

        self.assertIn("## Boss Requests — Open", text)
        self.assertIn("BOSS-001", text)
        self.assertIn("Ship the sandbox stories", text)
        self.assertNotIn("BOSS-002", text)

    def test_overdue_boundary(self):
        root = self.make_root()

        day_skeleton.generate(root, today=self.today)
        text = (root / ".beats" / "day_skeleton.md").read_text(encoding="utf-8")

        self.assertIn("### Overdue (1)", text)
        self.assertIn(f"Draft pricing brief — due {self.yesterday} (1d overdue)", text)
        self.assertIn("### Due Today (1)", text)
        self.assertIn(f"Send launch update — due {self.today.isoformat()}", text)
        # Due-tomorrow task appears in the lane table but never in the rollup.
        rollup = text.split("## Due Rollup", 1)[1].split("## Workstream Snapshot", 1)[0]
        self.assertNotIn("Review partner deck", rollup)

    def test_optional_sections_omitted_when_sources_missing(self):
        root = self.make_root(with_workstreams=False, with_boss=False)

        summary = day_skeleton.generate(root, today=self.today)

        self.assertEqual(summary["sections"], ["active-tasks", "due-rollup"])
        text = (root / ".beats" / "day_skeleton.md").read_text(encoding="utf-8")
        self.assertNotIn("## Workstream Snapshot", text)
        self.assertNotIn("## Boss Requests", text)

    def test_parse_generated_at_round_trip(self):
        root = self.make_root()
        now = dt.datetime(2026, 8, 17, 5, 30, 0).astimezone()

        day_skeleton.generate(root, today=self.today, now=now)
        text = (root / ".beats" / "day_skeleton.md").read_text(encoding="utf-8")

        parsed = day_skeleton.parse_generated_at(text)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed, now.replace(microsecond=0))
        self.assertIsNone(day_skeleton.parse_generated_at("# no comment here\n"))


if __name__ == "__main__":
    unittest.main()
