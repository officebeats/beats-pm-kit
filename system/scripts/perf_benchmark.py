
import time
import sys
import os
from pathlib import Path

# Add system to path
# Add Brain Root to path
current_file = Path(__file__).resolve()
brain_root = current_file.parent.parent.parent # beats-pm-antigravity-brain
sys.path.insert(0, str(brain_root))

from system.scripts import gps_indexer

def benchmark_gps():
    start_time = time.perf_counter()
    gps_indexer.scan_files()
    end_time = time.perf_counter()
    duration = end_time - start_time
    print(f"GPS Indexer Duration: {duration:.4f}s")
    return duration

if __name__ == "__main__":
    print("Running Antigravity Speed Benchmark...")
    duration = benchmark_gps()
    if duration > 1.0:
        print("FAIL: Too slow (>1.0s)")
        sys.exit(1)
    else:
        print("PASS: Blazing fast (<1.0s)")
