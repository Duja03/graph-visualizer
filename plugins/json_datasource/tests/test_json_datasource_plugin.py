import pytest
from datetime import date
from pathlib import Path
import json

from json_datasource.json_datasource_plugin import JsonDataSourcePlugin, _parse_typed_value


# ====== _parse_typed_value tests ======

def test_parse_int():
    assert _parse_typed_value(42) == 42
    assert isinstance(_parse_typed_value(42), int)

def test_parse_negative_int():
    assert _parse_typed_value(-7) == -7
    assert isinstance(_parse_typed_value(-7), int)

def test_parse_float():
    assert _parse_typed_value(3.14) == 3.14
    assert isinstance(_parse_typed_value(3.14), float)

def test_parse_int_string():
    assert _parse_typed_value("100") == 100
    assert isinstance(_parse_typed_value("100"), int)

def test_parse_negative_int_string():
    assert _parse_typed_value("-5") == -5
    assert isinstance(_parse_typed_value("-5"), int)

def test_parse_float_string():
    assert _parse_typed_value("3.14") == 3.14
    assert isinstance(_parse_typed_value("3.14"), float)

def test_parse_float_scientific():
    assert _parse_typed_value("1.5e3") == 1500.0
    assert isinstance(_parse_typed_value("1.5e3"), float)

def test_parse_date():
    assert _parse_typed_value("2020-01-15") == date(2020, 1, 15)
    assert isinstance(_parse_typed_value("2020-01-15"), date)

def test_parse_invalid_date_returns_string():
    result = _parse_typed_value("2020-99-99")
    assert isinstance(result, str)

def test_parse_string():
    assert _parse_typed_value("hello") == "hello"
    assert isinstance(_parse_typed_value("hello"), str)

def test_parse_none():
    assert _parse_typed_value(None) is None

def test_parse_bool_true():
    assert _parse_typed_value(True) == "True"
    assert isinstance(_parse_typed_value(True), str)

def test_parse_bool_false():
    assert _parse_typed_value(False) == "False"
    assert isinstance(_parse_typed_value(False), str)

def test_parse_whitespace_stripped():
    assert _parse_typed_value("  hello  ") == "hello"


# ====== helpers ======

def make_json(data: dict, tmp_path: Path) -> Path:
    p = tmp_path / "test.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


# ====== plugin metadata tests ======

@pytest.fixture
def plugin():
    return JsonDataSourcePlugin()


def test_plugin_id(plugin):
    assert plugin.plugin_id() == "json_datasource"

def test_plugin_name(plugin):
    assert plugin.name() == "JSON Data Source"

def test_plugin_static_identifier(plugin):
    assert JsonDataSourcePlugin.static_identifier == "JSON"

def test_plugin_parameters(plugin):
    assert "file_path" in plugin.parameters()

def test_missing_file_path_param(plugin):
    with pytest.raises(ValueError, match="file_path"):
        plugin.load()

def test_missing_file(plugin):
    with pytest.raises(ValueError, match="not found"):
        plugin.load(file_path="non_existing_file.json")


# ====== node loading tests ======

def test_load_single_node(plugin, tmp_path):
    p = make_json({"@id": "n1", "name": "Alice"}, tmp_path)
    graph = plugin.load(file_path=str(p))
    assert graph.has_node("n1")

def test_load_multiple_nodes(plugin, tmp_path):
    p = make_json({
        "@id": "parent",
        "child": {"@id": "child1", "v": 1}
    }, tmp_path)
    graph = plugin.load(file_path=str(p))
    assert graph.has_node("parent")
    assert graph.has_node("child1")

def test_root_node_always_created(plugin, tmp_path):
    p = make_json({}, tmp_path)
    graph = plugin.load(file_path=str(p))
    assert graph.has_node("root")

def test_node_without_id_gets_auto_id(plugin, tmp_path):
    p = make_json({"@id": "n1", "child": {"name": "no_id"}}, tmp_path)
    graph = plugin.load(file_path=str(p))
    assert graph.node_count() >= 2


# ====== attribute type tests ======

def test_attribute_int(plugin, tmp_path):
    p = make_json({"@id": "n1", "age": 30}, tmp_path)
    graph = plugin.load(file_path=str(p))
    val = graph.get_node("n1").get_attribute("age")
    assert val == 30
    assert isinstance(val, int)

def test_attribute_float(plugin, tmp_path):
    p = make_json({"@id": "n1", "score": 4.5}, tmp_path)
    graph = plugin.load(file_path=str(p))
    val = graph.get_node("n1").get_attribute("score")
    assert val == 4.5
    assert isinstance(val, float)

def test_attribute_string(plugin, tmp_path):
    p = make_json({"@id": "n1", "name": "Alice"}, tmp_path)
    graph = plugin.load(file_path=str(p))
    val = graph.get_node("n1").get_attribute("name")
    assert val == "Alice"
    assert isinstance(val, str)

def test_attribute_date(plugin, tmp_path):
    p = make_json({"@id": "n1", "joined": "2020-06-15"}, tmp_path)
    graph = plugin.load(file_path=str(p))
    val = graph.get_node("n1").get_attribute("joined")
    assert val == date(2020, 6, 15)
    assert isinstance(val, date)

def test_attribute_bool_stored_as_string(plugin, tmp_path):
    p = make_json({"@id": "n1", "active": True}, tmp_path)
    graph = plugin.load(file_path=str(p))
    val = graph.get_node("n1").get_attribute("active")
    assert isinstance(val, str)
    assert val == "True"

def test_id_field_not_stored_as_attribute(plugin, tmp_path):
    p = make_json({"@id": "n1", "name": "Alice"}, tmp_path)
    graph = plugin.load(file_path=str(p))
    assert graph.get_node("n1").get_attribute("@id") is None

def test_node_attributes_is_dict(plugin, tmp_path):
    p = make_json({"@id": "n1", "x": 10}, tmp_path)
    graph = plugin.load(file_path=str(p))
    assert isinstance(graph.get_node("n1").attributes, dict)


# ====== edge tests ======

def test_structural_edge_parent_to_child(plugin, tmp_path):
    p = make_json({
        "@id": "parent",
        "child": {"@id": "child1", "v": 1}
    }, tmp_path)
    graph = plugin.load(file_path=str(p))
    edge = next(
        (e for e in graph.iter_edges() if e.source == "parent" and e.target == "child1"),
        None
    )
    assert edge is not None

def test_reference_edge_created_for_known_id(plugin, tmp_path):
    p = make_json({
        "@id": "a",
        "ref": "b",
        "child": {"@id": "b", "v": 1}
    }, tmp_path)
    graph = plugin.load(file_path=str(p))
    ref = next(
        (e for e in graph.iter_edges() if e.source == "a" and e.target == "b"),
        None
    )
    assert ref is not None

def test_unknown_string_does_not_create_edge(plugin, tmp_path):
    p = make_json({"@id": "solo", "label": "not_a_known_id"}, tmp_path)
    graph = plugin.load(file_path=str(p))
    bad = [e for e in graph.iter_edges() if e.target == "not_a_known_id"]
    assert len(bad) == 0

def test_reference_edge_carries_field_name(plugin, tmp_path):
    p = make_json({
        "@id": "a",
        "points_to": "b",
        "child": {"@id": "b", "v": 1}
    }, tmp_path)
    graph = plugin.load(file_path=str(p))
    ref = next(
        (e for e in graph.iter_edges() if e.source == "a" and e.target == "b"),
        None
    )
    assert ref is not None
    assert ref.attributes.get("name") == "points_to"

def test_edge_ids_are_unique(plugin, tmp_path):
    p = make_json({
        "@id": "a",
        "c1": {"@id": "b", "v": 1},
        "c2": {"@id": "c", "v": 2}
    }, tmp_path)
    graph = plugin.load(file_path=str(p))
    ids = [e.id for e in graph.iter_edges()]
    assert len(ids) == len(set(ids))

def test_all_edge_ids_start_with_e(plugin, tmp_path):
    p = make_json({
        "@id": "a",
        "child": {"@id": "b", "v": 1}
    }, tmp_path)
    graph = plugin.load(file_path=str(p))
    for edge in graph.iter_edges():
        assert edge.id.startswith("e")

def test_no_self_loops(plugin, tmp_path):
    p = make_json({"@id": "a", "child": {"@id": "b", "v": 1}}, tmp_path)
    graph = plugin.load(file_path=str(p))
    for edge in graph.iter_edges():
        assert edge.source != edge.target

def test_edge_source_and_target_nodes_exist(plugin, tmp_path):
    p = make_json({
        "@id": "a",
        "child": {"@id": "b", "v": 1}
    }, tmp_path)
    graph = plugin.load(file_path=str(p))
    for edge in graph.iter_edges():
        assert graph.has_node(edge.source)
        assert graph.has_node(edge.target)

def test_cyclic_reference_does_not_crash(plugin, tmp_path):
    p = make_json({
        "@id": "x",
        "points_to": "y",
        "child": {"@id": "y", "points_to": "x"}
    }, tmp_path)
    graph = plugin.load(file_path=str(p))
    assert graph.has_node("x")
    assert graph.has_node("y")


# ====== list container tests ======

def test_list_creates_container_node(plugin, tmp_path):
    p = make_json({
        "@id": "root",
        "items": [{"@id": "i1", "v": 1}, {"@id": "i2", "v": 2}]
    }, tmp_path)
    graph = plugin.load(file_path=str(p))
    containers = [n for n in graph if n.get_attribute("type") == "list"]
    assert len(containers) >= 1

def test_list_container_ids_are_auto_generated(plugin, tmp_path):
    import re
    p = make_json({
        "@id": "root",
        "items": [{"@id": "i1", "v": 1}]
    }, tmp_path)
    graph = plugin.load(file_path=str(p))
    containers = [n for n in graph if n.get_attribute("type") == "list"]
    pattern = re.compile(r"^n\d+$")
    for c in containers:
        assert pattern.match(c.id)