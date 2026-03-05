"""
<<<<<<< HEAD
Flask web application for Graph Explorer.
Serves frontend templates and API endpoints.
Talks directly to platform and plugins — no Django dependency.
"""
from flask import Flask
from routes import api_bp
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
=======
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
>>>>>>> main
    return app