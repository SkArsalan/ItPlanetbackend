from functools import wraps
from flask import request, jsonify
import jwt
from app.models import User
from config import Config

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Retrieve token from the Authorization header
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"error": "Token is missing!"}), 401

        try:
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.get(data["sub"])
            if not current_user:
                return jsonify({"error": "Invalid token!"}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token!"}), 401

        return f(current_user, *args, **kwargs)

    return decorated
