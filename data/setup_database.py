"""
Database schema for Hifadhi multi-agent HR system
Tables: candidates, jobs, interviews, onboarding, compliance, payroll
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import random
import os

def create_hifadhi_database():
    """Create SQLite database with HR-specific tables"""
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    conn = sqlite3.connect('data/hifadhi.db')
    cursor = conn.cursor()
    
    # Drop existing tables
    cursor.executescript("""
        DROP TABLE IF EXISTS payroll;
        DROP TABLE IF EXISTS compliance_records;
        DROP TABLE IF EXISTS onboarding_tasks;
        DROP TABLE IF EXISTS interviews;
        DROP TABLE IF EXISTS applications;
        DROP TABLE IF EXISTS candidates;
        DROP TABLE IF EXISTS jobs;
    """)
    
    # Create tables
    cursor.executescript("""
        -- Jobs Table
        CREATE TABLE jobs (
            job_id VARCHAR(20) PRIMARY KEY,
            title VARCHAR(100),
            department VARCHAR(50),
            location VARCHAR(50),
            salary_min DECIMAL(10,2),
            salary_max DECIMAL(10,2),
            employment_type VARCHAR(20),
            shift VARCHAR(20),
            status VARCHAR(20),
            posted_date DATE,
            closing_date DATE
        );
        
        -- Candidates Table
        CREATE TABLE candidates (
            candidate_id VARCHAR(20) PRIMARY KEY,
            first_name VARCHAR(50),
            last_name VARCHAR(50),
            email VARCHAR(100),
            phone VARCHAR(20),
            years_experience INTEGER,
            education VARCHAR(50),
            current_location VARCHAR(50),
            willing_to_relocate BOOLEAN,
            available_start_date DATE
        );
        
        -- Applications Table
        CREATE TABLE applications (
            application_id VARCHAR(20) PRIMARY KEY,
            candidate_id VARCHAR(20),
            job_id VARCHAR(20),
            application_date DATE,
            status VARCHAR(30),
            ai_screening_score INTEGER,
            ai_notes TEXT,
            FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id),
            FOREIGN KEY (job_id) REFERENCES jobs(job_id)
        );
        
        -- Interviews Table
        CREATE TABLE interviews (
            interview_id VARCHAR(20) PRIMARY KEY,
            application_id VARCHAR(20),
            interview_date DATETIME,
            interview_type VARCHAR(30),
            interviewer VARCHAR(100),
            status VARCHAR(20),
            feedback TEXT,
            rating INTEGER,
            FOREIGN KEY (application_id) REFERENCES applications(application_id)
        );
        
        -- Onboarding Tasks Table
        CREATE TABLE onboarding_tasks (
            task_id VARCHAR(20) PRIMARY KEY,
            candidate_id VARCHAR(20),
            task_name VARCHAR(100),
            task_category VARCHAR(30),
            due_date DATE,
            status VARCHAR(20),
            completed_date DATE,
            assignee VARCHAR(100),
            FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id)
        );
        
        -- Compliance Records Table
        CREATE TABLE compliance_records (
            record_id VARCHAR(20) PRIMARY KEY,
            candidate_id VARCHAR(20),
            document_type VARCHAR(50),
            document_number VARCHAR(100),
            verification_status VARCHAR(20),
            verification_date DATE,
            expiry_date DATE,
            notes TEXT,
            FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id)
        );
        
        -- Payroll Table
        CREATE TABLE payroll (
            payroll_id VARCHAR(20) PRIMARY KEY,
            candidate_id VARCHAR(20),
            payment_type VARCHAR(30),
            amount DECIMAL(10,2),
            payment_date DATE,
            payment_method VARCHAR(30),
            status VARCHAR(20),
            transaction_id VARCHAR(100),
            mpesa_phone VARCHAR(20),
            FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id)
        );
    """)
    
    conn.commit()
    print("✅ Database schema created successfully!")
    return conn


def generate_sample_hr_data(conn, num_candidates=500):
    """Generate realistic HR sample data"""
    
    # Sample data pools
    first_names = ["John", "Jane", "Robert", "Maria", "David", "Lisa", "Michael", "Sarah", 
                   "James", "Emily", "William", "Emma", "Joseph", "Olivia", "Charles", "Ava"]
    
    last_names = ["Kamau", "Wanjiru", "Ochieng", "Akinyi", "Mwangi", "Nyambura", "Otieno", 
                  "Chebet", "Kipchoge", "Wangari", "Omondi", "Njeri", "Kimani", "Adhiambo"]
    
    job_titles = [
        "Customer Service Representative",
        "Call Center Agent",
        "Data Labeling Specialist",
        "Quality Assurance Agent",
        "Team Leader - Customer Support",
        "Technical Support Agent",
        "Back Office Coordinator"
    ]
    
    # Generate Jobs
    jobs = []
    for i in range(1, 21):
        title = random.choice(job_titles)
        jobs.append({
            'job_id': f'JOB{str(i).zfill(4)}',
            'title': title,
            'department': 'Customer Support' if 'Support' in title else 'Operations',
            'location': random.choice(['Nairobi', 'Mombasa', 'Kisumu']),
            'salary_min': random.randint(30000, 40000),
            'salary_max': random.randint(45000, 60000),
            'employment_type': random.choice(['Full-time', 'Contract', 'Part-time']),
            'shift': random.choice(['Morning', 'Evening', 'Night', 'Flexible']),
            'status': random.choice(['Open', 'Open', 'Open', 'Closed']),
            'posted_date': datetime.now() - timedelta(days=random.randint(1, 90)),
            'closing_date': datetime.now() + timedelta(days=random.randint(10, 60))
        })
    
    df_jobs = pd.DataFrame(jobs)
    df_jobs.to_sql('jobs', conn, if_exists='append', index=False)
    
    # Generate Candidates
    candidates = []
    for i in range(1, num_candidates + 1):
        candidates.append({
            'candidate_id': f'CAND{str(i).zfill(5)}',
            'first_name': random.choice(first_names),
            'last_name': random.choice(last_names),
            'email': f'candidate{i}@email.com',
            'phone': f'0{random.randint(700000000, 799999999)}',
            'years_experience': random.randint(0, 10),
            'education': random.choice(['High School', 'Diploma', 'Bachelors', 'Masters']),
            'current_location': random.choice(['Nairobi', 'Mombasa', 'Kisumu', 'Eldoret']),
            'willing_to_relocate': random.choice([True, False]),
            'available_start_date': datetime.now() + timedelta(days=random.randint(7, 60))
        })
    
    df_candidates = pd.DataFrame(candidates)
    df_candidates.to_sql('candidates', conn, if_exists='append', index=False)
    
    # Generate Applications
    applications = []
    for i in range(1, 1001):
        applications.append({
            'application_id': f'APP{str(i).zfill(5)}',
            'candidate_id': f'CAND{str(random.randint(1, num_candidates)).zfill(5)}',
            'job_id': f'JOB{str(random.randint(1, 20)).zfill(4)}',
            'application_date': datetime.now() - timedelta(days=random.randint(1, 60)),
            'status': random.choice(['New', 'Screening', 'Interview', 'Offer', 'Hired', 'Rejected']),
            'ai_screening_score': random.randint(50, 100),
            'ai_notes': f'Strong candidate with {random.randint(2, 8)} years experience'
        })
    
    df_applications = pd.DataFrame(applications)
    df_applications.to_sql('applications', conn, if_exists='append', index=False)
    
    print(f"✅ Generated {len(jobs)} jobs, {len(candidates)} candidates, {len(applications)} applications")
    conn.close()
    return True


if __name__ == "__main__":
    conn = create_hifadhi_database()
    generate_sample_hr_data(conn)
