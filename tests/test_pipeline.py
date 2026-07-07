import os
import sys
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from services.pipeline_service import PipelineService

pipeline = PipelineService()

jobs = pipeline.run("AIML Engineer")

print()
print("=" * 60)
print(f"TOTAL JOBS : {len(jobs)}")
print("=" * 60)

for job in jobs:
    # After cleaning, jobs are dicts
    if isinstance(job, dict):
        title = job.get("title", "")
        role = job.get("predicted_role", "Unknown")
        score = job.get("match_score", 0)
        salary = f"${job.get('min_salary', 'N/A')} - ${job.get('max_salary', 'N/A')}" if job.get("min_salary") else "N/A"
        source = job.get("source", "Unknown")
    else:
        title = getattr(job, "job_title", getattr(job, "title", ""))
        role = getattr(job, "predicted_role", "Unknown")
        score = getattr(job, "match_score", 0)
        salary = "N/A"
        source = getattr(job, "source_platform", "Unknown")

    print(f"  {title}")
    print(f"    Role: {role} | Score: {score} | Salary: {salary} | Source: {source}")
    print("-" * 40)