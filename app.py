from flask import Flask
from database.db import init_db, db
from routes.auth import auth_bp
from routes.main import main_bp
from config import Config  # Import the Config class
import pymysql

app = Flask(__name__)

# Load configurations
app.config.from_object(Config)  # Use Config class instead of config module

# Rest of your code remains the same...

# Initialize database
init_db(app)

# Register Blueprints (routes)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(main_bp)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # ✅ Ensures the database is created
    app.run(debug=True)
