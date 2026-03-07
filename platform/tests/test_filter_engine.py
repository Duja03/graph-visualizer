import pytest
from datetime import date
from api.model import Graph, Node, Edge
from core import FilterEngine, FilterError


@pytest.fixture
def sample_graph():
    graph = Graph(directed=True)

    n1 = Node(id="1")
    n1.set_attribute("name", "Alice")
    n1.set_attribute("age", 30)
    n1.set_attribute("city", "Berlin")
    n1.set_attribute("salary", 3500.5)
    n1.set_attribute("joined", date(2020, 1, 15))

    n2 = Node(id="2")
    n2.set_attribute("name", "Bob")
    n2.set_attribute("age", 25)
    n2.set_attribute("city", "Paris")
    n2.set_attribute("salary", 2800.0)
    n2.set_attribute("joined", date(2021, 6, 1))

    n3 = Node(id="3")
    n3.set_attribute("name", "Carol")
    n3.set_attribute("age", 40)
    n3.set_attribute("city", "Berlin")
    n3.set_attribute("salary", 4200.75)
    n3.set_attribute("joined", date(2019, 3, 22))

    graph.add_node(n1)
    graph.add_node(n2)
    graph.add_node(n3)

    graph.add_edge(Edge(id="e1", source="1", target="2"))
    graph.add_edge(Edge(id="e2", source="2", target="3"))
    graph.add_edge(Edge(id="e3", source="3", target="1"))

    return graph


# ====== int filters ======

def test_filter_age_greater_than(sample_graph):
    result = FilterEngine.filter(sample_graph, "age > 25")
    ids = {n.id for n in result}
    assert ids == {"1", "3"}  # Alice(30) and Carol(40)

def test_filter_age_equals(sample_graph):
    result = FilterEngine.filter(sample_graph, "age == 30")
    ids = {n.id for n in result}
    assert ids == {"1"}  # only Alice

def test_filter_age_less_than(sample_graph):
    result = FilterEngine.filter(sample_graph, "age < 30")
    ids = {n.id for n in result}
    assert ids == {"2"}  # only Bob

def test_filter_age_not_equals(sample_graph):
    result = FilterEngine.filter(sample_graph, "age != 30")
    ids = {n.id for n in result}
    assert ids == {"2", "3"}  # Bob and Carol


# ====== float filters ======

def test_filter_salary_greater_than(sample_graph):
    result = FilterEngine.filter(sample_graph, "salary > 3000.0")
    ids = {n.id for n in result}
    assert ids == {"1", "3"}  # Alice and Carol

def test_filter_salary_less_than_or_equal(sample_graph):
    result = FilterEngine.filter(sample_graph, "salary <= 2800.0")
    ids = {n.id for n in result}
    assert ids == {"2"}  # only Bob


# ====== string filters ======

def test_filter_city_equals(sample_graph):
    result = FilterEngine.filter(sample_graph, "city == Berlin")
    ids = {n.id for n in result}
    assert ids == {"1", "3"}  # Alice and Carol

def test_filter_city_not_equals(sample_graph):
    result = FilterEngine.filter(sample_graph, "city != Berlin")
    ids = {n.id for n in result}
    assert ids == {"2"}  # only Bob


# ====== date filters ======

def test_filter_joined_after(sample_graph):
    result = FilterEngine.filter(sample_graph, "joined > 2020-01-01")
    ids = {n.id for n in result}
    assert ids == {"1", "2"}  # Alice and Bob

def test_filter_joined_equals(sample_graph):
    result = FilterEngine.filter(sample_graph, "joined == 2020-01-15")
    ids = {n.id for n in result}
    assert ids == {"1"}  # only Alice


# ====== empty result ======

def test_filter_no_results(sample_graph):
    result = FilterEngine.filter(sample_graph, "age > 100")
    assert result.node_count() == 0
    assert result.edge_count() == 0


# ====== non-existing attribute ======

def test_filter_missing_attribute(sample_graph):
    result = FilterEngine.filter(sample_graph, "height > 170")
    assert result.node_count() == 0


# ====== faults ======

def test_filter_invalid_format(sample_graph):
    with pytest.raises(FilterError):
        FilterEngine.filter(sample_graph, "age 30")

def test_filter_type_mismatch(sample_graph):
    with pytest.raises(FilterError):
        FilterEngine.filter(sample_graph, "age > Berlin")