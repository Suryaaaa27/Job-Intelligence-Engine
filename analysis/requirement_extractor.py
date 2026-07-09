from analysis.analyzer import JDAnalyzer


class RequirementExtractor:

    def __init__(self):
        self.analyzer = JDAnalyzer()

    def extract_requirements(self, job_title, description):
        """
        Extract required qualifications, experience level, and preferred skills.
        """
        analysis = self.analyzer.analyze(job_title, description)
        return {
            "required_experience": analysis.get("required_experience", "Not specified"),
            "required_skills": analysis.get("required_skills", []),
            "preferred_skills": analysis.get("preferred_skills", []),
            "confidence": analysis.get("confidence", 0.0)
        }
