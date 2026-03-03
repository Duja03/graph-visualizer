import pytest
from datetime import date

from api.model import Graph, Node, Edge
from core import CLIParser, CLIParseError, CLIExecutor
from commands.node_commands import CreateNodeCommand, EditNodeCommand, DeleteNodeCommand
from commands.edge_commands import CreateEdgeCommand, EditEdgeCommand, DeleteEdgeCommand
from commands.graph_commands import DeleteGraphCommand
from commands.filter_commands import FilterCommand
from commands.search_commands import SearchCommand


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def empty_graph():
    return Graph(directed=True)


@pytest.fixture
def sample_graph():
    g = Graph(directed=True)

    n1 = Node(id="1")
    n1.set_attribute("name", "Alice")
    n1.set_attribute("age", 30)
    n1.set_attribute("city", "Belgrade")
    g.add_node(n1)

    n2 = Node(id="2")
    n2.set_attribute("name", "Bob")
    n2.set_attribute("age", 25)
    n2.set_attribute("city", "Novi Sad")
    g.add_node(n2)

    n3 = Node(id="3")
    n3.set_attribute("name", "Carol")
    n3.set_attribute("age", 40)
    n3.set_attribute("city", "Belgrade")
    n3.set_attribute("joined", date(2019, 3, 22))
    g.add_node(n3)

    g.add_edge(Edge(id="e1", source="1", target="2"))
    g.add_edge(Edge(id="e2", source="2", target="3"))

    return g


# ---------------------------------------------------------------------------
# CLIParser — parse() returns correct Command type
# ---------------------------------------------------------------------------

class TestParserCommandType:
    def test_create_node_returns_correct_type(self, sample_graph):
        cmd = CLIParser.parse("create node --id=4 --attribute name=Dave", sample_graph)
        assert isinstance(cmd, CreateNodeCommand)

    def test_edit_node_returns_correct_type(self, sample_graph):
        cmd = CLIParser.parse("edit node --id=1 --attribute age=31", sample_graph)
        assert isinstance(cmd, EditNodeCommand)

    def test_delete_node_returns_correct_type(self, sample_graph):
        cmd = CLIParser.parse("delete node --id=1", sample_graph)
        assert isinstance(cmd, DeleteNodeCommand)

    def test_create_edge_returns_correct_type(self, sample_graph):
        cmd = CLIParser.parse("create edge --id=e3 --source=1 --target=3", sample_graph)
        assert isinstance(cmd, CreateEdgeCommand)

    def test_edit_edge_returns_correct_type(self, sample_graph):
        cmd = CLIParser.parse("edit edge --id=e1 --attribute weight=5", sample_graph)
        assert isinstance(cmd, EditEdgeCommand)

    def test_delete_edge_returns_correct_type(self, sample_graph):
        cmd = CLIParser.parse("delete edge --id=e1", sample_graph)
        assert isinstance(cmd, DeleteEdgeCommand)

    def test_delete_graph_returns_correct_type(self, sample_graph):
        cmd = CLIParser.parse("delete graph", sample_graph)
        assert isinstance(cmd, DeleteGraphCommand)

    def test_filter_returns_correct_type(self, sample_graph):
        cmd = CLIParser.parse("filter age>25", sample_graph)
        assert isinstance(cmd, FilterCommand)

    def test_search_returns_correct_type(self, sample_graph):
        cmd = CLIParser.parse("search Alice", sample_graph)
        assert isinstance(cmd, SearchCommand)


# ---------------------------------------------------------------------------
# CLIParser — parsed arguments are correct
# ---------------------------------------------------------------------------

class TestParserArguments:
    def test_create_node_parses_id(self, sample_graph):
        cmd = CLIParser.parse("create node --id=99", sample_graph)
        assert cmd.node_id == "99"

    def test_create_node_parses_attributes_typed(self, sample_graph):
        cmd = CLIParser.parse(
            "create node --id=99 --attribute name=Dave --attribute age=28 --attribute score=4.5",
            sample_graph
        )
        assert cmd.attributes["name"] == "Dave"
        assert cmd.attributes["age"] == 28
        assert isinstance(cmd.attributes["age"], int)
        assert cmd.attributes["score"] == 4.5
        assert isinstance(cmd.attributes["score"], float)

    def test_create_node_parses_date_attribute(self, sample_graph):
        cmd = CLIParser.parse(
            "create node --id=99 --attribute joined=2023-05-01",
            sample_graph
        )
        assert cmd.attributes["joined"] == date(2023, 5, 1)

    def test_create_node_no_attributes(self, sample_graph):
        cmd = CLIParser.parse("create node --id=99", sample_graph)
        assert cmd.attributes == {}

    def test_edit_node_parses_id_and_attributes(self, sample_graph):
        cmd = CLIParser.parse("edit node --id=1 --attribute age=99", sample_graph)
        assert cmd.node_id == "1"
        assert cmd.attributes["age"] == 99

    def test_delete_node_parses_id(self, sample_graph):
        cmd = CLIParser.parse("delete node --id=2", sample_graph)
        assert cmd.node_id == "2"

    def test_create_edge_parses_all_arguments(self, sample_graph):
        cmd = CLIParser.parse(
            "create edge --id=e3 --source=1 --target=3 --attribute weight=7",
            sample_graph
        )
        assert cmd.edge_id == "e3"
        assert cmd.source == "1"
        assert cmd.target == "3"
        assert cmd.attributes["weight"] == 7

    def test_create_edge_no_attributes(self, sample_graph):
        cmd = CLIParser.parse("create edge --id=e3 --source=1 --target=3", sample_graph)
        assert cmd.attributes == {}

    def test_edit_edge_parses_id_and_attributes(self, sample_graph):
        cmd = CLIParser.parse("edit edge --id=e1 --attribute weight=10", sample_graph)
        assert cmd.edge_id == "e1"
        assert cmd.attributes["weight"] == 10

    def test_delete_edge_parses_id(self, sample_graph):
        cmd = CLIParser.parse("delete edge --id=e1", sample_graph)
        assert cmd.edge_id == "e1"

    def test_filter_parses_filter_str(self, sample_graph):
        cmd = CLIParser.parse("filter age>25", sample_graph)
        assert cmd.filter_str == "age>25"

    def test_filter_parses_equality(self, sample_graph):
        cmd = CLIParser.parse("filter city==Belgrade", sample_graph)
        assert cmd.filter_str == "city==Belgrade"

    def test_search_parses_query(self, sample_graph):
        cmd = CLIParser.parse("search Alice", sample_graph)
        assert cmd.query == "Alice"

    def test_search_parses_partial_query(self, sample_graph):
        cmd = CLIParser.parse("search 2019", sample_graph)
        assert cmd.query == "2019"


# ---------------------------------------------------------------------------
# CLIParser — parse errors
# ---------------------------------------------------------------------------

class TestParserErrors:
    def test_empty_command_raises(self, sample_graph):
        with pytest.raises(CLIParseError):
            CLIParser.parse("", sample_graph)

    def test_whitespace_only_raises(self, sample_graph):
        with pytest.raises(CLIParseError):
            CLIParser.parse("   ", sample_graph)

    def test_unknown_method_raises(self, sample_graph):
        with pytest.raises(CLIParseError):
            CLIParser.parse("fly node --id=1", sample_graph)

    def test_create_node_missing_id_raises(self, sample_graph):
        with pytest.raises(CLIParseError):
            CLIParser.parse("create node --attribute name=Alice", sample_graph)

    def test_edit_node_missing_attribute_raises(self, sample_graph):
        with pytest.raises(CLIParseError):
            CLIParser.parse("edit node --id=1", sample_graph)

    def test_create_edge_missing_source_raises(self, sample_graph):
        with pytest.raises(CLIParseError):
            CLIParser.parse("create edge --id=e3 --target=2", sample_graph)

    def test_create_edge_missing_target_raises(self, sample_graph):
        with pytest.raises(CLIParseError):
            CLIParser.parse("create edge --id=e3 --source=1", sample_graph)

    def test_edit_edge_missing_attribute_raises(self, sample_graph):
        with pytest.raises(CLIParseError):
            CLIParser.parse("edit edge --id=e1", sample_graph)

    def test_search_missing_query_raises(self, sample_graph):
        with pytest.raises(CLIParseError):
            CLIParser.parse("search", sample_graph)


# ---------------------------------------------------------------------------
# CLIExecutor — execute() via full integration
# ---------------------------------------------------------------------------

class TestExecutorCreateNode:
    def test_create_node_adds_to_graph(self, sample_graph):
        cmd = CLIParser.parse("create node --id=4 --attribute name=Dave", sample_graph)
        CLIExecutor.execute(cmd)
        assert sample_graph.has_node("4")
        assert sample_graph.get_node("4").get_attribute("name") == "Dave"

    def test_create_node_typed_attributes(self, sample_graph):
        cmd = CLIParser.parse("create node --id=4 --attribute age=28 --attribute score=9.5", sample_graph)
        CLIExecutor.execute(cmd)
        node = sample_graph.get_node("4")
        assert node.get_attribute("age") == 28
        assert isinstance(node.get_attribute("age"), int)
        assert node.get_attribute("score") == 9.5

    def test_create_node_duplicate_returns_error(self, sample_graph):
        cmd = CLIParser.parse("create node --id=1", sample_graph)  # id=1 already exists
        result = CLIExecutor.execute(cmd)
        assert "Error" in result

    def test_create_node_no_attributes(self, sample_graph):
        cmd = CLIParser.parse("create node --id=4", sample_graph)
        CLIExecutor.execute(cmd)
        assert sample_graph.has_node("4")


class TestExecutorEditNode:
    def test_edit_node_updates_existing_attribute(self, sample_graph):
        cmd = CLIParser.parse("edit node --id=1 --attribute age=99", sample_graph)
        CLIExecutor.execute(cmd)
        assert sample_graph.get_node("1").get_attribute("age") == 99

    def test_edit_node_adds_new_attribute(self, sample_graph):
        cmd = CLIParser.parse("edit node --id=1 --attribute salary=5000", sample_graph)
        CLIExecutor.execute(cmd)
        assert sample_graph.get_node("1").get_attribute("salary") == 5000

    def test_edit_node_nonexistent_returns_error(self, sample_graph):
        cmd = CLIParser.parse("edit node --id=999 --attribute age=1", sample_graph)
        result = CLIExecutor.execute(cmd)
        assert "Error" in result


class TestExecutorDeleteNode:
    def test_delete_node_removes_from_graph(self, sample_graph):
        # first remove edges connected to node 3
        sample_graph.remove_edge("e2")
        cmd = CLIParser.parse("delete node --id=3", sample_graph)
        CLIExecutor.execute(cmd)
        assert not sample_graph.has_node("3")

    def test_delete_node_with_edges_returns_error(self, sample_graph):
        cmd = CLIParser.parse("delete node --id=1", sample_graph)
        result = CLIExecutor.execute(cmd)
        assert "Error" in result

    def test_delete_node_nonexistent_returns_error(self, sample_graph):
        cmd = CLIParser.parse("delete node --id=999", sample_graph)
        result = CLIExecutor.execute(cmd)
        assert "Error" in result


class TestExecutorCreateEdge:
    def test_create_edge_adds_to_graph(self, sample_graph):
        cmd = CLIParser.parse("create edge --id=e3 --source=1 --target=3", sample_graph)
        CLIExecutor.execute(cmd)
        assert sample_graph.has_edge("e3")

    def test_create_edge_with_attributes(self, sample_graph):
        cmd = CLIParser.parse("create edge --id=e3 --source=1 --target=3 --attribute weight=7", sample_graph)
        CLIExecutor.execute(cmd)
        assert sample_graph.get_edge("e3").attributes["weight"] == 7

    def test_create_edge_duplicate_returns_error(self, sample_graph):
        cmd = CLIParser.parse("create edge --id=e1 --source=1 --target=3", sample_graph)
        result = CLIExecutor.execute(cmd)
        assert "Error" in result

    def test_create_edge_missing_source_node_returns_error(self, sample_graph):
        cmd = CLIParser.parse("create edge --id=e3 --source=999 --target=1", sample_graph)
        result = CLIExecutor.execute(cmd)
        assert "Error" in result


class TestExecutorEditEdge:
    def test_edit_edge_updates_attribute(self, sample_graph):
        cmd = CLIParser.parse("edit edge --id=e1 --attribute weight=10", sample_graph)
        CLIExecutor.execute(cmd)
        assert sample_graph.get_edge("e1").attributes["weight"] == 10

    def test_edit_edge_adds_new_attribute(self, sample_graph):
        cmd = CLIParser.parse("edit edge --id=e1 --attribute label=friends", sample_graph)
        CLIExecutor.execute(cmd)
        assert sample_graph.get_edge("e1").attributes["label"] == "friends"

    def test_edit_edge_nonexistent_returns_error(self, sample_graph):
        cmd = CLIParser.parse("edit edge --id=e999 --attribute weight=1", sample_graph)
        result = CLIExecutor.execute(cmd)
        assert "Error" in result


class TestExecutorDeleteEdge:
    def test_delete_edge_removes_from_graph(self, sample_graph):
        cmd = CLIParser.parse("delete edge --id=e1", sample_graph)
        CLIExecutor.execute(cmd)
        assert not sample_graph.has_edge("e1")

    def test_delete_edge_nonexistent_returns_error(self, sample_graph):
        cmd = CLIParser.parse("delete edge --id=e999", sample_graph)
        result = CLIExecutor.execute(cmd)
        assert "Error" in result


class TestExecutorDeleteGraph:
    def test_delete_graph_removes_all_nodes_and_edges(self, sample_graph):
        cmd = CLIParser.parse("delete graph", sample_graph)
        CLIExecutor.execute(cmd)
        assert sample_graph.node_count() == 0
        assert sample_graph.edge_count() == 0

    def test_delete_graph_on_empty_graph(self, empty_graph):
        cmd = CLIParser.parse("delete graph", empty_graph)
        CLIExecutor.execute(cmd)
        assert empty_graph.node_count() == 0


class TestExecutorFilter:
    def test_filter_returns_subgraph(self, sample_graph):
        cmd = CLIParser.parse("filter age>25", sample_graph)
        result = CLIExecutor.execute(cmd)
        ids = {n.id for n in result}
        assert ids == {"1", "3"}

    def test_filter_equality(self, sample_graph):
        cmd = CLIParser.parse("filter city==Belgrade", sample_graph)
        result = CLIExecutor.execute(cmd)
        ids = {n.id for n in result}
        assert ids == {"1", "3"}

    def test_filter_no_results(self, sample_graph):
        cmd = CLIParser.parse("filter age>100", sample_graph)
        result = CLIExecutor.execute(cmd)
        assert result.node_count() == 0

    def test_filter_invalid_returns_error(self, sample_graph):
        cmd = CLIParser.parse("filter age>Berlin", sample_graph)
        result = CLIExecutor.execute(cmd)
        assert "error" in result.lower()


class TestExecutorSearch:
    def test_search_returns_subgraph(self, sample_graph):
        cmd = CLIParser.parse("search Alice", sample_graph)
        result = CLIExecutor.execute(cmd)
        ids = {n.id for n in result}
        assert ids == {"1"}

    def test_search_partial_match(self, sample_graph):
        cmd = CLIParser.parse("search Bel", sample_graph)
        result = CLIExecutor.execute(cmd)
        ids = {n.id for n in result}
        assert ids == {"1", "3"}

    def test_search_no_results(self, sample_graph):
        cmd = CLIParser.parse("search xyz_not_found", sample_graph)
        result = CLIExecutor.execute(cmd)
        assert result.node_count() == 0

    def test_search_by_attribute_key(self, sample_graph):
        cmd = CLIParser.parse("search joined", sample_graph)
        result = CLIExecutor.execute(cmd)
        ids = {n.id for n in result}
        assert ids == {"3"}