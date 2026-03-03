# Graphify-Graph-Visualiser

### Contributors

1. Aleksa Ćurčić
2. Maksim Vasić
3. Milan Kačarević
4. Miomir Dujanović
5. Sara	Stojkov

### Project Setup

#### Web Application

1. Install NVM (Node Version Manager)
2. Use NVM to install NPM 22.12.0
   - Run `nvm list available`
   - Run `nvm install 22.12.0`
   - Run `nvm use 22.12.0`
3. Run `npm install`

### Style Setup
Import ```code-style.xml``` into your IDE of choice.


---

### Running the Application

The application has two servers that must both be running: a **Flask** backend and a **Django** frontend. Start them in the order below.

#### 1. Start the Flask server

Navigate to the `web` folder and run:

```bash
cd web
python -m explorer.run
```

Flask will start on its default port. Keep this terminal open.

#### 2. Start the Django server

In a **separate terminal**, navigate to `web/graph_explorer` and run:

```bash
cd web/graph_explorer
python manage.py runserver
```

Django will start at [http://127.0.0.1:8000](http://127.0.0.1:8000). Open this in your browser.

> **Note:** Flask must be running before Django, as Django proxies API requests to the Flask backend.