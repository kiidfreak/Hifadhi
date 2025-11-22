"""
Candidate Screening Agent - Handles application status, candidate profiles, AI screening
"""

import logging
from typing import Dict, Any
from utils.llm_client import run_llm
from utils.tracing import trace_agent
from prompts.agent_prompts import CANDIDATE_SCREENING_PROMPT
from tools.database_tools import (
    get_candidate_details,
    get_job_details,
    get_application_status,
    get_interview_schedule
)

logger = logging.getLogger(__name__)


@trace_agent
def candidate_screening_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handles candidate screening, application tracking, and interview scheduling
    
    Args:
        state: Conversation state with task and context
        
    Returns:
        Updated state with screening results
    """
    print("---CANDIDATE SCREENING AGENT---")
    logger.info("🔍 Candidate screening agent started")
    
    # Extract context
    task = state.get("task", "Provide candidate information")
    candidate_id = state.get("candidate_id", "Not provided")
    job_id = state.get("job_id", "Not provided")
    application_id = state.get("application_id", "Not provided")
    conversation_history = state.get("conversation_history", "")
    
    print(f"📋 Task: {task}")
    print(f"👤 Candidate ID: {candidate_id}")
    print(f"💼 Job ID: {job_id}")
    
    # Format prompt
    prompt = CANDIDATE_SCREENING_PROMPT.format(
        task=task,
        candidate_id=candidate_id,
        job_id=job_id,
        application_id=application_id,
        conversation_history=conversation_history
    )
    
    # Define available tools
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_candidate_details",
                "description": "Retrieve candidate profile information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "candidate_id": {
                            "type": "string",
                            "description": "Unique candidate identifier (e.g., CAND00001)"
                        }
                    },
                    "required": ["candidate_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_job_details",
                "description": "Retrieve job posting details",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "job_id": {
                            "type": "string",
                            "description": "Job identifier (e.g., JOB0001)"
                        }
                    },
                    "required": ["job_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_application_status",
                "description": "Get application status and details",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "application_id": {
                            "type": "string",
                            "description": "Application ID"
                        },
                        "candidate_id": {
                            "type": "string",
                            "description": "Candidate ID (alternative lookup)"
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_interview_schedule",
                "description": "Retrieve interview schedule",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "candidate_id": {
                            "type": "string"
                        },
                        "application_id": {
                            "type": "string"
                        }
                    }
                }
            }
        }
    ]
    
    # Execute LLM with tools
    print("🔄 Processing screening request...")
    result = run_llm(
        prompt=prompt,
        tools=tools,
        tool_functions={
            "get_candidate_details": get_candidate_details,
            "get_job_details": get_job_details,
            "get_application_status": get_application_status,
            "get_interview_schedule": get_interview_schedule
        }
    )
    
    print("✅ Candidate screening agent completed")
    logger.info("✅ Screening complete")
    
    # Update conversation history
    updated_history = (
        conversation_history 
        + f"\nCandidate Screening Agent: {result}"
    )
    
    return {
        "messages": [("assistant", result)],
        "conversation_history": updated_history
    }
