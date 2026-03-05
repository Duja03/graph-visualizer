"""
Flask web application for Graph Explorer.
Serves frontend templates and API endpoints.
Talks directly to platform and plugins — no Django dependency.
"""
from flask import Flask
from .routes import api_bp
from flask_cors import CORS
import os

def create_app():
    template_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..', 'platform', 'templates')
    )
    static_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..', 'platform', 'static')
    )
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    CORS(app)
    app.register_blueprint(api_bp)
    return app