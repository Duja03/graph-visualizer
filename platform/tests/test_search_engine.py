import pytest
from datetime import date

from api.model import Graph, Node, Edge
from core import SearchEngine


@pytest.fixture
def sample_graph():
    g = Graph(directed=True)

    n1 = Node(id="1")
    n1.set_attribute("name", "Alice")
    n1.set_attribute("age", 30)
    n1.set_attribute("city", "Belgrade")
    n1.set_attribute("salary", 3500.5)
    n1.set_attribute("joined", date(2020, 1, 15))

    n2 = Node(id="2")
    n2.set_attribute("name", "Bob")
    n2.set_attribute("age", 25)
    n2.set_attribute("city", "Novi Sad")
    n2.set_attribute("salary", 2800.0)
    n2.set_attribute("joined", date(2021, 6, 1))

    n3 = Node(id="3")
    n3.set_attribute("name", "Charlie")
    n3.set_attribute("age", 40)
    n3.set_attribute("city", "Belgrade")
    n3.set_attribute("salary", 4200.75)
    n3.set_attribute("joined", date(2019, 3, 22))

    g.add_node(n1)
    g.add_node(n2)
    g.add_node(n3)

    g.add_edge(Edge(id="e1", source="1", target="2"))
    g.add_edge(Edge(id="e2", source="2", target="3"))
    g.add_edge(Edge(id="e3", source="3", target="1"))

    return g


# ====== match by string value ======

def test_search_exact_name(sample_graph):
    result = SearchEngine(sample_graph).search("Alice")
    ids = {n.id for n in result}
    assert ids == {"1"}

def test_search_partial_name(sample_graph):
    result = SearchEngine(sample_graph).search("lic")   # inside "Alice"
    ids = {n.id for n in result}
    assert ids == {"1"}

def test_search_case_insensitive(sample_graph):
    result = SearchEngine(sample_graph).search("alice")
    ids = {n.id for n in result}
    assert ids == {"1"}

def test_search_city_multiple_nodes(sample_graph):
    result = SearchEngine(sample_graph).search("Belgrade")
    ids = {n.id for n in result}
    assert ids == {"1", "3"}   # Alice and Charlie

def test_search_city_partial(sample_graph):
    result = SearchEngine(sample_graph).search("Novi")
    ids = {n.id for n in result}
    assert ids == {"2"}   # only Bob


# ====== match by numeric value ======

def test_search_integer_value(sample_graph):
    result = SearchEngine(sample_graph).search("25")
    ids = {n.id for n in result}
    assert ids == {"2"}   # Bob has age=25

def test_search_float_value(sample_graph):
    result = SearchEngine(sample_graph).search("4200.75")
    ids = {n.id for n in result}
    assert ids == {"3"}   # Charlie has salary=4200.75

def test_search_partial_number(sample_graph):
    result = SearchEngine(sample_graph).search("3500")
    ids = {n.id for n in result}
    assert ids == {"1"}   # Alice has salary=3500.5


# ====== match by date value ======

def test_search_full_date(sample_graph):
    result = SearchEngine(sample_graph).search("2020-01-15")
    ids = {n.id for n in result}
    assert ids == {"1"}   # Alice joined 2020-01-15

def test_search_partial_date_year(sample_graph):
    result = SearchEngine(sample_graph).search("2021")
    ids = {n.id for n in result}
    assert ids == {"2"}   # Bob joined 2021-06-01

def test_search_partial_date_month(sample_graph):
    result = SearchEngine(sample_graph).search("03-22")
    ids = {n.id for n in result}
    assert ids == {"3"}   # Charlie joined 2019-03-22


# ====== match by attribute key ======

def test_search_attribute_key_exact(sample_graph):
    result = SearchEngine(sample_graph).search("salary")   # all have salary
    ids = {n.id for n in result}
    assert ids == {"1", "2", "3"}

def test_search_attribute_key_partial(sample_graph):
    result = SearchEngine(sample_graph).search("joi")   # "joined" key — all nodes
    ids = {n.id for n in result}
    assert ids == {"1", "2", "3"}

def test_search_attribute_key_unique(sample_graph):
    # add a node with a unique key
    g = Graph(directed=True)
    n = Node(id="x")
    n.set_attribute("passport_number", "ABC123")
    g.add_node(n)
    result = SearchEngine(g).search("passport")
    ids = {n.id for n in result}
    assert ids == {"x"}


# ====== empty result ======

def test_search_no_match(sample_graph):
    result = SearchEngine(sample_graph).search("xyz_not_found")
    assert result.node_count() == 0
    assert result.edge_count() == 0


# ====== edge preservation ======

def test_search_edges_between_matched_nodes_preserved(sample_graph):
    # Belgrade matches n1 and n3; e3 connects 3->1
    result = SearchEngine(sample_graph).search("Belgrade")
    assert "e3" in result.edges

def test_search_edges_to_unmatched_nodes_dropped(sample_graph):
    # Belgrade matches n1 and n3; n2 not matched so e1(1->2) and e2(2->3) dropped
    result = SearchEngine(sample_graph).search("Belgrade")
    assert "e1" not in result.edges
    assert "e2" not in result.edges

def test_search_no_edges_when_single_node_matched(sample_graph):
    result = SearchEngine(sample_graph).search("Alice")
    assert result.edge_count() == 0

def test_search_all_edges_preserved_when_all_match(sample_graph):
    result = SearchEngine(sample_graph).search("age")   # all nodes have "age" key
    assert result.edge_count() == 3


# ====== graph properties ======

def test_search_preserves_directed_flag(sample_graph):
    result = SearchEngine(sample_graph).search("Alice")
    assert result.directed is True

def test_search_preserves_undirected_flag():
    g = Graph(directed=False)
    n = Node(id="1")
    n.set_attribute("name", "Alice")
    g.add_node(n)
    result = SearchEngine(g).search("Alice")
    assert result.directed is False


# ====== edge cases ======

def test_search_empty_query_raises(sample_graph):
    with pytest.raises(ValueError):
        SearchEngine(sample_graph).search("")

def test_search_whitespace_only_raises(sample_graph):
    with pytest.raises(ValueError):
        SearchEngine(sample_graph).search("   ")

def test_search_empty_graph():
    result = SearchEngine(Graph(directed=True)).search("anything")
    assert result.node_count() == 0
    assert result.edge_count() == 0

def test_search_node_with_no_attributes_does_not_match():
    g = Graph(directed=True)
    g.add_node(Node(id="1"))
    result = SearchEngine(g).search("anything")
    assert result.node_count() == 0