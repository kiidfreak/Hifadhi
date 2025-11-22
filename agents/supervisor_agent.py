"""
Supervisor Agent - Central orchestrator for Hifadhi multi-agent system
Routes queries to specialist agents and manages conversation flow
"""

import json
import logging
from typing import Dict, Any
from utils.llm_client import run_llm, client
from utils.tracing import trace_agent
from prompts.agent_prompts import SUPERVISOR_PROMPT
from tools.user_interaction_tools import ask_user

logger = logging.getLogger(__name__)


@trace_agent
def supervisor_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Central routing agent that analyzes intent and delegates to specialists
    
    Args:
        state: Current conversation state with history and context
        
    Returns:
        Updated state with routing decision and task assignment
    """
    print("---SUPERVISOR AGENT---")
    
    # Increment iteration counter
    n_iter = state.get("n_iteration", 0) + 1
    state["n_iteration"] = n_iter
    print(f"🔢 Supervisor iteration: {n_iter}")
    
    # Force escalation if iteration limit reached
    if n_iter >= 5:
        print("⚠️ Maximum supervisor iterations reached — escalating to human")
        logger.warning(f"Max iterations reached. Escalating. State: {state.get('user_input')}")
        
        updated_history = (
            state.get("conversation_history", "")
            + "\nAssistant: This issue requires human review. Escalating to HR specialist."
        )
        
        return {
            "escalate_to_human": True,
            "conversation_history": updated_history,
            "next_agent": "human_escalation_agent",
            "n_iteration": n_iter,
            "task": "Escalate complex case to human HR team"
        }
    
    # Check if we're processing a clarification response
    if state.get("needs_clarification", False):
        user_clarification = state.get("user_clarification", "")
        print(f"🔄 Processing clarification: {user_clarification}")
        
        clarification_question = state.get("clarification_question", "")
        updated_conversation = (
            state.get("conversation_history", "") 
            + f"\nAssistant: {clarification_question}\nUser: {user_clarification}"
        )
        
        # Clear clarification flags and update state
        updated_state = state.copy()
        updated_state["needs_clarification"] = False
        updated_state["conversation_history"] = updated_conversation
        
        # Remove clarification-specific keys
        for key in ["clarification_question", "user_clarification"]:
            updated_state.pop(key, None)
        
        return updated_state
    
    # Extract context
    user_query = state["user_input"]
    conversation_history = state.get("conversation_history", "")
    
    print(f"📝 User Query: {user_query}")
    logger.info(f"Supervisor processing: {user_query[:100]}...")
    
    # Build full context prompt
    full_context = f"Full Conversation:\n{conversation_history}"
    
    prompt = SUPERVISOR_PROMPT.format(
        conversation_history=full_context
    )
    
    # Define ask_user tool schema
    tools = [
        {
            "type": "function",
            "function": {
                "name": "ask_user",
                "description": "Ask user for clarification when essential info is missing (candidate ID, job ID, etc.)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "Specific clarification question (max 15 words)"
                        },
                        "missing_info": {
                            "type": "string",
                            "description": "What information is missing"
                        }
                    },
                    "required": ["question", "missing_info"]
                }
            }
        }
    ]
    
    # Call LLM with tool support
    print("🤖 Calling LLM for routing decision...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}],
        tools=tools,
        tool_choice="auto"
    )
    
    message = response.choices[0].message
    
    # Handle clarification request
    if getattr(message, "tool_calls", None):
        print("🛠️ Supervisor requesting clarification")
        
        for tool_call in message.tool_calls:
            if tool_call.function.name == "ask_user":
                args = json.loads(tool_call.function.arguments)
                question = args.get("question", "Can you provide more details?")
                missing_info = args.get("missing_info", "additional information")
                
                print(f"❓ Asking user: {question}")
                logger.info(f"Clarification requested: {missing_info}")
                
                # Get user response
                user_response_data = ask_user(question, missing_info)
                user_response = user_response_data["context"]
                
                print(f"✅ User response: {user_response}")
                
                # Update history with Q&A exchange
                updated_history = (
                    conversation_history 
                    + f"\nAssistant: {question}"
                    + f"\nUser: {user_response}"
                )
                
                return {
                    "needs_clarification": True,
                    "clarification_question": question,
                    "user_clarification": user_response,
                    "conversation_history": updated_history
                }
    
    # Parse routing decision
    message_content = message.content
    
    try:
        parsed = json.loads(message_content)
        print("✅ Supervisor decision parsed successfully")
    except json.JSONDecodeError:
        print("❌ Invalid JSON from supervisor, using fallback")
        logger.error(f"JSON parse error: {message_content[:200]}")
        parsed = {
            "next_agent": "general_help_agent",
            "task": "Assist with general query",
            "justification": "Fallback routing due to parse error"
        }
    
    next_agent = parsed.get("next_agent", "general_help_agent")
    task = parsed.get("task", "Assist the user")
    justification = parsed.get("justification", "")
    
    print(f"---SUPERVISOR DECISION: {next_agent}---")
    print(f"📋 Task: {task}")
    print(f"💡 Reason: {justification}")
    logger.info(f"Routing to {next_agent}: {task}")
    
    # Update conversation history
    updated_conversation = (
        conversation_history 
        + f"\nAssistant: Routing to {next_agent} for: {task}"
    )
    
    return {
        "next_agent": next_agent,
        "task": task,
        "justification": justification,
        "conversation_history": updated_conversation,
        "n_iteration": n_iter
    }
