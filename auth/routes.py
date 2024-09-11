from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from src.auth_handler import check_password_hash, get_user_credentials, generate_token
from src.models import User
import src.logger as logger
import base64
from src.oauth2_config import oauth, oauth2_required

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

@auth_bp.route('/login/github')
def login_github():
    redirect_uri = url_for('auth.github_callback', _external=True)
    logger.log(f"GitHub OAuth redirect URI: {redirect_uri}")
    return oauth.github.authorize_redirect(redirect_uri)

@auth_bp.route('/login/okta')
def login_okta():
    redirect_uri = url_for('auth.okta_callback', _external=True)
    return oauth.okta.authorize_redirect(redirect_uri)

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

@auth_bp.route('/github/callback')
def github_callback():
    logger.log("GitHub callback reached")
    try:
        token = oauth.github.authorize_access_token()
        #logger.log(f"GitHub OAuth token received: {token}")
        user_info = oauth.github.get('user', token=token).json()
        #logger.log(f"GitHub user info: {user_info}")
        
        user = User.query.filter_by(email=user_info['email']).first()
        if user:
            login_user(user)
            session['oauth_token'] = token
            session['oauth_provider'] = 'github'
            logger.log(f"GitHub login successful for user: {user.username}")
            return redirect(url_for('logpage'))
        else:
            flash('No user found with this email. Please contact your administrator.', 'error')
            logger.log(f"GitHub login failed: No user found for email {user_info['email']}")
            return redirect(url_for('auth.login'))
    except Exception as e:
        logger.log(f"Error in GitHub callback: {str(e)}")
        flash('An error occurred during GitHub authentication.', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/okta/callback')
def okta_callback():
    token = oauth.okta.authorize_access_token()
    user_info = oauth.okta.get('v1/userinfo', token=token).json()
    
    user = User.query.filter_by(email=user_info['email']).first()
    if user:
        login_user(user)
        session['oauth_token'] = token
        session['oauth_provider'] = 'okta'
        logger.log(f"Okta login successful for user: {user.username}")
        return redirect(url_for('logpage'))
    else:
        flash('No user found with this email. Please contact your administrator.', 'error')
        logger.log(f"Okta login failed: No user found for email {user_info['email']}")
        return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('oauth_token', None)
    session.pop('oauth_provider', None)
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