# Platform

Core platform library for graph visualizer. Provides workspace management, graph manipulation (filtering, search), and a CLI engine. The web application (Django or Flask) communicates exclusively through the `Platform`.

## Dependencies
- `api` — graph model and plugin interfaces

## Installation
Make sure to turn on your virtual environment first!
```bash
cd ..
pip install -e api
pip install -e platform
```

## Usage

All operations go through the `Platform`:

```python
from core import Platform

platform = Platform()
```

### Workspace management

```python
# Create workspace after loading a graph via a datasource plugin
workspace_id = platform.create_workspace(graph, data_source_plugin, visualizer_plugin)

# Retrieve workspace
workspace = platform.get_workspace(workspace_id)

# List all active workspaces
workspaces = platform.list_workspaces()

# Delete workspace
platform.delete_workspace(workspace_id)

# Reset graph to its original loaded state
graph = platform.reset_workspace(workspace_id)
```

### Search

Free-text search over node attribute names and values (case-insensitive contains). Updates `workspace.graph` to the resulting subgraph.

```python
result = platform.search(workspace_id, "alice")
# returns Graph on success, str error message on failure
```

### Filter

Structured filter using the format `<attribute> <operator> <value>`. Supported operators: `==`, `!=`, `>`, `>=`, `<`, `<=`. Updates `workspace.graph` to the resulting subgraph.

```python
result = platform.filter(workspace_id, "age > 30")
result = platform.filter(workspace_id, "city == Berlin")
result = platform.filter(workspace_id, "joined >= 2020-01-01")
# returns Graph on success, str error message on failure
```

Filter respects attribute types — comparing an `int` attribute with a string value will return an error.

### CLI

Execute CLI command strings against the active workspace graph.

```python
result = platform.execute_cli(workspace_id, "create node --id=1 --attribute name=Alice")
# returns:
#   None  — mutating command succeeded (graph modified in-place)
#   Graph — filter/search command succeeded (workspace.graph updated)
#   str   — error message (workspace.graph unchanged)
```

#### CLI command reference

**Node commands**
```
create node --id=<id> [--attribute <name>=<value> ...]
edit node   --id=<id>  --attribute <name>=<value> [...]
delete node --id=<id>
```

**Edge commands**
```
create edge --id=<id> --source=<node_id> --target=<node_id> [--attribute <name>=<value> ...]
edit edge   --id=<id>  --attribute <name>=<value> [...]
delete edge --id=<id>
```

**Graph commands**
```
delete graph
```

**Filter**
```
filter <attribute><operator><value>
```
Examples:
```
filter age>30
filter city==Berlin
filter salary>=3500
filter joined!=2020-01-15
```

**Search**
```
search <query>
```
Examples:
```
search Alice
search 2020-01-15
search Berlin
```

**Other commands**
```
help    — display command reference
clear   — clear terminal output
```

#### CLI examples

```
create node --id=1 --attribute name=Alice --attribute age=30
create node --id=2 --attribute name=Bob --attribute age=25
create edge --id=e1 --source=1 --target=2 --attribute weight=0.8
edit node --id=1 --attribute age=31
edit edge --id=e1 --attribute weight=0.9
filter age>25
search Alice
delete edge --id=e1
delete node --id=2
delete graph
```

Notes:
- Attribute values are automatically typed: integers, floats, ISO dates (`YYYY-MM-DD`), and strings are all supported.
- `delete node` fails if the node still has connected edges — delete its edges first.
- `filter` and `search` are applied successively on the current workspace graph. Use `reset` to return to the original graph.
- `help` and `clear` are handled client-side and do not require a loaded workspace.