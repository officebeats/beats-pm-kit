"""
Async Task Queue & Background Worker
Antigravity Native Protocol

Handles heavy tasks in the background to keep the CLI responsive.
- Image Processing
- Transcript Archival
- Large File Operations
"""

import os
import sys
import time
import json
import traceback
import threading
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.ui import print_gray, print_cyan, print_error
from utils.config import get_path, get_root_directory

class TaskQueue:
    def __init__(self):
        self.root = Path(get_root_directory())
        self.queue_dir = self.root / "Beats-PM-System/system/queue"
        self.pending_dir = self.queue_dir / "pending"
        self.processing_dir = self.queue_dir / "processing"
        self.completed_dir = self.queue_dir / "completed"
        self.failed_dir = self.queue_dir / "failed"
        
        self._ensure_dirs()
        
    def _ensure_dirs(self):
        for d in [self.pending_dir, self.processing_dir, self.completed_dir, self.failed_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def submit_job(self, job_type: str, payload: Dict[str, Any]) -> str:
        """Submit a job to the queue."""
        job_id = f"{int(time.time())}_{job_type}"
        job_file = self.pending_dir / f"{job_id}.json"
        
        data = {
            "id": job_id,
            "type": job_type,
            "payload": payload,
            "submitted_at": time.time(),
            "status": "pending"
        }
        
        with open(job_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            
        return job_id

    def process_next(self):
        """Process the oldest pending job."""
        files = sorted(list(self.pending_dir.glob("*.json")))
        if not files:
            return False
            
        job_file = files[0]
        processing_path = self.processing_dir / job_file.name
        
        # Move to processing
        try:
            job_file.rename(processing_path)
        except:
            return False # Race condition or file lock
            
        print_gray(f"[Background] Processing {job_file.name}...")
        
        try:
            with open(processing_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            self._execute_job(data)
            
            # Completed
            processing_path.rename(self.completed_dir / job_file.name)
            
        except Exception as e:
            print_error(f"Job Failed: {e}")
            processing_path.rename(self.failed_dir / job_file.name)
            
            # Write log
            with open(self.failed_dir / f"{job_file.name}.log", "w") as f:
                f.write(traceback.format_exc())
                
        return True

    def _execute_job(self, data: Dict[str, Any]):
        """Routing logic for jobs."""
        job_type = data.get("type")
        payload = data.get("payload", {})
        
        if job_type == "structure_enforce":
            from scripts.enforce_structure import main as enforce
            enforce()
        elif job_type == "vacuum":
            from scripts.vacuum import main as vacuum
            vacuum()

        elif job_type == "optimize_skills":
            from scripts.optimize_skills import index_skills
            index_skills()
        elif job_type == "gps_index":
            from scripts.gps_indexer import scan_files
            scan_files()
        else:
            raise ValueError(f"Unknown job type: {job_type}")

def run_worker_daemon():
    """Runs the worker in a loop."""
    queue = TaskQueue()
    print_cyan("⚡ Async Worker Started")
    while True:
        if not queue.process_next():
            time.sleep(2)

if __name__ == "__main__":
    run_worker_daemon()
