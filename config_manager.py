"""
Configuration Manager - Handles loading, saving, and accessing user configurations
"""

import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration schema with validation rules
CONFIG_SCHEMA = {
    "theme": {
        "type": str,
        "default": "default",
        "validate": lambda x: isinstance(x, str) and len(x) > 0,
        "error_msg": "Theme must be a non-empty string"
    },
    "auto_save": {
        "type": bool,
        "default": True,
        "validate": lambda x: isinstance(x, bool),
        "error_msg": "Auto-save must be a boolean value"
    },
    "auto_save_interval": {
        "type": int,
        "default": 30,
        "validate": lambda x: isinstance(x, int) and 5 <= x <= 300,
        "error_msg": "Auto-save interval must be an integer between 5 and 300 seconds"
    },
    "line_numbers": {
        "type": bool,
        "default": True,
        "validate": lambda x: isinstance(x, bool),
        "error_msg": "Line numbers setting must be a boolean value"
    },
    "wrap_lines": {
        "type": bool,
        "default": False,
        "validate": lambda x: isinstance(x, bool),
        "error_msg": "Line wrapping must be a boolean value"
    },
    "tab_size": {
        "type": int,
        "default": 4,
        "validate": lambda x: isinstance(x, int) and 1 <= x <= 8,
        "error_msg": "Tab size must be an integer between 1 and 8"
    },
    "use_spaces": {
        "type": bool,
        "default": True,
        "validate": lambda x: isinstance(x, bool),
        "error_msg": "Use spaces setting must be a boolean value"
    },
    "syntax_check": {
        "type": bool,
        "default": True,
        "validate": lambda x: isinstance(x, bool),
        "error_msg": "Syntax check setting must be a boolean value"
    },
    "show_insights": {
        "type": bool,
        "default": True,
        "validate": lambda x: isinstance(x, bool),
        "error_msg": "Show insights setting must be a boolean value"
    },
    "terminal_height": {
        "type": int,
        "default": 8,
        "validate": lambda x: isinstance(x, int) and 3 <= x <= 30,
        "error_msg": "Terminal height must be an integer between 3 and 30 rows"
    },
    "default_shell": {
        "type": str,
        "default": None,
        "validate": lambda x: x is None or (isinstance(x, str) and len(x) > 0),
        "error_msg": "Default shell must be a non-empty string or None"
    },
    "folding_enabled": {
        "type": bool,
        "default": True,
        "validate": lambda x: isinstance(x, bool),
        "error_msg": "Code folding setting must be a boolean value"
    },
    "max_terminal_history": {
        "type": int,
        "default": 1000,
        "validate": lambda x: isinstance(x, int) and 100 <= x <= 10000,
        "error_msg": "Max terminal history must be an integer between 100 and 10000 lines"
    },
    "key_bindings": {
        "type": dict,
        "default": {},
        "validate": lambda x: isinstance(x, dict),
        "error_msg": "Key bindings must be a dictionary"
    }
}

# Build default config from schema
DEFAULT_CONFIG = {key: schema["default"] for key, schema in CONFIG_SCHEMA.items()}

class ConfigManager:
    """Manages editor configuration"""
    
    def __init__(self, config_path=None):
        """Initialize the configuration manager
        
        Args:
            config_path: Optional path to config file. If None, use default location.
        """
        if config_path is None:
            # Use default location in user home directory
            self.config_path = os.path.join(
                str(Path.home()), 
                ".text_shell_editor", 
                "config.json"
            )
        else:
            self.config_path = config_path
            
        # Initialize with default configuration
        self.config = DEFAULT_CONFIG.copy()
        
        # Try to load from file
        self.load()
    
    def load(self):
        """Load configuration from file"""
        if not os.path.exists(self.config_path):
            logger.info("No configuration file found, using defaults")
            return False
            
        try:
            with open(self.config_path, 'r') as f:
                user_config = json.load(f)
            
            # Validate config format
            if not isinstance(user_config, dict):
                logger.error(f"Invalid configuration format in {self.config_path}, using defaults")
                return False
                
            # Update config with user settings
            self.merge_config(user_config)
            logger.info(f"Configuration loaded from {self.config_path}")
            return True
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {str(e)}")
            logger.error(f"Using default configuration instead")
            return False
        except PermissionError:
            logger.error(f"Permission denied when accessing {self.config_path}")
            return False
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            return False
    
    def save(self):
        """Save current configuration to file"""
        return self.export(self.config_path)
    
    def export(self, path):
        """Export configuration to the specified file
        
        Args:
            path: Path to save the configuration to
            
        Returns:
            True if successful, False otherwise
        """
        # Ensure we have valid data to save
        if not isinstance(self.config, dict):
            logger.error("Invalid configuration data - not saving")
            return False
            
        try:
            # Ensure directory exists
            config_dir = os.path.dirname(path)
            if config_dir:  # Only create if there's a directory component
                try:
                    os.makedirs(config_dir, exist_ok=True)
                except PermissionError:
                    logger.error(f"Permission denied when creating directory {config_dir}")
                    return False
                except OSError as e:
                    logger.error(f"OS error when creating config directory: {str(e)}")
                    return False
            
            # Check if file exists and is writable before attempting write
            if os.path.exists(path) and not os.access(path, os.W_OK):
                logger.error(f"Configuration file exists but is not writable: {path}")
                return False
                
            # Write to a temporary file first, then rename to avoid corruption
            temp_path = f"{path}.tmp"
            with open(temp_path, 'w') as f:
                json.dump(self.config, f, indent=4)
                
            # Rename the temp file to the actual config file
            os.replace(temp_path, path)
            
            logger.info(f"Configuration saved to {path}")
            return True
        except PermissionError:
            logger.error(f"Permission denied when writing to {path}")
            return False
        except IOError as e:
            logger.error(f"I/O error when saving configuration: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            return False
    
    def merge_config(self, user_config):
        """Merge user configuration with defaults
        
        This ensures that new configuration options added in later versions
        are properly initialized with defaults. Also validates configuration
        values according to the schema.
        
        Args:
            user_config: User configuration dictionary
        """
        def merge_dicts(default_dict, user_dict):
            """Recursively merge dictionaries"""
            result = default_dict.copy()
            for k, v in user_dict.items():
                if k in result and isinstance(result[k], dict) and isinstance(v, dict):
                    # Both values are dicts, merge them recursively
                    result[k] = merge_dicts(result[k], v)
                else:
                    # Either key is not in result, or value types don't match
                    # In either case, validate the user value before using it
                    if k in CONFIG_SCHEMA and not self._validate_value(k, v):
                        # Invalid value, use default
                        logger.warning(f"Invalid configuration value for '{k}': {v}. "
                                      f"{CONFIG_SCHEMA[k]['error_msg']}. "
                                      f"Using default: {CONFIG_SCHEMA[k]['default']}")
                        result[k] = CONFIG_SCHEMA[k]['default']
                    else:
                        # Value is valid or not in schema, use as is
                        result[k] = v
            return result
        
        # Merge user config with defaults, validating as we go
        self.config = merge_dicts(self.config, user_config)
        
    def _validate_value(self, key, value):
        """Validate a configuration value against the schema
        
        Args:
            key: The configuration key
            value: The value to validate
            
        Returns:
            True if the value is valid, False otherwise
        """
        if key not in CONFIG_SCHEMA:
            # Key not in schema, can't validate
            return True
        
        # Use the validate function from the schema
        return CONFIG_SCHEMA[key]['validate'](value)
    
    def get(self, key, default=None):
        """Get a configuration value by key
        
        Args:
            key: The configuration key
            default: Default value if key not found
            
        Returns:
            The configuration value or default
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key, value):
        """Set a configuration value
        
        Args:
            key: The configuration key (can use dot notation for nested keys)
            value: The value to set
            
        Returns:
            True if successful, False otherwise
        """
        keys = key.split('.')
        config = self.config
        
        # Validate key format
        if not keys or any(not k for k in keys):
            logger.error(f"Invalid configuration key: {key}")
            return False
            
        # Get the main key (top-level key)
        main_key = keys[0]
            
        # Validate the value if it's a top-level key in our schema
        if len(keys) == 1 and main_key in CONFIG_SCHEMA:
            if not self._validate_value(main_key, value):
                logger.error(f"Invalid value for {main_key}: {value}. {CONFIG_SCHEMA[main_key]['error_msg']}")
                return False
                
        # Capture previous value for change notification
        previous_value = self.get(key)
        
        # Navigate to the parent of the final key
        try:
            for k in keys[:-1]:
                if k not in config or not isinstance(config[k], dict):
                    config[k] = {}
                config = config[k]
            
            # Set the final key
            config[keys[-1]] = value
            
            # Log the change if it's different
            if previous_value != value:
                logger.info(f"Configuration updated: {key} = {value}")
                
            return True
        except Exception as e:
            logger.error(f"Error setting configuration value: {str(e)}")
            return False
    
    def reset_to_defaults(self):
        """Reset configuration to default values"""
        self.config = DEFAULT_CONFIG.copy()
        return self.save()
    
    def get_all(self):
        """Get all configuration values
        
        Returns:
            A copy of the entire configuration dictionary
        """
        return self.config.copy()
        
    def validate_config(self):
        """Validate the entire configuration against the schema
        
        Returns:
            A tuple (is_valid, errors) where is_valid is a boolean indicating if
            the configuration is valid, and errors is a dictionary of error messages
            keyed by the config key.
        """
        errors = {}
        
        # Check each top-level key in the schema
        for key, schema in CONFIG_SCHEMA.items():
            if key in self.config:
                value = self.config[key]
                if not self._validate_value(key, value):
                    errors[key] = f"Invalid value: {value}. {schema['error_msg']}"
        
        # Also look for unknown keys that might be typos
        for key in self.config:
            if key not in CONFIG_SCHEMA:
                # This is not an error, just a warning
                logger.warning(f"Unknown configuration key: {key}")
        
        is_valid = len(errors) == 0
        return is_valid, errors


# Singleton instance
_instance = None

def get_config(config_path=None):
    """Get the configuration manager instance
    
    This function ensures only one instance exists.
    
    Args:
        config_path: Optional path to config file
        
    Returns:
        A ConfigManager instance
    """
    global _instance
    if _instance is None:
        _instance = ConfigManager(config_path)
    return _instance


def load_command_line_config(args):
    """Load configuration from command line arguments
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Updated configuration dictionary
    """
    config = get_config()
    
    # Dictionary mapping arg names to config keys and validation functions
    arg_mappings = {
        'theme': {
            'config_key': 'theme',
            'validate': lambda x: isinstance(x, str) and x,  # Must be non-empty string
            'error_msg': "Theme must be a non-empty string",
            'default': 'default'
        },
        'shell': {
            'config_key': 'default_shell',
            'validate': lambda x: isinstance(x, str) and x in ['bash', 'zsh', 'cmd'],
            'error_msg': "Shell must be one of: bash, zsh, cmd",
            'default': 'bash'
        },
        'auto_save': {
            'config_key': 'auto_save',
            'validate': lambda x: isinstance(x, bool),
            'error_msg': "Auto-save must be a boolean value",
            'default': False
        },
        'auto_save_interval': {
            'config_key': 'auto_save_interval',
            'validate': lambda x: isinstance(x, int) and 5 <= x <= 300,
            'error_msg': "Auto-save interval must be an integer between 5 and 300 seconds",
            'default': 60
        },
        'syntax_check': {
            'config_key': 'syntax_check',
            'validate': lambda x: isinstance(x, bool),
            'error_msg': "Syntax-check must be a boolean value",
            'default': True
        },
        'wrap_lines': {
            'config_key': 'wrap_lines',
            'validate': lambda x: isinstance(x, bool),
            'error_msg': "Wrap-lines must be a boolean value",
            'default': False
        },
        'line_numbers': {
            'config_key': 'line_numbers',
            'validate': lambda x: isinstance(x, bool),
            'error_msg': "Line-numbers must be a boolean value",
            'default': True
        },
        'tab_size': {
            'config_key': 'tab_size',
            'validate': lambda x: isinstance(x, int) and 2 <= x <= 8,
            'error_msg': "Tab size must be an integer between 2 and 8",
            'default': 4
        },
        'use_spaces': {
            'config_key': 'use_spaces',
            'validate': lambda x: isinstance(x, bool),
            'error_msg': "Use-spaces must be a boolean value",
            'default': True
        }
    }
    
    # Process each supported argument
    for arg_name, mapping in arg_mappings.items():
        if hasattr(args, arg_name) and getattr(args, arg_name) is not None:
            value = getattr(args, arg_name)
            
            # Validate the argument value
            if mapping['validate'](value):
                logger.debug(f"Setting {mapping['config_key']} to {value} from command line")
                config.set(mapping['config_key'], value)
            else:
                logger.warning(f"{mapping['error_msg']}. Using default: {mapping['default']}")
                config.set(mapping['config_key'], mapping['default'])
    
    # Handle special case for edit-config
    if hasattr(args, 'edit_config') and args.edit_config:
        logger.info("Opening configuration file for editing")
        config_path = config.config_path
        if not os.path.exists(config_path):
            # Create a default config file if it doesn't exist
            config.save()
        
        # The actual editor opening is handled in the main script
        
    return config