import sys
import os
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from preprocessing.cleaner import clean_job, extract_salary, standardize_job_type
from preprocessing.deduplicator import remove_duplicates

def test_salary_extraction():
    # Test ranges
    range_text1 = "Salary range is $100k - $130k per year."
    res1 = extract_salary(range_text1)
    assert res1["min_salary"] == 100000
    assert res1["max_salary"] == 130000
    assert res1["currency"] == "USD"

    range_text2 = "We pay £50,000 to £70,000 annually."
    res2 = extract_salary(range_text2)
    assert res2["min_salary"] == 50000
    assert res2["max_salary"] == 70000
    assert res2["currency"] == "GBP"

    # Test single
    single_text = "Competitive pay of €85k base."
    res3 = extract_salary(single_text)
    assert res3["min_salary"] == 85000
    assert res3["max_salary"] == 85000
    assert res3["currency"] == "EUR"


def test_job_type_standardization():
    assert standardize_job_type("Senior Engineer", "This is a part-time position.") == "Part-time"
    assert standardize_job_type("Contract Developer", "Freelance role for 6 months.") == "Contract"
    assert standardize_job_type("AI Intern", "Internship for students.") == "Internship"
    assert standardize_job_type("Remote ML Engineer", "Work from home anywhere.") == "Remote"
    assert standardize_job_type("Staff Scientist", "Full-time employment in the office.") == "Full-time"


def test_fuzzy_deduplication():
    jobs = [
        {
            "title": "Machine Learning Engineer",
            "company": "Google",
            "description": "Python PyTorch NLP experience required for building large language models.",
            "url": "https://google.com/jobs/1"
        },
        # Duplicate by URL
        {
            "title": "ML Engineer (Generative AI)",
            "company": "Alphabet",
            "description": "Different description.",
            "url": "https://google.com/jobs/1"
        },
        # Duplicate by Company & Title similarity
        {
            "title": "Machine Learning Engineer (Generative AI)",
            "company": "Google",
            "description": "Something entirely different.",
            "url": "https://google.com/jobs/2"
        },
        # Duplicate by Description Jaccard overlap + Title similarity
        {
            "title": "ML Engineer",
            "company": "Google",
            "description": "Python PyTorch NLP experience required for building large language models.",
            "url": "https://google.com/jobs/3"
        },
        # Unique job
        {
            "title": "Data Analyst",
            "company": "Google",
            "description": "SQL and Tableau experience required for business intelligence reports.",
            "url": "https://google.com/jobs/4"
        }
    ]
    
    cleaned = [clean_job(j) for j in jobs]
    unique = remove_duplicates(cleaned)
    
    # 1st is added (Google ML Engineer)
    # 2nd is duplicate by URL (Google/Alphabet url 1)
    # 3rd is duplicate by Company & Title similarity (Google ML Engineer vs Google Machine Learning Engineer)
    # 4th is duplicate by Jaccard description overlap + Title similarity
    # 5th is unique (Data Analyst)
    assert len(unique) == 2
    assert unique[0]["title"] == "Machine Learning Engineer"
    assert unique[1]["title"] == "Data Analyst"

if __name__ == "__main__":
    test_salary_extraction()
    test_job_type_standardization()
    test_fuzzy_deduplication()
    print("All deduplicator and cleaner tests passed!")
