import os
import json
import re

try:
    import fitz
    HAS_PYMUPDF = True
except:
    HAS_PYMUPDF = False

try:
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except:
    HAS_SKLEARN = False

DEFAULT_JOB_DATA = {
    "Software Engineer": ["Python", "Java", "JavaScript", "SQL", "Git"],
    "Data Scientist": ["Python", "Machine Learning", "Statistics", "SQL"]
}

def load_job_data():
    try:
        if os.path.exists("data/job_roles.json"):
            with open("data/job_roles.json", "r") as f:
                return json.load(f)
        return DEFAULT_JOB_DATA
    except:
        return DEFAULT_JOB_DATA

JOB_DATA = load_job_data()

def extract_text_from_pdf(uploaded_file):
    if not HAS_PYMUPDF:
        return "ERROR: PyMuPDF not installed"
    try:
        uploaded_file.seek(0)
        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text("text")
        doc.close()
        return text.strip() if text else "ERROR: No text found"
    except Exception as e:
        return f"ERROR: {str(e)}"

def analyze_resume(uploaded_file):
    resume_text = extract_text_from_pdf(uploaded_file)
    if resume_text.startswith("ERROR"):
        return resume_text, []
    if not HAS_SKLEARN:
        return resume_text, simple_job_matching(resume_text)
    resume_lower = resume_text.lower()
    job_matches = []
    for job_title, skills in JOB_DATA.items():
        try:
            job_description = " ".join(skills).lower()
            vectorizer = CountVectorizer()
            vectors = vectorizer.fit_transform([resume_lower, job_description])
            similarity = cosine_similarity(vectors)[0][1]
            job_matches.append({"job": job_title, "similarity": round(similarity * 100, 2)})
        except:
            continue
    job_matches.sort(key=lambda x: x["similarity"], reverse=True)
    return resume_text, job_matches

def simple_job_matching(resume_text):
    resume_words = set(re.findall(r'\b\w+\b', resume_text.lower()))
    job_matches = []
    for job_title, skills in JOB_DATA.items():
        matching = sum(1 for s in skills if s.lower() in resume_words)
        match_pct = round((matching / len(skills)) * 100, 2)
        job_matches.append({"job": job_title, "similarity": match_pct})
    job_matches.sort(key=lambda x: x["similarity"], reverse=True)
    return job_matches

def suggest_improvements(resume_text, target_role):
    if not target_role:
        return {"status": "error", "message": "Select a role", "present_skills": [], "missing_skills": []}
    required_skills = JOB_DATA.get(target_role, [])
    if not required_skills:
        return {"status": "error", "message": f"No data for {target_role}", "present_skills": [], "missing_skills": []}
    resume_words = set(re.findall(r'\b\w+\b', resume_text.lower()))
    present = [s for s in required_skills if s.lower() in resume_words]
    missing = [s for s in required_skills if s.lower() not in resume_words]
    status = "success" if len(present) > len(missing) else "needs_improvement"
    message = f"You have {len(present)}/{len(required_skills)} skills"
    return {"status": status, "message": message, "present_skills": present, "missing_skills": missing}

def get_all_job_roles():
    return sorted(list(JOB_DATA.keys()))

def get_module_info():
    return {"pymupdf_available": HAS_PYMUPDF, "sklearn_available": HAS_SKLEARN, "total_job_roles": len(JOB_DATA)}
