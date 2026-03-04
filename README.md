# Graphify-Graph-Visualiser

### Contributors

1. Aleksa Ćurčić
2. Maksim Vasić
3. Milan Kačarević
4. Miomir Dujanović
5. Sara Stojkov

### Installation

First, activate your virtual environment from the project root:
```bash
source .venv/bin/activate  # Unix/Mac
.venv\Scripts\activate     # Windows
```

Then run the install script to install all components:

**Windows:**
```bash
scripts/installation/install.bat
```

**Unix/Mac:**
```bash
./scripts/install.sh
```

### Running the Application

Both Django and Flask are fully independent web applications. Each can be run
and used on its own. They do not depend on each other.

### Running the Django app
```bash
source .venv/bin/activate
cd graph_explorer/django_app
python manage.py runserver
```

Django will be available at http://127.0.0.1:8000

### Running the Flask app
```bash
source .venv/bin/activate
cd graph_explorer/flask_app
python -m run
```

Flask will be available at http://127.0.0.1:5000

### Note

Both apps provide the same functionality independently. You do not need to run
both at the same time — each one is a complete standalone application.