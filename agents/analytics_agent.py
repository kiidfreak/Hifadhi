"""
Analytics Agent - Provides hiring metrics, pipeline analytics, performance insights
"""

import logging
from typing import Dict, Any
from utils.llm_client import run_llm
from utils.tracing import trace_agent
from prompts.agent_prompts import ANALYTICS_PROMPT
from tools.analytics_tools import get_hiring_metrics, get_pipeline_analytics

logger = logging.getLogger(__name__)


@trace_agent
def analytics_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates hiring analytics, metrics, and performance insights
    
    Args:
        state: Conversation state with analytics query
        
    Returns:
        Updated state with analytics results
    """
    print("---ANALYTICS AGENT---")
    logger.info("📊 Analytics agent started")
    
    task = state.get("task", "Provide hiring analytics")
    conversation_history = state.get("conversation_history", "")
    
    print(f"📋 Task: {task}")
    
    prompt = ANALYTICS_PROMPT.format(
        task=task,
        conversation_history=conversation_history
    )
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_hiring_metrics",
                "description": "Get overall hiring metrics (time-to-hire, cost-per-hire, etc.)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "time_period": {
                            "type": "string",
                            "description": "Time period for metrics (e.g., 'last_30_days', 'last_quarter')"
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_pipeline_analytics",
                "description": "Get hiring pipeline funnel analytics",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "job_id": {
                            "type": "string",
                            "description": "Optional: specific job to analyze"
                        }
                    }
                }
            }
        }
    ]
    
    print("🔄 Generating analytics...")
    result = run_llm(
        prompt=prompt,
        tools=tools,
        tool_functions={
            "get_hiring_metrics": get_hiring_metrics,
            "get_pipeline_analytics": get_pipeline_analytics
        }
    )
    
    print("✅ Analytics agent completed")
    logger.info("✅ Analytics generated")
    
    updated_history = (
        conversation_history 
        + f"\nAnalytics Agent: {result}"
    )
    
    return {
        "messages": [("assistant", result)],
        "conversation_history": updated_history
    }
