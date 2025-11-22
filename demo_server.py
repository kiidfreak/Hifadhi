"""
Simplified demo server for Hifadhi UI testing
This version provides mock responses to demonstrate the UI without requiring API keys
"""

import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hifadhi_demo")

# Initialize FastAPI
app = FastAPI(
    title="Hifadhi Demo Server",
    description="Demo server for Hifadhi UI",
    version="1.0.0-demo"
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

# Mock responses for demo
MOCK_RESPONSES = {
    "app00001": """📋 **Application Status for APP00001**

**Candidate**: Jane Mwangi  
**Position**: Customer Service Representative  
**Status**: Interview Scheduled  
**AI Screening Score**: 78/100  

**Interview Details**:
- **Date**: December 15, 2024
- **Time**: 10:00 AM
- **Location**: Nairobi Office, 5th Floor
- **Interviewer**: Sarah Kamau (HR Manager)

**Application Timeline**:
✅ Application Submitted - Nov 20, 2024  
✅ AI Screening Completed - Nov 22, 2024  
✅ Interview Scheduled - Nov 25, 2024  
🔄 Interview Pending - Dec 15, 2024  

The candidate has strong communication skills and 3 years of customer service experience. Recommended for technical skills assessment.
""",
    "metrics": """📊 **Hiring Metrics - Last 30 Days**

**Overview**:
- **Total Applications**: 127
- **Positions Open**: 8
- **Interviews Scheduled**: 23
- **Offers Extended**: 5
- **Hires Completed**: 3

**Performance Metrics**:
- **Average Time-to-Hire**: 18 days
- **Application-to-Interview Rate**: 18%
- **Interview-to-Offer Rate**: 22%
- **Offer Acceptance Rate**: 60%

**Top Performing Positions**:
1. Customer Service Representative - 45 applications
2. Software Engineer - 32 applications
3. Sales Executive - 28 applications

**Pipeline Health**: 🟢 Good  
Your hiring funnel is performing well with healthy conversion rates at each stage.
""",
    "onboarding": """📄 **Onboarding Documents Required**

**Personal Documents**:
✅ National ID Card (Copy)  
✅ KRA PIN Certificate  
✅ NSSF Number  
✅ NHIF Number  
✅ Passport-size Photos (2)  

**Banking Information**:
✅ Bank Account Details  
✅ M-Pesa Phone Number (for salary)  

**Education & Professional**:
✅ Academic Certificates  
✅ Professional Qualifications  
✅ Previous Employment Letters  

**HR Documents** (Provided by Company):
- Employment Contract
- Job Description
- Company Policies Handbook
- Code of Conduct

**Timeline**:
- **Week 1**: Document verification
- **Week 2**: System access setup
- **Week 3**: Department orientation
- **Week 4**: Full onboarding complete

All documents should be submitted within 7 days of offer acceptance.
""",
    "compliance": """✅ **Compliance Verification for CAND00001**

**Candidate**: John Kiplagat  

**KRA PIN Verification**:
✅ **Status**: Verified  
📄 **PIN**: A123456789X  
🕐 **Last Updated**: Nov 20, 2024  

**NSSF Verification**:
✅ **Status**: Active  
📄 **Number**: NSS001234567  
💰 **Contributions**: Up to date  

**NHIF Verification**:
✅ **Status**: Active  
📄 **Number**: 1234567890  
💰 **Contributions**: Current  

**Labor Law Compliance**:
✅ All employment documents reviewed  
✅ Contract terms compliant  
✅ Minimum wage requirements met  
✅ Working hours within legal limits  

**Overall Compliance Score**: 100% ✅

The candidate meets all statutory requirements for employment in Kenya.
""",
    "default": """🤖 Hello! I'm Hifadhi, your AI HR Assistant.

I can help you with:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 CANDIDATE SCREENING
  • Check application status
  • Review AI screening scores  
  • Schedule interviews

💰 PAYROLL & PAYMENTS
  • Process M-Pesa salary payments
  • View payment history
  • Bulk payroll processing

✅ COMPLIANCE VERIFICATION
  • Verify KRA PIN, NSSF, NHIF
  • Labor law compliance checks
  • Document verification

📊 ANALYTICS & INSIGHTS
  • Hiring metrics and KPIs
  • Pipeline performance analytics
  • Recruitment insights

📄 ONBOARDING MANAGEMENT
  • Task tracking
  • Document collection
  • Timeline management

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 TRY ASKING:

"What is the status of application APP00001?"
"Show me hiring metrics for last 30 days"
"What documents are needed for onboarding?"
"Verify compliance for candidate CAND00001"
"""
}

def get_mock_response(query: str) -> str:
    """Generate mock response based on query"""
    query_lower = query.lower()
    
    if "app00001" in query_lower or "application" in query_lower:
        return MOCK_RESPONSES["app00001"]
    elif "metric" in query_lower or "hiring" in query_lower or "analytics" in query_lower:
        return MOCK_RESPONSES["metrics"]
    elif "onboarding" in query_lower or "document" in query_lower:
        return MOCK_RESPONSES["onboarding"]
    elif "compliance" in query_lower or "kra" in query_lower or "nssf" in query_lower:
        return MOCK_RESPONSES["compliance"]
    else:
        return MOCK_RESPONSES["default"]

@app.get("/")
async def root():
    """Health check and system status"""
    return {
        "status": "online",
        "system": "Hifadhi Multi-Agent OS (Demo Mode)",
        "version": "1.0.0-demo",
        "note": "Using mock responses for demonstration"
    }

@app.get("/ui", response_class=HTMLResponse)
async def serve_ui():
    """Serve the web UI"""
    try:
        with open("web_ui.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>UI Not Found</h1><p>Please ensure web_ui.html exists.</p>",
            status_code=404
        )

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Process a user query (demo mode with mock responses)
    """
    logger.info(f"📨 Demo request: {request.query}")
    
    # Simulate processing time
    time.sleep(1)
    
    try:
        # Generate mock response
        response_text = get_mock_response(request.query)
        
        # Mock agent history
        agent_history = [
            "Supervisor Agent: Analyzed user intent",
            "Specialist Agent: Retrieved information",
            "Final Answer Agent: Formatted response"
        ]
        
        return ChatResponse(
            response=response_text,
            session_id=request.session_id or f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            agent_history=agent_history,
            requires_action=False
        )
        
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*70)
    print("🚀 Starting Hifadhi Demo Server")
    print("="*70)
    print("\n⚠️  DEMO MODE: Using mock responses")
    print("   For full functionality, configure OpenAI API key in .env")
    print("\n🌐 Access points:")
    print("  - Web UI:     http://localhost:8000/ui")
    print("  - API Docs:   http://localhost:8000/docs")
    print("\n" + "="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
