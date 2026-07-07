import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from taxonomy.role_manager import RoleManager

def test_classification():
    rm = RoleManager()
    
    # Test case 1: Strong title match for AIML Engineer
    job1 = {
        "title": "Generative AI Engineer (Remote)",
        "description": "Looking for a Python developer with LangChain and RAG experience to build LLM apps."
    }
    res1 = rm.classify_job(job1["title"], job1["description"])
    assert res1["predicted_role"] == "AIML Engineer"
    assert any("Generative AI Engineer" in kw or "title" in kw for kw in res1["matched_keywords"])

    # Test case 2: Title match with negative keyword override
    job2 = {
        "title": "AIML Engineer / Marketing Content Creator",
        "description": "We need a social media marketer to create YouTube videos. Some basic Python AI tools knowledge is a plus, but the main job is marketing, sales and design."
    }
    res2 = rm.classify_job(job2["title"], job2["description"])
    # The negative keywords "marketing", "sales", "design", "content creator" should heavily penalize "AIML Engineer"
    # While "Content Creator" has positive keywords match and no negatives.
    assert res2["predicted_role"] == "Content Creator"

    # Test case 3: Ambiguous or irrelevant job
    job3 = {
        "title": "Executive Assistant",
        "description": "Provide administrative support, manage calendars, and arrange travel."
    }
    res3 = rm.classify_job(job3["title"], job3["description"])
    assert res3["predicted_role"] == "Unknown"

    print("All taxonomy role classification tests passed!")

if __name__ == "__main__":
    test_classification()
