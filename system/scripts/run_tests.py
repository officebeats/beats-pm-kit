
import os
import sys
import unittest
import time
from pathlib import Path

# Setup Paths
CURRENT_FILE = Path(__file__).resolve()
SYSTEM_DIR = CURRENT_FILE.parent.parent
REPO_ROOT = SYSTEM_DIR.parent.parent
BEATS_PM_SYSTEM = REPO_ROOT / "Beats-PM-System"
LOG_DIR = BEATS_PM_SYSTEM / "test_logs"

def setup_logging():
    """Ensure log directory exists and handle rotation (Max 2 files)."""
    if not LOG_DIR.exists():
        LOG_DIR.mkdir(parents=True)
        print(f"Created log directory: {LOG_DIR}")
        return

    # Get all log files
    files = sorted(LOG_DIR.glob("test_results_*.txt"), key=os.path.getmtime)
    
    # Keep max 1 existing file (so new one makes 2)
    MAX_LOGS = 2
    if len(files) >= MAX_LOGS:
        files_to_delete = files[:-(MAX_LOGS - 1)]
        for f in files_to_delete:
            try:
                f.unlink()
                print(f"Rotated (Deleted): {f.name}")
            except Exception as e:
                print(f"Failed to delete {f.name}: {e}")

def run_tests_and_log():
    """Run tests and save output to new log file."""
    setup_logging()
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    log_file = LOG_DIR / f"test_results_{timestamp}.txt"
    
    print(f"Running tests... Logging to: {log_file}")
    
    # Redirect stdout/stderr to file
    with open(log_file, "w", encoding="utf-8") as f:
        # We need to capture both stream (runner) and prints
        class DualWriter:
            def __init__(self, file):
                self.file = file
                self.stdout = sys.stdout

            def write(self, message):
                self.file.write(message)
                self.stdout.write(message)
                self.file.flush()
                self.stdout.flush()

            def flush(self):
                self.file.flush()
                self.stdout.flush()

        # Capture output
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        
        sys.stdout = DualWriter(f)
        sys.stderr = DualWriter(f)
        
        try:
            # Run the actual tests matching test_full_suite logic
            loader = unittest.TestLoader()
            # Discover from tests dir
            tests_dir = BEATS_PM_SYSTEM / "tests"
            suite = loader.discover(str(tests_dir), pattern='test_*.py')
            
            runner = unittest.TextTestRunner(stream=sys.stdout, verbosity=2)
            result = runner.run(suite)
            
            if not result.wasSuccessful():
                print("\nTESTS FAILED. See log for details.")
                sys.exit(1)
            else:
                print("\nTESTS PASSED.")
                
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr

if __name__ == "__main__":
    # Ensure system is in path for imports
    sys.path.insert(0, str(REPO_ROOT)) 
    run_tests_and_log()
