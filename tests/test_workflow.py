"""
Comprehensive test suite for Hifadhi workflow
"""

import pytest
from utils.state_management import create_initial_state
from workflows.langgraph_workflow import app
from workflows.workflow_monitor import monitor


class TestWorkflowRouting:
    """Test routing decisions and agent selection"""
    
    def test_candidate_screening_routing(self):
        """Test routing to candidate screening agent"""
        query = "What is the status of application APP00001?"
        state = create_initial_state(query)
        
        final_state = app.invoke(state)
        
        assert "candidate_screening_agent" in final_state.get("conversation_history", "").lower()
        assert final_state.get("final_answer") is not None
    
    def test_payroll_routing(self):
        """Test routing to payroll agent"""
        query = "Show payment history for candidate CAND00001"
        state = create_initial_state(query)
        
        final_state = app.invoke(state)
        
        assert "payroll" in final_state.get("conversation_history", "").lower()
    
    def test_general_help_routing(self):
        """Test routing to general help agent"""
        query = "What documents are needed for onboarding?"
        state = create_initial_state(query)
        
        final_state = app.invoke(state)
        
        assert "general_help" in final_state.get("conversation_history", "").lower()


class TestClarificationFlow:
    """Test clarification and user input flow"""
    
    def test_missing_candidate_id_triggers_clarification(self):
        """Test that missing IDs trigger clarification"""
        query = "What's my application status?"
        state = create_initial_state(query)
        
        # This should trigger ask_user for candidate/application ID
        # In actual implementation, would need to mock user input
        pass  # Implement with mocking


class TestEscalation:
    """Test human escalation scenarios"""
    
    def test_explicit_human_request(self):
        """Test explicit request for human agent"""
        query = "I want to speak to a human"
        state = create_initial_state(query)
        
        final_state = app.invoke(state)
        
        assert final_state.get("requires_human_escalation") == True
    
    def test_iteration_limit_escalation(self):
        """Test auto-escalation after max iterations"""
        # Create state with high iteration count
        state = create_initial_state("Complex query")
        state["n_iteration"] = 5
        
        # Should auto-escalate
        # Test implementation would verify escalation


class TestEndToEnd:
    """End-to-end workflow tests"""
    
    @pytest.mark.parametrize("query,expected_agent", [
        ("Show candidate CAND00001", "candidate_screening"),
        ("Process payment", "payroll"),
        ("Verify KRA PIN", "compliance"),
        ("Hiring metrics", "analytics"),
    ])
    def test_query_to_agent_mapping(self, query, expected_agent):
        """Test various queries map to correct agents"""
        state = create_initial_state(query)
        final_state = app.invoke(state)
        
        assert expected_agent in final_state.get("conversation_history", "").lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
