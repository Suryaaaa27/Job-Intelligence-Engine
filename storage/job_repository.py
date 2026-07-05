import json
import os


class JobRepository:

    DATA_PATH = "data/raw_jobs.json"

    def save(self, jobs):

        os.makedirs("data", exist_ok=True)

        with open(

            self.DATA_PATH,

            "w",

            encoding="utf-8"

        ) as f:

            json.dump(

                [job.to_dict() for job in jobs],

                f,

                indent=4,

                ensure_ascii=False

            )

    def load(self):

        if not os.path.exists(self.DATA_PATH):

            return []

        with open(

            self.DATA_PATH,

            "r",

            encoding="utf-8"

        ) as f:

            return json.load(f)