from flask import Flask, render_template, request
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from werkzeug.utils import secure_filename
import uuid
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
    "data science",
    "node.js",
    "react",
    "angular",
    "mongodb",
    "rest api",
    "data structures",
    "figma",
    "canva",
    "communication",
    "leadership",
    "problem solving"
]

RESUME_KEYWORDS = [
    "education",
    "experience",
    "skills",
    "projects",
    "certifications",
    "objective",
    "summary",
    "internship",
    "qualification",
    "technical skills",
    "work experience",
    "contact",
    "email",
    "phone",
    "linkedin",
    "github"
]

REJECTION_KEYWORDS = [
    "summer internship report",
    "internship report",
    "report on summer internship",
    "table of content",
    "table of contents",
    "certificate from industry",
    "acknowledgement",
    "chapter 1",
    "chapter 2",
    "chapter 3",
    "chapter 4",
    "partial fulfillment for the award",
    "submitted in partial fulfillment",
    "experiment",
    "bibliography",
    "declaration",
    "project report",
    "training report",
    "research paper",
    "mark sheet",
    "marksheet",
    "bonafide certificate",
    "completion certificate",
    "experience letter",
    "offer letter"
]


def extract_pdf_text(file_path):
    try:
        reader = PdfReader(file_path)
        text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + " "

        return text.strip()

    except Exception:
        return ""


def detect_skills(text):
    text_lower = text.lower()
    found_skills = []

    for skill in SKILLS:
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(skill.lower()) + r"(?![a-zA-Z0-9])"

        if re.search(pattern, text_lower):
            found_skills.append(skill)

    return found_skills


def is_valid_resume(text):
    text_lower = text.lower()

    rejection_matches = []

    for keyword in REJECTION_KEYWORDS:
        if keyword in text_lower:
            rejection_matches.append(keyword)

    if len(rejection_matches) >= 2:
        return False

    resume_matches = 0

    for keyword in RESUME_KEYWORDS:
        if keyword in text_lower:
            resume_matches += 1

    skills = detect_skills(text)

    if len(text) < 200:
        return False

    if resume_matches < 3:
        return False

    if len(skills) < 2:
        return False

    return True


def calculate_job_matches(resume_text):
    jobs = pd.read_csv(DATA_FILE)

    jobs = jobs.fillna("")

    if len(jobs) == 0:
        return []

    text_columns = jobs.select_dtypes(
        include=["object"]
    ).columns.tolist()

    if not text_columns:
        return []

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

    return results


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

    original_filename = file.filename

    if not original_filename.lower().endswith(".pdf"):
        return render_template(
            "error.html",
            title="Invalid File",
            message="Please upload a PDF resume only."
        )

    safe_filename = secure_filename(original_filename)

    if not safe_filename.lower().endswith(".pdf"):
        return render_template(
            "error.html",
            title="Invalid File",
            message="Please upload a valid PDF resume."
        )

    os.makedirs(
        app.config["UPLOAD_FOLDER"],
        exist_ok=True
    )

    unique_filename = f"{uuid.uuid4().hex}.pdf"

    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        unique_filename
    )

    try:
        file.save(file_path)

        resume_text = extract_pdf_text(file_path)

    except Exception:
        return render_template(
            "error.html",
            title="Unable to Read Document",
            message="We could not read this PDF. Please upload a valid text-based resume."
        )

    if not resume_text:
        return render_template(
            "error.html",
            title="Unable to Read Resume",
            message="This PDF contains an image or scanned document that cannot currently be read. Please upload a text-based PDF resume."
        )

    if not is_valid_resume(resume_text):

        return render_template(
            "error.html",
            title="Invalid Document",
            message="The uploaded document does not appear to be a resume. Please upload a valid resume only. Internship reports, certificates and other documents are not supported."
        )

    matched_skills = detect_skills(resume_text)

    missing_skills = [
        skill
        for skill in SKILLS
        if skill not in matched_skills
    ]

    try:
        jobs = calculate_job_matches(resume_text)

    except Exception:
        return render_template(
            "error.html",
            title="Matching Error",
            message="We could not analyze the resume against the job dataset. Please try again."
        )

    if not jobs:
        return render_template(
            "error.html",
            title="No Jobs Available",
            message="There are currently no jobs available for matching."
        )

    return render_template(
        "results.html",
        filename=original_filename,
        match_score=jobs[0]["match_score"],
        matched_skills=matched_skills,
        missing_skills=missing_skills[:8],
        jobs=jobs
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )