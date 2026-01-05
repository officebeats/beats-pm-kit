import os
import shutil
import platform
import time
import subprocess
import urllib.request

# Colors (simplified for cross-platform support without extra libs)
def print_cyan(text): print(f"\033[96m{text}\033[0m")
def print_green(text): print(f"\033[92m{text}\033[0m")
def print_yellow(text): print(f"\033[93m{text}\033[0m")
def print_gray(text): print(f"\033[90m{text}\033[0m")

TEMPLATES = [
    {"src": "Beats-PM-System/TEMPLATES/SETTINGS_TEMPLATE.md", "dst": "SETTINGS.md"},
    {"src": "Beats-PM-System/TEMPLATES/bug-report.md", "dst": "5. Trackers/bugs/bugs-master.md"},
    {"src": "Beats-PM-System/TEMPLATES/boss-request.md", "dst": "5. Trackers/critical/boss-requests.md"},
    {"src": "Beats-PM-System/TEMPLATES/meeting-notes.md", "dst": "5. Trackers/critical/escalations.md"},
    {"src": "Beats-PM-System/TEMPLATES/feature-request.md", "dst": "5. Trackers/projects/projects-master.md"}
]

DIRECTORIES = [
    "0. Incoming/staging",
    "0. Incoming/archive",
    "1. Company",
    "2. Products",
    "3. Meetings/transcripts",
    "3. Meetings/daily-briefs",
    "3. Meetings/weekly-digests",
    "4. People",
    "5. Trackers/bugs",
    "5. Trackers/critical",
    "5. Trackers/projects",
    "5. Trackers/archive"
]

EXTENSIONS = [
    {
        "id": "iml1s.antigravity-plus",
        "name": "Antigravity Plus (UI & Feature Enhancements)",
        "url": None
    },
    {
        "id": "jlcodes.antigravity-cockpit",
        "name": "Antigravity Cockpit (Management Dashboard)",
        "url": None
    }
]

def check_extension_installed(ext_id):
    try:
        shell = platform.system() == "Windows"
        result = subprocess.run(["antigravity", "--list-extensions"], capture_output=True, text=True, check=True, shell=shell)
        return ext_id in result.stdout
    except:
        return False

def install_extension_headless(ext_name, ext_url, ext_id):
    shell = platform.system() == "Windows"
    if ext_url:
        filename = ext_url.split("/")[-1]
        print_cyan(f"  [↓] Downloading {ext_name}...")
        try:
            urllib.request.urlretrieve(ext_url, filename)
            print_green(f"  [+] Installing {ext_name}...")
            subprocess.run(["antigravity", "--install-extension", filename], check=True, capture_output=True, shell=shell)
            os.remove(filename)
            print_green(f"  [✓] {ext_name} installed successfully.")
            return True
        except Exception as e:
            print(f"\033[91m  [!] Failed to download/install {ext_name}: {e}\033[0m")
            if os.path.exists(filename): os.remove(filename)
            return False
    else:
        print_green(f"  [+] Installing {ext_name} from Open VSX...")
        try:
            subprocess.run(["antigravity", "--install-extension", ext_id], check=True, capture_output=True, shell=shell)
            print_green(f"  [✓] {ext_name} installed successfully.")
            return True
        except Exception as e:
            print(f"\033[91m  [!] Failed to install {ext_name} from gallery: {e}\033[0m")
            return False

def main():
    system = platform.system()
    print_cyan(f"🧠 Hydrating Antigravity Brain v2.4.0 ({system})...")

    # 1. Create Directories
    for d in DIRECTORIES:
        if not os.path.exists(d):
            os.makedirs(d)
            print_green(f"  [+] Created Directory {d}/")
    
    # 2. Copy Templates
    for t in TEMPLATES:
        src = t["src"]
        dst = t["dst"]
        
        # Ensure target dir exists
        target_dir = os.path.dirname(dst)
        if target_dir and not os.path.exists(target_dir):
            os.makedirs(target_dir)

        if not os.path.exists(dst):
            if os.path.exists(src):
                shutil.copy(src, dst)
                print_green(f"  [+] Created {dst}")
            else:
                print_yellow(f"  [!] Template missing: {src}")
        else:
            print_gray(f"  [skip] {dst} (Exists)")

    print_cyan("\n✅ Brain is ready. Your privacy is secured.")
    print_yellow("Active files are ignored by git. You can now add your real data.")

    # 3. Optional Extensions
    print_cyan("\n🚀 Optional Power-Ups:")
    for ext in EXTENSIONS:
        if not check_extension_installed(ext["id"]):
            response = input(f"  [?] Would you like to install {ext['name']}? (y/n): ").strip().lower()
            if response == 'y':
                install_extension_headless(ext["name"], ext["url"], ext["id"])
        else:
            print_gray(f"  [skip] {ext['name']} (Already installed)")
    
    if system == "Windows":
        time.sleep(3)

if __name__ == "__main__":
    main()
