
import os
import datetime

TASK_MASTER_PATH = "/Users/ernesto/Library/Mobile Documents/com~apple~CloudDocs/Vibe-Coding/beats-pm-antigravity-brain/5. Trackers/TASK_MASTER.md"

def get_priority_reason(row_text):
    """
    Infers a short 3-word reason based on content.
    """
    row_lower = row_text.lower()
    
    if "gabriel" in row_lower or "boss" in row_lower or "sudip" in row_lower:
        return "Boss Ask"
    if "bug" in row_lower or "fix" in row_lower or "incident" in row_lower:
        return "Stability"
    if "uat" in row_lower:
        return "Unblock QA"
    if "gov" in row_lower or "audit" in row_lower or "legal" in row_lower:
        return "Compliance"
    if "security" in row_lower or "sec-" in row_lower or "certificate" in row_lower:
        return "Security"
    if "prep" in row_lower or "plan" in row_lower or "discovery" in row_lower:
        return "Planning"
    if "r1" in row_lower or "salesforce" in row_lower:
        return "Partner Req"
    
    return "Strategic"

def migrate_schema():
    with open(TASK_MASTER_PATH, 'r') as f:
        lines = f.readlines()

    new_lines = []
    
    for line in lines:
        if line.strip().startswith('|'):
            parts = [p.strip() for p in line.split('|')]
            # Expected Old: empty, Prio, Due, ID, Task, Desc, Status, Owner, empty
            # Length usually 9 due to split on first/last pipe
            
            if len(parts) >= 8: # Valid row
                # Check if header
                if "Priority" in parts[1]:
                    # Update Header
                    # New: Priority | Reason | Due ...
                     new_line = "| Priority | Reason | Due | ID | Task | Description | Status | Owner |\n"
                     new_lines.append(new_line)
                elif "---" in parts[1]:
                    # Update Separator
                    new_line = "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
                    new_lines.append(new_line)
                else:
                    # Data Row
                    prio = parts[1]
                    due = parts[2]
                    tid = parts[3]
                    task = parts[4]
                    desc = parts[5]
                    status = parts[6]
                    owner = parts[7]
                    
                    reason = get_priority_reason(line)
                    
                    # Construct new row
                    new_line = f"| {prio} | {reason} | {due} | {tid} | {task} | {desc} | {status} | {owner} |\n"
                    new_lines.append(new_line)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    with open(TASK_MASTER_PATH, 'w') as f:
        f.writelines(new_lines)
    
    print("Schema Migrated Successfully.")

if __name__ == "__main__":
    migrate_schema()
