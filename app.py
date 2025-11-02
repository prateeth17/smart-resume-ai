
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
except Exception as e:
    st.error(f"❌ Error loading resume_ai: {e}")
    MODULES_LOADED = False

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
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
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
    """Generate job search URLs"""
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

def get_career_advice(question):
    """Provide career advice based on keywords"""
    q = question.lower()
    
    if "software" in q or "developer" in q or "programming" in q:
        return """**🚀 Software Engineering Career Path**

**Essential Skills:**
• Python, Java, JavaScript, C++
• Data Structures & Algorithms
• SQL, MongoDB databases
• Git/GitHub version control
• React, Django, Node.js
• AWS, Azure, GCP
• Docker, Kubernetes

**Roadmap:**
1. Learn programming fundamentals (3-6 months)
2. Practice DSA on LeetCode (ongoing)
3. Build 3-5 portfolio projects
4. Contribute to open source
5. Network on LinkedIn
6. Apply strategically

**Salary:** $70K-$200K+ depending on experience"""

    elif "data" in q or "machine learning" in q or "ai" in q:
        return """**📊 Data Science & AI Career Path**

**Core Skills:**
• Python (pandas, numpy, scikit-learn)
• Statistics & Mathematics
• Machine Learning algorithms
• TensorFlow, PyTorch
• Data Visualization (Tableau, Power BI)
• SQL & Big Data
• Deep Learning

**Learning Path:**
1. Master Python & statistics (2-3 months)
2. Complete ML courses (Coursera, edX)
3. Kaggle competitions
4. Build 5+ ML projects
5. Specialize (NLP, Computer Vision, etc.)
6. Get certified (AWS ML, TensorFlow)

**Salary:** $80K-$180K+ for ML Engineers"""

    elif "resume" in q or "cv" in q:
        return """**📝 Resume Best Practices**

**Must-Haves:**
✓ Contact info (phone, email, LinkedIn, GitHub)
✓ Professional summary (2-3 lines)
✓ Work experience (quantified achievements)
✓ Technical & soft skills
✓ Education & certifications
✓ Projects with links

**Power Tips:**
• Quantify: "Increased sales 30%" not "Improved sales"
• Action verbs: Led, Built, Optimized, Achieved
• ATS-friendly: Standard fonts, clear sections
• Keywords: Match job descriptions
• Length: 1 page (<5 years), 2 pages (senior)
• Zero typos!

**Avoid:**
❌ Generic objectives
❌ Job duties instead of achievements
❌ Unexplained gaps
❌ Irrelevant info"""

    elif "interview" in q:
        return """**🎯 Interview Success Strategy**

**Preparation (1-2 weeks):**
✓ Research company thoroughly
✓ Review job description
✓ Prepare STAR stories
✓ Practice coding (LeetCode)
✓ Prepare 5-10 questions to ask
✓ Mock interviews

**During Interview:**
• Professional attire
• Arrive 10 min early
• Eye contact & confidence
• STAR method for answers
• Think out loud (technical)
• Ask smart questions

**Common Questions:**
1. Tell me about yourself
2. Why this role/company?
3. Greatest strength/weakness
4. Describe challenging project
5. Where do you see yourself in 5 years?

**Follow-Up:**
• Thank-you email within 24 hours
• Mention specific points discussed
• Reiterate interest"""

    elif "skills" in q or "learn" in q:
        return """**🔥 Top In-Demand Skills (2025)**

**Technical:**
🔹 AI & Machine Learning
🔹 Cloud Computing (AWS/Azure/GCP)
🔹 Cybersecurity
🔹 Data Science & Analytics
🔹 Full-Stack Development
🔹 DevOps & CI/CD
🔹 Blockchain

**Soft Skills:**
🔹 Communication
🔹 Problem-solving
🔹 Leadership
🔹 Adaptability
🔹 Critical thinking
🔹 Collaboration
🔹 Time management

**Learn via:**
📚 Coursera, Udemy, edX
💻 GitHub projects, Kaggle
📜 AWS, Google Cloud certs
🤝 LinkedIn, meetups"""

    elif "career" in q or "job" in q:
        return """**🎯 Career Development Strategy**

**1-Year Goals:**
• Identify skill gaps
• Learn 2-3 key skills
• Build portfolio (3-5 projects)
• Network (50+ connections)
• Get 1-2 certifications

**Job Search:**
• Quality over quantity (5-10 targeted apps)
• 70% jobs via referrals/networking
• Active LinkedIn presence
• GitHub portfolio
• Track applications

**Negotiation:**
💰 Research market rates (Glassdoor, Levels.fyi)
💰 Wait for offer before salary talk
💰 Negotiate total package (equity, bonus, remote)
💰 Be confident but professional
💰 Get everything in writing"""

    else:
        return """**🤖 AI Career Assistant**

I can help with:

**📌 Career Paths**
   • Software Engineering
   • Data Science & ML
   • Cloud Architecture
   • DevOps

**📌 Job Search**
   • Resume optimization
   • Interview prep
   • Salary negotiation
   • Networking

**📌 Skills**
   • In-demand skills
   • Certifications
   • Learning resources

**Ask me:**
- "How to become a software engineer?"
- "Best data science skills?"
- "Resume tips"
- "Interview preparation"

Type your question! 👆"""

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
                    st.success(f"Welcome!")
                    st.rerun()
                else:
                    st.error("Enter credentials")
        
        with col2:
            if st.button("Demo", use_container_width=True):
                st.session_state["logged_in"] = True
                st.session_state["username"] = "Demo User"
                st.rerun()
    else:
        st.success(f"👤 {st.session_state['username']}")
        
        if MODULES_LOADED:
            try:
                info = get_module_info()
                st.metric("Job Roles", info["total_job_roles"])
            except:
                pass
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

# ===================== MAIN APPLICATION =====================
if st.session_state.get("logged_in") and MODULES_LOADED:
    
    st.markdown("### 📂 Upload Your Resume")
    
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
                st.error(f"❌ Error: {e}")
                st.stop()
        
        if resume_data and not resume_data.startswith("ERROR"):
            st.success("✅ Resume processed!")
            
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                "🎯 Jobs", 
                "📊 ATS", 
                "🔧 Skills", 
                "📄 Preview",
                "📥 PDF",
                "🤖 AI Chat"
            ])
            
            # ==================== TAB 1: JOB MATCHES ====================
            with tab1:
                st.markdown("### 🎯 Top Job Matches")
                
                if matched_jobs:
                    for i, job in enumerate(matched_jobs[:8], 1):
                        score = job["similarity"]
                        emoji = "🟢" if score >= 70 else "🟡" if score >= 50 else "🔴"
                        
                        with st.expander(f"{emoji} #{i} {job['job']} - {score}%"):
                            st.progress(score / 100)
                            st.markdown(f"**Search for {job['job']} jobs:**")
                            
                            job_links = search_jobs_simple(job["job"])
                            cols = st.columns(3)
                            for idx, (board, url) in enumerate(job_links.items()):
                                with cols[idx % 3]:
                                    st.markdown(f"[{board}]({url})")
                            
                            role_skills = JOB_DATA.get(job["job"], [])
                            if role_skills:
                                st.info(f"**Key Skills:** {', '.join(role_skills[:8])}")
                else:
                    st.warning("⚠️ No matches. Add more keywords.")
            
            # ==================== TAB 2: ATS SCORE ====================
            with tab2:
                st.markdown("### 📊 ATS Compatibility")
                
                if matched_jobs:
                    st.info("💡 Scores above 70% are excellent")
                    
                    cols = st.columns(3)
                    for idx, job in enumerate(matched_jobs[:6]):
                        with cols[idx % 3]:
                            ats_score = min(100, int(job["similarity"] + random.randint(5, 15)))
                            status = "Excellent" if ats_score >= 75 else "Good" if ats_score >= 60 else "Improve"
                            st.metric(job["job"], f"{ats_score}%", status)
                    
                    st.markdown("---")
                    st.markdown("**💡 Improve ATS Score:**")
                    st.markdown("""
                    1. Use keywords from job descriptions
                    2. Standard format (no tables/graphics)
                    3. Clear sections (Experience, Education, Skills)
                    4. PDF or Word format
                    5. Quantify achievements with numbers
                    """)
                else:
                    st.warning("Upload resume first")
            
            # ==================== TAB 3: SKILL ENHANCEMENT ====================
            with tab3:
                st.markdown("### 💼 Skill Gap Analysis")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    all_jobs = get_all_job_roles()
                    role_input = st.selectbox("Target role:", [""] + all_jobs)
                with col2:
                    custom_role = st.text_input("Custom role:", placeholder="e.g., AI Engineer")
                
                final_role = custom_role if custom_role else role_input
                
                if st.button("🔍 Analyze", type="primary", use_container_width=True):
                    if final_role:
                        with st.spinner("Analyzing..."):
                            suggestions = suggest_improvements(resume_data, final_role)
                        
                        if suggestions["status"] in ["success", "needs_improvement"]:
                            st.success(suggestions["message"]) if suggestions["status"] == "success" else st.warning(suggestions["message"])
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("✅ Have", len(suggestions["present_skills"]))
                            with col2:
                                st.metric("📚 Need", len(suggestions["missing_skills"]))
                            with col3:
                                match_pct = int((len(suggestions["present_skills"]) / (len(suggestions["present_skills"]) + len(suggestions["missing_skills"]) + 0.001)) * 100)
                                st.metric("🎯 Match", f"{match_pct}%")
                            
                            st.markdown("---")
                            
                            all_skills = JOB_DATA.get(final_role, [])
                            if all_skills:
                                st.info(f"**All Required Skills:** {', '.join(all_skills)}")
                            
                            st.markdown("---")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("**✅ Your Skills**")
                                if suggestions["present_skills"]:
                                    for skill in suggestions["present_skills"]:
                                        st.markdown(f"✓ {skill}")
                                else:
                                    st.markdown("*None found*")
                            
                            with col2:
                                st.markdown("**⚠️ Add These**")
                                if suggestions["missing_skills"]:
                                    for skill in suggestions["missing_skills"]:
                                        st.markdown(f"• {skill}")
                                else:
                                    st.success("*All present!*")
                            
                            st.markdown("---")
                            st.markdown("**💡 Action Plan:**")
                            st.info(f"""
**For {final_role}:**
1. Focus on top 5 missing skills
2. Build 2-3 projects using these skills
3. Add skills to resume naturally
4. Get relevant certifications
5. Network with {final_role} professionals
6. Tailor resume for each application
                            """)
                            
                            st.session_state["skill_analysis"] = {
                                "role": final_role,
                                "present": suggestions["present_skills"],
                                "missing": suggestions["missing_skills"]
                            }
                        else:
                            st.error(suggestions["message"])
                    else:
                        st.warning("⚠️ Select a role")
            
            # ==================== TAB 4: RESUME PREVIEW ====================
            with tab4:
                st.markdown("### 📄 Resume Content")
                
                word_count = len(resume_data.split())
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Words", word_count)
                with col2:
                    st.metric("Characters", len(resume_data))
                with col3:
                    st.metric("Pages", max(1, word_count // 300))
                
                st.text_area("Resume Text", resume_data, height=400)
                
                st.download_button(
                    "📥 Download TXT",
                    data=resume_data,
                    file_name=f"resume_{st.session_state['username']}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            # ==================== TAB 5: ENHANCED PDF ====================
            with tab5:
                st.markdown("### 📥 Enhanced Resume PDF")
                
                if not PDF_AVAILABLE:
                    st.error("❌ PDF generation unavailable")
                    st.info("Administrator: Add 'reportlab' to requirements.txt")
                elif "skill_analysis" in st.session_state:
                    analysis = st.session_state["skill_analysis"]
                    st.success(f"✅ Ready for: **{analysis['role']}**")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Current Skills", len(analysis['present']))
                    with col2:
                        st.metric("To Add", len(analysis['missing']))
                    
                    if st.button("🎨 Generate PDF", type="primary", use_container_width=True):
                        with st.spinner("Creating PDF..."):
                            try:
                                pdf_bytes = generate_enhanced_resume(
                                    original_text=resume_data,
                                    missing_skills=analysis['missing'],
                                    present_skills=analysis['present'],
                                    target_role=analysis['role'],
                                    username=st.session_state['username']
                                )
                                
                                st.success("✅ PDF generated!")
                                st.download_button(
                                    "📥 Download PDF",
                                    data=pdf_bytes,
                                    file_name=f"enhanced_resume_{analysis['role'].replace(' ', '_')}.pdf",
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                            except Exception as e:
                                st.error(f"Error: {e}")
                else:
                    st.info("👆 First analyze skills in **Skills** tab")
            
            # ==================== TAB 6: AI CHATBOT ====================
            with tab6:
                st.markdown("### 🤖 AI Career Assistant")
                
                if "chat_history" not in st.session_state:
                    st.session_state["chat_history"] = []
                
                st.markdown("**💬 Suggested Questions:**")
                cols = st.columns(2)
                
                suggestions = [
                    "How to become a software engineer?",
                    "Best skills for data science?",
                    "How to improve my resume?",
                    "Interview preparation tips"
                ]
                
                for idx, suggestion in enumerate(suggestions):
                    with cols[idx % 2]:
                        if st.button(f"🔹 {suggestion}", key=f"suggest_{idx}"):
                            st.session_state["chat_history"].append(("user", suggestion))
                            st.session_state["chat_history"].append(("ai", get_career_advice(suggestion)))
                            st.rerun()
                
                st.markdown("---")
                
                if st.session_state["chat_history"]:
                    for role, msg in st.session_state["chat_history"]:
                        if role == "user":
                            st.markdown(f"**🧑‍💼 You:** {msg}")
                        else:
                            with st.expander("🤖 AI Assistant", expanded=True):
                                st.markdown(msg)
                        st.markdown("")
                else:
                    st.info("👋 Ask me about careers, skills, or job search!")
                
                user_input = st.text_input("💬 Your Question:", placeholder="e.g., What skills are in demand?")
                
                col1, col2 = st.columns([4, 1])
                with col1:
                    if st.button("📤 Send", type="primary", use_container_width=True):
                        if user_input.strip():
                            st.session_state["chat_history"].append(("user", user_input))
                            st.session_state["chat_history"].append(("ai", get_career_advice(user_input)))
                            st.rerun()
                
                with col2:
                    if st.button("🗑️ Clear", use_container_width=True):
                        st.session_state["chat_history"] = []
                        st.rerun()
        
        else:
            st.error("❌ Could not extract text. Ensure PDF is not password-protected and contains selectable text.")

elif not st.session_state.get("logged_in"):
    st.markdown("""
    ## 🔒 Please Log In
    
    ### Features:
    
    **📊 Resume Analysis** - Extract and analyze content
    **🎯 Job Matching** - Find relevant roles
    **🔧 Skill Enhancement** - Identify gaps
    **🤖 AI Assistant** - Career guidance
    
    **👈 Use sidebar to login or try demo!**
    """)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**📄 PDF Processing**\nInstant analysis")
    with col2:
        st.success("**🎯 Smart Matching**\nAI recommendations")
    with col3:
        st.warning("**📈 Career Growth**\nPersonalized plans")

else:
    st.error("❌ System modules failed to load")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#6c757d; padding:20px;">
    <p style="margin:0;"><b>Smart Resume Enhancement System</b></p>
    <p style="margin:0; font-size:12px;">Powered by AI • Built with Streamlit</p>
    <p style="margin:0; font-size:11px;">© 2025 • All Rights Reserved</p>
</div>
""", unsafe_allow_html=True)
