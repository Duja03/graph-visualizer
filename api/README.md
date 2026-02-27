# API

Core API library for graph visualizer. Provides graph model classes (`Graph`, `Node`, `Edge`, `AttributeValue`) and plugin interfaces (`DataSourcePlugin`, `VisualizerPlugin`) used by the platform and all plugins.

## Installation
```bash
pip install -e ../api
```

## Usage
```python
from api.model import Graph, Node, Edge, AttributeValue
from api.plugins import DataSourcePlugin, VisualizerPlugin, Plugin
```