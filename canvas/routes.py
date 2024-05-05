from flask import Blueprint, request, render_template, redirect, url_for, flash, session, jsonify
from flask_login import login_required
from src.models import VendorProxies, CanvasOauthConfig, CanvasAuthorizedUsers, db
import requests, os

canvas_bp = Blueprint('canvas', __name__, template_folder='templates')

@canvas_bp.route('/config', methods=('GET', 'POST'))
@login_required
def canvas_config():
    if VendorProxies.query.get(1).canvas_proxy_enabled == False:
        return redirect(url_for('settings.main_config'))
    
    oauth_config = CanvasOauthConfig.query.get(1)
    authorized_users = CanvasAuthorizedUsers.query.all()
    
    if request.method == 'GET':
        # Generate a dynamic URL where the user can click a button to authorize the application
        # This URL will redirect to the redirect URI with the code parameter
        # Generate a unique state value for CSRF protection
        state = os.urandom(24).hex()
        session['state'] = state
                
        auth_url = (
            f"{oauth_config.canvas_base_url}/login/oauth2/auth"
            f"?client_id={oauth_config.canvas_client_id}"
            f"&response_type=code"
            f"&state={state}"
            f"&redirect_uri={oauth_config.redirect_uri}"
        )

        return render_template('canvas-test.html', 
                               oauth_config=oauth_config, \
                               auth_url=auth_url, \
                               authorized_users=authorized_users)
        
    elif request.method == 'POST':
        
        if request.args.get("f") == "oauth_config":
            oauth_config.canvas_base_url = request.form.get('canvas-base-url')
            oauth_config.canvas_client_id = request.form.get('canvas-client-id')
            oauth_config.canvas_client_secret = request.form.get('canvas-client-secret')
            oauth_config.redirect_uri = request.form.get('redirect-uri')
            db.session.add(oauth_config)
            db.session.commit()
            flash('Canvas OAuth config updated', 'warning')
        
        return redirect(url_for('canvas.canvas_config'))

# Redirect URI route
@canvas_bp.route("/oauth2response", methods=["GET"])
def oauth2response():
    
    canvas_base_url = CanvasOauthConfig.query.get(1).canvas_base_url
    client_id = CanvasOauthConfig.query.get(1).canvas_client_id
    client_secret = CanvasOauthConfig.query.get(1).canvas_client_secret
    redirect_uri = CanvasOauthConfig.query.get(1).redirect_uri
    code = request.args.get("code")
    
    # Exchange the code for an access token
    token_url = f"{canvas_base_url}/login/oauth2/token"
    response = requests.post(
        token_url,
        data={
            "grant_type": "authorization_code",
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "code": code,
        },
    )
    
    # store reponse for authorized user in the database
    if response.status_code == 200:  
        
        user_id = response.json().get("user", {}).get("id")
        full_name = response.json().get("user", {}).get("name")
        
        # Check if user is already authorized
        existing_user = CanvasAuthorizedUsers.query.filter_by(user_id=user_id).first()
        if existing_user:
            # User already authorized, return a message
            return jsonify({
                "message": "User already authorized.",
                "user_id": user_id,
                "name": full_name
            }), 200
        
        access_token = response.json()["access_token"]
        refresh_token = response.json()["refresh_token"]
        expiry = response.json()["expires_in"]
        #user_id = response.json()["user"]["id"]
        #full_name = response.json()["user"]["name"]
    
        authorized_user = CanvasAuthorizedUsers(
            primary_email='email_not_stored',
            user_id=user_id,   
            full_name=full_name,
            canvas_access_token=access_token,
            canvas_refresh_token=refresh_token,
            canvas_token_expiry=expiry
        )
        db.session.add(authorized_user)
        db.session.commit()

        token_payload = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expiry": expiry,
            "user_id": user_id,
            "name": full_name
        }
        return token_payload
    else:
        return {"error": "Failed to retrieve tokens"}, 400
         

@canvas_bp.route("/refreshtoken", methods=["GET"])
def refreshtoken():
    
    canvas_base_url = CanvasOauthConfig.query.get(1).canvas_base_url
    client_id = CanvasOauthConfig.query.get(1).canvas_client_id
    client_secret = CanvasOauthConfig.query.get(1).canvas_client_secret
    refresh_token = request.args.get("refresh_token")
    
    # Exchange the code for an access token
    token_url = f"{canvas_base_url}/login/oauth2/token"
    response = requests.post(
        token_url,
        data={
            "grant_type": "refresh_token",
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
        },
    )
    #access_token = response.json()["access_token"]
    token_payload = response.json()
    return token_payload