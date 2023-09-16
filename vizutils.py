import pygraphviz


def visualize_mdp(mdp_graph, fpath, winning_nodes=None, sr_acts=None):
    """
    Visualize an MDP graph.

    Directives:
        * States visualized as circles.
        * Each state shows its name.
        * Edges are labeled with action.
        * Special state `qF` is marked accepting.
        * If `winning_nodes` is provided, the winning nodes are marked in `blue` color.
        * If `winning_edges` is provided, the winning edges are marked in `blue` color.

    :param mdp_graph: (nx.MultiDiGraph) MDP graph.
    :param winning_nodes: (set) Set of winning nodes.
    :param sr_acts: (set) Set of winning edges.
    :param fpath: (str) Path to save the image.
    """
    # Create a graphviz graph
    vis_graph = pygraphviz.AGraph(directed=True, strict=False)

    # Add nodes
    for n, data in mdp_graph.nodes(data=True):
        dot_properties = {"shape": "circle"}
        if winning_nodes is not None and n in winning_nodes:
            dot_properties["color"] = "blue"
        if data.get("label", None) == "qF":
            dot_properties["peripheries"] = 2
        vis_graph.add_node(n, **dot_properties)

    # Add edges
    for u, v, a in mdp_graph.edges(keys=True):
        dot_properties = {"label": a}
        if sr_acts is not None:
            if a in sr_acts.get(u, set()):
                dot_properties["color"] = "red"
        vis_graph.add_edge(u, v, key=a, **dot_properties)

    # Generate graph layout
    vis_graph.layout("dot")

    # Draw the graph
    vis_graph.draw(fpath)


def visualize_game(
        game_graph,
        fpath,
        final=None,
        traps=None,
        fakes=None,
        rank=None,
        winning_nodes=None,
        sr_acts=None,
        winning_color="blue",
):
    """
    Visualize a two-player game graph.

    Directives:
        * P1 states visualized as circles, P2 states are visualized as box.
        * Each state shows its name (by default). If `rank` is provided, the state labels include their rank.
        * If provided, `final` states are marked accepting.
        * If provided, `traps` states are colored green and styled dashed.
        * If provided, `fakes` states are colored green and styled dashed + marked accepting.
        * If `winning_nodes` is provided, the winning nodes are marked in `red` color.
        * Edges are labeled with action.
        * If `winning_edges` is provided, the winning edges are marked in `red` color.

    :param game_graph: (nx.MultiDiGraph) Game graph.
    :param traps: (set) Nodes marked as a trap.
    :param fakes: (set) Nodes marked as a fake target.
    :param final: (set) Nodes marked as a final state.
    :param rank: (set) Rank of a node in the winning region.
    :param winning_nodes: (set) Set of winning nodes.
    :param sr_acts: (set) Set of winning edges.
    :param winning_color: (Color) Color of winning nodes and edges.
    :param fpath: (str) Path to save the image.
    """
    # Create a graphviz graph
    vis_graph = pygraphviz.AGraph(directed=True, strict=False)

    # Add nodes
    for n, data in game_graph.nodes(data=True):
        dot_properties = dict()

        if rank is not None and n in rank:
            dot_properties["label"] = f"({n}, r:{rank[n]})"
        else:
            dot_properties["label"] = f"{n}"

        if game_graph.nodes[n]["turn"] == 1:
            dot_properties["shape"] = "circle"
        else:
            dot_properties["shape"] = "box"

        if final is not None and n in final:
            dot_properties["peripheries"] = 2

        if traps is not None and n in traps:
            dot_properties["style"] = "dashed"
            dot_properties["fillcolor"] = "#00FF0080"

        if fakes is not None and n in fakes:
            dot_properties["style"] = "dashed"
            dot_properties["peripheries"] = 2
            dot_properties["fillcolor"] = "#00FF0080"

        if winning_nodes is not None and n in winning_nodes:
            dot_properties["color"] = winning_color

        vis_graph.add_node(n, **dot_properties)

    # Add edges
    for u, v, a in game_graph.edges(keys=True):
        dot_properties = {"label": a}
        if sr_acts is not None:
            if a in sr_acts.get(u, set()):
                dot_properties["color"] = "red"
        vis_graph.add_edge(u, v, key=a, **dot_properties)

    # Generate graph layout
    vis_graph.layout("sfdp")

    # Draw the graph
    vis_graph.draw(fpath)


def save_base_game(graph, solver, fpath, final=None, traps=None, fakes=None, sr_acts=None):
    # Extract rank
    rank = {state: level for level, states in solver.level_set.items() for state in states}
    for state in solver.winning_nodes[1]:
        rank[state] = float("inf")

    # Generate PNG and save.
    visualize_game(
        game_graph=graph,
        fpath=fpath,
        rank=rank,
        final=final,
        traps=traps,
        fakes=fakes,
        winning_nodes=solver.winning_nodes[2],
        sr_acts=sr_acts,
        winning_color="red",
    )


def save_p2_game(graph, solver, fpath, final=None, traps=None, fakes=None, sr_acts=None):
    # Extract rank
    rank = {state: level for level, states in solver.level_set.items() for state in states}
    for state in solver.winning_nodes[1]:
        rank[state] = float("inf")

    # Generate PNG and save.
    visualize_game(
        game_graph=graph,
        fpath=fpath,
        rank=rank,
        final=final,
        traps=traps,
        fakes=fakes,
        winning_nodes=solver.winning_nodes[2],
        sr_acts=sr_acts,
        winning_color="red",
    )


def save_hypergame(graph, solver, fpath, final=None, traps=None, fakes=None, sr_acts=None):
    # Extract rank
    rank = {state: level for level, states in solver.level_set.items() for state in states}
    for state in solver.winning_nodes[2]:
        rank[state] = float("inf")

    # Generate PNG and save.
    visualize_game(
        game_graph=graph,
        fpath=fpath,
        rank=rank,
        final=final,
        traps=traps,
        fakes=fakes,
        winning_nodes=solver.winning_nodes[1],
        sr_acts=sr_acts,
        winning_color="forestgreen",
    )
