import io
from flask import Flask, flash, jsonify, redirect, render_template, request, send_file, url_for
from database.db import init_db, db
from resume_generator_module import ResumeGenerator
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

app.secret_key = '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'

@app.route('/build-resume')
def build_resume():
    return render_template('build_resume.html')

@app.route('/generate-resume', methods=['POST'])
def generate_resume():
    try:
        # Collecting form data
        resume_data = {
            "personal_info": {
                "name": request.form.get('name'),
                "email": request.form.get('email'),
                "phone": request.form.get('phone'),
                "linkedin": request.form.get('linkedin'),
                "location": request.form.get('location')
            },
            "professional_summary": request.form.get('professional_summary'),
            "work_experience": [],
            "education": [],
            "skills": request.form.getlist('skills')
        }

        # Handle work experience (assuming it's sent as multiple entries)
        work_experiences = zip(
            request.form.getlist('company_name'),
            request.form.getlist('position'),
            request.form.getlist('work_dates'),
            request.form.getlist('work_description')
        )
        
        for company, position, dates, description in work_experiences:
            if company and position:  # Only add if essential fields are present
                resume_data["work_experience"].append({
                    "company": company,
                    "position": position,
                    "dates": dates,
                    "description": description
                })

        # Handle education entries
        educations = zip(
            request.form.getlist('institution'),
            request.form.getlist('degree'),
            request.form.getlist('education_dates'),
            request.form.getlist('gpa')
        )
        
        for institution, degree, dates, gpa in educations:
            if institution and degree:  # Only add if essential fields are present
                resume_data["education"].append({
                    "institution": institution,
                    "degree": degree,
                    "dates": dates,
                    "gpa": gpa
                })

        # Validate required fields
        if not resume_data["personal_info"]["name"]:
            flash("Please enter at least your name to generate a resume.", "error")
            return redirect(url_for('build_resume'))

        # Generate PDF
        generator = ResumeGenerator()
        pdf = generator.create_professional_pdf(resume_data)

        # Create a BytesIO object to serve the PDF
        pdf_buffer = io.BytesIO(pdf)
        pdf_buffer.seek(0)

        return send_file(
            pdf_buffer,
            download_name=f"{resume_data['personal_info']['name'].replace(' ', '_')}_professional_resume.pdf",
            mimetype='application/pdf',
            as_attachment=True
        )

    except Exception as e:
        flash(f"Error generating PDF: {str(e)}", "error")
        return redirect(url_for('build_resume'))

@app.route('/upload-resume', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        # Process the uploaded resume
        # Add your resume processing logic here
        return jsonify({'message': 'Resume uploaded successfully'})
    
    return jsonify({'error': 'Invalid file type'}), 400

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



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


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # ✅ Ensures the database is created
    app.run(debug=True)
