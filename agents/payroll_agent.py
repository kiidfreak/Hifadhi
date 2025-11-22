"""
Payroll Agent - Handles salary payments, M-Pesa transactions, payment history
"""

import logging
from typing import Dict, Any
from utils.llm_client import run_llm
from utils.tracing import trace_agent
from prompts.agent_prompts import PAYROLL_PROMPT
from tools.database_tools import get_payroll_history, get_candidate_details
from tools.paylink_tools import process_mpesa_payment, check_payment_status

logger = logging.getLogger(__name__)


@trace_agent
def payroll_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Manages payroll operations, M-Pesa payments, and transaction tracking
    
    Args:
        state: Conversation state with payment task
        
    Returns:
        Updated state with payment information
    """
    print("---PAYROLL AGENT---")
    logger.info("💰 Payroll agent started")
    
    task = state.get("task", "Handle payment inquiry")
    candidate_id = state.get("candidate_id", "Not provided")
    conversation_history = state.get("conversation_history", "")
    
    print(f"📋 Task: {task}")
    print(f"👤 Candidate ID: {candidate_id}")
    
    prompt = PAYROLL_PROMPT.format(
        task=task,
        candidate_id=candidate_id,
        conversation_history=conversation_history
    )
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_payroll_history",
                "description": "Get payment history for a candidate",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "candidate_id": {
                            "type": "string",
                            "description": "Candidate ID to retrieve payment history for"
                        }
                    },
                    "required": ["candidate_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "process_mpesa_payment",
                "description": "Process M-Pesa payment to candidate",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "candidate_id": {"type": "string"},
                        "amount": {"type": "number"},
                        "phone_number": {"type": "string"},
                        "payment_type": {
                            "type": "string",
                            "enum": ["salary", "bonus", "reimbursement"]
                        }
                    },
                    "required": ["candidate_id", "amount", "phone_number", "payment_type"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "check_payment_status",
                "description": "Check status of a payment transaction",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "transaction_id": {
                            "type": "string",
                            "description": "Transaction ID to check"
                        }
                    },
                    "required": ["transaction_id"]
                }
            }
        }
    ]
    
    print("🔄 Processing payroll request...")
    result = run_llm(
        prompt=prompt,
        tools=tools,
        tool_functions={
            "get_payroll_history": get_payroll_history,
            "process_mpesa_payment": process_mpesa_payment,
            "check_payment_status": check_payment_status
        }
    )
    
    print("✅ Payroll agent completed")
    logger.info("✅ Payroll operation complete")
    
    updated_history = (
        conversation_history 
        + f"\nPayroll Agent: {result}"
    )
    
    return {
        "messages": [("assistant", result)],
        "conversation_history": updated_history
    }
