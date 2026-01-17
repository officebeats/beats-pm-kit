import unittest
import os
import sys
import json
import time
import shutil
from unittest.mock import MagicMock

# Handle imports
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYSTEM_DIR = os.path.join(ROOT_DIR, 'Beats-PM-System', 'system')
sys.path.insert(0, SYSTEM_DIR)

# Mock utils 
if 'utils' not in sys.modules:
    sys.modules['utils'] = MagicMock()
    sys.modules['utils.ui'] = MagicMock()
    sys.modules['utils.config'] = MagicMock()
    sys.modules['utils.filesystem'] = MagicMock()

from scripts import dispatch, queue_worker

class TestAsyncQueue(unittest.TestCase):
    
    def setUp(self):
        # Clean up queue dirs before test
        queue_worker.setup_directories()
        
        # Clear specific dirs safely (Windows friendly)
        for d in [queue_worker.PENDING_DIR, queue_worker.PROCESSING_DIR, queue_worker.COMPLETED_DIR, queue_worker.FAILED_DIR]:
            if os.path.exists(d):
                for f in os.listdir(d):
                    file_path = os.path.join(d, f)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                    except Exception as e:
                        print(f"Warning: Failed to cleanup {file_path}: {e}")

    def test_end_to_end_job_processing(self):
        """Test that submitting a job and running the worker processes it."""
        
        # 1. Submit Job
        payload = {"message": "Hello World"}
        job_id = dispatch.submit_job("echo", payload)
        
        # Verify file in pending
        pending_files = os.listdir(queue_worker.PENDING_DIR)
        self.assertEqual(len(pending_files), 1)
        self.assertIn(job_id, pending_files[0])
        
        # 2. Run Worker (Process one job)
        # We simulate the loop by calling logic manually to avoid infinite loop
        job_file = os.path.join(queue_worker.PENDING_DIR, pending_files[0])
        queue_worker.process_job(job_file)
        
        # 3. Verify Completion
        # Pending should be empty
        self.assertEqual(len(os.listdir(queue_worker.PENDING_DIR)), 0)
        # Completed should have the file
        completed_files = os.listdir(queue_worker.COMPLETED_DIR)
        self.assertEqual(len(completed_files), 1)
        self.assertIn(job_id, completed_files[0])
        
    def test_failed_job_handling(self):
        """Test that invalid jobs move to failed."""
        
        # Submit invalid job type
        job_id = dispatch.submit_job("invalid_type", {})
        
        files = os.listdir(queue_worker.PENDING_DIR)
        job_file = os.path.join(queue_worker.PENDING_DIR, files[0])
        
        # Process
        queue_worker.process_job(job_file)
        
        # Check failed dir has at least 1 file (the job itself)
        failed_files = os.listdir(queue_worker.FAILED_DIR)
        self.assertGreaterEqual(len(failed_files), 1, "Failed job should be in failed directory")

if __name__ == '__main__':
    unittest.main()
