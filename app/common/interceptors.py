from flask import request, make_response
from functools import wraps
import re
from app.common.credentials import validate_credentials
from app.common.jwt import validate_jwt_token
from app.common.utils import get_env_path
from app.common.yt_music import check_connection
from app.modules.auth.api_v1.utils import reset_login

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == "OPTIONS":
            response = make_response("OK", 200)
            response.headers.add_header(
                "Access-Control-Allow-Headers", "Authorization, Content-Type"
            )

            return response

        resources_without_auth = [
            "get_login",
            "check",
            "create_session",
            "logout",
            "configure",
        ]

        if request.endpoint is not None:
            current_resource = request.endpoint.split(".")[1]

            if current_resource not in resources_without_auth:
                token = request.headers.get("Authorization")

                if token is not None and token != "":
                    splitted_token = token.split(" ")
                    if len(splitted_token) > 0:
                        token = splitted_token[1]
                else:
                    return make_response({"error": "Unauthorized"}, 401)

                result_validate = validate_token(token)
                result_credentials = validate_credentials()

                if not result_validate or not result_credentials:
                    reset_login()
                    return make_response({"error": "Unauthorized"}, 401)

        return f(*args, **kwargs)

    return decorated


def validate_token(token: str):
    if token is None or token == "":
        return False
    else:
        validated_token = validate_jwt_token(token)
        if not validated_token:
            return False

    return check_connection()


def configure_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.endpoint is not None:
            current_resource = request.endpoint.split(".")[1]

            if current_resource != "configure":
                is_not_configured = False
                with open(get_env_path(), "r") as fp:
                    data = fp.read()

                    pattern = re.compile(r'(\w+)=["\'](.*?)["\']')
                    matches = pattern.findall(data)
                    config_dict = {key: value for key, value in matches}

                    if (
                        "CLIENT_ID" not in data
                        or config_dict.get("CLIENT_ID") == ""
                        or "CLIENT_SECRET" not in data
                        or config_dict.get("CLIENT_SECRET") == ""
                        or "PROJECT_ID" not in data
                        or config_dict.get("PROJECT_ID") == ""
                        or "REDIRECT_URI" not in data
                        or config_dict.get("REDIRECT_URI") == ""
                    ):
                        is_not_configured = True

                if is_not_configured:
                    return make_response({"error": "The application has not been configured"}, 400)

        return f(*args, **kwargs)

    return decorated
