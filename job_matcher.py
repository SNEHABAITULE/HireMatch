from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

resume = """ Python SQL Pandas Flask Machine Learning
Data Analysis Scikit-learn """

job_description = """ Looking for a Python Developer with Python, SQL, Pandas,
Flask and Machine Learning skills. """

vectorizer = TfidfVectorizer()

vectors = vectorizer.fit_transform([resume, job_description])

similarity = cosine_similarity(vectors[0], vectors[1])

match_score = similarity[0][0] * 100

print(f"Job Match Score: {match_score:.2f}%")