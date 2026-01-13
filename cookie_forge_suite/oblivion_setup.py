#!/usr/bin/env python3
"""
OBLIVION FORGE NEXUS v5.0 - Installation and Setup Script
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Check Python version compatibility"""
    required = (3, 8)
    current = sys.version_info[:2]
    
    if current < required:
        print(f"[!] Python {required[0]}.{required[1]}+ required, found {current[0]}.{current[1]}")
        return False
    
    print(f"[+] Python version: {sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\\n[+] Installing dependencies...")
    
    # Determine platform-specific packages
    system = platform.system()
    extra_packages = []
    
    if system == "Windows":
        extra_packages = ["pywin32"]
    elif system == "Darwin":
        extra_packages = []
    elif system == "Linux":
        extra_packages = []
    
    # Install from requirements.txt
    try:
        # Create requirements.txt if it doesn't exist
        req_file = Path("requirements.txt")
        if not req_file.exists():
            print("[!] requirements.txt not found, creating default...")
            default_reqs = """# Core dependencies
python>=3.8
pycryptodome>=3.19.0
cryptography>=41.0.0
requests>=2.31.0
websocket-client>=1.6.0
plyvel>=1.5.0
chromedriver-autoinstaller>=0.6.0
selenium>=4.15.0
"""
            req_file.write_text(default_reqs)
        
        # Install packages
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        # Install platform-specific packages
        for package in extra_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"[+] Installed platform package: {package}")
            except:
                print(f"[!] Failed to install {package}, continuing...")
        
        print("[+] Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"[!] Failed to install dependencies: {e}")
        return False
    except Exception as e:
        print(f"[!] Installation error: {e}")
        return False

def setup_directories():
    """Create necessary directories"""
    print("\\n[+] Setting up directories...")
    
    directories = [
        "profiles",
        "configs",
        "logs",
        "exports",
        "templates"
    ]
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  [+] Created: {dir_name}")
    
    return True

def create_config_templates():
    """Create configuration templates"""
    print("\\n[+] Creating configuration templates...")
    
    templates = {
        "basic_template.json": {
            "description": "Basic profile configuration",
            "age_days": 90,
            "cookies": [],
            "forge_cache": True
        },
        "enterprise_template.json": {
            "description": "Enterprise-grade profile",
            "age_days": 365,
            "fingerprint_sync": True,
            "forensic_opsec": True
        },
        "stealth_template.json": {
            "description": "Maximum stealth configuration",
            "age_days": 730,
            "hybrid_injection": True,
            "advanced_fingerprint": True
        }
    }
    
    for filename, content in templates.items():
        import json
        filepath = Path("templates") / filename
        with open(filepath, 'w') as f:
            json.dump(content, f, indent=2)
        print(f"  [+] Created: {filename}")
    
    return True

def verify_installation():
    """Verify installation success"""
    print("\\n[+] Verifying installation...")
    
    checks = [
        ("Python version", lambda: sys.version_info >= (3, 8)),
        ("requirements.txt", lambda: Path("requirements.txt").exists()),
        ("oblivion_core.py", lambda: Path("oblivion_core.py").exists()),
        ("oblivion_importer.py", lambda: Path("oblivion_importer.py").exists()),
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        try:
            if check_func():
                print(f"  ✓ {check_name}")
            else:
                print(f"  ✗ {check_name}")
                all_passed = False
        except:
            print(f"  ✗ {check_name} (error)")
            all_passed = False
    
    return all_passed

def main():
    """Main installation routine"""
    print("=" * 60)
    print("OBLIVION FORGE NEXUS v5.0 - Installation")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("[!] Dependency installation failed")
        response = input("[?] Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Setup directories
    if not setup_directories():
        print("[!] Directory setup failed")
        sys.exit(1)
    
    # Create templates
    if not create_config_templates():
        print("[!] Template creation failed")
        # Non-fatal
    
    # Verify
    if not verify_installation():
        print("\\n[!] Installation verification failed")
        response = input("[?] Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    print("\\n" + "=" * 60)
    print("[+] INSTALLATION COMPLETE")
    print("=" * 60)
    print("\\nQuick start:")
    print("  1. Create a template: python oblivion_core.py --template")
    print("  2. Edit templates/enterprise_template.json")
    print("  3. Forge a profile: python oblivion_core.py --profile /path/to/profile --config templates/enterprise_template.json")
    print("  4. Import to anti-detect browser: python oblivion_importer.py --software multilogin --import /path/to/forged_profile")
    print("\\nDocumentation:")
    print("  See README.md for detailed usage instructions")
    print("=" * 60)

if __name__ == "__main__":
    main()
