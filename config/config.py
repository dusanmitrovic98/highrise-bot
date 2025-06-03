import json
import logging
import os
from typing import Any, Dict

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

def _load_config() -> Dict[str, Any]:
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def _save_config(cfg: Dict[str, Any]):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=2)

_config = _load_config()

def get(key: str, default=None):
    return _config.get(key, default)

def set(key: str, value: Any):
    _config[key] = value
    _save_config(_config)

def get_section(section: str) -> Dict[str, Any]:
    return _config.get(section, {})

def set_section(section: str, value: Dict[str, Any]):
    _config[section] = value
    _save_config(_config)

# Dynamic class generator for config sections
class _ConfigSection:
    def __init__(self, section: Dict[str, Any]):
        for k, v in section.items():
            if isinstance(v, dict):
                setattr(self, k, _ConfigSection(v))
            else:
                setattr(self, k, v)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        if isinstance(value, dict):
            value = _ConfigSection(value)
        setattr(self, key, value)
        # Optionally, persist changes here if needed

# Exported config classes
config = _ConfigSection(_config)
loggers = _ConfigSection(_config.get('loggers', {}))
messages = _ConfigSection(_config.get('messages', {}))
actions = _ConfigSection(_config.get('actions', {}))
spawn = _ConfigSection(_config.get('spawn', {}))

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
