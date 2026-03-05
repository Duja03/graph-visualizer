import pytest
from datetime import date
from pathlib import Path
import csv

from csv_datasource.src.csv_datasource.csv_datasource_plugin import CsvDataSourcePlugin, _parse_typed_value


# ====== _parse_typed_value tests ======

def test_parse_int():
    assert _parse_typed_value("42") == 42
    assert isinstance(_parse_typed_value("42"), int)

def test_parse_negative_int():
    assert _parse_typed_value("-10") == -10

def test_parse_float():
    assert _parse_typed_value("3500.5") == 3500.5
    assert isinstance(_parse_typed_value("3500.5"), float)

def test_parse_date():
    assert _parse_typed_value("2020-01-15") == date(2020, 1, 15)

def test_parse_string():
    assert _parse_typed_value("Berlin") == "Berlin"

def test_parse_empty():
    assert _parse_typed_value("") is None

def test_parse_none():
    assert _parse_typed_value(None) is None

def test_parse_bool():
    assert _parse_typed_value(True) == "True"
    assert isinstance(_parse_typed_value(True), str)


# ====== helpers ======

def make_csv(rows: list, tmp_path: Path, edge_column="connected_to") -> Path:
    fieldnames = ["id", "name", "age", "salary", "joined", edge_column]
    p = tmp_path / "tests.csv"
    with open(p, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return p


# ====== plugin tests ======

@pytest.fixture
def plugin():
    return CsvDataSourcePlugin()


def test_plugin_id(plugin):
    assert plugin.plugin_id() == "csv_data_source"

def test_plugin_name(plugin):
    assert plugin.name() == "CSV Data Source"

def test_plugin_parameters(plugin):
    params = plugin.parameters()
    assert "file_path" in params
    assert "edge_column" in params


def test_load_nodes(plugin, tmp_path):
    p = make_csv([
        {"id": "1", "name": "Alice", "age": "30", "salary": "3500.5", "joined": "2020-01-15", "connected_to": ""},
        {"id": "2", "name": "Bob",   "age": "25", "salary": "2800.0", "joined": "2021-06-01", "connected_to": ""},
    ], tmp_path)

    graph = plugin.load(file_path=str(p))

    assert graph.node_count() == 2
    assert graph.has_node("1")
    assert graph.has_node("2")


def test_load_attribute_types(plugin, tmp_path):
    p = make_csv([
        {"id": "1", "name": "Alice", "age": "30", "salary": "3500.5", "joined": "2020-01-15", "connected_to": ""},
    ], tmp_path)

    graph = plugin.load(file_path=str(p))
    node = graph.get_node("1")

    assert node.get_attribute("age") == 30
    assert isinstance(node.get_attribute("age"), int)

    assert node.get_attribute("salary") == 3500.5
    assert isinstance(node.get_attribute("salary"), float)

    assert node.get_attribute("joined") == date(2020, 1, 15)
    assert isinstance(node.get_attribute("joined"), date)

    assert node.get_attribute("name") == "Alice"
    assert isinstance(node.get_attribute("name"), str)


def test_load_edges(plugin, tmp_path):
    p = make_csv([
        {"id": "1", "name": "Alice", "age": "30", "salary": "", "joined": "", "connected_to": "2"},
        {"id": "2", "name": "Bob",   "age": "25", "salary": "", "joined": "", "connected_to": ""},
    ], tmp_path)

    graph = plugin.load(file_path=str(p))

    assert graph.edge_count() == 1
    edge = list(graph.iter_edges())[0]
    assert edge.source == "1"
    assert edge.target == "2"


def test_cyclic_graph(plugin, tmp_path):
    p = make_csv([
        {"id": "1", "name": "Alice", "age": "", "salary": "", "joined": "", "connected_to": "2"},
        {"id": "2", "name": "Bob",   "age": "", "salary": "", "joined": "", "connected_to": "3"},
        {"id": "3", "name": "Carol", "age": "", "salary": "", "joined": "", "connected_to": "1"},
    ], tmp_path)

    graph = plugin.load(file_path=str(p))

    assert graph.node_count() == 3
    assert graph.edge_count() == 3

    neighbors_1 = [n.id for n in graph.neighbors("1")]
    assert "2" in neighbors_1

    neighbors_2 = [n.id for n in graph.neighbors("2")]
    assert "3" in neighbors_2

    neighbors_3 = [n.id for n in graph.neighbors("3")]
    assert "1" in neighbors_3


def test_missing_file(plugin):
    with pytest.raises(ValueError, match="CSV file not found"):
        plugin.load(file_path="non-existing-file.csv")


def test_missing_file_path_param(plugin):
    with pytest.raises(ValueError, match="Missing parameter"):
        plugin.load()


def test_skip_row_without_id(plugin, tmp_path):
    p = tmp_path / "tests.csv"
    with open(p, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "connected_to"])
        writer.writeheader()
        writer.writerow({"id": "",    "name": "Ghost", "connected_to": ""})
        writer.writerow({"id": "1",   "name": "Alice", "connected_to": ""})

    graph = plugin.load(file_path=str(p))
    assert graph.node_count() == 1
    assert graph.has_node("1")


def test_multiple_edges(plugin, tmp_path):
    p = tmp_path / "tests.csv"
    with open(p, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "connected_to"])
        writer.writeheader()
        writer.writerow({"id": "1", "name": "Alice", "connected_to": "2;3"})
        writer.writerow({"id": "2", "name": "Bob",   "connected_to": ""})
        writer.writerow({"id": "3", "name": "Carol", "connected_to": ""})

    graph = plugin.load(file_path=str(p))
    assert graph.edge_count() == 2