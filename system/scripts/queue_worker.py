"""
Async Queue Worker
Watches system/queue/pending for new JSON jobs and processes them.
Moves files to 'processing' -> 'completed' or 'failed'.

NOTE: This is the legacy standalone worker. For new integrations, use
turbo_dispatch.submit() -> task_queue.TaskQueue (the canonical stack).
"""

import os
import sys
import time
import json
import traceback
from pathlib import Path

# Path setup
CURRENT_FILE = Path(__file__).resolve()
SYSTEM_ROOT = CURRENT_FILE.parent.parent      # system/
BRAIN_ROOT = SYSTEM_ROOT.parent               # beats-pm-antigravity-brain/

QUEUE_DIR = str(SYSTEM_ROOT / "queue")
PENDING_DIR = os.path.join(QUEUE_DIR, "pending")
PROCESSING_DIR = os.path.join(QUEUE_DIR, "processing")
COMPLETED_DIR = os.path.join(QUEUE_DIR, "completed")
FAILED_DIR = os.path.join(QUEUE_DIR, "failed")


def setup_directories():
    for d in [PENDING_DIR, PROCESSING_DIR, COMPLETED_DIR, FAILED_DIR]:
        if not os.path.exists(d):
            os.makedirs(d)


def move_file(src, dst_dir):
    filename = os.path.basename(src)
    dst = os.path.join(dst_dir, filename)
    os.rename(src, dst)
    return dst


def process_job(job_file):
    print(f"Picking up job: {os.path.basename(job_file)}")

    # Move to processing
    processing_path = move_file(job_file, PROCESSING_DIR)

    try:
        with open(processing_path, 'r', encoding='utf-8') as f:
            job_data = json.load(f)

        job_type = job_data.get('type')
        print(f"  Type: {job_type}")

        # Add brain root to path for imports
        if str(BRAIN_ROOT) not in sys.path:
            sys.path.insert(0, str(BRAIN_ROOT))

        # Dispatch based on job type
        if job_type == 'transcript_archive':
            from system.scripts import vacuum
            vacuum.archive_transcripts()
        elif job_type == 'vacuum':
            from system.scripts import vacuum
            vacuum.main()
        elif job_type == 'structure_enforce':
            from system.scripts import enforce_structure
            enforce_structure.main()
        elif job_type == 'gps_index':
            from system.scripts import gps_indexer
            gps_indexer.scan_files()
        elif job_type == 'optimize_skills':
            from system.scripts import optimize_skills
            optimize_skills.index_skills()
        elif job_type == 'echo':
            print(f"  Echo: {job_data.get('payload')}")
        elif job_type == 'agent_fan_out':
            from system.scripts import agent_dispatcher
            payload = job_data.get('payload', {})
            agent_dispatcher.fan_out(payload.get('task', {}), payload.get('agents', []))
        else:
            raise ValueError(f"Unknown job type: {job_type}")

        # Success
        print("  Job completed successfully.")
        move_file(processing_path, COMPLETED_DIR)

    except Exception as e:
        print(f"  Job FAILED: {str(e)}")
        # Move to failed
        failed_path = move_file(processing_path, FAILED_DIR)

        # Write error log
        with open(failed_path + ".error.log", 'w', encoding='utf-8') as f:
            f.write(str(e))
            f.write("\n")
            f.write(traceback.format_exc())


def run_worker_loop():
    print(f"Worker started. Watching {PENDING_DIR}...")
    setup_directories()

    while True:
        files = [f for f in os.listdir(PENDING_DIR) if f.endswith('.json')]

        if not files:
            time.sleep(2)
            continue

        # Process oldest file first (simple FIFO)
        files.sort()
        job_file = os.path.join(PENDING_DIR, files[0])

        process_job(job_file)


if __name__ == "__main__":
    run_worker_loop()
