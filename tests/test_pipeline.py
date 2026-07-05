from services.pipeline_service import PipelineService

pipeline = PipelineService()

jobs = pipeline.run("AIML Engineer")

print()

print("=" * 60)

print(f"TOTAL JOBS : {len(jobs)}")

print("=" * 60)

for job in jobs:

    print(job.title)

    print(job.predicted_role)

    print("-" * 40)