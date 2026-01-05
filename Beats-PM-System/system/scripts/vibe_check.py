import os
import platform
import subprocess
import shutil

def print_cyan(text): print(f"\033[96m{text}\033[0m")
def print_green(text): print(f"\033[92m{text}\033[0m")
def print_yellow(text): print(f"\033[93m{text}\033[0m")
def print_red(text): print(f"\033[91m{text}\033[0m")

def check_cmd(cmd, name):
    try:
        subprocess.run([cmd, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print_green(f"  [oc] {name}: Installed")
        return True
    except:
        print_red(f"  [x] {name}: Missing")
        return False

def check_extension(ext_id, name):
    try:
        shell = platform.system() == "Windows"
        result = subprocess.run(["antigravity", "--list-extensions"], capture_output=True, text=True, check=True, shell=shell)
        if ext_id in result.stdout:
            print_green(f"  [oc] Ext: {name}: Installed")
            return True
        else:
            print_yellow(f"  [!] Ext: {name}: Not Installed")
            return False
    except:
        print_red(f"  [x] Antigravity CLI: Not Found")
        return False

def main():
    system = platform.system()
    print_cyan(f"--- Antigravity Vibe Check ({system}) ---")

    # 1. Check Toolchain
    print_cyan("\nToolchain:")
    check_cmd("python" if system == "Windows" else "python3", "Python")
    check_cmd("git", "Git")
    check_cmd("gh", "GitHub CLI")
    check_cmd("npm.cmd" if system == "Windows" else "npm", "Node/NPM")

    # 2. Check File Structure
    print_cyan("\nCore Infrastructure:")
    folders = ["0. Incoming/staging", "1. Company", "2. Products", "3. Meetings", "5. Trackers"]
    for f in folders:
        if os.path.exists(f):
            print_green(f"  [oc] /{f}: Found")
        else:
            print_yellow(f"  [!] /{f}: Missing (Run #update)")

    # 3. Check Critical Files
    print_cyan("\nSystem Files:")
    files = ["KERNEL.md", "SETTINGS.md", "README.md"]
    for f in files:
        if os.path.exists(f):
            print_green(f"  [oc] {f}: Found")
        else:
            print_red(f"  [x] {f}: CRITICAL MISSING")

    # 4. Check Extensions
    print_cyan("\nOptional Power-Ups:")
    check_extension("iml1s.antigravity-plus", "Antigravity Plus")
    check_extension("jlcodes.antigravity-cockpit", "Antigravity Cockpit")

    print_cyan("\n--- Check Complete ---")

if __name__ == "__main__":
    main()
