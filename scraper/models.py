from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Job:

    # =========================================================
    # JOB IDENTITY
    # =========================================================

    job_id: str = ""

    job_title: str = ""

    company_name: str = ""

    company_website: str = ""


    # =========================================================
    # SOURCE INFORMATION
    # =========================================================

    source_platform: str = ""

    source_job_id: str = ""

    job_url: str = ""

    apply_url: str = ""


    # =========================================================
    # LOCATION INFORMATION
    # =========================================================

    location: str = ""

    country: str = ""

    state: str = ""

    city: str = ""

    workplace_type: str = ""


    # =========================================================
    # EMPLOYMENT INFORMATION
    # =========================================================

    employment_type: str = ""

    experience: str = ""

    posted_date: str = ""


    # =========================================================
    # SALARY INFORMATION
    # =========================================================

    salary: str = ""

    min_salary: Optional[float] = None

    max_salary: Optional[float] = None

    currency: str = ""

    salary_period: str = ""


    # =========================================================
    # JOB CONTENT
    # =========================================================

    description: str = ""

    responsibilities: List[str] = field(default_factory=list)

    skills: List[str] = field(default_factory=list)

    recruiter_name: str = ""

    recruiter_email: str = ""
    
    recruiter_phone: str = ""

    recruiter_office: str = ""

    benefits: List[str] = field(default_factory=list)

    education: List[str] = field(default_factory=list)


    # =========================================================
    # SCRAPING METADATA
    # =========================================================

    scraped_at: str = ""

    raw_data: dict = field(default_factory=dict)