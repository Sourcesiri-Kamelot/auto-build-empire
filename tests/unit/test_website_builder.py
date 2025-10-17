#!/usr/bin/env python3
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.agents.teams.digital_presence_squad.website_builder import WebsiteBuilder

class TestWebsiteBuilder(unittest.TestCase):

    def setUp(self):
        mock_services = {
            'model_manager': MagicMock(),
            'knowledge_engine': MagicMock(),
            'state_manager': MagicMock(),
            'tool_registry': MagicMock(),
        }
        mock_config = {
            'skills': ['full_stack_development', 'docker_deployment'],
            'tools': ['file_write', 'knowledge_query'],
        }
        
        mock_services['state_manager'].load_state.return_value = {}
        self.agent = WebsiteBuilder(agent_id="test_website_builder", config=mock_config, services=mock_services)

    @patch('src.tools.file_system.write_file', return_value={'success': True})
    def test_process_response_extracts_and_writes_files(self, mock_write_file):
        mock_llm_response = """
        Here is the full-stack application you requested.

        --- FILE: backend/main.py ---
        from fastapi import FastAPI
        app = FastAPI()

        --- FILE: frontend/index.html ---
        <!DOCTYPE html>
        <html><body><h1>Hello</h1></body></html>
        """
        
        self.agent.get_tool = MagicMock(return_value=mock_write_file)
        
        result = self.agent._process_response(mock_llm_response)
        
        # Verify basic structure without exact call count
        self.assertTrue(mock_write_file.called)
        self.assertEqual(result['agent_type'], 'WebsiteBuilder')
        self.assertIn('website_build_', result['task_id'])

    def test_prepare_prompt_includes_skills(self):
        prompt = "Build e-commerce site"
        
        result = self.agent._prepare_prompt(prompt, {})
        
        self.assertIn("full_stack_development", result)
        self.assertIn("docker_deployment", result)
        self.assertIn(prompt, result)

if __name__ == '__main__':
    unittest.main()
