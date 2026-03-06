# Graph Visualization Tool — Class Diagram

> **Software Patterns & Components** · `api` / `platform` / `data_source_plugin` / `visualizer_plugin`

```mermaid
classDiagram

    %% ── Enums / type aliases ────────────────────────────────────────────────

    class AttributeType {
        <<enumeration>>
        INT = "int"
        FLOAT = "float"
        STRING = "string"
        DATE = "date"
    }

    class AttributeValue {
        <<type alias>>
        Union[int, float, str, date]
    }

    %% ── Core model ──────────────────────────────────────────────────────────

    class Node {
        <<dataclass>>
        +str id
        +Dict~str, AttributeValue~ attributes
        +set_attribute(name: str, value: AttributeValue) None
        +get_attribute(name: str) AttributeValue
    }

    class Edge {
        <<dataclass>>
        +str id
        +str source
        +str target
        +Dict~str, AttributeValue~ attributes
        +set_attribute(name: str, value: AttributeValue) None
    }

    class Graph {
        <<class>>
        +bool directed
        +Dict~str, Node~ nodes
        +Dict~str, Edge~ edges
        -Dict~str, Set~ _outgoing
        -Dict~str, Set~ _incoming
        +add_node(node: Node) None
        +get_node(node_id: str) Node
        +add_edge(edge: Edge) None
        +get_edge(edge_id: str) Edge
        +remove_node(node_id: str) None
        +remove_edge(edge_id: str) None
        +neighbors(node_id: str) Iterable~Node~
        +subgraph(node_ids: Set) Graph
        +has_node(node_id: str) bool
        +has_edge(edge_id: str) bool
        +node_count() int
        +edge_count() int
        +iter_edges() Iterable~Edge~
        +is_directed bool
    }

    %% ── API abstractions ────────────────────────────────────────────────────

    class Plugin {
        <<abstract>>
        +plugin_id()* str
        +name()* str
    }

    class DataSourcePlugin {
        <<abstract>>
        +parameters()* Dict~str, str~
        +load(**kwargs)* Graph
    }

    class VisualizerPlugin {
        <<abstract>>
        +render(graph: Graph)* str
    }

    %% ── Platform ────────────────────────────────────────────────────────────

    class Platform {
        <<platform>>
        -Dict~int, Workspace~ __workspaces
        +add_workspace(workspace: Workspace) None
        +get_workspace(workspace_id: int) Workspace
    }

    class Workspace {
        <<class>>
        -str __id
        -str __filepath
        -DataSourcePlugin __data_source_plugin
        -VisualizerPlugin __visualizer_plugin
        -Graph __graph
        -Graph __initial_graph
        +id str
        +id(workspace_id: str) None
        +filepath str
        +filepath(filepath: str) None
        +source_plugin() DataSourcePlugin
        +visualizer_plugin() VisualizerPlugin
        +graph() Graph
        +graph(graph: Graph) None
        +initial_graph() Graph
        +initial_graph(graph: Graph) None
    }

    %% ── Data source plugins ─────────────────────────────────────────────────

    class JsonDataSourcePlugin {
        <<plugin>>
        +str static_identifier = "JSON"
        +plugin_id() str
        +name() str
        +parameters() Dict~str, str~
        +load(**kwargs) Graph
        -_collect_ids(value: Any) None
        -_visit(value, parent_node_id, rel_name) str
    }

    class XmlDataSourcePlugin {
        <<plugin>>
        +str static_identifier = "XML"
        -int _edge_counter
        -int _node_counter
        -Dict~str, str~ _id_registry
        +plugin_id() str
        +name() str
        +parameters() Dict~str, str~
        +load(**kwargs) Graph
        -_collect_ids(element: Element) None
        -_visit(graph: Graph, element: Element) str
        -_new_edge_id() str
        -_new_node_id() str
        -_ensure_node(graph: Graph, node_id: str) None
    }

    class CsvDataSourcePlugin {
        <<plugin>>
        +str static_identifier = "CSV"
        +plugin_id() str
        +name() str
        +parameters() Dict~str, str~
        +load(**kwargs) Graph
    }

    %% ── Visualizer plugins ──────────────────────────────────────────────────

    class BlockVisualizerPlugin {
        <<plugin>>
        +str static_identifier = "BLOCK"
        +plugin_id() str
        +name() str
        +render(graph: Graph) str
    }

    class SimpleVisualizerPlugin {
        <<plugin>>
        +str static_identifier = "SIMPLE"
        +plugin_id() str
        +name() str
        +render(graph: Graph) str
    }

    %% ── Relationships ───────────────────────────────────────────────────────

    Node ..> AttributeValue : uses
    Edge ..> AttributeValue : uses

    Graph "1" *-- "0..*" Node : nodes
    Graph "1" *-- "0..*" Edge : edges

    DataSourcePlugin --|> Plugin
    VisualizerPlugin --|> Plugin

    JsonDataSourcePlugin   ..|> DataSourcePlugin
    XmlDataSourcePlugin    ..|> DataSourcePlugin
    CsvDataSourcePlugin    ..|> DataSourcePlugin
    BlockVisualizerPlugin  ..|> VisualizerPlugin
    SimpleVisualizerPlugin ..|> VisualizerPlugin

    Platform "1" *-- "0..*" Workspace : __workspaces

    Workspace o-- DataSourcePlugin : __data_source_plugin
    Workspace o-- VisualizerPlugin : __visualizer_plugin
    Workspace o-- Graph            : __graph / __initial_graph
```

---

## Component Overview

| Layer | Classes | Package |
|---|---|---|
| **Model** | `Node`, `Edge`, `Graph`, `AttributeType`, `AttributeValue` | `api` |
| **Abstractions** | `Plugin`, `DataSourcePlugin`, `VisualizerPlugin` | `api` |
| **Platform** | `Platform`, `Workspace` | `platform` |
| **Data source plugins** | `JsonDataSourcePlugin`, `XmlDataSourcePlugin`, `CsvDataSourcePlugin` | `*_data_source_plugin` |
| **Visualizer plugins** | `BlockVisualizerPlugin`, `SimpleVisualizerPlugin` *(pending)* | `block_visualizer`, `simple_visualizer` |

## Relationship Key

| Notation | Meaning |
|---|---|
| `*--` | Composition |
| `o--` | Aggregation |
| `--|>` | Inheritance (extends) |
| `..|>` | Implementation (realization) |
| `..>` | Dependency / uses |