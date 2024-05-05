from flask import Flask, request, redirect, url_for
import requests
from models import CanvasOauthConfig

canvas_base_url = CanvasOauthConfig.query.get(1).canvas_base_url
client_id = CanvasOauthConfig.query.get(1).canvas_client_id
client_secret = CanvasOauthConfig.query.get(1).canvas_client_secret
redirect_uri = CanvasOauthConfig.query.get(1).redirect_uri

# Redirect URI route
@app.route("/oauth2response", methods=["GET"])
def oauth2response():
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
    #access_token = response.json()["access_token"]
    token_payload = response.json()
    return token_payload

@app.route("/refreshtoken", methods=["GET"])
def refreshtoken():
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

if __name__ == "__main__":
    app.run(debug=True)