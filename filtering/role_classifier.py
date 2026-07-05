import json


def classify_role(job):

    with open("config/roles.json", "r") as file:
        roles = json.load(file)

    content = (
        job["title"] + " " +
        job["description"]
    ).lower()

    best_role = None
    best_score = -999

    for role_name, role_data in roles.items():

        score = 0

        for keyword in role_data["positive_keywords"]:

            if keyword in content:
                score += 1

        if score > best_score:
            best_score = score
            best_role = role_name

    return best_role