"""
NDAVERSIS Configuration Module

Stores and manages configuration settings for the NDAVERSIS project.
"""

import json
import os
import pprint

# Configuration dictionary
CONFIG = {'ai_provider': 'gemini', 'api_base': None, 'model': None}

def get_config(key, default=None):
    """Get a configuration value."""
    return CONFIG.get(key, default)

def set_config(key, value):
    """Set a configuration value and persist."""
    CONFIG[key] = value
    _persist_config()

def get_all_config():
    """Get all configuration."""
    return CONFIG.copy()

def update_config(config_dict):
    """Update multiple configuration values."""
    CONFIG.update(config_dict)
    _persist_config()

def _persist_config():
    """Persist configuration to this Python file."""
    current_file = __file__
    with open(current_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find CONFIG = line
    start_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith('CONFIG = '):
            start_idx = i
            break
    
    if start_idx is None:
        return
    
    # Rebuild file with updated CONFIG
    new_lines = lines[:start_idx]
    
    # Use pprint
    formatted_config = pprint.pformat(CONFIG, indent=4, width=120)
    new_lines.append(f'CONFIG = {formatted_config}\n')
    
    # Find end of old CONFIG
    bracket_count = 0
    found_start = False
    for i in range(start_idx, len(lines)):
        line = lines[i]
        bracket_count += line.count('{') - line.count('}')
        if bracket_count == 0 and ('{' in line or found_start):
             new_lines.extend(lines[i+1:])
             break
        if '{' in line:
            found_start = True
    
    with open(current_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
