# Platform

Core platform library for graph visualizer. Provides graph manipulation logic including filtering, search, workspace management and CLI used by the web application.

## Dependencies
- `api` — graph model and plugin interfaces

## Installation
```bash
cd ..
source .venv/bin/activate
pip install -e api
pip install -e platform
```

## Usage
```python
from core import FilterEngine, FilterError
from core import SearchEngine
from core import Platform
from core import Workspace
```