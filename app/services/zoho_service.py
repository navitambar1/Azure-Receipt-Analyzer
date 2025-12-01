import requests
from app.utils.config import get_env

OWNER_NAME = get_env("ZOHO_OWNER_NAME")
APP_LINK_NAME = get_env("ZOHO_APP_LINK_NAME")
FORM_LINK_NAME = get_env("ZOHO_FORM_LINK_NAME")
ZOHO_CLIENT_ID = get_env("ZOHO_CLIENT_ID")
ZOHO_CLIENT_SECRET = get_env("ZOHO_CLIENT_SECRET")
ZOHO_REFRESH_TOKEN = get_env("ZOHO_REFRESH_TOKEN")

def fetch_zoho_token():
    url = f"https://accounts.zohocloud.ca/oauth/v2/token?refresh_token={ZOHO_REFRESH_TOKEN}&client_id={ZOHO_CLIENT_ID}&client_secret={ZOHO_CLIENT_SECRET}&grant_type=refresh_token"
    response = requests.request("POST", url)
    if response.status_code == 200:
        token_info = response.json()
        return token_info['access_token']
    else:
        print("Failed to fetch Zoho token", response.text,"-------------", response.status_code)


def create_record(receipt_data):
    ZOHO_ACCESS_TOKEN = fetch_zoho_token() 
    url = f"https://creator.zohocloud.ca/api/v2/{OWNER_NAME}/{APP_LINK_NAME}/form/{FORM_LINK_NAME}"
    headers={
            "Content-Type": "application/json",
            "Authorization": f"Zoho-oauthtoken {ZOHO_ACCESS_TOKEN}"
        }
    payload = {
        "data": receipt_data
    }
    res = requests.post(url, headers=headers, json=payload)
    print("Zoho Creator Response:", res.status_code, "==========",res.text)
    if res.status_code == 200:
        return res.status_code, res.text
    else:
        print("Failed to create record in Zoho Creator", res.text,"-------------", res.status_code)
        return res.status_code, res.text

