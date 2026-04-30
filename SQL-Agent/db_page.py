import os
from dataclasses import dataclass
from typing import Iterable

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


@dataclass(frozen=True)
class DbSettings:
    database_url: str


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS candidates (
    id SERIAL PRIMARY KEY,
    full_name TEXT,
    first_name TEXT NOT NULL,
    middle_name TEXT,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    alternate_phone TEXT,
    date_of_birth DATE,
    gender TEXT,
    address_full TEXT,
    city TEXT,
    state TEXT,
    country TEXT,
    pincode TEXT,
    location TEXT,
    linkedin_url TEXT,
    github_url TEXT,
    portfolio_url TEXT,
    website_url TEXT,
    other_links JSONB,
    summary_text TEXT,
    career_objective TEXT,
    years_of_experience INTEGER CHECK (years_of_experience >= 0),
    total_experience_years DOUBLE PRECISION,
    current_job_title TEXT,
    current_company TEXT,
    current_ctc TEXT,
    highest_education TEXT,
    primary_skill TEXT,
    domain TEXT,
    department TEXT,
    resume_url TEXT,
    skills TEXT,
    education TEXT,
    education_details JSONB,
    experience_details JSONB,
    projects JSONB,
    skills_detailed JSONB,
    achievements JSONB,
    certifications JSONB,
    positions JSONB,
    coding_profiles JSONB,
    languages JSONB,
    publications JSONB,
    activities JSONB,
    section_name JSONB,
    section_data JSONB,
    current_stage TEXT NOT NULL DEFAULT 'APPLIED',
    stage_history JSONB,
    resume_text TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""

SEED_SQL = """
INSERT INTO candidates (
    full_name, first_name, last_name, email, phone, location,
    years_of_experience, total_experience_years, current_job_title, department,
    skills, primary_skill, current_company, current_ctc, highest_education,
    education, summary_text, current_stage, resume_text, other_links,
    education_details, experience_details, projects, skills_detailed,
    certifications, languages, section_name, section_data, created_at, updated_at
) VALUES (
    'Raj Sharma', 'Raj', 'Sharma', 'raj.sharma@example.com', '9876543210', 'Mumbai, Maharashtra, India',
    5, 5.0, 'Senior Backend Engineer', 'Engineering',
    'Java, Spring Boot, PostgreSQL, Microservices', 'Java', 'Tech Corp', '15 LPA', 'B.Tech CSE',
    'B.Tech CSE', 'Experienced Java developer with 5 years in backend systems.', 'TECH_INTERVIEW',
    'Experienced Java developer with 5 years in backend systems...',
    '[\"https://linkedin.com/in/raj-sharma\"]'::jsonb,
    '[{\"degree\":\"B.Tech\",\"fieldOfStudy\":\"Computer Science\"}]'::jsonb,
    '[{\"companyName\":\"Tech Corp\",\"jobTitle\":\"Senior Backend Engineer\"}]'::jsonb,
    '[{\"name\":\"HRMS Platform\"}]'::jsonb,
    '[{\"skillName\":\"Java\"},{\"skillName\":\"Spring Boot\"},{\"skillName\":\"PostgreSQL\"}]'::jsonb,
    '[{\"name\":\"Oracle Certified Professional\"}]'::jsonb,
    '[\"English\",\"Hindi\"]'::jsonb,
    '[\"experience\",\"skills\",\"education\"]'::jsonb,
    '{\"source\":\"frontend-merged-schema\"}'::jsonb,
    NOW(), NOW()
)
ON CONFLICT (email) DO NOTHING;
"""


def load_settings() -> DbSettings:
    print("[DEBUG] Loading database settings...")
    database_url = os.getenv("NEON_DATABASE_URL")
    if not database_url:
        print("[DEBUG] ERROR: NEON_DATABASE_URL environment variable is missing.")
        raise SystemExit("Missing required environment variable: NEON_DATABASE_URL")
    print("[DEBUG] Database URL successfully retrieved from environment.")
    return DbSettings(database_url=database_url)


def get_engine(settings: DbSettings) -> Engine:
    print("[DEBUG] Creating SQLAlchemy connection engine...")
    return create_engine(settings.database_url)


def execute_sql(engine: Engine, sql_statements: Iterable[str]) -> None:
    print("[DEBUG] Opening database connection for schema/seed execution...")
    with engine.begin() as connection:
        for index, statement in enumerate(sql_statements):
            print(f"[DEBUG] Executing SQL statement block {index + 1}...")
            connection.execute(text(statement))
    print("[DEBUG] SQL statements executed and committed successfully.")


def verify_seed(engine: Engine) -> None:
    print("[DEBUG] Verifying database seeding operations...")
    with engine.begin() as connection:
        print("[DEBUG] Fetching total candidate count...")
        candidate_count = connection.execute(
            text("SELECT COUNT(*) FROM candidates")
        ).scalar_one()
        
        print("[DEBUG] Fetching sample rows for verification...")
        sample_rows = connection.execute(
            text(
                """
                SELECT full_name, email, department, current_stage, primary_skill
                FROM candidates
                ORDER BY id
                LIMIT 5
                """
            )
        ).all()

    print(f"\n[DEBUG] --- VERIFICATION RESULTS ---")
    print(f"candidates: {candidate_count}")
    print("Sample rows:")
    for row in sample_rows:
        print(
            f"  {row.full_name} | {row.email} | "
            f"{row.department} | {row.current_stage} | {row.primary_skill}"
        )
    print(f"[DEBUG] ------------------------------\n")


def main() -> None:
    print("[DEBUG] Starting db_page.py script...")
    
    if load_dotenv:
        print("[DEBUG] python-dotenv is installed. Loading .env file...")
        load_dotenv()
    else:
        print("[DEBUG] python-dotenv not installed; .env file will be ignored.")

    settings = load_settings()
    engine = get_engine(settings)

    execute_sql(engine, [SCHEMA_SQL, SEED_SQL])
    print("[DEBUG] Schema created and dummy data inserted.")
    
    verify_seed(engine)
    print("[DEBUG] Script execution finished.")


if __name__ == "__main__":
    main()