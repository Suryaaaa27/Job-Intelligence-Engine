import json

from preprocessing.cleaner import clean_job
from preprocessing.deduplicator import remove_duplicates
from taxonomy.role_manager import RoleManager
from filtering.keyword_filter import keyword_filter
from filtering.role_classifier import classify_role
from filtering.scorer import relevance_score


TARGET_ROLE = "AIML Engineer"

TARGET_SKILLS = [
    "Python",
    "Machine Learning",
    "NLP",
    "LangChain",
    "RAG",
    "TensorFlow"
]


def load_jobs():

    with open("data/machine_learning_engineer_20260711_200219.json", "r", encoding="utf-8") as file:
        return json.load(file)


def save_jobs(jobs):

    with open("data/filtered_jobs.json", "w", encoding="utf-8") as file:
        json.dump(
            jobs,
            file,
            indent=4
        )


def main():

    jobs = load_jobs()

    jobs = [clean_job(job) for job in jobs]

    jobs = remove_duplicates(jobs)

    shortlisted = []

    for job in jobs:

        filter_score = keyword_filter(
            job,
            TARGET_ROLE
        )

        if filter_score <= 0:
            continue

        role = classify_role(job)

        match_score = relevance_score(
            job,
            TARGET_SKILLS
        )

        job["role"] = role
        job["match_score"] = match_score

        shortlisted.append(job)

    save_jobs(shortlisted)

    print(
        f"{len(shortlisted)} jobs shortlisted."
    )
rm = RoleManager()

print("\nAvailable Roles:\n")

for role in rm.get_all_roles():
    print(role)

if __name__ == "__main__":
    main()