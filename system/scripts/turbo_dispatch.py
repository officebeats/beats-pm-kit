"""
Turbo Dispatcher (Centrifuge Protocol)
Antigravity Native

Seamlessly offloads tasks to the Background Worker (`task_queue.py`).
Usage:
    from system.scripts import turbo_dispatch
    turbo_dispatch.submit("vacuum", {})
"""

import json
import uuid
import time
from pathlib import Path
from typing import Any, Dict, Optional
from .task_queue import TaskQueue

_queue_instance = None

def get_queue() -> TaskQueue:
    global _queue_instance
    if _queue_instance is None:
        _queue_instance = TaskQueue()
    return _queue_instance

def submit(job_type: str, payload: Optional[Dict[str, Any]] = None) -> str:
    """
    Submit a job to the background queue.
    Returns: job_id
    """
    if payload is None:
        payload = {}
        
    queue = get_queue()
    job_id = queue.submit_job(job_type, payload)
    
    return job_id
