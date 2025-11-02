import streamlit as st
import re
import io
from datetime import datetime

try:
    import fitz
    HAS_PDF = True
except:
    HAS_PDF = False

try:
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except:
    HAS_SKLEARN = False

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    HAS_REPORTLAB = True
except:
    HAS_REPORTLAB = False

JOB_DATA = {
    "Software Engineer": ["python", "java", "javascript", "react", "node.js", "docker", "kubernetes", "git", "sql", "mongodb", "aws"],
    "Data Scientist": ["python", "machine learning", "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn", "sql", "tableau"],
    "Frontend Developer": ["html", "css", "javascript", "react", "vue", "angular", "typescript", "webpack", "git"],
    "Backend Developer": ["python", "java", "node.js", "express", "django", "flask", "rest api", "sql", "mongodb"],
    "Full Stack Developer": ["javascript", "react", "node.js", "express", "mongodb", "sql", "html", "css", "docker"],
    "DevOps Engineer": ["docker", "kubernetes", "jenkins", "terraform", "aws", "azure", "linux", "bash", "ci/cd"],
    "Mobile Developer": ["react native", "flutter", "swift", "kotlin", "android", "ios", "firebase", "git"],
    "Cloud Architect": ["aws", "azure", "gcp", "terraform", "docker", "kubernetes", "serverless", "networking"],
    "ML Engineer": ["python", "tensorflow", "pytorch", "scikit-learn", "deep learning", "mlops", "docker"],
    "Product Manager": ["product strategy", "roadmap", "agile", "jira", "analytics", "sql", "communication"]
}

def extract_pdf(file):
    if not HAS_PDF:
        return "ERROR: PDF reader missing"
    try:
        file.seek(0)
        doc = fitz.open(stream=file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip() if text else "ERROR: No text"
    except Exception as e:
        return f"ERROR: {e}"

def analyze(text):
    if not HAS_SKLEARN:
        return simple_match(text)
    matches = []
    for job, skills in JOB_DATA.items():
        try:
            vec = CountVectorizer()
            v = vec.fit_transform([text.lower(), " ".join(skills)])
            sim = cosine_similarity(v)[0][1]
            matches.append({"job": job, "score": round(sim * 100, 2)})
        except:
            pass
    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches

def simple_match(text):
    words = set(re.findall(r'\b\w+\b', text.lower()))
    matches = []
    for job, skills in JOB_DATA.items():
        count = sum(1 for s in skills if s in words)
        score = round((count / len(skills)) * 100, 2)
        matches.append({"job": job, "score": score})
    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches

def check_skills(text, role):
    skills = JOB_DATA.get(role, [])
    words = set(re.findall(r'\b\w+\b', text.lower()))
    present = [s for s in skills if s in words]
    missing = [s for s in skills if s not in words]
    return present, missing

def make_pdf(text, present, missing, role, user):
    if not HAS_REPORTLAB:
        return None
    try:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=letter, rightMargin=0.75*inch, leftMargin=0.75*inch, topMargin=0.75*inch, bottomMargin=0.75*inch)
        els = []
        styles = getSampleStyleSheet()
        
        els.append(Paragraph("<b>RESUME REPORT</b>", styles['Title']))
        els.append(Spacer(1, 0.2*inch))
        els.append(Paragraph(f"<b>Role:</b> {role}<br/><b>User:</b> {user}<br/><b>Date:</b> {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        els.append(Spacer(1, 0.3*inch))
        
        if present:
            els.append(Paragraph("<b>Current Skills:</b>", styles['Heading2']))
            els.append(Paragraph(", ".join(present[:20]), styles['Normal']))
            els.append(Spacer(1, 0.2*inch))
        
        if missing:
            els.append(Paragraph("<b>Add These Skills:</b>", styles['Heading2']))
            els.append(Paragraph(", ".join(missing[:20]), styles['Normal']))
            els.append(Spacer(1, 0.2*inch))
        
        els.append(Paragraph("<b>Summary:</b>", styles['Heading2']))
        els.append(Paragraph(" ".join(text.split()[:150]) + "...", styles['Normal']))
        
        doc.build(els)
        return buf.getvalue()
    except:
        return None

st.set_page_config(page_title="Resume System", page_icon="📄", layout="wide")

st.markdown("""
<div style='text-align:center;background:linear-gradient(135deg,#667eea,#764ba2);padding:1.5rem;border-radius:10px;color:white;margin-bottom:2rem;'>
<h1>🧠 Smart Resume Enhancement System</h1>
<p>AI-Powered Job Matching & Skill Analysis</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("🔐 Login")
    if "logged" not in st.session_state:
        st.session_state.logged = False
    
    if not st.session_state.logged:
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Login", use_container_width=True):
                if user and pwd:
                    st.session_state.logged = True
                    st.session_state.user = user
                    st.rerun()
        with c2:
            if st.button("Demo", use_container_width=True):
                st.session_state.logged = True
                st.session_state.user = "Demo"
                st.rerun()
    else:
        st.success(f"👤 {st.session_state.user}")
        st.metric("Roles", len(JOB_DATA))
        if st.button("Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

if st.session_state.get("logged"):
    st.markdown("### 📂 Upload Resume PDF")
    up = st.file_uploader("Choose PDF", type=["pdf"])
    
    if up:
        with st.spinner("Analyzing..."):
            text = extract_pdf(up)
        
        if not text.startswith("ERROR"):
            st.success("✅ Resume processed!")
            
            t1, t2, t3, t4 = st.tabs(["🎯 Jobs", "🔧 Skills", "📄 Text", "📥 PDF"])
            
            with t1:
                st.subheader("Top Job Matches")
                jobs = analyze(text)
                for i, j in enumerate(jobs[:6], 1):
                    s = j["score"]
                    e = "🟢" if s >= 70 else "🟡" if s >= 50 else "🔴"
                    with st.expander(f"{e} {i}. {j['job']} - {s}%"):
                        st.progress(s/100)
                        for b, u in {"LinkedIn": f"https://linkedin.com/jobs/search?keywords={j['job']}", "Indeed": f"https://indeed.com/jobs?q={j['job']}"}.items():
                            st.markdown(f"[{b}]({u})")
            
            with t2:
                st.subheader("Skill Analysis")
                role = st.selectbox("Role:", list(JOB_DATA.keys()))
                if st.button("Analyze", type="primary"):
                    p, m = check_skills(text, role)
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("**✅ Have:**")
                        for x in p: st.write(f"• {x}")
                    with c2:
                        st.markdown("**⚠️ Need:**")
                        for x in m: st.write(f"• {x}")
                    st.session_state.analysis = {"role": role, "p": p, "m": m, "t": text}
            
            with t3:
                st.subheader("Resume Text")
                st.text_area("Content", text, height=300)
                st.download_button("Download", text, "resume.txt")
            
            with t4:
                st.subheader("Generate PDF Report")
                if "analysis" in st.session_state:
                    a = st.session_state.analysis
                    if st.button("Generate PDF", type="primary"):
                        pdf = make_pdf(a["t"], a["p"], a["m"], a["role"], st.session_state.user)
                        if pdf:
                            st.download_button("Download PDF", pdf, f"report_{a['role']}.pdf", "application/pdf")
                else:
                    st.info("Analyze skills first")
        else:
            st.error(text)
else:
    st.info("👈 Login to start")

st.markdown("---")
st.markdown("<p style='text-align:center;'>© 2025 Resume System</p>", unsafe_allow_html=True)
