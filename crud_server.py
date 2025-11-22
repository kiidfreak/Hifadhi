"""
Complete CRUD API for Hifadhi HR Management System
"""

import logging
import os
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime
import sqlite3
import json

from utils.llm_client import run_llm
from tools.database_tools import *
from tools.analytics_tools import get_hiring_metrics, get_pipeline_analytics
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hifadhi_crud_api")

app = FastAPI(
    title="Hifadhi HR Management API",
    description="Complete CRUD API for HR Management",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# PYDANTIC MODELS
# ============================================

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    agent_history: list
    requires_action: bool = False

class CandidateCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    years_experience: Optional[int] = 0
    education: Optional[str] = "High School"
    current_location: Optional[str] = "Nairobi"

class CandidateUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    years_experience: Optional[int] = None
    education: Optional[str] = None
    current_location: Optional[str] = None

class ApplicationCreate(BaseModel):
    candidate_id: str
    job_id: str

class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    ai_screening_score: Optional[int] = None
    notes: Optional[str] = None

class JobCreate(BaseModel):
    title: str
    department: str
    location: str
    salary_min: float
    salary_max: float

# ============================================
# DATABASE HELPER FUNCTIONS
# ============================================

def get_db():
    return sqlite3.connect('data/hifadhi.db')

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# ============================================
# CANDIDATES CRUD
# ============================================

@app.get("/api/candidates")
async def get_all_candidates(skip: int = 0, limit: int = 100):
    """Get all candidates with pagination"""
    conn = get_db()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.*, COUNT(a.application_id) as application_count
        FROM candidates c
        LEFT JOIN applications a ON c.candidate_id = a.candidate_id
        GROUP BY c.candidate_id
        ORDER BY c.candidate_id DESC
        LIMIT ? OFFSET ?
    """, (limit, skip))
    
    candidates = cursor.fetchall()
    conn.close()
    
    return {"candidates": candidates, "count": len(candidates)}

@app.get("/api/candidates/{candidate_id}")
async def get_candidate(candidate_id: str):
    """Get single candidate details"""
    conn = get_db()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM candidates WHERE candidate_id = ?", (candidate_id,))
    candidate = cursor.fetchone()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Get applications
    cursor.execute("""
        SELECT a.*, j.title as job_title
        FROM applications a
        JOIN jobs j ON a.job_id = j.job_id
        WHERE a.candidate_id = ?
    """, (candidate_id,))
    applications = cursor.fetchall()
    
    conn.close()
    
    return {"candidate": candidate, "applications": applications}

@app.post("/api/candidates")
async def create_candidate(candidate: CandidateCreate):
    """Create new candidate"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Generate candidate ID
    cursor.execute("SELECT COUNT(*) FROM candidates")
    count = cursor.fetchone()[0]
    candidate_id = f"CAND{str(count + 1).zfill(5)}"
    
    try:
        cursor.execute("""
            INSERT INTO candidates (
                candidate_id, first_name, last_name, email, phone,
                years_experience, education, current_location,
                willing_to_relocate, available_start_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            candidate_id,
            candidate.first_name,
            candidate.last_name,
            candidate.email,
            candidate.phone,
            candidate.years_experience,
            candidate.education,
            candidate.current_location,
            True,  # willing_to_relocate
            datetime.now().strftime('%Y-%m-%d')  # available_start_date
        ))
        
        conn.commit()
        conn.close()
        
        return {"message": "Candidate created", "candidate_id": candidate_id}
        
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already exists")

@app.put("/api/candidates/{candidate_id}")
async def update_candidate(candidate_id: str, updates: CandidateUpdate):
    """Update candidate information"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Build dynamic update query
    update_fields = []
    values = []
    
    for field, value in updates.dict(exclude_unset=True).items():
        if value is not None:
            update_fields.append(f"{field} = ?")
            values.append(value)
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    values.append(candidate_id)
    query = f"UPDATE candidates SET {', '.join(update_fields)} WHERE candidate_id = ?"
    
    cursor.execute(query, values)
    
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    conn.commit()
    conn.close()
    
    return {"message": "Candidate updated", "candidate_id": candidate_id}

@app.delete("/api/candidates/{candidate_id}")
async def delete_candidate(candidate_id: str):
    """Delete candidate and all associated data"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Delete applications first (foreign key)
    cursor.execute("DELETE FROM applications WHERE candidate_id = ?", (candidate_id,))
    
    # Delete candidate
    cursor.execute("DELETE FROM candidates WHERE candidate_id = ?", (candidate_id,))
    
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    conn.commit()
    conn.close()
    
    return {"message": "Candidate deleted", "candidate_id": candidate_id}

# ============================================
# APPLICATIONS CRUD
# ============================================

@app.get("/api/applications")
async def get_all_applications(status: Optional[str] = None, limit: int = 100):
    """Get all applications with optional status filter"""
    conn = get_db()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    if status:
        cursor.execute("""
            SELECT a.*, 
                   c.first_name, c.last_name, c.email,
                   j.title as job_title, j.department
            FROM applications a
            JOIN candidates c ON a.candidate_id = c.candidate_id
            JOIN jobs j ON a.job_id = j.job_id
            WHERE a.status = ?
            ORDER BY a.application_date DESC
            LIMIT ?
        """, (status, limit))
    else:
        cursor.execute("""
            SELECT a.*, 
                   c.first_name, c.last_name, c.email,
                   j.title as job_title, j.department
            FROM applications a
            JOIN candidates c ON a.candidate_id = c.candidate_id
            JOIN jobs j ON a.job_id = j.job_id
            ORDER BY a.application_date DESC
            LIMIT ?
        """, (limit,))
    
    applications = cursor.fetchall()
    conn.close()
    
    return {"applications": applications, "count": len(applications)}

@app.post("/api/applications")
async def create_application(application: ApplicationCreate):
    """Submit new application"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Generate application ID
    cursor.execute("SELECT COUNT(*) FROM applications")
    count = cursor.fetchone()[0]
    application_id = f"APP{str(count + 1).zfill(5)}"
    
    try:
        cursor.execute("""
            INSERT INTO applications (
                application_id, candidate_id, job_id, application_date, status
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            application_id,
            application.candidate_id,
            application.job_id,
            datetime.now().strftime('%Y-%m-%d'),
            'Applied'
        ))
        
        conn.commit()
        conn.close()
        
        return {"message": "Application submitted", "application_id": application_id}
        
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/applications/{application_id}")
async def update_application(application_id: str, updates: ApplicationUpdate):
    """Update application status"""
    conn = get_db()
    cursor = conn.cursor()
    
    update_fields = []
    values = []
    
    for field, value in updates.dict(exclude_unset=True).items():
        if value is not None:
            update_fields.append(f"{field} = ?")
            values.append(value)
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    values.append(application_id)
    query = f"UPDATE applications SET {', '.join(update_fields)} WHERE application_id = ?"
    
    cursor.execute(query, values)
    
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Application not found")
    
    conn.commit()
    conn.close()
    
    return {"message": "Application updated", "application_id": application_id}

@app.delete("/api/applications/{application_id}")
async def delete_application(application_id: str):
    """Delete application"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM applications WHERE application_id = ?", (application_id,))
    
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Application not found")
    
    conn.commit()
    conn.close()
    
    return {"message": "Application deleted"}

# ============================================
# JOBS CRUD
# ============================================

@app.get("/api/jobs")
async def get_all_jobs(status: Optional[str] = None):
    """Get all job postings"""
    conn = get_db()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    if status:
        cursor.execute("""
            SELECT j.*, COUNT(a.application_id) as application_count
            FROM jobs j
            LEFT JOIN applications a ON j.job_id = a.job_id
            WHERE j.status = ?
            GROUP BY j.job_id
            ORDER BY j.posted_date DESC
        """, (status,))
    else:
        cursor.execute("""
            SELECT j.*, COUNT(a.application_id) as application_count
            FROM jobs j
            LEFT JOIN applications a ON j.job_id = a.job_id
            GROUP BY j.job_id
            ORDER BY j.posted_date DESC
        """)
    
    jobs = cursor.fetchall()
    conn.close()
    
    return {"jobs": jobs, "count": len(jobs)}

@app.post("/api/jobs")
async def create_job(job: JobCreate):
    """Create new job posting"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM jobs")
    count = cursor.fetchone()[0]
    job_id = f"JOB{str(count + 1).zfill(5)}"
    
    cursor.execute("""
        INSERT INTO jobs (
            job_id, title, department, location,
            salary_min, salary_max, employment_type, shift, posted_date, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        job_id,
        job.title,
        job.department,
        job.location,
        job.salary_min,
        job.salary_max,
        'Full-time',  # employment_type
        'Flexible',  # shift
        datetime.now().strftime('%Y-%m-%d'),
        'Open'
    ))
    
    conn.commit()
    conn.close()
    
    return {"message": "Job created", "job_id": job_id}

@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete job posting"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM jobs WHERE job_id = ?", (job_id,))
    
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    
    conn.commit()
    conn.close()
    
    return {"message": "Job deleted"}

# ============================================
# ANALYTICS
# ============================================

@app.get("/api/analytics/dashboard")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Total candidates
    cursor.execute("SELECT COUNT(*) FROM candidates")
    total_candidates = cursor.fetchone()[0]
    
    # Active applications
    cursor.execute("SELECT COUNT(*) FROM applications WHERE status != 'Rejected' AND status != 'Hired'")
    active_applications = cursor.fetchone()[0]
    
    # Interviews scheduled
    cursor.execute("SELECT COUNT(*) FROM applications WHERE status = 'Interview Scheduled'")
    interviews = cursor.fetchone()[0]
    
    # Hired this month
    current_month = datetime.now().strftime('%Y-%m')
    cursor.execute("""
        SELECT COUNT(*) FROM applications 
        WHERE status = 'Hired' AND application_date LIKE ?
    """, (f"{current_month}%",))
    hired = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "total_candidates": total_candidates,
        "active_applications": active_applications,
        "interviews_scheduled": interviews,
        "hired_this_month": hired
    }

# ============================================
# CHAT / AI ASSISTANT
# ============================================

def process_query_simple(query: str) -> str:
    """Process query using AI"""
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_application_status",
                "description": "Get status of a job application",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "application_id": {"type": "string"}
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_hiring_metrics",
                "description": "Get hiring metrics",
                "parameters": {"type": "object", "properties": {}}
            }
        }
    ]
    
    prompt = f"""You are Hifadhi, an AI HR assistant.

User Query: {query}

Provide helpful, professional responses with specific data."""

    try:
        response = run_llm(
            prompt=prompt,
            tools=tools,
            tool_functions={
                "get_application_status": get_application_status,
                "get_hiring_metrics": get_hiring_metrics,
            }
        )
        return response
    except Exception as e:
        return f"Error: {str(e)}"

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """AI Chat endpoint"""
    response_text = process_query_simple(request.query)
    
    return ChatResponse(
        response=response_text,
        session_id=request.session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        agent_history=["AI processed query"],
        requires_action=False
    )

# ============================================
# UI SERVING
# ============================================

@app.get("/")
async def root():
    return {
        "status": "online",
        "system": "Hifadhi HR Management System",
        "version": "2.0.0",
        "features": ["Full CRUD", "AI Assistant", "Analytics"]
    }

@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard():
    try:
        with open("dashboard_v2.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Dashboard Not Found</h1>", status_code=404)

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*70)
    print("🚀 Hifadhi HR Management System v2.0")
    print("="*70)
    print("\n✨ Features:")
    print("  - Full CRUD Operations (Create, Read, Update, Delete)")
    print("  - AI-Powered Assistant")
    print("  - Real-time Analytics")
    print("  - Modern Dashboard")
    print("\n🌐 Access:")
    print("  - Dashboard:  http://localhost:8000/dashboard")
    print("  - API Docs:   http://localhost:8000/docs")
    print("="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
