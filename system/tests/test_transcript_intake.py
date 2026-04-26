import sys
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent.parent
SYSTEM_DIR = ROOT_DIR / "system"
sys.path.insert(0, str(SYSTEM_DIR))

from scripts import transcript_intake


class TestTranscriptIntake(unittest.TestCase):
    def test_normalize_incoming_transcripts_moves_date_stamped_txt_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            incoming = root / "incoming"
            transcripts = root / "transcripts"
            incoming.mkdir()

            move_me = incoming / "2026-04-19_Meeting Name.txt"
            keep_md = incoming / "2026-04-19_notes.md"
            keep_txt = incoming / "notes.txt"
            move_me.write_text("hello", encoding="utf-8")
            keep_md.write_text("md", encoding="utf-8")
            keep_txt.write_text("txt", encoding="utf-8")

            moved, skipped = transcript_intake.normalize_incoming_transcripts(incoming, transcripts)

            self.assertEqual(moved, ["2026-04-19_Meeting Name.txt"])
            self.assertEqual(skipped, [])
            self.assertFalse(move_me.exists())
            self.assertTrue((transcripts / move_me.name).exists())
            self.assertTrue(keep_md.exists())
            self.assertTrue(keep_txt.exists())

    def test_normalize_incoming_transcripts_skips_existing_targets(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            incoming = root / "incoming"
            transcripts = root / "transcripts"
            incoming.mkdir()
            transcripts.mkdir()

            duplicate = incoming / "2026-04-19_Meeting Name.txt"
            duplicate.write_text("incoming", encoding="utf-8")
            (transcripts / duplicate.name).write_text("existing", encoding="utf-8")

            moved, skipped = transcript_intake.normalize_incoming_transcripts(incoming, transcripts)

            self.assertEqual(moved, [])
            self.assertEqual(skipped, ["2026-04-19_Meeting Name.txt"])
            self.assertTrue(duplicate.exists())
            self.assertEqual((transcripts / duplicate.name).read_text(encoding="utf-8"), "existing")


if __name__ == "__main__":
    unittest.main()
