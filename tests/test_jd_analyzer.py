import os
import sys
import tempfile
import shutil
import unittest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from analysis.analyzer import JDAnalyzer
from analysis.requirement_extractor import RequirementExtractor
from analysis.ats_optimizer import ATSOptimizer
from storage.job_repository import JobRepository


class TestJDIntelligence(unittest.TestCase):

    def setUp(self):
        # Temporarily clear LLM keys to ensure tests run against fallback deterministically
        self.original_gemini_key = os.environ.get("GEMINI_API_KEY")
        self.original_openai_key = os.environ.get("OPENAI_API_KEY")
        if "GEMINI_API_KEY" in os.environ:
            del os.environ["GEMINI_API_KEY"]
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]

        self.tmpdir = tempfile.mkdtemp()
        self.db_file = os.path.join(self.tmpdir, "test_analysis.db")
        self.repo = JobRepository(db_path=self.db_file)
        
        # Seed a test job description
        self.job_title = "Staff Machine Learning Engineer"
        self.job_desc = (
            "We are looking for a Staff Machine Learning Engineer.\n"
            "Requirements:\n"
            "- Must have 5+ years of experience in Python and TensorFlow.\n"
            "- Solid understanding of deep learning and NLP architectures.\n"
            "- Bachelor's degree in Computer Science.\n"
            "Nice to have:\n"
            "- Experience with Docker, AWS, and PyTorch is a plus.\n"
            "Responsibilities:\n"
            "- Build and maintain core machine learning pipeline APIs.\n"
            "- Collaborate with data engineers and product stakeholders."
        )
        self.repo.save({
            "title": self.job_title,
            "company": "TestCorp",
            "description": self.job_desc,
            "url": "https://testcorp.com/ml-engineer",
            "location": "San Francisco, CA",
            "source": "TestSource"
        })
        
        # Load seeded job to get ID
        jobs = self.repo.load()
        self.job_id = jobs[0]["id"]

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        if self.original_gemini_key:
            os.environ["GEMINI_API_KEY"] = self.original_gemini_key
        if self.original_openai_key:
            os.environ["OPENAI_API_KEY"] = self.original_openai_key

    def test_analyzer_fallback(self):
        analyzer = JDAnalyzer()
        # Force fallback parser for testing
        analysis = analyzer._analyze_fallback(self.job_title, self.job_desc)
        
        self.assertGreaterEqual(len(analysis["extracted_skills"]), 2)
        self.assertIn("Python", analysis["extracted_skills"])
        self.assertIn("TensorFlow", analysis["extracted_skills"])
        self.assertIn("PyTorch", analysis["extracted_skills"])
        self.assertEqual(analysis["required_experience"], "5+ Years Of Experience")
        self.assertGreater(len(analysis["responsibilities"]), 0)
        self.assertEqual(analysis["required_education"], "Bachelor's Degree")
        self.assertIn("Docker", analysis["tools_and_technologies"])
        self.assertEqual(analysis["work_setting"], "On-site")
        self.assertGreater(analysis["ats_score_estimate"], 50.0)
        self.assertEqual(analysis["confidence"], 0.5)

    def test_repository_save_and_get_analysis(self):
        analyzer = JDAnalyzer()
        analysis = analyzer._analyze_fallback(self.job_title, self.job_desc)
        
        self.repo.save_analysis(self.job_id, analysis)
        loaded = self.repo.get_analysis(self.job_id)
        
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["job_id"], self.job_id)
        self.assertListEqual(loaded["extracted_skills"], analysis["extracted_skills"])
        self.assertListEqual(loaded["required_skills"], analysis["required_skills"])
        self.assertListEqual(loaded["preferred_skills"], analysis["preferred_skills"])
        self.assertEqual(loaded["required_experience"], "5+ Years Of Experience")
        self.assertListEqual(loaded["responsibilities"], analysis["responsibilities"])
        self.assertEqual(loaded["required_education"], "Bachelor's Degree")
        self.assertEqual(loaded["preferred_education"], "Not specified")
        self.assertListEqual(loaded["tools_and_technologies"], analysis["tools_and_technologies"])
        self.assertListEqual(loaded["suggested_certifications"], analysis["suggested_certifications"])
        self.assertEqual(loaded["work_setting"], "On-site")
        self.assertListEqual(loaded["company_culture"], analysis["company_culture"])
        self.assertEqual(loaded["ats_score_estimate"], analysis["ats_score_estimate"])
        self.assertEqual(loaded["confidence"], 0.5)

    def test_requirement_extractor(self):
        extractor = RequirementExtractor()
        requirements = extractor.extract_requirements(self.job_title, self.job_desc)
        
        self.assertEqual(requirements["required_experience"], "5+ Years Of Experience")
        self.assertIn("Python", requirements["required_skills"])
        self.assertIn("PyTorch", requirements["preferred_skills"])

    def test_ats_optimizer(self):
        analyzer = JDAnalyzer()
        analysis = analyzer._analyze_fallback(self.job_title, self.job_desc)
        optimizer = ATSOptimizer()
        
        # 1. Test poor resume matching
        poor_resume = "Experienced developer familiar with Java and SQL."
        score1 = optimizer.calculate_match_score(poor_resume, analysis)
        self.assertLess(score1, 30.0)
        
        # 2. Test perfect/good resume matching
        good_resume = "Machine Learning Engineer with 5 years of Python, TensorFlow, PyTorch, and Docker experience. Build deep learning systems."
        score2 = optimizer.calculate_match_score(good_resume, analysis)
        self.assertGreater(score2, 50.0)
        
        # 3. Test suggestions
        suggestions = optimizer.suggest_improvements(poor_resume, analysis)
        self.assertIn("Python", suggestions["missing_skills"])
        self.assertIn("TensorFlow", suggestions["missing_skills"])


if __name__ == "__main__":
    unittest.main()
