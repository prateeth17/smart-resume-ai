"""
Smart Resume Enhancement System
Main Application File
"""
import streamlit as st
import random

# Import custom modules with error handling
try:
    from resume_ai import (
        analyze_resume, 
        suggest_improvements, 
        get_all_job_roles, 
        JOB_DATA,
        get_module_info
    )
    MODULES_LOADED = True
    MODULE_ERROR = None
except Exception as e:
    MODULES_LOADED = False
    MODULE_ERROR = str(e)

# Try to import PDF generator (optional)
try:
    from pdf_generator import generate_enhanced_resume
    PDF_AVAILABLE = True
except Exception as e:
    PDF_AVAILABLE = False

# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="Smart Resume Enhancement",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===================== CUSTOM CSS =====================
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #667eea, #764ba2);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ===================== HEADER =====================
st.markdown("""
<div class="main-header">
    <h1>🧠 Smart Resume Enhancement System</h1>
    <p style='font-size:1.1rem;margin:0;'>AI-Powered Job Alignment and Resume Optimization</p>
</div>
""", unsafe_allow_html=True)

# ===================== HELPER FUNCTIONS =====================
def search_jobs_simple(job_title, location=""):
    """Generate job search URLs for various job boards"""
    job_encoded = job_title.replace(" ", "%20")
    loc_encoded = location.replace(" ", "%20")
    
    return {
        "LinkedIn": f"https://www.linkedin.com/jobs/search/?keywords={job_encoded}&location={loc_encoded}",
        "Indeed": f"https://www.indeed.com/jobs?q={job_encoded}&l={loc_encoded}",
        "Glassdoor": f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={job_encoded}",
        "Monster": f"https://www.monster.com/jobs/search/?q={job_encoded}",
        "ZipRecruiter": f"https://www.ziprecruiter.com/Jobs/{job_encoded}",
        "Google Jobs": f"https://www.google.com/search?q={job_encoded}+jobs&ibp=htl;jobs"
    }

# ===================== LOGIN SYSTEM =====================
with st.sidebar:
    st.header("🔐 User Login")
    
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
    
    if not st.session_state["logged_in"]:
        st.info("Login to access the system")
        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔓 Login", use_container_width=True):
                if username and password:
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = username
                    st.success("Welcome!")
                    st.rerun()
                else:
                    st.error("Enter credentials")
        
        with col2:
            if st.button("🚀 Demo", use_container_width=True):
                st.session_state["logged_in"] = True
                st.session_state["username"] = "Demo User"
                st.rerun()
    else:
        st.success(f"👤 **{st.session_state['username']}**")
        
        if MODULES_LOADED:
            try:
                info = get_module_info()
                st.metric("Job Roles Available", info["total_job_roles"])
                
                with st.expander("🔧 System Status"):
                    st.write("✅ PyMuPDF:", "Loaded" if info["pymupdf_available"] else "❌ Missing")
                    st.write("✅ Scikit-learn:", "Loaded" if info["sklearn_available"] else "❌ Missing")
                    st.write("✅ PDF Generator:", "Loaded" if PDF_AVAILABLE else "❌ Missing")
            except Exception as e:
                st.warning(f"Status check: {e}")
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

# ===================== ERROR HANDLING =====================
if not MODULES_LOADED:
    st.error("❌ Critical Error: Core modules failed to load")
    st.code(f"Error Details: {MODULE_ERROR}")
    st.info("""
    **Troubleshooting Steps:**
    1. Verify all files are in GitHub repository
    2. Check requirements.txt for all dependencies
    3. Review Streamlit Cloud logs for detailed errors
    4. Ensure data/job_roles.json exists
    """)
    st.stop()

# ===================== MAIN APPLICATION =====================
if st.session_state.get("logged_in"):
    
    st.markdown("### 📂 Upload Your Resume")
    st.caption("Upload a PDF resume for AI-powered analysis and job matching")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file", 
        type=["pdf"],
        help="Upload your resume in PDF format"
    )
    
    if uploaded_file:
        with st.spinner("🔍 Analyzing your resume..."):
            try:
                resume_data, matched_jobs = analyze_resume(uploaded_file)
                st.session_state["resume_text"] = resume_data
                st.session_state["matched_jobs"] = matched_jobs
            except Exception as e:
                st.error(f"❌ Error analyzing resume: {e}")
                st.stop()
        
        if resume_data and not resume_data.startswith("ERROR"):
            st.success("✅ Resume processed successfully!")
            
            # Create tabs
            tab1, tab2, tab3, tab4 = st.tabs([
                "🎯 Job Matches", 
                "🔧 Skill Enhancement", 
                "📄 Resume Preview",
                "📥 Enhanced PDF"
            ])
            
            # ==================== TAB 1: JOB MATCHES ====================
            with tab1:
                st.markdown("### 🎯 Top Job Matches Based on Your Resume")
                st.caption("Jobs ranked by similarity to your resume content")
                
                if matched_jobs:
                    for i, job in enumerate(matched_jobs[:8], 1):
                        score = job["similarity"]
                        
                        # Color coding
                        if score >= 70:
                            emoji = "🟢"
                        elif score >= 50:
                            emoji = "🟡"
                        else:
                            emoji = "🔴"
                        
                        with st.expander(f"{emoji} #{i} **{job['job']}** - Match: **{score}%**"):
                            st.progress(score / 100)
                            
                            st.markdown(f"#### 🔗 Search for {job['job']} jobs:")
                            job_links = search_jobs_simple(job["job"])
                            
                            cols = st.columns(3)
                            for idx, (board, url) in enumerate(job_links.items()):
                                with cols[idx % 3]:
                                    st.markdown(f"[{board}]({url})")
                            
                            # Show key skills
                            role_skills = JOB_DATA.get(job["job"], [])
                            if role_skills:
                                st.markdown("#### 📚 Key Skills for this Role:")
                                st.info(", ".join(role_skills[:12]))
                else:
                    st.warning("⚠️ No job matches found. Try adding more relevant keywords.")
            
            # ==================== TAB 2: SKILL ENHANCEMENT ====================
            with tab2:
                st.markdown("### 💼 Resume Enhancement for Target Role")
                st.caption("Analyze skill gaps and get personalized recommendations")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    all_jobs = get_all_job_roles()
                    role_input = st.selectbox(
                        "Select your target role:",
                        [""] + all_jobs,
                        key="role_select"
                    )
                
                with col2:
                    custom_role = st.text_input(
                        "Or enter custom role:",
                        key="custom_role",
                        placeholder="e.g., AI Engineer"
                    )
                
                final_role = custom_role if custom_role else role_input
                
                if st.button("🔍 Analyze Skill Gap", type="primary", use_container_width=True):
                    if final_role:
                        with st.spinner("🔄 Analyzing..."):
                            suggestions = suggest_improvements(resume_data, final_role)
                        
                        if suggestions["status"] in ["success", "needs_improvement"]:
                            if suggestions["status"] == "success":
                                st.success(suggestions["message"])
                            else:
                                st.warning(suggestions["message"])
                            
                            # Metrics
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("✅ Skills You Have", len(suggestions["present_skills"]))
                            with col2:
                                st.metric("📚 Skills to Add", len(suggestions["missing_skills"]))
                            with col3:
                                match_pct = suggestions.get("match_percentage", 0)
                                st.metric("🎯 Match Score", f"{match_pct}%")
                            
                            st.markdown("---")
                            
                            # All required skills
                            st.markdown("#### 📘 Complete Skill Set for This Role")
                            all_skills = JOB_DATA.get(final_role, [])
                            if all_skills:
                                st.info("**Required Skills:** " + ", ".join(all_skills))
                            
                            st.markdown("---")
                            
                            # Skills comparison
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("#### ✅ Skills You Already Have")
                                if suggestions["present_skills"]:
                                    for skill in suggestions["present_skills"]:
                                        st.markdown(f"✓ **{skill}**")
                                else:
                                    st.markdown("*No matching skills found*")
                            
                            with col2:
                                st.markdown("#### ⚠️ Skills You Should Add")
                                if suggestions["missing_skills"]:
                                    for skill in suggestions["missing_skills"]:
                                        st.markdown(f"• **{skill}**")
                                else:
                                    st.success("*All key skills present!*")
                            
                            st.markdown("---")
                            
                            # Action Plan
                            st.markdown("#### 💡 Personalized Action Plan")
                            st.info(f"""
**To strengthen your resume for {final_role}:**

1. **Skill Development**: Focus on top 5 missing skills
2. **Build Projects**: Create 2-3 projects using these skills
3. **Get Certified**: Pursue relevant certifications
4. **Update Resume**: Add skills naturally throughout
5. **Network**: Connect with {final_role} professionals
6. **Apply Strategically**: Tailor applications to job descriptions
                            """)
                            
                            # Save for PDF generation
                            st.session_state["skill_analysis"] = {
                                "role": final_role,
                                "present": suggestions["present_skills"],
                                "missing": suggestions["missing_skills"]
                            }
                            
                        else:
                            st.error(suggestions["message"])
                    else:
                        st.warning("⚠️ Please select or enter a job role first")
            
            # ==================== TAB 3: RESUME PREVIEW ====================
            with tab3:
                st.markdown("### 📄 Extracted Resume Content")
                
                word_count = len(resume_data.split())
                char_count = len(resume_data)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Words", word_count)
                with col2:
                    st.metric("Characters", char_count)
                with col3:
                    st.metric("Estimated Pages", max(1, word_count // 300))
                
                st.markdown("---")
                
                st.text_area(
                    "Resume Text",
                    resume_data,
                    height=400,
                    key="preview_area"
                )
                
                st.download_button(
                    label="📥 Download as TXT",
                    data=resume_data,
                    file_name=f"resume_{st.session_state['username']}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            # ==================== TAB 4: ENHANCED PDF ====================
            with tab4:
                st.markdown("### 📥 Generate Enhanced Resume Report")
                st.caption("Create a professional PDF with AI recommendations")
                
                if not PDF_AVAILABLE:
                    st.error("❌ PDF generation is currently unavailable")
                    st.info("Administrator: Ensure 'reportlab' is in requirements.txt")
                elif "skill_analysis" in st.session_state:
                    analysis = st.session_state["skill_analysis"]
                    
                    st.success(f"✅ Ready to generate enhanced report for: **{analysis['role']}**")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Current Skills", len(analysis['present']))
                    with col2:
                        st.metric("Skills to Add", len(analysis['missing']))
                    
                    st.markdown("---")
                    
                    if st.button("🎨 Generate Enhanced PDF Report", type="primary", use_container_width=True):
                        with st.spinner("Creating your enhanced resume report..."):
                            try:
                                pdf_bytes = generate_enhanced_resume(
                                    original_text=resume_data,
                                    missing_skills=analysis['missing'],
                                    present_skills=analysis['present'],
                                    target_role=analysis['role'],
                                    username=st.session_state['username']
                                )
                                
                                st.success("✅ PDF generated successfully!")
                                
                                st.download_button(
                                    label="📥 Download Enhanced Resume Report",
                                    data=pdf_bytes,
                                    file_name=f"enhanced_resume_{analysis['role'].replace(' ', '_')}.pdf",
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                                
                                st.info("""
                                💡 **What's included in the PDF:**
                                - Your current skills highlighted
                                - Recommended skills to add
                                - Skills analysis summary
                                - Action plan for improvement
                                - Professional formatting
                                """)
                                
                            except Exception as e:
                                st.error(f"Error generating PDF: {e}")
                else:
                    st.info("👆 First, analyze your resume in the **Skill Enhancement** tab to generate a report")
        
        else:
            st.error("❌ Could not extract text from PDF")
            st.info("""
            **Please ensure:**
            - The PDF is not password-protected
            - The PDF contains selectable text (not just images)
            - The file is not corrupted
            """)

else:
    # Landing page
    st.markdown("""
    ## 🔒 Please Log In to Continue
    
    ### Features of This System:
    
    **📊 Resume Analysis**
    - Extract and analyze resume content using AI
    - Match your skills to relevant job roles
    - Get instant feedback on your profile
    
    **🎯 Job Matching**
    - Find the best job roles for your profile
    - Get direct links to multiple job boards
    - See detailed skill requirements
    
    **🔧 Skill Enhancement**
    - Identify skill gaps for target roles
    - Get personalized learning recommendations
    - Generate enhanced resume reports in PDF
    
    **👈 Use the sidebar to login or try the demo!**
    """)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**📄 PDF Processing**\n\nUpload and analyze instantly")
    with col2:
        st.success("**🎯 Smart Matching**\n\nAI-powered job recommendations")
    with col3:
        st.warning("**📈 Career Growth**\n\nPersonalized development plans")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#6c757d; padding:20px;">
    <p style="margin:0; font-size:14px;"><b>Smart Resume Enhancement System</b></p>
    <p style="margin:0; font-size:12px;">Powered by AI • Built with Streamlit</p>
    <p style="margin:0; font-size:11px; color:#adb5bd;">© 2025 • All Rights Reserved</p>
</div>
""", unsafe_allow_html=True)
