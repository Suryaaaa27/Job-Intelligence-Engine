from pipeline.scraping_pipeline import ScrapingPipeline


if __name__ == "__main__":

    queries = [

        "Machine Learning Engineer",

        "Software Engineer",

        "Data Scientist",

        "Data Analyst",

        "DevOps Engineer"

    ]

    pipeline = ScrapingPipeline()

    pipeline.run(queries)
