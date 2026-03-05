from json_datasource.src.json_datasource.json_datasource_plugin import JsonDataSourcePlugin


def main():

    plugin = JsonDataSourcePlugin()

    graph = plugin.load(
        file_path="scripts/sample.json"
    )

    print("====== GRAPH INFO ======")
    print("Nodes:", graph.node_count())
    print("Edges:", graph.edge_count())
    print()

    print("====== NODES ======")

    for node in graph:
        print(node.id, node.attributes)

    print()
    print("====== EDGES ======")

    for edge in graph.iter_edges():
        print(
            edge.id,
            edge.source,
            "->",
            edge.target,
            edge.attributes
        )

    print()
    print("====== NEIGHBORS emp_1 ======")

    for n in graph.neighbors("emp_1"):
        print(n.id)


if __name__ == "__main__":
    main()