from flask import Blueprint, request, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    from database.models import User, db  # ✅ Move import inside function to avoid circular import

    data = request.get_json()
    name, email, phone, password = data.get("name"), data.get("email"), data.get("phone"), data.get("password")

    if not all([name, email, phone, password]):
        return jsonify({"success": False, "message": "All fields are required!"})

    if User.query.filter((User.email == email) | (User.phone == phone)).first():
        return jsonify({"success": False, "message": "Email or Phone already registered!"})

    try:
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        new_user = User(name=name, email=email, phone=phone, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"success": True, "message": "Signup successful!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "An error occurred."})

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    from database.models import User, db  # ✅ Move import inside function to avoid circular import
    
    data = request.get_json()
    email_or_phone, password = data.get('email_or_phone'), data.get('password')

    user = User.query.filter((User.email == email_or_phone) | (User.phone == email_or_phone)).first()
    if user and check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        return jsonify({"success": True, "message": "Login successful!"})
    
    return jsonify({"success": False, "message": "Invalid credentials."})
