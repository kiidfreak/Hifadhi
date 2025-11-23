"""
Hifadhi V2: Agent OS Server
Exposes the Multi-Agent System via API.
"""

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
import asyncio
import uvicorn

from agent_engine import create_hifadhi_system, AgentEvent

app = FastAPI(title="Hifadhi Agent OS", version="2.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the System
hifadhi_os = create_hifadhi_system()

class MissionRequest(BaseModel):
    mission: str

class EventRequest(BaseModel):
    type: str
    source: str
    payload: Dict[str, Any]

@app.get("/")
async def root():
    return {"system": "Hifadhi Agent OS", "status": "online", "agents_active": len(hifadhi_os.agents)}

@app.get("/api/v2/agents")
async def get_agents_status():
    """Get the real-time state of all agents"""
    return {name: agent.get_state() for name, agent in hifadhi_os.agents.items()}

@app.post("/api/v2/mission")
async def start_mission(request: MissionRequest, background_tasks: BackgroundTasks):
    """Start a high-level mission (asynchronous)"""
    background_tasks.add_task(hifadhi_os.run_mission, request.mission)
    return {"status": "Mission started", "mission": request.mission}

@app.post("/api/v2/event")
async def trigger_event(request: EventRequest, background_tasks: BackgroundTasks):
    """Inject an event into the system"""
    event = AgentEvent(
        source=request.source,
        type=request.type,
        payload=request.payload
    )
    background_tasks.add_task(hifadhi_os.broadcast_event, event)
    return {"status": "Event broadcasted", "event_type": request.type}

@app.get("/api/v2/events")
async def get_recent_events():
    """Get recent events from the global memory"""
    # Return last 10 events
    return {"events": hifadhi_os.global_memory[-10:] if len(hifadhi_os.global_memory) > 0 else []}

@app.get("/dashboard")
async def serve_dashboard():
    """Serve the Mission Control Dashboard"""
    from fastapi.responses import FileResponse
    return FileResponse("dashboard_v6.html")

if __name__ == "__main__":
    print("🚀 Hifadhi Agent OS Starting...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
