import json
import os
import re
from difflib import SequenceMatcher

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

    def _title_similarity(self, t1, t2):
        # Remove parenthetical details for better matching
        t1_clean = re.sub(r'[\(\[\{].*?[\)\]\}]', '', t1.lower())
        t2_clean = re.sub(r'[\(\[\{].*?[\)\]\}]', '', t2.lower())
        return SequenceMatcher(None, t1_clean.strip(), t2_clean.strip()).ratio()

    def classify_job(self, title, description):
        title = title or ""
        description = description or ""
        
        title_lower = title.lower()
        description_lower = description.lower()
        combined_content = f"{title_lower} {description_lower}"

        results = {}
        role_matches = {}

        for role_name, role_data in self.roles.items():
            score = 0
            matched_keywords = []

            # 1. Job Title Matching (Highest Priority)
            # Check for exact or highly similar matches in defined job titles
            title_match_score = 0
            for taxonomy_title in role_data.get("job_titles", []):
                tax_lower = taxonomy_title.lower()
                
                # Direct substring match in title
                if tax_lower in title_lower:
                    title_match_score = max(title_match_score, 40)
                    matched_keywords.append(f"title_substring:{taxonomy_title}")
                
                # Sequence similarity check
                sim = self._title_similarity(title, taxonomy_title)
                if sim > 0.8:
                    title_match_score = max(title_match_score, int(sim * 60))
                    matched_keywords.append(f"title_similarity:{taxonomy_title}({round(sim, 2)})")

            score += title_match_score

            # 2. Positive Keywords (Medium Priority)
            for keyword in role_data.get("positive_keywords", []):
                kw_lower = keyword.lower()
                # If keyword matches as a full word boundary
                if re.search(r'\b' + re.escape(kw_lower) + r'\b', combined_content):
                    score += 5
                    matched_keywords.append(keyword)
                # Fallback to simple substring match if it's not a word (e.g. acronyms / technologies)
                elif kw_lower in combined_content:
                    score += 2
                    matched_keywords.append(keyword)

            # 3. Negative Keywords (Penalty)
            for keyword in role_data.get("negative_keywords", []):
                kw_lower = keyword.lower()
                if re.search(r'\b' + re.escape(kw_lower) + r'\b', combined_content):
                    score -= 20
                elif kw_lower in combined_content:
                    score -= 10

            results[role_name] = score
            role_matches[role_name] = matched_keywords

        # Predict role with the highest score
        best_role = max(results, key=results.get)
        best_score = results[best_role]

        # Classification threshold
        if best_score <= 10:
            return {
                "predicted_role": "Unknown",
                "score": 0,
                "matched_keywords": [],
                "scores": results
            }

        return {
            "predicted_role": best_role,
            "score": best_score,
            "matched_keywords": role_matches[best_role],
            "scores": results
        }