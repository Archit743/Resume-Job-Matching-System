import io
from flask import Flask, flash, jsonify, redirect, render_template, request, send_file, url_for
from database.db import init_db, db
from resume_generator_module import ResumeGenerator, resume_generator_module_bp  # Fixed import

from routes.auth import auth_bp
from routes.main import main_bp
from config import Config  # Import the Config class
import pymysql
import os
app = Flask(__name__)
# Static variable to store file path
uploaded_file_path = None

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# Load configurations
app.config.from_object(Config)  # Use Config class instead of config module

# Rest of your code remains the same...

# Initialize database
init_db(app)

# Register Blueprints (routes)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(main_bp)
app.register_blueprint(resume_generator_module_bp)

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

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    
    uploaded_file_path = file_path  # Store file path in a static variable

    return jsonify({"message": f"File '{file.filename}' uploaded successfully!", "success": True})
@app.route('/results')
def results():
    return render_template('results.html')


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # ✅ Ensures the database is created
    app.run(debug=True)
