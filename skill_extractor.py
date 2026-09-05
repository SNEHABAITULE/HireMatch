from pypdf import PdfReader

reader = PdfReader("resumes/RESUME.pdf")

resume_text = ""

for page in reader.pages:
    if page.extract_text():
        resume_text += page.extract_text() + " "

skills = [
    "python",
    "sql",
    "pandas",
    "numpy",
    "flask",
    "machine learning",
    "scikit-learn",
    "tensorflow",
    "java",
    "c++",
    "excel",
    "power bi"
]

resume_text = resume_text.lower()

found_skills = []

for skill in skills:
    if skill in resume_text:
        found_skills.append(skill)
        
print("Skills Found: ")
for skill in found_skills:
    print("-",skill)
    