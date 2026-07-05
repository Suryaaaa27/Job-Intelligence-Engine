import json
import os


class RoleManager:

    def __init__(self):

        base_dir = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )

        roles_path = os.path.join(
            base_dir,
            "config",
            "roles.json"
        )

        with open(
            roles_path,
            "r",
            encoding="utf-8"
        ) as f:

            self.roles = json.load(f)

    def get_all_roles(self):
        return list(self.roles.keys())

    def get_role_data(self, role_name):
        return self.roles.get(role_name)

    def classify_job(self, title, description):

        title_lower = title.lower()
        description_lower = description.lower()

        content = f"{title_lower} {description_lower}"

        results = {}
        role_matches = {}

        for role_name, role_data in self.roles.items():

            score = 0

            matched_keywords = []

            # -------------------------
            # Job Title Matching
            # -------------------------

            for job_title in role_data.get(
                "job_titles",
                []
            ):

                if job_title.lower() in title_lower:

                    score += 15

                    matched_keywords.append(
                        f"title:{job_title}"
                    )

            # -------------------------
            # Positive Keywords
            # -------------------------

            for keyword in role_data.get(
                "positive_keywords",
                []
            ):

                if keyword.lower() in content:

                    score += 5

                    matched_keywords.append(
                        keyword
                    )

            # -------------------------
            # Negative Keywords
            # -------------------------

            for keyword in role_data.get(
                "negative_keywords",
                []
            ):

                if keyword.lower() in content:

                    score -= 10

            results[role_name] = score

            role_matches[role_name] = matched_keywords

        best_role = max(
            results,
            key=results.get
        )

        best_score = results[best_role]

        if best_score <= 0:

            return {
                "predicted_role": "Unknown",
                "score": 0,
                "matched_keywords": [],
                "scores": results
            }

        return {
            "predicted_role": best_role,
            "score": best_score,
            "matched_keywords": role_matches[
                best_role
            ],
            "scores": results
        }