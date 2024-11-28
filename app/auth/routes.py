from flask import request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt
from app.models import User
from app.auth import auth


@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    full_name = data.get('full_name')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    location = data.get('location')

    if not all([full_name, email, password, confirm_password, location]):
        return jsonify({'message': 'All fields are required'}), 400

    if password != confirm_password:
        return jsonify({'message': 'Passwords do not match'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already registered'}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(full_name=full_name, email=email, password=hashed_password, location=location)

    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201


@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    location = data.get('location')

    if not all([email, password, location]):
        return jsonify({'message': 'Missing fields'}), 400

    user = User.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password, password):
        if user.location != location:
            return jsonify({'message': 'Invalid location'}), 401

        login_user(user)  # Use Flask-Login to log in the user
        return jsonify({
            'message': 'Logged in successfully',
             'user': {
                'username': user.full_name,
                'location': user.location
                }
            }), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401


@auth.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

@auth.route('/protected', methods=['GET'])
@login_required
def protected():
    return jsonify({'message': f'Hello, {current_user.full_name}. This is a protected route.'}), 200
