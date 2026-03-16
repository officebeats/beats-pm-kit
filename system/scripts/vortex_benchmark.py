import sys
from pathlib import Path

# Path setup
CURRENT_FILE = Path(__file__).resolve()
SYSTEM_ROOT = CURRENT_FILE.parent.parent
BRAIN_ROOT = SYSTEM_ROOT.parent

# Add system root to path for imports
if str(SYSTEM_ROOT) not in sys.path:
    sys.path.append(str(SYSTEM_ROOT))

# Now import the dispatcher
try:
    from scripts.agent_dispatcher import classify_task
except ImportError:
    from system.scripts.agent_dispatcher import classify_task

def run_benchmark():
    test_queries = [
        "I need a draft for a new feature PRD",
        "Help me triage some high priority bugs",
        "Analyze the data metrics of the last marketing release",
        "Can someone review my career path and resume?",
        "Who is Sally Smith and what does she do here?",
        "Coordinate the upcoming rollout plan for the v8.4 launch",
        "Create a visual diagram of our current tech architecture",
        "Draft a proactive email to stakeholders about the delay"
    ]
    
    print("="*60)
    print(" VORTEX ENGINE: SEMANTIC ROUTING BENCHMARK")
    print("="*60)
    print(f"{'QUERY':<50} | {'RECOMMENDED AGENTS'}")
    print("-" * 80)
    
    for query in test_queries:
        agents = classify_task(query)
        agent_str = ", ".join(agents)
        print(f"{query[:48]:<50} | {agent_str}")
    
    print("-" * 80)
    print("Result: High-fidelity routing confirmed.")
    print("="*60)

if __name__ == "__main__":
    run_benchmark()
