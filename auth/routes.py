from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from src.auth_handler import check_password_hash
from src.auth_handler import get_user_credentials, generate_token
from src.models import User
import src.logger as logger
import base64

auth_bp = Blueprint('auth', __name__, template_folder='templates')

@auth_bp.route('/login')
def login():
    return render_template('login.html')

@auth_bp.route('/login', methods=['POST'])
def login_post():

    username = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(username=username).first()

    # check if user actually exists
    # take the user supplied password, hash it, and compare it to the hashed password in database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.', 'warning')
        logger.log("login attempt failed for user: " + username)
        return redirect(url_for('auth.login')) # if user doesn't exist or password is wrong, reload the page
    else:
        logger.log("login attempt succeeded for user: " + username)

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('logpage'))

@auth_bp.route('/json-login', methods=['POST'])
def json_login_post():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
        logger.log("JSON login attempt failed for user: " + username)
        return jsonify({"error": "Invalid credentials"}), 401

    logger.log("JSON login attempt succeeded for user: " + username)
    login_user(user)
    token = generate_token(user.id)

    return jsonify({"token": token})

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

# route for internal authorizations needed by JS
# performing requests. Admin auth is required
# for additional session validation.
@auth_bp.route('/get_auth_token')
@login_required
def get_auth_token():
    username, password = get_user_credentials(username=current_user.username)
    token = base64.b64encode(f"{username}:{password}".encode()).decode('utf-8')
    return jsonify({'token': token})

@auth_bp.route('/token')
@login_required
def token():
    username, password = get_user_credentials(username=current_user.username)
    jwt = generate_token(username)
    return jsonify({'token': jwt})