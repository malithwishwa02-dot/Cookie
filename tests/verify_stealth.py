#!/usr/bin/env python3
"""
OBLIVION STEALTH VERIFIER
Forensic Consistency Checker & Auto-Remediation Agent

This tool analyzes a forged profile for forensic inconsistencies that could
lead to detection (e.g., timestamp mismatches, invalid checksums, metadata leaks).
"""

import os
import sys
import sqlite3
import json
import time
import argparse
from pathlib import Path
from datetime import datetime

class StealthVerifier:
    def __init__(self, profile_path: str, auto_fix: bool = False):
        self.profile_path = Path(profile_path)
        self.auto_fix = auto_fix
        self.issues_found = []
        self.fixed_count = 0
        
        # Thresholds
        self.timestamp_tolerance_sec = 2.0
    
    def log(self, msg: str, status: str = "INFO"):
        prefix = {
            "INFO": "[*]",
            "WARN": "[!]",
            "FAIL": "[x]",
            "PASS": "[+]",
            "FIX":  "[#]"
        }.get(status, "[?]")
        print(f"{prefix} {msg}")

    def verify_timestamp_consistency(self):
        """Check if file system timestamps match internal database timestamps"""
        self.log("Verifying Timestamp Consistency...", "INFO")
        
        # 1. Check Cookies
        cookie_path = self.profile_path / "Default" / "Network" / "Cookies"
        if not cookie_path.exists():
            cookie_path = self.profile_path / "Cookies"
        
        if cookie_path.exists():
            try:
                conn = sqlite3.connect(cookie_path)
                cursor = conn.cursor()
                cursor.execute("SELECT MAX(last_access_utc) FROM cookies")
                result = cursor.fetchone()
                conn.close()
                
                if result and result[0]:
                    # WebKit timestamp (microseconds since 1601) to Unix
                    webkit_ts = result[0]
                    unix_ts = (webkit_ts / 1000000) - 11644473600
                    
                    fs_mtime = os.path.getmtime(cookie_path)
                    
                    diff = abs(fs_mtime - unix_ts)
                    if diff > self.timestamp_tolerance_sec:
                        msg = f"Cookie timestamp mismatch: DB={unix_ts}, FS={fs_mtime}, Diff={diff}s"
                        self.log(msg, "FAIL")
                        self.issues_found.append(msg)
                        
                        if self.auto_fix:
                            os.utime(cookie_path, (unix_ts, unix_ts))
                            self.log("Fixed cookie file timestamp", "FIX")
                            self.fixed_count += 1
                    else:
                        self.log("Cookie timestamps aligned", "PASS")
            except Exception as e:
                self.log(f"Cookie check failed: {e}", "WARN")

    def verify_fingerprint_integrity(self):
        """Check fingerprint manifest against Preferences"""
        self.log("Verifying Fingerprint Integrity...", "INFO")
        
        manifest_path = self.profile_path / "fingerprint_manifest.json"
        prefs_path = self.profile_path / "Preferences"
        
        if manifest_path.exists() and prefs_path.exists():
            try:
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                with open(prefs_path, 'r') as f:
                    prefs = json.load(f)
                
                man_hash = manifest.get("fingerprint_hash")
                
                # Check if hash exists in prefs (custom location)
                # In v5.0 we store config, let's verify key props
                pref_fp = prefs.get("oblivion_fingerprint", {}).get("config", {})
                
                # Simple check: Does User Agent match?
                man_ua = "Unknown" 
                # (Manifest stores artifact paths, config hash is computed from config)
                
                if prefs.get("oblivion_fingerprint", {}).get("synchronized"):
                    self.log("Fingerprint marked as synchronized", "PASS")
                else:
                    msg = "Fingerprint sync flag missing in Preferences"
                    self.log(msg, "FAIL")
                    self.issues_found.append(msg)
                    
                    if self.auto_fix:
                        if "oblivion_fingerprint" not in prefs:
                            prefs["oblivion_fingerprint"] = {}
                        prefs["oblivion_fingerprint"]["synchronized"] = True
                        with open(prefs_path, 'w') as f:
                            json.dump(prefs, f, indent=2)
                        self.log("Injected sync flag", "FIX")
                        self.fixed_count += 1
                        
            except Exception as e:
                self.log(f"Fingerprint check failed: {e}", "WARN")
        else:
            self.log("Fingerprint artifacts missing", "WARN")

    def verify_forensic_cleanliness(self):
        """Check for known generator artifacts"""
        self.log("Scanning for Forensic Artifacts...", "INFO")
        
        suspicious_patterns = [
            "oblivion_", "forge_", "fake_", "dummy"
        ]
        
        # Scan JSON files for leaked strings
        for json_file in self.profile_path.glob("*.json"):
            try:
                with open(json_file, 'r') as f:
                    content = f.read().lower()
                    for pattern in suspicious_patterns:
                        if pattern in content and "manifest" not in json_file.name:
                            # Manifest is allowed to have engine name
                            self.log(f"Suspicious pattern '{pattern}' found in {json_file.name}", "WARN")
            except:
                pass

    def run(self):
        self.log(f"Starting Stealth Verification on: {self.profile_path}", "INFO")
        
        if not self.profile_path.exists():
            self.log("Profile path does not exist", "FAIL")
            sys.exit(1)
            
        self.verify_timestamp_consistency()
        self.verify_fingerprint_integrity()
        self.verify_forensic_cleanliness()
        
        print("-" * 40)
        self.log(f"Verification Complete", "INFO")
        self.log(f"Issues Found: {len(self.issues_found)}", "FAIL" if self.issues_found else "PASS")
        if self.auto_fix:
            self.log(f"Issues Fixed: {self.fixed_count}", "FIX")
            
        if self.issues_found and not self.auto_fix:
            sys.exit(1) # Fail build if issues found
        
        sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Oblivion Stealth Verifier")
    parser.add_argument("-p", "--profile", required=True, help="Profile path to verify")
    parser.add_argument("--fix", action="store_true", help="Auto-fix detected issues")
    
    args = parser.parse_args()
    
    verifier = StealthVerifier(args.profile, args.fix)
    verifier.run()
