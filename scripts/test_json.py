from plugins.json_datasource import JsonDataSourcePlugin

plugin = JsonDataSourcePlugin()

graph = plugin.load(
    file_path="plugins/json_datasource/sample.json"
)

print("Nodes:", graph.node_count())
print("Edges:", graph.edge_count())


print("\nNeighbors of emp_1:")

for n in graph.neighbors("emp_1"):
    print(n.id)