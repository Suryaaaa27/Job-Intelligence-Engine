from dataclasses import dataclass, field
from typing import List


@dataclass
class Job:

    # Identity
    title: str = ""
    company: str = ""

    # Metadata
    source: str = ""
    search_query: str = ""
    application_url: str = ""
    job_reference: str = ""

    # Location
    location: str = ""

    # Job Information
    employment_type: str = ""
    experience: str = ""
    salary: str = ""

    # Content
    description: str = ""

    # Optional extracted by scraper
    skills: List[str] = field(default_factory=list)