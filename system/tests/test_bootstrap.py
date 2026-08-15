import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent.parent


def _gitignored_names(directory: str, names: list[str]) -> set[str]:
    """Names under `directory` that the source checkout git-ignores.

    Local-only content (private skills, personal workflows, caches) is
    gitignored in the source repo and must never reach the public fixture.
    """
    if not names:
        return set()
    candidates = [str(Path(directory) / name) for name in names]
    try:
        proc = subprocess.run(
            ["git", "check-ignore", "--stdin", "-z"],
            cwd=ROOT,
            input=b"\x00".join(path.encode() for path in candidates) + b"\x00",
            capture_output=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return set()
    if proc.returncode not in (0, 1):
        return set()
    ignored = set(proc.stdout.split(b"\x00")) - {b""}
    return {name for name, path in zip(names, candidates) if path.encode() in ignored}


def copy_public_repo_subset(destination: Path) -> None:
    def ignore_local_only(path, names):
        ignored = {"__pycache__", ".pytest_cache", ".DS_Store", "test_logs"}
        ignored |= _gitignored_names(path, names)
        return ignored & set(names)

    shutil.copytree(
        ROOT / ".agent",
        destination / ".agent",
        ignore=ignore_local_only,
    )
    shutil.copytree(
        ROOT / "system",
        destination / "system",
        ignore=ignore_local_only,
    )
    for name in [
        ".antigravityignore",
        ".gitattributes",
        ".gitignore",
        "AGENTS.md",
        "CLAUDE.md",
        "CODEX_COMMANDS.md",
        "GEMINI.md",
        "README.md",
        "VERSION",
        "install.sh",
    ]:
        source = ROOT / name
        if source.exists():
            shutil.copy2(source, destination / name)
    if (ROOT / ".githooks").exists():
        shutil.copytree(ROOT / ".githooks", destination / ".githooks")


def git(command: list[str], cwd: Path) -> None:
    subprocess.run(["git", *command], cwd=cwd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


class TestBootstrapRealUse(unittest.TestCase):
    def test_agent_bootstrap_from_file_url_clone(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            source = tmp / "source"
            clone = tmp / "clone"
            source.mkdir()
            copy_public_repo_subset(source)

            git(["init"], source)
            git(["config", "user.email", "fixture@example.com"], source)
            git(["config", "user.name", "Fixture"], source)
            git(["add", "."], source)
            git(["commit", "-m", "fixture"], source)

            repo_url = source.resolve().as_uri()
            subprocess.run(["git", "clone", repo_url, str(clone)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            codex_output = tmp / "codex-skills"
            result = subprocess.run(
                [
                    sys.executable,
                    "system/scripts/bootstrap.py",
                    "--agent",
                    "--non-interactive",
                    "--repo-url",
                    repo_url,
                    "--codex-output-dir",
                    str(codex_output),
                    "--skip-hooks",
                    "--skip-guards",
                    "--skip-obsidian",
                    "--json",
                ],
                cwd=clone,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stdout)
            payload = json.loads(result.stdout)
            phases = {phase["name"]: phase for phase in payload["phases"]}

            self.assertEqual(phases["verify_repo"]["status"], "ok")
            self.assertEqual(phases["workspace"]["status"], "ok")
            self.assertEqual(phases["seed_templates"]["status"], "ok")
            self.assertEqual(phases["sync_cli_adapters"]["status"], "ok")
            self.assertEqual(phases["sync_codex_skills"]["status"], "ok")
            self.assertEqual(phases["privacy_guard"]["status"], "ok")

            self.assertTrue((clone / ".beats" / "test-logs").is_dir())
            self.assertTrue((clone / ".beats" / "initialized").exists())
            self.assertTrue((clone / "5. Trackers").is_dir())
            for generated in [
                "AGENTS.md",
                "CLAUDE.md",
                "GEMINI.md",
                "CODEX_COMMANDS.md",
                ".omp/config.yml",
                ".antigravityignore",
                ".cursorignore",
            ]:
                self.assertTrue((clone / generated).is_file(),
                                f"sync_cli_adapters did not generate {generated}")
            self.assertTrue(any(codex_output.glob("beats-*/SKILL.md")))
            obsidian_step = next(step for step in payload["next_steps"] if "Obsidian" in step)
            self.assertIn("/obsidian", obsidian_step)
            self.assertIn(str(clone.resolve()), obsidian_step)


if __name__ == "__main__":
    unittest.main()
