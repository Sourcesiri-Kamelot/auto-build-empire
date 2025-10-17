#!/usr/bin/env python3
"""
Agent Architecture 3.0: Tool Registry Service (Production)
This service dynamically discovers, loads, and manages all tools available
to agents from the `src/tools/` directory.
"""
import os
import importlib
import logging
from typing import Dict, Callable, Any
from pathlib import Path

# --- Tool Decorator ---
def tool(name: str, description: str):
    """
    A decorator to register a function as a tool. The decorated function
    becomes a tool that agents can call.
    """
    def decorator(func: Callable) -> Callable:
        func.is_tool = True
        func.tool_name = name
        func.description = description
        return func
    return decorator

# --- Tool Registry Class ---
class ToolRegistry:
    """
    Manages all available tools in the enterprise. It dynamically scans the
    `src/tools` directory and loads any function decorated with `@tool`.
    """
    def __init__(self, tools_path="src/tools"):
        self.tools_path = Path(tools_path)
        self._tools: Dict[str, Callable] = {}
        self.logger = logging.getLogger("Services.ToolRegistry")
        self._discover_and_register_tools()

    def _discover_and_register_tools(self):
        """Scans the tools directory and registers all decorated tool functions."""
        self.logger.info(f"Scanning for tools in '{self.tools_path}'...")
        if not self.tools_path.exists():
            self.logger.warning(f"Tools directory not found: '{self.tools_path}'")
            return

        for py_file in self.tools_path.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
                
            module_name = py_file.stem
            module_path = f"src.tools.{module_name}"
            try:
                module = importlib.import_module(module_path)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if callable(attr) and hasattr(attr, "is_tool"):
                        self.register_tool(attr)
            except Exception as e:
                self.logger.error(f"Failed to load tools from '{module_path}': {e}")
        
        self.logger.info(f"Tool discovery complete. {len(self._tools)} tools registered.")

    def register_tool(self, tool_func: Callable):
        """Adds a tool function to the registry."""
        tool_name = tool_func.tool_name
        self.logger.info(f"  -> Registering tool: '{tool_name}'")
        self._tools[tool_name] = tool_func

    def get_tool(self, tool_name: str) -> Callable:
        """Retrieves a tool by its name."""
        tool = self._tools.get(tool_name)
        if not tool:
            self.logger.warning(f"Attempted to access unregistered tool: '{tool_name}'")
        return tool

    def list_tools(self) -> Dict[str, str]:
        """Returns a dictionary of available tools and their descriptions."""
        return {name: func.description for name, func in self._tools.items()}

    def execute_tool(self, tool_name: str, **kwargs: Any) -> Any:
        """Executes a tool with the given arguments."""
        tool_func = self.get_tool(tool_name)
        if not tool_func:
            return {"error": f"Tool '{tool_name}' not found."}
        
        self.logger.info(f"Executing tool '{tool_name}'...")
        try:
            result = tool_func(**kwargs)
            self.logger.info(f"Tool '{tool_name}' executed successfully.")
            return result
        except Exception as e:
            self.logger.error(f"Error executing tool '{tool_name}': {e}", exc_info=True)
            return {"error": str(e)}
