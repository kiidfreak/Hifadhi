"""
Analytics and metrics calculation tools
"""

import sqlite3
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def get_hiring_metrics(time_period: str = "last_30_days") -> Dict[str, Any]:
    """
    Calculate hiring metrics for specified time period
    
    Args:
        time_period: Time period (last_7_days, last_30_days, last_quarter)
    
    Returns:
        Dictionary with hiring metrics
    """
    logger.info(f"📊 Calculating hiring metrics for: {time_period}")
    
    # Calculate date range
    end_date = datetime.now()
    if time_period == "last_7_days":
        start_date = end_date - timedelta(days=7)
    elif time_period == "last_30_days":
        start_date = end_date - timedelta(days=30)
    elif time_period == "last_quarter":
        start_date = end_date - timedelta(days=90)
    else:
        start_date = end_date - timedelta(days=30)
    
    conn = sqlite3.connect('data/hifadhi.db')
    
    # Total applications
    total_apps = pd.read_sql_query(f"""
        SELECT COUNT(*) as count 
        FROM applications 
        WHERE application_date >= '{start_date.strftime('%Y-%m-%d')}'
    """, conn).iloc[0]['count']
    
    # Hired count
    hired = pd.read_sql_query(f"""
        SELECT COUNT(*) as count 
        FROM applications 
        WHERE status = 'Hired' 
        AND application_date >= '{start_date.strftime('%Y-%m-%d')}'
    """, conn).iloc[0]['count']
    
    # Average time to hire (application to hired status)
    time_to_hire = pd.read_sql_query(f"""
        SELECT AVG(JULIANDAY(i.interview_date) - JULIANDAY(a.application_date)) as avg_days
        FROM applications a
        LEFT JOIN interviews i ON a.application_id = i.application_id
        WHERE a.status = 'Hired'
        AND a.application_date >= '{start_date.strftime('%Y-%m-%d')}'
    """, conn).iloc[0]['avg_days']
    
    # Conversion rates
    interview_rate = pd.read_sql_query(f"""
        SELECT 
            COUNT(DISTINCT i.application_id) * 100.0 / COUNT(DISTINCT a.application_id) as rate
        FROM applications a
        LEFT JOIN interviews i ON a.application_id = i.application_id
        WHERE a.application_date >= '{start_date.strftime('%Y-%m-%d')}'
    """, conn).iloc[0]['rate']
    
    conn.close()
    
    metrics = {
        "time_period": time_period,
        "start_date": start_date.strftime('%Y-%m-%d'),
        "end_date": end_date.strftime('%Y-%m-%d'),
        "total_applications": int(total_apps),
        "total_hired": int(hired),
        "conversion_rate": round((hired / total_apps * 100) if total_apps > 0 else 0, 2),
        "average_time_to_hire_days": round(time_to_hire, 1) if time_to_hire else None,
        "interview_conversion_rate": round(interview_rate, 2) if interview_rate else 0,
        "estimated_cost_per_hire": 15000  # Placeholder - could calculate from actual costs
    }
    
    logger.info(f"✅ Metrics calculated: {metrics}")
    
    return metrics


def get_pipeline_analytics(job_id: str = None) -> Dict[str, Any]:
    """
    Get hiring pipeline funnel analytics
    
    Args:
        job_id: Optional specific job to analyze
    
    Returns:
        Pipeline funnel data
    """
    logger.info(f"📊 Calculating pipeline analytics for job: {job_id or 'all'}")
    
    conn = sqlite3.connect('data/hifadhi.db')
    
    query = """
        SELECT 
            status,
            COUNT(*) as count,
            AVG(ai_screening_score) as avg_score
        FROM applications
    """
    
    if job_id:
        query += f" WHERE job_id = '{job_id}'"
    
    query += " GROUP BY status"
    
    pipeline_df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Convert to funnel format
    funnel = {}
    for _, row in pipeline_df.iterrows():
        funnel[row['status']] = {
            "count": int(row['count']),
            "avg_score": round(row['avg_score'], 1) if row['avg_score'] else None
        }
    
    total = sum([v['count'] for v in funnel.values()])
    
    result = {
        "job_id": job_id or "all_jobs",
        "total_applications": total,
        "funnel_stages": funnel,
        "drop_off_analysis": _calculate_dropoff(funnel)
    }
    
    logger.info(f"✅ Pipeline analytics calculated")
    
    return result


def _calculate_dropoff(funnel: Dict[str, Dict]) -> Dict[str, float]:
    """Calculate drop-off rates between stages"""
    stages = ["New", "Screening", "Interview", "Offer", "Hired"]
    dropoff = {}
    
    for i in range(len(stages) - 1):
        current = funnel.get(stages[i], {}).get('count', 0)
        next_stage = funnel.get(stages[i+1], {}).get('count', 0)
        
        if current > 0:
            dropoff[f"{stages[i]}_to_{stages[i+1]}"] = round(
                (current - next_stage) / current * 100, 2
            )
    
    return dropoff


def get_top_performing_jobs(limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get top performing job postings by application volume
    
    Args:
        limit: Number of top jobs to return
    
    Returns:
        List of top jobs with metrics
    """
    conn = sqlite3.connect('data/hifadhi.db')
    
    query = f"""
        SELECT 
            j.job_id,
            j.title,
            j.department,
            COUNT(a.application_id) as total_applications,
            AVG(a.ai_screening_score) as avg_score,
            SUM(CASE WHEN a.status = 'Hired' THEN 1 ELSE 0 END) as hired_count
        FROM jobs j
        LEFT JOIN applications a ON j.job_id = a.job_id
        WHERE j.status = 'Open'
        GROUP BY j.job_id, j.title, j.department
        ORDER BY total_applications DESC
        LIMIT {limit}
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df.to_dict('records')
