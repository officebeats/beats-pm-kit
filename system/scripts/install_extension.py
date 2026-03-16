import os
import shutil
import sys
from pathlib import Path
import json

def main():
    print("Installing Antigravity RPC Extension...")
    
    # Source directory (inside the repo)
    repo_ext_dir = Path(__file__).resolve().parent.parent / "extensions" / "antigravity.antigravity-rpc"
    
    if not repo_ext_dir.exists():
        print(f"Error: Extension source not found at {repo_ext_dir}")
        print("Skipping extension installation.")
        sys.exit(0) # Don't fail the whole update
        
    # Read package.json to get version
    pkg_json_path = repo_ext_dir / "package.json"
    version = "0.0.14"
    if pkg_json_path.exists():
        try:
            with open(pkg_json_path, "r", encoding="utf-8") as f:
                pkg_data = json.load(f)
                version = pkg_data.get("version", version)
        except Exception:
            pass
            
    # The actual folder in the user's system is typically antigravity.antigravity-rpc-{version}-universal
    # OR just antigravity.antigravity-rpc-{version} depending on how it was originally installed.
    # To be safe and override the old one, we will use the universal suffix since that's what was present.
    dest_name = f"antigravity.antigravity-rpc-{version}-universal"
    
    home = Path.home()
    target_dirs = [
        home / ".antigravity" / "extensions",
        home / ".vscode" / "extensions",
        home / ".kilocode" / "extensions"
    ]
    
    installed = False
    
    for target in target_dirs:
        # Only install to editors the user actually has installed
        if target.parent.exists():
            target.mkdir(exist_ok=True)
            dest_dir = target / dest_name
            
            print(f"Installing to {dest_dir}...")
            try:
                if dest_dir.exists():
                    shutil.rmtree(dest_dir, ignore_errors=True)
                    
                shutil.copytree(repo_ext_dir, dest_dir)
                installed = True
                print(f"  -> Successfully installed extension to {target}")
            except Exception as e:
                print(f"  -> Failed to install to {target}: {e}")
            
    if installed:
        print("Extension installation complete. Features include 'Vibe Coding' Slack sync and privacy fallbacks.")
        print("Please restart your editor to apply.")
    else:
        print("No compatible editors found (.antigravity, .vscode, .kilocode). Skipping.")

if __name__ == "__main__":
    main()
