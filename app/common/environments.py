import os
import secrets
from dotenv import load_dotenv
from app.common.utils import get_env_path

load_dotenv(dotenv_path=get_env_path())

ENVIRONMENT = os.getenv("ENVIRONMENT")

IS_DEVELOPMENT = False
if ENVIRONMENT == "development":
    IS_DEVELOPMENT = True
else:
    IS_DEVELOPMENT = False
    ENVIRONMENT = "production"

# CORS Enabled origins
ENABLED_ORIGIN = os.getenv("ENABLED_ORIGIN")

# App port
APP_PORT = os.getenv("APP_PORT")

if APP_PORT is None:
    APP_PORT = 5000

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

SECRET_KEY = generate_secret()
