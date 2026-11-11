import pandas as pd
import sqlite3

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Load job data from SQLite database
conn = sqlite3.connect("joblens.db")

jobs = pd.read_sql_query(
    """
    SELECT jobid, jobtitle, company,
           joblocation_address, jobdescription
    FROM naukri_jobs
    """,
    conn
)

conn.close()


# Clean job descriptions
jobs = jobs.dropna(subset=["jobdescription"])

jobs["jobdescription"] = (
    jobs["jobdescription"]
    .astype(str)
    .str.strip()
)

jobs = jobs[
    jobs["jobdescription"].str.len() > 0
].reset_index(drop=True)


# Build the TF-IDF model
vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=5000,
    ngram_range=(1, 2)
)

job_vectors = vectorizer.fit_transform(
    jobs["jobdescription"]
)


# Recommend jobs based on candidate profile
def recommend_jobs(candidate_profile, top_n=10):

    candidate_vector = vectorizer.transform(
        [candidate_profile]
    )

    similarity_scores = cosine_similarity(
        candidate_vector,
        job_vectors
    ).flatten()

    results = jobs.copy()

    results["similarity_score"] = similarity_scores

    recommendations = results.sort_values(
        by="similarity_score",
        ascending=False
    ).head(top_n)

    return recommendations[
        [
            "jobtitle",
            "company",
            "joblocation_address",
            "similarity_score"
        ]
    ]