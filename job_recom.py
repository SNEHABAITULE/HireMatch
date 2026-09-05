import pandas as pd
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

pdf_path = "resumes/resume.pdf"
reader = PdfReader(pdf_path)
resume_text = ""

for page in reader.pages:
    text = page.extract_text()
    if text:
        resume_text += text + " "
        
jobs = pd.read_csv("data/jobs.csv")

jobs["description"] = jobs["description"].fillna("")

documents = [resume_text] + jobs["description"].tolist()

vectorizer = TfidfVectorizer()
vectors = vectorizer.fit_transform(documents)

resume_vector = vectors[0]
job_vectors = vectors[1:]

scores = cosine_similarity(resume_vector, job_vectors)[0]
jobs["match_score"] = scores * 100

jobs = jobs.sort_values(
    by="match_score",
    ascending=False
)


print("\n--------HIREMATCH: TOP 5 JOBS---------\n")

for _, job in jobs.head(5).iterrows():
    print(f"{job['job_title']} - {job['company']}")
    print(f"Location: {job['location']}")
    print(f"Work Mode: {job['work_mode']}")
    print(f"Match Score: {job['match_score']:.2f}%")
    print("-" * 40)

