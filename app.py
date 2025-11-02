"""
Smart Resume Enhancement System - Complete Version
"""
import streamlit as st
import os
import json
import re
from datetime import datetime
import io

# Import dependencies
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

# ===================== JOB DATA =====================
JOB_DATA = {
    "Software Engineer": [
        "python", "java", "javascript", "react", "node.js", "docker", 
        "kubernetes", "git", "agile", "sql", "mongodb", "aws", "rest api",
        "microservices", "spring boot", "django", "flask"
    ],
    "Data Scientist": [
        "python", "machine learning", "deep learning", "tensorflow",
        "pytorch", "pandas", "numpy", "scikit-learn", "sql", "tableau",
        "statistics", "data visualization", "jupyter", "spark"
    ],
    "Frontend Developer": [
        "html", "css", "javascript", "react", "vue", "angular",
        "typescript", "webpack", "responsive design", "ui/ux", "git",
        "sass", "tailwind", "bootstrap"
    ],
    "Backend Developer": [
        "python", "java", "node.js", "express", "django", "flask",
        "spring boot", "rest api", "graphql", "sql", "mongodb", "redis",
        "postgresql", "mysql"
    ],
    "Full Stack Developer": [
        "javascript", "react", "node.js", "express", "mongodb",
        "sql", "html", "css", "git", "docker", "aws", "rest api",
        "python", "typescript"
    ],
    "DevOps Engineer": [
        "docker", "kubernetes", "jenkins", "ansible", "terraform",
        "aws", "azure", "gcp", "linux", "bash", "python", "ci/cd",
        "git", "monitoring"
    ],
    "Mobile Developer": [
        "react native", "flutter", "swift", "kotlin", "java",
        "android", "ios", "firebase", "rest api", "git"
    ],
    "Cloud Architect": [
        "aws", "azure", "gcp", "terraform", "docker", "kubernetes",
        "microservices", "serverless", "ci/cd", "networking", "security"
    ],
    "Machine Learning Engineer": [
        "python", "tensorflow", "pytorch", "scikit-learn", "keras",
        "deep learning", "nlp", "computer vision", "mlops", "docker"
    ],
    "Product Manager": [
        "product strategy", "roadmap", "agile", "scrum", "jira",
        "user research", "analytics", "sql", "communication", "leadership"
    ]
}

# ===================== FUNCTIONS =====================

def extract_text_from_pdf(file):
    """Extract text from PDF"""
    if not HAS_PDF:
        return "ERROR: PDF reader not available"
    try:
        file.seek(0)
        doc = fitz.open(stream=file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text("text")
        doc.close()
        return text.strip() if text else "ERROR: No text found"
    except Exception as e:
        return f"ERROR: {e}"

def analyze_resume(text):
    """Analyze resume and match jobs"""
    if not HAS_SKLEARN:
        return simple_job_match(text)
    
    matches = []
    text_lower = text.lower()
    
    for job, skills in JOB_DATA.items():
        try:
            job_text = " ".join(skills)
            vectorizer = CountVectorizer()
            vectors = vectorizer.fit_transform([text_lower, job_text.lower()])
            similarity = cosine_similarity(vectors)[0][1]
            matches.append({"job": job, "score": round(similarity * 100, 2)})
        except:
            continue
    
    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches

def simple_job_match(text):
    """Simple keyword matching"""
    words = set(re.findall(r'\b\w+\b', text.lower()))
    matches = []
    
    for job, skills in JOB_DATA.items():
        count = sum(1 for s in skills if s.lower() in words)
        score = round((count / len(skills)) * 100, 2)
        matches.append({"job": job, "score": score})
    
    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches

def check_skill_gap(text, role):
    """Check skills for a role"""
    skills = JOB_DATA.get(role, [])
    if not skills:
        return [], [], "No data for this role"
    
    words = set(re.findall(r'\b\w+\b', text.lower()))
    present = [s for s in skills if s.lower() in words]
    missing = [s for s in skills if s.lower() not in words]
    
    total = len(skills)
    match_pct = round((len(present) / total) * 100, 2) if total > 0 else 0
    
    if match_pct >= 60:
        status = "success"
        message = f"✅ Good match! {len(present)}/{total} skills ({match_pct}%)"
    else:
        status = "warning"
        message = f"⚠️ Needs improvement. {len(present)}/{total} skills ({match_pct}%)"
    
    return present, missing, message, status

def generate_pdf_report(text, present, missing, role, username):
    """Generate PDF report"""
    if not HAS_REPORTLAB:
        return None
    
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, 
                                rightMargin=0.75*inch, leftMargin=0.75*inch,
                                topMargin=0.75*inch, bottomMargin=0.75*inch)
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title = Paragraph("<b>ENHANCED RESUME REPORT</b>", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        # Info
        info = Paragraph(f"<b>Target Role:</b> {role}<br/><b>Candidate:</b> {username}<br/><b>Date:</b> {datetime.now().strftime('%B %d, %Y')}", styles['Normal'])
        elements.append(info)
        elements.append(Spacer(1, 0.3*inch))
        
        # Present skills
        if present:
            h1 = Paragraph("<b>✓ Current Skills:</b>", styles['Heading2'])
            elements.append(h1)
            p1 = Paragraph(", ".join(present[:25]), styles['Normal'])
            elements.append(p1)
            elements.append(Spacer(1, 0.2*inch))
        
        # Missing skills
        if missing:
            h2 = Paragraph("<b>+ Recommended Skills to Add:</b>", styles['Heading2'])
            elements.append(h2)
            p2 = Paragraph(", ".join(missing[:25]), styles['Normal'])
            elements.append(p2)
            elements.append(Spacer(1, 0.2*inch))
        
        # Summary
        h3 = Paragraph("<b>Resume Summary:</b>", styles['Heading2'])
        elements.append(h3)
        summary = " ".join(text.split()[:200])
        if len(text.split()) > 200:
            summary += "..."
        p3 = Paragraph(summary, styles['Normal'])
        elements.append(p3)
        elements.append(Spacer(1, 0.2*inch))
        
        # Action plan
        h4 = Paragraph("<b>Action Plan:</b>", styles['Heading2'])
        elements.append(h4)
        
        actions = [
            "1. Add recommended skills to your resume",
            "2. Build projects using these skills",
            "3. Get relevant certifications",
            "4. Quantify achievements with numbers",
            "5. Tailor resume for each application"
        ]
        
        for action in actions:
            p = Paragraph(action, styles['Normal'])
            elements.append(p)
        
        # Footer
        elements.append(Spacer(1, 0.2*inch))
        footer = Paragraph(f"<i>Generated by Smart Resume Enhancement System on {datetime.now().strftime('%B %d, %Y')}</i>", styles['Normal'])
        elements.append(footer)
        
        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
        
    except Exception as e:
        st.error(f"PDF generation error: {e}")
        return None

def get_job_links(job_title):
    """Get job search URLs"""
    job = job_title.replace(" ", "%20")
    return {
        "LinkedIn": f"https://www.linkedin.com/jobs/search/?keywords={job}",
        "Indeed": f"https://www.indeed.com/jobs?q={job}",
        "Glassdoor": f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={job}",
        "Monster": f"https://www.monster.com/jobs/search/?q={job}",
        "Google Jobs": f"https://www.google.com/search?q={job}+jobs&ibp=htl;jobs"
    }

# ===================== PAGE CONFIG =====================
st.set_page_config(page_title="Smart Resume Enhancement", page_icon="📄", layout="wide")

# ===================== HEADER =====================
st.markdown("""
<div style='text-align:center; background:linear-gradient(135deg,#667eea,#764ba2);
padding:1.5rem;border-radius:10px;color:white;margin-bottom:2rem;'>
    <h1>🧠 Smart Resume Enhancement System</h1>
    <p style='font-size:1rem;margin:0;'>AI-Powered Job Alignment • Resume Optimization • PDF Reports</p>
</div>
""", unsafe_allow_html=True)

# ===================== SIDEBAR LOGIN =====================
with st.sidebar:
    st.header("🔐 User Login")
    
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ""
    
    if not st.session_state.logged_in:
        st.info("Login to access the system")
        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔓 Login", use_container_width=True):
                if username and password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("Welcome!")
                    st.rerun()
                else:
                    st.error("Enter credentials")
        
        with col2:
            if st.button("🚀 Demo", use_container_width=True):
                st.session_state.logged_in = True
                st.session_state.username = "Demo User"
                st.rerun()
    else:
        st.success(f"👤 **{st.session_state.username}**")
        st.metric("Available Job Roles", len(JOB_DATA))
        
        with st.expander("🔧 System Status"):
            st.write("✅ PDF Reader:", "Loaded" if HAS_PDF else "❌ Missing")
            st.write("✅ ML Engine:", "Loaded" if HAS_SKLEARN else "❌ Missing")
            st.write("✅ PDF Generator:", "Loaded" if HAS_REPORTLAB else "❌ Missing")
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

# ===================== MAIN APP =====================
if st.session_state.get("logged_in"):
    
    st.markdown("### 📂 Upload Your Resume")
    st.caption("Upload a PDF resume for AI-powered analysis")
    
    uploaded = st.file_uploader("Choose PDF file", type=["pdf"])
    
    if uploaded:
        with st.spinner("🔍 Analyzing your resume..."):
            resume_text = extract_text_from_pdf(uploaded)
        
        if not resume_text.startswith("ERROR"):
            st.success("✅ Resume processed successfully!")
            
            # Store in session
            st.session_state.resume_text = resume_text
            st.session_state.job_matches = analyze_resume(resume_text)
            
            # Tabs
            tab1, tab2, tab3, tab4 = st.tabs(["🎯 Job Matches", "🔧 Skill Analysis", "📄 Resume Preview", "📥 PDF Report"])
            
            # ==================== TAB 1: JOB MATCHES ====================
            with tab1:
                st.markdown("### 🎯 Top Job Matches")
                st.caption("Jobs ranked by similarity to your resume")
                
                matches = st.session_state.job_matches
                
                for i, match in enumerate(matches[:8], 1):
                    score = match["score"]
                    emoji = "🟢" if score >= 70 else "🟡" if score >= 50 else "🔴"
                    
                    with st.expander(f"{emoji} #{i} **{match['job']}** - {score}%"):
                        st.progress(score / 100)
                        
                        st.markdown(f"**🔗 Search for {match['job']} jobs:**")
                        links = get_job_links(match['job'])
                        
                        cols = st.columns(3)
                        for idx, (board, url) in enumerate(links.items()):
                            with cols[idx % 3]:
                                st.markdown(f"[{board}]({url})")
                        
                        # Show key skills
                        skills = JOB_DATA.get(match['job'], [])
                        if skills:
                            st.info(f"**Key Skills:** {', '.join(skills[:10])}")
            
            # ==================== TAB 2: SKILL ANALYSIS ====================
            with tab2:
                st.markdown("### 🔧 Skill Gap Analysis")
                st.caption("Identify skill gaps for your target role")
                
                role = st.selectbox("Select target role:", list(JOB_DATA.keys()))
                
                if st.button("🔍 Analyze Skills", type="primary", use_container_width=True):
                    present, missing, message, status = check_skill_gap(resume_text, role)
                    
                    if status == "success":
                        st.success(message)
                    else:
                        st.warning(message)
                    
                    # Metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("✅ Skills You Have", len(present))
                    with col2:
                        st.metric("📚 Skills to Add", len(missing))
                    with col3:
                        total = len(present) + len(missing)
                        match = round((len(present)/total)*100, 1) if total > 0 else 0
                        st.metric("🎯 Match", f"{match}%")
                    
                    st.markdown("---")
                    
                    # All skills
                    all_skills = JOB_DATA.get(role, [])
                    st.info(f"**All Required Skills for {role}:** {', '.join(all_skills)}")
                    
                    st.markdown("---")
                    
                    # Comparison
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**✅ Skills You Have:**")
                        if present:
                            for skill in present:
                                st.write(f"• {skill}")
                        else:
                            st.write("*None found*")
                    
                    with col2:
                        st.markdown("**⚠️ Skills You Need:**")
                        if missing:
                            for skill in missing:
                                st.write(f"• {skill}")
                        else:
                            st.write("*All skills present!*")
                    
                    st.markdown("---")
                    
                    # Action plan
                    st.markdown("**💡 Action Plan:**")
                    st.info(f"""
**To enhance your resume for {role}:**
1. Focus on adding the top 5 missing skills
2. Build 2-3 projects demonstrating these skills
3. Get relevant certifications
4. Update your resume with quantified achievements
5. Network with {role} professionals on LinkedIn
                    """)
                    
                    # Save for PDF
                    st.session_state.skill_analysis = {
                        "role": role,
                        "present": present,
                        "missing": missing
                    }
            
            # ==================== TAB 3: PREVIEW ====================
            with tab3:
                st.markdown("### 📄 Resume Text Preview")
                
                word_count = len(resume_text.split())
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Words", word_count)
                with col2:
                    st.metric("Characters", len(resume_text))
                with col3:
                    st.metric("Pages", max(1, word_count // 300))
                
                st.text_area("Resume Content", resume_text, height=400)
                st.download_button("📥 Download TXT", resume_text, "resume.txt", "text/plain")
            
            # ==================== TAB 4: PDF REPORT ====================
            with tab4:
                st.markdown("### 📥 Generate Enhanced PDF Report")
                
                if not HAS_REPORTLAB:
                    st.error("❌ PDF generation not available")
                    st.info("Please ensure 'reportlab' is in requirements.txt")
                elif "skill_analysis" in st.session_state:
                    analysis = st.session_state.skill_analysis
                    
                    st.success(f"✅ Ready to generate report for: **{analysis['role']}**")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Current Skills", len(analysis['present']))
                    with col2:
                        st.metric("Skills to Add", len(analysis['missing']))
                    
                    if st.button("🎨 Generate PDF Report", type="primary", use_container_width=True):
                        with st.spinner("Creating PDF..."):
                            pdf = generate_pdf_report(
                                resume_text,
                                analysis['present'],
                                analysis['missing'],
                                analysis['role'],
                                st.session_state.username
                            )
                        
                        if pdf:
                            st.success("✅ PDF generated!")
                            st.download_button(
                                "📥 Download Enhanced Resume Report",
                                pdf,
                                f"resume_report_{analysis['role'].replace(' ', '_')}.pdf",
                                "application/pdf",
                                use_container_width=True
                            )
                            
                            st.info("""
                            **PDF includes:**
                            • Your current skills
                            • Recommended skills to add
                            • Resume summary
                            • Action plan for improvement
                            """)
                else:
                    st.info("👆 First analyze skills in the **Skill Analysis** tab")
        
        else:
            st.error(resume_text)
            st.info("Ensure PDF is not password-protected and contains text")

else:
    # Landing page
    st.markdown("""
    ## 🔒 Please Log In to Continue
    
    ### System Features:
    
    **📊 Resume Analysis**
    - AI-powered text extraction
    - Instant skill matching
    - Job compatibility scoring
    
    **🎯 Job Matching**
    - Match to 10+ job roles
    - Direct links to job boards
    - Skill requirements overview
    
    **🔧 Skill Enhancement**
    - Detailed skill gap analysis
    - Personalized recommendations
    - PDF report generation
    
    **👈 Use the sidebar to login or start demo!**
    """)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**📄 PDF Analysis**\n\nInstant processing")
    with col2:
        st.success("**🎯 Smart Matching**\n\nAI recommendations")
    with col3:
        st.warning("**📈 Career Growth**\n\nPersonalized plans")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#6c757d; padding:15px;">
    <p style="margin:0;"><b>Smart Resume Enhancement System</b></p>
    <p style="margin:0; font-size:12px;">Powered by AI • Built with Streamlit • © 2025</p>
</div>
""", unsafe_allow_html=True)
