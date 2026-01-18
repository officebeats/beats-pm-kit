"""
Configuration Utilities Module

Provides centralized configuration management for the Beats PM System.
"""

import json
from typing import Any, Optional, Dict
from pathlib import Path


# Default configuration values
DEFAULT_CONFIG = {
    'system': {
        'version': '4.10.0',
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
        'templates': '.agent/templates',
        'scripts': 'Beats-PM-System/system/scripts',
        'utils': 'Beats-PM-System/system/utils'
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
            '3. Meetings/weekly-digests',
            '4. People',
            '5. Trackers/archive'
        ]
    },
    'templates': {
        'settings': '.agent/templates/SETTINGS_TEMPLATE.md',
        'bug_report': '.agent/templates/trackers/bug-report.md',
        'boss_request': '.agent/templates/trackers/boss-request.md',
        'meeting_notes': '.agent/templates/meetings/meeting-notes.md',
        'feature_request': '.agent/templates/docs/feature-request.md',
        'prd': '.agent/templates/docs/PRD_TEMPLATE.md',
        'product_context': '.agent/templates/docs/product-context.md',
        '1on1': '.agent/templates/meetings/1-on-1-notes.md'
    },
    'trackers': {
        'bugs_master': '5. Trackers/BUG_TRACKER.md',
        'boss_requests': '5. Trackers/BOSS_REQUESTS.md',
        'decision_log': '5. Trackers/DECISION_LOG.md',
        'projects_master': '5. Trackers/PROJECT_TRACKER.md',
        'delegated_tasks': '5. Trackers/DELEGATED_TASKS.md',
        'eng_tasks': '5. Trackers/ENG_TASKS.md',
        'ux_tasks': '5. Trackers/UX_TASKS.md'
    },
    'ai': {
        'default_model': 'gemini-3-flash-preview',
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


def get_config_path() -> Path:
    """Get the path to the configuration file."""
    return Path('Beats-PM-System/system/config.json')


def load_config() -> Dict[str, Any]:
    """Load configuration from file, or create default if not exists."""
    global _config_cache
    
    if _config_cache is not None:
        return _config_cache
    
    config_path = get_config_path()
    
    if config_path.exists():
        try:
            with config_path.open('r', encoding='utf-8') as f:
                _config_cache = json.load(f)
            return _config_cache
        except (json.JSONDecodeError, IOError) as e:
            from .ui import print_warning
            print_warning(f"Failed to load config file, using defaults: {e}")
    
    # Create default config
    _config_cache = DEFAULT_CONFIG.copy()
    save_config(_config_cache)
    
    return _config_cache


def save_config(config: Optional[Dict[str, Any]] = None) -> bool:
    """Save configuration to file."""
    global _config_cache
    
    if config is None:
        config = _config_cache or DEFAULT_CONFIG.copy()
    
    config_path = get_config_path()
    
    try:
        from .filesystem import ensure_file_directory
        ensure_file_directory(str(config_path))
        
        with config_path.open('w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        _config_cache = config
        return True
    except IOError as e:
        from .ui import print_error
        print_error(f"Failed to save config file: {e}")
        return False


def get_config(key_path: str, default: Any = None) -> Any:
    """
    Get a configuration value by key path (e.g., 'paths.root').
    
    Args:
        key_path: Dot-separated path to the config value
        default: Default value if key not found
    
    Returns:
        Configuration value or default
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
    
    Args:
        key_path: Dot-separated path to the config value
        value: Value to set
    
    Returns:
        True if set was successful, False otherwise
    """
    config = load_config()
    
    keys = key_path.split('.')
    current = config
    
    # Navigate to the parent of the target key
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    # Set the value
    current[keys[-1]] = value
    
    return save_config(config)


def get_root_directory() -> str:
    """Get the root directory of the Beats PM System."""
    root = get_config('paths.root')
    
    if root is None:
        # Auto-detect root directory
        root = str(Path.cwd())
        set_config('paths.root', root)
    
    return root


def get_path(key: str, relative: bool = True) -> str:
    """Get a path from configuration."""
    path = get_config(f'paths.{key}')
    
    if path is None:
        from .ui import print_error
        print_error(f"Path not found in config: {key}")
        return ''
    
    if relative:
        return path
    
    return str(Path(get_root_directory()) / path)


def get_tracker_path(tracker_name: str) -> str:
    """
    Get the path to a tracker file.
    
    Args:
        tracker_name: Name of the tracker (e.g., 'bugs_master')
    
    Returns:
        Path to the tracker file
    """
    return get_config(f'trackers.{tracker_name}', '')


def get_template_path(template_name: str) -> str:
    """
    Get the path to a template file.
    
    Args:
        template_name: Name of the template (e.g., 'bug_report')
    
    Returns:
        Path to the template file
    """
    return get_config(f'templates.{template_name}', '')


def get_required_directories() -> list:
    """
    Get the list of required directories.
    
    Returns:
        List of directory paths
    """
    return get_config('directories.required', [])


def get_extensions() -> list:
    """
    Get the list of extensions to install.
    
    Returns:
        List of extension configurations
    """
    return get_config('extensions', [])


def get_default_model() -> str:
    """
    Get the default AI model.
    
    Returns:
        Default model name
    """
    return get_config('ai.default_model', 'gemini-3-flash-preview')


def set_default_model(model: str) -> bool:
    """
    Set the default AI model.
    
    Args:
        model: Model name to set
    
    Returns:
        True if set was successful, False otherwise
    """
    return set_config('ai.default_model', model)


def reset_config() -> bool:
    """
    Reset configuration to defaults.
    
    Returns:
        True if reset was successful, False otherwise
    """
    global _config_cache
    _config_cache = DEFAULT_CONFIG.copy()
    return save_config(_config_cache)


def reload_config() -> Dict[str, Any]:
    """
    Reload configuration from file.
    
    Returns:
        Configuration dictionary
    """
    global _config_cache
    _config_cache = None
    return load_config()
