import os
import datetime
import time
from pathlib import Path

# Paths
BRAIN_ROOT = Path(os.getcwd())
TASK_MASTER = BRAIN_ROOT / "5. Trackers" / "TASK_MASTER.md"
STATUS_FILE = BRAIN_ROOT / "STATUS.md"
SESSION_MEMORY = BRAIN_ROOT / "SESSION_MEMORY.md"

def get_day_part():
    hour = datetime.datetime.now().hour
    weekday = datetime.datetime.now().weekday() # 0=Mon, 6=Sun
    
    if weekday == 4 and hour >= 15:
        return "Friday PM"
    elif hour < 11:
        return "Morning"
    elif 11 <= hour <= 13:
        return "Lunch"
    elif 13 < hour < 17:
        return "Afternoon"
    else:
        return "Evening"

def count_critical_tasks():
    if not TASK_MASTER.exists():
        return 0
    
    count = 0
    try:
        with open(TASK_MASTER, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line in lines:
            line = line.strip()
            if not line.startswith("|") or "---" in line or "Priority" in line:
                continue
            
            # Robust Split: Handle escaped pipes if needed (simplified here)
            parts = [p.strip() for p in line.split("|")]
            
            # Markdown table rows often start/end with empty strings from split
            # | Col1 | Col2 | -> ['', 'Col1', 'Col2', '']
            if len(parts) < 7: 
                continue
                
            priority = parts[1].lower()
            status = parts[5].lower()
            
            # Check Criticality
            is_high = any(x in priority for x in ["high", "p0", "urgent", "critical"])
            
            # Check Active
            is_done = any(x in status for x in ["done", "completed", "✅", "closed"])
            
            if is_high and not is_done:
                count += 1
    except Exception as e:
        print(f"Debug: Pulse Error - {e}")
        pass 
        
    return count

def check_staleness():
    if not STATUS_FILE.exists():
        return "Never"
    
    mtime = STATUS_FILE.stat().st_mtime
    age_hours = (time.time() - mtime) / 3600
    
    if age_hours > 24:
        return "Stale (>24h)"
    elif age_hours > 4:
        return "Needs Update (>4h)"
    else:
        return "Fresh"

def main():
    part = get_day_part()
    crit_count = count_critical_tasks()
    status_health = check_staleness()
    
    # 🧠 The Pulse Logic
    
    emoji = "⚡"
    msg = ""
    
    if part == "Friday PM":
        emoji = "🎉"
        msg = "It's Friday afternoon. Time for a `/week` review?"
    elif part == "Morning":
        emoji = "☕"
        msg = f"Good morning. You have {crit_count} Critical Tasks."
        if crit_count > 0:
            msg += " Run `/day` to tackle them."
        else:
            msg += " Clear skies."
    elif part == "Lunch":
        emoji = "🥪"
        msg = "Mid-day check. How's the momentum?"
    else:
        # Afternoon / Evening
        if crit_count > 3:
            emoji = "🔥"
            msg = f"Heavy load: {crit_count} criticals remaining."
        elif status_health == "Stale (>24h)":
            emoji = "🕸️"
            msg = "Your STATUS is gathering dust. Run `/status`?"
        else:
            emoji = "🧠"
            msg = "System active. Ready."

    print(f"\n{emoji} **The Pulse**: {msg}")
    print(f"   (Context: {part} | Criticals: {crit_count} | Status: {status_health})\n")

if __name__ == "__main__":
    main()
