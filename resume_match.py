from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# -----------------------------
# 1. Sample Resume & JD
# -----------------------------
resume_text = """
I am a Computer Science student skilled in Python,
Machine Learning, Data Analysis, Pandas and NumPy.
I have built ML projects including a resume analyzer.
"""

jd_text = """
We are hiring a Python Developer with experience in
Machine Learning, Data Analysis, Pandas, NumPy and
Scikit-learn. Flask knowledge is a plus.
"""


# -----------------------------
# 2. TF-IDF + Cosine Similarity
# -----------------------------
def semantic_similarity(resume, jd):
    documents = [resume, jd]

    vectorizer = TfidfVectorizer(
        stop_words='english',
        lowercase=True
    )

    tfidf_matrix = vectorizer.fit_transform(documents)

    similarity = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:2]
    )[0][0]

    return similarity * 100

    
def normalize_text(text):
    replacements = {
        "ml": "machine learning",
        "ai": "artificial intelligence",
        "dev": "developer"
    }

    text = text.lower()
    for key, value in replacements.items():
        text = text.replace(key, value)

    return text


# -----------------------------
# 3. Skill List
# -----------------------------
SKILLS = [
    "python", "java", "machine learning", "deep learning",
    "data analysis", "pandas", "numpy", "scikit-learn",
    "tensorflow", "pytorch", "sql", "flask",
    "docker", "rest api", "backend", "frontend",
    "react", "node", "mongodb"
]


# -----------------------------
# 4. Skill Extraction
# -----------------------------
def extract_skills(text, skills):
    text = text.lower()
    found = set()

    for skill in skills:
        if skill in text:
            found.add(skill)

    return found


# -----------------------------
# 5. Skill Matching Logic
# -----------------------------
def skill_matching(resume, jd, skills):
    resume_skills = extract_skills(resume, skills)
    jd_skills = extract_skills(jd, skills)

    matched = resume_skills.intersection(jd_skills)
    missing = jd_skills - resume_skills

    skill_score = (
        len(matched) / len(jd_skills) * 100
        if len(jd_skills) > 0 else 0
    )

    return skill_score, matched, missing


# -----------------------------
# 6. Final Scoring
# -----------------------------
semantic_score = semantic_similarity(resume_text, jd_text)
skill_score, matched_skills, missing_skills = skill_matching(
    resume_text, jd_text, SKILLS
)

final_score = (semantic_score * 0.3) + (skill_score * 0.7)

semantic_score = semantic_similarity(
    normalize_text(resume_text),
    normalize_text(jd_text)
)


# -----------------------------
# 7. Output
# -----------------------------
print("🔹 Semantic Match Score:", f"{semantic_score:.2f}%")
print("🔹 Skill Match Score:", f"{skill_score:.2f}%")
print("\n✅ Matched Skills:", matched_skills)
print("❌ Missing Skills:", missing_skills)

print("\n⭐ Final Resume Score:", f"{final_score:.2f}%")
print("\n📌 Explanation:")
print(f"- Resume matches {len(matched_skills)} out of {len(matched_skills) + len(missing_skills)} required skills.")
print(f"- Improve score by adding: {', '.join(missing_skills)}")

if final_score >= 80:
    print("Result: Strong Match ✅")
elif final_score >= 50:
    print("Result: Moderate Match ⚠️")
else:
    print("Result: Low Match ❌")
