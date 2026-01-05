import os
import re
import datetime

# Auto-detect root (assuming script is in Beats-PM-System/system/scripts)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
TRACKERS_DIR = os.path.join(ROOT_DIR, "5. Trackers")
ARCHIVE_DIR = os.path.join(TRACKERS_DIR, "archive")

def ensure_archive():
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)

def vacuum_file(filename):
    filepath = os.path.join(TRACKERS_DIR, filename)
    if not os.path.exists(filepath):
        return

    print(f"Vacuuming {filename}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    active_lines = []
    archived_lines = []
    
    # Simple logic: Archive lines starting with '- [x]'
    # In a real app, we'd preserve headers, but for v1 fast-optimization, we strip done tasks.
    
    for line in lines:
        if line.strip().startswith("- [x]"):
            archived_lines.append(line)
        else:
            active_lines.append(line)

    if not archived_lines:
        print("  No completed items found.")
        return

    # Write back active
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(active_lines)

    # Append to archive
    timestamp = datetime.datetime.now().strftime("%Y-%m")
    archive_file = os.path.join(ARCHIVE_DIR, f"archive_{timestamp}_{filename}")
    
    with open(archive_file, 'a', encoding='utf-8') as f:
        f.write(f"\n\n--- Archived on {datetime.datetime.now()} ---\n")
        f.writelines(archived_lines)

    print(f"  Moved {len(archived_lines)} items to {os.path.basename(archive_file)}")

def main():
    ensure_archive()
    # List of files to clean
    targets = ["tasks.md", "bugs-master.md", "boss-requests.md"]
    
    for target in targets:
        vacuum_file(target)

if __name__ == "__main__":
    main()
