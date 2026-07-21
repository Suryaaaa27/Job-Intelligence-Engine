"""
Standard Resume Schema
=======================
Canonical dataclasses for parser output.
"""

from dataclasses import asdict, dataclass, field
from typing import List, Optional


@dataclass
class ContactInfo:
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None


@dataclass
class Experience:
    job_title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    bullets: List[str] = field(default_factory=list)
    raw_text: Optional[str] = None


@dataclass
class Project:
    name: Optional[str] = None
    description: Optional[str] = None
    technologies: List[str] = field(default_factory=list)
    bullets: List[str] = field(default_factory=list)
    link: Optional[str] = None
    raw_text: Optional[str] = None


@dataclass
class Education:
    degree: Optional[str] = None
    institution: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[str] = None
    raw_text: Optional[str] = None


@dataclass
class Certification:
    name: Optional[str] = None
    issuer: Optional[str] = None
    date: Optional[str] = None
    raw_text: Optional[str] = None


@dataclass
class ParseWarning:
    section: str
    message: str


@dataclass
class ResumeSchema:
    contact_info: ContactInfo = field(default_factory=ContactInfo)
    summary: Optional[str] = None
    skills: List[str] = field(default_factory=list)
    experience: List[Experience] = field(default_factory=list)
    projects: List[Project] = field(default_factory=list)
    education: List[Education] = field(default_factory=list)
    certifications: List[Certification] = field(default_factory=list)
    raw_sections: dict = field(default_factory=dict)
    warnings: List[ParseWarning] = field(default_factory=list)
    source_file: Optional[str] = None
    source_file_type: Optional[str] = None

    def to_dict(self):
        return asdict(self)
