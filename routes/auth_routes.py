from flask import Blueprint, request, jsonify
from config.supabase_config import supabase

auth_bp = Blueprint('auth_routes', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    try:
        response = supabase.auth.sign_up({"email": data['email'], "password": data['password']})
        return jsonify({"message": "User registered", "user_id": response.user.id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@auth_bp.route('/login-password', methods=['POST'])
def login_password():
    data = request.json
    response = supabase.auth.sign_in_with_password({
        "email": data['email'],
        "password": data['password']
    })

    print("SUPABASE RESPONSE:", response)  # 👈 ADD THIS

    return jsonify({
        "token": response.session.access_token,
        "user_id": response.user.id
    }), 200


@auth_bp.route('/login-otp-init', methods=['POST'])
def login_otp_init():
    data = request.json
    try:
        supabase.auth.sign_in_with_otp({"email": data['email']})
        return jsonify({"message": "OTP sent"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@auth_bp.route('/login-otp-verify', methods=['POST'])
def login_otp_verify():
    data = request.json
    try:
        response = supabase.auth.verify_otp({"email": data['email'], "token": data['otp'], "type": "email"})
        return jsonify({"token": response.session.access_token, "user_id": response.user.id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 401

@auth_bp.route('/me', methods=['GET'])
def get_me():
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return jsonify({"error": "Missing Authorization header"}), 401

    try:
        token = auth_header.replace("Bearer ", "")
        res = supabase.auth.get_user(token)

        return jsonify({
            "user_id": res.user.id,
            "email": res.user.email
        }), 200

    except Exception as e:
        return jsonify({"error": "Invalid or expired token"}), 401
