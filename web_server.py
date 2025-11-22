"""
Enhanced FastAPI server with CORS support and static file serving
"""

import logging
import os
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime
import sqlite3

from workflows.langgraph_workflow import app as workflow_app
from utils.state_management import create_initial_state

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hifadhi_server")

# Initialize FastAPI
app = FastAPI(
    title="Hifadhi Multi-Agent API",
    description="API for Hifadhi HR Agent System with PayLink Integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
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

# API Endpoints
@app.get("/")
async def root():
    """Health check and system status"""
    return {
        "status": "online",
        "system": "Hifadhi Multi-Agent OS",
        "version": "1.0.0"
    }

@app.get("/ui", response_class=HTMLResponse)
async def serve_ui():
    """Serve the web UI"""
    try:
        with open("web_ui.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>UI Not Found</h1><p>Please ensure web_ui.html exists in the project root.</p>",
            status_code=404
        )

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Process a user query through the multi-agent workflow
    """
    logger.info(f"📨 Received chat request: {request.query}")
    
    try:
        # Initialize state
        initial_state = create_initial_state(request.query)
        if request.session_id:
            initial_state["session_id"] = request.session_id
            
        # Run workflow
        final_state = workflow_app.invoke(initial_state)
        
        # Extract response
        response_text = final_state.get("final_answer", "I processed your request but have no response.")
        
        # Extract agent history for debugging/UI
        history = final_state.get("conversation_history", "").split("\n")
        agent_history = [line for line in history if "Agent:" in line]
        
        return ChatResponse(
            response=response_text,
            session_id=final_state.get("session_id", "unknown"),
            agent_history=agent_history,
            requires_action=final_state.get("needs_clarification", False)
        )
        
    except Exception as e:
        logger.error(f"❌ Error processing chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhooks/paylink")
async def paylink_webhook(callback: Request):
    """
    Handle M-Pesa payment callbacks from PayLink
    """
    try:
        payload = await callback.json()
        logger.info(f"💰 Received PayLink webhook: {payload}")
        
        transaction_id = payload.get("transaction_id")
        status = payload.get("status")
        
        if not transaction_id:
            logger.warning("⚠️ Webhook missing transaction_id")
            return {"status": "ignored"}
            
        # Update database
        _update_payment_status(transaction_id, status, payload)
        
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Webhook processing failed")

def _update_payment_status(transaction_id: str, status: str, details: Dict[str, Any]):
    """Update payment status in SQLite database"""
    try:
        conn = sqlite3.connect('data/hifadhi.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE payroll 
            SET status = ?, 
                payment_date = ? 
            WHERE transaction_id = ?
        """, (
            status, 
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
            transaction_id
        ))
        
        if cursor.rowcount > 0:
            logger.info(f"✅ Updated payment {transaction_id} to {status}")
        else:
            logger.warning(f"⚠️ Payment {transaction_id} not found in database")
            
        conn.commit()
        conn.close()
        
    except Exception as e:
        logger.error(f"❌ Database update failed: {e}")

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*70)
    print("🚀 Starting Hifadhi Multi-Agent API Server")
    print("="*70)
    print("\n🌐 Access points:")
    print("  - API:        http://localhost:8000")
    print("  - Web UI:     http://localhost:8000/ui")
    print("  - API Docs:   http://localhost:8000/docs")
    print("\n" + "="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
