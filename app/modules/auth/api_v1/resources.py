from flask import request, Blueprint
from google_auth_oauthlib import flow
from app.common.code_logger import APP_LOGGER
from app.common.credentials import credentials_to_dict, save_credentials
from app.common.yt_music import check_connection
from app.config import REDIRECT_URI
from app.common.jwt import generate_jwt_token, validate_jwt_token
from app.common.json import (
    load_data_from_json,
)
from app.modules.auth.api_v1.utils import (
    refresh_token_from_session,
    revoke_token,
    handle_login_response,
    reset_login,
)
from app.config import OAUTH_FILE, GOOGLE_SCOPES, CLIENT_CONFIG

# AUTH ROUTES
auth_v1_bp = Blueprint("auth_v1_bp", __name__)


@auth_v1_bp.route("/login", methods=["POST"])
def get_login():
    google_flow = flow.Flow.from_client_config(
        client_config=CLIENT_CONFIG,
        scopes=GOOGLE_SCOPES,
    )
    google_flow.redirect_uri = REDIRECT_URI

    authorization_url, state = google_flow.authorization_url(
        access_type="offline",
        prompt="consent",
        include_granted_scopes="true",
        state=generate_jwt_token({}, 365),
    )

    return {"Success": True, "Response": {"url": authorization_url}}


@auth_v1_bp.route("/session", methods=["POST"])
def create_session():
    data = request.get_json()
    code = data.get("code")
    state = data.get("state")

    if code is None or len(code) == 0 or code == "":
        return {
            "Success": False,
            "Error": "Code is required",
        }, 400

    if state is None or len(state) == 0 or state == "":
        return {
            "Success": False,
            "Error": "State is required",
        }, 400

    if validate_jwt_token(state) is False:
        return {
            "Success": False,
            "Error": "Invalid state",
        }, 400

    try:
        google_flow = flow.Flow.from_client_config(
            client_config=CLIENT_CONFIG,
            scopes=GOOGLE_SCOPES,
        )
        google_flow.redirect_uri = REDIRECT_URI
        response = google_flow.fetch_token(code=code)

        credentials = google_flow.credentials
        save_credentials(credentials_to_dict(credentials))

        return handle_login_response(response)
    except Exception as e:
        APP_LOGGER.error("Error fetching token:")
        APP_LOGGER.error(e)

    return {"Success": False}


@auth_v1_bp.route("/refresh", methods=["POST"])
def refresh_session():
    oauth_credettials = refresh_token_from_session()
    if oauth_credettials is False:
        return {"Success": False}, 400

    return handle_login_response(oauth_credettials)


@auth_v1_bp.route("/check", methods=["POST"])
def check():
    data = request.get_json()
    token = data.get("accessToken")

    if token is None or token == "":
        return {"Success": False}

    validated_token = validate_jwt_token(token)
    validated_connection = check_connection(True)

    return {"Success": validated_token and validated_connection}


@auth_v1_bp.route("/logout", methods=["POST"])
def logout():
    data_json = load_data_from_json(OAUTH_FILE)

    try:
        revoke_token(data_json.get("access_token"))
    except Exception as e:
        APP_LOGGER.error("Error revoking token:")
        APP_LOGGER.error(e)

    reset_login()

    return {"Success": True}