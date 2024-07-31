from datetime import timedelta
import traceback
from flask import Flask, jsonify
from app.common.code_logger import APP_LOGGER
from app.common.error_handling import UnauthorizedException
from app.modules.auth.api_v1.utils import reset_login
from app.modules.playlists.api_v1.resources import playlists_v1_bp
from app.modules.local_files.api_v1.resources import localfiles_v1_bp
from app.modules.songs.api_v1.resources import songs_v1_bp
from app.modules.auth.api_v1.resources import auth_v1_bp
from flask_cors import CORS
from app.common.interceptors import configure_required, token_required
from app.config import CREDENTIALS_FILE, ENABLED_ORIGIN, OAUTH_FILE, SECRET_KEY

def create_config_files(oauth_file, credentials_file):
    try:
        f = open(oauth_file, 'x')
        f.write("{}")
    except Exception:
        APP_LOGGER.info('Auth file already exists')

    try:
        f = open(credentials_file, 'x')
        f.write("{}")
    except Exception:
        APP_LOGGER.info('Credentials file already exists')

def create_app():
    create_config_files(OAUTH_FILE, CREDENTIALS_FILE)

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
