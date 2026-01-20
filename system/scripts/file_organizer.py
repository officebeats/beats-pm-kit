import os
import shutil
import datetime

# Configuration
INCOMING_DIR = "0. Incoming"
PROCESSED_DIR = os.path.join(INCOMING_DIR, "processed")
FYI_DIR = os.path.join(INCOMING_DIR, "fyi")
BRAIN_DUMP_FILE = os.path.join(INCOMING_DIR, "BRAIN_DUMP.md")

# Ensure processed directory exists
if not os.path.exists(PROCESSED_DIR):
    os.makedirs(PROCESSED_DIR)

def scan_and_process():
    print(f"--- 📂 Scanning {INCOMING_DIR} for new files ---")
    
    # Get all files in Incoming (not directories)
    files = [f for f in os.listdir(INCOMING_DIR) if os.path.isfile(os.path.join(INCOMING_DIR, f))]
    
    # Filter out system files
    ignored_files = ["BRAIN_DUMP.md", ".gitkeep"]
    new_files = [f for f in files if f not in ignored_files]

    if not new_files:
        print("✅ No new files found.")
        return

    print(f"🔎 Found {len(new_files)} file(s): {', '.join(new_files)}")
    
    for filename in new_files:
        file_path = os.path.join(INCOMING_DIR, filename)
        
        # 🤖 Auto-Sort Heuristic: Transcripts (YYYY-MM-DD_*.txt)
        # These are "Task Sources" from the db_bridge
        if filename[0:4].isdigit() and filename[4] == '-' and filename.endswith(".txt"):
            print(f"🤖 Auto-detected Transcript: {filename} -> Task Source")
            move_to_processed(file_path, filename, "task_source")
            continue

        # Interaction Loop
        print(f"\n📄 Processing: {filename}")
        print("What kind of file is this?")
        print("[1] Task Source (Extract actions)")
        print("[2] Reference / FYI (Just file away)")
        print("[3] Spec / Doc (Move to Products)")
        print("[4] Skip")
        
        choice = input("Select option (1-4): ").strip()
        
        if choice == "1": # Task Source
            # We don't move it to a specific folder, we keep it for processing but log it
            print("   -> 📝 Marked as Task Source. Please manually add tasks to TASK_MASTER.md referencing this file.")
            # Move to processed after "extraction" (symbolic here, user does extraction)
            move_to_processed(file_path, filename, "task_source")
            
        elif choice == "2": # Reference
            # Move to FYI
            if not os.path.exists(FYI_DIR):
                os.makedirs(FYI_DIR)
            new_path = os.path.join(FYI_DIR, filename)
            shutil.move(file_path, new_path)
            print(f"   -> 📂 Moved to {FYI_DIR}")
            
        elif choice == "3": # Spec
            # Move to processed but flag for PRD
            print("   -> 🚀 Marked as Product Spec.")
            move_to_processed(file_path, filename, "spec")
            
        elif choice == "4": # Skip
            print("   -> ⏭️ Skipped.")
            continue
            
        else:
            print("   -> 🤷 Unclear. Moving to 'processed/unclassified' to clear inbox.")
            move_to_processed(file_path, filename, "unclassified")

def move_to_processed(src, filename, tag):
    # Add timestamp to filename to prevent collisions
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    name, ext = os.path.splitext(filename)
    new_filename = f"{timestamp}_{name}{ext}"
    dest = os.path.join(PROCESSED_DIR, new_filename)
    
    shutil.move(src, dest)
    print(f"   -> ✅ Archived to {PROCESSED_DIR} (Tag: {tag})")

if __name__ == "__main__":
    scan_and_process()
