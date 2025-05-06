import os
from typing import Dict, Any, List
from dotenv import load_dotenv

class ToolEnvManager:
    def __init__(self):
        # Load both .env and tool_keys.env
        load_dotenv()
        load_dotenv('tool_keys.env')
        self.tool_keys = self._load_tool_keys()

    def _load_tool_keys(self) -> Dict[str, str]:
        """Load tool keys from tool_keys.env"""
        tool_keys = {}
        with open('tool_keys.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    tool_keys[key.strip()] = value.strip()
        return tool_keys

    def get_tool_key(self, key: str) -> str:
        """Get the actual environment variable name for a tool key"""
        return self.tool_keys.get(key)

    def get_tool_value(self, key: str) -> str:
        """Get the actual value of an environment variable for a tool"""
        env_key = self.get_tool_key(key)
        if env_key:
            return os.getenv(env_key)
        return None

    def get_available_keys(self) -> List[str]:
        """Get list of available tool keys"""
        return list(self.tool_keys.keys())

    def get_all_tool_values(self) -> Dict[str, str]:
        """Get all tool keys and their corresponding environment variable values"""
        return {
            key: self.get_tool_value(key)
            for key in self.tool_keys.keys()
        }

    def is_key_available(self, key: str) -> bool:
        """Check if a tool key is available and has a value"""
        return bool(self.get_tool_value(key))

    def get_tool_config(self, tool_name: str) -> Dict[str, Any]:
        """Get configuration for a specific tool based on its name"""
        config = {}
        for key, value in self.tool_keys.items():
            if key.startswith(tool_name.upper()):
                config[key] = self.get_tool_value(key)
        return config 