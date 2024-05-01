from datetime import datetime
from config import app, db
from src.models import Note, KalturaAppToken, User, AccessRestrictions, \
    AppTokenSessionDefaults, UICustomizations, VendorProxies

SAMPLE_TOKENS = [
    {
        "kaltura_token_id": "1_06ukdpod",
        "token": "743659feab72a7b9393bedc0sfcbf156",
        "partnerId": 12312312,
        "createdAt": 1688050262,
        "updatedAt": 1688050262,
        "status": 2,
        "expiry": 1767157200,
        "sessionDuration": 86400,
        "sessionPrivileges": "privacycontext:lceducation",
        "hashType": "SHA256",
        "objectType": "KalturaAppToken",
        "notes": [
            ("Applied a Privacy Context for specific Canvas courses", "2022-03-05 22:18:10"),
        ],
    },
    {
        "kaltura_token_id": "1_38xyqzs6",
        "token": "f047ddf1f144514ec0db9a587a312d8c",
        "partnerId": 4526213,
        "createdAt": 1690220095,
        "updatedAt": 1690220095,
        "status": 2,
        "expiry": 1767157200,
        "sessionUserId": "teacher1@university.edu",
        "sessionDuration": 86400,
        "sessionPrivileges": "enableentitlement,widget:1,urirestrict:/api_v3/service/media/*,/api_v3/service/caption_captionasset/*",
        "hashType": "SHA256",
        "objectType": "KalturaAppToken",
        "label": "ANTH-201-01",
        "notes": [
            ("This token has access limited to media and caption endpoints", "2022-03-05 22:18:10"),
        ],
    },
    {
        "kaltura_token_id": "1_1p5x2pya",
        "token": "0a8c24ddc480a37ed130fda312b47123",
        "partnerId": 12312312,
        "createdAt": 1666634128,
        "updatedAt": 1666634128,
        "status": 2,
        "sessionType": 0,
        "expiry": 1767157200,
        "sessionDuration": 86400,
        "sessionUserId": "teacher@university.edu",
        "sessionPrivileges": "setrole:25448593,editadmintags:*",
        "description": '{"type": "kalturaTESTAppToken", "version": "1.0.0"}',
        "label": "CIS10101-Test",
        "notes": [
            ("This token was created for access to ARTH-101 course videos.", "2022-01-06 17:10:24"),
            ("Updated label", "2022-03-05 22:18:10"),
        ],
    },
]

SAMPLE_USERS = [
    {
        "username": "testadmin",
        "password": "pbkdf2:sha256:600000$KRRW7nkGdZ6CIwU8$fc3c257399bbf4798773d047141344fac52530438a01e279f786d05a15e0bee7",
        "email": "test@college.edu",
        "role": "admin"
    },
    {
        "username": "developer",
        "password": "pbkdf2:sha256:600000$KRRW7nkGdZ6CIwU8$fc3c257399bbf4798773d047141344fac52530438a01e279f786d05a15e0bee7",
        "email": "developer@company.com",
        "role": "developer"
    }
]

SAMPLE_CONFIG = [
    {
        "allowed_categories": "594123,634123"
    }
]

SAMPLE_SESSION_DEFAULTS = [
    {
        "partner_id": 12121212,
        "session_expiry": 86400,
        "use_local_storage": True
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
    proxy_status = VendorProxies(
        kaltura_proxy_enabled=True,
        canvas_proxy_enabled=False
    )
    db.session.add(proxy_status)
    db.session.commit()
