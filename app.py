# app.py

from flask import render_template, redirect, url_for, request, flash, send_from_directory
from flask_login import login_required, logout_user, login_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import config
from models import KalturaAppToken, AccessRestrictions, User, AppTokenSessionDefaults, \
    UICustomizations, db
from config import login_manager
import logger

@config.connex_app.app.context_processor
def app_globals():
    app_title = UICustomizations.query.get(1)
    if app_title:
        title = app_title.integrator_title
    else:
        title = 'Integration Manager'

    return dict(custom_title=title)

app = config.connex_app
app.add_api(config.basedir / 'apispecs/swagger.yml', swagger_ui_options=config.swagoptions)
#app.add_api(config.basedir / 'apispecs/swagger-dev.yml', swagger_ui_options=config.swagoptions)

@login_manager.user_loader
def user_loader(user_id):
    """Given *user_id*, return the associated User object.

    :param unicode user_id: user_id (email) user to retrieve

    """
    return User.query.get(user_id)

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('addtokens'))
    else:
        return redirect(url_for('login'))

@app.route('/manage')
@login_required
def manage():
    tokens = KalturaAppToken.query.all()
    return render_template("manage.html", tokens=tokens)

@app.route('/log')
@login_required
def logpage():
    b_lines = [row for row in reversed(list(open("logs/log", "r")))]
    return render_template('log.html', b_lines=b_lines)

@app.route('/logs/<path:path>')
@login_required
def send_report(path):
    return send_from_directory('logs', path)

@app.route('/config', methods=('GET', 'POST'))
@login_required
def configpage():
    access_restrictions = AccessRestrictions.query.get(1)
    apptoken_session_defaults = AppTokenSessionDefaults.query.get(1)
    ui_customizations = UICustomizations.query.get(1)
    if request.method == 'GET':
        return render_template('config.html', access_restrictions=access_restrictions, \
                               apptoken_session_defaults=apptoken_session_defaults, \
                                ui_customizations=ui_customizations)
    elif request.method == 'POST':
        
        if request.args.get("f") == "restrictions":
            access_restrictions.allowed_categories = request.form.get('force-cats')
            access_restrictions.force_labels = True if request.form.get('force-labels') else False
            db.session.add(access_restrictions)
            db.session.commit()
            flash('Kaltura Access Restrictions config updated', 'warning')
        elif request.args.get("f") == "sessions":
            apptoken_session_defaults.partner_id = request.form.get('partner-id')
            apptoken_session_defaults.session_expiry = request.form.get('session-expiry')
            apptoken_session_defaults.use_local_storage = True if request.form.get('use-local-storage') else False
            db.session.add(apptoken_session_defaults)
            db.session.commit()
            flash('Session Defaults config updated', 'warning')
        elif request.args.get("f") == "ui":
            ui_customizations.integrator_title = request.form.get('integrator-title')
            db.session.add(ui_customizations)
            db.session.commit()
            flash('UI config updated', 'warning')
        
        return redirect(url_for('configpage'))
    

@app.route('/addtokens')
@login_required
def addtokens():
    return render_template('addtokens.html')

@app.route('/apidocs')
@login_required
def apidocs():
    return render_template('apidocs.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', username=current_user.username)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
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
        return redirect(url_for('login')) # if user doesn't exist or password is wrong, reload the page
    else:
        logger.log("login attempt succeeded for user: " + username)

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('addtokens'))

@app.route('/signup')
@login_required
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
@login_required
def signup_post():
    # code to validate and add user to database goes here
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')

    user = User.query.filter_by(username=username).first() # if this returns a user, then the username already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists', 'warning')
        return redirect(url_for('signup'))
    
    # create a new user with the form data. Hash the password so plaintext version isn't saved.
    new_user = User(username=username, password=generate_password_hash(password, method='pbkdf2'), email=email)

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)