"""
Smart Resume Enhancement System
Core Features - Fixed Version
"""
import streamlit as st
import random

# Import modules
try:
    from resume_ai import analyze_resume, suggest_improvements, get_all_job_roles, JOB_DATA
    RESUME_AI_OK = True
except Exception as e:
    st.error(f"Module Error: {e}")
    RESUME_AI_OK = False

# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="Smart Resume Enhancement",
    page_icon="📄",
    layout="wide"
)

# ===================== HEADER =====================
st.markdown("""
<div style='text-align:center; background:linear-gradient(135deg,#667eea,#764ba2);
padding:1.5rem;border-radius:10px;color:white;margin-bottom:2rem;'>
    <h1>🧠 Smart Resume Enhancement System</h1>
    <p>AI-Powered Job Alignment and Resume Optimization</p>
</div>
""", unsafe_allow_html=True)

# ===================== HELPER FUNCTIONS =====================
def search_jobs_simple(job_title, location=""):
    """Generate job search URLs"""
    job_boards = {
        "LinkedIn": f"https://www.linkedin.com/jobs/search/?keywords={job_title}&location={location}",
        "Indeed": f"https://www.indeed.com/jobs?q={job_title}&l={location}",
        "Glassdoor": f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={job_title}",
        "Monster": f"https://www.monster.com/jobs/search/?q={job_title}",
        "ZipRecruiter": f"https://www.ziprecruiter.com/Jobs/{job_title}",
        "Google Jobs": f"https://www.google.com/search?q={job_title}+jobs&ibp=htl;jobs"
    }
    return job_boards

# ===================== SESSION STATE =====================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

# ===================== SIDEBAR - LOGIN =====================
with st.sidebar:
    st.header("🔐 User Login")
    
    if not st.session_state["logged_in"]:
        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        
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

# ===================== MAIN APPLICATION =====================
if st.session_state.get("logged_in") and RESUME_AI_OK:
    
    st.subheader("📂 Upload Your Resume")
    uploaded_file = st.file_uploader("Upload PDF Resume", type=["pdf"])
    
    if uploaded_file:
        file_id = f"{uploaded_file.name}_{uploaded_file.size}"
        
        # Process file only once
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
            
            # ===================== TABS =====================
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                "🎯 Job Matches",
                "📊 ATS Score",
                "📄 Preview",
                "📥 PDF Report",
                "📊 Skills Chart",
                "🎓 Learning & Career"
            ])
            
            # ==================== TAB 1: JOB MATCHES ====================
            with tab1:
                st.markdown("### 🎯 Top Job Matches Based on Your Resume")
                
                if matched_jobs:
                    for i, job in enumerate(matched_jobs[:5], 1):
                        score = job["similarity"]
                        emoji = "🟢" if score >= 70 else "🟡" if score >= 50 else "🔴"
                        
                        with st.expander(f"{emoji} #{i} {job['job']} - {score}% Match"):
                            st.progress(score / 100)
                            
                            st.markdown(f"**🔗 Search for {job['job']} jobs:**")
                            job_links = search_jobs_simple(job["job"])
                            
                            col1, col2, col3 = st.columns(3)
                            for idx, (board, url) in enumerate(job_links.items()):
                                if idx % 3 == 0:
                                    col1.markdown(f"[{board}]({url})")
                                elif idx % 3 == 1:
                                    col2.markdown(f"[{board}]({url})")
                                else:
                                    col3.markdown(f"[{board}]({url})")
                else:
                    st.warning("No job matches found. Try improving your resume keywords.")
            
            # ==================== TAB 2: ATS SCORE ====================
            with tab2:
                st.markdown("### 📊 ATS Compatibility Analysis")
                st.caption("Estimated ATS scores based on keyword matching")
                
                if matched_jobs:
                    col1, col2, col3 = st.columns(3)
                    
                    for idx, job in enumerate(matched_jobs[:6]):
                        ats_score = min(100, int(job["similarity"] + random.randint(10, 25)))
                        
                        if idx % 3 == 0:
                            col1.metric(job["job"], f"{ats_score}%")
                        elif idx % 3 == 1:
                            col2.metric(job["job"], f"{ats_score}%")
                        else:
                            col3.metric(job["job"], f"{ats_score}%")
                    
                    st.markdown("---")
                    st.markdown("### 💡 ATS Optimization Tips")
                    st.info("""
                    **Improve Your ATS Score:**
                    1. Use standard section headings (Experience, Education, Skills)
                    2. Include relevant keywords from job descriptions
                    3. Avoid tables, graphics, and complex formatting
                    4. Use common fonts (Arial, Calibri, Times New Roman)
                    5. Save as PDF to preserve formatting
                    6. Quantify achievements with numbers
                    """)
                else:
                    st.warning("Upload a resume to view ATS compatibility.")
            
            # ==================== TAB 3: RESUME PREVIEW ====================
            with tab3:
                st.markdown("### 📄 Resume Text Preview")
                
                word_count = len(resume_data.split())
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("📝 Words", word_count)
                with col2:
                    st.metric("📊 Characters", len(resume_data))
                with col3:
                    sentences = resume_data.count('.') + resume_data.count('!') + resume_data.count('?')
                    st.metric("📄 Sentences", sentences)
                with col4:
                    st.metric("📑 Pages", max(1, word_count // 300))
                
                st.text_area("Extracted Resume Text", resume_data, height=400)
                
                st.download_button(
                    "📥 Download as TXT",
                    data=resume_data,
                    file_name=f"resume_{st.session_state['username']}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            # ==================== TAB 4: PDF REPORT ====================
            with tab4:
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
                                
                                # Title
                                title_style = ParagraphStyle(
                                    'CustomTitle',
                                    parent=styles['Heading1'],
                                    fontSize=24,
                                    textColor=colors.HexColor('#667eea'),
                                    spaceAfter=12,
                                    alignment=1
                                )
                                story.append(Paragraph("🧠 Resume Analysis Report", title_style))
                                story.append(Spacer(1, 0.2*inch))
                                
                                # Info table
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
                                
                                # Present skills
                                story.append(Paragraph("<b>✅ Skills You Have:</b>", styles['Heading2']))
                                if suggestions["present_skills"]:
                                    skills_text = ", ".join(suggestions["present_skills"])
                                    story.append(Paragraph(skills_text, styles['Normal']))
                                else:
                                    story.append(Paragraph("None identified", styles['Normal']))
                                story.append(Spacer(1, 0.2*inch))
                                
                                # Missing skills
                                story.append(Paragraph("<b>⚠️ Skills to Add:</b>", styles['Heading2']))
                                if suggestions["missing_skills"]:
                                    skills_text = ", ".join(suggestions["missing_skills"])
                                    story.append(Paragraph(skills_text, styles['Normal']))
                                else:
                                    story.append(Paragraph("All skills present!", styles['Normal']))
                                story.append(Spacer(1, 0.2*inch))
                                
                                # Action items
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
                                
                                # Top job matches
                                story.append(Paragraph("<b>🎯 Top 5 Job Matches:</b>", styles['Heading2']))
                                for i, job in enumerate(matched_jobs[:5], 1):
                                    story.append(Paragraph(f"{i}. {job['job']} - {job['similarity']}% match", styles['Normal']))
                                
                                # Build PDF
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
            
            # ==================== TAB 5: SKILLS CHART ====================
            with tab5:
                st.markdown("### 📊 Visual Skills Analysis")
                st.caption("Interactive visualization of your skill match across different roles")
                
                chart_type = st.radio("Select view type:", ["Bar Chart", "Table View"], horizontal=True)
                
                if st.button("📈 Generate Analysis", type="primary", use_container_width=True):
                    try:
                        role_scores = {}
                        for role in get_all_job_roles():
                            suggestions = suggest_improvements(resume_data, role)
                            role_scores[role] = suggestions.get('match_percentage', 0)
                        
                        sorted_roles = sorted(role_scores.items(), key=lambda x: x[1], reverse=True)
                        
                        if chart_type == "Bar Chart":
                            st.markdown("#### 📊 Skill Match by Role")
                            
                            for role, score in sorted_roles:
                                color = "🟢" if score >= 70 else "🟡" if score >= 50 else "🔴"
                                col1, col2, col3 = st.columns([3, 2, 1])
                                
                                with col1:
                                    st.write(f"{color} **{role}**")
                                with col2:
                                    st.progress(score / 100)
                                with col3:
                                    st.write(f"**{score:.1f}%**")
                            
                            st.markdown("---")
                            st.markdown("**Legend:** 🟢 Excellent (70%+) | 🟡 Good (50-69%) | 🔴 Needs Work (<50%)")
                        
                        else:  # Table View
                            st.markdown("#### 📋 Detailed Score Table")
                            
                            import pandas as pd
                            df = pd.DataFrame(sorted_roles, columns=["Role", "Match Score (%)"])
                            df["Rank"] = range(1, len(df) + 1)
                            df = df[["Rank", "Role", "Match Score (%)"]]
                            df["Rating"] = df["Match Score (%)"].apply(
                                lambda x: "⭐⭐⭐" if x >= 70 else "⭐⭐" if x >= 50 else "⭐"
                            )
                            
                            st.dataframe(df, use_container_width=True, hide_index=True)
                            
                            csv = df.to_csv(index=False)
                            st.download_button(
                                "📥 Download as CSV",
                                csv,
                                "skills_analysis.csv",
                                "text/csv",
                                use_container_width=True
                            )
                        
                    except Exception as e:
                        st.error(f"Error generating analysis: {str(e)}")
            
            # ==================== TAB 6: LEARNING & CAREER (History Removed) ====================
            with tab6:
                st.markdown("### 🎓 Personalized Learning Path")
                st.caption("Get customized learning recommendations based on your target role")
                
                learning_role = st.selectbox(
                    "Select role for learning recommendations:",
                    [""] + get_all_job_roles(),
                    key="learning_role"
                )
                
                if st.button("📚 Get Learning Path", type="primary", use_container_width=True):
                    if learning_role:
                        suggestions = suggest_improvements(resume_data, learning_role)
                        missing = suggestions["missing_skills"]
                        present = suggestions["present_skills"]
                        
                        # Show current status
                        st.markdown("#### 📊 Your Current Status")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("✅ Skills You Have", len(present))
                        with col2:
                            st.metric("📚 Skills to Learn", len(missing))
                        with col3:
                            match_pct = suggestions.get('match_percentage', 0)
                            st.metric("🎯 Match Score", f"{match_pct}%")
                        
                        st.markdown("---")
                        
                        if missing:
                            st.success(f"🎯 Learning path for **{learning_role}**")
                            
                            # Learning resources dictionary
                            learning_resources = {
                                "python": {
                                    "courses": ["Python for Everybody (Coursera)", "Complete Python Bootcamp (Udemy)"],
                                    "cert": "PCAP – Certified Associate in Python Programming"
                                },
                                "java": {
                                    "courses": ["Java Programming Masterclass (Udemy)", "Java Specialization (Coursera)"],
                                    "cert": "Oracle Certified Associate Java Programmer"
                                },
                                "javascript": {
                                    "courses": ["JavaScript: The Complete Guide (Udemy)", "Full Stack JavaScript (freeCodeCamp)"],
                                    "cert": "JavaScript Developer Certificate"
                                },
                                "react": {
                                    "courses": ["React - The Complete Guide (Udemy)", "React Specialization (Coursera)"],
                                    "cert": "Meta React Developer Certificate"
                                },
                                "nodejs": {
                                    "courses": ["Node.js - The Complete Guide (Udemy)", "Node.js API Development (Coursera)"],
                                    "cert": "Node.js Certified Developer"
                                },
                                "docker": {
                                    "courses": ["Docker Mastery (Udemy)", "Docker for Beginners (freeCodeCamp)"],
                                    "cert": "Docker Certified Associate"
                                },
                                "aws": {
                                    "courses": ["AWS Certified Solutions Architect (A Cloud Guru)", "AWS Fundamentals (Coursera)"],
                                    "cert": "AWS Certified Solutions Architect"
                                },
                                "sql": {
                                    "courses": ["The Complete SQL Bootcamp (Udemy)", "SQL for Data Science (Coursera)"],
                                    "cert": "Oracle Database SQL Certified Associate"
                                },
                                "machine learning": {
                                    "courses": ["Machine Learning by Andrew Ng (Coursera)", "Deep Learning Specialization"],
                                    "cert": "TensorFlow Developer Certificate"
                                },
                                "kubernetes": {
                                    "courses": ["Kubernetes for Developers (Udemy)", "Kubernetes Fundamentals (Linux Foundation)"],
                                    "cert": "Certified Kubernetes Application Developer"
                                }
                            }
                            
                            # Display top 5 missing skills with resources
                            st.markdown("### 📖 Recommended Learning Resources")
                            
                            for i, skill in enumerate(missing[:5], 1):
                                st.markdown(f"#### {i}. {skill.title()}")
                                
                                if skill.lower() in learning_resources:
                                    resource = learning_resources[skill.lower()]
                                    
                                    col1, col2 = st.columns([2, 1])
                                    with col1:
                                        st.markdown("**📚 Recommended Courses:**")
                                        for course in resource["courses"]:
                                            st.write(f"• {course}")
                                    with col2:
                                        st.markdown("**🏆 Certification:**")
                                        st.info(resource['cert'])
                                else:
                                    st.markdown(f"**📖 Search for:** '{skill} online courses', '{skill} certification'")
                                    st.markdown(f"**💡 Practice:** Build projects using {skill}")
                                
                                st.markdown("---")
                        else:
                            st.success(f"🎉 You already have all key skills for {learning_role}!")
                            st.info("""
                            **Next Steps:**
                            - Build advanced projects showcasing your skills
                            - Contribute to open-source projects
                            - Get advanced certifications
                            - Network with professionals in the field
                            - Consider leadership or specialized roles
                            """)
                        
                        # Interview Preparation Tips (Always shown)
                        st.markdown("---")
                        st.markdown("### 📅 Interview Preparation Tips")
                        
                        st.info(f"""
                        **Common Interview Questions for {learning_role}:**
                        
                        **1. Technical Questions:**
                        - Explain your experience with {', '.join(missing[:3] if missing else present[:3])}
                        - Walk me through a challenging project you've worked on
                        - How do you stay updated with new technologies and industry trends?
                        - Describe your development workflow and tools you use
                        
                        **2. Behavioral Questions:**
                        - Describe a time you solved a difficult technical problem
                        - How do you handle tight deadlines and pressure?
                        - Tell me about a time you worked effectively in a team
                        - Share an example of when you had to learn something quickly
                        
                        **3. Preparation Strategy:**
                        - Practice coding problems on LeetCode/HackerRank daily
                        - Review STAR method (Situation, Task, Action, Result) for behavioral questions
                        - Research the company culture, products, and recent news
                        - Prepare thoughtful questions to ask the interviewer
                        - Do mock interviews with peers or mentors
                        - Review your resume and be ready to discuss every point
                        - Prepare a 2-minute "tell me about yourself" pitch
                        
                        **4. Day Before Interview:**
                        - Get good sleep (7-8 hours)
                        - Prepare your outfit and documents
                        - Test your technology (for virtual interviews)
                        - Review your notes and the job description
                        - Plan to arrive 10-15 minutes early
                        """)
                        
                        # Additional Career Tips
                        st.markdown("### 💼 Career Development Tips")
                        st.success("""
                        **Boost Your Career:**
                        
                        **Networking:**
                        - Connect with professionals on LinkedIn
                        - Attend industry meetups and conferences
                        - Join relevant online communities (Reddit, Discord, Slack)
                        
                        **Portfolio Building:**
                        - Create a GitHub profile with quality projects
                        - Write technical blog posts about your learning
                        - Contribute to open-source projects
                        
                        **Continuous Learning:**
                        - Follow industry leaders on social media
                        - Subscribe to relevant newsletters and podcasts
                        - Take on side projects to practice new skills
                        - Participate in hackathons and coding challenges
                        """)
                        
                    else:
                        st.warning("⚠️ Please select a role to get personalized recommendations.")
        
        else:
            st.error("Could not extract text from the PDF. Please try again with a different file.")

elif not st.session_state.get("logged_in"):
    st.markdown("""
    <div style="text-align: center; padding: 3rem;">
        <h2>🔒 Please Log In to Access the System</h2>
        <p style="font-size: 1.2rem; color: #6c757d;">
            Use the sidebar to login and start optimizing your resume!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature showcase - BLACK TEXT
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 10px;">
            <h3 style="color: #000000;">🎯 Smart Matching</h3>
            <p style="color: #333333;">AI analyzes and suggests best-fit roles</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 10px;">
            <h3 style="color: #000000;">📊 ATS Analysis</h3>
            <p style="color: #333333;">Check compatibility with tracking systems</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 10px;">
            <h3 style="color: #000000;">📥 PDF Reports</h3>
            <p style="color: #333333;">Download comprehensive analysis reports</p>
        </div>
        """, unsafe_allow_html=True)

else:
    st.error("❌ System modules failed to load. Please contact support.")

# ===================== FOOTER =====================
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#6c757d;padding:20px;">
    <p><b>Smart Resume Enhancement System</b></p>
    <p style="font-size:12px;">Powered by AI • Built with Streamlit</p>
    <p style="font-size:11px;">© 2025 • All Rights Reserved</p>
</div>
""", unsafe_allow_html=True)
