import unittest


from system.scripts import privacy_guard


class TestPrivacyGuardRealUse(unittest.TestCase):
    def test_private_workspace_and_generated_paths_are_blocked(self):
        workspace_rules = {finding.rule for finding in privacy_guard.path_findings("5. Trackers/TASK_MASTER.md")}
        generated_rules = {finding.rule for finding in privacy_guard.path_findings(".codex/skills/example/SKILL.md")}

        self.assertIn("private-workspace-content", workspace_rules)
        self.assertIn("generated-or-local-runtime-path", generated_rules)
        self.assertEqual(privacy_guard.path_findings("5. Trackers/.gitkeep"), [])

    def test_content_rules_catch_email_and_local_path_without_static_pii(self):
        email_text = "Owner: " + "alex" + "@" + "privatecorp.invalid"
        path_text = "Local file: " + "/" + "Users/" + "alex/secret.md"
        findings = privacy_guard.content_findings(email_text + "\n" + path_text, "fixture.md")
        rules = {finding.rule for finding in findings}

        self.assertIn("email-address", rules)
        self.assertIn("local-user-path", rules)


if __name__ == "__main__":
    unittest.main()
