import os
import json
import re
from dotenv import load_dotenv
from utils.logger import JobLogger

load_dotenv()


class JDAnalyzer:

    def __init__(self):
        self.logger = JobLogger.get_logger()
        self.provider = os.environ.get("LLM_PROVIDER", "gemini").lower()
        self.openai_key = os.environ.get("OPENAI_API_KEY", "")
        self.gemini_key = os.environ.get("GEMINI_API_KEY", "")

    def analyze(self, job_title, job_description):
        """
        Analyze a job description and return structured intelligence.
        Attempts to use LLM first, falling back to local heuristic extraction if no key is present.
        """
        self.logger.info(f"Analyzing Job: {job_title} using {self.provider}...")

        # If LLM key is configured, use LLM
        if self.provider == "gemini" and self.gemini_key:
            try:
                return self._analyze_gemini(job_title, job_description)
            except Exception as e:
                self.logger.error(f"Gemini analysis failed: {e}. Falling back to local parser.")
        elif self.provider == "openai" and self.openai_key:
            try:
                return self._analyze_openai(job_title, job_description)
            except Exception as e:
                self.logger.error(f"OpenAI analysis failed: {e}. Falling back to local parser.")

        # Fallback to offline rule-based heuristic extraction
        return self._analyze_fallback(job_title, job_description)

    def _get_system_prompt(self):
        return (
            "You are an expert Job Description Parser and AI Recruiter. Your task is to analyze "
            "the provided job title and job description and extract structured intelligence. "
            "You must return a valid JSON object matching the following structure:\n"
            "{\n"
            '  "title": "Job Title",\n'
            '  "location": "Job Location",\n'
            '  "salary": "Salary or CTC if mentioned",\n'
            '  "employment_type": "Full Time / Part Time / Internship / Contract",\n'
            '  "required_experience": "Required experience",\n'
            '  "required_education": "Minimum education",\n'
            '  "preferred_education": "Preferred education",\n'
            '  "seniority": "Intern / Fresher / Junior / Mid Level / Senior / Lead",\n'
            '  "summary": "Short summary of the job",\n'
            '  "extracted_skills": ["all", "skills"],\n'
            '  "required_skills": ["mandatory", "skills"],\n'
            '  "preferred_skills": ["preferred", "skills"],\n'
            '  "ats_keywords": ["important", "ATS", "keywords"],\n'
            '  "responsibilities": ["responsibility1", "responsibility2"],\n'
            '  "tools_and_technologies": ["Git", "Docker", "Python"],\n'
            '  "suggested_certifications": ["AWS", "PMP"],\n'
            '  "work_setting": "Remote / Hybrid / On-site",\n'
            '  "company_culture": ["Collaborative", "Fast-paced"],\n'
            '  "ats_score_estimate": 85.5,\n'
            '  "confidence": 0.95,\n'
            '  "reasoning": ["reason1", "reason2"]\n'
            "}\n"
            "Ensure the output contains ONLY valid JSON. Do not include markdown code block formatting like ```json."
        )

    def _analyze_gemini(self, title, description):
        import google.generativeai as genai
        genai.configure(api_key=self.gemini_key)
        
        # Using the standard generative model with system instructions in constructor
        model = genai.GenerativeModel(
            "gemini-2.5-flash",
            system_instruction=self._get_system_prompt()
        )
        
        prompt = (
            f"Job Title: {title}\n"
            f"Job Description:\n{description}\n\n"
            f"Parse this job description according to the system prompt guidelines."
        )
        
        response = model.generate_content(
            contents=prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
        )
        
        # Parse the JSON response
        try:
            return json.loads(response.text.strip())
        except Exception as json_err:
            # Fallback to cleaning markdown markers if present
            cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned_text)

    def _analyze_openai(self, title, description):
        from openai import OpenAI
        client = OpenAI(api_key=self.openai_key)
        
        prompt = (
            f"Job Title: {title}\n"
            f"Job Description:\n{description}"
        )
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        return json.loads(response.choices[0].message.content)

    def _analyze_fallback(self, title, description):
        """
        Offline rule-based fallback when LLM credentials are not available.
        Ensures the pipeline is fully functional and does not crash.
        """
        self.logger.warning("No LLM credentials found. Executing offline heuristic parsing.")
        
        # Load roles config for local skill matching
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "config",
            "roles.json"
        )
        
        all_possible_skills = set()
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    roles = json.load(f)
                    for rdata in roles.values():
                        all_possible_skills.update(rdata.get("skills", []))
            except Exception as e:
                self.logger.error(f"Could not load config for skill fallback: {e}")
                
        if not all_possible_skills:
            all_possible_skills = {
                "Python", "SQL", "Java", "C++", "Docker", "AWS", "TensorFlow", "PyTorch",
                "Machine Learning", "NLP", "React", "Vue", "Canva", "SEO", "PPC"
            }
            
        desc_lower = description.lower()
        # ---------------- LOCATION ----------------

        location = "Not specified"

        location_patterns = [
            r'location[:\s]+([A-Za-z ,]+)',
            r'job location[:\s]+([A-Za-z ,]+)'
        ]

        for pattern in location_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                break

        cities = [
            "Mumbai",
            "Pune",
            "Bangalore",
            "Hyderabad",
            "Chennai",
            "Delhi",
            "Noida",
            "Gurgaon",
            "Ahmedabad",
            "Kolkata"
        ]

        if location == "Not specified":
            for city in cities:
                if city.lower() in desc_lower:
                    location = city
                    break


        # ---------------- SALARY ----------------

        salary = "Not specified"

        salary_patterns = [
            r'₹\s?[\d,]+(?:\s*-\s*₹?[\d,]+)?\s*(?:LPA|lakhs?|per annum)?',
            r'\$\s?[\d,]+',
            r'CTC[:\s]+([^\n]+)',
            r'Salary[:\s]+([^\n]+)'
        ]

        for pattern in salary_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                salary = match.group(0).strip()
                break


        # ---------------- EMPLOYMENT TYPE ----------------

        employment_type = "Not specified"

        employment_types = [
            "Full Time",
            "Part Time",
            "Internship",
            "Contract",
            "Temporary",
            "Freelance"
        ]

        for emp in employment_types:
            if emp.lower() in desc_lower:
                employment_type = emp
                break
        extracted_skills = []
        for skill in all_possible_skills:
            if re.search(r'\b' + re.escape(skill.lower()) + r'\b', desc_lower):
                extracted_skills.append(skill)
                
        # Classify required vs preferred skills based on section context
        required_skills = []
        preferred_skills = []
        current_section = "general"
        
        for line in description.split("\n"):
            line_lower = line.lower().strip()
            if any(h in line_lower for h in ["requirement", "qualification", "must have", "what you need", "skills required"]):
                current_section = "required"
            elif any(h in line_lower for h in ["preferred", "plus", "nice to have", "desired"]):
                current_section = "preferred"
            elif any(h in line_lower for h in ["responsibility", "what you'll do", "key duties"]):
                current_section = "responsibilities"
                
            # Scan matching skills in this line
            for skill in extracted_skills:
                if re.search(r'\b' + re.escape(skill.lower()) + r'\b', line_lower):
                    if current_section == "preferred":
                        preferred_skills.append(skill)
                    elif current_section == "required":
                        required_skills.append(skill)
                    else:
                        # If found in general text before any header, default to required
                        required_skills.append(skill)
                        
        # Dedup lists and ensure preferred doesn't overlap required
        required_skills = list(set(required_skills))
        preferred_skills = list(set(preferred_skills) - set(required_skills))
                
        # Extract required experience using regex
        # ---------------- EXPERIENCE ----------------

        experience_patterns = [
            r'\d+\+?\s*(?:years?|yrs?)',
            r'\d+\s*-\s*\d+\s*(?:years?|yrs?)',
            r'minimum\s+\d+\+?\s*(?:years?|yrs?)',
            r'at least\s+\d+\+?\s*(?:years?|yrs?)',
            r'\d+\+?\s*(?:years?|yrs?)\s+of\s+experience'
        ]

        required_exp = "Not specified"

        for pattern in experience_patterns:
            match = re.search(pattern, desc_lower, re.IGNORECASE)
            if match:
                required_exp = match.group(0).title()
                break
        # Extract education requirements
        # ---------------- EDUCATION ----------------

        education_keywords = {
            "Bachelor's Degree": [
                "bachelor",
                "bachelors",
                "b.tech",
                "btech",
                "b.e",
                "be",
                "bca",
                "b.sc",
                "bsc"
            ],

            "Master's Degree": [
                "master",
                "masters",
                "m.tech",
                "mtech",
                "m.e",
                "me",
                "mca",
                "mba",
                "m.sc",
                "msc"
            ],

            "PhD": [
                "phd",
                "ph.d"
            ],

            "Diploma": [
                "diploma"
            ]
        }

        required_edu = "Not specified"

        for degree, keywords in education_keywords.items():
            if any(keyword in desc_lower for keyword in keywords):
                required_edu = degree
                break

        preferred_edu = "Not specified"

        if required_edu == "Bachelor's Degree":
            if any(k in desc_lower for k in ["master", "masters", "m.tech", "mba", "mca", "phd"]):
                preferred_edu = "Master's Degree"

        elif required_edu == "Master's Degree":
            if "phd" in desc_lower or "ph.d" in desc_lower:
                preferred_edu = "PhD"
        # Detect tools and technologies
        potential_tools = [
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
            "AutoCAD",
            "Revit",
            "STAAD Pro",
            "SQL",
            "MySQL",
            "PostgreSQL",
            "MongoDB",
            "Redis",
            "Kafka",
            "React",
            "Angular",
            "Node.js",
            "Spring Boot"
        ]
        extracted_tools = [tool for tool in potential_tools if re.search(r'\b' + re.escape(tool.lower()) + r'\b', desc_lower)]

        # Detect suggested certifications
        cert_matches = []
        if "aws" in desc_lower:
            cert_matches.append("AWS Certified Solutions Architect")
        if "pmp" in desc_lower or "project management professional" in desc_lower:
            cert_matches.append("PMP Certification")
        if "scrum" in desc_lower:
            cert_matches.append("Scrum Alliance CSM")
            
        # Detect work setting
        work_setting = "On-site"
        if "remote" in desc_lower or "wfh" in desc_lower:
            work_setting = "Remote"
        elif "hybrid" in desc_lower:
            work_setting = "Hybrid"
            
        # Detect company culture traits
        culture_keywords = {
            "Collaborative": ["collaborative", "team", "cooperation", "together"],
            "Fast-paced": ["fast-paced", "rapid", "dynamic", "quick"],
            "Innovative": ["innovative", "innovation", "cutting-edge", "creative"],
            "Diverse": ["diverse", "diversity", "inclusive", "inclusion"],
            "Growth-oriented": ["growth", "learning", "development", "career"]
        }
        extracted_culture = []
        for trait, keys in culture_keywords.items():
            if any(k in desc_lower for k in keys):
                extracted_culture.append(trait)
        # ---------------- SENIORITY ----------------

        seniority = "Not specified"

        if "intern" in desc_lower:
            seniority = "Intern"

        elif "fresher" in desc_lower or "entry level" in desc_lower:
            seniority = "Fresher"

        elif "lead" in desc_lower:
            seniority = "Lead"

        elif "architect" in desc_lower:
            seniority = "Architect"

        elif required_exp != "Not specified":

            years_match = re.search(r"\d+", required_exp)

            if years_match:

                years = int(years_match.group())

                if years <= 1:
                    seniority = "Junior"

                elif years <= 4:
                    seniority = "Mid Level"

                elif years <= 8:
                    seniority = "Senior"

                else:
                    seniority = "Expert"


        # ---------------- SUMMARY ----------------

        summary = (
            f"{title} position requiring {required_exp}, "
            f"{required_edu}, "
            f"{employment_type}, "
            f"located in {location}."
        )
        # Estimate ATS Score rating based on keyword density
        base_score = 50.0
        if len(extracted_skills) > 3:
            base_score += 15.0
        if required_exp != "Not specified":
            base_score += 10.0
        if required_edu != "Not specified":
            base_score += 10.0
        if len(extracted_tools) > 0:
            base_score += 10.0
        ats_score_est = min(base_score, 100.0)

        # Extract responsibilities by looking for bullet points starting with active verbs
        responsibilities = []
        lines = description.split("\n")
        for line in lines:
            line_clean = line.strip()
            if line_clean.startswith(("-", "*", "•")):
                content = line_clean.lstrip("-*• ").strip()
                if content and len(content) > 15:
                    responsibilities.append(content)
                    
        if not responsibilities:
            responsibilities = ["Analyze business requirements and collaborate with the engineering team."]
            
        return {
            "title": title,
            "location": location,
            "salary": salary,
            "employment_type": employment_type,
            "required_experience": required_exp,
            "required_education": required_edu,
            "preferred_education": preferred_edu,
            "seniority": seniority,
            "summary": summary,
            "extracted_skills": sorted(list(set(extracted_skills))),
            "required_skills": sorted(list(set(required_skills))),
            "preferred_skills": sorted(list(set(preferred_skills))),
            "ats_keywords": sorted(list(set(extracted_skills + [title]))),
            "required_experience": required_exp,
            "responsibilities": responsibilities[:8],
            "required_education": required_edu,
            "preferred_education": preferred_edu,
            "tools_and_technologies": sorted(extracted_tools),
            "suggested_certifications": sorted(cert_matches),
            "work_setting": work_setting,
            "company_culture": sorted(extracted_culture),
            "ats_score_estimate": ats_score_est,
            "confidence": 0.50,
            "reasoning": ["Offline heuristic parser based on dictionary matching and regex rules."]
        }
