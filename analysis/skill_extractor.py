class SkillExtractor:

    def __init__(self):

        self.skills = [

            "Python",
            "Java",

            "TensorFlow",
            "PyTorch",

            "Scikit-learn",

            "LangChain",

            "OpenAI",

            "Gemini",

            "Docker",

            "AWS",

            "Azure",

            "SQL",

            "MongoDB",

            "RAG",

            "LLM",

            "NLP",

            "Computer Vision"

        ]

    def extract(self, description):

        found = []

        text = description.lower()

        for skill in self.skills:

            if skill.lower() in text:

                found.append(skill)

        return sorted(set(found))