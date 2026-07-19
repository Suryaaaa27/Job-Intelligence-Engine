"""
Minimal local FastAPI server to view Group E match results in a browser.
Run with: uvicorn services.resume_optimizer.api:app --reload
Then open: http://127.0.0.1:8000/match
"""

from fastapi import FastAPI
from services.resume_optimizer.service import load_jd_from_json, load_resume_from_json
from services.resume_optimizer.matcher import calculate_match

app = FastAPI(title="Group E - Resume Optimizer")


@app.get("/")
def root():
    return {"status": "Group E API is running"}


@app.get("/match")
def get_match():
    jd = load_jd_from_json("data/samples/sample_jd.json")
    resume = load_resume_from_json("data/samples/sample_resume.json")
    result = calculate_match(jd, resume)
    return result.model_dump()
