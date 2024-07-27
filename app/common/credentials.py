from app.common.json import load_data_from_json, save_data_to_json
from app.config import CREDENTIALS_FILE, GOOGLE_SCOPES, CLIENT_CONFIG

CLIENT_ID = CLIENT_CONFIG["web"]["client_id"]
CLIENT_SECRET = CLIENT_CONFIG["web"]["client_secret"]

def credentials_to_dict(credentials):
    return {"token": credentials.token, "refresh_token": credentials.refresh_token}

def credentials_from_dict(credentials):
    credentials["client_id"] = CLIENT_ID
    credentials["client_secret"] = CLIENT_SECRET
    credentials["scopes"] = GOOGLE_SCOPES
    credentials["token_uri"] = "https://oauth2.googleapis.com/token"

    return credentials


def validate_credentials():
    credentials = load_data_from_json(CREDENTIALS_FILE)
    return "token" in credentials


def save_credentials(credentials):
    save_data_to_json(credentials, CREDENTIALS_FILE)


def get_credentials():
    return credentials_from_dict(load_data_from_json(CREDENTIALS_FILE))


def remove_credentials():
    save_data_to_json({}, CREDENTIALS_FILE)
