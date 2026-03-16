"""
Kernel Utils (Hard Kernel) - Centrifuge Protocol

Deterministic enforcement of system rules (Anchors, Privacy, Templates).
Replaces loose text instructions in KERNEL.md with executable logic.
"""

from pathlib import Path
from typing import List, Optional, Tuple


def check_anchor_rule(path: str) -> bool:
    """
    Enforce Company Anchor Rule.
    Any new project/product must be in Folder 0-5.

    Args:
        path: The target path for the new item.

    Returns:
        bool: True if valid, False if violation.
    """
    p = Path(path)
    allowed_prefixes = [
        "0. Incoming",
        "1. Company",
        "2. Products",
        "3. Meetings",
        "4. People",
        "5. Trackers",
    ]

    # Check if path starts with any of the allowed folders
    for prefix in allowed_prefixes:
        # Check if the path is a child of the prefix
        try:
            p.relative_to(prefix)
            return True
        except ValueError:
            continue

    # Allow root level files
    if len(p.parts) <= 1:
        return True

    return False


def check_privacy_rule(file_paths: List[str]) -> Tuple[bool, List[str]]:
    """
    Enforce Privacy Rule.
    Files in Folders 1-5 cannot be pushed to public repos.

    Args:
        file_paths: List of files attempting to be staged/pushed.

    Returns:
        Tuple(bool, List[str]): (Passed?, List of violating files)
    """
    protected_prefixes = [
        "1. Company",
        "2. Products",
        "3. Meetings",
        "4. People",
        "5. Trackers",
    ]

    violations = []

    for fp in file_paths:
        p = Path(fp)
        for prefix in protected_prefixes:
            try:
                # If path starts with prefix, it's protected
                p.relative_to(prefix)
                violations.append(fp)
                break
            except ValueError:
                # Also check absolute-ish paths
                if str(p).startswith(f"/{prefix}"):
                    violations.append(fp)
                    break

    return (len(violations) == 0, violations)


def get_suggested_template(intent: str) -> Optional[str]:
    """
    Return the mandatory template for a given intent.

    Args:
        intent: The detected user code (bug, prd, meeting, etc.)

    Returns:
        Path to the template, or None.
    """
    intent = intent.lower()

    mapping = {
        "bug": ".agent/templates/bug-report.md",
        "fix": ".agent/templates/bug-fix-spec.md",
        "feature": ".agent/templates/feature-request.md",
        "spec": ".agent/templates/feature-spec.md",
        "transcript": ".agent/templates/transcript-extraction.md",
        "strategy": ".agent/templates/strategy-memo.md",
        "weekly": ".agent/templates/weekly-review.md",
    }
    return mapping.get(intent)



