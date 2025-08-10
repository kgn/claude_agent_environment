#!/usr/bin/env python3

import json
import sys
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
import socket
from packaging import version

def get_current_version():
    """Get the current installed version of claude-agent-environment."""
    try:
        from claude_agent_environment import __version__
        return __version__
    except ImportError:
        # Fallback to reading from __init__.py if import fails
        init_file = Path(__file__).parent / "__init__.py"
        if init_file.exists():
            with open(init_file, 'r') as f:
                for line in f:
                    if line.startswith("__version__"):
                        return line.split("=")[1].strip().strip('"').strip("'")
        return "1.0.0"  # Default fallback

def get_latest_version():
    """Fetch the latest version from GitHub releases."""
    try:
        # Use GitHub API to get latest release
        url = "https://api.github.com/repos/kgn/claude_agent_environment/releases/latest"
        
        # Set a timeout for the request
        with urlopen(url, timeout=2) as response:
            data = json.loads(response.read().decode())
            # Remove 'v' prefix if present (e.g., v1.0.1 -> 1.0.1)
            tag = data.get("tag_name", "")
            return tag.lstrip("v") if tag else None
    except (URLError, HTTPError, socket.timeout, KeyError, json.JSONDecodeError):
        # Silently fail if we can't check the version
        return None

def check_for_update():
    """Check if a newer version is available and return update info."""
    try:
        current = get_current_version()
        latest = get_latest_version()
        
        if latest is None:
            return None
        
        # Use packaging.version for proper version comparison
        current_ver = version.parse(current)
        latest_ver = version.parse(latest)
        
        if latest_ver > current_ver:
            return {
                "current": current,
                "latest": latest,
                "update_available": True
            }
        else:
            return {
                "current": current,
                "latest": latest,
                "update_available": False
            }
    except Exception:
        # Silently fail on any error
        return None

def display_update_notice():
    """Display an update notice if a new version is available."""
    update_info = check_for_update()
    
    if update_info and update_info["update_available"]:
        print(f"🆕 A new version of claude-agent-environment is available!")
        print(f"   Current version: {update_info['current']}")
        print(f"   Latest version: {update_info['latest']}")
        print(f"   Update from: https://github.com/kgn/claude_agent_environment/releases/latest")
        print("-" * 50)