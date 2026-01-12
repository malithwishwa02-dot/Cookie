#!/usr/bin/env python3
# MULTILOGIN PROFILE IMPORTER
# Import forged profiles into Multilogin/Anti-detect browsers

import os
import sys
import json
import shutil
import sqlite3
import zipfile
import argparse
from pathlib import Path
from datetime import datetime
import xml.etree.ElementTree as ET

class MultiloginImporter:
    def __init__(self, multilogin_path: str = None):
        # Auto-detect Multilogin paths
        self.multilogin_paths = [
            os.path.expanduser("~/AppData/Local/Multilogin"),
            os.path.expanduser("~/Library/Application Support/Multilogin"),
            os.path.expanduser("~/.multilogin"),
            "C:/Program Files/Multilogin",
            "/opt/multilogin"
        ]
        
        if multilogin_path:
            self.multilogin_paths.insert(0, multilogin_path)
        
        self.profiles_path = None
        self.find_multilogin_path()
    
    def find_multilogin_path(self):
        """Find Multilogin installation path"""
        for path in self.multilogin_paths:
            test_path = Path(path)
            if test_path.exists():
                print(f"[+] Found Multilogin at: {path}")
                self.profiles_path = test_path / "profiles"
                if not self.profiles_path.exists():
                    self.profiles_path.mkdir(parents=True, exist_ok=True)
                return True
        
        print("[!] Multilogin not found in standard locations")
        return False
    
    def import_profile(self, source_path: str, profile_name: str = None):
        """Import forged profile into Multilogin"""
        
        source = Path(source_path)
        if not source.exists():
            print(f"[!] Source profile not found: {source_path}")
            return False
        
        # Generate profile name if not provided
        if not profile_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            profile_name = f"forged_profile_{timestamp}"
        
        # Create profile directory in Multilogin
        profile_dir = self.profiles_path / profile_name
        profile_dir.mkdir(exist_ok=True)
        
        try:
            # Copy profile contents
            print(f"[+] Importing profile: {profile_name}")
            
            if source.is_file() and source.suffix == '.zip':
                # Extract zip file
                with zipfile.ZipFile(source, 'r') as zip_ref:
                    zip_ref.extractall(profile_dir)
            else:
                # Copy directory
                shutil.copytree(source, profile_dir, dirs_exist_ok=True)
            
            # Create Multilogin metadata
            self.create_metadata(profile_dir, profile_name)
            
            print(f"[+] Profile imported successfully: {profile_dir}")
            return True
            
        except Exception as e:
            print(f"[!] Import failed: {e}")
            return False
    
    def create_metadata(self, profile_dir: Path, profile_name: str):
        """Create Multilogin metadata files"""
        
        # Create profile.json
        profile_data = {
            "name": profile_name,
            "notes": "Forged profile with synthetic aging",
            "created": datetime.now().isoformat(),
            "browser": "mimic",
            "os": "windows",
            "navigator": {
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "platform": "Win32",
                "language": "en-US"
            },
            "canvas": {
                "mode": "noise"
            },
            "webgl": {
                "mode": "noise"
            },
            "timezone": {
                "mode": "real"
            },
            "location": {
                "mode": "real"
            },
            "proxy": {
                "mode": "none"
            },
            "extensions": [],
            "cookies": "imported",
            "storage": "imported"
        }
        
        meta_file = profile_dir / "profile.json"
        with open(meta_file, 'w') as f:
            json.dump(profile_data, f, indent=2)
        
        print(f"[+] Metadata created: {meta_file}")
    
    def list_profiles(self):
        """List all imported profiles"""
        if not self.profiles_path.exists():
            print("[!] No profiles directory found")
            return []
        
        profiles = []
        for item in self.profiles_path.iterdir():
            if item.is_dir():
                profile_json = item / "profile.json"
                if profile_json.exists():
                    with open(profile_json, 'r') as f:
                        data = json.load(f)
                    profiles.append({
                        "name": data.get("name", item.name),
                        "path": str(item),
                        "created": data.get("created", "")
                    })
        
        print(f"\\n[+] Found {len(profiles)} profiles:")
        for profile in profiles:
            print(f"    • {profile['name']} ({profile['created']})")
        
        return profiles

def main():
    parser = argparse.ArgumentParser(
        description="Multilogin Profile Importer - Import forged profiles"
    )
    
    parser.add_argument("-i", "--import", dest="import_path",
                       help="Path to forged profile to import")
    parser.add_argument("-n", "--name",
                       help="Profile name (default: auto-generated)")
    parser.add_argument("-l", "--list", action="store_true",
                       help="List all imported profiles")
    parser.add_argument("-p", "--path",
                       help="Custom Multilogin installation path")
    
    args = parser.parse_args()
    
    # Initialize importer
    importer = MultiloginImporter(args.path)
    
    if args.list:
        importer.list_profiles()
    elif args.import_path:
        importer.import_profile(args.import_path, args.name)
    else:
        print("[!] No action specified")
        parser.print_help()

if __name__ == "__main__":
    main()
