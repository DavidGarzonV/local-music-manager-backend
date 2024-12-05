from datetime import timedelta
import traceback
from flask import Flask, jsonify
from app.common.code_logger import APP_LOGGER
from app.common.environments import ENABLED_ORIGIN, SECRET_KEY
from app.common.error_handling import UnauthorizedException
from app.common.utils import check_if_file_is_empty, create_folder_if_not_exists
from app.config import CONFIGURATION_FILE, CREDENTIALS_FILE, OAUTH_FILE
from app.modules.auth.api_v1.utils import reset_login
from app.modules.playlists.api_v1.resources import playlists_v1_bp
from app.modules.local_files.api_v1.resources import localfiles_v1_bp
from app.modules.songs.api_v1.resources import songs_v1_bp
from app.modules.auth.api_v1.resources import auth_v1_bp
from flask_cors import CORS
from app.common.interceptors import configure_required, token_required


def create_config_files(oauth_file, credentials_file, configuration_file):
    create_folder_if_not_exists("config_files")

    try:
        if check_if_file_is_empty(oauth_file):
            f = open(oauth_file, "w")
            f.write("{}")
            f.close()
    except Exception:
        APP_LOGGER.info("Error creating Oauth file")

    try:
        if check_if_file_is_empty(credentials_file):
            f = open(credentials_file, "w")
            f.write("{}")
            f.close()
    except Exception:
        APP_LOGGER.info("Error creating Credentials file")

    try:
        if check_if_file_is_empty(configuration_file):
            f = open(configuration_file, "w")
            f.write("{}")
            f.close()
    except Exception:
        APP_LOGGER.info("Error creating Configuration file")


def create_app():
    app = Flask(__name__)
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": ENABLED_ORIGIN,
                "methods": ["GET", "POST", "OPTIONS", "HEAD"],
                "allow_headers": ["Authorization, Content-Type"],
            }
        },
    )
    app.config["CORS_HEADERS"] = "Content-Type"
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SESSION_PERMANENT"] = True
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=365)
    app.config["SECRET_KEY"] = SECRET_KEY

    # Disables the strict mode of URL completion with /
    app.url_map.strict_slashes = False

    # Register blueprints
    app.register_blueprint(playlists_v1_bp, url_prefix="/api/v1/playlists")
    app.register_blueprint(localfiles_v1_bp, url_prefix="/api/v1/local-files")
    app.register_blueprint(auth_v1_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(songs_v1_bp, url_prefix="/api/v1/songs")

    # Registers custom error handlers
    register_error_handlers(app)

    # Registers global interceptors
    register_global_interceptors(app)

    create_config_files(OAUTH_FILE, CREDENTIALS_FILE, CONFIGURATION_FILE)

    print('Application started')

    return app


def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_exception_error(e):
        traceback.print_exc()
        return jsonify({"msg": "Internal server error"}), 500

    @app.errorhandler(401)
    def handle_401_error(e):
        return jsonify({"msg": "Unauthorized"}), 401

    @app.errorhandler(403)
    def handle_403_error(e):
        return jsonify({"msg": "Forbidden"}), 403

    @app.errorhandler(404)
    def handle_404_error(e):
        return jsonify({"msg": "Not Found"}), 404

    @app.errorhandler(405)
    def handle_405_error(e):
        return jsonify({"msg": "Method not allowed"}), 405

    @app.errorhandler(UnauthorizedException)
    def handle_unauthorized(e):
        reset_login()
        return jsonify({"msg": "Unauthorized"}), 401


def register_global_interceptors(app):
    @app.before_request
    @configure_required
    @token_required
    def before_request_func():
        pass

    @app.after_request
    def after_request_func(response):
        return response
