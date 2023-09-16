import networkx as nx
import numpy as np
from functools import reduce
from loguru import logger


class SWinReach:
    DTPTB_REACH = "dtptb-reach"
    PGSOLVER = "pgsolver"
    GGSOLVER = "ggsolver"

    def __init__(self, graph, final, player=1, **kwargs):
        # Input parameters:
        self._graph = graph
        self._final = set(final)
        self._player = player

        # Solver parameters:
        self._is_solved = False
        self._solver = kwargs.get("solver", SWinReach.GGSOLVER)

        # Output parameters:
        self.level_set = {0: set(final)}
        self.winning_nodes = {player: set(final), 3 - player: set()}
        self.winning_edges = {player: set(), 3 - player: set()}

    def solve(self, force=False):
        # If game is solved and `force` is False, then warn the user.
        if self._is_solved and not force:
            logger.warning(f"Game is solved. To solve again, call `solve(force=True)`.")
            return

        # Invoke the appropriate solver by asserting appropriate model type.
        if self._solver == SWinReach.GGSOLVER:
            assert isinstance(self._graph, nx.MultiDiGraph), \
                f"dtptb.SWinReach python solver expects model of type `nx.MultiDiGraph`, not `{type(self._graph)}`."
            self.solve_ggsolver()

        if self._solver == SWinReach.PGSOLVER:
            assert isinstance(self._graph, [nx.MultiDiGraph, dict, np.array]), \
                f"dtptb.SWinReach pgsolver expects model of type `nx.MultiDiGraph, dict` or `np.array`, not `{type(self._graph)}`."
            self.solve_pgsolver()

        if self._solver == SWinReach.DTPTB_REACH:
            assert isinstance(self._graph, nx.MultiDiGraph), \
                f"dtptb.SWinReach dtptb-reach expects model of type `nx.MultiDiGraph, dict` or `np.array`, not `{type(self._graph)}`."
            self.solve_dtptb_reach()

    def solve_dtptb_reach(self):
        # Generate input to dtptb-reach CLI utility.
        # Run the utility and read the output.
        # Mark winning nodes and winning edges.
        pass

    def solve_pgsolver(self):
        # Generate input to pgsolver CLI utility.
        # Run the utility and read the output.
        # Mark winning nodes and winning edges.
        pass

    def solve_ggsolver(self):
        """
        Expects model to be networkx graph.
        """
        # Reset solver
        self.reset()

        # If no final states, do not run solver utility. Declare all states are winning for opponent.
        if len(self._final) == 0:
            logger.warning(f"Game has no final states. Marking all states to be winning for player-{3 - self._player}.")
            self.winning_nodes[3 - self._player] = self._graph.nodes()
            self.winning_edges[3 - self._player] = self._graph.edges()
            self._is_solved = True
            return

        # Mark all final states as sink states
        graph = nx.subgraph_view(
            self._graph,
            filter_node=lambda n: True,
            filter_edge=lambda u, v, a: u not in self._final
        )

        # Initialization
        rank = 1
        win_nodes = set(self._final)

        while True:
            predecessors = set(reduce(set.union, map(set, map(graph.predecessors, win_nodes))))
            pre_p = {uid for uid in predecessors if graph.nodes[uid]["turn"] == self._player}
            pre_np = predecessors - pre_p
            pre_np = {uid for uid in pre_np if set(graph.successors(uid)).issubset(win_nodes)}
            next_level = set.union(pre_p, pre_np) - win_nodes

            if len(next_level) == 0:
                break

            self.level_set[rank] = next_level
            self.winning_edges[self._player].update(
                {(u, v, a) for u in next_level for _, v, a in graph.out_edges(u, keys=True) if v in win_nodes}
            )
            win_nodes |= next_level
            rank += 1

        # States not in win_nodes are winning for np.
        self.winning_nodes[self._player] = win_nodes
        self.winning_nodes[3 - self._player] = set(graph.nodes()) - self.winning_nodes[self._player]
        self.winning_edges[3 - self._player] = set(graph.edges(keys=True)) - self.winning_edges[self._player]

        # Mark the game to be solved
        self._is_solved = True

    def reset(self):
        self.level_set = {0: set(self._final)}
        self.winning_nodes = {self._player: set(self._final), 3 - self._player: set()}
        self.winning_edges = {self._player: set(), 3 - self._player: set()}

    def final(self):
        return self._final
