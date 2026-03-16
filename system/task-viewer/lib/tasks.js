import fs from 'fs';
import path from 'path';

export async function getTasks() {
  // Use relative path to the task master file from the app root
  const filePath = path.resolve(process.cwd(), '../../5. Trackers/TASK_MASTER.md');
  
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split('\n');
    
    let activeTasks = [];
    let completedTasks = [];
    let inCompleted = false;
    
    for (const line of lines) {
      const clean = line.trim();
      if (clean.includes("## ✅ Completed Tasks")) {
        inCompleted = true;
        continue;
      }
      
      if (clean.startsWith('|') && !clean.includes('Priority |') && !clean.includes(':---')) {
        const parts = clean.split('|').map(p => p.trim()).filter(p => p !== '');
        
        if (parts.length >= 10) {
          const task = {
            priorityRaw: parts[0],
            priority: parts[0].includes('P0') ? 'P0' : parts[0].includes('P1') ? 'P1' : 'P2',
            project: parts[1],
            reason: parts[2],
            due: parts[3],
            id: parts[4],
            title: parts[5].replace(/\*\*/g, ''),
            description: parts[6],
            status: parts[7], // Now, Next Week, Later
            stage: parts[8].replace(/\*\*/g, ''), // Old status values (New, Active, etc)
            owner: parts[9]
          };
          
          if (inCompleted) {
            completedTasks.push(task);
          } else {
            activeTasks.push(task);
          }
        }
      }
    }
    
    return {
      active: activeTasks,
      completed: completedTasks,
      stats: {
        p0: activeTasks.filter(t => t.priority === 'P0').length,
        p1: activeTasks.filter(t => t.priority === 'P1').length,
        p2: activeTasks.filter(t => t.priority === 'P2').length,
        done: completedTasks.length
      }
    };
  } catch (error) {
    console.error("Error reading tasks:", error);
    return { active: [], completed: [], stats: { p0: 0, p1: 0, p2: 0, done: 0 } };
  }
}
