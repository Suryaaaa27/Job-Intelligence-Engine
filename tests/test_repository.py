import os
import sys
import tempfile
import shutil

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from storage.job_repository import JobRepository
from scraper.models import Job

def run_tests():
    # Create temporary directory for test DB — no side effects on production DB
    tmpdir = tempfile.mkdtemp()
    db_file = os.path.join(tmpdir, "test_jobs.db")
    
    try:
        # Use constructor parameter instead of mutating class variable
        repo = JobRepository(db_path=db_file)
        
        # Test 1: dicts
        jobs = [
            {
                "title": "Machine Learning Engineer",
                "company": "Google",
                "description": "Python developer",
                "url": "https://google.com/ml-job",
                "location": "Mountain View, CA",
                "posted_date": "2026-07-07",
                "predicted_role": "AIML Engineer",
                "match_score": 90.0,
                "min_salary": 120000,
                "max_salary": 160000,
                "currency": "USD",
                "job_type": "Full-time",
                "source": "TestSource"
            },
            {
                "title": "Data Analyst",
                "company": "Facebook",
                "description": "SQL analyst",
                "url": "https://facebook.com/da-job",
                "location": "Remote",
                "posted_date": "2026-07-06",
                "predicted_role": "Data Analyst",
                "match_score": 80.0,
                "min_salary": 90000,
                "max_salary": 110000,
                "currency": "USD",
                "job_type": "Remote",
                "source": "TestSource"
            }
        ]
        
        repo.save(jobs)
        
        loaded = repo.load()
        assert len(loaded) == 2, f"Expected 2 jobs, got {len(loaded)}"
        
        ml_jobs = repo.load(role="AIML Engineer")
        assert len(ml_jobs) == 1, f"Expected 1 AIML job, got {len(ml_jobs)}"
        assert ml_jobs[0]["company"] == "Google"
        assert ml_jobs[0]["min_salary"] == 120000.0
        
        # Test 2: dataclasses
        job_obj = Job(
            job_title="Software Architect",
            company_name="Amazon",
            job_url="https://amazon.com/architect",
            location="Seattle, WA",
            description="System architecture design",
            source_platform="TestSource"
        )
        # Manually set prediction attributes
        job_obj.predicted_role = "Software Engineer"
        job_obj.match_score = 75.0
        
        repo.save(job_obj)
        
        loaded_all = repo.load()
        assert len(loaded_all) == 3, f"Expected 3 jobs, got {len(loaded_all)}"
        
        architect_job = [j for j in loaded_all if j["title"] == "Software Architect"]
        assert len(architect_job) == 1
        assert architect_job[0]["company"] == "Amazon"
        assert architect_job[0]["description"] == "System architecture design"
        assert architect_job[0]["predicted_role"] == "Software Engineer"
        assert architect_job[0]["match_score"] == 75.0

        # Test 3: get_by_id
        architect_id = architect_job[0]["id"]
        fetched = repo.get_by_id(architect_id)
        assert fetched is not None
        assert fetched["title"] == "Software Architect"

        # Test 4: search
        search_res = repo.search(role="AIML Engineer")
        assert len(search_res) == 1
        assert search_res[0]["company"] == "Google"

        search_res_salary = repo.search(min_salary=100000)
        assert len(search_res_salary) == 2
        companies = [j["company"] for j in search_res_salary]
        assert "Google" in companies
        assert "Facebook" in companies

        # Test 5: get_stats
        stats = repo.get_stats()
        assert stats["total_jobs"] == 3
        assert stats["roles_distribution"]["AIML Engineer"] == 1
        assert stats["platforms_distribution"]["TestSource"] == 3
        assert stats["average_salary"]["AIML Engineer"] == 140000.0

        print("All repository tests passed!")
        
    finally:
        # Clean up temporary directory
        shutil.rmtree(tmpdir)

if __name__ == "__main__":
    run_tests()
