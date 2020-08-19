#!/usr/bin/env python
# coding: utf-8

import copy
from itertools import combinations
import json
import random
from tqdm import tqdm

import networkx as nx
import matplotlib.pyplot as plt

import gamegraph
import surewin

num_nodes = 20
num_edges = 3
num_decoys = 3


# Helper class
class Pair(object):
    def __init__(self, n, dswin_n):
        self.n = n
        self.dswin_n = dswin_n

    def __repr__(self):
        return f"({self.n}: {self.dswin_n})"

    def __len__(self):
        return len(self.dswin_n)


# Greedy Algorithm (Adds set with most new elements)
# https://homes.cs.washington.edu/~marcotcr/blog/greedy-submodular/
def greedy_cover(universe, subsets, max_k=float("inf")):

        # avoid mutation
        tmp_subsets = copy.deepcopy(subsets)

        elements = set(e for s in tmp_subsets for e in s.dswin_n)
        largest_subset = max(tmp_subsets, key=lambda x: len(x))
        tmp_subsets.remove(largest_subset)

        covered = largest_subset.dswin_n
        uncovered = elements - covered
        cover = [largest_subset.n]


        # Greedily add the subsets with the most uncovered points
        while len(uncovered) > 0 and len(cover) < max_k:
            subset = max(tmp_subsets, key=lambda s: len(s.dswin_n - covered))
            cover.append(subset.n)
            covered |= subset.dswin_n
            uncovered = elements - covered
            tmp_subsets.remove(subset)

        cover.sort()  # for convenience of reading :)
        return cover, covered


def greedymax(universe, subsets, max_k=float("inf")):

    tmp_subsets = copy.deepcopy(subsets)
    elements = set(e for s in tmp_subsets for e in s.dswin_n)
    decoys = set()
    covered = set()

    iter_count = 0
    while (len(elements - covered) > 0 and len(decoys) < max_k):
        iter_count += 1
        # print(f"Iteration {iter_count}")

        nondecoys = elements - decoys
        updated_dswins = list()
        # print(f"\tNon-decoy: {nondecoys}")

        for n in nondecoys:
            final = list() + list(decoys) + [n]
            pair = Pair(n, surewin.surewin(hgame, set(final), 1))
            updated_dswins.append(pair)
            # print(f"\t\tPair({n}, surewin.surewin(hgame, {final}, 1)): {pair}")

        next_decoy = max(updated_dswins, key=lambda x: len(x))
        decoys.add(next_decoy.n)
        covered.update(next_decoy.dswin_n)

        # print(f"\tUpdated DSWin_n: {updated_dswins}")

        # print(f"\tSelected Decoy: {next_decoy.n}")

    return decoys, covered


def is_submodular(dswin_u, dswin_uv):
    """
    This function assumes number of decoys is limited to 2.
    In this case, it is sufficient that
            DSWin_{s1 U s2) = DSWin_s1 U DSWin_s2
    to ensure submodularity.

    :param dswin_u: DSWin of individual states.
    :param dswin_uv: DSWin of pairs of states.

    """
    for pair_uv in dswin_uv:

        dswin_p1 = dswin_p2 = None
        for pair_u in dswin_u:
            if pair_u.n == pair_uv.n[0]:
                dswin_p1 = pair_u.dswin_n

            if pair_u.n == pair_uv.n[1]:
                dswin_p2 = pair_u.dswin_n

        if set.union(dswin_p1, dswin_p2) != pair_uv.dswin_n:
            return False

    return True


def is_supermodular(dswin_u, dswin_uv):
    """
    Supermodularity becomes relevant only for k >= 3.
    """
    return True


class setEncoder(json.JSONEncoder):
    def default(self, obj):
        return list(obj)


data = []
for seed in tqdm(range(250)):
    random.seed(seed)

    try:
        graph = gamegraph.generate_game_graph(num_nodes, num_edges)
        final = set(random.sample(graph.nodes(), 2))
        sw = surewin.surewin(graph, final, 2)
        hgame = surewin.surewin_graph(graph, sw, 2)

        # DSWin Computation
        dswin_u = set()
        for n in hgame.nodes():
            if n in final:
                continue

            dswin_u.add(Pair(n, surewin.surewin(hgame, {n}, 1)))

        pairs = combinations(set(hgame.nodes()) - final, num_decoys)

        dswin = set()
        for p in pairs:
            dswin.add(Pair(tuple(p), surewin.surewin(hgame, set(p), 1)))

        dswin = list(dswin)
        pair = max(dswin, key=lambda x: len(x))

        decoys_combinatorial, covered_combinatorial = pair.n, pair.dswin_n
        decoys_submodular, covered_submodular = greedy_cover(hgame.nodes(), dswin_u, num_decoys)
        decoys_algorithm2, covered_algorithm2 = greedymax(hgame.nodes(), dswin_u, num_decoys)

        record = {"seed": seed,
                  "graph_nodes": list(graph.nodes()),
                  "graph_edges": list(graph.edges()),
                  "final": list(final),
                  "hgame_nodes": list(hgame.nodes()),
                  "hgame_edges": list(hgame.edges()),
                  "decoys_combinatorial": decoys_combinatorial,
                  "decoys_greedysetcover": decoys_submodular,
                  "decoys_greedymax": decoys_algorithm2,
                  "covered_combinatorial": covered_combinatorial,
                  "covered_greedysetcover": covered_submodular,
                  "covered_greedymax": covered_algorithm2,
                  "is_submodular": is_submodular(dswin_u, dswin)
                  }

        data.append(record)

    except (ValueError) as err:
        record = {"seed": seed, "error": str(type(err)), "error message": str(err)}
        data.append(record)

with open(f"logs/search_n{num_nodes}_e{num_edges}_k{num_decoys}.json", "w") as file:
    json.dump(data, file, indent=4, cls=setEncoder)
