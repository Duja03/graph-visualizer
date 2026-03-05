import csv
import re
from datetime import date
from pathlib import Path
from typing import Any, Optional, Dict

from api.model.graph import Graph
from api.model.node import Node
from api.model.edge import Edge
from api.model.attribute_type import AttributeValue
from api.plugins.datasource_plugin import DataSourcePlugin

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _parse_typed_value(v: Any) -> Optional[AttributeValue]:
    if v is None or v == "":
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


class CsvDataSourcePlugin(DataSourcePlugin):

    static_identifier = "CSV"

    def plugin_id(self) -> str:
        return "csv_data_source"

    def name(self) -> str:
        return "CSV Data Source"

    def parameters(self) -> Dict[str, str]:
        return {
            "file_path": "Path to CSV file",
            "edge_column": "Column referencing another row's id (default: connected_to)"
        }

    def load(self, **kwargs: Any) -> Graph:
        file_path = kwargs.get("file_path")
        if not file_path:
            raise ValueError("Missing parameter: file_path")

        p = Path(str(file_path))
        if not p.exists() or not p.is_file():
            raise ValueError(f"CSV file not found: {p}")

        edge_column = kwargs.get("edge_column", "connected_to")
        edge_counter = 0
        graph = Graph(directed=True)
        rows = []

        # First pass - create all nodes
        with open(p, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                node_id = row.get("id", "").strip()
                if not node_id:
                    continue
                node = Node(id=node_id)
                for col, val in row.items():
                    if col in ("id", edge_column):
                        continue
                    typed = _parse_typed_value(val)
                    if typed is not None:
                        node.set_attribute(col, typed)
                graph.add_node(node)
                rows.append(row)

        # Second pass - create all edges
        for row in rows:
            source_id = row.get("id", "").strip()
            target_ids = row.get(edge_column, "").strip()
            if not target_ids:
                continue
            for target_id in target_ids.split(";"):
                target_id = target_id.strip()
                if target_id and graph.has_node(target_id):
                    edge_counter += 1
                    graph.add_edge(Edge(
                        id=f"e{edge_counter}",
                        source=source_id,
                        target=target_id,
                        attributes={"name": edge_column}
                    ))

        return graph