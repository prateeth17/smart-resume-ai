import streamlit as st
import random

try:
    from resume_ai import analyze_resume, suggest_improvements, get_all_job_roles, JOB_DATA, get_module_info
    LOADED = True
except Exception as e:
    LOADED = False
    st.error(f"Error: {e}")

try:
    from pdf_generator import generate_enhanced_resume
    PDF_OK = True
except:
    PDF_OK = False

st.set_page_config(page_title="Smart Resume Enhancement", page_icon="📄", layout="wide")

st.markdown("""
<div style='text-align:center; background:linear-gradient(135deg,#667eea,#764ba2);
padding:1.5rem;border-radius:10px;color:white;margin-bottom:2rem;'>
    <h1>🧠 Smart Resume Enhancement System</h1>
    <p>AI-Powered Job Alignment and Resume Optimization</p>
</div>
""", unsafe_allow_html=True)

if not LOADED:
    st.error("❌ System failed to load")
    st.stop()

def search_jobs(job_title):
    job = job_title.replace(" ", "%20")
    return {
        "LinkedIn": f"https://www.linkedin.com/jobs/search/?keywords={job}",
        "Indeed": f"https://www.indeed.com/jobs?q={job}",
        "Glassdoor": f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={job}"
    }

with st.sidebar:
    st.header("🔐 Login")
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    
    if not st.session_state["logged_in"]:
        if st.button("🚀 Demo Login", use_container_width=True):
            st.session_state["logged_in"] = True
            st.session_state["username"] = "Demo User"
            st.rerun()
    else:
        st.success(f"👤 {st.session_state.get('username', 'User')}")
        try:
            info = get_module_info()
            st.metric("Job Roles", info["total_job_roles"])
        except:
            pass
        if st.button("Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

if st.session_state.get("logged_in"):
    st.markdown("### 📂 Upload Resume (PDF)")
    uploaded = st.file_uploader("Choose PDF", type=["pdf"])
    
    if uploaded:
        with st.spinner("Analyzing..."):
            text, jobs = analyze_resume(uploaded)
        
        if not text.startswith("ERROR"):
            st.success("✅ Resume processed!")
            
            tab1, tab2, tab3 = st.tabs(["🎯 Jobs", "🔧 Skills", "📄 Preview"])
            
            with tab1:
                st.markdown("### Top Job Matches")
                for i, job in enumerate(jobs[:6], 1):
                    score = job["similarity"]
                    emoji = "🟢" if score >= 70 else "🟡" if score >= 50 else "🔴"
                    with st.expander(f"{emoji} {i}. {job['job']} - {score}%"):
                        links = search_jobs(job['job'])
                        for board, url in links.items():
                            st.markdown(f"[{board}]({url})")
            
            with tab2:
                st.markdown("### Skill Analysis")
                role = st.selectbox("Target Role:", [""] + get_all_job_roles())
                
                if st.button("🔍 Analyze", type="primary"):
                    if role:
                        result = suggest_improvements(text, role)
                        st.success(result["message"])
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**✅ Your Skills**")
                            for s in result["present_skills"]:
                                st.write(f"• {s}")
                        with col2:
                            st.markdown("**⚠️ Missing**")
                            for s in result["missing_skills"]:
                                st.write(f"• {s}")
                        
                        st.session_state["analysis"] = {"role": role, "present": result["present_skills"], "missing": result["missing_skills"]}
                        
                        if PDF_OK:
                            st.markdown("---")
                            if st.button("📥 Generate PDF"):
                                pdf = generate_enhanced_resume(text, result["missing_skills"], result["present_skills"], role, st.session_state["username"])
                                st.download_button("Download PDF", pdf, f"resume_{role.replace(' ', '_')}.pdf", "application/pdf")
                    else:
                        st.warning("Select a role")
            
            with tab3:
                st.markdown("### Resume Preview")
                st.text_area("Text", text, height=400)
                st.download_button("📥 Download TXT", text, "resume.txt", "text/plain")
        else:
            st.error(text)
else:
    st.info("👈 Click 'Demo Login' to start")

st.markdown("---")
st.markdown("<p style='text-align:center;color:#6c757d;'>© 2025 Smart Resume Enhancement System</p>", unsafe_allow_html=True)
