from dataclasses import dataclass, field


@dataclass
class Job:

    job_id: str = ""

    job_title: str = ""

    company_name: str = ""

    company_website: str = ""

    source_platform: str = ""

    location: str = ""

    country: str = ""

    state: str = ""

    city: str = ""

    workplace_type: str = ""

    employment_type: str = ""

    salary: str = ""

    posted_date: str = ""

    job_url: str = ""

    apply_url: str = ""

    description: str = ""

    skills: list = field(default_factory=list)