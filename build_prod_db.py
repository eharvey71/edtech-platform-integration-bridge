# build_database.py

from datetime import datetime
from config import app, db
from models import Note, KalturaAppToken, User, AccessRestrictions, \
    AppTokenSessionDefaults, UICustomizations

SAMPLE_TOKENS = [
    {
        "kaltura_token_id": "1_68dcnqj4",
        "token": "d08a1e56669a1708fac4f70054233236",
        "partner_id": 4526213,
        "createdAt": 1702924341,
        "updatedAt": 1702924341,
        "status": 2,
        "expiry": 1735603200,
        "sessionType": 2,
        "sessionDuration": 86400,
        "hashType": "SHA256",
        "description": "Testing No Restrictons",
        "objectType": "KalturaAppToken",
        "label": "UnrestrictedToken1",
        "notes": [
            ("This token was created for testing with unrestricted access to APIs", "2022-01-06 17:10:24"),
        ]
    }
]

SAMPLE_USERS = [
    {
        "username": "admin",
        "password": "pbkdf2:sha256:600000$7U76bfR0B52uFkSN$5270c986f23025fea3e55e5035da66910de3d71d85c996de87d04a564bed15e7",
        "email": "admin@enwiseweb.com",
        "role": "admin"
    },
    {
        "username": "developer",
        "password": "pbkdf2:sha256:600000$7U76bfR0B52uFkSN$5270c986f23025fea3e55e5035da66910de3d71d85c996de87d04a564bed15e7",
        "email": "developer@company.com",
        "role": "developer"
    }
]

SAMPLE_CONFIG = [
    {
        "allowed_categories": ""
    }
]

SAMPLE_SESSION_DEFAULTS = [
    {
        "partner_id": 4526213,
        "session_expiry": 86400,
        "use_local_storage": False
    }
]

with app.app_context():
    db.drop_all()
    db.create_all()
    for data in SAMPLE_TOKENS:
        new_token = KalturaAppToken(
            kaltura_token_id=data.get("kaltura_token_id"),
            token=data.get("token"),
            partner_id=data.get("partnerId"),
            created_at=data.get("createdAt"),
            updated_at=data.get("updatedAt"),
            status=data.get("status"),
            session_type=data.get("sessionType"),
            expiry=data.get("expiry"),
            session_duration=data.get("sessionDuration"),
            session_user_id=data.get("sessionUserId"),
            session_privileges=data.get("sessionPrivileges"),
            description=data.get("description"),
            label=data.get("label")
        )
        for content, timestamp in data.get("notes", []):
            new_token.notes.append(
                Note(
                    content=content,
                    timestamp=datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S"),
                )
            )
        db.session.add(new_token)
    for user in SAMPLE_USERS:
        new_user = User(
            username=user.get("username"),
            password=user.get("password"),
            email=user.get("email"),
            role=user.get("role")
        )
        db.session.add(new_user)
    new_cat_restrict = AccessRestrictions(
        allowed_categories=SAMPLE_CONFIG[0].get("allowed_categories"),
        force_labels=False
    )
    db.session.add(new_cat_restrict)
    new_app_token_session_defaults = AppTokenSessionDefaults(
        partner_id=SAMPLE_SESSION_DEFAULTS[0].get("partner_id"),
        session_expiry=SAMPLE_SESSION_DEFAULTS[0].get("session_expiry"),
        use_local_storage=False
    )   
    db.session.add(new_app_token_session_defaults)
    new_ui_customizations = UICustomizations(
        integrator_title="EdTech Platform Integration Bridge"
    )
    db.session.add(new_ui_customizations)
    db.session.commit()
