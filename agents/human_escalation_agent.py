"""
Human Escalation Agent - Gracefully hands off complex cases to human HR team
"""

import logging
from typing import Dict, Any
from utils.llm_client import client
from utils.tracing import trace_agent
from prompts.agent_prompts import HUMAN_ESCALATION_PROMPT

logger = logging.getLogger(__name__)


@trace_agent
def human_escalation_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handles escalation to human HR specialists
    
    Args:
        state: Conversation state requiring human intervention
        
    Returns:
        Final state with escalation confirmation
    """
    print("---HUMAN ESCALATION AGENT---")
    logger.warning(f"🚨 Escalation triggered for: {state.get('user_input', 'unknown')}")
    
    task = state.get("task", "Escalate to human HR team")
    conversation_history = state.get("conversation_history", "")
    
    prompt = HUMAN_ESCALATION_PROMPT.format(
        task=task,
        conversation_history=conversation_history
    )
    
    print("🤖 Generating escalation message...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}]
    )
    
    escalation_message = response.choices[0].message.content
    
    print("🚨 Conversation escalated to human HR team")
    logger.warning("Escalation complete. Human intervention required.")
    
    return {
        "final_answer": escalation_message,
        "requires_human_escalation": True,
        "escalation_reason": state.get("justification", "Complex case requiring human review"),
        "messages": [("assistant", escalation_message)],
        "end_conversation": True
    }
