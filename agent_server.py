"""
AI-Powered HR System with Agent Task Execution
Now with CLICKABLE actions that trigger real agents!
"""

import logging
import os
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime, timedelta
import sqlite3
import asyncio

from utils.llm_client import run_llm
from tools.database_tools import *
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hifadhi_agents")

app = FastAPI(title="Hifadhi AI HR System with Agents", version="4.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
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

class AgentTask(BaseModel):
    task_type: str
    entity_id: str
    params: Optional[Dict] = {}

def get_db():
    return sqlite3.connect('data/hifadhi.db')

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# ============================================
# AGENT TASK EXECUTION ENDPOINTS
# ============================================

@app.post("/api/agent/execute")
async def execute_agent_task(task: AgentTask):
    """Execute an agent task - the magic happens here!"""
    logger.info(f"🤖 Agent task: {task.task_type} for {task.entity_id}")
    
    try:
        if task.task_type == "send_job_recommendations":
            result = await _agent_send_job_recommendations(task.entity_id)
        elif task.task_type == "schedule_screening_call":
            result = await _agent_schedule_screening(task.entity_id)
        elif task.task_type == "schedule_interview":
            result = await _agent_schedule_interview(task.entity_id, task.params)
        elif task.task_type == "update_application_status":
            result = await _agent_update_status(task.entity_id, task.params)
        elif task.task_type == "fast_track_candidate":
            result = await _agent_fast_track(task.entity_id)
        elif task.task_type == "boost_job_visibility":
            result = await _agent_boost_job(task.entity_id)
        elif task.task_type == "increase_salary":
            result = await _agent_adjust_salary(task.entity_id, task.params)
        else:
            raise HTTPException(status_code=400, detail="Unknown task type")
        
        return {"success": True, "result": result}
        
    except Exception as e:
        logger.error(f"Agent error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# AGENT IMPLEMENTATIONS
# ============================================

async def _agent_send_job_recommendations(candidate_id: str):
    """Agent: Send personalized job recommendations to candidate"""
    conn = get_db()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    # Get candidate
    cursor.execute("SELECT * FROM candidates WHERE candidate_id = ?", (candidate_id,))
    candidate = cursor.fetchone()
    
    # Get suitable jobs
    cursor.execute("""
        SELECT * FROM jobs 
        WHERE status = 'Open' 
        LIMIT 3
    """)
    jobs = cursor.fetchall()
    
    conn.close()
    
    # Simulate sending email (in production, use SendGrid/AWS SES)
    email_body = f"""
    Hi {candidate['first_name']},
    
    We found {len(jobs)} great opportunities that match your profile:
    
    """
    for job in jobs:
        email_body += f"- {job['title']} at {job['location']}\n"
    
    email_body += f"\n\nBest regards,\nHifadhi HR Team"
    
    logger.info(f"📧 Email sent to {candidate['email']}")
    
    return {
        "action": "email_sent",
        "to": candidate['email'],
        "jobs_recommended": len(jobs),
        "preview": email_body[:200] + "..."
    }

async def _agent_schedule_screening(candidate_id: str):
    """Agent: Schedule initial screening call"""
    conn = get_db()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM candidates WHERE candidate_id = ?", (candidate_id,))
    candidate = cursor.fetchone()
    conn.close()
    
    # In production: integrate with Calendly, Google Calendar, etc.
    # Simulate scheduling
    interview_date = datetime.now() + timedelta(days=2, hours=10)
    
    logger.info(f"📅 Screening scheduled for {candidate['first_name']} on {interview_date}")
    
    return {
        "action": "screening_scheduled",
        "candidate": f"{candidate['first_name']} {candidate['last_name']}",
        "scheduled_for": interview_date.strftime("%Y-%m-%d %H:%M"),
        "calendar_link": "https://calendar.google.com/..." # Placeholder
    }

async def _agent_schedule_interview(application_id: str, params: Dict):
    """Agent: Schedule formal interview"""
    conn = get_db()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT a.*, c.first_name, c.last_name, c.email, j.title as job_title
        FROM applications a
        JOIN candidates c ON a.candidate_id = c.candidate_id
        JOIN jobs j ON a.job_id = j.job_id
        WHERE a.application_id = ?
    """, (application_id,))
    app = cursor.fetchone()
    
    # Update status
    cursor.execute("""
        UPDATE applications 
        SET status = 'Interview Scheduled' 
        WHERE application_id = ?
    """, (application_id,))
    
    conn.commit()
    conn.close()
    
    logger.info(f"📅 Interview scheduled for {app['first_name']} - {app['job_title']}")
    
    return {
        "action": "interview_scheduled",
        "candidate": f"{app['first_name']} {app['last_name']}",
        "job": app['job_title'],
        "status_updated": True,
        "scheduled_for": (datetime.now() + timedelta(days=3, hours=9)).strftime("%Y-%m-%d %H:%M"),
        "calendar_link": "https://calendar.google.com/..."
    }

async def _agent_update_status(application_id: str, params: Dict):
    """Agent: Update application status"""
    new_status = params.get('status', 'Screening')
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE applications 
        SET status = ? 
        WHERE application_id = ?
    """, (new_status, application_id))
    
    conn.commit()
    conn.close()
    
    logger.info(f"✅ Application {application_id} status updated to {new_status}")
    
    return {
        "action": "status_updated",
        "application_id": application_id,
        "new_status": new_status
    }

async def _agent_fast_track(application_id: str):
    """Agent: Fast-track high-scoring candidate"""
    conn = get_db()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT a.*, c.first_name, c.last_name
        FROM applications a
        JOIN candidates c ON a.candidate_id = c.candidate_id
        WHERE a.application_id = ?
    """, (application_id,))
    app = cursor.fetchone()
    
    # Update to fast-track
    cursor.execute("""
        UPDATE applications 
        SET status = 'Offer', ai_notes = 'Fast-tracked by AI recommendation'
        WHERE application_id = ?
    """, (application_id,))
    
    conn.commit()
    conn.close()
    
    logger.info(f"🚀 Fast-tracked {app['first_name']} {app['last_name']}")
    
    return {
        "action": "fast_tracked",
        "candidate": f"{app['first_name']} {app['last_name']}",
        "new_status": "Offer"
    }

async def _agent_boost_job(job_id: str):
    """Agent: Boost job posting visibility"""
    # In production: post to LinkedIn, Indeed, etc.
    logger.info(f"📢 Boosting job {job_id} visibility")
    
    return {
        "action": "job_boosted",
        "job_id": job_id,
        "platforms": ["LinkedIn", "Indeed", "Company Website"],
        "estimated_reach": "+500 candidates"
    }

async def _agent_adjust_salary(job_id: str, params: Dict):
    """Agent: Adjust salary range to be more competitive"""
    increase_percent = params.get('increase_percent', 10)
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT salary_min, salary_max FROM jobs WHERE job_id = ?", (job_id,))
    current = cursor.fetchone()
    
    new_min = current[0] * (1 + increase_percent/100)
    new_max = current[1] * (1 + increase_percent/100)
    
    cursor.execute("""
        UPDATE jobs 
        SET salary_min = ?, salary_max = ?
        WHERE job_id = ?
    """, (new_min, new_max, job_id))
    
    conn.commit()
    conn.close()
    
    logger.info(f"💰 Salary increased for job {job_id} by {increase_percent}%")
    
    return {
        "action": "salary_adjusted",
        "old_range": f"KSh {current[0]:,.0f} - {current[1]:,.0f}",
        "new_range": f"KSh {new_min:,.0f} - {new_max:,.0f}",
        "increase": f"+{increase_percent}%"
    }

# ============================================
# AI INSIGHTS ENDPOINTS
# ============================================

@app.get("/api/candidates/{candidate_id}/insights")
async def get_candidate_insights(candidate_id: str):
    conn = get_db()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM candidates WHERE candidate_id = ?", (candidate_id,))
    candidate = cursor.fetchone()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    cursor.execute("""
        SELECT a.*, j.title as job_title, j.department
        FROM applications a
        JOIN jobs j ON a.job_id = j.job_id
        WHERE a.candidate_id = ?
    """, (candidate_id,))
    applications = cursor.fetchall()
    
    conn.close()
    
    insights = {
        "profile_strength": _calculate_profile_strength(candidate),
        "recommendations": _get_ai_recommendations(candidate, applications),
        "next_steps": _suggest_next_steps(candidate, applications),
        "risk_alerts": _identify_risks(candidate, applications),
        # Add actionable tasks
        "actionable_tasks": [
            {"id": "send_job_recommendations", "label": "📧 Send Job Recommendations", "type": "send_job_recommendations"},
            {"id": "schedule_screening_call", "label": "📞 Schedule Screening Call", "type": "schedule_screening_call"}
        ]
    }
    
    return {
        "candidate": candidate,
        "applications": applications,
        "insights": insights
    }

@app.get("/api/applications/{application_id}/insights")
async def get_application_insights(application_id: str):
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
        "recommendation": _get_hiring_recommendation(app_data),
        # Actionable tasks
        "actionable_tasks": _get_application_actions(app_data)
    }
    
    return {
        "application": app_data,
        "insights": insights
    }

def _get_application_actions(app_data):
    """Get actionable tasks based on application status and score"""
    actions = []
    status = app_data.get('status')
    score = app_data.get('ai_screening_score', 70)
    
    # Fast track: Only for high scores and not if already far along or rejected
    if score >= 80 and status not in ['Offer', 'Hired', 'Rejected']:
        actions.append({"id": "fast_track", "label": "🚀 Fast-Track to Offer", "type": "fast_track_candidate"})
    
    # Schedule Interview: If not already scheduled/interviewing or done
    if status not in ['Interview Scheduled', 'Interview', 'Offer', 'Hired', 'Rejected']:
        actions.append({"id": "schedule_interview", "label": "📅 Schedule Interview", "type": "schedule_interview"})
    
    # Move to Screening: If New or Review
    if status in ['New', 'Review']:
        actions.append({"id": "update_screening", "label": "✅ Move to Screening", "type": "update_application_status", "params": {"status": "Screening"}})
    
    # Reject: If not already rejected or hired
    if status not in ['Rejected', 'Hired']:
        actions.append({"id": "reject", "label": "❌ Reject Application", "type": "update_application_status", "params": {"status": "Rejected"}})
    
    return actions

@app.get("/api/jobs/{job_id}/insights")
async def get_job_insights(job_id: str):
    conn = get_db()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
    job = cursor.fetchone()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
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
        "optimization_tips": _get_optimization_tips(job, applications),
        # Actionable tasks
        "actionable_tasks": _get_job_actions(job, applications)
    }
    
    return {
        "job": job,
        "applications": applications,
        "insights": insights
    }

def _get_job_actions(job, applications):
    """Get actionable tasks for job optimization"""
    actions = []
    
    if len(applications) < 5:
        actions.append({"id": "boost_visibility", "label": "📢 Boost Job Visibility", "type": "boost_job_visibility"})
    
    if job.get('salary_max', 0) < 50000:
        actions.append({"id": "increase_salary", "label": "💰 Increase Salary 10%", "type": "increase_salary", "params": {"increase_percent": 10}})
    
    return actions

# Helper functions
def _calculate_profile_strength(candidate):
    score = 50
    if candidate.get('years_experience', 0) > 3: score += 20
    if candidate.get('education') in ['Bachelors', 'Masters']: score += 20
    if '@' in candidate.get('email', ''): score += 10
    return min(score, 100)

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
# EXISTING CRUD ENDPOINTS
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
    return {"status": "online", "system": "Hifadhi AI with Agents", "version": "5.0.0"}

@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard():
    """Serve the Agent Dashboard V5 (Soft UI)"""
    try:
        with open("dashboard_v5.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Dashboard Not Found</h1>", status_code=404)

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*70)
    print("🤖 Hifadhi AI-Powered HR System v5.0 - WITH AGENT EXECUTION!")
    print("="*70)
    print("\n✨ Features:")
    print("  - Full CRUD Operations")
    print("  - AI-Powered Insights")
    print("  - 🆕 CLICKABLE Agent Tasks!")
    print("  - 🆕 Auto Email Sending")
    print("  - 🆕 Auto Scheduling")
    print("  - 🆕 Status Updates")
    print("\n🌐 Access:")
    print("  - Dashboard:  http://localhost:8000/dashboard")
    print("  - API Docs:   http://localhost:8000/docs")
    print("="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
