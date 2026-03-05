"""
<<<<<<< HEAD
run.py — development entry point for the Flask app.
Run with: python run.py
"""
from __init__ import create_app
=======
run.py — development entry point for the Flask flask_app API.
Run with: python run.py
"""

from flask_app import create_app
>>>>>>> main

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)