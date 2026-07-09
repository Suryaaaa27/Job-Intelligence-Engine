from analysis.analyzer import JDAnalyzer


class ATSOptimizer:

    def __init__(self):
        self.analyzer = JDAnalyzer()

    def calculate_match_score(self, resume_text, job_analysis):
        """
        Calculate an ATS match score comparing resume text against extracted job analysis.
        """
        if not resume_text or not job_analysis:
            return 0.0

        required_skills = [s.lower() for s in job_analysis.get("required_skills", [])]
        ats_keywords = [k.lower() for k in job_analysis.get("ats_keywords", [])]
        
        if not required_skills and not ats_keywords:
            return 0.0

        resume_text_lower = resume_text.lower()
        matched_required = [s for s in required_skills if s in resume_text_lower]
        matched_keywords = [k for k in ats_keywords if k in resume_text_lower]

        total_keys = len(required_skills) + len(ats_keywords)
        if total_keys == 0:
            return 100.0

        total_matches = len(matched_required) + len(matched_keywords)
        score = round((total_matches / total_keys) * 100, 2)
        return score

    def suggest_improvements(self, resume_text, job_analysis):
        """
        Find missing ATS keywords and skills to improve match rating.
        """
        if not resume_text or not job_analysis:
            return {"missing_skills": [], "missing_keywords": [], "recommendation": "Please upload a resume."}

        required_skills = job_analysis.get("required_skills", [])
        ats_keywords = job_analysis.get("ats_keywords", [])
        
        resume_text_lower = resume_text.lower()
        missing_skills = [s for s in required_skills if s.lower() not in resume_text_lower]
        missing_keywords = [k for k in ats_keywords if k.lower() not in resume_text_lower]

        recommendation = ""
        if missing_skills or missing_keywords:
            recommendation = f"Integrate these missing skills: {', '.join(missing_skills[:5])} to pass standard ATS screening."
        else:
            recommendation = "Excellent resume match! No critical optimizations required."

        return {
            "missing_skills": missing_skills,
            "missing_keywords": missing_keywords,
            "recommendation": recommendation
        }
