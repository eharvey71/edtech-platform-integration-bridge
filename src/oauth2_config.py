from authlib.integrations.flask_client import OAuth
from flask import url_for, redirect, session, request
from functools import wraps

oauth = OAuth()

def init_oauth(app):
    oauth.init_app(app)

    # GitHub OAuth configuration
    oauth.register(
        name='github',
        client_id=app.config['GITHUB_CLIENT_ID'],
        client_secret=app.config['GITHUB_CLIENT_SECRET'],
        access_token_url='https://github.com/login/oauth/access_token',
        access_token_params=None,
        authorize_url='https://github.com/login/oauth/authorize',
        authorize_params=None,
        api_base_url='https://api.github.com/',
        client_kwargs={'scope': 'user:email'},
    )

    # Okta OAuth configuration
    oauth.register(
        name='okta',
        client_id=app.config['OKTA_CLIENT_ID'],
        client_secret=app.config['OKTA_CLIENT_SECRET'],
        server_metadata_url=f'{app.config["OKTA_DOMAIN"]}/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid profile email'
        }
    )

def oauth2_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'oauth_token' not in session:
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def github_token_info(token):
    resp = oauth.github.get('user', token=token)
    resp.raise_for_status()
    return resp.json()

def okta_token_info(token):
    resp = oauth.okta.get('v1/userinfo', token=token)
    resp.raise_for_status()
    return resp.json()

def oauth2_scope_validate(required_scopes, token_scopes, request):
    return set(required_scopes).issubset(set(token_scopes))