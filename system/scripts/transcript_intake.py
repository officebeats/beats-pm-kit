"""
Transcript Intake Normalizer
Moves raw meeting transcript files from 0. Incoming/ into 3. Meetings/transcripts/
so later /transcript and /meet runs can discover them consistently.
"""

import re
import shutil
from pathlib import Path


CURRENT_FILE = Path(__file__).resolve()
SYSTEM_ROOT = CURRENT_FILE.parent.parent
BRAIN_ROOT = SYSTEM_ROOT.parent
INCOMING_DIR = BRAIN_ROOT / "0. Incoming"
TRANSCRIPTS_DIR = BRAIN_ROOT / "3. Meetings" / "transcripts"

DATE_STAMPED_TRANSCRIPT = re.compile(r"^\d{4}-\d{2}-\d{2}_.+\.txt$")


def is_transcript_candidate(path: Path) -> bool:
    """Return True when the file looks like a raw imported meeting transcript."""
    return path.is_file() and DATE_STAMPED_TRANSCRIPT.match(path.name) is not None


def normalize_incoming_transcripts(incoming_dir: Path, transcripts_dir: Path):
    """Move date-stamped transcript files into the transcript archive directory."""
    transcripts_dir.mkdir(parents=True, exist_ok=True)
    moved = []
    skipped = []

    for path in sorted(incoming_dir.iterdir()):
        if not is_transcript_candidate(path):
            continue

        target = transcripts_dir / path.name
        if target.exists():
            skipped.append(path.name)
            continue

        shutil.move(str(path), str(target))
        moved.append(path.name)

    return moved, skipped


def main():
    moved, skipped = normalize_incoming_transcripts(INCOMING_DIR, TRANSCRIPTS_DIR)

    if moved:
        print(f"Normalized {len(moved)} transcript(s) into 3. Meetings/transcripts/")
        for name in moved:
            print(f"  moved: {name}")
    else:
        print("No raw transcripts needed normalization.")

    if skipped:
        print(f"Skipped {len(skipped)} transcript(s) because the target already exists.")
        for name in skipped:
            print(f"  skipped: {name}")


if __name__ == "__main__":
    main()
