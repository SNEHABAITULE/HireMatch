from pypdf import PdfReader


pdf_path = "resumes/resume.pdf"
reader = PdfReader(pdf_path)

resume_text = ""

for page in reader.pages:
    text = page.extract_text()

    if text:
        resume_text += text + " "

resume_text = resume_text.lower()

required_skills = [
    "python",
    "sql",
    "pandas",
    "flask",
    "django",
    "git",
    "docker",
    "aws",
    "machine learning",
    "scikit-learn"
]

matched = []
missing = []

for skill in required_skills:

    if skill in resume_text:
        matched.append(skill)
    else:
        missing.append(skill)


print("\n-------SKILL GAP ANALYSIS------")

print("\nMatched Skills:")
for skill in matched:
    print("✅", skill)

print("\nMissing Skills:")
for skill in missing:
    print("❌", skill)