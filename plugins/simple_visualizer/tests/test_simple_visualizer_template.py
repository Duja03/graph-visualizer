from api.model import Graph, Node, Edge
from simple_visualizer import SimpleVisualizerPlugin

graph = Graph(directed=True)

data = {
    "nodes": [
        {"id": "company_1"},
        {"id": "emp_1"},
        {"id": "emp_2"},
        {"id": "emp_3"},
        {"id": "dep_1"},
    ],
    "edges": [
        {"id": "company_1_emp_1", "source": "company_1", "target": "emp_1"},
        {"id": "company_1_emp_2", "source": "company_1", "target": "emp_2"},
        {"id": "company_1_emp_3", "source": "company_1", "target": "emp_3"},
        {"id": "emp_1_emp_3",     "source": "emp_1",     "target": "emp_3"},
        {"id": "emp_2_emp_3",     "source": "emp_2",     "target": "emp_3"},
        {"id": "emp_3_dep_1",     "source": "emp_3",     "target": "dep_1"},
        {"id": "company_1_dep_1", "source": "company_1", "target": "dep_1"},
    ]
}

for n in data["nodes"]:
    graph.add_node(Node(id=n["id"]))

for e in data["edges"]:
    graph.add_edge(Edge(id=e["id"], source=e["source"], target=e["target"]))

plugin = SimpleVisualizerPlugin()
html = plugin.render(graph)

full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Simple Visualizer Test</title>
  <style>html, body {{ margin: 0; height: 100%; }}</style>
</head>
<body style="height:100%">
{html}
</body>
</html>"""

with open("visualizer_output.html", "w") as f:
    f.write(full_html)

print("Done — open 'visualizer_output.html' in your browser.")