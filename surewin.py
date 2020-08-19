"""
Sure winning region computation (Zielonka, McNaughton) algorithm.
Expected graph class is Networkx.DiGraph
"""

import networkx as nx


def pre_exists(graph, y, player):
    pre = set()
    for v in y:
        if graph.nodes[v]["turn"] == player:
            for (u, _) in graph.in_edges(v):
                pre.add(u)

    return pre


def pre_forall(graph, y, player):
    pre = set()
    for v in y:
        if graph.nodes[v]["turn"] == player:
            for (u, _) in graph.in_edges(v):

                post = set()
                for (_, w) in graph.out_edges(u):
                    post.add(w)

                if post.issubset(y):
                    pre.add(u)

    return pre


def surewin(graph, final, player):

    y = final

    while True:
        y1 = pre_exists(graph, y, player)
        y2 = pre_forall(graph, y, player)
        pre = set.union(*(y, y1, y2))

        if pre == y:
            break

        y = pre

    return y


def sr_acts(graph, sw, player):
    sr_edges = set()
    for u in graph.nodes():
        if u in sw and graph.nodes[u]["turn"] == player:     # n is winning for player in surewin of player
            for (_, v) in graph.out_edges(u):
                if v in sw:
                    sr_edges.add((u, v))

        if u in sw and graph.nodes[u]["turn"] != player:     # n is winning for player in surewin of player
            for (_, v) in graph.out_edges(u):
                if v in sw:
                    sr_edges.add((u, v))

    return sr_edges


def surewin_graph(graph, sw, player):
    sr_edges = sr_acts(graph, sw, player)
    sw_graph = nx.DiGraph()

    # sw_graph.add_nodes_from(sw)
    for n in sw:
        sw_graph.add_node(n, turn=graph.nodes[n]["turn"])

    sw_graph.add_edges_from(sr_edges)

    return sw_graph
