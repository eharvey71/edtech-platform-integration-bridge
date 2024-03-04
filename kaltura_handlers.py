from KalturaClient import *
from KalturaClient.Plugins.Core import *
from pprint import pprint

import hashlib
import json, requests, logger
from models import AccessRestrictions, AppTokenSessionDefaults, KalturaAppToken

kaltura_header = {
    "Content-Type": "application/x-www-form-urlencoded",
}
kaltura_service_url = 'https://www.kaltura.com/api_v3/service'

def get_transcript(entry_id, ks='', label=''):
    
    # Kaltura only returns only XML responses for entry_id/transcript requests
    # JSON is returned only when using an asset id.
    cap_asset_response = get_caption_list(entry_id, ks, label)
    asset_id = cap_asset_response["objects"][0]["id"]
    
    log_info = 'Get caption transcript for entry id: ' + entry_id
    ks = resolveLabels(label, ks, log_info)
    
    data = 'ks=' + ks + '&format=1&captionAssetId=' + asset_id
    response = requests.post(kaltura_service_url + '/caption_captionasset/action/serveAsJson', headers=kaltura_header, data=data)
    json_response = json.loads(response.text)
    logger.log('Caption transcript retrieved for entry ID: ' + str(entry_id))
    
    return json_response
    
def get_caption_list(entry_id, ks='', label=''):
    
    log_info = 'Get caption list for entry: ' + entry_id
    ks = resolveLabels(label, ks, log_info)
    data = 'ks=' +  ks + '&format=1&filter[entryIdEqual]=' + entry_id
    response = requests.post(kaltura_service_url + '/caption_captionasset/action/list', headers=kaltura_header, data=data)
    json_response = json.loads(response.text)
    logger.log('Caption list retrieved for entry ID: ' + str(entry_id))

    return json_response
   
def get_entries_by_category(category_id, ks='', label=''):

    isAllowed = False
    empty_response = {"objects": []}

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

    if isAllowed:
        log_info = 'Get entries from category: ' + category_id
        ks = resolveLabels(label, ks, log_info)

        data = (
            """ks="""
            + ks
            + """
            &format=1
            &filter[objectType]=KalturaMediaEntryFilter
            &filter[categoriesIdsMatchAnd]=
            """
            + category_id
        )

        response = requests.post(
            kaltura_service_url + '/media/action/list', headers=kaltura_header, data=data
        )
        json_response = json.loads(response.text)
        logger.log('Retrieved entries by category ID ' + str(category_id))

    else:
        json_response = empty_response
        logger.log('Attempted to retrieve entries by category ID ' + str(category_id) + ' but was not allowed')

    return json_response

def start_ksession(payload):
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
    session_type = 0
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
    logger.log('Started Kaltura session for token ID ' + token_id)
    return ksession

# def get_entry(entry_id, ks, label=""):
#     if ks == "":
#         # Generate a token KS if one is not provided, using label
#         # Label will allow retrieval of the token and token ID from the database
#         ks = token_ks()

#     data = 'ks=' +  ks + '&format=1&entryId=' + entry_id
#     response = requests.post(
#         kaltura_service_url + '/media/action/get', headers=kaltura_header, data=data
#     )
#     resp_dict = json.loads(response.text)
#     logger.log("Retrieved info for entry: " + str(entry_id))
#     return resp_dict

def resolveLabels(label, ks, log_info: str):

    Denied = False
    access_restrictions = AccessRestrictions.query.get(1)
    force_labels = access_restrictions.force_labels
    payload = dict()

    all_tokens = KalturaAppToken.query.all()
    matched_token_id = ''
    matched_token = ''
    for token in all_tokens:
        if token.label == label:
            matched_token_id = token.kaltura_token_id
            matched_token = token.token

    # Deny if label is empty or not matched, but forced
    if force_labels:
        if label == '' or matched_token_id == '':
            logger.log('Action denied: ' + log_info + '. Force labels is on.')
            Denied = True

    # If not denied and if we have a label
    if not Denied:
        if matched_token_id != '' or (force_labels and ks == ''):

            # If a label is passed in, use it if we've found it.
            if force_labels == False :
                logger.log('Label used and labels aren\'t being forced: ' + log_info)
            
            # Generate a KS for the associated token and id
            logger.log('Generating a KS with token id: ' + matched_token_id)
            payload = {
                'kaltura_token_id': matched_token_id,
                'token': matched_token
            }
            
            ks = start_ksession(payload)
        
    if (not Denied) and (ks != ''):
        resolved_ks = ks
        
    return resolved_ks