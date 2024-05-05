from flask import render_template, redirect, url_for, send_from_directory
from flask_login import login_required, current_user
import config
from src.models import User, UICustomizations, VendorProxies
from config import login_manager
from auth.routes import auth_bp
from kaltura.routes import kaltura_bp
from settings.routes import settings_bp
from canvas.routes import canvas_bp

@config.connex_app.app.context_processor
def app_globals():
    app_title = UICustomizations.query.get(1)
    proxies = VendorProxies.query.get(1)
    if app_title:
        title = app_title.integrator_title
    else:
        title = 'Integration Manager'  
    if proxies:
        kaltura_proxy_enabled = proxies.kaltura_proxy_enabled
        canvas_proxy_enabled = proxies.canvas_proxy_enabled
    return dict(custom_title=title,
                kaltura_enabled=kaltura_proxy_enabled,
                canvas_enabled=canvas_proxy_enabled)

app = config.connex_app
app.add_api(config.basedir / 'apispecs/swagger.yml', swagger_ui_options=config.swagoptions)
app.app.register_blueprint(auth_bp, url_prefix='/auth')
app.app.register_blueprint(kaltura_bp, url_prefix='/kaltura')
app.app.register_blueprint(settings_bp, url_prefix='/settings')
app.app.register_blueprint(canvas_bp, url_prefix='/canvas')

@login_manager.user_loader
def user_loader(user_id):
    """Given *user_id*, return the associated User object.
    :param unicode user_id: user_id (email) user to retrieve
    """
    return User.query.get(user_id)

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('logpage'))
    else:
        return redirect(url_for('auth.login'))

@app.route('/log')
@login_required
def logpage():
    b_lines = [row for row in reversed(list(open("logs/log", "r")))]
    return render_template('log.html', b_lines=b_lines)

@app.route('/logs/<path:path>')
@login_required
def send_report(path):
    return send_from_directory('logs', path)

@app.route('/apidocs')
@login_required
def apidocs():
    return render_template('apidocs.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', username=current_user.username, role=current_user.role)
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)