"""
OpenAI client with tool calling support
"""

from openai import OpenAI
import json
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def run_llm(
    prompt: str,
    tools: Optional[List[Dict]] = None,
    tool_functions: Optional[Dict[str, Any]] = None,
    model: str = "gpt-4o-mini",
) -> str:
    """
    Execute LLM call with optional tool support
    
    Args:
        prompt: System prompt
        tools: Tool schema for function calling
        tool_functions: Mapping of tool names to Python functions
        model: Model to use (default: gpt-4o-mini)
    
    Returns:
        Final LLM response text
    """
    
    # Step 1: Initial LLM call
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": prompt}],
        tools=tools if tools else None,
        tool_choice="auto" if tools else None
    )
    
    message = response.choices[0].message
    
    # Step 2: If no tool calls, return simple response
    if not getattr(message, "tool_calls", None):
        return message.content
    
    # Step 3: Execute tool calls
    if not tool_functions:
        return message.content + "\n\n⚠️ No tool functions provided."
    
    tool_messages = []
    for tool_call in message.tool_calls:
        func_name = tool_call.function.name
        args = json.loads(tool_call.function.arguments or "{}")
        tool_fn = tool_functions.get(func_name)
        
        try:
            result = tool_fn(**args) if tool_fn else {"error": f"Tool '{func_name}' not found."}
        except Exception as e:
            result = {"error": str(e)}
        
        tool_messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result)
        })
    
    # Step 4: Second pass - send tool outputs back
    followup_messages = [
        {"role": "system", "content": prompt},
        {
            "role": "assistant",
            "content": message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                } for tc in message.tool_calls
            ],
        },
        *tool_messages,
    ]
    
    final = client.chat.completions.create(model=model, messages=followup_messages)
    return final.choices[0].message.content
