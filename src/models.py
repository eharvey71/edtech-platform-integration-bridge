from datetime import datetime
from marshmallow_sqlalchemy import fields

from config import db, ma
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    role = db.Column(db.String, nullable=False)

class AccessRestrictions(db.Model):
    __tablename__ = "access_restrictions"
    id = db.Column(db.Integer, primary_key=True)
    allowed_categories = db.Column(db.String, nullable=True, unique=True)
    force_labels = db.Column(db.Boolean, nullable=False)

class AppTokenSessionDefaults(db.Model):
    __tablename__ = "app_token_session_defaults"
    id = db.Column(db.Integer, primary_key=True)
    partner_id = db.Column(db.Integer, nullable=False)
    session_expiry = db.Column(db.Integer, nullable=True)
    use_local_storage = db.Column(db.Boolean, nullable=False)

class UICustomizations(db.Model):
    __tablename__ = "ui_customizations"
    id = db.Column(db.Integer, primary_key=True)
    integrator_title= db.Column(db.String, nullable=False)
    
class VendorProxies(db.Model):
    __tablename__ = "vendor_proxies"
    id = db.Column(db.Integer, primary_key=True)
    kaltura_proxy_enabled = db.Column(db.Boolean, nullable=False)
    canvas_proxy_enabled = db.Column(db.Boolean, nullable=False)
    zoom_proxy_enabled = db.Column(db.Boolean, nullable=False)

class Note(db.Model):
    __tablename__ = "note"
    id = db.Column(db.Integer, primary_key=True)
    kaltura_token_id = db.Column(db.String, db.ForeignKey("kaltura_app_token.kaltura_token_id"))
    content = db.Column(db.String, nullable=False)
    timestamp = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

class NoteSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Note
        load_instance = True
        sqla_session = db.session
        include_fk = True

class KalturaAppToken(db.Model):
    __tablename__ = "kaltura_app_token"
    #id = db.Column(db.Integer, primary_key=True)
    kaltura_token_id = db.Column(db.String(32), primary_key=True)
    token = db.Column(db.String(64), nullable=False)
    partner_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.Integer, nullable=True)
    updated_at = db.Column(db.Integer, nullable=True)
    status = db.Column(db.Integer, nullable=True)
    session_type = db.Column(db.Integer, nullable=True)
    expiry = db.Column(db.Integer, nullable=True)
    session_duration = db.Column(db.Integer, nullable=True)
    session_user_id = db.Column(db.String(128), nullable=True)
    session_privileges = db.Column(db.String(128), nullable=True)
    description = db.Column(db.String(128), nullable=True)
    label = db.Column(db.String(128), nullable=True, unique=True)

    notes = db.relationship(
        Note,
        backref="kaltura_app_token",
        cascade="all, delete, delete-orphan",
        single_parent=True,
        order_by="desc(Note.timestamp)"
    )

class KalturaAppTokenSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = KalturaAppToken
        load_instance = True
        sqla_session = db.session
        include_relationships = True

    notes = fields.Nested(NoteSchema, many=True)
    
class CanvasOauthConfig(db.Model):
    __tablename__ = "canvas_oauth_config"
    id = db.Column(db.Integer, primary_key=True)
    canvas_base_url = db.Column(db.String(128), nullable=False)
    canvas_client_id = db.Column(db.Integer, nullable=False)
    canvas_client_secret = db.Column(db.String(128), nullable=False)
    redirect_uri = db.Column(db.String(128), nullable=False)
    
class ZoomClientConfig(db.Model):
    __tablename__ = "zoom_client_config"
    id = db.Column(db.Integer, primary_key=True)
    zoom_client_id = db.Column(db.String(128), nullable=False)
    zoom_client_secret = db.Column(db.String(128), nullable=False)
    zoom_account_id = db.Column(db.String(128), nullable=False)
    access_key = db.Column(db.String(128), nullable=True)
    require_access_key = db.Column(db.Boolean, default=False, nullable=False)
    
class CanvasAuthorizedUsers(db.Model):
    __tablename__ = "canvas_authorized_users"
    id = db.Column(db.Integer, primary_key=True)
    primary_email = db.Column(db.String(128), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    full_name = db.Column(db.String(128), nullable=True)
    canvas_access_token = db.Column(db.String(128), nullable=False)
    canvas_refresh_token = db.Column(db.String(128), nullable=False)
    canvas_token_expiry = db.Column(db.Integer, nullable=False)

note_schema = NoteSchema()
kapptoken_schema = KalturaAppTokenSchema()
kapptokens_schema = KalturaAppTokenSchema(many=True)