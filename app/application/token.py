from flask import Blueprint, request, render_template, jsonify
from flask import current_app as app
from .models import Admin 
from . import jwt
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_refresh_token_required, set_access_cookies, set_refresh_cookies, get_jwt_identity
import hashlib

# blueprint configuration
token_bp = Blueprint("token_bp", __name__)

@token_bp.route('/token/auth', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        print(f'PASSWORD: {request.form["password"]}')
        # get username and password from database
        user = Admin.query.filter_by(username=request.form['username']).first()
        username = user.username
        password = user.password
        salt = user.salt
        # hash user password
        entered_pass = request.form["password"]
        key = hashlib.pbkdf2_hmac(
            'sha256', # The hash digest algorithm for HMAC
            entered_pass.encode('utf-8'), # Convert the password to bytes
            salt, # Provide the salt
            100000 # It is recommended to use at least 100,000 iterations of SHA-256 
        )
        
        # compare the values
        if request.form['username'] != username or key != password:
            error = f'Invalid Credentials. Please try again.'
        else:
            dictToSend = {
                'username': request.form['username'],
                'password': request.form['password']
            }
            access_token = create_access_token(identity=dictToSend['username'])
            refresh_token = create_refresh_token(
                identity=dictToSend['username'])
            # Set the JWT cookies in the response
            resp = jsonify({'login': True})
            set_access_cookies(resp, access_token)
            set_refresh_cookies(resp, refresh_token)
            return resp, 200
    return render_template('login.html', error=error)


@token_bp.route('/token/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    # Create the new access token
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)

    # Set the JWT access cookie in the response
    resp = jsonify({'refresh': True})
    set_access_cookies(resp, access_token)
    return resp, 200

