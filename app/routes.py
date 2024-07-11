# app/routes.py
import logging
from flask import Blueprint, jsonify, request
from app.models import User, Organisation, db
from flask_jwt_extended import jwt_required, get_jwt_identity

main = Blueprint('main', __name__)

@main.route('/api/users/<id>', methods=['GET'])
@jwt_required()
def get_user(id):
    current_user_id = get_jwt_identity()

    if current_user_id != id:
        return jsonify({"status": "Bad request", "message": "Unauthorized", "statusCode": 401}), 401

    user = User.query.get_or_404(id)
    return jsonify({"status": "success", "message": "User found", "data": {"userId": user.id, "firstName": user.first_name, "lastName": user.last_name, "email": user.email, "phone": user.phone}}), 200

@main.route('/api/organisations', methods=['GET'])
@jwt_required()
def get_organisations():
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)

    organisations = [{"orgId": org.id, "name": org.name, "description": org.description} for org in user.organisations]
    return jsonify({"status": "success", "message": "Organisations found", "data": {"organisations": organisations}}), 200

@main.route('/api/organisations/<org_id>', methods=['GET'])
@jwt_required()
def get_organisation(org_id):
    current_user_id = get_jwt_identity()
    organisation = Organisation.query.get_or_404(org_id)

    if not any(user.id == current_user_id for user in organisation.users):
        return jsonify({"status": "Bad request", "message": "Unauthorized", "statusCode": 401}), 401

    return jsonify({"status": "success", "message": "Organisation found", "data": {"orgId": organisation.id, "name": organisation.name, "description": organisation.description}}), 200

@main.route('/api/organisations', methods=['POST'])
@jwt_required()
def create_organisation():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')

    if not name:
        return jsonify({"status": "Bad Request", "message": "Client error", "statusCode": 400}), 400

    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)

    new_org = Organisation(name=name, description=description, users=[user])
    db.session.add(new_org)
    db.session.commit()

    return jsonify({"status": "success", "message": "Organisation created successfully", "data": {"orgId": new_org.id, "name": new_org.name, "description": new_org.description}}), 201

@main.route('/api/organisations/<org_id>/users', methods=['POST'])
@jwt_required()
def add_user_to_organisation(org_id):
    try:
        data = request.get_json()
        if not data or 'userId' not in data:
            return jsonify({"status": "Bad request", "message": "Missing userId in request", "statusCode": 400}), 400

        user_id = data.get('userId')

        organisation = Organisation.query.get_or_404(org_id)
        user = User.query.get_or_404(user_id)

        # Check if the requesting user is authorized to add users
        if not any(u.id == get_jwt_identity() for u in organisation.users):
            return jsonify({"status": "Unauthorized", "message": "You are not authorized to add users to this organisation", "statusCode": 401}), 401

        # Check if the user is already in the organization
        if any(u.id == user_id for u in organisation.users):
            return jsonify({"status": "Conflict", "message": "User is already in the organisation", "statusCode": 409}), 409

        organisation.users.append(user)
        db.session.commit()

        return jsonify({"status": "success", "message": "User added to organisation successfully"}), 200

    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return jsonify({"status": "Internal Server Error", "message": "An error occurred", "statusCode": 500}), 500

