"""
Simplified production server with direct agent calls
"""

import logging
import os
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime
import sqlite3

from utils.llm_client import run_llm
from tools.database_tools import (
    get_candidate_details,
    get_application_status,
    get_interview_schedule,
    get_payroll_history
)
from tools.analytics_tools import get_hiring_metrics, get_pipeline_analytics
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hifadhi_server")

# Initialize FastAPI
app = FastAPI(
    title="Hifadhi Multi-Agent API",
    description="AI-Powered HR Management System",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    agent_history: list
    requires_action: bool = False

def process_query_simple(query: str) -> str:
    """Process query using direct LLM call with tools"""
    
    # Determine intent and call appropriate tools
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_application_status",
                "description": "Get status of a job application",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "application_id": {"type": "string", "description": "Application ID like APP00001"}
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_hiring_metrics",
                "description": "Get hiring metrics and statistics",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "time_period": {"type": "string", "description": "Time period like 'last_30_days'"}
                    }
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
                        "candidate_id": {"type": "string", "description": "Candidate ID like CAND00001"}
                    },
                    "required": ["candidate_id"]
                }
            }
        }
    ]
    
    prompt = f"""You are Hifadhi, an AI HR assistant for companies in Kenya.

User Query: {query}

Analyze the query and use the appropriate tools to help the user. 

If asked about application status, use get_application_status.
If asked about metrics or analytics, use get_hiring_metrics.
If asked about a candidate, use get_candidate_details.

Provide helpful, professional responses formatted nicely with:
- Clear sections
- Bullet points
- Emojis for visual appeal
- Specific data from the tools

Be concise but thorough."""

    tool_functions = {
        "get_application_status": get_application_status,
        "get_hiring_metrics": get_hiring_metrics,
        "get_candidate_details": get_candidate_details,
        "get_pipeline_analytics": get_pipeline_analytics
    }
    
    try:
        response = run_llm(
            prompt=prompt,
            tools=tools,
            tool_functions=tool_functions
        )
        return response
    except Exception as e:
        logger.error(f"LLM error: {e}", exc_info=True)
        return f"I encountered an error: {str(e)}\n\nPlease check your OpenAI API key in the .env file."

@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "online",
        "system": "Hifadhi Multi-Agent OS",
        "version": "1.0.0",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY"))
    }

@app.get("/ui", response_class=HTMLResponse)
async def serve_ui():
    """Serve the web UI"""
    try:
        with open("web_ui.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>UI Not Found</h1>",
            status_code=404
        )

@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard():
    """Serve the multi-page dashboard"""
    try:
        with open("dashboard.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Dashboard Not Found</h1>",
            status_code=404
        )

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Process user query"""
    logger.info(f"📨 Query: {request.query}")
    
    try:
        # Process with simplified LLM
        response_text = process_query_simple(request.query)
        
        return ChatResponse(
            response=response_text,
            session_id=request.session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            agent_history=["AI Agent: Processed query"],
            requires_action=False
        )
        
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhooks/paylink")
async def paylink_webhook(callback: Request):
    """Handle M-Pesa payment callbacks"""
    try:
        payload = await callback.json()
        logger.info(f"💰 Webhook: {payload}")
        return {"status": "received"}
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*70)
    print("🚀 Hifadhi AI-Powered HR System")
    print("="*70)
    print("\n🌐 Access:")
    print("  - Web UI:     http://localhost:8000/ui")
    print("  - API Docs:   http://localhost:8000/docs")
    print("\n✅ OpenAI Configured:", bool(os.getenv("OPENAI_API_KEY")))
    print("="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
