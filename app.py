import os
import pdfplumber
import requests
from dotenv import load_dotenv

from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    login_required,
    current_user,
    login_user,
    logout_user
)
from werkzeug.security import generate_password_hash, check_password_hash

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from models import db, User, ResumeReport

# -----------------------------
# App Setup
# -----------------------------
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = "uploads"

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)

with app.app_context():
    db.create_all()

# -----------------------------
# Login Manager
# -----------------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# -----------------------------
# HuggingFace Config
# -----------------------------
HF_TOKEN = os.getenv("HF_TOKEN")
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}


# -----------------------------
# Skill List
# -----------------------------
SKILLS = [
    "python", "java", "machine learning", "deep learning",
    "data analysis", "pandas", "numpy", "scikit-learn",
    "tensorflow", "pytorch", "sql", "flask"
]


# -----------------------------
# Helper Functions
# -----------------------------
def normalize_text(text):
    replacements = {
        "ml": "machine learning",
        "ai": "artificial intelligence"
    }
    text = text.lower()
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text


def semantic_similarity(resume, jd):
    documents = [resume, jd]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf = vectorizer.fit_transform(documents)
    score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    return score * 100


def extract_skills(text):
    text = text.lower()
    return {skill for skill in SKILLS if skill in text}


def skill_match(resume, jd):
    resume_skills = extract_skills(resume)
    jd_skills = extract_skills(jd)

    matched = resume_skills & jd_skills
    missing = jd_skills - resume_skills

    score = (len(matched) / len(jd_skills) * 100) if jd_skills else 0
    return score, matched, missing


def interpret_score(score):
    if score >= 80:
        return "Strong", "green"
    elif score >= 60:
        return "Moderate", "orange"
    else:
        return "Weak", "red"


def generate_ai_suggestions(missing_skills):
    if not missing_skills:
        return "No missing skills detected."

    prompt = f"""
You are a career mentor.

The candidate is missing these skills:
{', '.join(missing_skills)}

Give short and practical resume improvement suggestions.
Use bullet points.
"""

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 250,
            "temperature": 0.7
        }
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)

        if response.status_code != 200:
            return "AI service temporarily unavailable."

        result = response.json()

        if isinstance(result, list) and len(result) > 0:
            return result[0].get("generated_text", "No suggestions generated.")
        else:
            return "Could not generate suggestions."

    except Exception:
        return "Error generating AI suggestions."


# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
@login_required
def analyze():
    try:
        jd_text = normalize_text(request.form.get("jd", ""))

        file = request.files.get("resume_pdf")

        if not file or not file.filename.endswith(".pdf"):
            flash("Please upload a valid PDF file.", "danger")
            return redirect("/")

        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)

        resume_text = extract_text_from_pdf(file_path)
        resume_text = normalize_text(resume_text)

        # Scoring
        semantic_score = semantic_similarity(resume_text, jd_text)
        skill_score, matched, missing = skill_match(resume_text, jd_text)

        final_score = (semantic_score * 0.3) + (skill_score * 0.7)
        label, color = interpret_score(final_score)

        ai_suggestions = generate_ai_suggestions(missing)

        # Save to DB
        report = ResumeReport(
            score=int(final_score),
            feedback=ai_suggestions,
            user_id=current_user.id
        )

        db.session.add(report)
        db.session.commit()

        return render_template(
            "result.html",
            semantic=round(semantic_score, 2),
            skill=round(skill_score, 2),
            final=round(final_score, 2),
            matched=matched,
            missing=missing,
            label=label,
            color=color,
            suggestions=ai_suggestions
        )

    except Exception as e:
        print("Analyze Error:", e)
        return "Something went wrong."


@app.route("/dashboard")
@login_required
def dashboard():
    reports = ResumeReport.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", reports=reports)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered!", "danger")
            return redirect("/register")

        hashed_password = generate_password_hash(password)

        new_user = User(
            username=username,
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please login.", "success")
        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect("/dashboard")
        else:
            flash("Invalid email or password!", "danger")
            return redirect("/login")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")


# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)