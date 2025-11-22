"""
Real-time workflow monitoring and statistics
"""

import logging
from typing import Dict, Any, List
from collections import Counter
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class WorkflowMonitor:
    """Monitor and track workflow execution statistics"""
    
    def __init__(self):
        self.conversations = []
        self.agent_call_counts = Counter()
        self.total_iterations = 0
        self.escalation_count = 0
        self.clarification_count = 0
    
    def log_conversation(self, initial_state: Dict, final_state: Dict):
        """
        Log a completed conversation for analytics
        
        Args:
            initial_state: Initial conversation state
            final_state: Final conversation state
        """
        conversation_log = {
            "timestamp": datetime.now().isoformat(),
            "user_query": initial_state.get("user_input"),
            "session_id": final_state.get("session_id"),
            "iterations": final_state.get("n_iteration", 0),
            "escalated": final_state.get("requires_human_escalation", False),
            "agents_used": self._extract_agents(final_state.get("conversation_history", "")),
            "final_answer_length": len(final_state.get("final_answer", "")),
            "success": not final_state.get("error_message")
        }
        
        self.conversations.append(conversation_log)
        
        # Update counters
        self.total_iterations += conversation_log["iterations"]
        if conversation_log["escalated"]:
            self.escalation_count += 1
        
        # Count agent usage
        for agent in conversation_log["agents_used"]:
            self.agent_call_counts[agent] += 1
        
        logger.info(f"Logged conversation: {conversation_log['session_id']}")
    
    def _extract_agents(self, history: str) -> List[str]:
        """Extract list of agents from conversation history"""
        agents = []
        agent_markers = [
            "Candidate Screening Agent",
            "Onboarding Agent",
            "Compliance Agent",
            "Payroll Agent",
            "Analytics Agent",
            "General Help Agent",
            "Human Escalation Agent"
        ]
        
        for marker in agent_markers:
            if marker in history:
                agent_name = marker.lower().replace(" ", "_")
                agents.append(agent_name)
        
        return list(set(agents))  # Remove duplicates
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive workflow statistics
        
        Returns:
            Dictionary with statistics
        """
        total_conversations = len(self.conversations)
        
        if total_conversations == 0:
            return {"message": "No conversations logged yet"}
        
        successful = sum(1 for c in self.conversations if c["success"])
        avg_iterations = self.total_iterations / total_conversations
        
        stats = {
            "total_conversations": total_conversations,
            "successful_conversations": successful,
            "success_rate": round(successful / total_conversations * 100, 2),
            "average_iterations": round(avg_iterations, 2),
            "escalation_rate": round(self.escalation_count / total_conversations * 100, 2),
            "most_used_agents": dict(self.agent_call_counts.most_common(5)),
            "average_response_length": round(
                sum(c["final_answer_length"] for c in self.conversations) / total_conversations, 0
            )
        }
        
        return stats
    
    def print_dashboard(self):
        """Print formatted statistics dashboard"""
        stats = self.get_statistics()
        
        if "message" in stats:
            print(stats["message"])
            return
        
        print("\n" + "="*70)
        print("HIFADHI WORKFLOW STATISTICS DASHBOARD")
        print("="*70)
        
        print(f"\n📊 Overall Metrics:")
        print(f"  Total Conversations: {stats['total_conversations']}")
        print(f"  Success Rate: {stats['success_rate']}%")
        print(f"  Average Iterations: {stats['average_iterations']}")
        print(f"  Escalation Rate: {stats['escalation_rate']}%")
        print(f"  Avg Response Length: {stats['average_response_length']} chars")
        
        print(f"\n🤖 Most Used Agents:")
        for agent, count in stats['most_used_agents'].items():
            print(f"  {agent}: {count} calls")
        
        print("="*70 + "\n")
    
    def export_logs(self, filepath: str = "logs/conversation_logs.json"):
        """
        Export conversation logs to JSON file
        
        Args:
            filepath: Path to save logs
        """
        with open(filepath, "w") as f:
            json.dump({
                "statistics": self.get_statistics(),
                "conversations": self.conversations
            }, f, indent=2)
        
        print(f"✅ Logs exported to {filepath}")


# Global monitor instance
monitor = WorkflowMonitor()
