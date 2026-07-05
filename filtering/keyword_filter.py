import json


def load_role(role_name):

    with open("config/roles.json", "r") as file:
        roles = json.load(file)

    return roles.get(role_name)


def keyword_filter(job, role_name):

    role = load_role(role_name)

    score = 0

    content = (
        job["title"] + " " +
        job["description"]
    ).lower()

    for keyword in role["positive_keywords"]:

        if keyword.lower() in content:
            score += 5

    for keyword in role["negative_keywords"]:

        if keyword.lower() in content:
            score -= 10

    return score