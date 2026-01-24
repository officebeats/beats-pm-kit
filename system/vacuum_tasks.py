
import os

TASK_MASTER_PATH = "/Users/ernesto/Library/Mobile Documents/com~apple~CloudDocs/Vibe-Coding/beats-pm-antigravity-brain/5. Trackers/TASK_MASTER.md"
ARCHIVE_PATH = "/Users/ernesto/Library/Mobile Documents/com~apple~CloudDocs/Vibe-Coding/beats-pm-antigravity-brain/5. Trackers/archive/tasks_archive_2026.md"

def vacuum_tasks():
    with open(TASK_MASTER_PATH, 'r') as f:
        lines = f.readlines()

    active_content = []
    completed_content = []
    
    in_completed_section = False
    
    for line in lines:
        if "## ✅ Completed Tasks" in line:
            in_completed_section = True
            active_content.append(line) # Keep the header
            # Add table header and separator to active file if removed
            active_content.append("\n") 
            active_content.append("| Priority | Reason | Due | ID | Task | Description | Status | Owner |\n")
            active_content.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
            continue
            
        if in_completed_section:
            if line.strip().startswith('|') and "Done" in line:
                completed_content.append(line)
        else:
            active_content.append(line)

    if not completed_content:
        print("No completed tasks to archive.")
        return

    # Append to Archive
    with open(ARCHIVE_PATH, 'a') as f:
        for row in completed_content:
            f.write(row)
            
    # Rewrite Master
    with open(TASK_MASTER_PATH, 'w') as f:
        f.writelines(active_content)
        
    print(f"Vacuumed {len(completed_content)} tasks to archive.")

if __name__ == "__main__":
    vacuum_tasks()
