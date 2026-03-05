"""
flask_app — Flask microservice.
Exposes the graph data API consumed by the Django django_app app.
All heavy logic is delegated to the platform library and installed plugins.
"""

from flask import Flask
from .routes import api_bp
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)  
    app.register_blueprint(api_bp, url_prefix='/api')
    return app