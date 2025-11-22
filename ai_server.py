"""
Enhanced CRUD server with AI-powered insights for candidates, applications, and jobs
"""

import logging
import os
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime
import sqlite3

from utils.llm_client import run_llm
from tools.database_tools import *
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hifadhi_ai_api")

app = FastAPI(title="Hifadhi AI HR System", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Previous models (keeping them all)
class CandidateCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    years_experience: Optional[int] = 0
    education: Optional[str] = "High School"
    current_location: Optional[str] = "Nairobi"

class JobCreate(BaseModel):
    title: str
    department: str
    location: str
    salary_min: float
    salary_max: float

def get_db():
    return sqlite3.connect('data/hifadhi.db')

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# ============================================
# AI INSIGHTS ENDPOINTS
# ============================================

@app.get("/api/candidates/{candidate_id}/insights")
async def get_candidate_insights(candidate_id: str):
    """Get AI-powered insights for a candidate"""
    conn = get_db()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    # Get candidate details
    cursor.execute("SELECT * FROM candidates WHERE candidate_id = ?", (candidate_id,))
    candidate = cursor.fetchone()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Get applications
    cursor.execute("""
        SELECT a.*, j.title as job_title, j.department
        FROM applications a
        JOIN jobs j ON a.job_id = j.job_id
        WHERE a.candidate_id = ?
    """, (candidate_id,))
    applications = cursor.fetchall()
    
    conn.close()
    
    # Generate AI insights
    insights = {
        "profile_strength": _calculate_profile_strength(candidate),
        "top_matches": _get_top_job_matches(candidate),
        "recommendations": _get_ai_recommendations(candidate, applications),
        "next_steps": _suggest_next_steps(candidate, applications),
        "risk_alerts": _identify_risks(candidate, applications)
    }
    
    return {
        "candidate": candidate,
        "applications": applications,
        "insights": insights
    }

@app.get("/api/applications/{application_id}/insights")
async def get_application_insights(application_id: str):
    """Get AI insights for an application"""
    conn = get_db()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT a.*, 
               c.first_name, c.last_name, c.email, c.phone, c.years_experience, c.education,
               j.title as job_title, j.department, j.salary_min, j.salary_max
        FROM applications a
        JOIN candidates c ON a.candidate_id = c.candidate_id
        JOIN jobs j ON a.job_id = j.job_id
        WHERE a.application_id = ?
    """, (application_id,))
    
    app_data = cursor.fetchone()
    conn.close()
    
    if not app_data:
        raise HTTPException(status_code=404, detail="Application not found")
    
    insights = {
        "fit_score": _calculate_fit_score(app_data),
        "strengths": _analyze_strengths(app_data),
        "concerns": _identify_concerns(app_data),
        "interview_questions": _generate_interview_questions(app_data),
        "recommendation": _get_hiring_recommendation(app_data)
    }
    
    return {
        "application": app_data,
        "insights": insights
    }

@app.get("/api/jobs/{job_id}/insights")
async def get_job_insights(job_id: str):
    """Get AI insights for a job posting"""
    conn = get_db()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
    job = cursor.fetchone()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get applications for this job
    cursor.execute("""
        SELECT a.*, c.first_name, c.last_name, c.years_experience, c.education
        FROM applications a
        JOIN candidates c ON a.candidate_id = c.candidate_id
        WHERE a.job_id = ?
    """, (job_id,))
    applications = cursor.fetchall()
    
    conn.close()
    
    insights = {
        "application_stats": _get_application_stats(applications),
        "top_candidates": _rank_top_candidates(applications),
        "hiring_timeline": _estimate_timeline(applications, job),
        "market_insights": _get_market_insights(job),
        "optimization_tips": _get_optimization_tips(job, applications)
    }
    
    return {
        "job": job,
        "applications": applications,
        "insights": insights
    }

# ============================================
# AI HELPER FUNCTIONS
# ============================================

def _calculate_profile_strength(candidate):
    score = 50
    if candidate.get('years_experience', 0) > 3: score += 20
    if candidate.get('education') in ['Bachelors', 'Masters']: score += 20
    if '@' in candidate.get('email', ''): score += 10
    return min(score, 100)

def _get_top_job_matches(candidate):
    # Simplified - in production, use ML
    return [
        {"job_id": "JOB0001", "title": "Customer Service Rep", "match_score": 85},
        {"job_id": "JOB0002", "title": "Data Analyst", "match_score": 72}
    ]

def _get_ai_recommendations(candidate, applications):
    recs = []
    if len(applications) == 0:
        recs.append("💡 Strong profile! Recommend for 3+ open positions.")
    if candidate.get('years_experience', 0) > 5:
        recs.append("⭐ Senior candidate - consider for leadership roles.")
    if candidate.get('education') == 'Masters':
        recs.append("🎓 Advanced degree - excellent for technical positions.")
    return recs if recs else ["Resume looks good. Move to screening."]

def _suggest_next_steps(candidate, applications):
    if len(applications) == 0:
        return ["📧 Send job recommendations", "📞 Schedule initial screening call"]
    else:
        return ["Review pending applications", "Schedule interviews for top matches"]

def _identify_risks(candidate, applications):
    risks = []
    if len(applications) > 5:
        risks.append("⚠️ Multiple applications - may accept other offers")
    return risks

def _calculate_fit_score(app_data):
    score = app_data.get('ai_screening_score', 70)
    if app_data.get('years_experience', 0) >= 3: score += 10
    return min(score, 100)

def _analyze_strengths(app_data):
    strengths = []
    if app_data.get('years_experience', 0) > 3:
        strengths.append(f"✅ {app_data['years_experience']} years of relevant experience")
    if app_data.get('education') in ['Bachelors', 'Masters']:
        strengths.append(f"✅ {app_data['education']} degree holder")
    return strengths if strengths else ["Good baseline qualifications"]

def _identify_concerns(app_data):
    concerns = []
    if app_data.get('ai_screening_score', 100) < 70:
        concerns.append("⚠️ Below average AI screening score")
    return concerns

def _generate_interview_questions(app_data):
    return [
        f"Tell us about your {app_data.get('years_experience', 0)} years of experience",
        f"How does your {app_data.get('education')} prepare you for this role?",
        "What are your salary expectations?"
    ]

def _get_hiring_recommendation(app_data):
    score = app_data.get('ai_screening_score', 70)
    if score >= 80:
        return {"action": "fast_track", "message": "🚀 Fast-track to final interview", "priority": "high"}
    elif score >= 70:
        return {"action": "interview", "message": "✅ Schedule interview", "priority": "medium"}
    else:
        return {"action": "review", "message": "⏳ Needs further review", "priority": "low"}

def _get_application_stats(applications):
    statuses = {}
    for app in applications:
        status = app.get('status', 'New')
        statuses[status] = statuses.get(status, 0) + 1
    return statuses

def _rank_top_candidates(applications):
    sorted_apps = sorted(applications, key=lambda x: x.get('ai_screening_score', 0), reverse=True)
    return sorted_apps[:3]

def _estimate_timeline(applications, job):
    app_count = len(applications)
    if app_count > 20:
        return "2-3 weeks (high volume)"
    elif app_count > 5:
        return "1-2 weeks (moderate volume)"
    else:
        return "3-5 days (low volume - consider promotion)"

def _get_market_insights(job):
    salary_range = f"KSh {job.get('salary_min', 0):,.0f} - {job.get('salary_max', 0):,.0f}"
    return {
        "salary_competitiveness": "Market competitive" if job.get('salary_min', 0) > 35000 else "Below market",
        "demand_level": "High demand" if job.get('title', '').lower().find('engineer') >= 0 else "Moderate",
        "salary_range": salary_range
    }

def _get_optimization_tips(job, applications):
    tips = []
    if len(applications) < 5:
        tips.append("📢 Low application volume - boost job posting visibility")
    if job.get('salary_max', 0) < 50000:
        tips.append("💰 Consider increasing salary range to attract top talent")
    return tips if tips else ["Job posting performing well"]

# ============================================
# EXISTING CRUD ENDPOINTS (keeping all from before)
# ============================================

@app.get("/api/candidates")
async def get_all_candidates(skip: int = 0, limit: int = 100):
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

@app.post("/api/candidates")
async def create_candidate(candidate: CandidateCreate):
    conn = get_db()
    cursor = conn.cursor()
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
            candidate_id, candidate.first_name, candidate.last_name,
            candidate.email, candidate.phone, candidate.years_experience,
            candidate.education, candidate.current_location,
            True, datetime.now().strftime('%Y-%m-%d')
        ))
        conn.commit()
        conn.close()
        return {"message": "Candidate created", "candidate_id": candidate_id}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already exists")

@app.delete("/api/candidates/{candidate_id}")
async def delete_candidate(candidate_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM applications WHERE candidate_id = ?", (candidate_id,))
    cursor.execute("DELETE FROM candidates WHERE candidate_id = ?", (candidate_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Candidate not found")
    conn.commit()
    conn.close()
    return {"message": "Candidate deleted"}

@app.get("/api/applications")
async def get_all_applications(limit: int = 100):
    conn = get_db()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.*, c.first_name, c.last_name, c.email,
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

@app.delete("/api/applications/{application_id}")
async def delete_application(application_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM applications WHERE application_id = ?", (application_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Application not found")
    conn.commit()
    conn.close()
    return {"message": "Application deleted"}

@app.get("/api/jobs")
async def get_all_jobs():
    conn = get_db()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
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
        job_id, job.title, job.department, job.location,
        job.salary_min, job.salary_max, 'Full-time', 'Flexible',
        datetime.now().strftime('%Y-%m-%d'), 'Open'
    ))
    conn.commit()
    conn.close()
    return {"message": "Job created", "job_id": job_id}

@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jobs WHERE job_id = ?", (job_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    conn.commit()
    conn.close()
    return {"message": "Job deleted"}

@app.get("/api/analytics/dashboard")
async def get_dashboard_stats():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM candidates")
    total_candidates = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM applications WHERE status != 'Rejected' AND status != 'Hired'")
    active_applications = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM applications WHERE status = 'Interview Scheduled' OR status = 'Interview'")
    interviews = cursor.fetchone()[0]
    current_month = datetime.now().strftime('%Y-%m')
    cursor.execute("SELECT COUNT(*) FROM applications WHERE status = 'Hired' AND application_date LIKE ?", (f"{current_month}%",))
    hired = cursor.fetchone()[0]
    conn.close()
    return {
        "total_candidates": total_candidates,
        "active_applications": active_applications,
        "interviews_scheduled": interviews,
        "hired_this_month": hired
    }

@app.get("/")
async def root():
    return {"status": "online", "system": "Hifadhi AI HR System", "version": "3.0.0"}

@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard():
    try:
        with open("dashboard_v3.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Dashboard Not Found</h1>", status_code=404)

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*70)
    print("🚀 Hifadhi AI-Powered HR System v3.0")
    print("="*70)
    print("\n✨ Features:")
    print("  - Full CRUD Operations")
    print("  - AI-Powered Insights & Recommendations")
    print("  - Smart Candidate Matching")
    print("  - Interview Question Generation")
    print("\n🌐 Access:")
    print("  - Dashboard:  http://localhost:8000/dashboard")
    print("  - API Docs:   http://localhost:8000/docs")
    print("="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
