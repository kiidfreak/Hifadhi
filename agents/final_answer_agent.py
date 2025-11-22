"""
Final Answer Agent - Polishes and summarizes responses before ending conversation
"""

import logging
from typing import Dict, Any
from utils.llm_client import client
from utils.tracing import trace_agent

logger = logging.getLogger(__name__)

FINAL_ANSWER_PROMPT = """
The HR manager asked: "{user_query}"

The specialist agent provided this response:
{specialist_response}

Your task: Create a FINAL, POLISHED response that:
1. Directly answers the original question in a professional tone
2. Includes only the most relevant information
3. Is clear, concise, and actionable
4. Ends with a helpful closing (e.g., "Is there anything else I can help with?")

Important: Remove any technical details, internal reasoning, or tool call information.

Final response:
"""


@trace_agent
def final_answer_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates final polished response before ending conversation
    
    Args:
        state: Conversation state with specialist responses
        
    Returns:
        Final state with clean, user-ready answer
    """
    print("---FINAL ANSWER AGENT---")
    logger.info("🎯 Final answer agent started")
    
    user_query = state["user_input"]
    conversation_history = state.get("conversation_history", "")
    
    # Extract most recent specialist response
    recent_responses = []
    for msg in reversed(state.get("messages", [])):
        if hasattr(msg, 'content') and "clarification" not in msg.content.lower():
            recent_responses.append(msg.content)
            if len(recent_responses) >= 2:
                break
        elif isinstance(msg, tuple) and len(msg) == 2:
            role, content = msg
            if "clarification" not in content.lower():
                recent_responses.append(content)
                if len(recent_responses) >= 2:
                    break
    
    specialist_response = recent_responses[0] if recent_responses else "No response available"
    
    prompt = FINAL_ANSWER_PROMPT.format(
        user_query=user_query,
        specialist_response=specialist_response
    )
    
    print("🤖 Generating final polished response...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}]
    )
    
    final_answer = response.choices[0].message.content
    
    print(f"✅ Final answer generated: {final_answer[:100]}...")
    logger.info("✅ Final answer complete")
    
    # Update state with clean final response
    updated_history = (
        conversation_history 
        + f"\nAssistant (Final): {final_answer}"
    )
    
    return {
        "final_answer": final_answer,
        "end_conversation": True,
        "conversation_history": updated_history,
        "messages": [("assistant", final_answer)]
    }
