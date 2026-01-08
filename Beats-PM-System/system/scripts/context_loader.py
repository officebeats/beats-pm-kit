"""
Context Loader Utility

Designed for Google Antigravity Efficiencies (Gemini 1M+ Context Window).
Ingests entire directories of markdown files into a single context stream.
This minimizes tool round-trips and maximizes the "Conductor" agent's reasoning ability.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.ui import print_error

def load_context(directory_path, ignore_dirs=None):
    """
    Recursively loads all markdown files from a directory.
    """
    if ignore_dirs is None:
        ignore_dirs = ['archive', 'templates', '.git']
        
    full_path = os.path.abspath(directory_path)
    
    if not os.path.exists(full_path):
        print_error(f"Directory not found: {full_path}")
        return
        
    print(f"--- CONTEXT LOAD: {full_path} ---")
    
    file_count = 0
    
    for root, dirs, files in os.walk(full_path):
        # Filter directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]
        
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, full_path)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    print(f"\n<<< START AGENT CONTEXT: {rel_path} >>>\n")
                    print(content)
                    print(f"\n<<< END AGENT CONTEXT: {rel_path} >>>\n")
                    file_count += 1
                except Exception as e:
                    print(f"Error reading {file}: {e}")

    print(f"--- LOAD COMPLETE: {file_count} files ---")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python context_loader.py <directory_path>")
        sys.exit(1)
        
    target_dir = sys.argv[1]
    load_context(target_dir)
