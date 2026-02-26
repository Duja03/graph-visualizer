import json
import re
from datetime import date
from pathlib import Path
from typing import Any, Dict, Optional

from api.model.graph import Graph
from api.model.node import Node
from api.model.edge import Edge
from api.model.attribute_type import AttributeValue
from api.plugins.datasource_plugin import DataSourcePlugin


_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _parse_typed_value(v: Any) -> Optional[AttributeValue]:
    """
    Returns AttributeValue if scalar (int/float/str/date),
    otherwise None.
    """
    if v is None:
        return None

    if isinstance(v, bool):
        return str(v)

    if isinstance(v, int):
        return v

    if isinstance(v, float):
        return v

    if isinstance(v, str):
        s = v.strip()

        # ISO date
        if _DATE_RE.match(s):
            try:
                y, m, d = s.split("-")
                return date(int(y), int(m), int(d))
            except ValueError:
                return s

        # int as string
        if s.isdigit() or (s.startswith("-") and s[1:].isdigit()):
            try:
                return int(s)
            except Exception:
                pass

        # float as string
        try:
            if "." in s or "e" in s.lower():
                return float(s)
        except Exception:
            pass

        return s

    return None


class JsonDataSourcePlugin(DataSourcePlugin):

    def plugin_id(self) -> str:
        return "json_datasource"

    def name(self) -> str:
        return "JSON Data Source"

    def parameters(self) -> Dict[str, str]:
        return {
            "file_path": "Path to JSON file"
        }

    def load(self, **kwargs: Any) -> Graph:

        file_path = kwargs.get("file_path")
        if not file_path:
            raise ValueError("Missing parameter: file_path")

        p = Path(str(file_path))
        if not p.exists() or not p.is_file():
            raise ValueError(f"JSON file not found: {p}")

        data = json.loads(p.read_text(encoding="utf-8"))

        graph = Graph(directed=True)

        id_to_node_id: Dict[str, str] = {}

        edge_counter = 0
        auto_node_counter = 0

        def new_edge_id() -> str:
            nonlocal edge_counter
            edge_counter += 1
            return f"e{edge_counter}"

        def new_auto_node_id() -> str:
            nonlocal auto_node_counter
            auto_node_counter += 1
            return f"n{auto_node_counter}"

        def ensure_node(node_id: str):
            if not graph.has_node(node_id):
                graph.add_node(Node(id=node_id))

        # first pass to collect all @id values

        def collect_ids(value: Any):

            if isinstance(value, dict):

                raw_id = value.get("@id")
                if isinstance(raw_id, str) and raw_id.strip():
                    node_id = raw_id.strip()
                    id_to_node_id[node_id] = node_id
                    ensure_node(node_id)

                for v in value.values():
                    collect_ids(v)

            elif isinstance(value, list):
                for item in value:
                    collect_ids(item)

        collect_ids(data)

        # second pass to construct graph

        def visit(
            value: Any,
            parent_node_id: Optional[str],
            rel_name: str
        ) -> Optional[str]:

            if isinstance(value, dict):

                node_id = None

                raw_id = value.get("@id")
                if isinstance(raw_id, str) and raw_id.strip():
                    node_id = raw_id.strip()

                if node_id is None:
                    node_id = new_auto_node_id()

                ensure_node(node_id)

                node = graph.get_node(node_id)

                # scalar attributes
                for k, v in value.items():
                    if k == "@id":
                        continue

                    typed = _parse_typed_value(v)
                    if typed is not None:
                        node.set_attribute(k, typed)

                # relations
                for k, v in value.items():

                    if k == "@id":
                        continue

                    if isinstance(v, (dict, list)):

                        child_id = visit(v, node_id, k)

                        if child_id:
                            graph.add_edge(
                                Edge(
                                    id=new_edge_id(),
                                    source=node_id,
                                    target=child_id,
                                    attributes={"name": k}
                                )
                            )

                    elif isinstance(v, str):

                        ref = v.strip()

                        if ref in id_to_node_id:
                            graph.add_edge(
                                Edge(
                                    id=new_edge_id(),
                                    source=node_id,
                                    target=ref,
                                    attributes={"name": k}
                                )
                            )

                if parent_node_id is not None:
                    graph.add_edge(
                        Edge(
                            id=new_edge_id(),
                            source=parent_node_id,
                            target=node_id,
                            attributes={"name": rel_name}
                        )
                    )

                return node_id

            # LIST
            if isinstance(value, list):

                container_id = new_auto_node_id()
                ensure_node(container_id)

                container = graph.get_node(container_id)
                container.set_attribute("type", "list")

                if parent_node_id:
                    graph.add_edge(
                        Edge(
                            id=new_edge_id(),
                            source=parent_node_id,
                            target=container_id,
                            attributes={"name": rel_name}
                        )
                    )

                for idx, item in enumerate(value):

                    child_id = visit(
                        item,
                        container_id,
                        f"{rel_name}[{idx}]"
                    )

                    if child_id is None:
                        typed = _parse_typed_value(item)
                        if typed is not None:
                            container.set_attribute(
                                str(idx),
                                typed
                            )

                return container_id

            return None

        root_id = "root"
        ensure_node(root_id)

        visit(data, root_id, "root")

        return graph