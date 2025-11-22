"""
Database interaction tools for Hifadhi agents
"""

import sqlite3
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

def get_candidate_details(candidate_id: str) -> Dict[str, Any]:
    """Fetch candidate profile"""
    logger.info(f"🔍 Fetching candidate: {candidate_id}")
    conn = sqlite3.connect('data/hifadhi.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM candidates WHERE candidate_id = ?
    """, (candidate_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, result))
    
    return {"error": "Candidate not found"}


def get_job_details(job_id: str) -> Dict[str, Any]:
    """Fetch job posting details"""
    conn = sqlite3.connect('data/hifadhi.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM jobs WHERE job_id = ?
    """, (job_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, result))
    
    return {"error": "Job not found"}


def get_application_status(application_id: str = None, candidate_id: str = None) -> Dict[str, Any]:
    """Get application status"""
    conn = sqlite3.connect('data/hifadhi.db')
    cursor = conn.cursor()
    
    if application_id:
        cursor.execute("""
            SELECT a.*, j.title, c.first_name, c.last_name
            FROM applications a
            JOIN jobs j ON a.job_id = j.job_id
            JOIN candidates c ON a.candidate_id = c.candidate_id
            WHERE a.application_id = ?
        """, (application_id,))
    elif candidate_id:
        cursor.execute("""
            SELECT a.*, j.title
            FROM applications a
            JOIN jobs j ON a.job_id = j.job_id
            WHERE a.candidate_id = ?
            ORDER BY a.application_date DESC LIMIT 5
        """, (candidate_id,))
    
    results = cursor.fetchall()
    conn.close()
    
    if results:
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in results]
    
    return {"error": "No applications found"}


def get_interview_schedule(candidate_id: str = None, application_id: str = None) -> List[Dict[str, Any]]:
    """Get interview schedule"""
    conn = sqlite3.connect('data/hifadhi.db')
    cursor = conn.cursor()
    
    if application_id:
        cursor.execute("""
            SELECT * FROM interviews 
            WHERE application_id = ?
            ORDER BY interview_date DESC
        """, (application_id,))
    elif candidate_id:
        cursor.execute("""
            SELECT i.*, a.job_id
            FROM interviews i
            JOIN applications a ON i.application_id = a.application_id
            WHERE a.candidate_id = ?
            ORDER BY i.interview_date DESC LIMIT 5
        """, (candidate_id,))
    
    results = cursor.fetchall()
    conn.close()
    
    if results:
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in results]
    
    return []


def get_onboarding_tasks(candidate_id: str) -> List[Dict[str, Any]]:
    """Get onboarding checklist"""
    conn = sqlite3.connect('data/hifadhi.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM onboarding_tasks 
        WHERE candidate_id = ?
        ORDER BY due_date ASC
    """, (candidate_id,))
    
    results = cursor.fetchall()
    conn.close()
    
    if results:
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in results]
    
    return []


def get_compliance_status(candidate_id: str) -> List[Dict[str, Any]]:
    """Get compliance verification status"""
    conn = sqlite3.connect('data/hifadhi.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM compliance_records 
        WHERE candidate_id = ?
        ORDER BY verification_date DESC
    """, (candidate_id,))
    
    results = cursor.fetchall()
    conn.close()
    
    if results:
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in results]
    
    return []


def get_payroll_history(candidate_id: str) -> List[Dict[str, Any]]:
    """Get payment history"""
    conn = sqlite3.connect('data/hifadhi.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM payroll 
        WHERE candidate_id = ?
        ORDER BY payment_date DESC LIMIT 10
    """, (candidate_id,))
    
    results = cursor.fetchall()
    conn.close()
    
    if results:
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in results]
    
    return []
