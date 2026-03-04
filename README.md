# Graphify-Graph-Visualiser

### Contributors

1. Aleksa Ćurčić
2. Maksim Vasić
3. Milan Kačarević
4. Miomir Dujanović
5. Sara	Stojkov

### Installation

From the project root, install all components in order:
```bash
source .venv/bin/activate
pip install -e api
pip install -e platform
pip install -e plugins/csv_datasource_plugin
pip install -e plugins/json_datasource
pip install -e plugins/xml_datasource_plugin
pip install -e plugins/block_visualizer_plugin
```

### Running the Application

The application has two servers that must both be running: a **Flask** backend and a **Django** frontend. Start them in the order below.

#### 1. Start the Flask server

Navigate to the `web` folder and run:

```bash
source .venv/bin/activate
cd web
python -m explorer.run
```

Flask will start on its default port. Keep this terminal open.

#### 2. Start the Django server

In a **separate terminal** run:

```bash
source .venv/bin/activate
cd web/graph_explorer
python manage.py runserver
```

Django will start at [http://127.0.0.1:8000](http://127.0.0.1:8000). Open this in your browser.

> **Note:** Flask must be running before Django, as Django proxies API requests to the Flask backend.