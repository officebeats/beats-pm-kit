#!/usr/bin/env python3
import os
import sys
import glob
import time
import argparse
from datetime import datetime, timedelta

def get_modified_files(directories, hours_ago):
    """Fetch files modified within the last X hours from target directories."""
    cutoff_time = time.time() - (hours_ago * 3600)
    recent_files = []
    
    for directory in directories:
        # Search for markdown files
        search_pattern = os.path.join(directory, '**', '*.md')
        for filepath in glob.glob(search_pattern, recursive=True):
            try:
                mtime = os.path.getmtime(filepath)
                if mtime >= cutoff_time:
                    # Skip common untracked/system dirs
                    if '.git' in filepath or '.agent' in filepath or 'system' in filepath:
                        continue
                    recent_files.append(filepath)
            except Exception as e:
                continue
                
    return recent_files

def main():
    parser = argparse.ArgumentParser(description="Memory Consolidator Script for Antigravity Brain")
    parser.add_argument("--hours", type=int, default=48, help="Number of hours to look back for modified files")
    parser.add_argument("--dirs", nargs='+', default=['2. Products', '3. Meetings', '1. Company', '0. Incoming'], help="Directories to scan")
    
    args = parser.parse_args()
    
    print(f"🧠 Initiating Memory Consolidation Phase...")
    print(f"Scanning for context changed in the last {args.hours} hours...")
    
    files = get_modified_files(args.dirs, args.hours)
    
    if not files:
        print("No recent context modifications found. Sleep state bypassed.")
        sys.exit(0)
        
    print(f"Found {len(files)} files with unconsolidated context.")
    # print("- " + "\n- ".join(f for f in files))
    
    # In a full run, this script triggers the connected LLM via a CLI wrapper to interpret data.
    # Note for Antigravity integration: This python script is run BEFORE the AI agent is given 
    # the /reflect system prompt so it knows EXACTLY which files to attach to context.
    
    # Output the list of files to standard out so the orchestration layer can ingest them
    print("\n---TARGET MEMORY FILES---")
    for f in files:
        print(f"FILE_TARGET:{f}")
    
    print("\nOrchestrator: Please attach the above files and trigger the 'memory-consolidator' skill.")

if __name__ == "__main__":
    main()
