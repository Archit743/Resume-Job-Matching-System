from flask import Flask, jsonify, request
from database.db import init_db, db
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
