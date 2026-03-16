import fs from 'fs';
import path from 'path';

const TASK_MASTER_PATH = path.resolve(process.cwd(), '../../5. Trackers/TASK_MASTER.md');

export async function POST(request) {
  try {
    const { id, field, value } = await request.json();
    
    let content = fs.readFileSync(TASK_MASTER_PATH, 'utf8');
    let lines = content.split('\n');
    let updated = false;

    const newLines = lines.map(line => {
      const rawParts = line.split('|');
      if (rawParts.length >= 11) {
        const rowId = rawParts[5].replace(/\*\*/g, '').trim();
        
        if (rowId === id) {
          // Schema indices (1-indexed split):
          // 0: "", 1: Prio, 2: Proj, 3: Reason, 4: Due, 5: ID, 6: Task, 7: Desc, 8: Status, 9: Stage, 10: Owner, 11: ""
          
          let index = -1;
          switch(field) {
            case 'priority': index = 1; break;
            case 'project': index = 2; break;
            case 'reason': index = 3; break;
            case 'due': index = 4; break;
            case 'status': index = 8; break;
            case 'stage': index = 9; break;
            case 'owner': index = 10; break;
          }

          if (index !== -1) {
            rawParts[index] = ` ${value.trim()} `;
            updated = true;
            return rawParts.join('|');
          }
        }
      }
      return line;
    });

    if (updated) {
      fs.writeFileSync(TASK_MASTER_PATH, newLines.join('\n'));
      return new Response(JSON.stringify({ success: true }), { status: 200 });
    }

    return new Response(JSON.stringify({ error: 'Task not found' }), { status: 404 });
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), { status: 500 });
  }
}
