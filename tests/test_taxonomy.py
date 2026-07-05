from taxonomy.role_manager import RoleManager

rm = RoleManager()

test_jobs = [

    {
        "title": "Generative AI Engineer",
        "description": "Building RAG systems with LangChain and LLMs"
    },

    {
        "title": "Applied Scientist",
        "description": "Researching transformer models and NLP"
    },

    {
        "title": "Growth Marketing Manager",
        "description": "SEO PPC campaign optimization"
    },

    {
        "title": "YouTube Content Creator",
        "description": "Create engaging videos and manage social channels"
    }
]
for job in test_jobs:

    result = rm.classify_job(
        job["title"],
        job["description"]
    )

    print("\n----------------")
    print(job["title"])
    print(result)