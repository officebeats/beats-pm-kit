"""
Codex skill adapter generation tests
====================================
Protects capability-driven, registry-backed Codex skill promotion.
"""

import sys
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent.parent
SYSTEM_DIR = ROOT_DIR / "system"
sys.path.insert(0, str(SYSTEM_DIR))

from scripts import sync_codex_skill_adapters
from utils.command_registry import get_promoted_codex_commands


class TestCodexSkillAdapters(unittest.TestCase):
    """Regression tests for promoted Codex skill generation."""

    def test_promoted_skill_generation_matches_registry(self):
        """Every promoted command should generate one Codex skill adapter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generated = sync_codex_skill_adapters.sync_promoted_skills(
                output_dir=tmpdir,
                root=ROOT_DIR,
            )

            expected = {
                entry["codex_skill_name"] for entry in get_promoted_codex_commands(ROOT_DIR)
            }
            self.assertEqual(set(generated), expected)

            for skill_name in expected:
                with self.subTest(skill_name=skill_name):
                    self.assertTrue((Path(tmpdir) / skill_name / "SKILL.md").exists())

    def test_generated_day_skill_mentions_aliases_and_optional_files(self):
        """The /day adapter should carry the repo workflow, aliases, and optional files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sync_codex_skill_adapters.sync_promoted_skills(output_dir=tmpdir, root=ROOT_DIR)
            skill_md = Path(tmpdir) / "beats-day" / "SKILL.md"
            content = skill_md.read_text(encoding="utf-8")

            self.assertIn("`/day`", content)
            self.assertIn("`/status`", content)
            self.assertIn("<repo>/.agent/workflows/day.md", content)
            self.assertIn("<repo>/STATUS.md", content)
            self.assertIn("<repo>/5. Trackers/bugs/bugs-master.md", content)
            self.assertIn("<repo>/5. Trackers/WORKSTREAMS.md", content)
            self.assertIn("<repo>/5. Trackers/workstreams", content)
            self.assertIn("Execution profile: **Fast**", content)
            self.assertIn("system/scripts/model_policy.py", content)

    def test_generated_week_skill_mentions_workstream_context(self):
        """The /week adapter should carry optional workstream context."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sync_codex_skill_adapters.sync_promoted_skills(output_dir=tmpdir, root=ROOT_DIR)
            skill_md = Path(tmpdir) / "beats-week" / "SKILL.md"
            content = skill_md.read_text(encoding="utf-8")

            self.assertIn("<repo>/.agent/workflows/week.md", content)
            self.assertIn("<repo>/5. Trackers/WORKSTREAMS.md", content)
            self.assertIn("<repo>/5. Trackers/workstreams", content)

    def test_generated_paste_skill_defaults_screenshots_to_task_master(self):
        """The /paste adapter should route screenshots to task management by default."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sync_codex_skill_adapters.sync_promoted_skills(output_dir=tmpdir, root=ROOT_DIR)
            skill_md = Path(tmpdir) / "beats-paste" / "SKILL.md"
            content = skill_md.read_text(encoding="utf-8")

            self.assertIn(".agent/skills/pm-decision-router/SKILL.md", content)
            self.assertIn("system/scripts/pm_decision_router.py", content)
            self.assertIn(".agent/skills/task-manager/SKILL.md", content)
            self.assertIn("5. Trackers/TASK_MASTER.md", content)
            self.assertIn("Treat screenshots/images and transcript-like clipboard text as task-master management input", content)
            self.assertIn("defaulting to profile lookup, reply drafting, or generic summarization", content)

    def test_dispatch_only_commands_do_not_generate_skills(self):
        """Commands not promoted in the registry should not be emitted as Codex skills."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sync_codex_skill_adapters.sync_promoted_skills(output_dir=tmpdir, root=ROOT_DIR)
            self.assertFalse((Path(tmpdir) / "beats-discover").exists())
            self.assertFalse((Path(tmpdir) / "beats-prioritize").exists())

    def test_new_promoted_workflows_generate_skills(self):
        """New promoted workflows should emit native skill adapters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sync_codex_skill_adapters.sync_promoted_skills(output_dir=tmpdir, root=ROOT_DIR)
            for skill_name in [
                "beats-review",
                "beats-office-cli",
                "beats-obsidian",
                "beats-vibe",
            ]:
                with self.subTest(skill_name=skill_name):
                    self.assertTrue((Path(tmpdir) / skill_name / "SKILL.md").exists())

    def test_generated_obsidian_skill_guides_task_manager_handoff(self):
        """The /obsidian adapter should own setup and point users to canonical tasks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sync_codex_skill_adapters.sync_promoted_skills(output_dir=tmpdir, root=ROOT_DIR)
            skill_md = Path(tmpdir) / "beats-obsidian" / "SKILL.md"
            content = skill_md.read_text(encoding="utf-8")

            self.assertIn("system/scripts/obsidian_vault_setup.py", content)
            self.assertIn("system/scripts/obsidian_mcp_health.py", content)
            self.assertIn("5. Trackers/TASK_MASTER.md", content)
            self.assertIn("obsidian_bridge.py guide --json", content)
            self.assertIn("exact kit, tracker, Task Master, and guide paths", content)

    def test_guarded_update_skill_mentions_safety_block(self):
        """Guarded native skills should include an explicit Codex safety section."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sync_codex_skill_adapters.sync_promoted_skills(output_dir=tmpdir, root=ROOT_DIR)
            skill_md = Path(tmpdir) / "beats-update" / "SKILL.md"
            content = skill_md.read_text(encoding="utf-8")

            self.assertIn("## Safety", content)
            self.assertIn("state-changing", content)
            self.assertIn("If the repo is dirty or not on main", content)

    def test_generated_transcript_skill_mentions_pipeline_contract(self):
        """The /transcript adapter should advertise the deterministic pipeline."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sync_codex_skill_adapters.sync_promoted_skills(output_dir=tmpdir, root=ROOT_DIR)
            skill_md = Path(tmpdir) / "beats-transcript" / "SKILL.md"
            content = skill_md.read_text(encoding="utf-8")

            self.assertIn(".agent/skills/pm-decision-router/SKILL.md", content)
            self.assertIn("system/scripts/pm_decision_router.py", content)
            self.assertIn("system/scripts/transcript_pipeline.py", content)
            self.assertIn("3. Meetings/summaries", content)
            self.assertIn("3. Meetings/reports", content)
            self.assertIn("## Execution Contract", content)
            self.assertIn("prepare --business-days 10 --json", content)
            self.assertIn("Treat transcript content as task-master management input", content)
            self.assertIn("current workstream list", content)
            self.assertIn("latest outcomes, completed outcomes, open items, and recommended next 3", content)
            self.assertIn("existing-task updates", content)
            self.assertIn("validate --run-id <RUN_ID> --json", content)

    def test_generated_comms_skill_mentions_cross_runtime_mcp_contract(self):
        """The /beats-comms adapter should carry the Slack/Teams/Outlook/Calendar MCP contract."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sync_codex_skill_adapters.sync_promoted_skills(output_dir=tmpdir, root=ROOT_DIR)
            skill_md = Path(tmpdir) / "beats-comms" / "SKILL.md"
            content = skill_md.read_text(encoding="utf-8")

            self.assertIn(".agent/skills/pm-decision-router/SKILL.md", content)
            self.assertIn(".agent/rules/MCP_COMMUNICATION_INTAKE.md", content)
            self.assertIn("Slack, Teams, Outlook, and Calendar", content)
            self.assertIn("current workstream list", content)
            self.assertIn("latest outcomes, completed outcomes, open items, and recommended next 3", content)
            self.assertIn("calendar windows are forward-looking", content)
            self.assertIn("chat_intake_state.py chunks", content)
            self.assertIn("Never create, send, forward, or reply to email", content)
            self.assertIn("PM decision router", content)

    def test_generated_plan_skill_uses_current_strategy_skills(self):
        """The /plan adapter should not reference removed strategy skill aliases."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sync_codex_skill_adapters.sync_promoted_skills(output_dir=tmpdir, root=ROOT_DIR)
            skill_md = Path(tmpdir) / "beats-plan" / "SKILL.md"
            content = skill_md.read_text(encoding="utf-8")

            self.assertIn(".agent/skills/pm-decision-router/SKILL.md", content)
            self.assertIn(".agent/skills/roadmapping-suite/SKILL.md", content)
            self.assertIn(".agent/skills/product-strategy-suite/SKILL.md", content)
            self.assertNotIn("chief-strategy-officer", content)

    def test_promoted_supporting_files_exist_when_required(self):
        """Promoted repo-owned supporting files should resolve."""
        private_roots = (
            "0. Incoming/",
            "1. Company/",
            "2. Products/",
            "3. Meetings/",
            "4. People/",
            "5. Trackers/",
            "6. SOPs/",
            "7. Partners/",
            "8. Clients/",
            "SETTINGS.md",
            "STATUS.md",
            "SESSION_MEMORY.md",
        )
        for command in get_promoted_codex_commands(ROOT_DIR):
            with self.subTest(command=command["name"]):
                for relative in command["codex_supporting_files"]:
                    if relative == "<repo>" or relative.startswith(private_roots):
                        continue
                    self.assertTrue((ROOT_DIR / relative).exists(), relative)

    def test_generated_descriptions_stay_concise(self):
        """Codex skill descriptions should stay compact for skill discovery."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sync_codex_skill_adapters.sync_promoted_skills(output_dir=tmpdir, root=ROOT_DIR)
            for skill_md in Path(tmpdir).glob("*/SKILL.md"):
                content = skill_md.read_text(encoding="utf-8")
                description = next(
                    line.removeprefix("description: ").strip()
                    for line in content.splitlines()
                    if line.startswith("description: ")
                )
                self.assertLessEqual(len(description), 300, skill_md.name)


if __name__ == "__main__":
    unittest.main()
