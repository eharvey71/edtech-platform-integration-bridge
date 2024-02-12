# config.py

import pathlib
from datetime import datetime
from connexion import FlaskApp
from connexion.options import SwaggerUIOptions
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
#from models import UICustomizations

basedir = pathlib.Path(__file__).parent.resolve()
swagoptions = SwaggerUIOptions(swagger_ui = True, swagger_ui_template_dir = basedir / 'swagger-ui')
connex_app = FlaskApp(__name__, specification_dir=basedir)

app = connex_app.app

app.config['DEBUG'] = True
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{basedir / 'lc.db'}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['BOOTSTRAP_BOOTSWATCH_THEME'] = 'darkly'
app.config['SECRET_KEY'] = '3d329dj239d0j2390df023f320f32d9023nd3290d230'
app.config['MESSAGE_FLASHING_OPTIONS'] = {'duration': 5}

@app.template_filter('datetimeformat')
def datetime_format(timestamp):
    realdate = datetime.utcfromtimestamp(timestamp).strftime('%m-%d-%Y %H:%M:%S')
    return realdate

@app.template_filter('secstohours')
def datetime_format(seconds):
    hours = seconds // 3600
    return hours

@app.template_filter('stripwhitespace')
def strip_whitespace(s):
    sclean = s.replace(" ", "")
    return sclean

db = SQLAlchemy(app)
ma = Marshmallow(app)
bootstrap = Bootstrap5(app)

login_manager = LoginManager()
login_manager.init_app(app)
