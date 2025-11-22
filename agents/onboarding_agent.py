"""
Onboarding Agent - Manages new hire onboarding tasks and document collection
"""

import logging
from typing import Dict, Any
from utils.llm_client import run_llm
from utils.tracing import trace_agent
from prompts.agent_prompts import ONBOARDING_PROMPT
from tools.database_tools import get_onboarding_tasks, get_candidate_details

logger = logging.getLogger(__name__)


@trace_agent
def onboarding_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handles onboarding task tracking, document collection, and timeline management
    
    Args:
        state: Conversation state with task and candidate context
        
    Returns:
        Updated state with onboarding information
    """
    print("---ONBOARDING AGENT---")
    logger.info("📋 Onboarding agent started")
    
    task = state.get("task", "Manage onboarding process")
    candidate_id = state.get("candidate_id", "Not provided")
    conversation_history = state.get("conversation_history", "")
    
    print(f"📋 Task: {task}")
    print(f"👤 Candidate ID: {candidate_id}")
    
    prompt = ONBOARDING_PROMPT.format(
        task=task,
        candidate_id=candidate_id,
        conversation_history=conversation_history
    )
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_onboarding_tasks",
                "description": "Retrieve onboarding checklist for a candidate",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "candidate_id": {
                            "type": "string",
                            "description": "Candidate ID to get onboarding tasks for"
                        }
                    },
                    "required": ["candidate_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_candidate_details",
                "description": "Get candidate profile information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "candidate_id": {"type": "string"}
                    },
                    "required": ["candidate_id"]
                }
            }
        }
    ]
    
    print("🔄 Processing onboarding request...")
    result = run_llm(
        prompt=prompt,
        tools=tools,
        tool_functions={
            "get_onboarding_tasks": get_onboarding_tasks,
            "get_candidate_details": get_candidate_details
        }
    )
    
    print("✅ Onboarding agent completed")
    logger.info("✅ Onboarding check complete")
    
    updated_history = (
        conversation_history 
        + f"\nOnboarding Agent: {result}"
    )
    
    return {
        "messages": [("assistant", result)],
        "conversation_history": updated_history
    }
