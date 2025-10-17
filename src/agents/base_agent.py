#!/usr/bin/env python3
"""
BaseAgent Framework - Agent Architecture 3.0
The foundational class for all agents in the Autonomous Enterprise Builder.
Every agent inherits from this class for unified capabilities.
"""
import json
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

class MockStateManager:
    """Temporary mock for Step 1 - will be replaced with SQLite in Step 2"""
    def __init__(self, state_dir):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
    
    def save_state(self, agent_id, state):
        state_file = self.state_dir / f"{agent_id}.json"
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2, default=str)
    
    def load_state(self, agent_id):
        state_file = self.state_dir / f"{agent_id}.json"
        if state_file.exists():
            with open(state_file, 'r') as f:
                return json.load(f)
        return {}

class MockToolRegistry:
    """Temporary mock for Step 1 - will be replaced with real registry in Step 2"""
    def __init__(self):
        self.tools = {
            'file_system': self._file_system_tool,
            'code_linter': self._code_linter_tool,
            'knowledge_base': self._knowledge_base_tool
        }
    
    def get_tool(self, tool_name):
        return self.tools.get(tool_name)
    
    def _file_system_tool(self, action, path, content=None):
        """Mock file system operations"""
        return f"FileSystem: {action} on {path}"
    
    def _code_linter_tool(self, code, language):
        """Mock code linting"""
        return f"CodeLinter: Analyzed {language} code ({len(code)} chars)"
    
    def _knowledge_base_tool(self, query):
        """Mock knowledge base query"""
        return f"KnowledgeBase: Query '{query}' executed"

class BaseAgent(ABC):
    """
    The foundational class for all agents in the Autonomous Enterprise Builder.
    Provides unified structure for state, tools, communication, and execution.
    """
    
    def __init__(self, agent_id, config, services):
        self.agent_id = agent_id
        self.config = config
        self.services = services
        
        # Initialize state management
        self.state_manager = services.get('state_manager') or MockStateManager("./data/agent_states")
        self.state = self.state_manager.load_state(agent_id)
        
        # Initialize tool registry
        self.tool_registry = services.get('tool_registry')
        
        # Core services
        self.model_manager = services.get('model_manager')
        self.knowledge_engine = services.get('knowledge_engine')
        
        # Logging
        self.logger = logging.getLogger(f"Agent.{self.agent_id}")
        self.logger.info(f"Agent {self.agent_id} initialized with skills: {config.get('skills', [])}")
        
        # Performance tracking
        self.task_count = 0
        self.last_activity = datetime.now()
    
    def get_tool(self, tool_name):
        """Securely retrieves a tool from the registry."""
        authorized_tools = self.config.get('tools', [])
        if tool_name in authorized_tools:
            tool = self.tool_registry.get_tool(tool_name)
            if tool:
                self.logger.debug(f"Retrieved tool: {tool_name}")
                return tool
            else:
                self.logger.error(f"Tool not found in registry: {tool_name}")
                return None
        else:
            self.logger.warning(f"Unauthorized tool access attempt: {tool_name}")
            return None
    
    def update_state(self, key, value):
        """Updates agent state and persists it"""
        self.state[key] = value
        self.state['last_updated'] = datetime.now().isoformat()
        self.state_manager.save_state(self.agent_id, self.state)
        self.logger.debug(f"State updated: {key} = {value}")
    
    def get_state(self, key, default=None):
        """Retrieves value from agent state"""
        return self.state.get(key, default)
    
    async def run(self):
        """Main async lifecycle method for enterprise-scale execution"""
        from ..core.task_queue_redis import claim_and_process_task
        await claim_and_process_task(
            self.agent_id, 
            self.config.get('skills', []), 
            self.execute_task_async
        )
    
    async def execute_task_async(self, task_data):
        """Async version of execute_task for Redis Streams"""
        prompt = task_data.get('prompt', '')
        context = task_data.get('context', {})
        
        self.logger.info(f"Executing async task: {prompt[:100]}...")
        self.task_count += 1
        self.last_activity = datetime.now()
        
        try:
            self.update_state_fast('task_status', 'executing')
            
            full_prompt = self._prepare_prompt(prompt, context)
            
            # Async model execution
            if self.model_manager:
                response = await self.model_manager.generate_async(full_prompt)
            else:
                response = f"Mock response for: {prompt}"
            
            result = self._process_response(response)
            
            self.update_state_fast('task_status', 'completed')
            self.update_state('last_result', result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            self.update_state_fast('task_status', 'failed')
            raise
    
    def update_state_fast(self, key, value):
        """Fast Redis-based state update for high-frequency changes"""
        import redis
        import os
        redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            decode_responses=True
        )
        redis_client.hset(f"agent_state:{self.agent_id}", key, value)
        redis_client.hset(f"agent_state:{self.agent_id}", "last_updated", datetime.now().isoformat())
    
    def execute_task(self, prompt, context=None):
        """
        Main entry point for agent task execution.
        This is the unified interface all agents use.
        """
        self.logger.info(f"Executing task: {prompt[:100]}...")
        self.task_count += 1
        self.last_activity = datetime.now()
        
        try:
            # Update state to track current task
            self.update_state('current_task', prompt[:200])
            self.update_state('task_status', 'executing')
            self.update_state('task_count', self.task_count)
            
            # 1. Prepare the full prompt with context and agent state
            full_prompt = self._prepare_prompt(prompt, context)
            
            # 2. Select the best model for the task
            model_preference = self.config.get('model_preference', 'default')
            if self.model_manager:
                model = self.model_manager.get_model(model_preference)
            else:
                # Mock model for Step 1
                model = MockModel()
            
            # 3. Generate the response
            self.logger.debug(f"Using model preference: {model_preference}")
            response = model.generate(full_prompt)
            
            # 4. Process the response and update state
            result = self._process_response(response)
            
            # 5. Update completion state
            self.update_state('task_status', 'completed')
            self.update_state('last_result', str(result)[:500])  # Truncate for storage
            
            self.logger.info(f"Task completed successfully. Result type: {type(result).__name__}")
            return result
            
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}", exc_info=True)
            self.update_state('task_status', 'failed')
            self.update_state('last_error', str(e))
            return {"error": f"Agent {self.agent_id} failed: {str(e)}"}
    
    def get_agent_status(self):
        """Returns current agent status for monitoring"""
        return {
            'agent_id': self.agent_id,
            'skills': self.config.get('skills', []),
            'task_count': self.task_count,
            'last_activity': self.last_activity.isoformat(),
            'current_status': self.get_state('task_status', 'idle'),
            'current_task': self.get_state('current_task', 'None')
        }
    
    @abstractmethod
    def _prepare_prompt(self, prompt, context):
        """
        Each agent must implement its own logic for prompt construction.
        This is where agent specialization happens.
        """
        pass
    
    @abstractmethod
    def _process_response(self, response):
        """
        Each agent must implement its own logic for parsing the model's response.
        This is where agent output formatting happens.
        """
        pass

class MockModel:
    """Temporary mock model for Step 1 testing"""
    def generate(self, prompt):
        return f"Mock response to: {prompt[:50]}..."

# Agent Skills Registry - will be moved to separate service in Step 2
AGENT_SKILLS = {
    'backend_development': ['python', 'fastapi', 'sqlalchemy', 'api_design'],
    'frontend_development': ['react', 'javascript', 'tailwind_css', 'html'],
    'database_design': ['postgresql', 'schema_design', 'optimization'],
    'financial_analysis': ['financial_modeling', 'rag_query', 'reporting']
}
