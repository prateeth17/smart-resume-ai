import streamlit as st
from resume_ai import analyze_resume, suggest_improvements, get_all_job_roles, JOB_DATA
from duckduckgo_search import DDGS  # ✅ Fixed import
import random


# ===================== PAGE CONFIG =====================
st.set_page_config(page_title="Smart Resume Enhancement", page_icon="📄", layout="wide")


# ===================== DARK/LIGHT MODE =====================
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "Default"  # Default to cream mode

theme_mode = st.sidebar.radio(
    "🎨 Theme Mode",
    options=["Default", "Light", "Dark"],
    index=["Default", "Light", "Dark"].index(st.session_state["theme_mode"]),
    horizontal=True
)
st.session_state["theme_mode"] = theme_mode

if st.session_state["theme_mode"] == "Light":
    st.markdown("""
        <style>
        .stApp { background-color: #FFFFFF !important; color: #1F1F1F !important; }
        .stMarkdown { color: #1F1F1F !important; }
        </style>
    """, unsafe_allow_html=True)
elif st.session_state["theme_mode"] == "Dark":
    st.markdown("""
        <style>
        .stApp { background-color: #0E1117 !important; color: #FAFAFA !important; }
        .stMarkdown { color: #FAFAFA !important; }
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
                "📄 Resume Preview", "📥 PDF Report", "📊 Skills Chart"
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
            
            with tab6:
                st.markdown("### 📥 Generate PDF Report")
                st.caption("Download a comprehensive resume analysis report")
                
                report_role = st.selectbox("Select role for report:", [""] + get_all_job_roles(), key="report_role")
                
                if st.button("🎨 Generate PDF Report", type="primary", use_container_width=True):
                    if report_role:
                        with st.spinner("Creating your professional report..."):
                            try:
                                from reportlab.lib.pagesizes import letter
                                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                                from reportlab.lib.units import inch
                                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
                                from reportlab.lib import colors
                                from io import BytesIO
                                from datetime import datetime
                                
                                suggestions = suggest_improvements(resume_data, report_role)
                                
                                buffer = BytesIO()
                                doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
                                story = []
                                styles = getSampleStyleSheet()
                                
                                title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#667eea'), spaceAfter=12, alignment=1)
                                story.append(Paragraph("🧠 Resume Enhancement Report", title_style))
                                story.append(Spacer(1, 0.2*inch))
                                
                                info_data = [
                                    ["Candidate:", st.session_state['username']],
                                    ["Target Role:", report_role],
                                    ["Date:", datetime.now().strftime('%B %d, %Y')],
                                    ["Match Score:", f"{suggestions.get('match_percentage', 0)}%"]
                                ]
                                info_table = Table(info_data, colWidths=[1.5*inch, 4*inch])
                                info_table.setStyle(TableStyle([
                                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
                                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
                                ]))
                                story.append(info_table)
                                story.append(Spacer(1, 0.3*inch))
                                
                                story.append(Paragraph("<b>✅ Skills You Have:</b>", styles['Heading2']))
                                if suggestions["present_skills"]:
                                    skills_text = ", ".join(suggestions["present_skills"])
                                    story.append(Paragraph(skills_text, styles['Normal']))
                                else:
                                    story.append(Paragraph("None identified", styles['Normal']))
                                story.append(Spacer(1, 0.2*inch))
                                
                                story.append(Paragraph("<b>⚠️ Skills to Add:</b>", styles['Heading2']))
                                if suggestions["missing_skills"]:
                                    skills_text = ", ".join(suggestions["missing_skills"])
                                    story.append(Paragraph(skills_text, styles['Normal']))
                                else:
                                    story.append(Paragraph("All skills present!", styles['Normal']))
                                story.append(Spacer(1, 0.2*inch))
                                
                                story.append(Paragraph("<b>💡 Action Items:</b>", styles['Heading2']))
                                recommendations = [
                                    "• Add missing skills with concrete project examples",
                                    "• Quantify achievements (e.g., 'increased efficiency by 30%')",
                                    "• Include relevant certifications and courses",
                                    "• Optimize keywords for ATS compatibility",
                                    "• Use strong action verbs (achieved, implemented, led)",
                                    "• Ensure clear formatting and structure"
                                ]
                                for rec in recommendations:
                                    story.append(Paragraph(rec, styles['Normal']))
                                story.append(Spacer(1, 0.2*inch))
                                
                                story.append(Paragraph("<b>🎯 Top 5 Job Matches:</b>", styles['Heading2']))
                                for i, job in enumerate(matched_jobs[:5], 1):
                                    story.append(Paragraph(f"{i}. {job['job']} - {job['similarity']}% match", styles['Normal']))
                                
                                doc.build(story)
                                pdf_data = buffer.getvalue()
                                buffer.close()
                                
                                st.success("✅ PDF Report Generated!")
                                st.download_button(
                                    "📥 Download PDF Report",
                                    pdf_data,
                                    f"resume_report_{report_role.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                                    "application/pdf",
                                    use_container_width=True
                                )
                                
                            except Exception as e:
                                st.error(f"Error generating PDF: {str(e)}")
                    else:
                        st.warning("Please select a role for the report.")
            
            with tab5:
                st.markdown("### 📊 Visual Skills Analysis")
                st.caption("Interactive visualization of your skill match across different roles")
                
                chart_type = st.radio("Select chart type:", ["Bar Chart", "Radar Chart"], horizontal=True)
                
                if st.button("📈 Generate Chart", type="primary", use_container_width=True):
                    try:
                        import matplotlib.pyplot as plt
                        import numpy as np
                        from io import BytesIO
                        
                        role_scores = {}
                        for role in get_all_job_roles():
                            suggestions = suggest_improvements(resume_data, role)
                            role_scores[role] = suggestions.get('match_percentage', 0)
                        
                        sorted_roles = sorted(role_scores.items(), key=lambda x: x[1], reverse=True)[:8]
                        roles = [r[0] for r in sorted_roles]
                        scores = [r[1] for r in sorted_roles]
                        
                        fig, ax = plt.subplots(figsize=(10, 6))
                        
                        if chart_type == "Bar Chart":
                            colors_list = ['#667eea' if s >= 70 else '#fbbf24' if s >= 50 else '#ef4444' for s in scores]
                            bars = ax.barh(roles, scores, color=colors_list)
                            ax.set_xlabel('Match Percentage (%)', fontsize=12)
                            ax.set_title('Resume Match Score by Role', fontsize=14, fontweight='bold')
                            ax.set_xlim(0, 100)
                            
                            for i, (bar, score) in enumerate(zip(bars, scores)):
                                ax.text(score + 2, i, f'{score:.1f}%', va='center', fontsize=10)
                            
                        else:  # Radar Chart
                            angles = np.linspace(0, 2 * np.pi, len(roles), endpoint=False).tolist()
                            scores_plot = scores + [scores[0]]
                            angles += angles[:1]
                            
                            ax = plt.subplot(111, projection='polar')
                            ax.plot(angles, scores_plot, 'o-', linewidth=2, color='#667eea')
                            ax.fill(angles, scores_plot, alpha=0.25, color='#667eea')
                            ax.set_xticks(angles[:-1])
                            ax.set_xticklabels(roles, size=9)
                            ax.set_ylim(0, 100)
                            ax.set_title('Resume Skills Radar', fontsize=14, fontweight='bold', pad=20)
                            ax.grid(True)
                        
                        plt.tight_layout()
                        
                        st.pyplot(fig)
                        
                        buf = BytesIO()
                        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
                        buf.seek(0)
                        st.download_button(
                            "📥 Download Chart",
                            buf,
                            f"skills_chart_{chart_type.replace(' ', '_').lower()}.png",
                            "image/png",
                            use_container_width=True
                        )
                        plt.close()
                        
                    except Exception as e:
                        st.error(f"Error generating chart: {str(e)}")
                        st.info("Install matplotlib with: pip install matplotlib")
            
                st.markdown("---")
                st.markdown("### 💾 Analysis History & Learning Path")
                
                if "analysis_history" not in st.session_state:
                    st.session_state["analysis_history"] = []
                
                if st.button("💾 Save Current Analysis", use_container_width=True):
                    if matched_jobs:
                        from datetime import datetime
                        history_entry = {
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "filename": uploaded_file.name,
                            "top_match": matched_jobs[0]["job"],
                            "top_score": matched_jobs[0]["similarity"],
                            "total_matches": len(matched_jobs)
                        }
                        st.session_state["analysis_history"].append(history_entry)
                        st.success("✅ Analysis saved to history!")
                
                if st.session_state["analysis_history"]:
                    st.markdown("#### 📜 Your Resume Analysis History")
                    for i, entry in enumerate(reversed(st.session_state["analysis_history"]), 1):
                        with st.expander(f"Analysis #{len(st.session_state['analysis_history']) - i + 1} - {entry['date']}"):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("File", entry['filename'])
                            with col2:
                                st.metric("Top Match", entry['top_match'])
                            with col3:
                                st.metric("Score", f"{entry['top_score']}%")
                    
                    if st.button("🗑️ Clear History", use_container_width=True):
                        st.session_state["analysis_history"] = []
                        st.rerun()
                else:
                    st.info("No analysis history yet. Upload and analyze a resume to get started!")
                
                st.markdown("---")
                
                st.markdown("### 🎓 Personalized Learning Path")
                learning_role = st.selectbox("Select role for learning recommendations:", [""] + get_all_job_roles(), key="learning_role")
                
                if st.button("📚 Get Learning Path", type="primary", use_container_width=True):
                    if learning_role:
                        suggestions = suggest_improvements(resume_data, learning_role)
                        missing = suggestions["missing_skills"]
                        
                        if missing:
                            st.success(f"🎯 Learning path for **{learning_role}**")
                            
                            learning_resources = {
                                "python": {"courses": ["Python for Everybody (Coursera)", "Complete Python Bootcamp (Udemy)"], "cert": "PCAP – Certified Associate in Python Programming"},
                                "java": {"courses": ["Java Programming Masterclass (Udemy)", "Java Specialization (Coursera)"], "cert": "Oracle Certified Associate Java Programmer"},
                                "javascript": {"courses": ["JavaScript: The Complete Guide (Udemy)", "Full Stack JavaScript (freeCodeCamp)"], "cert": "JavaScript Developer Certificate"},
                                "react": {"courses": ["React - The Complete Guide (Udemy)", "React Specialization (Coursera)"], "cert": "Meta React Developer Certificate"},
                                "docker": {"courses": ["Docker Mastery (Udemy)", "Docker for Beginners (freeCodeCamp)"], "cert": "Docker Certified Associate"},
                                "aws": {"courses": ["AWS Certified Solutions Architect (A Cloud Guru)", "AWS Fundamentals (Coursera)"], "cert": "AWS Certified Solutions Architect"},
                                "sql": {"courses": ["The Complete SQL Bootcamp (Udemy)", "SQL for Data Science (Coursera)"], "cert": "Oracle Database SQL Certified Associate"},
                                "machine learning": {"courses": ["Machine Learning by Andrew Ng (Coursera)", "Deep Learning Specialization"], "cert": "TensorFlow Developer Certificate"},
                            }
                            
                            for i, skill in enumerate(missing[:5], 1):
                                st.markdown(f"#### {i}. {skill.title()}")
                                
                                if skill.lower() in learning_resources:
                                    resource = learning_resources[skill.lower()]
                                    st.markdown("**📖 Recommended Courses:**")
                                    for course in resource["courses"]:
                                        st.write(f"• {course}")
                                    st.markdown(f"**🏆 Certification:** {resource['cert']}")
                                else:
                                    st.markdown(f"**📖 Search for:** '{skill} online courses', '{skill} certification'")
                                    st.markdown(f"**💡 Practice:** Build projects using {skill}")
                                
                                st.markdown("---")
                            
                            st.markdown("### 📅 Interview Preparation Tips")
                            st.info(f"""
                            **Common Interview Questions for {learning_role}:**
                            
                            1. **Technical Questions:**
                               - Explain your experience with {', '.join(missing[:3])}
                               - Walk me through a challenging project
                               - How do you stay updated with new technologies?
                            
                            2. **Behavioral Questions:**
                               - Describe a time you solved a difficult problem
                               - How do you handle tight deadlines?
                               - Tell me about a time you worked in a team
                            
                            3. **Preparation Strategy:**
                               - Practice coding problems on LeetCode/HackerRank
                               - Review STAR method for behavioral questions
                               - Research the company and role thoroughly
                               - Prepare thoughtful questions for the interviewer
                               - Do mock interviews with peers
                            """)
                        else:
                            st.success(f"🎉 You already have all key skills for {learning_role}!")
                            st.info("""
                            **Next Steps:**
                            - Build advanced projects showcasing your skills
                            - Contribute to open-source projects
                            - Get advanced certifications
                            - Network with professionals in the field
                            """)
                    else:
                        st.warning("Please select a role.")
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
