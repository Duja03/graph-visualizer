"""
explorer — Flask microservice.
Exposes the graph data API consumed by the Django graph_explorer app.
All heavy logic is delegated to the platform library and installed plugins.
"""

from flask import Flask
from .routes import api_bp


def create_app():
    app = Flask(__name__)
    app.register_blueprint(api_bp, url_prefix='/api')
    return app