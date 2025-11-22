"""
Compliance Agent - Handles KRA, NSSF, NHIF verification and labor law compliance
"""

import logging
from typing import Dict, Any
from utils.llm_client import run_llm
from utils.tracing import trace_agent
from prompts.agent_prompts import COMPLIANCE_PROMPT
from tools.database_tools import get_compliance_status, get_candidate_details

logger = logging.getLogger(__name__)


@trace_agent
def compliance_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Manages compliance verification for KRA PIN, NSSF, NHIF, and labor law requirements
    
    Args:
        state: Conversation state with compliance task
        
    Returns:
        Updated state with compliance status
    """
    print("---COMPLIANCE AGENT---")
    logger.info("⚖️ Compliance agent started")
    
    task = state.get("task", "Verify compliance status")
    candidate_id = state.get("candidate_id", "Not provided")
    conversation_history = state.get("conversation_history", "")
    
    print(f"📋 Task: {task}")
    print(f"👤 Candidate ID: {candidate_id}")
    
    prompt = COMPLIANCE_PROMPT.format(
        task=task,
        candidate_id=candidate_id,
        conversation_history=conversation_history
    )
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_compliance_status",
                "description": "Retrieve compliance verification records (KRA, NSSF, NHIF)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "candidate_id": {
                            "type": "string",
                            "description": "Candidate ID to check compliance for"
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
                "description": "Get candidate personal details",
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
    
    print("🔄 Processing compliance check...")
    result = run_llm(
        prompt=prompt,
        tools=tools,
        tool_functions={
            "get_compliance_status": get_compliance_status,
            "get_candidate_details": get_candidate_details
        }
    )
    
    print("✅ Compliance agent completed")
    logger.info("✅ Compliance verification complete")
    
    updated_history = (
        conversation_history 
        + f"\nCompliance Agent: {result}"
    )
    
    return {
        "messages": [("assistant", result)],
        "conversation_history": updated_history
    }
