"""Tests for the FTUE configuration helper across in-house and consulting workflows."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from system.scripts.ftue import (
    BANNER_MATRIX,
    BANNER_COMPLETE,
    inspect_profile,
    update_profile,
    render_human_status,
    parse_clients_input,
)


class TestFTUE(unittest.TestCase):
    def test_inspect_unconfigured_profile(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            status = inspect_profile(root)
            self.assertFalse(status.exists)
            self.assertFalse(status.is_configured)

    def test_update_and_inspect_in_house_profile(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            agent_templates = root / ".agent" / "templates"
            agent_templates.mkdir(parents=True, exist_ok=True)
            real_template = Path(__file__).resolve().parents[2] / ".agent" / "templates" / "SETTINGS_TEMPLATE.md"
            (agent_templates / "SETTINGS_TEMPLATE.md").write_text(real_template.read_text(encoding="utf-8"))

            ok = update_profile(
                root,
                owner="Alex Rivera",
                role="Staff Product Manager",
                timezone="America/New_York",
                boss_name="Marcus Vance",
                boss_alias="marcus",
                products=[
                    {"name": "Core Platform", "alias": "core", "description": "APIs and infra"},
                    {"name": "Web Dashboard", "alias": "web", "description": "Admin console"},
                ],
            )
            self.assertTrue(ok)

            status = inspect_profile(root)
            self.assertTrue(status.exists)
            self.assertTrue(status.is_configured)
            self.assertEqual(status.org_type, "in-house")
            self.assertEqual(status.owner, "Alex Rivera")
            self.assertEqual(status.role, "Staff Product Manager")
            self.assertEqual(status.timezone, "America/New_York")
            self.assertEqual(status.boss_name, "Marcus Vance")
            self.assertEqual(len(status.products), 2)
            self.assertEqual(status.products[0]["name"], "Core Platform")

            human = render_human_status(status)
            self.assertIn("BEATS PM KIT", human)
            self.assertIn("Alex Rivera", human)
            self.assertIn("In-House Product Management", human)
            self.assertIn("YES", human)

    def test_parse_clients_input_formats(self):
        # Semicolon delimited format
        text = "FinCorp: Mobile Banking, Cloud Migration; HealthNet: Provider Portal"
        parsed = parse_clients_input(text)
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]["client"], "FinCorp")
        self.assertEqual(len(parsed[0]["projects"]), 2)
        self.assertEqual(parsed[0]["projects"][0]["name"], "Mobile Banking")
        self.assertEqual(parsed[1]["client"], "HealthNet")
        self.assertEqual(len(parsed[1]["projects"]), 1)

    def test_consulting_profile_configuration_and_workspace_seeding(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            agent_templates = root / ".agent" / "templates"
            agent_templates.mkdir(parents=True, exist_ok=True)
            real_template = Path(__file__).resolve().parents[2] / ".agent" / "templates" / "SETTINGS_TEMPLATE.md"
            (agent_templates / "SETTINGS_TEMPLATE.md").write_text(real_template.read_text(encoding="utf-8"))
            (root / "4. People").mkdir(parents=True, exist_ok=True)
            (root / "4. People" / "PEOPLE.md").write_text("# People\n\n| Name | Role | Context |\n|:---|:---|:---|\n")

            clients_input = [
                {
                    "client": "FinCorp",
                    "sponsor": "VP Jane Doe",
                    "projects": [
                        {"name": "Mobile Banking", "alias": "finc-mob", "description": "iOS app"},
                        {"name": "Cloud Migration", "alias": "finc-cld", "description": "AWS infra"},
                    ],
                },
                {
                    "client": "HealthNet",
                    "sponsor": "CTO Mark Davis",
                    "projects": [
                        {"name": "Provider Portal", "alias": "hlth-prt", "description": "Clinical portal"},
                    ],
                },
            ]

            ok = update_profile(
                root,
                owner="Jordan Lee",
                role="Principal Consultant",
                org_type="consulting",
                firm="Slalom",
                boss_name="Sarah Jenkins",
                boss_alias="sarah",
                client_sponsors={"FinCorp": "VP Jane Doe", "HealthNet": "CTO Mark Davis"},
                clients=clients_input,
            )
            self.assertTrue(ok)

            status = inspect_profile(root)
            self.assertTrue(status.exists)
            self.assertTrue(status.is_configured)
            self.assertEqual(status.org_type, "consulting")
            self.assertEqual(status.firm, "Slalom")
            self.assertEqual(status.owner, "Jordan Lee")
            self.assertEqual(status.boss_name, "Sarah Jenkins")
            self.assertEqual(len(status.clients), 2)
            self.assertEqual(len(status.products), 3)

            # Check seeded folders and files
            self.assertTrue((root / "8. Clients" / "FinCorp" / "CLIENT_OVERVIEW.md").exists())
            self.assertTrue((root / "8. Clients" / "HealthNet" / "CLIENT_OVERVIEW.md").exists())
            self.assertTrue((root / "5. Trackers" / "workstreams" / "fincorp-mobile-banking.md").exists())
            self.assertTrue((root / "5. Trackers" / "workstreams" / "healthnet-provider-portal.md").exists())

            # Check PEOPLE.md updated with sponsors
            people_text = (root / "4. People" / "PEOPLE.md").read_text(encoding="utf-8")
            self.assertIn("VP Jane Doe", people_text)
            self.assertIn("CTO Mark Davis", people_text)

            # Check branding remains Beats PM Kit
            human = render_human_status(status)
            self.assertIn("BEATS PM KIT", human)
            self.assertIn("Consulting (Multi-Client Engagements)", human)
            self.assertIn("FinCorp", human)
            self.assertIn("Slalom", human)

    def test_banners_preserve_beats_pm_kit_branding(self):
        self.assertIn("B E A T S   P M   K I T", BANNER_MATRIX)
        self.assertIn("B E A T S   P M   K I T", BANNER_COMPLETE)


if __name__ == "__main__":
    unittest.main()
