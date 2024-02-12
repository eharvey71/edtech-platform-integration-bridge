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