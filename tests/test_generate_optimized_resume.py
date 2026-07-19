import unittest

from generate_optimized_resume import select_job_from_report


class GenerateOptimizedResumeTests(unittest.TestCase):
    def test_select_job_from_report_uses_report_index(self):
        raw_jobs = [
            {"job_id": "1", "job_title": "First Role", "description": "A"},
            {"job_id": "2", "job_title": "Best Role", "description": "B"},
        ]
        report = [
            {"index": 1, "match_score": 93.4, "job_title": "Best Role", "ats_report": {"missing_skills": ["Python"], "missing_keywords": ["ML"]}},
        ]

        selected = select_job_from_report(raw_jobs, report)

        self.assertEqual(selected["job_id"], "2")


if __name__ == "__main__":
    unittest.main()
