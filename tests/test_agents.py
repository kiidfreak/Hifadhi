"""
Comprehensive Test Suite for Hifadhi Agents
"""

import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.supervisor_agent import supervisor_agent
from agents.candidate_screening_agent import candidate_screening_agent
from agents.payroll_agent import payroll_agent

class TestHifadhiAgents(unittest.TestCase):

    @patch('agents.supervisor_agent.client.chat.completions.create')
    def test_supervisor_routing_payroll(self, mock_create):
        # Mock LLM response for payroll intent
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            "next_agent": "payroll_agent",
            "task": "Check payment status",
            "justification": "User asked about salary"
        })
        mock_response.choices[0].message.tool_calls = None
        mock_create.return_value = mock_response

        state = {
            "user_input": "Has the salary for candidate CAND001 been paid?",
            "conversation_history": "",
            "n_iteration": 0
        }

        result = supervisor_agent(state)
        
        self.assertEqual(result["next_agent"], "payroll_agent")
        self.assertEqual(result["task"], "Check payment status")

    @patch('agents.candidate_screening_agent.run_llm')
    def test_candidate_screening_agent(self, mock_run_llm):
        # Mock LLM response
        mock_run_llm.return_value = "Candidate John Doe has an AI score of 85."
        
        state = {
            "task": "Screen candidate",
            "candidate_id": "CAND001",
            "conversation_history": ""
        }
        
        result = candidate_screening_agent(state)
        
        self.assertIn("Candidate John Doe", result["messages"][0][1])
        self.assertIn("Candidate Screening Agent:", result["conversation_history"])

    @patch('agents.payroll_agent.run_llm')
    def test_payroll_agent(self, mock_run_llm):
        # Mock LLM response
        mock_run_llm.return_value = "Payment of 50,000 KES initiated successfully."
        
        state = {
            "task": "Pay salary",
            "candidate_id": "CAND001",
            "conversation_history": ""
        }
        
        result = payroll_agent(state)
        
        self.assertIn("Payment of 50,000 KES", result["messages"][0][1])

if __name__ == '__main__':
    unittest.main()
