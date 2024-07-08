# app/auth.py
from flask import Blueprint, request, jsonify
from app.models import db, User, Organisation
from app.helpers import is_valid_email, is_valid_password
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

auth = Blueprint('auth', __name__)

@auth.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()

    required_fields = ['firstName', 'lastName', 'email', 'password', 'phone']
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        return jsonify({"field": "general", 'message': f'Missing required fields: {", ".join(missing_fields)}'}), 400

    # Validate email format
    if not is_valid_email(data['email']):
        return jsonify({"errors":[{"field": "Invalid email", "message": "Invalid email format"}]}), 400

    # Validate password strength
    if not is_valid_password(data['password']):
        return jsonify({"errors":[{"field": "Invalid password","message": 'Password must be at least 8 characters long and contain a combination of letters, numbers, and special characters'}]}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"errors": [{"field": "email", "message": "Email already in use"}]}), 422

    new_user = User(first_name=data['firstName'], last_name=data['lastName'], email=data['email'], password=data['password'], phone=data['phone'])
    db.session.add(new_user)
    db.session.commit()

    org_name = f"{data['firstName']}'s Organisation"
    new_org = Organisation(name=org_name, users=[new_user])
    db.session.add(new_org)
    db.session.commit()

    access_token = create_access_token(identity=new_user.id)
    return jsonify({"status": "success", "message": "Registration successful", "data": {"accessToken": access_token, "user": {"userId": new_user.id, "firstName": data['firstName'], "lastName": data['lastName'], "email": data['email'], "phone": data['phone']}}}), 201


@auth.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user and user.verify_password(password):
        access_token = create_access_token(identity=user.id)
        return jsonify({"status": "success", "message": "Login successful", "data": {"accessToken": access_token, "user": {"userId": user.id, "firstName": user.first_name, "lastName": user.last_name, "email": user.email, "phone": user.phone}}}), 200

    return jsonify({"status": "Bad request", "message": "Authentication failed", "statusCode": 401}), 401
