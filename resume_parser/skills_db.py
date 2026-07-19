"""Starter skill lexicon for resume parsing."""

KNOWN_SKILLS = {
    "python", "java", "javascript", "typescript", "c++", "c#", "c", "go", "golang",
    "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "sql", "bash",
    "perl", "objective-c", "dart", "html", "css", "react", "react.js", "angular", "vue",
    "vue.js", "next.js", "nextjs", "svelte", "redux", "tailwind", "bootstrap", "jquery",
    "webpack", "node.js", "nodejs", "express", "django", "flask", "fastapi", "spring",
    "spring boot", ".net", "asp.net", "rails", "ruby on rails", "graphql", "rest",
    "restful api", "grpc", "pandas", "numpy", "scikit-learn", "sklearn", "tensorflow",
    "pytorch", "keras", "opencv", "nltk", "spacy", "huggingface", "transformers", "llm",
    "nlp", "machine learning", "deep learning", "data science", "data analysis",
    "computer vision", "generative ai", "prompt engineering", "langchain", "mysql",
    "postgresql", "postgres", "mongodb", "redis", "sqlite", "oracle", "cassandra",
    "dynamodb", "elasticsearch", "neo4j", "firebase", "aws", "azure", "gcp",
    "google cloud", "docker", "kubernetes", "k8s", "terraform", "ansible", "jenkins",
    "ci/cd", "github actions", "gitlab ci", "cloudformation", "linux", "nginx",
    "microservices", "serverless", "git", "github", "gitlab", "jira", "agile", "scrum",
    "kanban", "figma", "postman", "swagger", "unit testing", "pytest", "junit", "selenium",
    "tdd", "ci", "cd", "cybersecurity", "penetration testing", "owasp", "siem",
    "network security", "encryption", "iam",
}

import re


def find_skills_in_text(text: str) -> list:
    if not text:
        return []
    lower_text = text.lower()
    found = []
    seen = set()
    for skill in sorted(KNOWN_SKILLS, key=len, reverse=True):
        if skill in seen:
            continue
        if re.search(r"[^\w\s]", skill):
            match = skill in lower_text
        else:
            match = re.search(r"\b" + re.escape(skill) + r"\b", lower_text) is not None
        if match:
            found.append(skill)
            seen.add(skill)
    return found
