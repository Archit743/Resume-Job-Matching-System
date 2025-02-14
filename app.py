import io
from flask import Flask, flash, jsonify, redirect, render_template, request, send_file, url_for
from database.db import init_db, db
from resume_generator_module import ResumeGenerator, resume_generator_module_bp
from routes.auth import auth_bp
from routes.main import main_bp
from config import Config
import os
import spacy
import pdfplumber
import pymysql
from typing import Set, Optional
from datetime import datetime
import pandas as pd
from rapidfuzz import process

class EnhancedResumeAnalyzer:
    def __init__(self):
        try:
            self.nlp_sm = spacy.load("en_core_web_sm")
        except OSError:
            raise OSError("Please install spaCy model using: python -m spacy download en_core_web_sm")
        
        # Define skills list
        self.skills_list = {
            # Programming Languages
            "python", "java", "javascript", "c++", "c#", "ruby", "php",
            # Web Technologies
            "html", "css", "react", "angular", "vue.js", "node.js",
            # Databases
            "sql", "mongodb", "postgresql", "mysql",
            # Tools & Frameworks
            "git", "docker", "kubernetes", "aws", "azure"
        }

    def extract_text(self, pdf_path: str) -> Optional[str]:
        """Extract text from a PDF file."""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                return text.strip()
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return None

    def extract_skills(self, text: str) -> list:
        """Extract skills using NLP and predefined list"""
        if not text:
            return []
            
        doc = self.nlp_sm(text.lower())
        found_skills = set()

        # Extract skills
        for token in doc:
            if token.text in self.skills_list:
                found_skills.add(token.text)
            # Check for compound skills (e.g., "machine learning")
            if token.i + 1 < len(doc):
                bigram = token.text + " " + doc[token.i + 1].text
                if bigram in self.skills_list:
                    found_skills.add(bigram)

        return list(found_skills)

# Initialize Flask app
app = Flask(__name__)

# Initialize ResumeAnalyzer
resume_analyzer = EnhancedResumeAnalyzer()

# Static variable to store file path
uploaded_file_path = None

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load configurations
app.config.from_object(Config)

# Initialize database
init_db(app)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(main_bp)
app.register_blueprint(resume_generator_module_bp)

# Set secret key
app.secret_key = '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'

@app.route('/build-resume')
def build_resume():
    return render_template('build_resume.html')

@app.route('/generate-resume', methods=['POST'])
def generate_resume():
    resume_data = {
        'personal_info': {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'location': request.form.get('location'),
            'linkedin': request.form.get('linkedin')
        },
        'summary': request.form.get('professional_summary'),
        'work_experience': {
            'company_name': request.form.getlist('company_name[]'),
            'position': request.form.getlist('position[]'),
            'work_dates': request.form.getlist('work_dates[]'),
            'work_description': request.form.getlist('work_description[]')
        },
        'education': {
            'institution': request.form.getlist('institution[]'),
            'degree': request.form.getlist('degree[]'),
            'education_dates': request.form.getlist('education_dates[]'),
            'gpa': request.form.getlist('gpa[]')
        },
        'skills': request.form.get('skills', '').split(',')
    }
    
    generator = ResumeGenerator()
    pdf = generator.create_professional_pdf(resume_data)
    
    return send_file(
        io.BytesIO(pdf),
        mimetype='application/pdf',
        as_attachment=True,
        download_name='resume.pdf'
    )

@app.route('/upload', methods=['POST'])
def upload_file():
    global uploaded_file_path
    
    if 'file' not in request.files:
        return jsonify({"message": "No file part", "success": False}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No selected file", "success": False}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    
    uploaded_file_path = file_path
    
    return jsonify({
        "message": f"File '{file.filename}' uploaded successfully!",
        "success": True
    })

@app.route('/results')
def results():
    global uploaded_file_path
    
    if uploaded_file_path:
        # Extract text from the uploaded PDF
        resume_text = resume_analyzer.extract_text(uploaded_file_path)
        if resume_text:
            # Extract skills
            skills_list = resume_analyzer.extract_skills(resume_text)
            return render_template('results.html', skills=skills_list, jobs=[], certifications=[])

    # Handle the case where no file is uploaded
    return render_template('results.html', skills=[], jobs=[], certifications=[])



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)