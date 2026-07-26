#!/usr/bin/env python3
"""Dependency-free local state memory for Beats PM Kit.

Implements symbolic short-term state (a Mermaid graph) and layered long-term
memory (L0 traces, L1 facts, and L2 scenarios). Optional semantic recall lives
behind ``personal_memory.py`` so this canonical store remains portable.
"""

import sys
import os
import json
import argparse
import re
from datetime import datetime
from pathlib import Path

# Paths relative to repository root
ROOT = Path(__file__).resolve().parents[2]
MEMORY_DIR = ROOT / ".beats" / "memory"
TRACES_DIR = MEMORY_DIR / "traces"
FACTS_FILE = MEMORY_DIR / "facts.json"
SCENARIOS_FILE = MEMORY_DIR / "scenarios.json"
GRAPH_FILE = MEMORY_DIR / "symbolic_graph.mermaid"
SESSION_MEMORY_FILE = ROOT / "SESSION_MEMORY.md"

def ensure_initialized():
    """Ensure directories and files exist."""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    TRACES_DIR.mkdir(parents=True, exist_ok=True)
    
    if not FACTS_FILE.exists():
        with open(FACTS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2)
            
    if not SCENARIOS_FILE.exists():
        with open(SCENARIOS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2)
            
    if not GRAPH_FILE.exists():
        with open(GRAPH_FILE, "w", encoding="utf-8") as f:
            f.write("graph TD\n  Start[System Initialized] --> Active[Active Session]\n")

def load_json(filepath: Path) -> list:
    ensure_initialized()
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_json(filepath: Path, data: list):
    ensure_initialized()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# L1: Atomic Facts Management
def add_fact(content: str, category: str = "general") -> bool:
    content = content.strip()
    if not content:
        return False
    facts = load_json(FACTS_FILE)
    # Deduplicate
    for fact in facts:
        if fact.get("content", "").lower() == content.lower():
            return False
            
    new_fact = {
        "id": len(facts) + 1,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "category": category,
        "content": content
    }
    facts.append(new_fact)
    save_json(FACTS_FILE, facts)
    sync_session_memory()
    return True

def remove_fact(fact_id_or_content: str) -> bool:
    facts = load_json(FACTS_FILE)
    original_len = len(facts)
    
    if fact_id_or_content.isdigit():
        fid = int(fact_id_or_content)
        facts = [f for f in facts if f.get("id") != fid]
    else:
        facts = [f for f in facts if f.get("content", "").lower() != fact_id_or_content.lower()]
        
    if len(facts) < original_len:
        # Re-index
        for idx, fact in enumerate(facts):
            fact["id"] = idx + 1
        save_json(FACTS_FILE, facts)
        sync_session_memory()
        return True
    return False

def list_facts(category: str = None) -> list:
    facts = load_json(FACTS_FILE)
    if category:
        facts = [f for f in facts if f.get("category", "").lower() == category.lower()]
    return facts

# L2: Scenarios Management
def add_scenario(title: str, description: str, details: str = "") -> bool:
    title = title.strip()
    description = description.strip()
    if not title or not description:
        return False
        
    scenarios = load_json(SCENARIOS_FILE)
    new_scenario = {
        "id": len(scenarios) + 1,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "title": title,
        "description": description,
        "details": details
    }
    scenarios.append(new_scenario)
    save_json(SCENARIOS_FILE, scenarios)
    sync_session_memory()
    return True

def list_scenarios() -> list:
    return load_json(SCENARIOS_FILE)

# L0: Traces Management (Offloaded Logs)
def log_trace(source: str, trace_content: str):
    ensure_initialized()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_source = "".join(c for c in source if c.isalnum() or c in ("-", "_")).strip()
    filename = f"{timestamp}_{safe_source}.md"
    filepath = TRACES_DIR / filename
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# Trace: {source}\n")
        f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Content\n")
        f.write(trace_content)
        f.write("\n")
    print(f"Logged trace to {filepath.name}")

# Symbolic Short-Term Memory Graph Parser/Modifier
def get_graph_content() -> str:
    ensure_initialized()
    try:
        return GRAPH_FILE.read_text(encoding="utf-8")
    except Exception:
        return "graph TD\n"

def set_graph_content(content: str):
    ensure_initialized()
    # Normalize line endings
    content = content.replace("\r\n", "\n")
    if not content.strip().startswith("graph"):
        content = "graph TD\n" + content
    GRAPH_FILE.write_text(content, encoding="utf-8")
    sync_session_memory()

def parse_mermaid_nodes_and_edges(content: str) -> tuple[dict[str, str], list[tuple[str, str, str]]]:
    """Parse node IDs, labels, and edges from Mermaid syntax."""
    nodes = {}
    edges = []
    
    # Matches: id["Label"] or id(Label) or id[Label] or id
    node_pattern = re.compile(r'^\s*([a-zA-Z0-9_\-]+)(?:\["([^"]+)"\]|\[([^\]]+)\]|\(([^)]+)\)|)?\s*$')
    # Matches: source --> target or source -->|label| target
    edge_pattern_labeled = re.compile(r'^\s*([a-zA-Z0-9_\-]+)\s*-->\s*\|([^|]+)\|\s*([a-zA-Z0-9_\-]+)\s*$')
    edge_pattern_unlabeled = re.compile(r'^\s*([a-zA-Z0-9_\-]+)\s*-->\s*([a-zA-Z0-9_\-]+)\s*$')
    
    for line in content.split("\n"):
        line = line.strip()
        if not line or line.startswith("graph"):
            continue
            
        # Try edge labeled
        m = edge_pattern_labeled.match(line)
        if m:
            edges.append((m.group(1), m.group(3), m.group(2)))
            continue
            
        # Try edge unlabeled
        m = edge_pattern_unlabeled.match(line)
        if m:
            edges.append((m.group(1), m.group(2), ""))
            continue
            
        # Try node
        # Strip comments
        if "%%" in line:
            line = line.split("%%")[0].strip()
        if not line:
            continue
            
        # Match node pattern or simple words
        m = node_pattern.match(line)
        if m:
            node_id = m.group(1)
            label = m.group(2) or m.group(3) or m.group(4) or node_id
            nodes[node_id] = label
            
    return nodes, edges

def build_mermaid_graph(nodes: dict[str, str], edges: list[tuple[str, str, str]]) -> str:
    lines = ["graph TD"]
    # Write nodes
    for node_id, label in nodes.items():
        lines.append(f'  {node_id}["{label}"]')
    # Write edges
    for src, dst, lbl in edges:
        if lbl:
            lines.append(f'  {src} -->|"{lbl}"| {dst}')
        else:
            lines.append(f'  {src} --> {dst}')
    return "\n".join(lines) + "\n"

def update_graph(add_nodes: list[tuple[str, str]] = None, 
                 add_edges: list[tuple[str, str, str]] = None,
                 remove_nodes: list[str] = None,
                 remove_edges: list[tuple[str, str]] = None):
    """Surgically update nodes and edges in the Mermaid graph."""
    content = get_graph_content()
    nodes, edges = parse_mermaid_nodes_and_edges(content)
    
    # 1. Add nodes
    if add_nodes:
        for node_id, label in add_nodes:
            nodes[node_id] = label
            
    # 2. Add edges
    if add_edges:
        for src, dst, lbl in add_edges:
            # Add endpoint nodes if they don't exist
            if src not in nodes:
                nodes[src] = src
            if dst not in nodes:
                nodes[dst] = dst
            # Avoid duplicate edges
            exists = False
            for s, d, _ in edges:
                if s == src and d == dst:
                    exists = True
                    break
            if not exists:
                edges.append((src, dst, lbl))
                
    # 3. Remove edges
    if remove_edges:
        edges = [e for e in edges if not any(e[0] == s and e[1] == d for s, d in remove_edges)]
        
    # 4. Remove nodes
    if remove_nodes:
        for node_id in remove_nodes:
            if node_id in nodes:
                del nodes[node_id]
        # Clean up dangling edges
        edges = [e for e in edges if e[0] in nodes and e[1] in nodes]
        
    new_content = build_mermaid_graph(nodes, edges)
    set_graph_content(new_content)

# Synchronization to SESSION_MEMORY.md
def sync_session_memory():
    """Update root SESSION_MEMORY.md with facts, scenarios, and Mermaid graph."""
    ensure_initialized()
    graph = get_graph_content().strip()
    facts = load_json(FACTS_FILE)
    scenarios = load_json(SCENARIOS_FILE)
    
    lines = [
        "# Session Memory",
        "> Last known state registry for the local Beats PM Kit memory.",
        "",
        "## 📊 Symbolic Short-Term State (Mermaid Graph)",
        "```mermaid",
        graph,
        "```",
        "",
        "## 🧠 Layered Long-Term Memory",
        "",
        "### 💡 L1: Atomic Facts",
    ]
    
    if not facts:
        lines.append("- No atomic facts recorded yet.")
    else:
        for f in facts:
            lines.append(f"- **[{f.get('id')}]** *({f.get('category')})* {f.get('content')} *(Added: {f.get('timestamp')})*")
            
    lines.extend([
        "",
        "### 🎬 L2: Scenarios & Scene Blocks",
    ])
    
    if not scenarios:
        lines.append("- No scenarios recorded yet.")
    else:
        for s in scenarios:
            lines.append(f"- **{s.get('title')}** *({s.get('timestamp')})*")
            lines.append(f"  {s.get('description')}")
            if s.get("details"):
                lines.append(f"  *Details:* {s.get('details')}")
                
    lines.append("")
    
    SESSION_MEMORY_FILE.write_text("\n".join(lines), encoding="utf-8")
    print("SESSION_MEMORY.md successfully synchronized.")

# Memory Consolidation: compiling L0 traces to L1 facts and L2 scenarios
def consolidate_memory(hours_ago: int = 168):
    """Consolidate raw logs and traces into L1 facts and L2 scenarios."""
    print(f"Consolidating memory traces modified in the last {hours_ago} hours...")
    # Find trace files
    ensure_initialized()
    cutoff_time = datetime.now().timestamp() - (hours_ago * 3600)
    trace_files = []
    
    for filepath in TRACES_DIR.glob("*.md"):
        try:
            if filepath.stat().st_mtime >= cutoff_time:
                trace_files.append(filepath)
        except Exception:
            continue
            
    if not trace_files:
        print("No recent traces eligible for consolidation.")
        return
        
    print(f"Found {len(trace_files)} traces. Starting distillation...")
    
    # In a full agent execution, the model itself does the actual parsing/distillation of traces.
    # The CLI tool logs which traces were processed and registers a scenario block for the consolidation event.
    details = f"Processed {len(trace_files)} traces: " + ", ".join(f.name for f in trace_files)
    add_scenario(
        "Memory Consolidation Sweeper",
        f"Consolidated traces from the last {hours_ago} hours into atomic state facts.",
        details
    )
    
    # Auto-archive trace files to a subdirectory so they are cleared from the active queue
    archive_dir = TRACES_DIR / "archive"
    archive_dir.mkdir(exist_ok=True)
    for f in trace_files:
        shutil_move_safe(f, archive_dir / f.name)
        
    print(f"Consolidated and archived {len(trace_files)} traces.")

def shutil_move_safe(src: Path, dst: Path):
    import shutil
    try:
        shutil.move(str(src), str(dst))
    except Exception as e:
        print(f"Failed to move {src.name} to archive: {e}")

def main():
    parser = argparse.ArgumentParser(description="Beats PM Kit local memory CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # init
    subparsers.add_parser("init", help="Initialize the memory folders and stubs")
    
    # add-fact
    add_fact_parser = subparsers.add_parser("add-fact", help="Add an L1 atomic fact")
    add_fact_parser.add_argument("content", help="The fact text")
    add_fact_parser.add_argument("--category", default="general", help="Category of the fact")
    
    # remove-fact
    remove_fact_parser = subparsers.add_parser("remove-fact", help="Remove an L1 fact by ID or content")
    remove_fact_parser.add_argument("target", help="Fact ID or content text")
    
    # list-facts
    list_facts_parser = subparsers.add_parser("list-facts", help="List L1 facts")
    list_facts_parser.add_argument("--category", default=None, help="Filter by category")
    
    # add-scenario
    add_scenario_parser = subparsers.add_parser("add-scenario", help="Add an L2 scenario block")
    add_scenario_parser.add_argument("title", help="Scenario title")
    add_scenario_parser.add_argument("description", help="Scenario description")
    add_scenario_parser.add_argument("--details", default="", help="Detailed scenario information")
    
    # list-scenarios
    subparsers.add_parser("list-scenarios", help="List L2 scenarios")
    
    # log-trace
    log_trace_parser = subparsers.add_parser("log-trace", help="Log an L0 context trace")
    log_trace_parser.add_argument("source", help="Trace source/name")
    log_trace_parser.add_argument("content", help="Raw trace log content")
    
    # get-graph
    subparsers.add_parser("get-graph", help="Print the current short-term Mermaid graph")
    
    # set-graph
    set_graph_parser = subparsers.add_parser("set-graph", help="Set the current short-term Mermaid graph content")
    set_graph_parser.add_argument("content", help="Full Mermaid graph text")
    
    # update-graph
    update_graph_parser = subparsers.add_parser("update-graph", help="Surgically update nodes/edges of the Mermaid graph")
    update_graph_parser.add_argument("--add-node", nargs=2, action="append", metavar=("ID", "LABEL"), help="Add a node")
    update_graph_parser.add_argument("--add-edge", nargs=3, action="append", metavar=("SRC", "DST", "LABEL"), help="Add an edge")
    update_graph_parser.add_argument("--remove-node", action="append", metavar="ID", help="Remove a node")
    update_graph_parser.add_argument("--remove-edge", nargs=2, action="append", metavar=("SRC", "DST"), help="Remove an edge")
    
    # consolidate
    consolidate_parser = subparsers.add_parser("consolidate", help="Consolidate old traces")
    consolidate_parser.add_argument("--hours", type=int, default=168, help="Hours lookback")
    
    # sync
    subparsers.add_parser("sync", help="Force synchronize SESSION_MEMORY.md")
    
    args = parser.parse_args()
    
    if args.command == "init":
        ensure_initialized()
        print("Agentic Memory initialized successfully.")
        
    elif args.command == "add-fact":
        if add_fact(args.content, args.category):
            print(f"Added L1 fact under '{args.category}': {args.content}")
        else:
            print("Fact already exists or is invalid.")
            
    elif args.command == "remove-fact":
        if remove_fact(args.target):
            print(f"Removed L1 fact: {args.target}")
        else:
            print("Fact not found.")
            
    elif args.command == "list-facts":
        facts = list_facts(args.category)
        print(json.dumps(facts, indent=2))
        
    elif args.command == "add-scenario":
        if add_scenario(args.title, args.description, args.details):
            print(f"Added L2 scenario: {args.title}")
        else:
            print("Invalid scenario details.")
            
    elif args.command == "list-scenarios":
        scenarios = list_scenarios()
        print(json.dumps(scenarios, indent=2))
        
    elif args.command == "log-trace":
        log_trace(args.source, args.content)
        
    elif args.command == "get-graph":
        print(get_graph_content())
        
    elif args.command == "set-graph":
        set_graph_content(args.content)
        print("Mermaid graph updated.")
        
    elif args.command == "update-graph":
        add_nodes = [(n[0], n[1]) for n in args.add_node] if args.add_node else None
        add_edges = [(e[0], e[1], e[2]) for e in args.add_edge] if args.add_edge else None
        remove_nodes = args.remove_node if args.remove_node else None
        remove_edges = [(e[0], e[1]) for e in args.remove_edge] if args.remove_edge else None
        
        update_graph(add_nodes=add_nodes, add_edges=add_edges, remove_nodes=remove_nodes, remove_edges=remove_edges)
        print("Mermaid graph updated programmatically.")
        
    elif args.command == "consolidate":
        consolidate_memory(args.hours)
        
    elif args.command == "sync":
        sync_session_memory()

if __name__ == "__main__":
    main()
