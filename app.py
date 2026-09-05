from flask import Flask, render_template, request
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import os
import re

app = Flask(__name__)

UPLOAD_FOLDER = "resumes"
DATA_FILE = "data/jobs.csv"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

SKILLS = [
    "python",
    "java",
    "c++",
    "javascript",
    "html",
    "css",
    "sql",
    "mysql",
    "pandas",
    "numpy",
    "flask",
    "django",
    "machine learning",
    "deep learning",
    "scikit-learn",
    "tensorflow",
    "pytorch",
    "git",
    "github",
    "docker",
    "aws",
    "power bi",
    "tableau",
    "excel",
    "nlp",
    "data analysis",
    "data science"
]

RESUME_KEYWORDS = [
    "resume",
    "curriculum vitae",
    "education",
    "experience",
    "skills",
    "projects",
    "certifications",
    "objective",
    "summary",
    "internship",
    "academic",
    "qualification"
]


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():

    if "resume" not in request.files:
        return render_template(
            "error.html",
            title="No Resume Uploaded",
            message="Please upload your resume in PDF format."
        )

    file = request.files["resume"]

    if file.filename == "":
        return render_template(
            "error.html",
            title="No File Selected",
            message="Please select a resume before clicking Analyze Resume."
        )

    if not file.filename.lower().endswith(".pdf"):
        return render_template(
            "error.html",
            title="Invalid File",
            message="Please upload a valid resume in PDF format only."
        )

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        file.filename
    )

    file.save(file_path)

    try:
        reader = PdfReader(file_path)

        resume_text = ""

        for page in reader.pages:
            text = page.extract_text()

            if text:
                resume_text += text + " "

    except Exception:
        return render_template(
            "error.html",
            title="Unable to Read Document",
            message="We could not read this PDF. Please upload a valid text-based resume."
        )

    resume_text = resume_text.strip()

    if len(resume_text) < 200:
        return render_template(
            "error.html",
            title="Invalid Resume",
            message="This document does not appear to be a valid resume. Please upload your complete resume."
        )

    text_lower = resume_text.lower()

    keyword_matches = 0

    for keyword in RESUME_KEYWORDS:
        if keyword in text_lower:
            keyword_matches += 1

    skill_matches = []

    for skill in SKILLS:
        if re.search(r"\b" + re.escape(skill) + r"\b", text_lower):
            skill_matches.append(skill)

    if keyword_matches < 3 or len(skill_matches) < 2:
        return render_template(
            "error.html",
            title="Invalid Document",
            message="The uploaded document does not appear to be a resume. Please upload a valid resume only. Certificates and other documents are not supported."
        )

    try:
        jobs = pd.read_csv(DATA_FILE)

    except Exception:
        return render_template(
            "error.html",
            title="Job Data Error",
            message="The job dataset could not be loaded. Please check data/jobs.csv."
        )

    jobs = jobs.fillna("")

    if len(jobs) == 0:
        return render_template(
            "error.html",
            title="No Jobs Available",
            message="There are currently no jobs available for matching."
        )

    text_columns = jobs.select_dtypes(
        include=["object"]
    ).columns.tolist()

    if len(text_columns) == 0:
        return render_template(
            "error.html",
            title="Invalid Job Dataset",
            message="The job dataset does not contain usable text information."
        )

    documents = []

    for _, row in jobs.iterrows():

        job_text = " ".join(
            str(row[column])
            for column in text_columns
        )

        documents.append(job_text)

    documents.append(resume_text)

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    vectors = vectorizer.fit_transform(documents)

    resume_vector = vectors[-1]

    job_vectors = vectors[:-1]

    similarity_scores = cosine_similarity(
        resume_vector,
        job_vectors
    )[0]

    jobs["match_score"] = similarity_scores * 100

    jobs = jobs.sort_values(
        by="match_score",
        ascending=False
    )

    top_jobs = jobs.head(5)

    results = []

    for _, job in top_jobs.iterrows():

        job_data = {}

        for column in jobs.columns:

            if column != "match_score":
                job_data[column] = job[column]

        job_data["match_score"] = round(
            float(job["match_score"]),
            1
        )

        results.append(job_data)

    matched_skills = skill_matches

    missing_skills = [
        skill for skill in SKILLS
        if skill not in matched_skills
    ]

    return render_template(
        "results.html",
        filename=file.filename,
        match_score=round(
            float(top_jobs.iloc[0]["match_score"]),
            1
        ),
        matched_skills=matched_skills,
        missing_skills=missing_skills[:8],
        jobs=results
    )
 
if __name__ == "__main__":
    app.run(debug=True)