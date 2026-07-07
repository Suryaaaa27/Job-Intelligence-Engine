from fastapi import FastAPI, BackgroundTasks, Query, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import os
import sys

# Ensure root is visible
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from storage.job_repository import JobRepository
from services.pipeline_service import PipelineService

app = FastAPI(
    title="Job Intelligence Engine API",
    description="Data query and pipeline triggering service for Team A (Data Intelligence Team)",
    version="1.0.0"
)

repository = JobRepository()

class PipelineRunRequest(BaseModel):
    role: str

# In-memory status tracker for running pipelines
pipeline_runs = {}

def run_pipeline_task(role: str, task_id: str):
    pipeline_runs[task_id] = "RUNNING"
    try:
        pipeline = PipelineService()
        pipeline.run(role)
        pipeline_runs[task_id] = "COMPLETED"
    except Exception as e:
        pipeline_runs[task_id] = f"FAILED: {str(e)}"

@app.get("/jobs", response_model=List[Dict[str, Any]])
def get_jobs(
    role: Optional[str] = Query(None, description="Filter by classified role"),
    source: Optional[str] = Query(None, description="Filter by scraper source platform"),
    location: Optional[str] = Query(None, description="Filter by location (fuzzy substring)"),
    job_type: Optional[str] = Query(None, description="Filter by job type (e.g. Full-time, Remote)"),
    min_salary: Optional[float] = Query(None, description="Filter for jobs matching at least this salary"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(20, ge=1, le=100, description="Limit for pagination")
):
    """Retrieve structured, cleaned, and classified jobs matching query criteria."""
    try:
        return repository.search(
            role=role,
            source=source,
            location=location,
            job_type=job_type,
            min_salary=min_salary,
            offset=offset,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs/{job_id}", response_model=Dict[str, Any])
def get_job_by_id(job_id: int):
    """Retrieve detailed information of a specific job by its database ID."""
    job = repository.get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job with ID {job_id} not found")
    return job

@app.get("/stats")
def get_stats():
    """Get aggregated metrics and statistics on scraped jobs."""
    try:
        return repository.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/pipeline/run")
def trigger_pipeline(request: PipelineRunRequest, background_tasks: BackgroundTasks):
    """
    Trigger the scraper & data intelligence pipeline for a specific role in a background task.
    Returns immediately with a status tracking key.
    """
    import uuid
    task_id = str(uuid.uuid4())
    pipeline_runs[task_id] = "QUEUED"
    
    background_tasks.add_task(run_pipeline_task, request.role, task_id)
    
    return {
        "status": "QUEUED",
        "task_id": task_id,
        "message": f"Pipeline execution started in background for role: {request.role}"
    }

@app.get("/pipeline/status/{task_id}")
def get_pipeline_status(task_id: str):
    """Check the execution status of a background pipeline run."""
    status = pipeline_runs.get(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task ID not found")
    return {"task_id": task_id, "status": status}

if __name__ == "__main__":
    host = os.environ.get("API_HOST", "127.0.0.1")
    port = int(os.environ.get("API_PORT", "8000"))
    uvicorn.run("services.app_api:app", host=host, port=port, reload=False)
