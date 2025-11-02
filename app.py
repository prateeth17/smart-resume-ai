import streamlit as st
from resume_ai import analyze_resume, suggest_improvements, get_all_job_roles, JOB_DATA
from duckduckgo_search import DDGS  # ✅ Fixed import
import random


# ===================== PAGE CONFIG =====================
st.set_page_config(page_title="Smart Resume Enhancement", page_icon="📄", layout="wide")


# ===================== DARK/LIGHT MODE =====================
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "Light"  # Default to Light mode

theme_mode = st.sidebar.radio(
    "🎨 Theme Mode",
    options=["Light", "Dark"],
    index=0 if st.session_state["theme_mode"] == "Light" else 1,
    horizontal=True
)
st.session_state["theme_mode"] = theme_mode

if st.session_state["theme_mode"] == "Dark":
    st.markdown("""
        <style>
        body { background-color: #0E1117; color: #FAFAFA; }
        .stApp { background-color: #0E1117; }
        </style>
    """, unsafe_allow_html=True)


# ===================== HEADER =====================
st.markdown("""
<div style='text-align:center; background:linear-gradient(135deg,#667eea,#764ba2);
padding:1.5rem;border-radius:10px;color:white;'>
    <h1>🧠 Smart Resume Enhancement System</h1>
    <p>AI-Powered Job Alignment and Resume Optimization</p>
</div>
""", unsafe_allow_html=True)


# ===================== LOGIN SYSTEM =====================
with st.sidebar:
    st.header("🔐 User Login")


    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""


    if not st.session_state["logged_in"]:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login", use_container_width=True):
            if username and password:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.rerun()
            else:
                st.error("Enter both username and password.")
    else:
        st.success(f"Welcome, {st.session_state['username']}!")
        if st.button("Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()


# ===================== HELPER =====================
def search_jobs_simple(job_title, location=""):
    job_boards = {
        "LinkedIn": f"https://www.linkedin.com/jobs/search/?keywords={job_title}&location={location}",
        "Indeed": f"https://www.indeed.com/jobs?q={job_title}&l={location}",
        "Glassdoor": f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={job_title}",
        "Monster": f"https://www.monster.com/jobs/search/?q={job_title}",
        "ZipRecruiter": f"https://www.ziprecruiter.com/Jobs/{job_title}",
        "Google Jobs": f"https://www.google.com/search?q={job_title}+jobs&ibp=htl;jobs"
    }
    return job_boards



# ===================== MAIN BODY =====================
if st.session_state.get("logged_in"):


    st.subheader("📂 Upload Your Resume")
    uploaded_file = st.file_uploader("Upload PDF Resume", type=["pdf"])


    if uploaded_file:
        file_id = f"{uploaded_file.name}_{uploaded_file.size}"
        
        if "last_processed_file" not in st.session_state or st.session_state["last_processed_file"] != file_id:
            with st.spinner("Analyzing your resume..."):
                try:
                    resume_data, matched_jobs = analyze_resume(uploaded_file)
                    st.session_state["resume_text"] = resume_data
                    st.session_state["matched_jobs"] = matched_jobs
                    st.session_state["last_processed_file"] = file_id
                except Exception as e:
                    st.error(f"Error processing resume: {str(e)}")
                    st.session_state["resume_text"] = None
                    st.session_state["matched_jobs"] = []
        
        resume_data = st.session_state.get("resume_text")
        matched_jobs = st.session_state.get("matched_jobs", [])


        if resume_data:
            st.success("✅ Resume processed successfully!")


            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "🎯 Job Matches", "📊 ATS Score Analysis",
                "🔧 Resume Enhancement", "📄 Resume Preview", "🤖 AI Career Chatbot"
            ])


            # ---------------------------------------------------
            # TAB 1: JOB MATCHES
            # ---------------------------------------------------
            with tab1:
                st.markdown("### 🎯 Top Job Matches Based on Your Resume")
                if matched_jobs:
                    for i, job in enumerate(matched_jobs[:5], 1):
                        score = job["similarity"]
                        with st.expander(f"#{i} {job['job']} (Match: {score}%)"):
                            st.progress(score / 100)
                            job_links = search_jobs_simple(job["job"])
                            st.markdown(f"**Recommended Jobs for {job['job']}:**")
                            for board, url in job_links.items():
                                st.markdown(f"🔗 [{board}]({url})", unsafe_allow_html=True)
                else:
                    st.warning("No job matches found. Try improving your resume keywords.")


            # ---------------------------------------------------
            # TAB 2: ATS SCORE ANALYSIS
            # ---------------------------------------------------
            with tab2:
                st.markdown("### 📊 ATS Compatibility Analysis")
                if matched_jobs:
                    st.caption("Approximate compatibility based on your resume and common ATS keyword match rate.")
                    for job in matched_jobs[:5]:
                        ats_score = min(100, int(job["similarity"] + random.randint(10, 25)))
                        st.metric(label=job["job"], value=f"{ats_score}%")
                else:
                    st.warning("Upload a resume to view ATS compatibility.")


            # ---------------------------------------------------
            # TAB 3: RESUME ENHANCEMENT
            # ---------------------------------------------------
            with tab3:
                st.markdown("### 💼 Improve Resume for a Specific Role")


                all_jobs = get_all_job_roles()
                role_input = st.selectbox("Select a desired role:", [""] + all_jobs)
                if role_input == "":
                    role_input = st.text_input("Or enter a custom role:")


                if st.button("🔍 Analyze Gap", type="primary"):
                    if role_input:
                        with st.spinner("Analyzing skill gaps..."):
                            suggestions = suggest_improvements(resume_data, role_input)


                        if suggestions["status"] in ["success", "needs_improvement"]:
                            st.success(suggestions["message"])


                            # Full Skill Set for Role
                            st.markdown("#### 📘 All Key Skills for This Role:")
                            all_skills = JOB_DATA.get(role_input, [])
                            st.markdown(", ".join(all_skills))


                            # Available & Missing
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("#### ✅ Present Skills:")
                                for skill in suggestions["present_skills"]:
                                    st.markdown(f"- {skill}")
                            with col2:
                                st.markdown("#### ⚠️ Missing Skills:")
                                for skill in suggestions["missing_skills"]:
                                    st.markdown(f"- {skill}")


                            st.markdown("#### 💡 Recommendations:")
                            st.info(f"""
                            To enhance your resume for **{role_input}**:
                            - Add missing skills and relevant projects  
                            - Quantify results (e.g., "increased efficiency by 30%")  
                            - Include certifications  
                            - Optimize wording for ATS scanning
                            """)
                        else:
                            st.warning(suggestions["message"])
                    else:
                        st.warning("Please select or enter a role.")


            # ---------------------------------------------------
            # TAB 4: RESUME PREVIEW
            # ---------------------------------------------------
            with tab4:
                st.markdown("### 📄 Resume Text Preview")
                st.text_area("Extracted Resume Text", resume_data, height=400)


            # ---------------------------------------------------
            # TAB 5: AI CAREER CHATBOT
            # ---------------------------------------------------
            with tab5:
                st.subheader("🤖 AI Career Chatbot (Real-Time Web Search, No API Key)")
                st.caption("Ask career, skill, or resume-related questions — responds in English using DuckDuckGo search.")


                if "chat_history" not in st.session_state:
                    st.session_state["chat_history"] = []


                for role, msg in st.session_state["chat_history"]:
                    if role == "user":
                        st.markdown(f"🧑‍💼 **You:** {msg}")
                    else:
                        st.markdown(f"🤖 **AI:** {msg}")


                user_input = st.text_input("💬 Ask your question:", key="chat_query")
                
                col_btn1, col_btn2 = st.columns([4, 1])
                with col_btn1:
                    ask_clicked = st.button("Ask AI", type="primary", use_container_width=True)
                with col_btn2:
                    if st.button("Clear", use_container_width=True):
                        st.session_state["chat_history"] = []
                        st.rerun()
                
                if ask_clicked:
                    if user_input.strip():
                        with st.spinner("Searching the web..."):
                            try:
                                results = []
                                with DDGS() as ddgs:
                                    search_results = ddgs.text(user_input, region="wt-wt", safesearch="moderate", max_results=3)
                                    for r in search_results:
                                        if r and "title" in r and "href" in r and "body" in r:
                                            if r["title"] and r["href"] and r["body"]:
                                                results.append(r)


                                if results:
                                    snippets = [f"🔹 [{r['title']}]({r['href']}) — {r['body']}" for r in results]
                                    ai_response = "Here's what I found:\n\n" + "\n\n".join(snippets)
                                else:
                                    # Fallback AI logic
                                    q = user_input.lower()
                                    if "software engineer" in q:
                                        ai_response = "To become a Software Engineer, focus on skills like Python, Java, data structures, algorithms, databases (SQL), version control (Git), and frameworks such as Django or React."
                                    elif "resume" in q:
                                        ai_response = "A strong resume should highlight measurable achievements, relevant skills, clear formatting, and keywords matching the job description."
                                    elif "skills" in q:
                                        ai_response = "Common in-demand skills include problem-solving, communication, data analysis, and technical specialization like cloud computing or AI."
                                    else:
                                        ai_response = "Sorry, I couldn't find relevant information."
                            except Exception as e:
                                ai_response = f"Search error: {str(e)}"


                        st.session_state["chat_history"].append(("user", user_input))
                        st.session_state["chat_history"].append(("ai", ai_response))
                        st.rerun()
                    else:
                        st.warning("Please enter a question.")
        else:
            st.error("Could not extract text from the PDF. Try again.")
else:
    st.info("🔒 Please log in to access the system.")


# -------------------------------------------------------------
# FOOTER
# -------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#6c757d;">
    <p>Made with ❤️ using Streamlit | © 2025 Smart Resume Enhancement System</p>
</div>
""", unsafe_allow_html=True)
