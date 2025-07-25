"""
Configuration management for Google AI Studio Proxy
Centralized settings with environment variable support
"""

import os
from typing import Dict, Any, List

# Default configuration values
DEFAULT_CONFIG = {
    "tunnel_provider": "Ngrok",
    "ngrok_token": "",
    "model": "gemini-2.5-flash",
    "top_p": 0.9,
    "top_k": 45,
    "enable_jailbreak": True,
    "bypass_level": "strong",
    "enable_ooc_injection": True,
    "enable_markdown_check": True,
    "enable_force_thinking": False,
    "enable_forbidden_words": True,
    "forbidden_words": "possessive,possessiveness,damn,mind body and soul,pang,pangs,butterflies in stomach,butterflies,knot",
    "enable_autoplot": True,
    "autoplot_chance": 15,
    "enable_crazy_mode": True,
    "enable_medieval_mode": False,
    "enable_better_spice": True,
    "spice_chance": 20,
    "custom_ooc_text": "",
    "custom_prefill_text": "",
    "enable_lorebook": False,
    "lorebook_json_content": ""
}

class Config:
    """Configuration manager with environment variable override support"""
    
    def __init__(self):
        self._config = DEFAULT_CONFIG.copy()
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        for key in self._config:
            env_value = os.getenv(f"PROXY_{key.upper()}")
            if env_value is not None:
                # Type conversion based on default value type
                default_type = type(self._config[key])
                if default_type == bool:
                    self._config[key] = env_value.lower() in ('true', '1', 'yes', 'on')
                elif default_type == int:
                    self._config[key] = int(env_value)
                elif default_type == float:
                    self._config[key] = float(env_value)
                else:
                    self._config[key] = env_value
    
    def get(self, key: str, default=None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        if key in self._config:
            self._config[key] = value
    
    def get_forbidden_words_list(self) -> List[str]:
        """Get forbidden words as a list"""
        words_str = self.get("forbidden_words", "")
        return [word.strip() for word in words_str.split(',') if word.strip()]
    
    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary"""
        return self._config.copy()

# Global configuration instance
config = Config()
