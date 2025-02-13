import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os

class ResumeGenerator:
    def _init_(self):
        self.model = ChatGroq(model="llama3-groq-70b-8192-tool-use-preview", 
                            api_key="{{ $API_KEY }}")
        self.parser = StrOutputParser()
        self.styles = self._create_styles()
    
    def _create_styles(self):
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name='NameStyle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=20,
            alignment=TA_CENTER
        ))
        styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1a237e'),
            spaceBefore=15,
            spaceAfter=10,
            borderColor=colors.HexColor('#1a237e'),
            borderWidth=1,
            borderPadding=5,
            borderRadius=3
        ))
        styles.add(ParagraphStyle(
            name='ContactInfo',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            spaceAfter=20
        ))
        return styles
    
    def enhance_bullet_points(self, text, role):
        prompt = ChatPromptTemplate.from_template(
            """Enhance the following bullet point for a {role} position to be more impactful and professional, 
            focusing on achievements and quantifiable results where possible:
            {text}
            
            Return only the enhanced bullet point with no additional text or formatting."""
        )
        chain = prompt | self.model | self.parser
        try:
            return chain.invoke({"role": role, "text": text}).strip()
        except Exception as e:
            print(f"Error enhancing bullet point: {str(e)}")
            return text
    
    def create_professional_pdf(self, resume_data):
        print("Received work experience data:", resume_data.get("work_experience", "No data found"))

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        elements = []
        
        # Header section
        elements.append(Paragraph(resume_data['personal_info']['name'], self.styles['NameStyle']))
        
        # Contact info
        contact_info = [
            resume_data['personal_info']['email'],
            resume_data['personal_info']['phone'],
            resume_data['personal_info']['location'],
            resume_data['personal_info'].get('linkedin', '')
        ]
        elements.append(Paragraph(' | '.join(filter(None, contact_info)), self.styles['ContactInfo']))
        
        # Enhanced summary
        elements.extend(self._create_summary_section(resume_data.get('summary', '')))
        
        # Experience Section
        elements.extend(self._create_experience_section(resume_data['work_experience']))
        
        # Education Section
        elements.extend(self._create_education_section(resume_data['education']))
        
        # Skills Section
        elements.extend(self._create_skills_section(resume_data['skills']))
        
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        return pdf
    
    def _create_summary_section(self, summary):
        elements = []
        summary_prompt = ChatPromptTemplate.from_template(
            """Enhance the following professional summary to be more impactful and compelling:
            {summary}
            
            Return only the enhanced summary with no additional text."""
        )
        summary_chain = summary_prompt | self.model | self.parser
        try:
            enhanced_summary = summary_chain.invoke({"summary": summary})
            elements.append(Paragraph('Professional Summary', self.styles['SectionHeading']))
            elements.append(Paragraph(enhanced_summary, self.styles['Normal']))
        except Exception as e:
            print(f"Error enhancing summary: {str(e)}")
            elements.append(Paragraph('Professional Summary', self.styles['SectionHeading']))
            elements.append(Paragraph(summary, self.styles['Normal']))
        return elements
    
    def _create_experience_section(self, experiences):
        elements = []
        elements.append(Paragraph('Professional Experience', self.styles['SectionHeading']))
        for exp in experiences:
            exp_table_data = [
                [Paragraph(f"<b>{exp['title']}</b>", self.styles['Normal']),
                 Paragraph(f"{exp['start_date']} - {exp['end_date']}", self.styles['Normal'])],
                [Paragraph(f"{exp['company']}, {exp['location']}", self.styles['Normal']), '']
            ]
            exp_table = Table(exp_table_data, colWidths=[4*inch, 2*inch])
            exp_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(exp_table)
            
            responsibilities = exp['responsibilities'].split('\n')
            bullets = []
            for resp in responsibilities:
                if resp.strip():
                    enhanced_resp = self.enhance_bullet_points(resp.strip(), exp['title'])
                    bullets.append(ListItem(Paragraph(enhanced_resp, self.styles['Normal'])))
            elements.append(ListFlowable(bullets, bulletType='bullet', leftIndent=20))
            elements.append(Spacer(1, 10))
        return elements
    
    def _create_education_section(self, education):
        elements = []
        elements.append(Paragraph('Education', self.styles['SectionHeading']))
        for edu in education:
            edu_table_data = [
                [Paragraph(f"<b>{edu['degree']}</b>", self.styles['Normal']),
                 Paragraph(edu['graduation_date'], self.styles['Normal'])],
                [Paragraph(f"{edu['school']}, {edu['location']}", self.styles['Normal']),
                 Paragraph(f"GPA: {edu['gpa']}" if edu['gpa'] else "", self.styles['Normal'])]
            ]
            edu_table = Table(edu_table_data, colWidths=[4*inch, 2*inch])
            edu_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(edu_table)
            elements.append(Spacer(1, 10))
        return elements
    
    def _create_skills_section(self, skills):
        elements = []
        skills_prompt = ChatPromptTemplate.from_template(
            """Organize and enhance the following skills into a professional, well-structured format:
            {skills}
            
            Return the skills as a bullet-pointed list, grouped by category."""
        )
        skills_chain = skills_prompt | self.model | self.parser
        try:
            enhanced_skills = skills_chain.invoke({"skills": "\n".join(skills)})
            elements.append(Paragraph('Technical Skills', self.styles['SectionHeading']))
            elements.append(Paragraph(enhanced_skills, self.styles['Normal']))
        except Exception as e:
            print(f"Error enhancing skills: {str(e)}")
            elements.append(Paragraph('Technical Skills', self.styles['SectionHeading']))
            skills_text = " • ".join(skills)
            elements.append(Paragraph(skills_text, self.styles['Normal']))
        return elements