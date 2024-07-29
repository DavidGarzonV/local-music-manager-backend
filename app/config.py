import os
import secrets
from app.common.utils import get_env_path
from dotenv import load_dotenv

load_dotenv(dotenv_path=get_env_path())


def generate_secret():
    SECRET_KEY = os.getenv("SECRET_KEY")

    if SECRET_KEY is None or SECRET_KEY == "":
        SECRET_KEY = secrets.token_hex(24)
        with open(get_env_path(), "r") as fp:
            data = fp.read()
            data_env = data.replace('SECRET_KEY=""', 'SECRET_KEY="' + SECRET_KEY + '"')

        with open(get_env_path(), "w") as fp:
            fp.write(data_env)

    return SECRET_KEY


ENVIRONMENT = os.getenv("PROJECT_ENVIRONMENT")
SECRET_KEY = generate_secret()

if ENVIRONMENT == "development":
    IS_DEVELOPMENT = True
else:
    IS_DEVELOPMENT = False
    ENVIRONMENT = "production"

# CORS Enabled origins
ENABLED_ORIGIN = os.getenv("ENABLED_ORIGIN")

# PROPAGATE_EXCEPTIONS: To propagate exceptions and handle them at the application level.
PROPAGATE_EXCEPTIONS = True

# Disables suggestions for other endpoints related to one that does not exist (Flask-Restful).
ERROR_404_HELP = False

# App port
APP_PORT = os.getenv("APP_PORT")

if APP_PORT is None:
    APP_PORT = 5000

# Paths to config files
OAUTH_FILE = os.path.join(os.path.dirname(__file__), "config_files/oauth.json")
CREDENTIALS_FILE = os.path.join(
    os.path.dirname(__file__), "config_files/credentials.json"
)

# Google client config
GOOGLE_SCOPES = ["https://www.googleapis.com/auth/youtube"]
CLIENT_ID = os.getenv("CLIENT_ID")
PROJECT_ID = os.getenv("PROJECT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

CLIENT_CONFIG = {
    "web": {
        "client_id": CLIENT_ID,
        "project_id": PROJECT_ID,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": CLIENT_SECRET,
        "redirect_uris": [REDIRECT_URI],
        "javascript_origins": [ENABLED_ORIGIN],
    }
}
