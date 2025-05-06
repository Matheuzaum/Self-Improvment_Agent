import os
from groq import Groq
from typing import Dict, Any, List
import json
from dotenv import load_dotenv
from memory_manager import MemoryManager
from tools import ToolRegistry, Tool

load_dotenv()

class GroqAgent:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.memory_manager = MemoryManager()
        self.tool_registry = ToolRegistry()
        self.max_iterations = 10

    def _create_system_prompt(self, user_id: str) -> str:
        """Create a system prompt that includes user memories and available tools"""
        memories = self.memory_manager.get_memories(user_id)
        tools = self.tool_registry.get_tools()
        env_vars = self.tool_registry.get_available_env_vars()
        
        prompt = "You are an AI assistant with access to user memories and tools.\n\n"
        
        if memories:
            prompt += "User memories:\n"
            for key, value in memories.items():
                prompt += f"- {key}: {value}\n"
        
        if tools:
            prompt += "\nAvailable tools:\n"
            for tool in tools:
                prompt += f"- {tool['name']}: {tool['description']}\n"
                prompt += f"  Parameters: {json.dumps(tool['parameters'], indent=2)}\n"
                prompt += f"  Created: {tool['created_at']}\n"
                prompt += f"  Last Modified: {tool['last_modified']}\n"
        
        if env_vars:
            prompt += "\nAvailable environment variables for tools:\n"
            for key, value in env_vars.items():
                if value:  # Only show variables that have values
                    prompt += f"- {key}: [Available]\n"
                else:
                    prompt += f"- {key}: [Not configured]\n"
        
        prompt += "\nYou can create new tools or edit existing ones using the following commands:\n"
        prompt += "- To create a new tool: Use the 'create_tool' command with name, description, and parameters\n"
        prompt += "- To edit a tool: Use the 'edit_tool' command with the tool name and new description/parameters\n"
        prompt += "- To delete a tool: Use the 'delete_tool' command with the tool name\n"
        prompt += "- To view tool history: Use the 'get_tool_history' command with the tool name\n"
        prompt += "\nWhen creating or editing tools, you can use environment variables by setting parameter type to 'env_var' and specifying the env_var_name.\n"
        prompt += "Example parameter for using an environment variable:\n"
        prompt += '{\n  "type": "env_var",\n  "description": "API Key for the service",\n  "env_var_name": "SERVICE_API_KEY"\n}'
        
        return prompt

    def _execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute a tool and return its result"""
        tool = self.tool_registry.get_tool_by_name(tool_name)
        if not tool:
            return f"Tool {tool_name} not found"
        
        # Handle tool management commands
        if tool_name == "create_tool":
            try:
                new_tool = self.tool_registry.create_tool(
                    name=parameters["name"],
                    description=parameters["description"],
                    parameters=parameters["parameters"]
                )
                return f"Successfully created tool: {new_tool.to_dict()}"
            except Exception as e:
                return f"Error creating tool: {str(e)}"
        
        elif tool_name == "edit_tool":
            try:
                result = self.tool_registry.edit_tool(
                    name=parameters["name"],
                    description=parameters.get("description"),
                    parameters=parameters.get("parameters")
                )
                return f"Tool edited successfully. {result['warning']}\nOriginal: {result['original_tool'].to_dict()}\nUpdated: {result['updated_tool'].to_dict()}"
            except Exception as e:
                return f"Error editing tool: {str(e)}"
        
        elif tool_name == "delete_tool":
            try:
                self.tool_registry.delete_tool(parameters["name"])
                return f"Successfully deleted tool: {parameters['name']}"
            except Exception as e:
                return f"Error deleting tool: {str(e)}"
        
        elif tool_name == "get_tool_history":
            try:
                history = self.tool_registry.get_tool_history(parameters["name"])
                return f"Tool history: {json.dumps(history, indent=2)}"
            except Exception as e:
                return f"Error getting tool history: {str(e)}"
        
        # Handle regular tools
        elif tool_name == "search_web":
            return f"Searching web for: {parameters['query']}"
        elif tool_name == "calculate":
            return f"Calculating: {parameters['expression']}"
        
        return "Tool execution not implemented"

    def process_message(self, user_id: str, message: str) -> str:
        """Process a user message with thinking and tool usage"""
        system_prompt = self._create_system_prompt(user_id)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
        
        for iteration in range(self.max_iterations):
            # Get AI response
            response = self.client.chat.completions.create(
                messages=messages,
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                tools=self.tool_registry.get_tools()
            )
            
            message = response.choices[0].message
            
            # Check if the AI wants to use a tool
            if hasattr(message, 'tool_calls') and message.tool_calls:
                tool_call = message.tool_calls[0]
                tool_name = tool_call.function.name
                parameters = json.loads(tool_call.function.arguments)
                
                # Execute the tool
                tool_result = self._execute_tool(tool_name, parameters)
                
                # Add tool result to messages
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [tool_call]
                })
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(tool_result)
                })
            else:
                # AI has a final response
                return message.content
        
        return "Maximum iterations reached without a final response"

    def update_user_memory(self, user_id: str, key: str, value: Any):
        """Update user memory with new information"""
        self.memory_manager.update_memory(user_id, key, value)

# Example usage
if __name__ == "__main__":
    agent = GroqAgent()
    user_id = "user123"
    
    # Example of updating user memory
    agent.update_user_memory(user_id, "preferences", "Prefers concise responses")
    
    # Example of processing a message
    response = agent.process_message(user_id, "What's the weather like?")
    print(response) 