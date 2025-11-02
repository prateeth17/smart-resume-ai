"""
PDF Resume Generator with Skill Recommendations
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib import colors
import io
from datetime import datetime

def generate_enhanced_resume(original_text, missing_skills, present_skills, target_role, username):
    """
    Generate an enhanced resume PDF with skill recommendations
    
    Args:
        original_text (str): Original resume text
        missing_skills (list): Skills to add
        present_skills (list): Skills already present
        target_role (str): Target job role
        username (str): User's name
    
    Returns:
        bytes: PDF file as bytes
    """
    # Create BytesIO buffer for PDF
    buffer = io.BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Container for flowable objects
    elements = []
    
    # Get default styles
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph("<b>ENHANCED RESUME REPORT</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
    # Subtitle
    subtitle = Paragraph(f"<i>Optimized for: {target_role}</i>", styles['Normal'])
    elements.append(subtitle)
    elements.append(Spacer(1, 0.2*inch))
    
    # User information
    info_text = f"""
    <b>Candidate:</b> {username}<br/>
    <b>Date Generated:</b> {datetime.now().strftime('%B %d, %Y')}<br/>
    <b>Target Role:</b> {target_role}
    """
    info = Paragraph(info_text, styles['Normal'])
    elements.append(info)
    elements.append(Spacer(1, 0.3*inch))
    
    # Current Skills Section
    if present_skills:
        heading = Paragraph("<b>✓ CURRENT SKILLS</b>", styles['Heading2'])
        elements.append(heading)
        
        skills_text = ", ".join(present_skills[:25])
        para = Paragraph(skills_text, styles['Normal'])
        elements.append(para)
        elements.append(Spacer(1, 0.2*inch))
    
    # Recommended Skills Section
    if missing_skills:
        heading = Paragraph("<b>+ RECOMMENDED SKILLS TO ADD</b>", styles['Heading2'])
        elements.append(heading)
        
        rec_text = Paragraph("<i>(Adding these will strengthen your profile)</i>", styles['Normal'])
        elements.append(rec_text)
        elements.append(Spacer(1, 0.1*inch))
        
        # Limit to top 25 missing skills
        top_missing = missing_skills[:25]
        skills_text = ", ".join(top_missing)
        para = Paragraph(skills_text, styles['Normal'])
        elements.append(para)
        
        if len(missing_skills) > 25:
            more_text = Paragraph(f"<i>...and {len(missing_skills) - 25} more</i>", styles['Normal'])
            elements.append(more_text)
        
        elements.append(Spacer(1, 0.2*inch))
    
    # Resume Summary Section
    summary_heading = Paragraph("<b>RESUME SUMMARY</b>", styles['Heading2'])
    elements.append(summary_heading)
    
    # Extract first 200 words as summary
    words = original_text.split()[:200]
    summary = " ".join(words)
    if len(original_text.split()) > 200:
        summary += "..."
    
    summary_para = Paragraph(summary, styles['Normal'])
    elements.append(summary_para)
    elements.append(Spacer(1, 0.3*inch))
    
    # Action Plan Section
    rec_heading = Paragraph("<b>ENHANCEMENT ACTION PLAN</b>", styles['Heading2'])
    elements.append(rec_heading)
    
    recommendations = [
        "<b>1. Skill Development:</b> Focus on adding the recommended skills through online courses, certifications, or hands-on projects.",
        f"<b>2. Project Portfolio:</b> Build 2-3 projects demonstrating {target_role} expertise using the recommended technologies.",
        "<b>3. Quantify Achievements:</b> Add metrics and numbers to your experience (e.g., 'Increased efficiency by 40%').",
        "<b>4. Certifications:</b> Consider relevant certifications for missing skills to strengthen your credentials.",
        "<b>5. Tailor Resume:</b> Customize your resume for each application, emphasizing relevant skills and experience.",
        "<b>6. Keywords:</b> Use industry-standard terminology and keywords from job descriptions.",
        "<b>7. ATS Optimization:</b> Ensure your resume uses standard formatting with clear headers and bullet points."
    ]
    
    for rec in recommendations:
        para = Paragraph(rec, styles['Normal'])
        elements.append(para)
        elements.append(Spacer(1, 0.05*inch))
    
    elements.append(Spacer(1, 0.2*inch))
    
    # Next Steps
    next_heading = Paragraph("<b>NEXT STEPS</b>", styles['Heading2'])
    elements.append(next_heading)
    
    next_steps = f"""
    <b>Immediate Actions:</b><br/>
    • Review the recommended skills and prioritize which to learn first<br/>
    • Update your LinkedIn profile with current skills<br/>
    • Start a GitHub portfolio project using target technologies<br/>
    • Network with professionals in the {target_role} field<br/>
    • Apply to positions that match your current skill level
    """
    next_para = Paragraph(next_steps, styles['Normal'])
    elements.append(next_para)
    elements.append(Spacer(1, 0.2*inch))
    
    # Footer
    footer_text = f"""
    <i>This enhanced resume report was generated using AI-powered analysis to optimize your profile for 
    the role: <b>{target_role}</b>. The recommendations are based on skill gap analysis, industry 
    standards, and current job market requirements. Generated on {datetime.now().strftime('%B %d, %Y')} 
    by the Smart Resume Enhancement System.</i>
    """
    footer = Paragraph(footer_text, styles['Normal'])
    elements.append(footer)
    
    # Build the PDF
    try:
        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
    except Exception as e:
        print(f"Error generating PDF: {e}")
        buffer.close()
        raise
