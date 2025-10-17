#!/usr/bin/env python3
import unittest
from unittest.mock import MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.agents.teams.finance_squad.finance_agent import FinanceAgent

class TestConfigDriven(unittest.TestCase):

    def test_agent_behavior_changes_with_config(self):
        """Test that agent behavior adapts based on configuration"""
        
        # Basic config
        basic_config = {
            'skills': ['financial_analysis'],
            'tools': ['financial_calculator']
        }
        
        # Advanced config  
        advanced_config = {
            'skills': ['financial_analysis', 'investment_strategy', 'risk_management'],
            'tools': ['financial_calculator', 'market_data']
        }
        
        mock_services = {
            'model_manager': MagicMock(),
            'knowledge_engine': MagicMock(),
            'state_manager': MagicMock(),
            'tool_registry': MagicMock(),
        }
        mock_services['state_manager'].load_state.return_value = {}
        
        basic_agent = FinanceAgent("basic", basic_config, mock_services)
        advanced_agent = FinanceAgent("advanced", advanced_config, mock_services)
        
        prompt = "Analyze investment opportunity"
        
        basic_result = basic_agent._prepare_prompt(prompt, {})
        advanced_result = advanced_agent._prepare_prompt(prompt, {})
        
        # Verify different behaviors based on config
        self.assertIn("financial_analysis", basic_result)
        self.assertIn("financial_analysis", advanced_result)
        self.assertNotIn("investment_strategy", basic_result)
        self.assertIn("investment_strategy", advanced_result)
        self.assertIn(prompt, basic_result)
        self.assertIn(prompt, advanced_result)

if __name__ == '__main__':
    unittest.main()
