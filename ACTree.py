from graphviz import Digraph

def draw_tree(node, graph=None):
    if graph is None:
        graph = Digraph()

    label = f"{node.label}"
    color = "red" if node.failed else "black"

    graph.node(str(id(node)), label, color=color)

    for child in node.children:
        graph.edge(str(id(node)), str(id(child)))
        draw_tree(child, graph)

    return graph