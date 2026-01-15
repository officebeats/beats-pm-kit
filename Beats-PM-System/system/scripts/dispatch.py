"""
Queue Dispatcher - Centrifuge Protocol

Helper to submit jobs to the async queue.
Usage:
    from system.scripts import dispatch
    dispatch.submit_job("transcript_archive", {"file": "meeting.txt"})
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Path setup using pathlib
CURRENT_FILE = Path(__file__).resolve()
ROOT_DIR = CURRENT_FILE.parent.parent.parent.parent
QUEUE_DIR = ROOT_DIR / "Beats-PM-System/system/queue"
PENDING_DIR = QUEUE_DIR / "pending"


def submit_job(job_type: str, payload: Optional[Dict[str, Any]] = None) -> str:
    """
    Submit a job to the pending queue.

    Args:
        job_type: String identifier for the job handler
        payload: Dict of arguments for the job

    Returns:
        job_id: The UUID of the submitted job
    """
    if payload is None:
        payload = {}

    job_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()

    job_data = {
        "id": job_id,
        "type": job_type,
        "timestamp": timestamp,
        "payload": payload,
        "status": "pending",
    }

    # Ensure directory exists
    PENDING_DIR.mkdir(parents=True, exist_ok=True)

    filename = f"{int(datetime.now().timestamp())}_{job_id}.json"
    filepath = PENDING_DIR / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(job_data, f, indent=2)

    return job_id
