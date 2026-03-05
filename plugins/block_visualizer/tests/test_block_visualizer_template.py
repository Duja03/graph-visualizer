from api.model import Graph, Node, Edge
from block_visualizer.src.block_visualizer import BlockVisualizerPlugin

graph = Graph(directed=True)

data = {
    "nodes": [
        {"id": "company_1", "attributes": {"name": "GraphSoft", "founded": "2015-03-10"}},
        {"id": "emp_1",     "attributes": {"name": "Sara",  "age": 23, "salary": "3500.5"}},
        {"id": "emp_2",     "attributes": {"name": "Marko", "age": 30}},
        {"id": "emp_3",     "attributes": {"name": "Luka",  "age": 40}},
        {"id": "dep_1",     "attributes": {"name": "Engineering"}},
    ],
    "edges": [
        {"id": "company_1_emp_1", "source": "company_1", "target": "emp_1", "attributes": {"relation": "employees"}},
        {"id": "company_1_emp_2", "source": "company_1", "target": "emp_2", "attributes": {"relation": "employees"}},
        {"id": "company_1_emp_3", "source": "company_1", "target": "emp_3", "attributes": {"relation": "employees"}},
        {"id": "emp_1_emp_3",     "source": "emp_1",     "target": "emp_3", "attributes": {"relation": "manager"}},
        {"id": "emp_2_emp_3",     "source": "emp_2",     "target": "emp_3", "attributes": {"relation": "manager"}},
        {"id": "emp_3_dep_1",     "source": "emp_3",     "target": "dep_1", "attributes": {"relation": "department"}},
        {"id": "company_1_dep_1", "source": "company_1", "target": "dep_1", "attributes": {"relation": "main_department"}},
    ]
}

for n in data["nodes"]:
    graph.add_node(Node(id=n["id"], attributes=n["attributes"]))

for e in data["edges"]:
    graph.add_edge(Edge(id=e["id"], source=e["source"], target=e["target"], attributes=e["attributes"]))

plugin = BlockVisualizerPlugin()
html = plugin.render(graph)

full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Block Visualizer Test</title>
  <style>html, body {{ margin: 0; height: 100%; }}</style>
</head>
<body style="height:100%">
{html}
</body>
</html>"""

with open("visualizer_output.html", "w") as f:
    f.write(full_html)

print("Done — open 'visualizer_output.html' in your browser.")
