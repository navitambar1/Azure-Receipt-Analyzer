import requests
import json
from app.utils.config import get_env

ZOHO_CLIENT_ID = get_env("ZOHO_CLIENT_ID")
ZOHO_CLIENT_SECRET = get_env("ZOHO_CLIENT_SECRET")
ZOHO_WORKDRIVE_REFRESH_TOKEN = get_env("ZOHO_WORKDRIVE_REFRESH_TOKEN")

def refresh_zoho_oauth_token():
    url = f"https://accounts.zohocloud.ca/oauth/v2/token?refresh_token={ZOHO_WORKDRIVE_REFRESH_TOKEN}&client_id={ZOHO_CLIENT_ID}&client_secret={ZOHO_CLIENT_SECRET}&grant_type=refresh_token"
    response = requests.request("POST", url)
    if response.status_code == 200:
        token_info = response.json()
        return token_info['access_token']
    else:
        print("Failed to fetch Zoho Workdrive token", response.text,"-------------", response.status_code)

def get_zoho_workdrive_download_link(resource_id, link_id):

    url = f"https://workdrive.zohoexternal.ca/public/api/v1/downloadauth/{resource_id}?linkId={link_id}"
    response = requests.request("GET", url)
    if response.status_code == 200:
        res_json = response.json()
        download_link = res_json.get("DOWNLOAD_LINK")
        return download_link
    else:
        print("Failed to fetch Download Link from Workdrive", response.text,"-------------", response.status_code)
        
def create_zoho_workdrive_link(resource_id):
    url = "https://workdrive.zohocloud.ca/workdrive/api/v1/links"
    ZOHO_WORKDRIVE_ACCESS_TOKEN = refresh_zoho_oauth_token()
    
    payload = json.dumps({
    "data": {
        "attributes": {
        "resource_id": resource_id,
        "link_name": "Recipt1",
        "link_type": "download",
        "request_user_data": "false",
        "allow_download": "true"
        },
        "type": "links"
    }
    })
    headers = {
    'Authorization': f'Zoho-oauthtoken {ZOHO_WORKDRIVE_ACCESS_TOKEN}',
    'Content-Type': 'application/json',
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 201:
        res_json = response.json()
        link_id = res_json.get("data", {}).get("id", "")
        download_link = get_zoho_workdrive_download_link(resource_id, link_id)
        return download_link
    else:
        print("Failed to fetch Download link from Workdrive", response.text,"-------------", response.status_code)

