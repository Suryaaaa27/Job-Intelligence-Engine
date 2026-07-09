from analysis.analyzer import JDAnalyzer
import os
import json


class SkillExtractor:

    def __init__(self):
        self.analyzer = JDAnalyzer()
        # Fallback static list
        self.static_skills = [
            "Python", "Java", "TensorFlow", "PyTorch", "Scikit-learn",
            "LangChain", "OpenAI", "Gemini", "Docker", "AWS", "Azure",
            "SQL", "MongoDB", "RAG", "LLM", "NLP", "Computer Vision"
        ]

    def extract(self, description):
        """
        Extract skills from job description text.
        Tries to use the full AI analyzer first, falling back to static lookup.
        """
        # Try dynamic extraction
        try:
            analysis = self.analyzer.analyze("Job Title", description)
            skills = analysis.get("extracted_skills", [])
            if skills:
                return sorted(list(set(skills)))
        except Exception:
            pass

        # Fallback to static list lookup
        found = []
        text = description.lower()
        for skill in self.static_skills:
            if skill.lower() in text:
                found.append(skill)
        return sorted(list(set(found)))