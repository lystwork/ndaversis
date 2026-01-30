"""
NDAVERSIS Version History Module

This module stores and manages the version history for the NDAVERSIS project.
It is automatically updated by the main ndaversis.py script.

Each version entry contains:
- version: Semantic version string (e.g., "0.0.63")
- timestamp: When the version was created
- author: Who created the version
- changes: Description of what changed
- goals: Main goals of the version
- diff_data: Detailed file-level changes
"""

import json
import os

VERSION_HISTORY = [
    {
        "version": "1.0.1",
        "timestamp": "2026-01-30 02:08:49",
        "author": "admin",
        "changes": "Test Change",
        "goals": "Test Goals"
    },
    {
        "version": "1.0.1",
        "timestamp": "2026-01-30 02:08:23",
        "author": "admin",
        "changes": "Test Change",
        "goals": "Test Goals"
    },
    {
        "version": "1.0.1",
        "timestamp": "2026-01-30 02:00:53",
        "author": "admin",
        "changes": "Test Change",
        "goals": "Test Goals"
    },
    {
        "version": "1.0.1",
        "timestamp": "2026-01-30 01:58:25",
        "author": "admin",
        "changes": "Test Change",
        "goals": "Test Goals"
    },
    {
        "version": "1.0.1",
        "timestamp": "2026-01-30 01:57:36",
        "author": "admin",
        "changes": "Test Change",
        "goals": "Test Goals"
    },
    {
        "version": "1.0.1",
        "timestamp": "2026-01-30 01:56:28",
        "author": "admin",
        "changes": "Test Change",
        "goals": "Test Goals"
    },
    {
        "version": "1.0.1",
        "timestamp": "2026-01-30 01:56:09",
        "author": "admin",
        "changes": "Test Change",
        "goals": "Test Goals"
    },
    {
        "version": "1.0.1",
        "timestamp": "2026-01-30 01:55:31",
        "author": "admin",
        "changes": "Test Change",
        "goals": "Test Goals"
    },
    {
        "version": "1.0.1",
        "timestamp": "2026-01-30 01:54:32",
        "author": "admin",
        "changes": "Test Change",
        "goals": "Test Goals"
    },
    {
        "version": "1.0.1",
        "timestamp": "2026-01-30 01:54:11",
        "author": "admin",
        "changes": "Test Change",
        "goals": "Test Goals"
    },
    {
        "version": "1.0.1",
        "timestamp": "2026-01-30 01:52:54",
        "author": "admin",
        "changes": "Test Change",
        "goals": "Test Goals"
    },
    {
        "version": "1.0.1",
        "timestamp": "2026-01-30 01:18:05",
        "author": "admin",
        "changes": "Test Change",
        "goals": "Test Goals"
    },
    {
        "version": "1.0.1",
        "timestamp": "2026-01-30 00:45:10",
        "author": "admin",
        "changes": "Test Change",
        "goals": "Test Goals"
    },
    {
        "version": "1.0.1",
        "timestamp": "2026-01-30 00:41:56",
        "author": "admin",
        "changes": "Test Change",
        "goals": "Test Goals"
    }
]
def add_version(version_data):
    """
    Add a new version to the history.
    
    Args:
        version_data (dict): Dictionary containing version information
    """
    global VERSION_HISTORY
    VERSION_HISTORY.insert(0, version_data)
    _save_history()

def get_recent_versions(count=3):
    """
    Get the most recent N versions.
    
    Args:
        count (int): Number of recent versions to retrieve
        
    Returns:
        list: List of version dictionaries
    """
    return VERSION_HISTORY[:count]

def get_all_versions():
    """
    Get all version history.
    
    Returns:
        list: Complete list of all versions
    """
    return VERSION_HISTORY

def _save_history():
    """Save the version history to this file."""
    # Read the current file
    current_file = __file__
    with open(current_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find where VERSION_HISTORY starts
    start_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith('VERSION_HISTORY = '):
            start_idx = i
            break
    
    if start_idx is None:
        return
    
    # Rebuild the file with updated VERSION_HISTORY
    new_lines = lines[:start_idx]
    new_lines.append(f'VERSION_HISTORY = {json.dumps(VERSION_HISTORY, indent=4, ensure_ascii=False)}\n')
    
    # Find the end of the old VERSION_HISTORY
    bracket_count = 0
    found_start = False
    for i in range(start_idx, len(lines)):
        if '[' in lines[i]:
            found_start = True
            bracket_count += lines[i].count('[')
        if found_start:
            bracket_count -= lines[i].count(']')
            if bracket_count == 0:
                # Add remaining lines after VERSION_HISTORY
                new_lines.extend(lines[i+1:])
                break
    
    # Write back
    with open(current_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

def load_history():
    """Load version history (already loaded at module import)."""
    return VERSION_HISTORY
