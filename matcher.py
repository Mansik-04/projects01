import pandas as pd
from utils import clean_text, extract_skills
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load data
resumes_df = pd.read_csv("data/Resume.csv")
jobs_df = pd.read_csv("data/training_data.csv")

# Clean data
resumes_df["cleaned_text"] = resumes_df["Resume_str"].apply(clean_text)
jobs_df["cleaned_text"] = jobs_df["job_description"].apply(clean_text)

vectorizer = TfidfVectorizer(ngram_range=(1, 2))
job_vectors = vectorizer.fit_transform(jobs_df["cleaned_text"])

resume_text = resumes_df.iloc[0]["cleaned_text"]
resume_vector = vectorizer.transform([resume_text])

# Text similarity
similarity = cosine_similarity(resume_vector, job_vectors)[0] * 100
jobs_df["Text_Score"] = similarity

# Skills
resume_skills = extract_skills(resumes_df.iloc[0]["Resume_str"])
jobs_df["Skill_Score"] = jobs_df["job_description"].apply(
    lambda x: len(set(extract_skills(x)) & set(resume_skills)) * 10
)

# Title weight
def title_boost(title):
    title = title.lower()
    if "data analyst" in title: return 20
    if "analyst" in title: return 15
    if "scientist" in title: return 10
    return 5

jobs_df["Title_Score"] = jobs_df["position_title"].apply(title_boost)

# Final score
jobs_df["Final_Score"] = (
    jobs_df["Text_Score"] * 0.55 +
    jobs_df["Skill_Score"] * 0.30 +
    jobs_df["Title_Score"] * 0.15
)

# Print
print(
    jobs_df[["position_title", "company_name", "Final_Score"]]
    .sort_values(by="Final_Score", ascending=False)
    .head(10)
)
