# 🚀 HireMatch

# 🤖 AI-Powered Resume & Job Matching System

HireMatch is a Python-based web application that analyzes a user's resume and recommends suitable job opportunities based on their skills and job descriptions.

## ✨ Features

- 📄 Upload resume in PDF format
- 🔍 Extract text from resume
- 🧠 Detect skills from resume
- 🎯 Calculate resume-job similarity
- 💼 Recommend suitable jobs
- 📊 Display job match scores
- 📚 Identify missing skills
- ⚠️ Reject invalid documents such as certificates
- 🎨 Clean and responsive web interface

## 🛠️ Technologies Used

- 🐍 Python
- 🌐 Flask
- 📊 Pandas
- 🧠 Scikit-learn
- 📄 pypdf
- 🎨 HTML
- 🎨 CSS
- 🗃️ CSV Dataset

## 🧠 How It Works

1. 👤 User uploads a resume.
2. 📄 HireMatch extracts text from the PDF.
3. 🔎 Resume content and skills are analyzed.
4. 🗃️ Job information is loaded from the dataset.
5. 🧠 TF-IDF converts text into numerical vectors.
6. 📐 Cosine similarity compares the resume with job descriptions.
7. 🎯 Jobs are ranked according to their match score.
8. 📊 Results are displayed on the website.
9. 📚 Missing skills are shown to help the user improve.

## 📁 Project Structure

```text
HireMatch/
│
├── app.py
├── job_matcher.py
├── job_recom.py
├── skill_gap.py
├── resume_parser.py
├── skill_extractor.py
├── test_jobs.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── data/
│   └── jobs.csv
│
├── templates/
│   ├── index.html
│   ├── results.html
│   └── error.html
│
└── static/
    └── style.css