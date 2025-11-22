"""
State management for Hifadhi multi-agent system
Defines the conversation state structure using TypedDict
"""

from typing import TypedDict, List, Annotated, Dict, Any, Optional
from langgraph.graph import add_messages
from datetime import datetime


class HifadhiState(TypedDict):
    """
    Complete state structure for Hifadhi conversation flow
    
    This state is passed between all agents and tracks:
    - Conversation history and messages
    - User context (candidate ID, job ID, etc.)
    - Routing decisions
    - Agent outputs
    - Escalation flags
    """
    
    # ============================================
    # CORE CONVERSATION TRACKING
    # ============================================
    messages: Annotated[List[Any], add_messages]
    """All conversation messages (assistant and user)"""
    
    user_input: str
    """Current user query"""
    
    conversation_history: Optional[str]
    """Full conversation history as text"""
    
    n_iteration: Optional[int]
    """Iteration counter for supervisor (prevents infinite loops)"""
    
    # ============================================
    # USER INTENT & CONTEXT
    # ============================================
    user_intent: Optional[str]
    """Detected user intent (e.g., 'check_application_status', 'process_payment')"""
    
    candidate_id: Optional[str]
    """Candidate identifier (e.g., CAND00001)"""
    
    job_id: Optional[str]
    """Job posting identifier (e.g., JOB0001)"""
    
    application_id: Optional[str]
    """Application identifier (e.g., APP00001)"""
    
    claim_id: Optional[str]
    """Claim/issue identifier (reserved for future use)"""
    
    # ============================================
    # SUPERVISOR & ROUTING LAYER
    # ============================================
    next_agent: Optional[str]
    """Next agent to route to (determined by supervisor)"""
    
    task: Optional[str]
    """Current task assigned to specialist agent"""
    
    justification: Optional[str]
    """Supervisor's reasoning for routing decision"""
    
    end_conversation: Optional[bool]
    """Flag to end conversation gracefully"""
    
    # ============================================
    # CLARIFICATION FLOW
    # ============================================
    needs_clarification: Optional[bool]
    """Flag indicating if supervisor needs user input"""
    
    clarification_question: Optional[str]
    """Question asked to user for clarification"""
    
    user_clarification: Optional[str]
    """User's response to clarification question"""
    
    # ============================================
    # ENTITY EXTRACTION & DB LOOKUPS
    # ============================================
    extracted_entities: Dict[str, Any]
    """Parsed entities from user input (names, dates, IDs)"""
    
    database_lookup_result: Dict[str, Any]
    """Results from database queries"""
    
    retrieved_faqs: Optional[List[Dict[str, Any]]]
    """FAQs retrieved from vector store (General Help Agent)"""
    
    # ============================================
    # ESCALATION STATE
    # ============================================
    requires_human_escalation: bool
    """Flag for human escalation requirement"""
    
    escalation_reason: Optional[str]
    """Reason for escalation"""
    
    escalate_to_human: Optional[bool]
    """Direct escalation flag from supervisor"""
    
    # ============================================
    # PAYMENT-SPECIFIC FIELDS
    # ============================================
    billing_amount: Optional[float]
    """Payment amount in KES"""
    
    payment_method: Optional[str]
    """Payment method (M-Pesa, Bank Transfer, etc.)"""
    
    payment_status: Optional[str]
    """Payment transaction status"""
    
    transaction_id: Optional[str]
    """PayLink transaction ID"""
    
    mpesa_phone: Optional[str]
    """M-Pesa phone number for payment"""
    
    # ============================================
    # ONBOARDING-SPECIFIC FIELDS
    # ============================================
    onboarding_stage: Optional[str]
    """Current onboarding stage (documents, compliance, training, etc.)"""
    
    pending_documents: Optional[List[str]]
    """List of pending documents"""
    
    # ============================================
    # COMPLIANCE-SPECIFIC FIELDS
    # ============================================
    kra_pin_verified: Optional[bool]
    """KRA PIN verification status"""
    
    nssf_verified: Optional[bool]
    """NSSF enrollment status"""
    
    nhif_verified: Optional[bool]
    """NHIF enrollment status"""
    
    compliance_issues: Optional[List[str]]
    """List of compliance issues"""
    
    # ============================================
    # ANALYTICS-SPECIFIC FIELDS
    # ============================================
    analytics_time_period: Optional[str]
    """Time period for analytics (last_30_days, last_quarter, etc.)"""
    
    metrics_requested: Optional[List[str]]
    """Specific metrics requested by user"""
    
    # ============================================
    # SYSTEM METADATA
    # ============================================
    timestamp: Optional[str]
    """ISO timestamp of latest state update"""
    
    final_answer: Optional[str]
    """Final polished response to user"""
    
    error_message: Optional[str]
    """Error message if something went wrong"""
    
    session_id: Optional[str]
    """Unique session identifier for tracking"""


def create_initial_state(user_query: str) -> HifadhiState:
    """
    Create initial state for a new conversation
    
    Args:
        user_query: User's initial question
    
    Returns:
        Initialized HifadhiState dictionary
    """
    return {
        # Core
        "n_iteration": 0,
        "messages": [],
        "user_input": user_query,
        "conversation_history": f"User: {user_query}",
        
        # Context
        "user_intent": "",
        "candidate_id": "",
        "job_id": "",
        "application_id": "",
        "claim_id": "",
        
        # Routing
        "next_agent": "supervisor_agent",
        "task": "Help user with their HR query",
        "justification": "",
        "end_conversation": False,
        
        # Clarification
        "needs_clarification": False,
        "clarification_question": "",
        "user_clarification": "",
        
        # Data
        "extracted_entities": {},
        "database_lookup_result": {},
        "retrieved_faqs": None,
        
        # Escalation
        "requires_human_escalation": False,
        "escalation_reason": "",
        "escalate_to_human": False,
        
        # Payment
        "billing_amount": None,
        "payment_method": None,
        "payment_status": None,
        "transaction_id": None,
        "mpesa_phone": None,
        
        # Onboarding
        "onboarding_stage": None,
        "pending_documents": None,
        
        # Compliance
        "kra_pin_verified": None,
        "nssf_verified": None,
        "nhif_verified": None,
        "compliance_issues": None,
        
        # Analytics
        "analytics_time_period": None,
        "metrics_requested": None,
        
        # System
        "timestamp": datetime.now().isoformat(),
        "final_answer": "",
        "error_message": None,
        "session_id": f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    }


def update_state(
    current_state: HifadhiState, 
    updates: Dict[str, Any]
) -> HifadhiState:
    """
    Safely update state with new values
    
    Args:
        current_state: Current state dictionary
        updates: Dictionary of updates to apply
    
    Returns:
        Updated state
    """
    new_state = current_state.copy()
    new_state.update(updates)
    new_state["timestamp"] = datetime.now().isoformat()
    return new_state


def extract_ids_from_history(conversation_history: str) -> Dict[str, Optional[str]]:
    """
    Extract candidate ID, job ID, application ID from conversation history
    
    Args:
        conversation_history: Full conversation text
    
    Returns:
        Dictionary with extracted IDs
    """
    import re
    
    ids = {
        "candidate_id": None,
        "job_id": None,
        "application_id": None
    }
    
    # Regex patterns for ID formats
    candidate_pattern = r"CAND\d{5}"
    job_pattern = r"JOB\d{4}"
    application_pattern = r"APP\d{5}"
    
    # Search for IDs in history
    candidate_match = re.search(candidate_pattern, conversation_history)
    if candidate_match:
        ids["candidate_id"] = candidate_match.group(0)
    
    job_match = re.search(job_pattern, conversation_history)
    if job_match:
        ids["job_id"] = job_match.group(0)
    
    application_match = re.search(application_pattern, conversation_history)
    if application_match:
        ids["application_id"] = application_match.group(0)
    
    return ids


def is_state_ready_for_agent(state: HifadhiState, agent_name: str) -> bool:
    """
    Check if state has required information for a specific agent
    
    Args:
        state: Current state
        agent_name: Name of agent to check readiness for
    
    Returns:
        True if ready, False otherwise
    """
    requirements = {
        "candidate_screening_agent": ["candidate_id"],
        "onboarding_agent": ["candidate_id"],
        "compliance_agent": ["candidate_id"],
        "payroll_agent": ["candidate_id"],
        "analytics_agent": [],  # No specific requirements
        "general_help_agent": []  # No specific requirements
    }
    
    required_fields = requirements.get(agent_name, [])
    
    for field in required_fields:
        if not state.get(field):
            return False
    
    return True
