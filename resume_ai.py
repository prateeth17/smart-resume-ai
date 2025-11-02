"""
Resume Analysis and Job Matching Module
"""
import os
import json
import re

# Import dependencies with error handling
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

try:
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

# Default job data (fallback if JSON file not found)
DEFAULT_JOB_DATA = {
    "Software Engineer": ["Python", "Java", "JavaScript", "SQL", "Git", "Docker", "AWS"],
    "Data Scientist": ["Python", "Machine Learning", "Statistics", "SQL", "Pandas", "NumPy"],
    "Frontend Developer": ["HTML", "CSS", "JavaScript", "React", "Angular", "Vue"],
    "Backend Developer": ["Python", "Java", "Node.js", "SQL", "MongoDB", "REST API"],
    "Full Stack Developer": ["JavaScript", "Python", "React", "Node.js", "SQL", "Docker"]
}

def load_job_data():
    """Load job roles from JSON file or use default data"""
    try:
        # Try to load from data/job_roles.json
        if os.path.exists("data/job_roles.json"):
            with open("data/job_roles.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                print(f"✅ Loaded {len(data)} job roles from JSON")
                return data
        
        # Fallback to default
        print("⚠️ Using default job data")
        return DEFAULT_JOB_DATA
        
    except Exception as e:
        print(f"⚠️ Error loading job data: {e}")
        return DEFAULT_JOB_DATA

# Load job data on module import
JOB_DATA = load_job_data()

def extract_text_from_pdf(uploaded_file):
    """Extract text from uploaded PDF file using PyMuPDF"""
    if not HAS_PYMUPDF:
        return "ERROR: PyMuPDF not installed. Install with: pip install PyMuPDF"
    
    try:
        # Reset file pointer to beginning
        uploaded_file.seek(0)
        
        # Read PDF bytes
        pdf_bytes = uploaded_file.read()
        
        # Open PDF from bytes
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        # Extract text from all pages
        text = ""
        for page_num, page in enumerate(doc):
            page_text = page.get_text("text")
            text += page_text
            print(f"Page {page_num + 1}: Extracted {len(page_text)} characters")
        
        doc.close()
        
        # Clean and return text
        text = text.strip()
        print(f"✅ Total extracted: {len(text)} characters")
        
        return text if text else "ERROR: No text found in PDF"
        
    except Exception as e:
        error_msg = f"ERROR extracting PDF: {str(e)}"
        print(error_msg)
        return error_msg

def analyze_resume(uploaded_file):
    """Analyze resume and find matching job roles"""
    
    # Extract text from PDF
    resume_text = extract_text_from_pdf(uploaded_file)
    
    # Check for errors
    if not resume_text or resume_text.startswith("ERROR"):
        return resume_text, []
    
    # Check if sklearn is available for similarity analysis
    if not HAS_SKLEARN:
        print("⚠️ scikit-learn not available, using simple keyword matching")
        return resume_text, simple_job_matching(resume_text)
    
    # Perform cosine similarity analysis
    resume_lower = resume_text.lower()
    job_matches = []
    
    for job_title, skills in JOB_DATA.items():
        try:
            # Create job description from skills
            job_description = " ".join(skills).lower()
            
            # Calculate cosine similarity
            vectorizer = CountVectorizer()
            vectors = vectorizer.fit_transform([resume_lower, job_description])
            similarity = cosine_similarity(vectors)[0][1]
            
            # Convert to percentage
            similarity_percentage = round(similarity * 100, 2)
            
            job_matches.append({
                "job": job_title,
                "similarity": similarity_percentage
            })
            
        except Exception as e:
            print(f"Error processing {job_title}: {e}")
            continue
    
    # Sort by similarity (highest first)
    job_matches.sort(key=lambda x: x["similarity"], reverse=True)
    
    print(f"✅ Found {len(job_matches)} job matches")
    return resume_text, job_matches

def simple_job_matching(resume_text):
    """Simple keyword-based matching (fallback when sklearn not available)"""
    resume_lower = resume_text.lower()
    resume_words = set(re.findall(r'\b\w+\b', resume_lower))
    
    job_matches = []
    
    for job_title, skills in JOB_DATA.items():
        # Count matching skills
        matching_skills = sum(1 for skill in skills if skill.lower() in resume_words)
        total_skills = len(skills)
        
        # Calculate percentage
        match_percentage = round((matching_skills / total_skills) * 100, 2) if total_skills > 0 else 0
        
        job_matches.append({
            "job": job_title,
            "similarity": match_percentage
        })
    
    # Sort by similarity
    job_matches.sort(key=lambda x: x["similarity"], reverse=True)
    return job_matches

def suggest_improvements(resume_text, target_role):
    """Analyze skill gaps for a target role"""
    
    if not target_role:
        return {
            "status": "error",
            "message": "Please select or enter a job role",
            "present_skills": [],
            "missing_skills": []
        }
    
    # Get required skills for the role
    required_skills = JOB_DATA.get(target_role, [])
    
    if not required_skills:
        return {
            "status": "error",
            "message": f"No skill data available for role: {target_role}",
            "present_skills": [],
            "missing_skills": []
        }
    
    # Extract words from resume
    resume_words = set(re.findall(r'\b\w+\b', resume_text.lower()))
    
    # Find present and missing skills
    present_skills = [skill for skill in required_skills if skill.lower() in resume_words]
    missing_skills = [skill for skill in required_skills if skill.lower() not in resume_words]
    
    # Determine status
    if len(present_skills) > len(missing_skills):
        status = "success"
        message = f"✅ Good match! You have {len(present_skills)}/{len(required_skills)} skills for {target_role}"
    elif present_skills:
        status = "needs_improvement"
        message = f"⚠️ Partial match. You have {len(present_skills)}/{len(required_skills)} skills for {target_role}"
    else:
        status = "needs_improvement"
        message = f"⚠️ Low match. Consider adding skills for {target_role}"
    
    return {
        "status": status,
        "message": message,
        "present_skills": present_skills,
        "missing_skills": missing_skills,
        "total_required": len(required_skills),
        "match_percentage": round((len(present_skills) / len(required_skills)) * 100, 2) if required_skills else 0
    }

def get_all_job_roles():
    """Return sorted list of all available job roles"""
    return sorted(list(JOB_DATA.keys()))

def get_module_info():
    """Return information about loaded modules and data"""
    return {
        "pymupdf_available": HAS_PYMUPDF,
        "sklearn_available": HAS_SKLEARN,
        "total_job_roles": len(JOB_DATA),
        "job_roles": list(JOB_DATA.keys())
    }
