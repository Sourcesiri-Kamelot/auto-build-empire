#!/usr/bin/env python3
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.agents.teams.development_squad.backend_developer import BackendDeveloper

class TestBackendDeveloper(unittest.TestCase):

    def setUp(self):
        mock_services = {
            'model_manager': MagicMock(),
            'knowledge_engine': MagicMock(),
            'state_manager': MagicMock(),
            'tool_registry': MagicMock(),
        }
        mock_config = {
            'skills': ['python', 'fastapi'],
            'preferred_frameworks': ['FastAPI'],
        }
        
        # Mock the state_manager to return empty state
        mock_services['state_manager'].load_state.return_value = {}
        
        self.agent = BackendDeveloper(agent_id="test_backend_dev", config=mock_config, services=mock_services)

    def test_prepare_prompt_includes_context(self):
        prompt = "Create API endpoint"
        context = {"database": "postgresql"}
        
        result = self.agent._prepare_prompt(prompt, context)
        
        self.assertIn(prompt, result)
        self.assertIn("postgresql", result)
        self.assertIn("Backend Developer Agent", result)

    def test_prepare_prompt_includes_skills(self):
        prompt = "Build service"
        
        result = self.agent._prepare_prompt(prompt, {})
        
        self.assertIn("python", result)
        self.assertIn("FastAPI", result)

if __name__ == '__main__':
    unittest.main()
