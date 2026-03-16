import { getTasks } from '@/lib/tasks';
import TaskDashboard from '@/components/Dashboard';

export const dynamic = 'force-dynamic';
export const revalidate = 0;

export default async function Home() {
  const initialTasks = await getTasks();
  
  return (
    <TaskDashboard initialTasks={initialTasks} />
  );
}
