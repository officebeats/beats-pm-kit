"""
Queue Dispatcher
Helper to submit jobs to the async queue.
Usage:
    import dispatch
    dispatch.submit_job("transcript_archive", {"file": "meeting.txt"})
"""

import os
import json
import uuid
import datetime

# Configuration
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
QUEUE_DIR = os.path.join(ROOT_DIR, "Beats-PM-System", "system", "queue")
PENDING_DIR = os.path.join(QUEUE_DIR, "pending")

def submit_job(job_type: str, payload: dict = None) -> str:
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
    timestamp = datetime.datetime.now().isoformat()
    
    job_data = {
        "id": job_id,
        "type": job_type,
        "timestamp": timestamp,
        "payload": payload,
        "status": "pending"
    }
    
    # Ensure directory exists
    if not os.path.exists(PENDING_DIR):
        os.makedirs(PENDING_DIR)
        
    filename = f"{int(datetime.datetime.now().timestamp())}_{job_id}.json"
    filepath = os.path.join(PENDING_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(job_data, f, indent=2)
        
    return job_id
