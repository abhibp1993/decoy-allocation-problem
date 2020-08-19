"""
Generate random graph.
"""

import random
import networkx as nx


def generate_nk_graph(n, k):
    graph = nx.generators.directed.random_k_out_graph(n, k, alpha=50, self_loops=False)
    return graph


def make_two_player(graph):
    num_nodes = graph.number_of_nodes()
    p1_nodes = random.sample(range(num_nodes), k=int(num_nodes/2))

    for i in range(num_nodes):
        if i in p1_nodes:
            graph.nodes[i]["turn"] = 1
        else:
            graph.nodes[i]["turn"] = 2

    return graph


def label_actions(graph):
    return graph


def generate_game_graph(n, k):
    graph = generate_nk_graph(n, k)
    graph = make_two_player(graph)
    graph = label_actions(graph)

    return graph

