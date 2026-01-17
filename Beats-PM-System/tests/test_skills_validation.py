"""
Enhanced Skills Validation Test Suite
Tests the enhanced SKILL.md files for proper structure and content.
Validates processing speed and edge cases.
"""

import unittest
import re
import time
from functools import lru_cache
from pathlib import Path


# Setup paths
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
SKILLS_DIR = ROOT_DIR / ".agent" / "skills"

# Skill inventory
SKILLS = [
    "requirements-translator",
    "daily-synth",
    "task-manager",
    "visual-processor",
    "prd-author",
    "bug-chaser",
    "boss-tracker",
    "meeting-synth",
    "stakeholder-mgr",
    "engineering-collab",
    "ux-collab",
    "delegation-manager",
    "strategy-synth",
    "weekly-synth",
    "code-simplifier"
]


@lru_cache(maxsize=20)
def get_skill_content(skill: str) -> str:
    """Load skill content with caching to avoid repeated I/O."""
    skill_path = SKILLS_DIR / skill / "SKILL.md"
    return skill_path.read_text(encoding='utf-8')


class TestSkillStructure(unittest.TestCase):
    """Verify all enhanced skills have the required structure."""
    
    def test_all_skills_have_frontmatter(self):
        """Each skill must have YAML frontmatter with name and description."""
        for skill in SKILLS:
            with self.subTest(skill=skill):
                content = get_skill_content(skill)
                self.assertTrue(content.startswith("---"), f"{skill}: Missing frontmatter")
                self.assertIn("name:", content, f"{skill}: Missing 'name'")
                self.assertIn("description:", content, f"{skill}: Missing 'description'")
    
    def test_all_skills_have_activation_triggers(self):
        """Each skill must define activation triggers."""
        for skill in SKILLS:
            with self.subTest(skill=skill):
                content = get_skill_content(skill)
                self.assertIn("Activation Triggers", content)
                self.assertIn("Keywords", content)
    
    def test_all_skills_have_workflow(self):
        """Each skill must have a Workflow section with numbered steps."""
        for skill in SKILLS:
            with self.subTest(skill=skill):
                content = get_skill_content(skill)
                self.assertIn("## Workflow", content)
                steps = re.findall(r'### \d+\.', content)
                self.assertGreaterEqual(len(steps), 2, f"{skill}: Need ≥2 workflow steps")
    
    def test_all_skills_have_quality_checklist(self):
        """Each skill must have a Quality Checklist with checkboxes."""
        for skill in SKILLS:
            with self.subTest(skill=skill):
                content = get_skill_content(skill)
                self.assertIn("Quality Checklist", content)
                self.assertIn("- [ ]", content)
    
    def test_all_skills_have_error_handling(self):
        """Each skill must have an Error Handling section."""
        for skill in SKILLS:
            with self.subTest(skill=skill):
                content = get_skill_content(skill)
                self.assertIn("Error Handling", content)
    
    def test_cross_skill_integration(self):
        """Key skills should reference other skills for integration."""
        integration_skills = [
            "requirements-translator", "daily-synth", "meeting-synth",
            "task-manager", "bug-chaser", "boss-tracker", "stakeholder-mgr"
        ]
        for skill in integration_skills:
            with self.subTest(skill=skill):
                content = get_skill_content(skill)
                self.assertIn("Cross-Skill Integration", content)


class TestSkillContent(unittest.TestCase):
    """Validate specific content enhancements in skills."""
    
    def test_daily_synth_features(self):
        """Daily synth should have time-adaptive intelligence."""
        content = get_skill_content("daily-synth")
        for term in ["Time-Adaptive", "Morning", "Evening", "Today's List"]:
            self.assertIn(term, content)
    
    def test_prd_author_features(self):
        """PRD Author should have RICE/MoSCoW scoring."""
        content = get_skill_content("prd-author")
        for term in ["RICE", "MoSCoW", "User Story", "Acceptance Criteria"]:
            self.assertIn(term, content)
    
    def test_bug_chaser_features(self):
        """Bug Chaser should have severity matrix and SLA."""
        content = get_skill_content("bug-chaser")
        for term in ["Severity Matrix", "SLA", "Impact Assessment", "Root Cause"]:
            self.assertIn(term, content)
    
    def test_boss_tracker_features(self):
        """Boss Tracker should have verbatim capture."""
        content = get_skill_content("boss-tracker")
        for term in ["Verbatim", "Escalation", "Risk Assessment"]:
            self.assertIn(term, content)
    
    def test_meeting_synth_features(self):
        """Meeting Synth should have parallel extraction."""
        content = get_skill_content("meeting-synth")
        for term in ["PARALLEL", "Sentiment", "Strategic Pillar"]:
            self.assertIn(term, content)
    
    def test_strategy_synth_features(self):
        """Strategy Synth should have OKR alignment."""
        content = get_skill_content("strategy-synth")
        for term in ["OKR", "SWOT", "Executive Memo"]:
            self.assertIn(term, content)
    
    def test_delegation_manager_features(self):
        """Delegation Manager should have state machine."""
        content = get_skill_content("delegation-manager")
        for term in ["State Machine", "Follow-Up", "Accountability"]:
            self.assertIn(term, content)


class TestSkillSize(unittest.TestCase):
    """Verify skills are appropriately sized."""
    
    def test_skills_are_substantial(self):
        """Enhanced skills should be at least 3KB each."""
        for skill_dir in SKILLS_DIR.iterdir():
            if not skill_dir.is_dir():
                continue
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists():
                continue
            with self.subTest(skill=skill_dir.name):
                size = skill_file.stat().st_size
                self.assertGreaterEqual(size, 3000, f"{skill_dir.name}: <3KB")
    
    def test_total_skills_size(self):
        """Total skills size should be >80KB."""
        total = sum(
            (d / "SKILL.md").stat().st_size 
            for d in SKILLS_DIR.iterdir() 
            if d.is_dir() and (d / "SKILL.md").exists()
        )
        self.assertGreaterEqual(total, 80000)


class TestProcessingSpeed(unittest.TestCase):
    """Verify file processing speed is acceptable."""
    
    def test_skill_files_load_quickly(self):
        """All skill files should load in <100ms combined."""
        get_skill_content.cache_clear()
        start = time.perf_counter()
        for skill in SKILLS:
            _ = get_skill_content(skill)
        elapsed = time.perf_counter() - start
        self.assertLess(elapsed, 0.1)
    
    def test_skill_parsing_is_fast(self):
        """Parsing skill content should be fast (<200ms)."""
        start = time.perf_counter()
        for skill in SKILLS:
            content = get_skill_content(skill)
            _ = content.split("##")
            _ = re.findall(r'`[^`]+`', content)
            _ = re.findall(r'\*\*[^*]+\*\*', content)
        elapsed = time.perf_counter() - start
        self.assertLess(elapsed, 0.2)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and potential failure modes."""
    
    def test_fallback_triggers_exist(self):
        """Skills should have fallback patterns beyond just keywords."""
        for skill in SKILLS:
            with self.subTest(skill=skill):
                content = get_skill_content(skill).lower()
                self.assertTrue(
                    "patterns" in content or "context" in content,
                    f"{skill}: Missing fallback triggers"
                )
    
    def test_fallback_behavior_defined(self):
        """Critical skills should define fallback behaviors."""
        critical = ["prd-author", "bug-chaser", "meeting-synth", "task-manager"]
        fallback_terms = ["missing", "fallback", "default", "not found", "unavailable"]
        
        for skill in critical:
            with self.subTest(skill=skill):
                content = get_skill_content(skill).lower()
                self.assertTrue(
                    any(term in content for term in fallback_terms),
                    f"{skill}: No fallback behavior"
                )
    
    def test_valid_system_paths(self):
        """Skills should reference valid file paths."""
        patterns = [
            r'SETTINGS\.md', r'STATUS\.md', r'KERNEL\.md',
            r'5\. Trackers', r'4\. People', r'3\. Meetings',
            r'2\. Products', r'1\. Company', r'\.gemini/templates'
        ]
        
        for skill in SKILLS:
            if skill == 'code-simplifier':
                continue
            with self.subTest(skill=skill):
                content = get_skill_content(skill)
                self.assertTrue(
                    any(re.search(p, content) for p in patterns),
                    f"{skill}: No system path references"
                )
    
    def test_no_hardcoded_pii(self):
        """Skills should not contain hardcoded PII."""
        pii_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            r'\b\d{3}-\d{3}-\d{4}\b',
        ]
        
        for skill in SKILLS:
            with self.subTest(skill=skill):
                content = get_skill_content(skill)
                for pattern in pii_patterns:
                    self.assertEqual(len(re.findall(pattern, content)), 0)


class TestTableFormats(unittest.TestCase):
    """Verify skills use proper markdown table formats."""
    
    def test_valid_table_headers(self):
        """Tables should have proper header separators."""
        for skill in SKILLS:
            with self.subTest(skill=skill):
                content = get_skill_content(skill)
                tables = [l for l in content.split('\n') if l.strip().startswith('|')]
                if tables:
                    self.assertTrue(
                        any(':--' in l or '---' in l for l in tables),
                        f"{skill}: Missing table separators"
                    )


if __name__ == '__main__':
    unittest.main(verbosity=2)
