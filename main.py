import json
import sys

from preprocessing.cleaner import clean_job
from preprocessing.deduplicator import remove_duplicates
from taxonomy.role_manager import RoleManager
from filtering.keyword_filter import keyword_filter
from filtering.scorer import relevance_score


def load_jobs():
    with open("data/raw_jobs.json", "r") as file:
        return json.load(file)


def save_jobs(jobs):
    with open("data/filtered_jobs.json", "w") as file:
        json.dump(jobs, file, indent=4)


def main():
    # Accept role from CLI args, default to first role in config
    rm = RoleManager()
    available_roles = rm.get_all_roles()

    if len(sys.argv) > 1:
        target_role = sys.argv[1]
    elif available_roles:
        target_role = available_roles[0]
    else:
        print("No roles configured in config/roles.json")
        return

    # Get skills for the target role from config
    role_data = rm.get_role_data(target_role)
    if not role_data:
        print(f"Role '{target_role}' not found. Available: {available_roles}")
        return

    target_skills = role_data.get("skills", [])

    print(f"\nTarget Role: {target_role}")
    print(f"Target Skills: {target_skills}\n")

    jobs = load_jobs()

    jobs = [clean_job(job) for job in jobs]

    jobs = remove_duplicates(jobs)

    shortlisted = []

    for job in jobs:

        filter_score = keyword_filter(job, target_role)

        if filter_score <= 0:
            continue

        role_info = rm.classify_job(
            job["title"],
            job["description"]
        )
        role = role_info["predicted_role"]

        match_score = relevance_score(job, target_skills)

        job["role"] = role
        job["match_score"] = match_score

        shortlisted.append(job)

    save_jobs(shortlisted)

    print(f"{len(shortlisted)} jobs shortlisted.")


if __name__ == "__main__":
    main()

    # Show available roles for reference
    rm = RoleManager()
    print("\nAvailable Roles:\n")
    for role in rm.get_all_roles():
        print(f"  - {role}")