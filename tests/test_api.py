import os
import sys
import tempfile
import shutil
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Create a temporary test DB using constructor parameter — no production side effects
_tmpdir = tempfile.mkdtemp()
_test_db = os.path.join(_tmpdir, "test_api.db")

from storage.job_repository import JobRepository
test_repo = JobRepository(db_path=_test_db)

# Mock PipelineService.run to prevent real scraping during API tests
import services.pipeline_service
services.pipeline_service.PipelineService.run = MagicMock(return_value=[])

# Seed test database with known entries
test_repo.save([
    {
        "title": "Staff ML Engineer",
        "company": "Google",
        "description": "Python, TensorFlow, NLP research.",
        "url": "https://google.com/ml-1",
        "location": "Mountain View, CA",
        "posted_date": "2026-07-07",
        "predicted_role": "AIML Engineer",
        "match_score": 95.0,
        "min_salary": 150000,
        "max_salary": 200000,
        "currency": "USD",
        "job_type": "Full-time",
        "source": "TestSource"
    },
    {
        "title": "Lead SEO Specialist",
        "company": "Growth Inc",
        "description": "Search engine optimization and performance marketing.",
        "url": "https://growth.com/seo-1",
        "location": "Remote",
        "posted_date": "2026-07-06",
        "predicted_role": "Digital Marketing",
        "match_score": 85.0,
        "min_salary": 80000,
        "max_salary": 100000,
        "currency": "USD",
        "job_type": "Remote",
        "source": "TestSource"
    }
])

import services.app_api
services.app_api.repository = test_repo

from services.app_api import app

client = TestClient(app)

def test_api_endpoints():
    # 1. Get jobs
    response = client.get("/jobs")
    assert response.status_code == 200
    jobs = response.json()
    assert len(jobs) == 2
    
    # 2. Get jobs with filters
    response = client.get("/jobs?role=AIML Engineer")
    assert response.status_code == 200
    jobs = response.json()
    assert len(jobs) == 1
    assert jobs[0]["company"] == "Google"

    # 3. Get job details
    job_id = jobs[0]["id"]
    response = client.get(f"/jobs/{job_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Staff ML Engineer"

    # 4. Get job details 404
    response = client.get("/jobs/9999")
    assert response.status_code == 404

    # 5. Get stats
    response = client.get("/stats")
    assert response.status_code == 200
    stats = response.json()
    assert stats["total_jobs"] == 2
    assert stats["roles_distribution"]["AIML Engineer"] == 1
    assert stats["roles_distribution"]["Digital Marketing"] == 1

    # 6. Trigger pipeline background run (mock status check)
    response = client.post("/pipeline/run", json={"role": "Content Creator"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "QUEUED"
    assert "task_id" in data
    
    task_id = data["task_id"]
    response = client.get(f"/pipeline/status/{task_id}")
    assert response.status_code == 200
    assert response.json()["status"] in ["QUEUED", "RUNNING", "COMPLETED"]

    print("All API integration tests passed successfully!")

if __name__ == "__main__":
    try:
        test_api_endpoints()
    finally:
        # Clean up temp directory
        shutil.rmtree(_tmpdir, ignore_errors=True)
