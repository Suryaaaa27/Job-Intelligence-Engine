def relevance_score(job, target_skills):

    content = (
        job["title"] + " " +
        job["description"]
    ).lower()

    matches = 0

    for skill in target_skills:

        if skill.lower() in content:
            matches += 1

    score = round(
        (matches / len(target_skills)) * 100,
        2
    )

    return score