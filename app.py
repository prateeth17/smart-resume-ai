import streamlit as st
import re
from datetime import datetime
import time

# Check imports
PDF_OK = False
ML_OK = False
REPORT_OK = False

try:
    import fitz
    PDF_OK = True
except:
    pass

try:
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    ML_OK = True
except:
    pass

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from io import BytesIO
    REPORT_OK = True
except:
    pass

# Job database
JOBS = {
    "Software Engineer": ["python", "java", "javascript", "react", "nodejs", "docker", "git", "sql", "aws"],
    "Data Scientist": ["python", "machine learning", "pandas", "numpy", "tensorflow", "sql", "statistics"],
    "Frontend Developer": ["html", "css", "javascript", "react", "vue", "angular", "typescript"],
    "Backend Developer": ["python", "java", "nodejs", "sql", "mongodb", "api", "rest"],
    "Full Stack Developer": ["javascript", "react", "nodejs", "sql", "mongodb", "docker", "git"],
    "DevOps Engineer": ["docker", "kubernetes", "jenkins", "aws", "linux", "bash", "terraform"],
}

def get_text(pdf_file):
    """Extract text from PDF with timeout protection"""
    if not PDF_OK:
        return "Error: PDF library not loaded"
    
    try:
        # Read file bytes
        pdf_bytes = pdf_file.read()
        
        # Check file size (limit to 10MB)
        if len(pdf_bytes) > 10 * 1024 * 1024:
            return "Error: File too large (max 10MB)"
        
        # Open PDF
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        # Limit pages (max 20 pages)
        max_pages = min(20, len(doc))
        
        txt = ""
        for page_num in range(max_pages):
            page = doc[page_num]
            txt += page.get_text()
        
        doc.close()
        
        if not txt.strip():
            return "Error: No text found in PDF"
        
        return txt.strip()
    
    except Exception as e:
        return f"Error: {str(e)}"

def match_jobs(txt):
    """Match resume text to job roles"""
    if not ML_OK:
        return basic_match(txt)
    
    result = []
    txt_low = txt.lower()
    
    for job_name, skills in JOBS.items():
        try:
            job_txt = " ".join(skills)
            vec = CountVectorizer()
            matrix = vec.fit_transform([txt_low, job_txt.lower()])
            score = cosine_similarity(matrix)[0][1] * 100
            result.append({"name": job_name, "score": round(score, 1)})
        except:
            continue
    
    result.sort(key=lambda x: x["score"], reverse=True)
    return result

def basic_match(txt):
    """Basic keyword matching fallback"""
    words = set(txt.lower().split())
    result = []
    
    for job_name, skills in JOBS.items():
        matches = sum(1 for s in skills if s.lower() in words)
        score = (matches / len(skills)) * 100
        result.append({"name": job_name, "score": round(score, 1)})
    
    result.sort(key=lambda x: x["score"], reverse=True)
    return result

def find_skills(txt, role):
    """Find matched and missing skills"""
    if role not in JOBS:
        return [], []
    
    skills = JOBS[role]
    words = set(txt.lower().split())
    
    have = [s for s in skills if s.lower() in words]
    need = [s for s in skills if s.lower() not in words]
    
    return have, need

def create_pdf(txt, have, need, role, username):
    """Generate PDF report"""
    if not REPORT_OK:
        return None
    
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        story.append(Paragraph("<b>Resume Enhancement Report</b>", styles['Title']))
        story.append(Spacer(1, 0.3*inch))
        
        info = f"<b>Candidate:</b> {username}<br/><b>Target Role:</b> {role}<br/><b>Date:</b> {datetime.now().strftime('%B %d, %Y')}"
        story.append(Paragraph(info, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        if have:
            story.append(Paragraph("<b>Skills You Have:</b>", styles['Heading2']))
            story.append(Paragraph(", ".join(have), styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        if need:
            story.append(Paragraph("<b>Skills to Add:</b>", styles['Heading2']))
            story.append(Paragraph(", ".join(need), styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph("<b>Summary:</b>", styles['Heading2']))
        summary = " ".join(txt.split()[:100]) + "..."
        story.append(Paragraph(summary, styles['Normal']))
        
        doc.build(story)
        pdf_data = buffer.getvalue()
        buffer.close()
        return pdf_data
    except Exception as e:
        st.error(f"PDF generation error: {str(e)}")
        return None

# Initialize session state
if "user" not in st.session_state:
    st.session_state.user = None
if "processing" not in st.session_state:
    st.session_state.processing = False

# Page setup
st.set_page_config(page_title="Resume App", page_icon="📄", layout="wide")

# Header
st.markdown("""
<div style='background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
padding: 2rem; border-radius: 10px; text-align: center; color: white; margin-bottom: 2rem;'>
<h1>🧠 Smart Resume Enhancement System</h1>
<p style='font-size: 1.1rem; margin: 0;'>AI-Powered Career Analysis</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("🔐 Access")
    
    if not st.session_state.user:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login", use_container_width=True):
                if username and password:
                    st.session_state.user = username
                    st.success("Logged in!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Enter credentials")
        with col2:
            if st.button("Demo", use_container_width=True):
                st.session_state.user = "Demo User"
                st.success("Demo mode!")
                time.sleep(0.5)
                st.rerun()
    else:
        st.success(f"👤 {st.session_state.user}")
        st.metric("Job Roles", len(JOBS))
        
        st.markdown("**System Status:**")
        st.write("✅ PDF Reader" if PDF_OK else "❌ PDF Reader")
        st.write("✅ ML Engine" if ML_OK else "❌ ML Engine")
        st.write("✅ PDF Generator" if REPORT_OK else "❌ PDF Generator")
        
        if st.button("Logout", use_container_width=True):
            st.session_state.clear()
            st.info("Logged out")
            time.sleep(0.5)
            st.rerun()

# Main app
if st.session_state.get("user"):
    
    st.subheader("📂 Upload Your Resume")
    
    # File size warning
    st.caption("📌 Maximum file size: 10MB, 20 pages")
    
    file = st.file_uploader("Choose PDF file", type=["pdf"], key="pdf_uploader")
    
    if file and not st.session_state.processing:
        
        # Prevent multiple processing
        st.session_state.processing = True
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Read file
            status_text.text("📖 Reading PDF...")
            progress_bar.progress(25)
            
            text = get_text(file)
            
            if text.startswith("Error"):
                st.error(text)
                st.session_state.processing = False
            else:
                # Step 2: Process text
                status_text.text("🔍 Analyzing content...")
                progress_bar.progress(50)
                
                st.session_state.text = text
                
                # Step 3: Match jobs
                status_text.text("🎯 Matching jobs...")
                progress_bar.progress(75)
                
                st.session_state.jobs = match_jobs(text)
                
                # Complete
                progress_bar.progress(100)
                status_text.text("✅ Processing complete!")
                time.sleep(0.5)
                
                status_text.empty()
                progress_bar.empty()
                
                st.success("✅ Resume loaded successfully!")
                st.session_state.processing = False
        
        except Exception as e:
            st.error(f"Processing error: {str(e)}")
            st.session_state.processing = False
            progress_bar.empty()
            status_text.empty()
    
    # Show results if text is loaded
    if "text" in st.session_state and "jobs" in st.session_state:
        
        text = st.session_state.text
        
        tab1, tab2, tab3, tab4 = st.tabs(["🎯 Jobs", "🔧 Skills", "📄 Text", "📥 Report"])
        
        with tab1:
            st.markdown("### Top Matching Roles")
            
            for i, job in enumerate(st.session_state.jobs[:5], 1):
                score = job["score"]
                color = "🟢" if score >= 70 else "🟡" if score >= 50 else "🔴"
                
                with st.expander(f"{color} {i}. {job['name']} ({score}%)"):
                    st.progress(score / 100)
                    
                    st.markdown("**🔗 Job Search:**")
                    cols = st.columns(3)
                    links = {
                        "LinkedIn": f"https://linkedin.com/jobs/search?keywords={job['name']}",
                        "Indeed": f"https://indeed.com/jobs?q={job['name']}",
                        "Glassdoor": f"https://glassdoor.com/Job/{job['name']}-jobs-SRCH_KO0,20.htm"
                    }
                    
                    for idx, (site, url) in enumerate(links.items()):
                        with cols[idx]:
                            st.markdown(f"[🔗 {site}]({url})")
        
        with tab2:
            st.markdown("### Skill Gap Analysis")
            
            role = st.selectbox("Select target role:", list(JOBS.keys()))
            
            if st.button("Analyze Skills", type="primary", use_container_width=True):
                have, need = find_skills(text, role)
                
                total = len(have) + len(need)
                match_pct = round((len(have) / total * 100), 1) if total > 0 else 0
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("✅ Have", len(have))
                with col2:
                    st.metric("📚 Need", len(need))
                with col3:
                    st.metric("🎯 Match", f"{match_pct}%")
                
                st.markdown("---")
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.markdown("**✅ Your Skills:**")
                    if have:
                        for skill in have:
                            st.write(f"• {skill}")
                    else:
                        st.write("None found")
                
                with col_b:
                    st.markdown("**⚠️ Add These:**")
                    if need:
                        for skill in need:
                            st.write(f"• {skill}")
                    else:
                        st.write("All present!")
                
                st.session_state.analysis = {
                    "role": role,
                    "have": have,
                    "need": need
                }
        
        with tab3:
            st.markdown("### Resume Content")
            
            words = len(text.split())
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Words", words)
            with col2:
                st.metric("Characters", len(text))
            
            st.text_area("Extracted Text", text, height=300)
            st.download_button("📥 Download Text", text, "resume.txt", use_container_width=True)
        
        with tab4:
            st.markdown("### PDF Report")
            
            if "analysis" in st.session_state:
                a = st.session_state.analysis
                
                st.success(f"Ready to generate report for: **{a['role']}**")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Current Skills", len(a['have']))
                with col2:
                    st.metric("Skills to Add", len(a['need']))
                
                if st.button("🎨 Generate PDF", type="primary", use_container_width=True):
                    with st.spinner("Creating PDF..."):
                        pdf = create_pdf(text, a['have'], a['need'], a['role'], st.session_state.user)
                    
                    if pdf:
                        st.success("✅ PDF created!")
                        st.download_button(
                            "📥 Download PDF Report",
                            pdf,
                            f"resume_report_{a['role'].replace(' ', '_')}.pdf",
                            "application/pdf",
                            use_container_width=True
                        )
                    else:
                        st.error("PDF generation failed - check library installation")
            else:
                st.info("👆 Analyze skills first in the Skills tab")

else:
    st.info("👈 Please login using the sidebar")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**📄 PDF Upload**\nExtract resume text")
    with col2:
        st.success("**🎯 Job Matching**\nFind best roles")
    with col3:
        st.warning("**🔧 Skill Analysis**\nIdentify gaps")

st.markdown("---")
st.markdown("<p style='text-align:center; color:#888;'>© 2025 Smart Resume Enhancement System</p>", unsafe_allow_html=True)
