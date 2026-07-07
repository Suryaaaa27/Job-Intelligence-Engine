import json
import os

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ROLES_PATH = os.path.join(_PROJECT_ROOT, "config", "roles.json")


def load_role(role_name):

    with open(_ROLES_PATH, "r", encoding="utf-8") as file:
        roles = json.load(file)

    return roles.get(role_name)


def keyword_filter(job, role_name):

    role = load_role(role_name)

    if not role:
        return 0

    score = 0

    title = job.get("title", "") if isinstance(job, dict) else getattr(job, "title", "")
    desc = job.get("description", "") if isinstance(job, dict) else getattr(job, "description", "")
    content = f"{title} {desc}".lower()

    for keyword in role.get("positive_keywords", []):

        if keyword.lower() in content:
            score += 5

    for keyword in role.get("negative_keywords", []):

        if keyword.lower() in content:
            score -= 10

    return score