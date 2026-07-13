import re
from typing import List, Optional, Tuple


class JobDetailExtractor:
    """
    Deterministic job-detail intelligence layer.

    Accepts cleaned job dictionaries and enriches them with
    structured information extracted from job descriptions.

    Designed to work across Hays, LinkedIn, Greenhouse,
    Indeed, and future job sources.
    """

    SECTION_HEADINGS = [
        "About the Role",
        "About The Role",
        "Key Responsibilities",
        "Your Responsibilities",
        "Responsibilities",
        "What You'll Do",
        "What You Will Do",
        "Key Duties",
        "Duties",
        "Required Skills & Experience",
        "Required Skills and Experience",
        "Required Skills",
        "Required Experience",
        "Skills & Experience",
        "Skills and Experience",
        "Requirements",
        "Desirable Experience",
        "Preferred Experience",
        "Preferred Skills",
        "Qualifications",
        "Education",
        "Benefits",
        "What We Offer",
        "Why Join?",
        "Why Join",
        "About You",
        "About the Company",
        "About The Company",
    ]

    RESPONSIBILITY_HEADINGS = [
        "key responsibilities",
        "responsibilities",
        "your responsibilities",
        "what you'll do",
        "what you will do",
        "duties",
        "key duties",
    ]

    RESPONSIBILITY_STOP_HEADINGS = [
        "required skills",
        "required experience",
        "requirements",
        "skills and experience",
        "skills & experience",
        "required skills & experience",
        "required skills and experience",
        "desirable experience",
        "preferred skills",
        "preferred experience",
        "qualifications",
        "education",
        "benefits",
        "what we offer",
        "why join?",
        "why join",
        "about you",
        "about the company",
    ]

    EXPERIENCE_PATTERNS = [
        r"(\d+\+?\s*(?:-\s*\d+\+?)?\s*years?(?:\s+of)?\s+experience)",
        r"(\d+\+?\s*(?:-\s*\d+\+?)?\s*yrs?(?:\s+of)?\s+experience)",
        r"(minimum\s+(?:of\s+)?\d+\+?\s+years?(?:\s+of)?\s+experience)",
        r"(at\s+least\s+\d+\+?\s+years?(?:\s+of)?\s+experience)",
    ]

    EDUCATION_PATTERNS = [
        r"(bachelor(?:'s)?\s+degree[^.\n]*)",
        r"(master(?:'s)?\s+degree[^.\n]*)",
        r"(ph\.?d\.?[^.\n]*)",
        r"(doctorate[^.\n]*)",
        r"(b\.?tech[^.\n]*)",
        r"(m\.?tech[^.\n]*)",
        r"(degree\s+in\s+[^.\n]*)",
    ]

    BENEFIT_KEYWORDS = [
        "health insurance",
        "medical insurance",
        "dental insurance",
        "vision insurance",
        "paid time off",
        "pto",
        "retirement plan",
        "401k",
        "401(k)",
        "life insurance",
        "flexible working",
        "remote working",
        "hybrid working",
        "parental leave",
        "maternity leave",
        "paternity leave",
        "annual leave",
        "paid holidays",
        "bonus",
        "stock options",
        "equity",
        "learning budget",
        "training budget",
        "gym membership",
    ]

    SKILL_KEYWORDS = [
        "Python",
        "Java",
        "JavaScript",
        "TypeScript",
        "C++",
        "C#",
        "Go",
        "Rust",
        "SQL",
        "NoSQL",
        "MongoDB",
        "PostgreSQL",
        "MySQL",
        "Redis",
        "TensorFlow",
        "PyTorch",
        "Scikit-learn",
        "Keras",
        "Pandas",
        "NumPy",
        "Spark",
        "Hadoop",
        "Kafka",
        "Airflow",
        "Docker",
        "Kubernetes",
        "AWS",
        "Azure",
        "GCP",
        "Terraform",
        "Jenkins",
        "Git",
        "GitHub",
        "GitLab",
        "REST",
        "GraphQL",
        "FastAPI",
        "Flask",
        "Django",
        "React",
        "Angular",
        "Vue",
        "Node.js",
        "Express",
        "Spring Boot",
        "Machine Learning",
        "Deep Learning",
        "NLP",
        "Natural Language Processing",
        "Computer Vision",
        "LLM",
        "LLMs",
        "RAG",
        "Vector Database",
        "Vector Databases",
        "Embeddings",
        "Retrieval Systems",
        "ETL",
        "Data Pipelines",
        "MLOps",
        "CI/CD",
        "APIs",
    ]

    def enrich(self, job: dict) -> dict:
        """
        Enrich a cleaned job dictionary in-place.
        """

        if not isinstance(job, dict):
            raise TypeError(
                "JobDetailExtractor expects a cleaned job dictionary."
            )

        description = job.get("description", "") or ""

        if not description.strip():
            return job

        normalized_description = self.normalize_description_structure(
            description
        )

        job["responsibilities"] = self.extract_responsibilities(
            normalized_description
        )

        job["skills"] = self.extract_skills(
            normalized_description
        )

        job["experience"] = self.extract_experience(
            normalized_description
        )

        job["education"] = self.extract_education(
            normalized_description
        )

        job["benefits"] = self.extract_benefits(
            normalized_description
        )

        salary_min, salary_max, currency, period = self.extract_salary(
            normalized_description
        )

        if job.get("min_salary") is None:
            job["min_salary"] = salary_min

        if job.get("max_salary") is None:
            job["max_salary"] = salary_max

        if not job.get("currency"):
            job["currency"] = currency

        job["salary_period"] = period

        return job

    def normalize_description_structure(
        self,
        description: str,
    ) -> str:
        """
        Repair descriptions where source APIs glue section headings
        directly to surrounding text.

        Example:

        reliability.Key ResponsibilitiesBuild pipelines

        becomes:

        reliability.
        Key Responsibilities
        Build pipelines
        """

        text = str(description)

        headings = sorted(
            self.SECTION_HEADINGS,
            key=len,
            reverse=True,
        )

        for heading in headings:

            pattern = re.escape(heading)

            text = re.sub(
                pattern,
                f"\n{heading}\n",
                text,
                flags=re.IGNORECASE,
            )

        text = re.sub(
            r"\n\s*\n+",
            "\n",
            text,
        )

        return text.strip()

    def extract_responsibilities(
        self,
        description: str,
    ) -> List[str]:

        section = self._extract_section(
            description,
            self.RESPONSIBILITY_HEADINGS,
            self.RESPONSIBILITY_STOP_HEADINGS,
        )

        if not section:
            return []

        responsibilities = []

        lines = self._clean_lines(section)

        for line in lines:

            cleaned = self._clean_bullet(line)

            if not self._is_meaningful_sentence(cleaned):
                continue

            split_items = self._split_camel_sentences(
                cleaned
            )

            for item in split_items:

                item = self._normalize_whitespace(item)

                if self._is_meaningful_sentence(item):
                    responsibilities.append(item)

        return self._unique(responsibilities)

    def extract_skills(
        self,
        description: str,
    ) -> List[str]:

        found = []

        for skill in self.SKILL_KEYWORDS:

            pattern = self._skill_pattern(skill)

            if re.search(
                pattern,
                description,
                flags=re.IGNORECASE,
            ):
                found.append(skill)

        aliases = {
            "Natural Language Processing": "NLP",
            "LLMs": "LLM",
            "Vector Databases": "Vector Database",
        }

        normalized = [
            aliases.get(skill, skill)
            for skill in found
        ]

        return sorted(
            self._unique(normalized),
            key=str.lower,
        )

    def extract_experience(
        self,
        description: str,
    ) -> str:

        for pattern in self.EXPERIENCE_PATTERNS:

            match = re.search(
                pattern,
                description,
                flags=re.IGNORECASE,
            )

            if match:

                return self._normalize_whitespace(
                    match.group(1)
                )

        return ""

    def extract_education(
        self,
        description: str,
    ) -> List[str]:

        education = []

        for pattern in self.EDUCATION_PATTERNS:

            matches = re.findall(
                pattern,
                description,
                flags=re.IGNORECASE,
            )

            for match in matches:

                cleaned = self._normalize_whitespace(
                    match
                )

                if cleaned:
                    education.append(cleaned)

        return self._unique(education)

    def extract_benefits(
        self,
        description: str,
    ) -> List[str]:

        text = description.lower()

        benefits = []

        for benefit in self.BENEFIT_KEYWORDS:

            if benefit.lower() in text:
                benefits.append(benefit)

        return self._unique(benefits)

    def extract_salary(
        self,
        description: str,
    ) -> Tuple[
        Optional[float],
        Optional[float],
        str,
        str,
    ]:

        currency = self._extract_currency(
            description
        )

        period = self._extract_salary_period(
            description
        )

        range_patterns = [
            (
                r"[£$€₹]?\s*"
                r"([\d,]+(?:\.\d+)?)"
                r"\s*[-–—]\s*"
                r"[£$€₹]?\s*"
                r"([\d,]+(?:\.\d+)?)"
            ),
            (
                r"([\d,]+(?:\.\d+)?)"
                r"\s+to\s+"
                r"([\d,]+(?:\.\d+)?)"
            ),
        ]

        for pattern in range_patterns:

            match = re.search(
                pattern,
                description,
                flags=re.IGNORECASE,
            )

            if match:

                minimum = self._to_float(
                    match.group(1)
                )

                maximum = self._to_float(
                    match.group(2)
                )

                return (
                    minimum,
                    maximum,
                    currency,
                    period,
                )

        single_patterns = [
            r"[£$€₹]\s*([\d,]+(?:\.\d+)?)",
            (
                r"(?:salary|rate|pay)"
                r"\s*[:\-]?\s*"
                r"[£$€₹]?\s*"
                r"([\d,]+(?:\.\d+)?)"
            ),
        ]

        for pattern in single_patterns:

            match = re.search(
                pattern,
                description,
                flags=re.IGNORECASE,
            )

            if match:

                value = self._to_float(
                    match.group(1)
                )

                return (
                    value,
                    value,
                    currency,
                    period,
                )

        return (
            None,
            None,
            currency,
            period,
        )

    def _extract_section(
        self,
        description: str,
        start_headings: List[str],
        stop_headings: List[str],
    ) -> str:

        lines = self._clean_lines(description)

        collecting = False
        collected = []

        for line in lines:

            normalized = self._normalize_heading(line)

            if self._matches_heading(
                normalized,
                start_headings,
            ):
                collecting = True
                continue

            if collecting and self._matches_heading(
                normalized,
                stop_headings,
            ):
                break

            if collecting:
                collected.append(line)

        return "\n".join(collected)

    def _extract_currency(
        self,
        text: str,
    ) -> str:

        lower_text = text.lower()

        if "£" in text or "gbp" in lower_text:
            return "GBP"

        if "$" in text or "usd" in lower_text:
            return "USD"

        if "€" in text or "eur" in lower_text:
            return "EUR"

        if "₹" in text or "inr" in lower_text:
            return "INR"

        return ""

    def _extract_salary_period(
        self,
        text: str,
    ) -> str:

        lower_text = text.lower()

        period_patterns = {
            "hour": [
                "per hour",
                "/hour",
                "/hr",
                "hourly",
            ],
            "day": [
                "per day",
                "/day",
                "daily rate",
                "day rate",
            ],
            "week": [
                "per week",
                "/week",
                "weekly",
            ],
            "month": [
                "per month",
                "/month",
                "monthly",
            ],
            "year": [
                "per year",
                "/year",
                "per annum",
                "annually",
                "annual salary",
            ],
        }

        for period, patterns in period_patterns.items():

            for pattern in patterns:

                if pattern in lower_text:
                    return period

        return ""

    @staticmethod
    def _split_camel_sentences(
        text: str,
    ) -> List[str]:
        """
        Repair sentences and list items glued together by source APIs.

        Examples:

        contentDevelop pipelines
            ->
        content
        Develop pipelines

        strategies.Improve quality
            ->
        strategies.
        Improve quality

        testing for:AccuracyHallucination detection
            ->
        testing for:
        Accuracy
        Hallucination detection
        """

        # Split sentence punctuation followed immediately by uppercase text.
        text = re.sub(
            r"(?<=[.!?])(?=[A-Z])",
            "\n",
            text,
        )

        # Split colon followed immediately by uppercase text.
        text = re.sub(
            r"(?<=:)(?=[A-Z])",
            "\n",
            text,
        )

        # Split lowercase/digit -> uppercase camel-style source concatenation.
        text = re.sub(
            r"(?<=[a-z0-9])(?=[A-Z][a-z])",
            "\n",
            text,
        )

        return [
            item.strip()
            for item in text.splitlines()
            if item.strip()
        ]

    @staticmethod
    def _clean_lines(
        text: str,
    ) -> List[str]:

        return [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

    @staticmethod
    def _normalize_heading(
        text: str,
    ) -> str:

        text = text.lower().strip()

        text = text.rstrip(":")

        return re.sub(
            r"\s+",
            " ",
            text,
        )

    @staticmethod
    def _matches_heading(
        line: str,
        headings: List[str],
    ) -> bool:

        return any(
            line == heading.lower().rstrip(":")
            for heading in headings
        )

    @staticmethod
    def _clean_bullet(
        text: str,
    ) -> str:

        text = re.sub(
            r"^[\-\*\u2022\u25cf\u25e6]+\s*",
            "",
            text,
        )

        return JobDetailExtractor._normalize_whitespace(
            text
        )

    @staticmethod
    def _is_meaningful_sentence(
        text: str,
    ) -> bool:

        if not text:
            return False

        if len(text) < 10:
            return False

        return True

    @staticmethod
    def _skill_pattern(
        skill: str,
    ) -> str:

        escaped = re.escape(skill)

        return rf"(?<!\w){escaped}(?!\w)"

    @staticmethod
    def _normalize_whitespace(
        text: str,
    ) -> str:

        return re.sub(
            r"\s+",
            " ",
            text,
        ).strip()

    @staticmethod
    def _to_float(
        value: str,
    ) -> Optional[float]:

        try:

            return float(
                value.replace(",", "")
            )

        except (
            TypeError,
            ValueError,
        ):

            return None

    @staticmethod
    def _unique(
        items: List[str],
    ) -> List[str]:

        seen = set()

        result = []

        for item in items:

            key = item.lower()

            if key in seen:
                continue

            seen.add(key)

            result.append(item)

        return result