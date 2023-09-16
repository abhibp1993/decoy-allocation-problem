import networkx as nx
from loguru import logger
import copy


class ASWinReach:
    SOLV_POMC = "pomc-alg45"
    SOLV_ATTR = "attractor"
    PLAYER_NATURE = 0
    PLAYER1 = 1

    def __init__(self, model, final, **kwargs):
        # Input parameters:
        self._model = model
        self._final = set(final)
        self._player = ASWinReach.PLAYER1

        # Solver parameters:
        self._is_solved = False
        self._solver = kwargs.get("solver", ASWinReach.SOLV_POMC)

        # Output parameters:
        self.winning_nodes = {ASWinReach.PLAYER1: set(), ASWinReach.PLAYER_NATURE: set()}
        self.winning_edges = {ASWinReach.PLAYER1: set(), ASWinReach.PLAYER_NATURE: set()}

    def solve(self, force=False):
        # If game is solved and `force` is False, then warn the user.
        if self._is_solved and not force:
            logger.warning(f"Game is solved. To solve again, call `solve(force=True)`.")
            return

        # Invoke the appropriate solver by asserting appropriate model type.
        if self._solver == ASWinReach.SOLV_POMC:
            assert isinstance(self._model, nx.MultiDiGraph), \
                f"dtptb.SWinReach python solver expects model of type `nx.MultiDiGraph`, not `{type(self._model)}`."
            self.solve_pomc45()

    def solve_pomc45(self):
        """
        Expects model to be networkx graph.
        """
        # Helper functions
        def pre(g, vid):
            return {(uid, key) for uid, _, key in graph.in_edges(vid, keys=True)}

        # Reset solver
        self.reset()

        # If no final states, do not run solver utility. Declare all states are winning for opponent.
        if len(self._final) == 0:
            logger.warning(f"Game has no final states. Marking all states to be winning for player-{3 - self._player}.")
            self.winning_nodes[ASWinReach.PLAYER_NATURE] = self._model.nodes()
            self.winning_edges[ASWinReach.PLAYER_NATURE] = self._model.edges()
            self._is_solved = True
            return

        # Initializations
        # 0. Create a subgraph view.
        #   The Subgraph view is defined using two "mutable" sets: hidden_nodes/edges.
        #   Modifying hidden_nodes/edges will modify subgraph.
        #   When lambda returns True, node/edge is included in subgraph.
        hidden_nodes = set()
        hidden_edges = set()
        graph = nx.subgraph_view(
            self._model,
            filter_node=lambda x: x not in hidden_nodes,
            filter_edge=lambda u, v, a: (u, v, a) not in hidden_edges
        )

        # 1. Mark B absorbing
        b = set.intersection(set(graph.nodes()), set(self._final))
        hidden_edges.update([(u, v, a) for u in b for _, v, a in self._model.out_edges(u, keys=True)])

        # 2. Identify disconnected nodes
        disconnected = self.disconnected(graph, b)

        # 3. Initialize U
        set_u = {s for s in graph.nodes() if s in disconnected}

        # Alg. 45 from PoMC.
        while True:
            set_r = set_u.copy()
            while len(set_r) > 0:
                u = set_r.pop()

                for t, a in pre(graph, u):
                    if t in set_u:
                        continue
                    # self.remove_act(graph, t, a)
                    for _, v, act in graph.out_edges(t, keys=True):
                        if act == a:
                            hidden_edges.add((t, v, a))
                    if len(set(graph.successors(t))) == 0:
                        set_r.add(t)
                        set_u.add(t)
                hidden_nodes.add(u)
            disconnected = self.disconnected(graph, b)
            set_u = {s for s in set(graph.nodes()) - set_u if s in disconnected}
            if len(set_u) == 0:
                break

        # Any node which is not hidden is winning for P1.
        self.winning_nodes[self._player] = set(graph.nodes())
        self.winning_nodes[1 - self._player] = set(self._model.nodes()) - self.winning_nodes[self._player]
        self.winning_edges[self._player] = set(graph.edges(keys=True))
        self.winning_edges[3 - self._player] = set(self._model.edges(keys=True)) - self.winning_nodes[self._player]

        # Mark the game to be solved
        self._is_solved = True

    # def solve_attr(self):
    #     # Reset solver
    #     self.reset()
    #
    #     # If no final states, do not run solver utility. Declare all states are winning for opponent.
    #     if len(self._final) == 0:
    #         logger.warning(f"Game has no final states. Marking all states to be winning for player-{3 - self._player}.")
    #         self.winning_nodes[ASWinReach.PLAYER_NATURE] = self._model.nodes()
    #         self.winning_edges[ASWinReach.PLAYER_NATURE] = self._model.edges()
    #         self._is_solved = True
    #         return
    #
    #     # Construct suppDict.
    #     # TODO.
    #
    #     # Define pre function
    #     def pre(x, y):
    #         pre_ = set()
    #         for s in self._model.nodes():
    #             for a in mdp.actlist:
    #                 if len(mdp.suppDict[(s, a)].intersection(X)) != 0 and mdp.suppDict[(s, a)].issubset(Y):
    #                     Pre.add(s)
    #                     break
    #         return X.union(Pre)
    #
    #     # Initializations
    #     set_y = set(self._model.nodes())
    #     x_new = set([])
    #     x_level_sets = []
    #     y_level_sets = []
    #     flag = True
    #     while True:
    #         if x_new == set_y:
    #             break
    #         else:
    #             if flag:
    #                 flag = False
    #                 pass
    #             else:
    #                 set_y = x_new
    #                 x_level_sets = []
    #             set_x = set(self._final)
    #             x_level_sets.append(set_x)
    #             y_level_sets.append(set_y)
    #             while True:
    #                 x_new = pre(set_x, set_y)
    #                 if x_new == set_x:
    #                     break
    #                 else:
    #                     set_x = x_new
    #                     x_level_sets.append(set_x)

    def reset(self):
        self.winning_nodes = {1: set(), 2: set()}
        self.winning_edges = {1: set(), 2: set()}

    def final(self):
        return self._final

    @staticmethod
    def disconnected(graph, sources):
        rev_graph = nx.reverse_view(graph)
        bfs_layers = nx.bfs_layers(rev_graph, sources)
        reachable_nodes = set.union(set(), *(set(nodes) for nodes in bfs_layers))
        return set(graph.nodes()) - reachable_nodes

    # @staticmethod
    # def pre(graph, vid):
    #     if graph.has_node(vid):
    #         return {(uid, graph["input"][uid, vid, key]) for uid, _, key in graph.in_edges(vid)}
    #     return set()

    @staticmethod
    def remove_act(graph, uid, act):
        for _, vid, key in graph.out_edges(uid):
            if graph["input"][uid, vid, key] == act:
                # print(f"\tHiding {uid}, {act}, edge:{uid, vid, key}")
                graph.hide_edge(uid, vid, key)
