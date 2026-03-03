"""
run.py — development entry point for the Flask explorer API.
Run with: python run.py
"""

from explorer import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)