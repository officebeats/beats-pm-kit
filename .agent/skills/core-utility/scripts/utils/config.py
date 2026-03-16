"""
Configuration Utilities Module

Provides centralized configuration management for the Beats PM System (v3.1.0).
"""

import os
import json
from typing import Any, Optional, Dict
from pathlib import Path


# Default configuration values
DEFAULT_CONFIG = {
    'system': {
        'version': '3.1.0',
        'name': 'Beats PM System'
    },
    'paths': {
        'root': None,  # Will be auto-detected
        'staging': '0. Incoming/staging',
        'trackers': '5. Trackers',
        'archive': '5. Trackers/archive',
        'meetings': '3. Meetings',
        'people': '4. People',
        'company': '1. Company',
        'products': '2. Products',
        'templates': '.gemini/templates',
        'skills': '.gemini/skills'
    },
    'files': {
        'kernel': 'KERNEL.md',
        'settings': 'SETTINGS.md',
        'readme': 'README.md',
        'action_plan': 'ACTION_PLAN.md',
        'brain_dump': '0. Incoming/BRAIN_DUMP.md',
        'status': 'STATUS.md'
    },
    'directories': {
        'required': [
            '0. Incoming/staging',
            '0. Incoming/archive',
            '1. Company',
            '2. Products',
            '3. Meetings/transcripts',
            '3. Meetings/daily-briefs',
            '4. People',
            '5. Trackers/archive'
        ]
    },
    'templates': {
        'settings': '.gemini/templates/SETTINGS_TEMPLATE.md',
        'bug_report': '.gemini/templates/trackers/bug-report.md',
        'boss_request': '.gemini/templates/trackers/boss-request.md',
        'meeting_notes': '.gemini/templates/meetings/meeting-notes.md',
        'feature_request': '.gemini/templates/docs/feature-request.md',
        'prd': '.gemini/templates/docs/PRD_TEMPLATE.md',
        'product_context': '.gemini/templates/docs/product-context.md',
        '1on1': '.gemini/templates/meetings/1-on-1-notes.md'
    },
    'trackers': {
        'task_master': '5. Trackers/TASK_MASTER.md',
        'bug_tracker': '5. Trackers/BUG_TRACKER.md',
        'boss_requests': '5. Trackers/BOSS_REQUESTS.md',
        'project_tracker': '5. Trackers/PROJECT_TRACKER.md',
        'delegated_tasks': '5. Trackers/DELEGATED_TASKS.md',
        'eng_tasks': '5. Trackers/ENG_TASKS.md',
        'ux_tasks': '5. Trackers/UX_TASKS.md',
        'decision_log': '5. Trackers/DECISION_LOG.md'
    },
    'ai': {
        'default_model': 'gemini-3-flash-preview'
    },
    'extensions': [
        {
            'id': 'pesosz.antigravity-auto-accept',
            'name': 'Antigravity Auto-Accept (Autonomous Execution)',
            'url': None
        }
    ]
}


# Global config cache
_config_cache: Optional[Dict[str, Any]] = None


def get_config_path() -> str:
    """
    Get the path to the configuration file.
    
    Returns:
        Path to config.json
    """
    return '.gemini/config.json'


def load_config() -> Dict[str, Any]:
    """
    Load configuration from file, or create default if not exists.
    
    Returns:
        Configuration dictionary
    """
    global _config_cache
    
    config_path = get_config_path()
    
    if _config_cache is not None:
        return _config_cache
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                _config_cache = json.load(f)
            return _config_cache
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to load config file, using defaults: {e}")
    
    # Create default config
    _config_cache = DEFAULT_CONFIG.copy()
    save_config(_config_cache)
    
    return _config_cache


def save_config(config: Optional[Dict[str, Any]] = None) -> bool:
    """
    Save configuration to file.
    
    Args:
        config: Configuration dictionary (uses current config if None)
    
    Returns:
        True if save was successful, False otherwise
    """
    global _config_cache
    
    if config is None:
        config = _config_cache
    
    if config is None:
        config = DEFAULT_CONFIG.copy()
    
    config_path = get_config_path()
    
    try:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        _config_cache = config
        return True
    except IOError as e:
        print(f"Error: Failed to save config file: {e}")
        return False


def get_config(key_path: str, default: Any = None) -> Any:
    """
    Get a configuration value by key path.
    """
    config = load_config()
    keys = key_path.split('.')
    value = config
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    return value


def set_config(key_path: str, value: Any) -> bool:
    """
    Set a configuration value by key path.
    """
    config = load_config()
    keys = key_path.split('.')
    current = config
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    current[keys[-1]] = value
    return save_config(config)


def get_root_directory() -> str:
    """
    Get the root directory of the Beats PM System.
    """
    root = get_config('paths.root')
    if root is None:
        root = os.getcwd()
        set_config('paths.root', root)
    return root


def get_path(key: str, relative: bool = True) -> str:
    """
    Get a path from configuration.
    """
    path = get_config(f'paths.{key}')
    if path is None:
        return ''
    if relative:
        return path
    return os.path.join(get_root_directory(), path)


def get_default_model() -> str:
    """
    Get the default AI model.
    """
    return get_config('ai.default_model', 'gemini-3-flash-preview')


def set_default_model(model: str) -> bool:
    """
    Set the default AI model.
    """
    return set_config('ai.default_model', model)
