"""
Kernel Utils (Hard Kernel)

Deterministic enforcement of system rules (Anchors, Privacy, Templates).
Replaces loose text instructions in KERNEL.md with executable logic.
"""

import os
from typing import List, Optional, Tuple

# Mock utils imports for now to ensure standalone validity if utils missing
# In production, these should be:
# from utils.ui import print_error, print_warning
# from utils.config import get_config

def check_anchor_rule(path: str) -> bool:
    """
    Enforce Company Anchor Rule.
    Any new project/product must be in '1. Company/'.
    
    Args:
        path: The target path for the new item.
        
    Returns:
        bool: True if valid, False if violation.
    """
    # Normalize path separators
    path = path.replace("\\", "/")
    
    # Validation logic
    allowed_prefixes = [
        "0. Incoming/", "1. Company/", "2. Products/", 
        "3. Meetings/", "4. People/", "5. Trackers/"
    ]
    
    for prefix in allowed_prefixes:
        if path.startswith(prefix):
            return True
            
    # Allow root level for non-project files
    if path.count("/") == 0:
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
        "1. Company/",
        "2. Products/",
        "3. Meetings/",
        "4. People/",
        "5. Trackers/"
    ]
    
    violations = []
    
    for fp in file_paths:
        fp_clean = fp.replace("\\", "/")
        for prefix in protected_prefixes:
            if fp_clean.startswith(prefix) or fp_clean.startswith(f"/{prefix}"):
                # Exception: Templates or config might be allowed, but strictly strict for now
                violations.append(fp)
                break
                
    return (len(violations) == 0, violations)


def get_suggested_template(intent: str) -> Optional[str]:
    """
    Return the mandatory template for a given intent.
    
    Args:
        intent: The detected user code (bug, prd, meeting, etc.)
        
    Returns:
        str: Path to the template, or None.
    """
    intent = intent.lower()
    
    mapping = {
        "bug": ".gemini/templates/bug-report.md",
        "fix": ".gemini/templates/bug-fix-spec.md",
        "feature": ".gemini/templates/feature-request.md",
        "spec": ".gemini/templates/feature-spec.md",
        "transcript": ".gemini/templates/transcript-extraction.md",
        "strategy": ".gemini/templates/strategy-memo.md",
        "weekly": ".gemini/templates/weekly-review.md"
    }
    return mapping.get(intent)


def get_active_context(project_name: str, context_file: str) -> str:
    """
    Filter the master context file (e.g. TASK_MASTER.md) to only return lines 
    relevant to the active project.
    
    Args:
        project_name: The name of the project (e.g. "Mobile App")
        context_file: Path to the context file.
        
    Returns:
        str: Pruned context string.
    """
    if not os.path.exists(context_file):
        return ""
        
    with open(context_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    active_lines = []
    capture = False
    
    # Simple Header-Based Context Pruning
    # Start capturing when we see "# ProjectName"
    # Stop when we see another "# "
    
    for line in lines:
        is_project_header = (
            line.strip().startswith(f"# {project_name}") or 
            line.strip().startswith(f"## {project_name}")
        )
        is_new_section = line.startswith("# ") or line.startswith("## ")
        
        if is_project_header:
            capture = True
            active_lines.append(line)
        elif capture and is_new_section:
            capture = False
        elif capture:
            active_lines.append(line)
                
    return "".join(active_lines)
