import re
from datetime import date
from enum import Enum
from typing import Dict, Tuple

from commands.command import Command
from api.model import AttributeValue, Graph
from commands.edge_commands import CreateEdgeCommand, EditEdgeCommand, DeleteEdgeCommand
from commands.filter_commands import FilterCommand
from commands.graph_commands import DeleteGraphCommand
from commands.node_commands import CreateNodeCommand, EditNodeCommand, DeleteNodeCommand
from commands.search_commands import SearchCommand

_METHOD_RE = re.compile(r'^(create|edit|delete|filter|search)\b')
_SUBJECT_RE = re.compile(r'^(?:create|edit|delete|filter|search)\s+(node|edge|graph)\b')


class CLIParseError(Exception):
    """Raised when a CLI command string cannot be parsed."""
    pass


class Method(Enum):
    CREATE = "create"
    EDIT = "edit"
    DELETE = "delete"
    FILTER = "filter"
    SEARCH = "search"


class Subject(Enum):
    NODE = "node"
    EDGE = "edge"
    GRAPH = "graph"


def _infer_type(value: str) -> AttributeValue:
    """Infer the type of raw string value"""
    # date: YYYY-MM-DD
    try:
        return date.fromisoformat(value)
    except ValueError:
        pass
    # int
    try:
        return int(value)
    except ValueError:
        pass
    # float
    try:
        return float(value)
    except ValueError:
        pass
    # fallback to str
    return value


class CLIParser:

    @staticmethod
    def parse(command: str, graph: Graph) -> Command | None:
        command = command.strip()
        if not command:
            raise CLIParseError("Empty command.")

        method = CLIParser._parse_method(command)

        match method:
            case Method.CREATE:
                subject = CLIParser._parse_subject(command)
                if subject == Subject.NODE:
                    node_id, attributes = CLIParser._parse_create_node_arguments(command)
                    return CreateNodeCommand(graph, node_id, attributes)
                elif subject == Subject.EDGE:
                    edge_id, source, target, attributes = CLIParser._parse_create_edge_arguments(command)
                    return CreateEdgeCommand(graph, edge_id, source, target, attributes)

            case Method.EDIT:
                subject = CLIParser._parse_subject(command)
                if subject == Subject.NODE:
                    node_id, attributes = CLIParser._parse_edit_node_arguments(command)
                    return EditNodeCommand(graph, node_id, attributes)
                elif subject == Subject.EDGE:
                    edge_id, attributes = CLIParser._parse_edit_edge_arguments(command)
                    return EditEdgeCommand(graph, edge_id, attributes)

            case Method.DELETE:
                subject = CLIParser._parse_subject(command)
                if subject == Subject.NODE:
                    node_id = CLIParser._parse_delete_node_arguments(command)
                    return DeleteNodeCommand(graph, node_id)
                elif subject == Subject.EDGE:
                    edge_id = CLIParser._parse_delete_edge_arguments(command)
                    return DeleteEdgeCommand(graph, edge_id)
                elif subject == Subject.GRAPH:
                    return DeleteGraphCommand(graph)

            case Method.FILTER:
                filter_str = re.sub(r'^filter\s+', '', command).strip()
                return FilterCommand(graph, filter_str)

            case Method.SEARCH:
                query = CLIParser._parse_search_arguments(command)
                return SearchCommand(graph, query)

        return None

    @staticmethod
    def _parse_method(command: str) -> Method:
        match_obj = _METHOD_RE.match(command)
        if not match_obj:
            raise CLIParseError(f"Unknown command method in: '{command}'")
        return Method(match_obj.group(1))

    @staticmethod
    def _parse_subject(command: str) -> Subject:
        match_obj = _SUBJECT_RE.match(command)
        if not match_obj:
            raise CLIParseError(f"Unknown command subject in: '{command}'")
        return Subject(match_obj.group(1))

    @staticmethod
    def _parse_id(command: str) -> str:
        match_obj = re.search(r'--id=(\S+)', command)
        if not match_obj:
            raise CLIParseError(f"Missing --id in: '{command}'")
        return match_obj.group(1)

    @staticmethod
    def _parse_attributes(command: str) -> Dict[str, AttributeValue]:
        pairs = re.findall(r'--attribute\s+([a-zA-Z_]\w*)=(\S+)', command)
        return {name: _infer_type(raw) for name, raw in pairs}

    @staticmethod
    def _parse_search_arguments(command: str) -> str:
        match_obj = re.match(r'search\s+(.+)', command.strip())
        if not match_obj:
            raise CLIParseError(
                f"Invalid search syntax: '{command}'. Expected: search <query>"
            )
        return match_obj.group(1).strip()

    @staticmethod
    def _parse_create_node_arguments(command: str) -> Tuple[str, Dict[str, AttributeValue]]:
        node_id = CLIParser._parse_id(command)
        attributes = CLIParser._parse_attributes(command)
        return node_id, attributes

    @staticmethod
    def _parse_edit_node_arguments(command: str) -> Tuple[str, Dict[str, AttributeValue]]:
        node_id = CLIParser._parse_id(command)
        attributes = CLIParser._parse_attributes(command)
        if not attributes:
            raise CLIParseError(f"edit node requires at least one --attribute in: '{command}'")
        return node_id, attributes

    @staticmethod
    def _parse_delete_node_arguments(command: str) -> str:
        return CLIParser._parse_id(command)

    @staticmethod
    def _parse_create_edge_arguments(command: str) -> Tuple[str, str, str, Dict[str, AttributeValue]]:
        edge_id = CLIParser._parse_id(command)

        source_match = re.search(r'--source=(\S+)', command)
        target_match = re.search(r'--target=(\S+)', command)

        if not source_match:
            raise CLIParseError(f"Missing --source in: '{command}'")
        if not target_match:
            raise CLIParseError(f"Missing --target in: '{command}'")

        attributes = CLIParser._parse_attributes(command)
        return edge_id, source_match.group(1), target_match.group(1), attributes

    @staticmethod
    def _parse_edit_edge_arguments(command: str) -> Tuple[str, Dict[str, AttributeValue]]:
        edge_id = CLIParser._parse_id(command)
        attributes = CLIParser._parse_attributes(command)
        if not attributes:
            raise CLIParseError(f"edit edge requires at least one --attribute in: '{command}'")
        return edge_id, attributes

    @staticmethod
    def _parse_delete_edge_arguments(command: str) -> str:
        return CLIParser._parse_id(command)
