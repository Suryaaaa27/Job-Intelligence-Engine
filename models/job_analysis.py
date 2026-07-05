from dataclasses import dataclass, field
from typing import List


@dataclass
class JobAnalysis:

    predicted_role: str = ""

    confidence: float = 0

    extracted_skills: List[str] = field(default_factory=list)

    required_skills: List[str] = field(default_factory=list)

    preferred_skills: List[str] = field(default_factory=list)

    ats_keywords: List[str] = field(default_factory=list)

    match_score: float = 0

    reasoning: List[str] = field(default_factory=list)