from services.resume_service import ResumeService

resume = ResumeService.parse("data/resume.pdf")

print("="*50)
print("Candidate:", resume.candidate_name)
print("Summary:", bool(resume.summary))
print("Skills:", len(resume.skills))
print("Experience:", len(resume.experience))
print("Projects:", len(resume.projects))
print("Education:", len(resume.education))
print("Certifications:", len(resume.certifications))
print("="*50)