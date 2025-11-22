"""
Routing logic and decision functions for LangGraph workflow
"""

import logging
from typing import Dict, Any, Literal

logger = logging.getLogger(__name__)


def decide_next_agent(state: Dict[str, Any]) -> str:
    """
    Central routing function that decides which agent to call next
    
    This function is used as a conditional edge in the LangGraph workflow.
    It examines the state and returns the name of the next agent to invoke.
    
    Args:
        state: Current conversation state
    
    Returns:
        Name of next agent or 'end' to terminate
    """
    
    # ============================================
    # PRIORITY 1: Handle clarification loop
    # ============================================
    if state.get("needs_clarification"):
        logger.info("🔄 Returning to supervisor for clarification")
        return "supervisor_agent"
    
    # ============================================
    # PRIORITY 2: Check for end condition
    # ============================================
    if state.get("end_conversation"):
        logger.info("✅ Conversation complete - ending")
        return "end"
    
    # ============================================
    # PRIORITY 3: Check for human escalation
    # ============================================
    if state.get("requires_human_escalation") or state.get("escalate_to_human"):
        logger.info("🚨 Escalating to human")
        return "human_escalation_agent"
    
    # ============================================
    # PRIORITY 4: Route based on supervisor decision
    # ============================================
    next_agent = state.get("next_agent", "general_help_agent")
    
    # Validate agent name
    valid_agents = [
        "supervisor_agent",
        "candidate_screening_agent",
        "onboarding_agent",
        "compliance_agent",
        "payroll_agent",
        "analytics_agent",
        "general_help_agent",
        "human_escalation_agent",
        "final_answer_agent"
    ]
    
    if next_agent not in valid_agents:
        logger.warning(f"⚠️ Invalid agent '{next_agent}', defaulting to general_help_agent")
        return "general_help_agent"
    
    logger.info(f"➡️ Routing to: {next_agent}")
    return next_agent


def should_continue_conversation(state: Dict[str, Any]) -> Literal["continue", "end"]:
    """
    Determine if conversation should continue or end
    
    Used as a conditional edge after specialist agents complete their work
    
    Args:
        state: Current state
    
    Returns:
        'continue' to return to supervisor, 'end' to terminate
    """
    
    # Check if explicitly marked to end
    if state.get("end_conversation"):
        return "end"
    
    # Check if escalated
    if state.get("requires_human_escalation"):
        return "end"
    
    # Check iteration limit
    if state.get("n_iteration", 0) >= 5:
        logger.warning("⚠️ Max iterations reached")
        return "end"
    
    # Default: continue to supervisor for next routing decision
    return "continue"


def determine_agent_from_intent(intent: str) -> str:
    """
    Map user intent to appropriate specialist agent
    
    Args:
        intent: Detected user intent
    
    Returns:
        Agent name
    """
    intent_to_agent = {
        # Candidate screening intents
        "check_application_status": "candidate_screening_agent",
        "view_candidate_profile": "candidate_screening_agent",
        "get_interview_schedule": "candidate_screening_agent",
        "review_screening_scores": "candidate_screening_agent",
        
        # Onboarding intents
        "check_onboarding_tasks": "onboarding_agent",
        "upload_documents": "onboarding_agent",
        "onboarding_timeline": "onboarding_agent",
        
        # Compliance intents
        "verify_kra_pin": "compliance_agent",
        "check_nssf_status": "compliance_agent",
        "verify_nhif": "compliance_agent",
        "compliance_check": "compliance_agent",
        
        # Payroll intents
        "process_payment": "payroll_agent",
        "check_payment_status": "payroll_agent",
        "view_payment_history": "payroll_agent",
        "salary_inquiry": "payroll_agent",
        
        # Analytics intents
        "get_hiring_metrics": "analytics_agent",
        "view_pipeline_analytics": "analytics_agent",
        "recruitment_statistics": "analytics_agent",
        
        # General intents
        "general_question": "general_help_agent",
        "faq": "general_help_agent",
        
        # Escalation
        "complex_issue": "human_escalation_agent",
        "speak_to_human": "human_escalation_agent"
    }
    
    return intent_to_agent.get(intent, "general_help_agent")


def should_ask_for_clarification(state: Dict[str, Any], required_info: list) -> bool:
    """
    Determine if supervisor should ask for clarification
    
    Args:
        state: Current state
        required_info: List of required information keys
    
    Returns:
        True if clarification needed
    """
    for info in required_info:
        if not state.get(info):
            return True
    return False


def calculate_conversation_complexity(state: Dict[str, Any]) -> str:
    """
    Assess conversation complexity for escalation decisions
    
    Args:
        state: Current state
    
    Returns:
        Complexity level: 'simple', 'moderate', 'complex'
    """
    complexity_score = 0
    
    # Factor 1: Number of iterations
    complexity_score += state.get("n_iteration", 0) * 2
    
    # Factor 2: Number of agents involved
    conversation = state.get("conversation_history", "")
    agent_mentions = sum([
        conversation.count(agent) for agent in [
            "Candidate Screening Agent",
            "Onboarding Agent",
            "Compliance Agent",
            "Payroll Agent",
            "Analytics Agent"
        ]
    ])
    complexity_score += agent_mentions * 1.5
    
    # Factor 3: Clarifications needed
    if state.get("needs_clarification"):
        complexity_score += 3
    
    # Factor 4: Missing required information
    if not state.get("candidate_id") and "candidate" in state.get("user_input", "").lower():
        complexity_score += 2
    
    # Classify complexity
    if complexity_score < 5:
        return "simple"
    elif complexity_score < 10:
        return "moderate"
    else:
        return "complex"


def get_fallback_agent(state: Dict[str, Any]) -> str:
    """
    Determine fallback agent if routing fails
    
    Args:
        state: Current state
    
    Returns:
        Fallback agent name
    """
    user_input = state.get("user_input", "").lower()
    
    # Check for keywords
    if any(word in user_input for word in ["candidate", "application", "interview"]):
        return "candidate_screening_agent"
    
    if any(word in user_input for word in ["payment", "salary", "mpesa", "pay"]):
        return "payroll_agent"
    
    if any(word in user_input for word in ["onboard", "document", "training"]):
        return "onboarding_agent"
    
    if any(word in user_input for word in ["kra", "nssf", "nhif", "compliance"]):
        return "compliance_agent"
    
    if any(word in user_input for word in ["metric", "analytics", "report", "statistics"]):
        return "analytics_agent"
    
    # Default fallback
    return "general_help_agent"
