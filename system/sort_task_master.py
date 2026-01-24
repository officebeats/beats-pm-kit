
import os
import re
from datetime import datetime

TASK_MASTER_PATH = "/Users/ernesto/Library/Mobile Documents/com~apple~CloudDocs/Vibe-Coding/beats-pm-antigravity-brain/5. Trackers/TASK_MASTER.md"

def parse_date_score(due_str):
    """
    Returns a sorting key for due dates.
    Lower score = Earlier/Higher Priority.
    """
    s = due_str.strip().upper()
    
    if "NOW" in s:
        return 0
    if "ASAP" in s:
        return 1
    
    # Try parsing "Month Day" format (e.g. Jan 15)
    try:
        # Assume current year 2026 based on metadata context, or handle rollover if needed
        dt = datetime.strptime(s, "%b %d")
        return dt.timetuple().tm_yday + 10  # Offset to be after NOW/ASAP
    except ValueError:
        pass
        
    return 999 # TBD, Text, PI Prep, etc go last

def parse_priority_score(prio_str):
    """
    Returns a sorting key for priority.
    """
    s = prio_str.strip()
    if "P0" in s: return 0
    if "P1" in s: return 1
    if "P2" in s: return 2
    return 3

def sort_tasks():
    with open(TASK_MASTER_PATH, 'r') as f:
        lines = f.readlines()

    header_lines = []
    table_lines = []
    footer_lines = []
    
    in_table = False
    
    # Simple parser: Grab the header (Legend, etc), then the table rows
    for line in lines:
        if line.strip().startswith('|'):
            table_lines.append(line)
        elif len(table_lines) > 0 and not line.strip().startswith('|'):
             # Table ended
             footer_lines.append(line)
        else:
            if len(table_lines) == 0:
                header_lines.append(line)
            else:
                footer_lines.append(line)

    if not table_lines:
        print("No table found to sort.")
        return

    # Separate Header Row and Separator
    table_header = table_lines[0]
    table_sep = table_lines[1]
    data_rows = table_lines[2:]

    active_rows = []
    done_rows = []

    for row in data_rows:
        # Ignore matching header or separator lines that might have been read in
        if row.strip() == table_header.strip() or row.strip() == table_sep.strip():
            continue
            
        if "🟢 Done" in row or "✅ Done" in row or "~~" in row:
            done_rows.append(row)
        else:
            active_rows.append(row)

    # Sort Active Rows
    # Table columns: | Priority | Reason | Due | ID | Task | Description | Status | Owner |
    # Indices (split by |): 0 empty, 1 Prio, 2 Reason, 3 Due, ...
    
    def sort_key(row):
        parts = [p.strip() for p in row.split('|')]
        if len(parts) < 4: return (99, 99)
        
        prio = parts[1]
        due = parts[3] # Due date is now index 3
        
        return (parse_priority_score(prio), parse_date_score(due))

    active_rows.sort(key=sort_key)

    # Reconstruct File
    new_content = []
    
    # Original Header
    new_content.extend(header_lines)
    
    # Active Table
    new_content.append(table_header)
    new_content.append(table_sep)
    new_content.extend(active_rows)
    new_content.append("\n")
    
    # Completed Table Section
    new_content.append("## ✅ Completed Tasks\n\n")
    new_content.append(table_header) # Re-use header
    new_content.append(table_sep)
    new_content.extend(done_rows)

    with open(TASK_MASTER_PATH, 'w') as f:
        f.writelines(new_content)
    
    print(f"Sorted TASK_MASTER.md: {len(active_rows)} Active, {len(done_rows)} Completed.")

if __name__ == "__main__":
    sort_tasks()
