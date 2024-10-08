from KalturaClient import *
from KalturaClient.Plugins.Core import *
from pprint import pprint

import hashlib
import json, requests, src.logger as logger
from src.models import AccessRestrictions, AppTokenSessionDefaults, KalturaAppToken

kaltura_header = {
    "Content-Type": "application/x-www-form-urlencoded",
}
kaltura_service_url = 'https://www.kaltura.com/api_v3/service'

def filter_category(kaltura_tags='', freetext='', ks='', label=''):

    # TODO: Ensure that category restrictions are applied here?
    
    log_info = ''
    tag_filter = ''

    if kaltura_tags:
        log_info = f'Retrieving categories tagged with {kaltura_tags}'
        tag_filter = '&filter[tagsMultiLikeAnd]=' + kaltura_tags 

    if freetext:
        separator = '\n\n' if log_info else ''
        log_info += f'{separator}Retrieving categories containing text {freetext}'
        tag_filter += '&filter[freeText]=' + freetext

    ks = resolve_session(label, ks, log_info)
    
    data = 'ks=' + ks + tag_filter + '&format=1&filter[objectType]=KalturaCategoryFilter'
    response = requests.post(kaltura_service_url + '/category/action/list', headers=kaltura_header, data=data)
    json_response = json.loads(response.text)
    logger.log("Returned category list")
    
    return json_response
    

def get_transcript(entry_id, ks='', label=''):
    
    # Kaltura only returns only XML responses for entry_id/transcript requests
    # JSON is returned only when using an asset id.
    cap_asset_response = get_caption_list(entry_id, ks, label)
    try:
        asset_id = cap_asset_response["objects"][0]["id"]
    except IndexError:
        logger.log('No caption asset found for entry ID: ' + str(entry_id))
        return {"objects": []}
    
    log_info = 'Get caption transcript for entry id: ' + entry_id
    ks = resolve_session(label, ks, log_info)
    
    data = 'ks=' + ks + '&format=1&captionAssetId=' + asset_id
    response = requests.post(kaltura_service_url + '/caption_captionasset/action/serveAsJson', headers=kaltura_header, data=data)
    json_response = json.loads(response.text)
    logger.log('Caption transcript retrieved for entry ID: ' + str(entry_id))
    
    return json_response
    
def get_caption_list(entry_id, ks='', label=''):
    
    log_info = 'Get caption list for entry: ' + entry_id
    ks = resolve_session(label, ks, log_info)
    data = 'ks=' +  ks + '&format=1&filter[entryIdEqual]=' + entry_id
    response = requests.post(kaltura_service_url + '/caption_captionasset/action/list', headers=kaltura_header, data=data)
    json_response = json.loads(response.text)
    logger.log('Caption list retrieved for entry ID: ' + str(entry_id))

    return json_response

def get_category_info(category_id, ks='', label=''):
    
    empty_response = {"objects": []}
    
    if category_allowed(category_id):
        log_info = 'Getting info for a single category: ' + category_id
        ks = resolve_session(label, ks, log_info)
        data = 'ks=' +  ks + '&format=1&id=' + category_id
        response = requests.post(kaltura_service_url + '/category/action/get', headers=kaltura_header, data=data)
        json_response = json.loads(response.text)
    else:
        json_response = empty_response
        logger.log('Attempted to retrieve info by category ID ' + str(category_id) + ' but was not administratively allowed')

    return json_response
   
def get_entries_by_category(category_id='', full_cat_id='', ks='', label=''):

    empty_response = {"objects": []}
    isAllowed = category_allowed(category_id)

    if isAllowed:
        
        if full_cat_id:
            log_info = 'Get entries using full category id: ' + full_cat_id
            ks = resolve_session(label, ks, log_info)
            data = 'ks=' + ks + '&format=1&filter[objectType]=KalturaMediaEntryFilter&filter[categoriesFullNameIn]=' + full_cat_id
            
        elif category_id:
            log_info = 'Get entries from category: ' + category_id
            ks = resolve_session(label, ks, log_info)
            data = 'ks=' + ks + '&format=1&filter[objectType]=KalturaMediaEntryFilter&filter[categoriesIdsMatchAnd]=' + category_id
            
        response = requests.post(
            kaltura_service_url + '/media/action/list', headers=kaltura_header, data=data
        )
        json_response = json.loads(response.text)

    else:
        json_response = empty_response
        logger.log('Attempted to retrieve entries by category ID ' + str(category_id) + ' but was not administratively allowed')

    return json_response

def start_ksession(payload):
    
    # Check if the token exists in the local database
    if not check_token(payload["kaltura_token_id"]):
        return "invalid app token used"
    
    # - pull expiry and partner id from database (stored in configuration tab)
    appTokenSessionDefaults = AppTokenSessionDefaults.query.get(1)
    partner_id = appTokenSessionDefaults.partner_id
    expiry = appTokenSessionDefaults.session_expiry

    kconfig = KalturaConfiguration(partner_id)
    kconfig.serviceUrl = "https://www.kaltura.com/"
    client = KalturaClient(kconfig)

    # example payload
    # {
    #     "partner_id": 4526213,
    #     "kaltura_token_id": "1_391z1o7d",
    #     "token": "8b18249b218808ade2ca2c9c87e01490",
    #     "expiry": 86400,
    #     "session_type": 0,
    #     "session_privileges": "",
    # }

    # destructure payload
    app_token = payload["token"]
    token_id = payload["kaltura_token_id"]

    # For session type to 0. Kaltura admin can override at the time of token creation.
    session_type = 2
    session_privileges = ''

    # Create an unpriviliged KS for use in generating a new app token session
    expiry_uks = 86400
    widget_id = "_" + str(partner_id)
    widget_result = client.session.startWidgetSession(widget_id, expiry_uks)
    client.setKs(widget_result.ks)

    # Create sha256 hash of ks
    hashString = hashlib.sha256(
        widget_result.ks.encode("ascii") + app_token.encode("ascii")
    ).hexdigest()

    result = client.appToken.startSession(
        token_id, hashString, "", session_type, expiry, session_privileges
    )
    ksession = result.ks
    logger.log('Kaltura session (Apptoken KS created) using token ID ' + token_id)
    return ksession

def resolve_session(label, ks, log_info):
    access_restrictions = AccessRestrictions.query.get(1)
    force_labels = access_restrictions.force_labels

    matched_token = find_matching_token(label)
    if not matched_token and label:
        logger.log(f'No token found for label: {label}')
        return handle_denied_access(ks, log_info, force_labels)

    if not matched_token and force_labels:
        logger.log(f'Action denied: {log_info}. Force labels is on.')
        return handle_denied_access('', '', force_labels)

    if matched_token:
        return handle_valid_token(matched_token, log_info, force_labels)

    if log_info:
        logger.log(log_info)
    return ks

def find_matching_token(label):
    for token in KalturaAppToken.query.all():
        if token.label == label:
            logger.log(f'Token found for label: {label}')
            return {'kaltura_token_id': token.kaltura_token_id, 'token': token.token}
    return None

def handle_denied_access(ks, log_info, force_labels):
    if force_labels:
        log_info = ''  # Clear log_info if force_labels is enabled and denied
    if log_info:
        logger.log(log_info)
    return ks if ks else ''

def handle_valid_token(matched_token, log_info, force_labels):
    if log_info:
        logger.log(log_info)
    if not force_labels:
        logger.log('Label used and labels aren\'t being forced')
    logger.log(f'Generating a KS with token id: {matched_token["kaltura_token_id"]}')
    return start_ksession(matched_token)

def check_token(token_id):
    good_token = False
    all_tokens = KalturaAppToken.query.all()
    for token in all_tokens:
        if token.kaltura_token_id == token_id:
            good_token = True
            break
    
    return good_token

def category_allowed(category_id):
    isAllowed = False
    
    # Check against allowed categories list in database
    access_restrictions = AccessRestrictions.query.get(1)
    allowed_categories = access_restrictions.allowed_categories
    
    if allowed_categories == '':
        isAllowed = True
    else:
        allowed_categories_list = [int(x) for x in allowed_categories.split(',')]

        for category in allowed_categories_list:
            if category == int(category_id):
                isAllowed = True
    
    return isAllowed