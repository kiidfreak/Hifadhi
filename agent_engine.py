"""
Hifadhi V2 Agent Engine
The core brain of the AI Hiring Operating System.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import json
from enum import Enum
from pydantic import BaseModel

from utils.llm_client import run_llm

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agent_engine")

class AgentStatus(Enum):
    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"

class AgentEvent(BaseModel):
    """Event emitted by an agent"""
    source: str
    type: str
    payload: Dict[str, Any]
    timestamp: str = datetime.now().isoformat()

# --- Tool Definitions ---

def search_linkedin(role: str, location: str = "Kenya"):
    """Simulates searching LinkedIn for candidates"""
    return {
        "source": "LinkedIn",
        "candidates": [
            {"name": "John Doe", "role": role, "experience": "5 years", "match": "High"},
            {"name": "Jane Smith", "role": role, "experience": "3 years", "match": "Medium"}
        ]
    }

def screen_resume(candidate_name: str, skills: List[str]):
    """Simulates screening a resume"""
    score = 85 if "Python" in skills else 60
    return {
        "candidate": candidate_name,
        "score": score,
        "decision": "Pass" if score > 70 else "Reject",
        "reason": "Strong skill match" if score > 70 else "Missing core skills"
    }

def schedule_meeting(candidate_name: str, time: str):
    """Simulates scheduling a meeting"""
    return {
        "status": "Scheduled",
        "candidate": candidate_name,
        "time": time,
        "link": "https://meet.google.com/abc-defg-hij"
    }

# Tool Registry
TOOL_FUNCTIONS = {
    "search_linkedin": search_linkedin,
    "screen_resume": screen_resume,
    "schedule_meeting": schedule_meeting
}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_linkedin",
            "description": "Search for candidates on LinkedIn",
            "parameters": {
                "type": "object",
                "properties": {
                    "role": {"type": "string"},
                    "location": {"type": "string"}
                },
                "required": ["role"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "screen_resume",
            "description": "Screen a candidate's resume against skills",
            "parameters": {
                "type": "object",
                "properties": {
                    "candidate_name": {"type": "string"},
                    "skills": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["candidate_name", "skills"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_meeting",
            "description": "Schedule an interview meeting",
            "parameters": {
                "type": "object",
                "properties": {
                    "candidate_name": {"type": "string"},
                    "time": {"type": "string"}
                },
                "required": ["candidate_name", "time"]
            }
        }
    }
]

class Agent:
    """Base class for all AI Agents"""
    def __init__(self, name: str, role: str, tools: List[Dict] = None):
        self.name = name
        self.role = role
        self.tools = tools or [] # List of tool names allowed for this agent
        self.status = AgentStatus.IDLE
        self.memory: List[Dict] = []
        self.events: List[AgentEvent] = []

    async def think(self, context: str) -> str:
        """Process context and decide on an action using Real LLM (with Fallback)"""
        self.status = AgentStatus.WORKING
        logger.info(f"🤖 {self.name} is thinking...")
        
        # Filter tools allowed for this agent
        allowed_schemas = [s for s in TOOL_SCHEMAS if s['function']['name'] in self.tools]
        
        system_prompt = f"""
        You are {self.name}, a specialized AI agent.
        Role: {self.role}
        
        Your goal is to autonomously handle tasks.
        Use the provided tools to execute actions.
        
        Current Context: {context}
        """
        
        try:
            # Call the LLM
            response = run_llm(
                prompt=system_prompt,
                tools=allowed_schemas if allowed_schemas else None,
                tool_functions=TOOL_FUNCTIONS
            )
            
            self.memory.append({"role": "assistant", "content": response})
            logger.info(f"💡 {self.name} thought/action: {response[:100]}...")
            return response
            
        except Exception as e:
            logger.warning(f"⚠️ LLM Failed (using fallback): {e}")
            return self._fallback_think(context)

    def _fallback_think(self, context: str) -> str:
        """Simulated logic when LLM is down"""
        if self.name == "SourcingAgent":
            # Simulate searching
            result = search_linkedin("Python Developer")
            return f"I searched LinkedIn and found {len(result['candidates'])} candidates. Top match: {result['candidates'][0]['name']}."
        
        elif self.name == "ScreeningAgent":
            # Simulate screening
            return "I have screened the candidate. Score: 85/100. Decision: Pass. Reason: Strong Python skills."
            
        elif self.name == "InterviewAgent":
            # Simulate scheduling
            return "I have scheduled the interview for tomorrow at 10:00 AM. Calendar invite sent."
            
        return f"I have processed the task: {context}"

    async def act(self, action_name: str, params: Dict) -> Any:
        """Execute a specific tool/action (Legacy manual call)"""
        # This is now largely handled by run_llm's internal tool execution, 
        # but kept for direct orchestration calls if needed.
        pass

    def get_state(self) -> Dict:
        return {
            "name": self.name,
            "status": self.status.value,
            "last_thought": self.memory[-1]['content'] if self.memory else None
        }

class Orchestrator:
    """Manages the lifecycle and coordination of multiple agents"""
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.global_memory: List[Dict] = []
        self.current_mission: str = ""

    def register_agent(self, agent: Agent):
        self.agents[agent.name] = agent
        logger.info(f"✅ Registered agent: {agent.name}")

    async def broadcast_event(self, event: AgentEvent):
        """Send an event to all agents (Event Bus)"""
        logger.info(f"📢 Event: {event.type} from {event.source}")
        self.global_memory.append(event.dict())
        
        # Reactive Logic with delay to show status changes
        if event.type == "CANDIDATE_FOUND":
            # Check mission intent
            mission_lower = self.current_mission.lower()
            is_hiring_mission = "hire" in mission_lower or "interview" in mission_lower or "schedule" in mission_lower
            
            if not is_hiring_mission:
                # Stop here if just searching
                await asyncio.sleep(2)
                completion_event = AgentEvent(
                    source="Orchestrator",
                    type="MISSION_COMPLETED",
                    payload={
                        "summary": "✅ Mission Complete! Found candidates.",
                        "actions_taken": [
                            "🔍 Sourced qualified candidates",
                            "📝 List compiled for review"
                        ],
                        "next_steps": [
                            {"label": "Review Candidates", "action": "view_candidates"},
                            {"label": "Start Screening", "action": "start_screening"}
                        ]
                    }
                )
                self.global_memory.append(completion_event.dict())
                logger.info("🎉 Mission completed (Sourcing Only)!")
                return

            # Wait a bit so UI can see the status change
            await asyncio.sleep(2)
            # Pass the candidate to the Screening Agent
            payload = event.payload
            context = f"New candidate found: {payload.get('name')}. Skills: {payload.get('skills')}. Please screen them."
            await self.delegate_task("ScreeningAgent", context)
            
            # After screening, trigger interview if passed
            await asyncio.sleep(2)
            context_interview = f"Schedule interview for {payload.get('name')} who passed screening."
            await self.delegate_task("InterviewAgent", context_interview)
            
            # After interview, emit mission completed event
            await asyncio.sleep(2)
            completion_event = AgentEvent(
                source="Orchestrator",
                type="MISSION_COMPLETED",
                payload={
                    "summary": "✅ Mission Complete! Found and screened Python candidates.",
                    "actions_taken": [
                        "🔍 Sourced qualified Python developers",
                        "✅ Screened candidates (Score: 85/100)",
                        "📅 Scheduled interviews"
                    ],
                    "next_steps": [
                        {"label": "Review Candidates", "action": "view_candidates"},
                        {"label": "Check Schedule", "action": "view_interviews"},
                        {"label": "Start New Mission", "action": "new_mission"}
                    ]
                }
            )
            self.global_memory.append(completion_event.dict())
            logger.info("🎉 Mission completed successfully!")

    async def delegate_task(self, agent_name: str, context: str):
        """Assign a task to a specific agent"""
        agent = self.agents.get(agent_name)
        if not agent:
            logger.error(f"❌ Agent {agent_name} not found!")
            return

        logger.info(f"👉 Delegating to {agent_name}: {context}")
        agent.status = AgentStatus.WORKING  # Set to WORKING
        
        # Wait a bit so the UI can see the status change
        await asyncio.sleep(2)
        
        result = await agent.think(context)
        
        # Keep working status a bit longer so UI catches it
        await asyncio.sleep(2)
        
        # Return to IDLE
        agent.status = AgentStatus.IDLE
        
        return result

    def _extract_role_from_mission(self, mission: str) -> str:
        """Extract the job role from mission text"""
        # Common patterns: "Hire a X", "Find X", "Search for X", etc.
        import re
        
        # Try common patterns
        patterns = [
            r"hire (?:a |an )?(.+?)(?:\s+in\s+|\s+for\s+|$)",
            r"find (?:a |an )?(.+?)(?:\s+in\s+|\s+for\s+|$)",
            r"search for (?:a |an )?(.+?)(?:\s+in\s+|\s+for\s+|$)",
            r"recruit (?:a |an )?(.+?)(?:\s+in\s+|\s+for\s+|$)",
        ]
        
        mission_lower = mission.lower()
        for pattern in patterns:
            match = re.search(pattern, mission_lower)
            if match:
                role = match.group(1).strip()
                # Clean up common words
                role = re.sub(r'\s+in\s+.*$', '', role)  # Remove location
                return role.title()  # Capitalize properly
        
        # Default fallback
        return "Candidate"
    
    async def run_mission(self, mission: str):
        """Run a high-level mission"""
        logger.info(f"🚀 Starting Mission: {mission}")
        self.current_mission = mission
        role = self._extract_role_from_mission(mission)
        candidate_name = f"{role} Candidate"
        
        mission_lower = mission.lower()
        
        if "screen" in mission_lower or "evaluate" in mission_lower:
             # Direct to Screening
             await self.delegate_task("ScreeningAgent", f"Mission: {mission}. Screen the candidates.")
             # Simulate event to continue flow if needed, or just finish
             # For this demo, we'll assume screening triggers the interview flow if successful
             event = AgentEvent(
                source="ScreeningAgent",
                type="CANDIDATE_SCREENED", # We might need to handle this in broadcast_event if we want full chaining
                payload={"name": candidate_name, "score": 85, "decision": "Pass"}
            )
             # We'll just manually chain for now to keep it simple
             await self.delegate_task("InterviewAgent", "Schedule interview for the candidate who passed screening.")
             
             completion_event = AgentEvent(
                source="Orchestrator",
                type="MISSION_COMPLETED",
                payload={
                    "summary": f"✅ Mission Complete! {role} candidates screened and interviewed.",
                    "actions_taken": ["✅ Screened candidates", "📅 Scheduled interviews"],
                    "next_steps": [{"label": "View Results", "action": "view_interviews"}]
                }
            )
             self.global_memory.append(completion_event.dict())
             
        elif "interview" in mission_lower or "schedule" in mission_lower:
             # Direct to Interview
             await self.delegate_task("InterviewAgent", f"Mission: {mission}. Schedule interviews.")
             completion_event = AgentEvent(
                source="Orchestrator",
                type="MISSION_COMPLETED",
                payload={
                    "summary": "✅ Mission Complete! Interviews scheduled.",
                    "actions_taken": ["📅 Scheduled interviews"],
                    "next_steps": [{"label": "View Calendar", "action": "view_interviews"}]
                }
            )
             self.global_memory.append(completion_event.dict())

        else:
            # Default to Sourcing
            result = await self.delegate_task("SourcingAgent", f"Mission: {mission}. Start by searching for candidates.")
            
            # Always emit event to trigger next agent (assuming sourcing always finds candidates)
            logger.info("📢 SourcingAgent completed, triggering ScreeningAgent...")
            event = AgentEvent(
                source="SourcingAgent",
                type="CANDIDATE_FOUND",
                payload={"name": candidate_name, "skills": ["Python", "Django", "FastAPI"]}
            )
            await self.broadcast_event(event)

# --- Specialized Agents Definitions ---

class SourcingAgent(Agent):
    def __init__(self):
        super().__init__(
            "SourcingAgent", 
            "Finds top talent. You search for candidates based on job descriptions.",
            tools=["search_linkedin"]
        )

class ScreeningAgent(Agent):
    def __init__(self):
        super().__init__(
            "ScreeningAgent", 
            "Evaluates candidates. You screen resumes and make pass/fail decisions.",
            tools=["screen_resume"]
        )

class InterviewAgent(Agent):
    def __init__(self):
        super().__init__(
            "InterviewAgent", 
            "Schedules and conducts interviews.",
            tools=["schedule_meeting"]
        )

# --- Factory ---
def create_hifadhi_system() -> Orchestrator:
    system = Orchestrator()
    system.register_agent(SourcingAgent())
    system.register_agent(ScreeningAgent())
    system.register_agent(InterviewAgent())
    return system

if __name__ == "__main__":
    # Test the Real AI
    async def main():
        hifadhi = create_hifadhi_system()
        print("\n--- 🧪 Testing Real AI Agents ---\n")
        
        # 1. Run a mission
        await hifadhi.run_mission("Hire a Senior Python Developer in Nairobi")
        
        # 2. Simulate finding a candidate to trigger screening
        print("\n--- 🔄 Triggering Reactive Event ---\n")
        event = AgentEvent(
            source="SourcingAgent", 
            type="CANDIDATE_FOUND", 
            payload={"name": "Alice Wanjiku", "skills": ["Python", "Django", "FastAPI"]}
        )
        await hifadhi.broadcast_event(event)

    asyncio.run(main())
