#!/usr/bin/env python3
"""
Dependency Manager for Beats PM Antigravity Kit

Validates and installs required Python dependencies automatically.
Run this before any system scripts that depend on external packages.
"""
import sys
import subprocess
from pathlib import Path

def check_module(module_name, package_name=None):
    """Check if a module is installed."""
    if package_name is None:
        package_name = module_name
    
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False

def install_package(package_name):
    """Install a package using pip."""
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "--break-system-packages", package_name
        ])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("--- 🔍 Validating Dependencies ---")
    
    # Define required dependencies
    dependencies = [
        ("PIL", "Pillow"),
    ]
    
    all_installed = True
    installed = []
    missing = []
    
    for module, package in dependencies:
        if check_module(module, package):
            installed.append(package)
        else:
            missing.append(package)
            all_installed = False
    
    # Report status
    if installed:
        print(f"✅ Installed: {', '.join(installed)}")
    
    if missing:
        print(f"⚠️  Missing: {', '.join(missing)}")
        print(f"\n📦 Installing missing dependencies...")
        
        for package in missing:
            print(f"  Installing {package}...")
            if install_package(package):
                print(f"    ✅ {package} installed successfully")
            else:
                print(f"    ❌ Failed to install {package}")
                print(f"    Please install manually: pip3 install --break-system-packages {package}")
                return False
    
    print("\n✅ All dependencies are ready!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
