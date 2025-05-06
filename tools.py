from typing import Dict, Any, List
import json
from datetime import datetime
from tool_env_manager import ToolEnvManager

class Tool:
    def __init__(self, name: str, description: str, parameters: Dict[str, Any], created_at: str = None, last_modified: str = None):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.created_at = created_at or datetime.now().isoformat()
        self.last_modified = last_modified or datetime.now().isoformat()
        self.env_manager = ToolEnvManager()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "created_at": self.created_at,
            "last_modified": self.last_modified
        }

    def update(self, description: str = None, parameters: Dict[str, Any] = None):
        """Update tool properties"""
        if description:
            self.description = description
        if parameters:
            self.parameters = parameters
        self.last_modified = datetime.now().isoformat()

    def get_required_env_vars(self) -> List[str]:
        """Get list of required environment variables for this tool"""
        required_vars = []
        for param in self.parameters.get("properties", {}).values():
            if param.get("type") == "env_var":
                required_vars.append(param.get("env_var_name"))
        return required_vars

    def check_env_vars(self) -> Dict[str, bool]:
        """Check if all required environment variables are available"""
        required_vars = self.get_required_env_vars()
        return {
            var: self.env_manager.is_key_available(var)
            for var in required_vars
        }

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.env_manager = ToolEnvManager()
        self._register_default_tools()
        self._load_tools_from_file()

    def _register_default_tools(self):
        # Example tool for searching the web
        self.register_tool(
            Tool(
                name="search_web",
                description="Search the web for information",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query"
                        },
                        "api_key": {
                            "type": "env_var",
                            "description": "Google Search API Key",
                            "env_var_name": "GOOGLE_API_KEY"
                        }
                    },
                    "required": ["query", "api_key"]
                }
            )
        )

        # Example tool for weather
        self.register_tool(
            Tool(
                name="weather",
                description="Get weather information for a location",
                parameters={
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The location to get weather for"
                        },
                        "api_key": {
                            "type": "env_var",
                            "description": "OpenWeather API Key",
                            "env_var_name": "WEATHER_API_KEY"
                        }
                    },
                    "required": ["location", "api_key"]
                }
            )
        )

    def _load_tools_from_file(self):
        """Load tools from a JSON file"""
        try:
            with open('tools_config.json', 'r') as f:
                tools_data = json.load(f)
                for tool_data in tools_data:
                    tool = Tool(
                        name=tool_data['name'],
                        description=tool_data['description'],
                        parameters=tool_data['parameters'],
                        created_at=tool_data.get('created_at'),
                        last_modified=tool_data.get('last_modified')
                    )
                    self.tools[tool.name] = tool
        except FileNotFoundError:
            # If file doesn't exist, create it with default tools
            self._save_tools_to_file()

    def _save_tools_to_file(self):
        """Save tools to a JSON file"""
        tools_data = [tool.to_dict() for tool in self.tools.values()]
        with open('tools_config.json', 'w') as f:
            json.dump(tools_data, f, indent=2)

    def register_tool(self, tool: Tool):
        """Register a new tool"""
        if tool.name in self.tools:
            raise ValueError(f"Tool with name '{tool.name}' already exists")
        
        # Check if required environment variables are available
        env_check = tool.check_env_vars()
        missing_vars = [var for var, available in env_check.items() if not available]
        
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables for tool '{tool.name}': {', '.join(missing_vars)}"
            )
        
        self.tools[tool.name] = tool
        self._save_tools_to_file()

    def create_tool(self, name: str, description: str, parameters: Dict[str, Any]) -> Tool:
        """Create and register a new tool"""
        tool = Tool(name=name, description=description, parameters=parameters)
        self.register_tool(tool)
        return tool

    def edit_tool(self, name: str, description: str = None, parameters: Dict[str, Any] = None) -> Tool:
        """Edit an existing tool"""
        if name not in self.tools:
            raise ValueError(f"Tool with name '{name}' not found")
        
        tool = self.tools[name]
        original_tool = Tool(
            name=tool.name,
            description=tool.description,
            parameters=tool.parameters,
            created_at=tool.created_at,
            last_modified=tool.last_modified
        )
        
        # If parameters are being updated, check environment variables
        if parameters:
            temp_tool = Tool(name=name, description=description or tool.description, parameters=parameters)
            env_check = temp_tool.check_env_vars()
            missing_vars = [var for var, available in env_check.items() if not available]
            
            if missing_vars:
                raise ValueError(
                    f"Missing required environment variables for tool '{name}': {', '.join(missing_vars)}"
                )
        
        tool.update(description, parameters)
        self._save_tools_to_file()
        
        return {
            "updated_tool": tool,
            "original_tool": original_tool,
            "warning": "Warning: Editing existing tools may affect their functionality. Make sure to test the tool after modification."
        }

    def delete_tool(self, name: str):
        """Delete a tool"""
        if name not in self.tools:
            raise ValueError(f"Tool with name '{name}' not found")
        del self.tools[name]
        self._save_tools_to_file()

    def get_tools(self) -> List[Dict[str, Any]]:
        """Get all registered tools in the format expected by Groq"""
        return [tool.to_dict() for tool in self.tools.values()]

    def get_tool_by_name(self, name: str) -> Tool:
        """Get a specific tool by name"""
        return self.tools.get(name)

    def get_tool_history(self, name: str) -> Dict[str, Any]:
        """Get the creation and modification history of a tool"""
        if name not in self.tools:
            raise ValueError(f"Tool with name '{name}' not found")
        
        tool = self.tools[name]
        return {
            "name": tool.name,
            "created_at": tool.created_at,
            "last_modified": tool.last_modified,
            "current_version": tool.to_dict()
        }

    def get_available_env_vars(self) -> Dict[str, str]:
        """Get all available environment variables for tools"""
        return self.env_manager.get_all_tool_values() 