import pathlib, os
from dotenv import load_dotenv
from datetime import datetime
from connexion import FlaskApp #, json_schema
from connexion.options import SwaggerUIOptions
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager

basedir = pathlib.Path(__file__).parent.resolve()

load_dotenv()
swagoptions = SwaggerUIOptions(
    swagger_ui=True, swagger_ui_template_dir=basedir / "swagger-ui"
)
connex_app = FlaskApp(__name__, specification_dir=basedir / "apispecs")

# Support for CORS front-end development
connex_app.add_middleware(
    CORSMiddleware,
    position=MiddlewarePosition.BEFORE_EXCEPTION,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "api_key", "Authorization"],
    expose_headers=["Access-Control-Allow-Origin"]
)

app = connex_app.app

app.config["DEBUG"] = os.getenv("DEBUG", "True")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{basedir / 'database/epib.db'}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["BOOTSTRAP_BOOTSWATCH_THEME"] = "darkly"
app.config["SECRET_KEY"] = os.getenv(
    "FLASK_SECRET_KEY", "missing_flask_secret_key - check .env"
)
app.config["MESSAGE_FLASHING_OPTIONS"] = {"duration": 5}

@app.template_filter("datetimeformat")
def datetime_format(timestamp):
    realdate = datetime.utcfromtimestamp(timestamp).strftime("%m-%d-%Y %H:%M:%S")
    return realdate

@app.template_filter("secstohours")
def datetime_format(seconds):
    hours = seconds // 3600
    return hours

@app.template_filter("stripwhitespace")
def strip_whitespace(s):
    sclean = s.replace(" ", "")
    print(sclean)
    return sclean

db = SQLAlchemy(app)
ma = Marshmallow(app)
bootstrap = Bootstrap5(app)

login_manager = LoginManager()
login_manager.init_app(app)
