import pytest
from datetime import date
from pathlib import Path

from xml_datasource.src.xml_datasource.xml_datasource_plugin import XmlDataSourcePlugin, _parse_typed_value


def test_parse_int():
    assert _parse_typed_value("42") == 42
    assert isinstance(_parse_typed_value("42"), int)

def test_parse_negative_int():
    assert _parse_typed_value("-10") == -10

def test_parse_float():
    assert _parse_typed_value("3.14") == 3.14
    assert isinstance(_parse_typed_value("3.14"), float)

def test_parse_date():
    assert _parse_typed_value("2020-01-15") == date(2020, 1, 15)

def test_parse_string():
    assert _parse_typed_value("Berlin") == "Berlin"

def test_parse_empty():
    assert _parse_typed_value("") is None

def test_parse_none():
    assert _parse_typed_value(None) is None

def test_parse_whitespace_only():
    assert _parse_typed_value("   ") is None


def write_xml(content: str, tmp_path: Path) -> Path:
    p = tmp_path / "tests.xml"
    p.write_text(content, encoding="utf-8")
    return p

@pytest.fixture
def plugin():
    return XmlDataSourcePlugin()

def test_plugin_id(plugin):
    assert plugin.plugin_id() == "xml_datasource"

def test_plugin_name(plugin):
    assert plugin.name() == "XML Data Source"

def test_plugin_parameters(plugin):
    params = plugin.parameters()
    assert "file_path" in params

def test_load_single_node(plugin, tmp_path):
    xml = """<root>
        <Person xml:id="p1">
            <name>Alice</name>
        </Person>
    </root>"""
    p = write_xml(xml, tmp_path)
    graph = plugin.load(file_path=str(p))
    assert graph.has_node("p1")

def test_load_multiple_nodes(plugin, tmp_path):
    xml = """<root>
        <Person xml:id="p1"><name>Alice</name></Person>
        <Person xml:id="p2"><name>Bob</name></Person>
    </root>"""
    p = write_xml(xml, tmp_path)
    graph = plugin.load(file_path=str(p))
    assert graph.has_node("p1")
    assert graph.has_node("p2")

def test_node_tag_attribute(plugin, tmp_path):
    xml = """<root>
        <Person xml:id="p1"><name>Alice</name></Person>
    </root>"""
    p = write_xml(xml, tmp_path)
    graph = plugin.load(file_path=str(p))
    node = graph.get_node("p1")
    assert node.get_attribute("_tag") == "Person"

def test_load_scalar_attributes(plugin, tmp_path):
    xml = """<root>
        <Person xml:id="p1" age="30" salary="3500.5" joined="2020-01-15" city="Berlin"/>
    </root>"""
    p = write_xml(xml, tmp_path)
    graph = plugin.load(file_path=str(p))
    node = graph.get_node("p1")

    assert node.get_attribute("age") == 30
    assert isinstance(node.get_attribute("age"), int)

    assert node.get_attribute("salary") == 3500.5
    assert isinstance(node.get_attribute("salary"), float)

    assert node.get_attribute("joined") == date(2020, 1, 15)
    assert isinstance(node.get_attribute("joined"), date)

    assert node.get_attribute("city") == "Berlin"
    assert isinstance(node.get_attribute("city"), str)

def test_leaf_text_becomes_attribute(plugin, tmp_path):
    xml = """<root>
        <Person xml:id="p1">
            <name>Alice</name>
            <age>30</age>
        </Person>
    </root>"""
    p = write_xml(xml, tmp_path)
    graph = plugin.load(file_path=str(p))
    node = graph.get_node("p1")
    assert node.get_attribute("name") == "Alice"
    assert node.get_attribute("age") == 30

def test_child_with_subtree_becomes_edge(plugin, tmp_path):
    xml = """<root xml:id="r">
        <Address xml:id="a1">
            <street>Main St</street>
        </Address>
    </root>"""
    p = write_xml(xml, tmp_path)
    graph = plugin.load(file_path=str(p))
    assert graph.has_node("r")
    assert graph.has_node("a1")
    assert graph.edge_count() >= 1

def test_reference_creates_edge(plugin, tmp_path):
    xml = """<root>
        <Person xml:id="p1"><name>Alice</name></Person>
        <Person xml:id="p2" reference="p1"><name>Bob</name></Person>
    </root>"""
    p = write_xml(xml, tmp_path)
    graph = plugin.load(file_path=str(p))

    edges = list(graph.iter_edges())
    ref_edges = [e for e in edges if e.attributes.get("name") == "reference"]
    assert any(e.source == "p2" and e.target == "p1" for e in ref_edges)

def test_cyclic_graph_via_reference(plugin, tmp_path):
    xml = """<root>
        <Person xml:id="p1">
            <name>Alice</name>
            <friend reference="p2"/>
        </Person>
        <Person xml:id="p2">
            <name>Bob</name>
            <friend reference="p1"/>
        </Person>
    </root>"""
    p = write_xml(xml, tmp_path)
    graph = plugin.load(file_path=str(p))

    assert graph.has_node("p1")
    assert graph.has_node("p2")

    edges = list(graph.iter_edges())

    reachable_from_p1 = {e.target for e in edges if e.source == "p1"}
    reachable_from_p2 = {e.target for e in edges if e.source == "p2"}

    assert any("p2" in {e2.target for e2 in edges if e2.source == mid} for mid in reachable_from_p1)
    assert any("p1" in {e2.target for e2 in edges if e2.source == mid} for mid in reachable_from_p2)

def test_self_closing_with_attributes_becomes_node(plugin, tmp_path):
    xml = """<root>
        <Person xml:id="p1" age="30" city="Berlin"/>
    </root>"""
    p = write_xml(xml, tmp_path)
    graph = plugin.load(file_path=str(p))
    assert graph.has_node("p1")
    node = graph.get_node("p1")
    assert node.get_attribute("age") == 30

def test_attributes_create_value_nodes_and_edges(plugin, tmp_path):
    xml = """<root>
        <Person xml:id="p1" age="30"/>
    </root>"""
    p = write_xml(xml, tmp_path)
    graph = plugin.load(file_path=str(p))

    edges = list(graph.iter_edges())
    age_edges = [e for e in edges if e.attributes.get("name") == "age"]
    assert len(age_edges) == 1

    value_node = graph.get_node(age_edges[0].target)
    assert value_node.get_attribute("value") == 30

def test_missing_file(plugin):
    with pytest.raises(ValueError, match="XML file not found"):
        plugin.load(file_path="non-existing-file.xml")

def test_missing_file_path_param(plugin):
    with pytest.raises(ValueError, match="Missing parameter"):
        plugin.load()

def test_invalid_xml(plugin, tmp_path):
    p = tmp_path / "bad.xml"
    p.write_text("<root><unclosed>", encoding="utf-8")
    with pytest.raises(ValueError, match="XML parse error"):
        plugin.load(file_path=str(p))

def test_auto_generated_node_ids(plugin, tmp_path):
    """Nodes without xml:id should still be added with auto-generated IDs."""
    xml = """<root>
        <Person>
            <name>Ghost</name>
        </Person>
    </root>"""
    p = write_xml(xml, tmp_path)
    graph = plugin.load(file_path=str(p))
    assert graph.node_count() >= 1

def test_reference_to_unknown_id_ignored(plugin, tmp_path):
    """A reference to a non-existent xml:id should not crash."""
    xml = """<root>
        <Person xml:id="p1" reference="nonexistent"><name>Alice</name></Person>
    </root>"""
    p = write_xml(xml, tmp_path)
    graph = plugin.load(file_path=str(p))
    assert graph.has_node("p1")

def test_xml_id_not_stored_as_attribute(plugin, tmp_path):
    """xml:id and reference attributes should not appear as node attributes."""
    xml = """<root>
        <Person xml:id="p1" reference="p2" age="25"/>
        <Person xml:id="p2" age="30"/>
    </root>"""
    p = write_xml(xml, tmp_path)
    graph = plugin.load(file_path=str(p))
    node = graph.get_node("p1")
    assert node.get_attribute("xml:id") is None
    assert node.get_attribute("reference") is None
    assert node.get_attribute("age") == 25

def test_plugin_is_stateless_across_loads(plugin, tmp_path):
    """Calling load() twice should not accumulate state from previous call."""
    xml = """<root>
        <Person xml:id="p1"><name>Alice</name></Person>
    </root>"""
    p = write_xml(xml, tmp_path)

    graph1 = plugin.load(file_path=str(p))
    graph2 = plugin.load(file_path=str(p))

    assert graph1.node_count() == graph2.node_count()
    assert graph1.edge_count() == graph2.edge_count()

def test_deep_nested_structure(plugin, tmp_path):
    xml = """<company xml:id="c1">
        <department xml:id="d1">
            <employee xml:id="e1">
                <name>Alice</name>
            </employee>
        </department>
    </company>"""
    p = write_xml(xml, tmp_path)
    graph = plugin.load(file_path=str(p))

    assert graph.has_node("c1")
    assert graph.has_node("d1")
    assert graph.has_node("e1")

    edges = list(graph.iter_edges())
    sources_targets = {(e.source, e.target) for e in edges}
    assert ("c1", "d1") in sources_targets
    assert ("d1", "e1") in sources_targets

def test_load_scalar_attributes_create_value_nodes(plugin, tmp_path):
    xml = """<root>
        <Person xml:id="p1" age="30" salary="3500.5" joined="2020-01-15" city="Berlin"/>
    </root>"""
    p = write_xml(xml, tmp_path)
    graph = plugin.load(file_path=str(p))

    edges = list(graph.iter_edges())

    age_edges = [e for e in edges if e.attributes.get("name") == "age"]
    assert len(age_edges) == 1
    assert graph.get_node(age_edges[0].target).get_attribute("value") == 30

    salary_edges = [e for e in edges if e.attributes.get("name") == "salary"]
    assert len(salary_edges) == 1
    assert graph.get_node(salary_edges[0].target).get_attribute("value") == 3500.5

    joined_edges = [e for e in edges if e.attributes.get("name") == "joined"]
    assert len(joined_edges) == 1
    assert graph.get_node(joined_edges[0].target).get_attribute("value") == date(2020, 1, 15)

    city_edges = [e for e in edges if e.attributes.get("name") == "city"]
    assert len(city_edges) == 1
    assert graph.get_node(city_edges[0].target).get_attribute("value") == "Berlin"


def test_self_closing_without_id_becomes_node(plugin, tmp_path):
    xml = """<root>
        <Person age="30" city="Berlin"/>
    </root>"""
    p = write_xml(xml, tmp_path)
    graph = plugin.load(file_path=str(p))

    # treba biti kreiran bar jedan cvor osim root-a
    assert graph.node_count() >= 2

    # treba postojati grana za age i city
    edges = list(graph.iter_edges())
    attr_edge_names = {e.attributes.get("name") for e in edges}
    assert "age" in attr_edge_names
    assert "city" in attr_edge_names


def test_self_closing_with_id_and_multiple_attributes_creates_edges(plugin, tmp_path):
    xml = """<root>
        <Car xml:id="c1" brand="Toyota" year="2020" price="25000.0"/>
    </root>"""
    p = write_xml(xml, tmp_path)
    graph = plugin.load(file_path=str(p))

    assert graph.has_node("c1")
    node = graph.get_node("c1")
    assert node.get_attribute("brand") == "Toyota"
    assert node.get_attribute("year") == 2020
    assert node.get_attribute("price") == 25000.0

    edges = list(graph.iter_edges())
    edge_names = {e.attributes.get("name") for e in edges if e.source == "c1"}
    assert "brand" in edge_names
    assert "year" in edge_names
    assert "price" in edge_names


def test_value_nodes_are_separate_from_element_nodes(plugin, tmp_path):
    xml = """<root>
        <Person xml:id="p1" age="30"/>
    </root>"""
    p = write_xml(xml, tmp_path)
    graph = plugin.load(file_path=str(p))

    edges = list(graph.iter_edges())
    age_edges = [e for e in edges if e.attributes.get("name") == "age"]
    assert len(age_edges) == 1

    value_node_id = age_edges[0].target
    assert value_node_id != "p1"
    assert graph.has_node(value_node_id)


def test_multiple_nodes_each_create_their_own_value_nodes(plugin, tmp_path):
    xml = """<root>
        <Person xml:id="p1" age="30"/>
        <Person xml:id="p2" age="25"/>
    </root>"""
    p = write_xml(xml, tmp_path)
    graph = plugin.load(file_path=str(p))

    edges = list(graph.iter_edges())

    age_edges_p1 = [e for e in edges if e.source == "p1" and e.attributes.get("name") == "age"]
    age_edges_p2 = [e for e in edges if e.source == "p2" and e.attributes.get("name") == "age"]

    assert len(age_edges_p1) == 1
    assert len(age_edges_p2) == 1

    # value nodovi moraju biti razliciti
    assert age_edges_p1[0].target != age_edges_p2[0].target

    assert graph.get_node(age_edges_p1[0].target).get_attribute("value") == 30
    assert graph.get_node(age_edges_p2[0].target).get_attribute("value") == 25


def test_xml_id_and_reference_dont_create_value_nodes(plugin, tmp_path):
    xml = """<root>
        <Person xml:id="p1" reference="p2" age="25"/>
        <Person xml:id="p2" age="30"/>
    </root>"""
    p = write_xml(xml, tmp_path)
    graph = plugin.load(file_path=str(p))

    edges = list(graph.iter_edges())
    edge_names = {e.attributes.get("name") for e in edges}

    assert "xml:id" not in edge_names
    assert "{http://www.w3.org/XML/1998/namespace}id" not in edge_names