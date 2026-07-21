from pipeline.resume_pipeline import ResumePipeline

resume = ResumePipeline.execute("data/resume.pdf")

print("=" * 60)
print("Candidate Name :", resume.candidate_name)
print("Summary Exists :", bool(resume.summary))
print("Skills         :", len(resume.skills))
print("Experience     :", len(resume.experience))
print("Projects       :", len(resume.projects))
print("Education      :", len(resume.education))
print("Certifications :", len(resume.certifications))
print("=" * 60)

print("\nTop 10 Skills:")
for skill in resume.skills[:10]:
    print("-", skill)

print("\nExperience:")
for exp in resume.experience:
    print(f"- {exp.title} @ {exp.company}")

print("\n")
print("=" * 60)
print("FULL STRUCTURED RESUME JSON")
print("=" * 60)

# Pydantic v2
print(resume.model_dump_json(indent=2))

# If you're on Pydantic v1, use this instead:
# print(resume.json(indent=2))