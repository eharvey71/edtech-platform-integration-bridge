from werkzeug.security import check_password_hash
import logger
from models import User
import config

def swag_auth(username, password):
    with config.connex_app.app.app_context():
        user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        logger.log("Swagger UI Auth attempt failed for user: " + username)
    else:
        logger.log("Swagger UI Auth succeeded for user: " + username)
        return {"sub": username}
    # optional: raise exception for custom error response
    return None

def get_user_credentials(username):
    with config.connex_app.app.app_context():
        user = User.query.filter_by(username=username).first()
    if user:
        return user.username, user.password
    else:
        return None, None

####
# To Do:
####
# Implement API Key Auth in swagger/openapi as a second option
# for accessing internal APIs.
# Store hashed in DB and allow to be changed in the Integration Bridge UI.
####