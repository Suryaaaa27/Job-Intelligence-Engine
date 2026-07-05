import json
import os


class QueryManager:

    def __init__(self):

        base_dir = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )

        path = os.path.join(
            base_dir,
            "config",
            "search_queries.json"
        )

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            self.queries = json.load(f)

    def get_queries(self, role_name):

        return self.queries.get(
            role_name,
            []
        )

    def get_all_roles(self):

        return list(self.queries.keys())