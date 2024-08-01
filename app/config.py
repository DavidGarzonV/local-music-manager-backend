import os
from app.common.environments import ENABLED_ORIGIN
from app.common.json import load_data_from_json

# PROPAGATE_EXCEPTIONS: To propagate exceptions and handle them at the application level.
PROPAGATE_EXCEPTIONS = True

# Disables suggestions for other endpoints related to one that does not exist (Flask-Restful).
ERROR_404_HELP = False

# Paths to config files
OAUTH_FILE = os.path.join(os.path.dirname(__file__), "config_files/oauth.json")
CREDENTIALS_FILE = os.path.join(
    os.path.dirname(__file__), "config_files/credentials.json"
)
CONFIGURATION_FILE = os.path.join(
    os.path.dirname(__file__), "config_files/configuration.json"
)

# Google client config
GOOGLE_SCOPES = ["https://www.googleapis.com/auth/youtube"]

def get_client_config():
    configuration_data = load_data_from_json(CONFIGURATION_FILE)
    CLIENT_ID = configuration_data.get("CLIENT_ID")
    PROJECT_ID = configuration_data.get("PROJECT_ID")
    CLIENT_SECRET = configuration_data.get("CLIENT_SECRET")
    REDIRECT_URI = configuration_data.get("REDIRECT_URI")

    return {
        "web": {
            "client_id": CLIENT_ID,
            "project_id": PROJECT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uris": [REDIRECT_URI],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "javascript_origins": [ENABLED_ORIGIN],
        }
    }
