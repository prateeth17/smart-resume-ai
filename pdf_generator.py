from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import io
from datetime import datetime

def generate_enhanced_resume(original_text, missing_skills, present_skills, target_role, username):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=0.75*inch, leftMargin=0.75*inch, topMargin=0.75*inch, bottomMargin=0.75*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    title = Paragraph("<b>ENHANCED RESUME</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
    info = Paragraph(f"<b>Target Role:</b> {target_role}<br/><b>Candidate:</b> {username}<br/><b>Date:</b> {datetime.now().strftime('%B %d, %Y')}", styles['Normal'])
    elements.append(info)
    elements.append(Spacer(1, 0.3*inch))
    
    if present_skills:
        heading = Paragraph("<b>Current Skills:</b>", styles['Heading2'])
        elements.append(heading)
        skills_text = ", ".join(present_skills[:20])
        para = Paragraph(skills_text, styles['Normal'])
        elements.append(para)
        elements.append(Spacer(1, 0.2*inch))
    
    if missing_skills:
        heading = Paragraph("<b>Recommended Skills to Add:</b>", styles['Heading2'])
        elements.append(heading)
        skills_text = ", ".join(missing_skills[:20])
        para = Paragraph(skills_text, styles['Normal'])
        elements.append(para)
        elements.append(Spacer(1, 0.2*inch))
    
    summary_heading = Paragraph("<b>Resume Summary:</b>", styles['Heading2'])
    elements.append(summary_heading)
    words = original_text.split()[:200]
    summary = " ".join(words)
    if len(original_text.split()) > 200:
        summary += "..."
    summary_para = Paragraph(summary, styles['Normal'])
    elements.append(summary_para)
    elements.append(Spacer(1, 0.3*inch))
    
    rec_heading = Paragraph("<b>Action Plan:</b>", styles['Heading2'])
    elements.append(rec_heading)
    recommendations = [
        "1. Add the recommended skills to your resume",
        "2. Build projects demonstrating these skills",
        "3. Get relevant certifications",
        "4. Quantify your achievements with numbers",
        "5. Tailor your resume for each application"
    ]
    for rec in recommendations:
        para = Paragraph(rec, styles['Normal'])
        elements.append(para)
    
    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
