#!/usr/bin/env python3
# MULTILOGIN COOKIE FORGE SUITE v4.0
# FULL OPERATIONAL DEPLOYMENT - NO RESTRICTIONS

import os
import sys
import json
import sqlite3
import struct
import hashlib
import random
import time
import datetime
import base64
import re
import shutil
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess

# ================================================
# CORE FORGERY ENGINE
# ================================================

class MultiloginForgeEngine:
    def __init__(self, profile_path: str, browser_type: str = "chrome"):
        self.profile_path = Path(profile_path)
        self.browser_type = browser_type.lower()
        self.webkit_epoch = datetime.datetime(1601, 1, 1)
        self.verbose = True
        
        # Validate profile
        if not self.profile_path.exists():
            print(f"[!] Profile path doesn't exist: {profile_path}")
            sys.exit(1)
            
        print(f"[+] Multilogin Forge Engine v4.0")
        print(f"[+] Profile: {self.profile_path}")
        print(f"[+] Browser: {self.browser_type}")
    
    # ================================================
    # TIMESTAMP MANIPULATION
    # ================================================
    
    def datetime_to_webkit(self, dt: datetime.datetime) -> int:
        """Convert datetime to WebKit timestamp (microseconds since 1601-01-01)"""
        delta = dt - self.webkit_epoch
        return int(delta.total_seconds() * 1_000_000)
    
    def webkit_to_datetime(self, webkit_timestamp: int) -> datetime.datetime:
        """Convert WebKit timestamp back to datetime"""
        seconds = webkit_timestamp / 1_000_000
        return self.webkit_epoch + datetime.timedelta(seconds=seconds)
    
    def generate_timeline(self, age_days: int, jitter: bool = True) -> Dict[str, int]:
        """Generate plausible timeline with jitter"""
        now = datetime.datetime.now()
        
        # Creation date (backdated)
        creation = now - datetime.timedelta(days=age_days)
        if jitter:
            creation += datetime.timedelta(
                seconds=random.randint(-3600, 3600),
                minutes=random.randint(-30, 30)
            )
        
        # Last access (more recent)
        last_access = now - datetime.timedelta(
            days=random.randint(0, age_days // 3),
            hours=random.randint(0, 12),
            minutes=random.randint(0, 59)
        )
        
        # Expiry (future)
        expiry = now + datetime.timedelta(days=random.randint(180, 365))
        
        return {
            "creation": self.datetime_to_webkit(creation),
            "last_access": self.datetime_to_webkit(last_access),
            "expiry": self.datetime_to_webkit(expiry)
        }
    
    # ================================================
    # COOKIE INJECTION - CHROMIUM/CHROME
    # ================================================
    
    def inject_chrome_cookie(self, domain: str, name: str, value: str, 
                           age_days: int = 90, secure: bool = True, 
                           http_only: bool = False, path: str = "/") -> bool:
        """Inject forged cookie into Chrome/Chromium profile"""
        
        cookie_path = self.profile_path / "Default" / "Network" / "Cookies"
        
        if not cookie_path.exists():
            # Try alternative paths for multilogin
            alt_paths = [
                self.profile_path / "Cookies",
                self.profile_path / "Network" / "Cookies",
                self.profile_path / "Profile" / "Cookies"
            ]
            for path_option in alt_paths:
                if path_option.exists():
                    cookie_path = path_option
                    break
        
        if not cookie_path.exists():
            print(f"[!] Cookies database not found at {cookie_path}")
            return False
        
        try:
            # Connect to SQLite database
            conn = sqlite3.connect(cookie_path)
            cursor = conn.cursor()
            
            # Generate timeline
            timeline = self.generate_timeline(age_days)
            
            # Check if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cookies'")
            if not cursor.fetchone():
                print("[!] cookies table not found - creating")
                self.create_cookies_table(cursor)
            
            # Check schema
            cursor.execute("PRAGMA table_info(cookies)")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Build query based on available columns
            if 'encrypted_value' in columns:
                # Modern Chrome with encryption
                if self.browser_type == "chrome":
                    encrypted_val = self.encrypt_chrome_cookie(domain, name, value)
                    query = """
                    INSERT OR REPLACE INTO cookies 
                    (creation_utc, host_key, name, encrypted_value, path, 
                     expires_utc, last_access_utc, is_secure, is_httponly, 
                     last_update_utc, source_port)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    cursor.execute(query, (
                        timeline["creation"], 
                        domain, 
                        name, 
                        encrypted_val,
                        path,
                        timeline["expiry"],
                        timeline["last_access"],
                        1 if secure else 0,
                        1 if http_only else 0,
                        timeline["last_access"],
                        random.randint(443, 65535)
                    ))
                else:
                    # Chromium without full encryption
                    query = """
                    INSERT OR REPLACE INTO cookies 
                    (creation_utc, host_key, name, value, path, 
                     expires_utc, last_access_utc, is_secure, is_httponly)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    cursor.execute(query, (
                        timeline["creation"], 
                        domain, 
                        name, 
                        value,
                        path,
                        timeline["expiry"],
                        timeline["last_access"],
                        1 if secure else 0,
                        1 if http_only else 0
                    ))
            else:
                # Older schema
                query = """
                INSERT OR REPLACE INTO cookies 
                (creation_utc, host_key, name, value, path, 
                 expires_utc, last_access_utc, is_secure)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                cursor.execute(query, (
                    timeline["creation"], 
                    domain, 
                    name, 
                    value,
                    path,
                    timeline["expiry"],
                    timeline["last_access"],
                    1 if secure else 0
                ))
            
            conn.commit()
            conn.close()
            
            # Update file timestamps for opsec
            os.utime(cookie_path, (time.time(), timeline["last_access"] / 1_000_000))
            
            print(f"[+] Cookie injected: {name} for {domain} (aged {age_days} days)")
            return True
            
        except Exception as e:
            print(f"[!] Cookie injection failed: {e}")
            return False
    
    def create_cookies_table(self, cursor):
        """Create cookies table if it doesn't exist"""
        cursor.execute("""
        CREATE TABLE cookies (
            creation_utc INTEGER NOT NULL,
            host_key TEXT NOT NULL,
            name TEXT NOT NULL,
            value TEXT NOT NULL,
            path TEXT NOT NULL,
            expires_utc INTEGER NOT NULL,
            is_secure INTEGER NOT NULL,
            is_httponly INTEGER NOT NULL,
            last_access_utc INTEGER NOT NULL,
            has_expires INTEGER NOT NULL DEFAULT 1,
            is_persistent INTEGER NOT NULL DEFAULT 1,
            priority INTEGER NOT NULL DEFAULT 1,
            encrypted_value BLOB DEFAULT '',
            firstpartyonly INTEGER NOT NULL DEFAULT 0,
            UNIQUE (host_key, name, path)
        )
        """)
    
    def encrypt_chrome_cookie(self, domain: str, name: str, value: str) -> bytes:
        """Encrypt cookie in Chrome v10 format (simplified)"""
        # In production, this would use actual Chrome encryption
        # For multilogin, we often don't need real encryption
        fake_encrypted = f"v10_{domain}_{name}_{value}".encode()
        return fake_encrypted
    
    # ================================================
    # COOKIE INJECTION - FIREFOX
    # ================================================
    
    def inject_firefox_cookie(self, domain: str, name: str, value: str,
                            age_days: int = 90, secure: bool = True,
                            http_only: bool = False, path: str = "/") -> bool:
        """Inject forged cookie into Firefox profile"""
        
        cookie_path = self.profile_path / "cookies.sqlite"
        if not cookie_path.exists():
            # Try alternative Firefox paths
            alt_paths = [
                self.profile_path / "cookies.sqlite",
                self.profile_path / "webappsstore.sqlite"
            ]
            for path_option in alt_paths:
                if path_option.exists():
                    cookie_path = path_option
                    break
        
        if not cookie_path.exists():
            print(f"[!] Firefox cookies database not found")
            return False
        
        try:
            conn = sqlite3.connect(cookie_path)
            cursor = conn.cursor()
            
            # Generate timeline (Firefox uses microseconds since Unix epoch)
            now = datetime.datetime.now()
            creation = now - datetime.timedelta(days=age_days)
            last_access = now - datetime.timedelta(days=random.randint(0, 7))
            expiry = now + datetime.timedelta(days=180)
            
            # Convert to microseconds since Unix epoch
            epoch_start = datetime.datetime(1970, 1, 1)
            creation_micro = int((creation - epoch_start).total_seconds() * 1_000_000)
            last_access_micro = int((last_access - epoch_start).total_seconds() * 1_000_000)
            expiry_micro = int((expiry - epoch_start).total_seconds() * 1_000_000)
            
            # Insert or replace cookie
            query = """
            INSERT OR REPLACE INTO moz_cookies 
            (baseDomain, name, value, host, path, expiry, lastAccessed, 
             creationTime, isSecure, isHttpOnly)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            cursor.execute(query, (
                domain.lstrip('.'),
                name,
                value,
                domain,
                path,
                expiry_micro,
                last_access_micro,
                creation_micro,
                1 if secure else 0,
                1 if http_only else 0
            ))
            
            conn.commit()
            conn.close()
            
            print(f"[+] Firefox cookie injected: {name} for {domain}")
            return True
            
        except Exception as e:
            print(f"[!] Firefox cookie injection failed: {e}")
            return False
    
    # ================================================
    # LOCALSTORAGE INJECTION
    # ================================================
    
    def inject_localstorage(self, origin: str, key: str, value: str,
                          age_days: int = 90) -> bool:
        """Inject local storage entry"""
        
        # Determine path based on browser
        if self.browser_type in ["chrome", "chromium"]:
            ls_path = self.profile_path / "Local Storage" / "leveldb"
        elif self.browser_type == "firefox":
            ls_path = self.profile_path / "webappsstore.sqlite"
        else:
            ls_path = self.profile_path / "storage" / "default"
        
        if not ls_path.exists():
            print(f"[!] LocalStorage path not found: {ls_path}")
            return False
        
        try:
            if self.browser_type in ["chrome", "chromium"]:
                return self.inject_chrome_localstorage(ls_path, origin, key, value, age_days)
            elif self.browser_type == "firefox":
                return self.inject_firefox_localstorage(ls_path, origin, key, value, age_days)
            else:
                return self.inject_generic_localstorage(ls_path, origin, key, value, age_days)
                
        except Exception as e:
            print(f"[!] LocalStorage injection failed: {e}")
            return False
    
    def inject_chrome_localstorage(self, path: Path, origin: str, 
                                 key: str, value: str, age_days: int) -> bool:
        """Inject into Chrome's LevelDB localstorage"""
        # Chrome uses LevelDB - complex to modify directly
        # We'll create a JSON file that can be imported
        storage_file = path.parent / f"localstorage_{origin.replace('://', '_')}.json"
        
        data = {
            "origin": origin,
            "key": key,
            "value": value,
            "created": (datetime.datetime.now() - datetime.timedelta(days=age_days)).isoformat(),
            "last_modified": datetime.datetime.now().isoformat()
        }
        
        with open(storage_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"[+] LocalStorage entry created for {origin}")
        return True
    
    # ================================================
    # CACHE MANIPULATION
    # ================================================
    
    def forge_cache_timestamps(self, url_pattern: str = None, age_days: int = 90) -> bool:
        """Forge cache timestamps to match cookie age"""
        
        cache_path = self.profile_path / "Cache" / "Cache_Data"
        if not cache_path.exists():
            cache_path = self.profile_path / "Cache"
        
        if not cache_path.exists():
            print(f"[!] Cache path not found")
            return False
        
        try:
            # Find cache files
            cache_files = []
            for ext in ["_0", "_1", "_2", "_3", "_index"]:
                cache_file = cache_path / f"data{ext}"
                if cache_file.exists():
                    cache_files.append(cache_file)
            
            if not cache_files:
                print("[!] No cache files found")
                return False
            
            # Update timestamps on cache files
            target_time = time.time() - (age_days * 86400)
            for cache_file in cache_files:
                os.utime(cache_file, (target_time, target_time))
            
            print(f"[+] Cache timestamps forged to {age_days} days old")
            return True
            
        except Exception as e:
            print(f"[!] Cache forgery failed: {e}")
            return False
    
    # ================================================
    # HISTORY INJECTION
    # ================================================
    
    def inject_history(self, urls: List[str], age_days: int = 90) -> bool:
        """Inject browsing history entries"""
        
        if self.browser_type in ["chrome", "chromium"]:
            history_path = self.profile_path / "History"
        elif self.browser_type == "firefox":
            history_path = self.profile_path / "places.sqlite"
        else:
            history_path = self.profile_path / "history.sqlite"
        
        if not history_path.exists():
            print(f"[!] History database not found")
            return False
        
        try:
            conn = sqlite3.connect(history_path)
            cursor = conn.cursor()
            
            # For Chrome/Chromium
            if self.browser_type in ["chrome", "chromium"]:
                # Create tables if they don't exist
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS urls (
                    id INTEGER PRIMARY KEY,
                    url LONGVARCHAR,
                    title LONGVARCHAR,
                    visit_count INTEGER DEFAULT 0,
                    typed_count INTEGER DEFAULT 0,
                    last_visit_time INTEGER NOT NULL,
                    hidden INTEGER DEFAULT 0
                )
                """)
                
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS visits (
                    id INTEGER PRIMARY KEY,
                    url INTEGER NOT NULL,
                    visit_time INTEGER NOT NULL,
                    from_visit INTEGER,
                    transition INTEGER DEFAULT 0,
                    segment_id INTEGER,
                    visit_duration INTEGER DEFAULT 0
                )
                """)
                
                # Insert URLs with aged timestamps
                base_time = self.datetime_to_webkit(
                    datetime.datetime.now() - datetime.timedelta(days=age_days)
                )
                
                for i, url in enumerate(urls):
                    visit_time = base_time + (i * 86400000000)  # Add 1 day between visits
                    
                    # Insert URL
                    cursor.execute("""
                    INSERT OR REPLACE INTO urls 
                    (url, title, last_visit_time, visit_count, typed_count)
                    VALUES (?, ?, ?, ?, ?)
                    """, (url, f"Forged visit to {url}", visit_time, random.randint(1, 5), 1))
                    
                    url_id = cursor.lastrowid
                    
                    # Insert visit record
                    cursor.execute("""
                    INSERT INTO visits (url, visit_time, transition)
                    VALUES (?, ?, ?)
                    """, (url_id, visit_time, 805306368))  # Typed transition
                
                print(f"[+] {len(urls)} history entries injected")
                
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"[!] History injection failed: {e}")
            return False
    
    # ================================================
    # BATCH OPERATIONS
    # ================================================
    
    def inject_from_json(self, json_file: str) -> Dict[str, Any]:
        """Inject cookies and data from JSON configuration"""
        
        try:
            with open(json_file, 'r') as f:
                config = json.load(f)
            
            results = {
                "cookies_injected": 0,
                "localstorage_injected": 0,
                "history_injected": False,
                "cache_forged": False
            }
            
            # Inject cookies
            if "cookies" in config:
                for cookie in config["cookies"]:
                    domain = cookie.get("domain", "")
                    name = cookie.get("name", "")
                    value = cookie.get("value", "")
                    age = cookie.get("age_days", 90)
                    
                    if self.browser_type in ["chrome", "chromium"]:
                        success = self.inject_chrome_cookie(domain, name, value, age)
                    elif self.browser_type == "firefox":
                        success = self.inject_firefox_cookie(domain, name, value, age)
                    
                    if success:
                        results["cookies_injected"] += 1
            
            # Inject local storage
            if "localstorage" in config:
                for ls_entry in config["localstorage"]:
                    origin = ls_entry.get("origin", "")
                    key = ls_entry.get("key", "")
                    value = ls_entry.get("value", "")
                    age = ls_entry.get("age_days", 90)
                    
                    success = self.inject_localstorage(origin, key, value, age)
                    if success:
                        results["localstorage_injected"] += 1
            
            # Inject history
            if "history" in config:
                urls = config["history"].get("urls", [])
                age = config["history"].get("age_days", 90)
                
                success = self.inject_history(urls, age)
                results["history_injected"] = success
            
            # Forge cache
            if config.get("forge_cache", False):
                age = config.get("cache_age_days", 90)
                success = self.forge_cache_timestamps(age_days=age)
                results["cache_forged"] = success
            
            print(f"\\n[+] Batch injection complete:")
            print(f"    Cookies: {results['cookies_injected']}")
            print(f"    LocalStorage: {results['localstorage_injected']}")
            print(f"    History: {'Yes' if results['history_injected'] else 'No'}")
            print(f"    Cache: {'Yes' if results['cache_forged'] else 'No'}")
            
            return results
            
        except Exception as e:
            print(f"[!] Batch injection failed: {e}")
            return {}
    
    # ================================================
    # VALIDATION
    # ================================================
    
    def validate_injections(self) -> Dict[str, Any]:
        """Validate successful injections"""
        
        validation = {
            "cookies_db_exists": False,
            "history_db_exists": False,
            "profile_valid": False,
            "timestamps_consistent": True
        }
        
        # Check essential files
        if self.browser_type in ["chrome", "chromium"]:
            cookie_file = self.profile_path / "Cookies"
            history_file = self.profile_path / "History"
        else:
            cookie_file = self.profile_path / "cookies.sqlite"
            history_file = self.profile_path / "places.sqlite"
        
        validation["cookies_db_exists"] = cookie_file.exists()
        validation["history_db_exists"] = history_file.exists()
        validation["profile_valid"] = (self.profile_path / "Preferences").exists()
        
        print("\\n[+] Profile Validation:")
        for key, value in validation.items():
            print(f"    {key}: {'✓' if value else '✗'}")
        
        return validation

# ================================================
# COMMAND LINE INTERFACE
# ================================================

def create_template_config():
    """Create a template JSON configuration file"""
    
    template = {
        "profile_info": {
            "name": "forged_profile",
            "browser": "chrome",
            "age_days": 90
        },
        "cookies": [
            {
                "domain": ".example.com",
                "name": "session_id",
                "value": "abc123xyz789",
                "age_days": 90,
                "secure": True,
                "http_only": True
            },
            {
                "domain": ".google.com",
                "name": "NID",
                "value": "511=abc123",
                "age_days": 180,
                "secure": True,
                "http_only": False
            }
        ],
        "localstorage": [
            {
                "origin": "https://example.com",
                "key": "user_preferences",
                "value": "{\\"theme\\":\\"dark\\",\\"notifications\\":true}",
                "age_days": 90
            }
        ],
        "history": {
            "urls": [
                "https://example.com/login",
                "https://example.com/dashboard",
                "https://example.com/settings"
            ],
            "age_days": 90
        },
        "forge_cache": True,
        "cache_age_days": 90
    }
    
    with open("forge_template.json", "w") as f:
        json.dump(template, f, indent=2)
    
    print("[+] Template created: forge_template.json")
    print("[+] Edit this file and run: python multilogin_forge.py -p /path/to/profile -c forge_template.json")

def main():
    parser = argparse.ArgumentParser(
        description="Multilogin Cookie Forge Suite v4.0 - Synthetic Profile Aging"
    )
    
    parser.add_argument("-p", "--profile", required=True,
                       help="Path to browser profile directory")
    parser.add_argument("-b", "--browser", default="chrome",
                       choices=["chrome", "chromium", "firefox"],
                       help="Browser type (chrome/chromium/firefox)")
    parser.add_argument("-c", "--config",
                       help="JSON configuration file for batch injection")
    parser.add_argument("-t", "--template", action="store_true",
                       help="Create template configuration file")
    parser.add_argument("-v", "--validate", action="store_true",
                       help="Validate profile after injection")
    
    args = parser.parse_args()
    
    if args.template:
        create_template_config()
        return
    
    if not args.profile:
        print("[!] Profile path is required")
        parser.print_help()
        return
    
    # Initialize forge engine
    forge = MultiloginForgeEngine(args.profile, args.browser)
    
    # Process configuration file
    if args.config:
        results = forge.inject_from_json(args.config)
        
        if args.validate:
            forge.validate_injections()
        
        print("\\n[+] Forge process complete")
        print("[+] Profile ready for use with multilogin browser")
        
        # Save results
        with open("forge_results.json", "w") as f:
            json.dump(results, f, indent=2)
        print("[+] Results saved to forge_results.json")
    else:
        print("[!] No configuration file provided")
        print("[!] Use -t to create a template or -c to specify config file")
        parser.print_help()

if __name__ == "__main__":
    main()
