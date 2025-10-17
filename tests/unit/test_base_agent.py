#!/usr/bin/env python3
import unittest
from unittest.mock import MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.agents.base_agent import BaseAgent

class TestAgent(BaseAgent):
    def _prepare_prompt(self, prompt, context):
        return f"Test: {prompt}"
    
    def _process_response(self, response):
        return {"result": response}

class TestBaseAgent(unittest.TestCase):

    def setUp(self):
        mock_services = {
            'model_manager': MagicMock(),
            'knowledge_engine': MagicMock(),
            'state_manager': MagicMock(),
            'tool_registry': MagicMock(),
        }
        # Mock state_manager to return empty state
        mock_services['state_manager'].load_state.return_value = {}
        
        self.agent = TestAgent(agent_id="test_agent", config={}, services=mock_services)

    def test_agent_initialization(self):
        self.assertEqual(self.agent.agent_id, "test_agent")
        self.assertIsNotNone(self.agent.services)
        self.assertIsNotNone(self.agent.logger)

    def test_state_management(self):
        self.agent.update_state('test_key', 'test_value')
        result = self.agent.get_state('test_key')
        self.assertEqual(result, 'test_value')

if __name__ == '__main__':
    unittest.main()
