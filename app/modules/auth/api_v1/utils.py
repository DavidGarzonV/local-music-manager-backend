import requests
from app.common.code_logger import APP_LOGGER
from app.common.credentials import (
    credentials_to_dict,
    get_credentials,
    remove_credentials,
    save_credentials,
    validate_credentials,
)
from app.common.jwt import generate_jwt_token
from app.common.json import load_data_from_json, save_data_to_json
from app.common.utils import generate_expired_at
from app.config import OAUTH_FILE
import google.oauth2.credentials


def revoke_token(access_token):
    try:
        x = requests.post(
            "https://oauth2.googleapis.com/revoke",
            params={"token": access_token},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )
        return x.status_code == 200
    except Exception as e:
        APP_LOGGER.error("Error revoking token:")
        APP_LOGGER.error(e)

    return False


def create_login_token():
    login_token = generate_jwt_token({}, 365)
    return login_token


def handle_login_response(response):
    save_data_to_json(response, OAUTH_FILE)
    login_token = create_login_token()

    return {
        "Success": True,
        "Response": {
            "access_token": login_token,
        },
    }


def create_session_from_file():
    data_json = load_data_from_json(OAUTH_FILE)

    if "access_token" not in data_json or "refresh_token" not in data_json:
        return False

    save_credentials({
        "token": data_json.get("access_token"),
        "refresh_token": data_json.get("refresh_token")
    })

    return True


def refresh_token_from_session():
    data_json = load_data_from_json(OAUTH_FILE)

    try:
        if not validate_credentials():
            return create_session_from_file()

        # Refresh the token with method from google.oauth2.credentials.Credentials
        credentials = google.oauth2.credentials.Credentials(**get_credentials())

        request = google.auth.transport.requests.Request()
        credentials.refresh(request)

        expires_in = data_json.get("expires_in")
        expires_at = generate_expired_at(expires_in)

        refresh_token = credentials.refresh_token
        if refresh_token is None or len(refresh_token) == 0 or refresh_token == "":
            return False

        save_credentials(credentials_to_dict(credentials))

        oauth_credentials = {
            "access_token": credentials.token,
            "expires_in": expires_in,
            "refresh_token": credentials.refresh_token,
            "scope": credentials.scopes,
            "token_type": "Bearer",
            "expires_at": expires_at,
        }

        return oauth_credentials
    except Exception as e:
        APP_LOGGER.error("Error refreshing token:")
        APP_LOGGER.error(e)

        return False


def reset_login():
    save_data_to_json({}, OAUTH_FILE)
    remove_credentials()
