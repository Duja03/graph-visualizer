import re
from datetime import date
from pathlib import Path
from typing import Any, Dict, Optional
from xml.etree import ElementTree

from api.model.graph import Graph
from api.model.node import Node
from api.model.edge import Edge
from api.plugins.datasource_plugin import DataSourcePlugin

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"

def _parse_typed_value(v: Any) -> Optional[str | int | float | date]:
    if v is None:
        return None

    if isinstance(v, str):
        s = v.strip()

        if not s:
            return None

        if _DATE_RE.match(s):
            try:
                y, m, d = s.split("-")
                return date(int(y), int(m), int(d))
            except ValueError:
                return s

        if s.isdigit() or (s.startswith("-") and s[1:].isdigit()):
            return int(s)

        try:
            if "." in s or "e" in s.lower():
                return float(s)
        except ValueError:
            pass

        return s

    return None


class XmlDataSourcePlugin(DataSourcePlugin):

    static_identifier = "XML"

    def __init__(self):
        self._edge_counter: int = 0
        self._node_counter: int = 0
        self._id_registry: Dict[str, str] = {}

    def plugin_id(self) -> str:
        return "xml_datasource"

    def name(self) -> str:
        return "XML Data Source"

    def parameters(self) -> Dict[str, str]:
        return {
            "file_path": "Path to the XML file to load."
        }

    def load(self, **kwargs: Any) -> Graph:
        file_path = kwargs.get("file_path")
        if not file_path:
            raise ValueError("Missing parameter: file_path")

        p = Path(str(file_path))
        if not p.exists() or not p.is_file():
            raise ValueError(f"XML file not found: {p}")

        try:
            tree = ElementTree.parse(str(p))
        except ElementTree.ParseError as e:
            raise ValueError(f"XML parse error: {e}")

        xml_root = tree.getroot()

        graph = Graph(directed=True)

        self._edge_counter = 0
        self._node_counter = 0
        self._id_registry = {}

        self._collect_ids(xml_root)
        self._visit(graph, xml_root)

        return graph

    def _new_edge_id(self) -> str:
        self._edge_counter += 1
        return f"e{self._edge_counter}"

    def _new_node_id(self) -> str:
        self._node_counter += 1
        return f"n{self._node_counter}"

    @staticmethod
    def _ensure_node(graph: Graph, node_id: str) -> None:
        if not graph.has_node(node_id):
            graph.add_node(Node(id=node_id))

    def _collect_ids(self, element: ElementTree.Element) -> None:
        xml_id = element.get(XML_ID)
        if xml_id and xml_id.strip():
            self._id_registry[xml_id.strip()] = xml_id.strip()
        for child in element:
            self._collect_ids(child)

    def _visit(self, graph: Graph, element: ElementTree.Element) -> str:
        xml_id = element.get(XML_ID)
        node_id = xml_id.strip() if (xml_id and xml_id.strip()) else self._new_node_id()

        self._ensure_node(graph, node_id)
        node = graph.get_node(node_id)
        node.set_attribute("_tag", element.tag)

        for attr_name, attr_val in element.attrib.items():
            if attr_name in (XML_ID, "reference"):
                continue
            typed = _parse_typed_value(attr_val)
            if typed is not None:
                node.set_attribute(attr_name, typed)

                value_node_id = self._new_node_id()
                graph.add_node(Node(id=value_node_id))
                graph.get_node(value_node_id).set_attribute("value", typed)
                graph.add_edge(Edge(
                    id=self._new_edge_id(),
                    source=node_id,
                    target=value_node_id,
                    attributes={"name": attr_name}
                ))

        ref = element.get("reference")
        if ref and ref.strip() in self._id_registry:
            target_id = ref.strip()
            self._ensure_node(graph, target_id)
            graph.add_edge(Edge(
                id=self._new_edge_id(),
                source=node_id,
                target=target_id,
                attributes={"name": "reference"},
            ))

        for child in element:
            child_has_children = len(child) > 0
            child_has_attributes = any(
                k not in (XML_ID, "reference")
                for k in child.attrib
            )

            if not child_has_children and not child_has_attributes:
                typed = _parse_typed_value((child.text or "").strip())
                if typed is not None:
                    node.set_attribute(child.tag, typed)

                if child.get(XML_ID) or child.get("reference"):
                    child_id = self._visit(graph, child)
                    graph.add_edge(Edge(
                        id=self._new_edge_id(),
                        source=node_id,
                        target=child_id,
                        attributes={"name": child.tag},
                    ))

            else:
                child_id = self._visit(graph, child)
                graph.add_edge(Edge(
                    id=self._new_edge_id(),
                    source=node_id,
                    target=child_id,
                    attributes={"name": child.tag},
                ))

        return node_id