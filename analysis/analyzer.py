import json
import os
import re
from typing import Any, Dict, Iterable, List

from dotenv import load_dotenv

from utils.logger import JobLogger


load_dotenv()


class JDAnalyzer:

    def __init__(self):

        self.logger = JobLogger.get_logger()

        self.provider = os.environ.get(
            "LLM_PROVIDER",
            "gemini"
        ).lower().strip()

        self.openai_key = os.environ.get(
            "OPENAI_API_KEY",
            ""
        ).strip()

        self.gemini_key = os.environ.get(
            "GEMINI_API_KEY",
            ""
        ).strip()

        self.project_root = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )

        self.roles_config_path = os.path.join(
            self.project_root,
            "config",
            "roles.json"
        )

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    def analyze(
        self,
        job,
        job_description=None
    ):
        """
        Analyze an enriched job object.

        Preferred usage:
            analyzer.analyze(job_dict)

        Backward-compatible usage:
            analyzer.analyze(
                job_title,
                job_description
            )
        """

        normalized_job = self._normalize_job_input(
            job,
            job_description
        )

        title = normalized_job["title"]

        self.logger.info(
            f"Analyzing Job: {title} "
            f"using {self.provider}..."
        )

        analysis = None

        if (
            self.provider == "gemini"
            and self.gemini_key
        ):

            try:

                analysis = self._analyze_gemini(
                    normalized_job
                )

            except Exception as error:

                self.logger.error(
                    "Gemini analysis failed: "
                    f"{error}. "
                    "Falling back to local parser."
                )

        elif (
            self.provider == "openai"
            and self.openai_key
        ):

            try:

                analysis = self._analyze_openai(
                    normalized_job
                )

            except Exception as error:

                self.logger.error(
                    "OpenAI analysis failed: "
                    f"{error}. "
                    "Falling back to local parser."
                )

        if not isinstance(
            analysis,
            dict
        ):

            analysis = self._analyze_fallback(
                normalized_job
            )

        return self._finalize_analysis(
            normalized_job,
            analysis
        )

    # ==========================================================
    # INPUT NORMALIZATION
    # ==========================================================

    def _normalize_job_input(
        self,
        job,
        job_description=None
    ):

        if isinstance(job, dict):

            data = dict(job)

        elif isinstance(job, str):

            data = {

                "title": job,

                "description": (
                    job_description
                    or ""
                )

            }

        else:

            data = (
                job.__dict__.copy()
                if hasattr(job, "__dict__")
                else {}
            )

        return {

            "title": (
                data.get("title")
                or data.get("job_title")
                or "Unknown Title"
            ),

            "company": (
                data.get("company")
                or data.get("company_name")
                or "Unknown Company"
            ),

            "description": (
                data.get("description")
                or ""
            ),

            "location": (
                data.get("location")
                or ""
            ),

            "country": (
                data.get("country")
                or ""
            ),

            "state": (
                data.get("state")
                or ""
            ),

            "city": (
                data.get("city")
                or ""
            ),

            "workplace_type": (
                data.get("workplace_type")
                or ""
            ),

            "employment_type": (
                data.get("employment_type")
                or data.get("job_type")
                or ""
            ),

            "salary": (
                data.get("salary")
                or ""
            ),

            "min_salary": data.get(
                "min_salary"
            ),

            "max_salary": data.get(
                "max_salary"
            ),

            "currency": (
                data.get("currency")
                or ""
            ),

            "salary_period": (
                data.get("salary_period")
                or ""
            ),

            "skills": self._ensure_list(
                data.get("skills")
                or data.get("extracted_skills")
            ),

            "responsibilities": self._ensure_list(
                data.get("responsibilities")
            ),

            "experience": (
                data.get("experience")
                or ""
            ),

            "education": self._ensure_list(
                data.get("education")
            ),

            "requirements": self._ensure_list(
                data.get("requirements")
            ),

            "benefits": self._ensure_list(
                data.get("benefits")
            )

        }

    # ==========================================================
    # SYSTEM PROMPT
    # ==========================================================

    def _get_system_prompt(self):

        return (
            "You are an expert Job Description Intelligence "
            "Analyzer and AI Recruiter.\n\n"

            "You receive an already extracted and partially "
            "structured job object.\n\n"

            "IMPORTANT RULES:\n"
            "1. Do not invent job information.\n"
            "2. Preserve trusted structured values supplied "
            "by the extraction pipeline.\n"
            "3. Infer only intelligence fields that can be "
            "supported by the supplied job data.\n"
            "4. If information is unavailable, use an empty "
            "list, empty string, or 'Not specified'.\n"
            "5. ATS keywords describe important job keywords. "
            "They are NOT a resume match score.\n\n"

            "Return ONLY valid JSON matching this structure:\n"

            "{\n"
            '  "required_experience": "Required experience",\n'
            '  "required_education": "Minimum education",\n'
            '  "preferred_education": "Preferred education",\n'
            '  "seniority": "Intern / Fresher / Junior / '
            'Mid Level / Senior / Lead / Expert",\n'
            '  "summary": "Short factual job summary",\n'
            '  "extracted_skills": [],\n'
            '  "required_skills": [],\n'
            '  "preferred_skills": [],\n'
            '  "ats_keywords": [],\n'
            '  "responsibilities": [],\n'
            '  "tools_and_technologies": [],\n'
            '  "suggested_certifications": [],\n'
            '  "company_culture": [],\n'
            '  "analysis_completeness_score": 0.0,\n'
            '  "confidence": 0.0,\n'
            '  "reasoning": []\n'
            "}\n\n"

            "Do not include markdown code fences."
        )

    # ==========================================================
    # GEMINI
    # ==========================================================

    def _analyze_gemini(
        self,
        job
    ):

        import google.generativeai as genai

        genai.configure(
            api_key=self.gemini_key
        )

        model = genai.GenerativeModel(

            "gemini-2.5-flash",

            system_instruction=(
                self._get_system_prompt()
            )

        )

        prompt = json.dumps(
            job,
            indent=2,
            ensure_ascii=False,
            default=str
        )

        response = model.generate_content(

            contents=prompt,

            generation_config=(
                genai.GenerationConfig(

                    response_mime_type=(
                        "application/json"
                    ),

                    temperature=0.1

                )
            )

        )

        return self._parse_json_response(
            response.text
        )

    # ==========================================================
    # OPENAI
    # ==========================================================

    def _analyze_openai(
        self,
        job
    ):

        from openai import OpenAI

        client = OpenAI(
            api_key=self.openai_key
        )

        response = (
            client.chat.completions.create(

                model="gpt-4o-mini",

                messages=[

                    {

                        "role": "system",

                        "content": (
                            self._get_system_prompt()
                        )

                    },

                    {

                        "role": "user",

                        "content": json.dumps(
                            job,
                            ensure_ascii=False,
                            default=str
                        )

                    }

                ],

                response_format={
                    "type": "json_object"
                },

                temperature=0.1

            )
        )

        return self._parse_json_response(

            response
            .choices[0]
            .message
            .content

        )

    # ==========================================================
    # JSON RESPONSE PARSER
    # ==========================================================

    def _parse_json_response(
        self,
        response_text
    ):

        if not response_text:

            raise ValueError(
                "LLM returned an empty response."
            )

        cleaned_text = (
            str(response_text)
            .replace("```json", "")
            .replace("```JSON", "")
            .replace("```", "")
            .strip()
        )

        parsed = json.loads(
            cleaned_text
        )

        if not isinstance(
            parsed,
            dict
        ):

            raise ValueError(
                "LLM response must be a JSON object."
            )

        return parsed

    # ==========================================================
    # FALLBACK ANALYZER
    # ==========================================================

    def _analyze_fallback(
        self,
        job
    ):

        self.logger.warning(
            "Executing offline heuristic "
            "JD intelligence parsing."
        )

        title = job["title"]

        description = job["description"]

        desc_lower = description.lower()

        known_skills = (
            self._load_known_skills()
        )

        extracted_skills = (
            self._extract_skills(
                description,
                known_skills
            )
        )

        extracted_skills = self._merge_unique(

            job["skills"],

            extracted_skills

        )

        (
            required_skills,
            preferred_skills

        ) = self._classify_skills(

            description,

            extracted_skills

        )

        required_experience = (

            job["experience"]

            or self._extract_experience(
                description
            )

        )

        (
            required_education,
            preferred_education

        ) = self._extract_education(

            description,

            job["education"]

        )

        seniority = self._detect_seniority(

            title,

            description,

            required_experience

        )

        responsibilities = (

            job["responsibilities"]

            or self._extract_responsibilities(
                description
            )

        )

        tools = self._extract_tools(
            description
        )

        certifications = (
            self._extract_certifications(
                description
            )
        )

        company_culture = (
            self._extract_company_culture(
                description
            )
        )

        ats_keywords = self._merge_unique(

            extracted_skills,

            tools,

            [title]

        )

        summary = self._build_summary(

            job,

            required_experience,

            required_education,

            seniority

        )

        completeness_score = (
            self._calculate_completeness_score(

                extracted_skills,

                required_experience,

                required_education,

                responsibilities,

                tools

            )
        )

        return {

            "required_experience": (
                required_experience
                or "Not specified"
            ),

            "required_education": (
                required_education
                or "Not specified"
            ),

            "preferred_education": (
                preferred_education
                or "Not specified"
            ),

            "seniority": seniority,

            "summary": summary,

            "extracted_skills": (
                extracted_skills
            ),

            "required_skills": (
                required_skills
            ),

            "preferred_skills": (
                preferred_skills
            ),

            "ats_keywords": ats_keywords,

            "responsibilities": (
                responsibilities
            ),

            "tools_and_technologies": (
                tools
            ),

            "suggested_certifications": (
                certifications
            ),

            "company_culture": (
                company_culture
            ),

            "analysis_completeness_score": (
                completeness_score
            ),

            "confidence": 0.50,

            "reasoning": [

                "Offline heuristic analysis "
                "using trusted extracted fields, "
                "dictionary matching and regex rules."

            ]

        }

    # ==========================================================
    # KNOWN SKILLS
    # ==========================================================

    def _load_known_skills(self):

        skills = set()

        if os.path.exists(
            self.roles_config_path
        ):

            try:

                with open(
                    self.roles_config_path,
                    "r",
                    encoding="utf-8"
                ) as file:

                    roles = json.load(
                        file
                    )

                for role_data in roles.values():

                    skills.update(
                        role_data.get(
                            "skills",
                            []
                        )
                    )

            except Exception as error:

                self.logger.error(
                    "Could not load roles config: "
                    f"{error}"
                )

        fallback_skills = {

            "Python",
            "Java",
            "C++",
            "C#",
            "JavaScript",
            "TypeScript",
            "SQL",
            "Machine Learning",
            "Deep Learning",
            "NLP",
            "LLM",
            "RAG",
            "Computer Vision",
            "TensorFlow",
            "PyTorch",
            "Scikit-learn",
            "LangChain",
            "Embeddings",
            "Vector Database",
            "ETL",
            "Data Pipelines",
            "APIs",
            "React",
            "Angular",
            "Vue",
            "Node.js",
            "Spring Boot",
            "Docker",
            "Kubernetes",
            "AWS",
            "Azure",
            "GCP",
            "MongoDB",
            "PostgreSQL",
            "MySQL",
            "Redis",
            "Kafka"

        }

        skills.update(
            fallback_skills
        )

        return skills

    # ==========================================================
    # SKILL EXTRACTION
    # ==========================================================

    def _extract_skills(
        self,
        description,
        known_skills
    ):

        desc_lower = description.lower()

        extracted = []

        for skill in known_skills:

            if self._contains_term(
                desc_lower,
                skill
            ):

                extracted.append(
                    skill
                )

        return self._sorted_unique(
            extracted
        )

    def _classify_skills(
        self,
        description,
        extracted_skills
    ):

        required = []

        preferred = []

        text = str(
            description or ""
        )

        text_lower = text.lower()

        # ======================================================
        # SECTION DEFINITIONS
        # ======================================================

        section_markers = [

            (
                "required",
                (
                    "required skills & experience",
                    "required skills and experience",
                    "required skills",
                    "requirements",
                    "minimum requirements",
                    "minimum qualifications",
                    "qualifications",
                    "your expertise",
                    "what you need",
                    "what you'll need",
                    "what you will need",
                    "you have"
                )
            ),

            (
                "preferred",
                (
                    "preferred qualifications",
                    "preferred skills",
                    "preferred experience",
                    "desirable experience",
                    "desirable skills",
                    "nice to have",
                    "nice-to-have",
                    "bonus points",
                    "desired qualifications"
                )
            ),

            (
                "responsibilities",
                (
                    "key responsibilities",
                    "responsibilities",
                    "what you'll do",
                    "what you will do",
                    "key duties",
                    "a typical day",
                    "a typical day:",
                    "the difference you will make"
                )
            ),

            (
                "other",
                (
                    "why join",
                    "why join?",
                    "benefits",
                    "our benefits",
                    "what we offer",
                    "company culture",
                    "about the company",
                    "about us",
                    "our commitment",
                    "equal opportunity",
                    "pay transparency"
                )
            )

        ]

        # ======================================================
        # FIND SECTION MARKERS
        # ======================================================

        marker_positions = []

        for section_type, markers in section_markers:

            for marker in markers:

                start_position = 0

                while True:

                    position = text_lower.find(
                        marker,
                        start_position
                    )

                    if position == -1:

                        break

                    marker_positions.append(
                        (
                            position,
                            section_type,
                            marker
                        )
                    )

                    start_position = (
                        position
                        + len(marker)
                    )

        marker_positions.sort(
            key=lambda item: item[0]
        )

        # ======================================================
        # BUILD SEMANTIC SECTIONS
        # ======================================================

        sections = []

        if marker_positions:

            first_position = (
                marker_positions[0][0]
            )

            if first_position > 0:

                sections.append(
                    (
                        0,
                        first_position,
                        "general"
                    )
                )

            for index, marker_data in enumerate(
                marker_positions
            ):

                start_position = (
                    marker_data[0]
                )

                section_type = (
                    marker_data[1]
                )

                if index + 1 < len(
                    marker_positions
                ):

                    end_position = (
                        marker_positions[
                            index + 1
                        ][0]
                    )

                else:

                    end_position = len(
                        text
                    )

                sections.append(
                    (
                        start_position,
                        end_position,
                        section_type
                    )
                )

        else:

            sections.append(
                (
                    0,
                    len(text),
                    "general"
                )
            )

        # ======================================================
        # LOCAL PREFERENCE MODIFIERS
        # ======================================================

        preferred_patterns = (

            r"\bpreferred\b",

            r"\bnice\s+to\s+have\b",

            r"\bnice-to-have\b",

            r"\ba\s+plus\b",

            r"\bis\s+a\s+plus\b",

            r"\bwould\s+be\s+a\s+plus\b",

            r"\bdesirable\b",

            r"\bdesired\b",

            r"\bfamiliarity\s+with\b",

            r"\bexposure\s+to\b",

            r"\bbonus\b",

            r"\badvantageous\b",

            r"\bnot\s+required\b"

        )

        # ======================================================
        # CLASSIFY EACH SKILL
        # ======================================================

        for skill in extracted_skills:

            skill_pattern = (

                r"(?<!\w)"
                + re.escape(
                    str(skill).lower()
                )
                + r"(?!\w)"

            )

            matches = list(
                re.finditer(
                    skill_pattern,
                    text_lower
                )
            )

            if not matches:

                continue

            skill_required = False

            skill_preferred = False

            for match in matches:

                match_position = (
                    match.start()
                )

                section_type = "general"

                section_start = 0

                section_end = len(
                    text_lower
                )

                for (
                    start_position,
                    end_position,
                    candidate_section

                ) in sections:

                    if (
                        start_position
                        <= match_position
                        < end_position
                    ):

                        section_type = (
                            candidate_section
                        )

                        section_start = (
                            start_position
                        )

                        section_end = (
                            end_position
                        )

                        break

                # ==============================================
                # LOCAL SEGMENT AROUND SKILL
                # ==============================================

                local_start = max(

                    section_start,

                    match.start() - 55

                )

                local_end = min(

                    section_end,

                    match.end() + 55

                )

                local_context = (

                    text_lower[
                        local_start:local_end
                    ]

                )

                # ==============================================
                # EXPLICIT PREFERRED MODIFIER
                # ==============================================

                has_preferred_modifier = any(

                    re.search(
                        pattern,
                        local_context
                    )

                    for pattern
                    in preferred_patterns

                )

                if has_preferred_modifier:

                    skill_preferred = True

                    continue

                # ==============================================
                # SECTION CLASSIFICATION
                # ==============================================

                if section_type == "preferred":

                    skill_preferred = True

                elif section_type == "required":

                    skill_required = True

                elif section_type == "responsibilities":

                    # Skills used in responsibilities are
                    # relevant to performing the role.

                    skill_required = True

                else:

                    # General technical mentions default to
                    # required unless explicitly preferred.

                    skill_required = True

            # ==================================================
            # FINAL SKILL DECISION
            # ==================================================

            if skill_required:

                required.append(
                    skill
                )

            elif skill_preferred:

                preferred.append(
                    skill
                )

        # ======================================================
        # NORMALIZE RESULTS
        # ======================================================

        required = self._sorted_unique(
            required
        )

        preferred = [

            skill

            for skill in self._sorted_unique(
                preferred
            )

            if skill not in required

        ]

        # ======================================================
        # ORPHAN SKILL INVARIANT
        # ======================================================

        classified_skill_keys = {
            str(skill).strip().lower()
            for skill in (required + preferred)
        }

        for skill in extracted_skills:

            skill_key = str(skill).strip().lower()

            if (
                not skill_key
                or skill_key in classified_skill_keys
            ):
                continue

            skill_pattern = (
                r"(?<!\\w)"
                + re.escape(skill_key)
                + r"(?!\\w)"
            )

            matches = list(
                re.finditer(
                    skill_pattern,
                    text_lower
                )
            )

            orphan_is_preferred = False

            for match in matches:

                local_start = max(
                    0,
                    match.start() - 80
                )

                local_end = min(
                    len(text_lower),
                    match.end() + 80
                )

                local_context = text_lower[
                    local_start:local_end
                ]

                if any(
                    re.search(
                        pattern,
                        local_context
                    )
                    for pattern in preferred_patterns
                ):
                    orphan_is_preferred = True
                    break

            if orphan_is_preferred:
                preferred.append(skill)
            else:
                required.append(skill)

            classified_skill_keys.add(
                skill_key
            )

        required = self._sorted_unique(
            required
        )

        preferred = [
            skill
            for skill in self._sorted_unique(
                preferred
            )
            if skill not in required
        ]

        return (
            required,
            preferred
        )

    # ==========================================================
    # EXPERIENCE
    # ==========================================================

    def _extract_experience(
        self,
        description
    ):

        description_text = str(
            description
            or ""
        )

        patterns = (

            r"\bminimum\s+of\s+(\d+)\+?\s*"
            r"(?:years?|yrs?)\b",

            r"\bminimum\s+(\d+)\+?\s*"
            r"(?:years?|yrs?)\b",

            r"\bat least\s+(\d+)\+?\s*"
            r"(?:years?|yrs?)\b",

            r"\b(\d+)\+?\s*"
            r"(?:years?|yrs?)\s+of\s+"
            r"(?:professional\s+)?experience\b",

            r"\b(\d+)\+?\s*"
            r"(?:years?|yrs?)\s+"
            r"(?:building|developing|working|leading|"
            r"designing|supporting)\b",

            r"\b(\d+)\s*-\s*(\d+)\s*"
            r"(?:years?|yrs?)\b",

            r"\b(\d+)\+?\s*"
            r"(?:years?|yrs?)\b"

        )

        matches = []

        for pattern in patterns:

            for match in re.finditer(
                pattern,
                description_text,
                re.IGNORECASE
            ):

                numbers = [

                    int(number)

                    for number in match.groups()

                    if number is not None

                ]

                if not numbers:

                    continue

                minimum_years = min(
                    numbers
                )

                matches.append(
                    (
                        minimum_years,
                        match.group(0).strip()
                    )
                )

        if not matches:

            return "Not specified"

        matches.sort(
            key=lambda item: item[0],
            reverse=True
        )

        return matches[0][1]

    # ==========================================================
    # EDUCATION
    # ==========================================================

    def _extract_education(
        self,
        description,
        existing_education
    ):

        existing_text = " ".join(
            str(item)
            for item in existing_education
        )

        searchable_text = (

            existing_text
            + "\n"
            + description

        ).lower()

        degree_patterns = {

            "PhD": (

                r"\bph\.?d\b",
                r"\bdoctorate\b"

            ),

            "Master's Degree": (

                r"\bmaster'?s?\b",
                r"\bm\.?\s?tech\b",
                r"\bmca\b",
                r"\bmba\b",
                r"\bm\.?\s?sc\b"

            ),

            "Bachelor's Degree": (

                r"\bbachelor'?s?\b",
                r"\bb\.?\s?tech\b",
                r"\bbca\b",
                r"\bb\.?\s?sc\b",
                r"\bb\.?\s?e\.?\b"

            ),

            "Diploma": (

                r"\bdiploma\b",

            )

        }

        detected = []

        for degree, patterns in (
            degree_patterns.items()
        ):

            if any(

                re.search(
                    pattern,
                    searchable_text,
                    re.IGNORECASE
                )

                for pattern in patterns

            ):

                detected.append(
                    degree
                )

        hierarchy = [

            "Diploma",
            "Bachelor's Degree",
            "Master's Degree",
            "PhD"

        ]

        detected = [

            degree

            for degree in hierarchy

            if degree in detected

        ]

        if not detected:

            return (
                "Not specified",
                "Not specified"
            )

        required = detected[0]

        preferred = (

            detected[-1]

            if len(detected) > 1

            else "Not specified"

        )

        if preferred == required:

            preferred = "Not specified"

        return (
            required,
            preferred
        )

    # ==========================================================
    # SENIORITY
    # ==========================================================

    def _detect_seniority(
        self,
        title,
        description,
        required_experience
    ):

        combined = (
            f"{title}\n{description}"
        ).lower()

        if re.search(
            r"\bintern(?:ship)?\b",
            combined
        ):

            return "Intern"

        if any(
            term in combined
            for term in (
                "fresher",
                "entry level",
                "entry-level",
                "graduate role"
            )
        ):

            return "Fresher"

        if re.search(
            r"\b(?:lead|principal)\b",
            title,
            re.IGNORECASE
        ):

            return "Lead"

        years_match = re.search(
            r"\d+",
            required_experience
            or ""
        )

        if years_match:

            years = int(
                years_match.group()
            )

            if years <= 1:

                return "Junior"

            if years <= 4:

                return "Mid Level"

            if years <= 8:

                return "Senior"

            return "Expert"

        if re.search(
            r"\bsenior\b|\bsr\.?\b",
            title,
            re.IGNORECASE
        ):

            return "Senior"

        if re.search(
            r"\bjunior\b|\bjr\.?\b",
            title,
            re.IGNORECASE
        ):

            return "Junior"

        return "Not specified"

    # ==========================================================
    # RESPONSIBILITIES
    # ==========================================================

    def _extract_responsibilities(
        self,
        description
    ):

        responsibilities = []

        active_verbs = (

            "build",
            "develop",
            "design",
            "maintain",
            "create",
            "implement",
            "collaborate",
            "manage",
            "lead",
            "support",
            "optimize",
            "optimise",
            "analyze",
            "analyse",
            "monitor",
            "deploy",
            "improve",
            "ensure",
            "evaluate",
            "research"

        )

        for line in description.splitlines():

            content = (
                line
                .strip()
                .lstrip("-*• ")
                .strip()
            )

            if len(content) < 15:

                continue

            first_word = (
                content
                .split()[0]
                .lower()
                .rstrip(":")
            )

            if first_word in active_verbs:

                responsibilities.append(
                    content
                )

        return self._merge_unique(
            responsibilities
        )[:10]

    # ==========================================================
    # TOOLS
    # ==========================================================

    def _extract_tools(
        self,
        description
    ):

        tools = (

            "Git",
            "GitHub",
            "GitLab",
            "Docker",
            "Kubernetes",
            "Linux",
            "VS Code",
            "Jira",
            "Slack",
            "AWS",
            "Azure",
            "GCP",
            "Jenkins",
            "Terraform",
            "Ansible",
            "SQL",
            "MySQL",
            "PostgreSQL",
            "MongoDB",
            "Redis",
            "Kafka",
            "React",
            "Angular",
            "Node.js",
            "Spring Boot",
            "TensorFlow",
            "PyTorch"

        )

        description_lower = (
            description.lower()
        )

        return self._sorted_unique([

            tool

            for tool in tools

            if self._contains_term(
                description_lower,
                tool
            )

        ])

    # ==========================================================
    # CERTIFICATIONS
    # ==========================================================

    def _extract_certifications(
        self,
        description
    ):

        desc_lower = description.lower()

        certifications = []

        certification_rules = {

            "AWS Certified Solutions Architect": (
                "aws certified",
                "solutions architect"
            ),

            "PMP Certification": (
                "pmp",
                "project management professional"
            ),

            "Certified ScrumMaster": (
                "certified scrummaster",
                "csm certification"
            )

        }

        for certification, terms in (
            certification_rules.items()
        ):

            if any(
                term in desc_lower
                for term in terms
            ):

                certifications.append(
                    certification
                )

        return self._sorted_unique(
            certifications
        )

    # ==========================================================
    # COMPANY CULTURE
    # ==========================================================

    def _extract_company_culture(
        self,
        description
    ):

        desc_lower = description.lower()

        culture_rules = {

            "Collaborative": (
                "collaborative",
                "collaboration"
            ),

            "Fast-paced": (
                "fast-paced",
                "fast paced",
                "rapid environment"
            ),

            "Innovative": (
                "innovative",
                "innovation",
                "cutting-edge"
            ),

            "Inclusive": (
                "inclusive",
                "inclusion",
                "diversity"
            ),

            "Growth-oriented": (
                "career growth",
                "professional development",
                "learning opportunities"
            )

        }

        traits = []

        for trait, terms in (
            culture_rules.items()
        ):

            if any(
                term in desc_lower
                for term in terms
            ):

                traits.append(
                    trait
                )

        return self._sorted_unique(
            traits
        )

    # ==========================================================
    # SUMMARY
    # ==========================================================

    def _build_summary(
        self,
        job,
        experience,
        education,
        seniority
    ):

        summary_parts = [

            f"{job['title']} position"

        ]

        if seniority != "Not specified":

            summary_parts.append(
                f"at {seniority} level"
            )

        if experience != "Not specified":

            summary_parts.append(
                f"requiring {experience}"
            )

        if education != "Not specified":

            summary_parts.append(
                f"with {education}"
            )

        if job["location"]:

            summary_parts.append(
                f"located in {job['location']}"
            )

        return (
            ", ".join(summary_parts)
            + "."
        )

    # ==========================================================
    # COMPLETENESS SCORE
    # ==========================================================

    def _calculate_completeness_score(
        self,
        skills,
        experience,
        education,
        responsibilities,
        tools
    ):

        score = 0.0

        if skills:

            score += 25.0

        if (
            experience
            and experience != "Not specified"
        ):

            score += 20.0

        if (
            education
            and education != "Not specified"
        ):

            score += 15.0

        if responsibilities:

            score += 25.0

        if tools:

            score += 15.0

        return round(
            min(score, 100.0),
            2
        )

    # ==========================================================
    # FINAL ANALYSIS NORMALIZATION
    # ==========================================================

    def _finalize_analysis(
        self,
        job,
        analysis
    ):

        responsibilities = self._merge_unique(

            job["responsibilities"],

            self._ensure_list(
                analysis.get(
                    "responsibilities"
                )
            )

        )

        extracted_skills = self._merge_unique(

            job["skills"],

            self._ensure_list(
                analysis.get(
                    "extracted_skills"
                )
            )

        )

        return {

            "required_experience": (

                analysis.get(
                    "required_experience"
                )

                or job["experience"]

                or "Not specified"

            ),

            "required_education": (

                analysis.get(
                    "required_education"
                )

                or "Not specified"

            ),

            "preferred_education": (

                analysis.get(
                    "preferred_education"
                )

                or "Not specified"

            ),

            "seniority": (

                analysis.get(
                    "seniority"
                )

                or "Not specified"

            ),

            "summary": (

                analysis.get(
                    "summary"
                )

                or ""

            ),

            "extracted_skills": (
                extracted_skills
            ),

            "required_skills": self._sorted_unique(

                self._ensure_list(
                    analysis.get(
                        "required_skills"
                    )
                )

            ),

            "preferred_skills": self._sorted_unique(

                self._ensure_list(
                    analysis.get(
                        "preferred_skills"
                    )
                )

            ),

            "ats_keywords": self._sorted_unique(

                self._ensure_list(
                    analysis.get(
                        "ats_keywords"
                    )
                )

            ),

            "responsibilities": (
                responsibilities
            ),

            "tools_and_technologies": self._sorted_unique(

                self._ensure_list(
                    analysis.get(
                        "tools_and_technologies"
                    )
                )

            ),

            "suggested_certifications": self._sorted_unique(

                self._ensure_list(
                    analysis.get(
                        "suggested_certifications"
                    )
                )

            ),

            "company_culture": self._sorted_unique(

                self._ensure_list(
                    analysis.get(
                        "company_culture"
                    )
                )

            ),

            "analysis_completeness_score": self._safe_float(

                analysis.get(
                    "analysis_completeness_score"
                )

            ),

            "confidence": self._safe_float(

                analysis.get(
                    "confidence"
                )

            ),

            "reasoning": self._ensure_list(

                analysis.get(
                    "reasoning"
                )

            )

        }

    # ==========================================================
    # HELPERS
    # ==========================================================

    def _contains_term(
        self,
        text,
        term
    ):

        pattern = (

            r"(?<!\w)"
            + re.escape(
                str(term).lower()
            )
            + r"(?!\w)"

        )

        return bool(
            re.search(
                pattern,
                text
            )
        )

    def _ensure_list(
        self,
        value
    ):

        if value is None:

            return []

        if isinstance(
            value,
            list
        ):

            return value

        if isinstance(
            value,
            (
                tuple,
                set
            )
        ):

            return list(
                value
            )

        if isinstance(
            value,
            str
        ):

            value = value.strip()

            if not value:

                return []

            return [
                value
            ]

        return [
            value
        ]

    def _merge_unique(
        self,
        *collections
    ):

        merged = []

        seen = set()

        for collection in collections:

            for item in self._ensure_list(
                collection
            ):

                text = str(
                    item
                ).strip()

                if not text:

                    continue

                key = text.lower()

                if key in seen:

                    continue

                seen.add(
                    key
                )

                merged.append(
                    text
                )

        return merged

    def _sorted_unique(
        self,
        values
    ):

        return sorted(

            self._merge_unique(
                values
            ),

            key=lambda value: (
                value.lower()
            )

        )

    def _safe_float(
        self,
        value
    ):

        try:

            return float(
                value
                or 0.0
            )

        except (
            TypeError,
            ValueError
        ):

            return 0.0