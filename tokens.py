from flask import abort, make_response
import json
from config import db
from models import KalturaAppToken, kapptoken_schema, kapptokens_schema

def read_all():
    tokens = KalturaAppToken.query.all()
    return kapptokens_schema.dump(tokens)

def read_one(kaltura_token_id):
    token = KalturaAppToken.query.get(kaltura_token_id)
    
    if token is not None:
        return kapptoken_schema.dump(token)
    else:
        abort(
            404, f"Token with ID {kaltura_token_id} not found"
        )

def create_new(token):
    new_token = kapptoken_schema.load(token, session=db.session)
    db.session.add(new_token)
    db.session.commit()
    return kapptoken_schema.dump(new_token), 201

def add_existing(payload):
    # fake a couple of values to make the schema happy
    payload['expiry'] = 0
    payload['session_duration'] = 86400
    new_token = kapptoken_schema.load(payload, session=db.session)
    db.session.add(new_token)
    db.session.commit()
    return kapptoken_schema.dump(new_token), 201

def update_existing(payload):
    # map data if payload is coming from Kaltura directly
    if payload['id'] is not None:
        map_payload = {}
        map_payload['kaltura_token_id'] = payload['id']
        map_payload['token'] = payload['token']
        map_payload['partner_id'] = payload['partnerId']
        map_payload['created_at'] = payload['createdAt']
        map_payload['updated_at'] = payload['updatedAt']
        map_payload['session_duration'] = payload['sessionDuration']
        if 'sessionUserId' in payload:
            map_payload['session_user_id'] = payload['sessionUserId']
        if 'sessionPrivileges' in payload:
            map_payload['session_privileges'] = payload['sessionPrivileges']
        if 'expiry' in payload:
            map_payload['expiry'] = payload['expiry']
        if 'description' in payload:
            map_payload['description'] = payload['description']
        payload = map_payload
        
    kaltura_token_id = payload['kaltura_token_id']
    existing_token = KalturaAppToken.query.get(kaltura_token_id)

    if existing_token:
        kapptoken_schema.loads(json.dumps(payload))
        db.session.commit()
        return kapptoken_schema.dump(existing_token), 201
    else:
        abort(404, f"Token with ID {kaltura_token_id} not found")

def delete(kaltura_token_id):
    existing_token = KalturaAppToken.query.get(kaltura_token_id)

    if existing_token:
        db.session.delete(existing_token)
        db.session.commit()
        return make_response(f"Token with ID {kaltura_token_id} successfully deleted", 200)
    else:
        abort(404, f"Token with ID {kaltura_token_id} not found")
