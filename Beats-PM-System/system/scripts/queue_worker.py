"""
Async Queue Worker
Watches system/queue/pending for new JSON jobs and processes them.
Moves files to 'processing' -> 'completed' or 'failed'.
"""

import os
import sys
import time
import json
import traceback

# Paths
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
QUEUE_DIR = os.path.join(ROOT_DIR, "Beats-PM-System", "system", "queue")
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
        
        # Dispatch based on job type
        if job_type == 'transcript_archive':
            from system.scripts import vacuum
            vacuum.archive_transcripts()
        elif job_type == 'echo':
            print(f"  Echo: {job_data.get('payload')}")
        else:
            raise ValueError(f"Unknown job type: {job_type}")
            
        # Success
        print("  Job completed successfully.")
        move_file(processing_path, COMPLETED_DIR)
        
    except Exception as e:
        print(f"  Job FAILED: {str(e)}")
        traceback.print_exc()
        # Move to failed
        failed_path = move_file(processing_path, FAILED_DIR)
        
        # Write error log
        with open(failed_path + ".error.log", 'w') as f:
            f.write(str(e))
            f.write("\n")
            traceback.print_exc(file=f)

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
    # Add system root to path so imports work
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    run_worker_loop()
