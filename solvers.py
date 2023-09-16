import dtptb
import mdp
import networkx as nx
from loguru import logger


class DecoyAllocator:
    SWin = "sure winning"
    ASWin = "almost-sure winning"
    GREEDY = "greedy"
    ENUMERATIVE = "enumerative"

    def __init__(self, p1game, true_final, n_traps, n_fakes, candidates, sol_concept=SWin, approach=GREEDY, **kwargs):
        # Parameters needed for generating solution
        self._p1game = p1game
        self._true_final = true_final
        self._candidates = candidates
        self._num_traps = n_traps
        self._num_fakes = n_fakes
        self._init_fakes = set(kwargs.get("init_fakes", set()))
        self._init_traps = set(kwargs.get("init_traps", set()))
        self._debug = kwargs.get("debug", False)
        self._sol_concept = sol_concept
        self._approach = approach

        # Variables for outputs
        self._best_vod = 0.0
        self._best_traps = set()
        self._best_fakes = set()
        self._best_decoys = None
        self._best_win = None
        self._data = None  # {iteration: {<vod>: {"traps": [<trap-cells>], "fakes": [<fake-cells>]}}}

        # Intermediate variables
        self._base_game_sol = None

    def best_decoys(self):
        return self._best_decoys

    def data(self):
        return self._data

    def solve(self):
        # Solve base game

        # Place decoys
        if self._approach == DecoyAllocator.GREEDY and self._sol_concept == DecoyAllocator.SWin:
            self.solve_greedy(solver=DSWinReach)
        if self._approach == DecoyAllocator.GREEDY and self._sol_concept == DecoyAllocator.ASWin:
            self.solve_greedy(solver=DASWinReach)
        if self._approach == DecoyAllocator.ENUMERATIVE and self._sol_concept == DecoyAllocator.ASWin:
            self.solve_enumerative(algo=DSWinReach)
        else:
            self.solve_enumerative(algo=DASWinReach)

    def solve_greedy(self, solver):
        # Terminate if no decoys are to be placed
        if self._num_fakes == 0 and self._num_traps == 0:
            self._best_win = set()
            self._data = dict()
            logger.warning("DecoyAllocator terminated without placing any decoys. Parameters `n_traps` and `n_fakes` are set to 0.")
            return

        # Initialize traps and fakes as empty set
        traps = self._init_traps
        fakes = self._init_fakes

        # FIXME. Candidate decoys cannot include final states. This was missing previously!
        # # Identify candidate decoys
        # win2 = set(self._base_game_solution.winning_nodes(player=2))
        # final = set(self._base_game_solution.final())
        # candidate2nodes = dict()
        # for candidate in self._candidates:
        #     potential_finals = set.intersection(self._candidates[candidate], win2) - final
        #     if len(potential_finals) > 0:
        #         candidate2nodes[candidate] = potential_finals
        # logger.info(f"Candidate Decoys: {set(candidate2nodes.keys())} ")
        logger.info(f"Initializing candidate decoys: {set(self._candidates.keys())} ")

        # 1. ALLOCATE FAKES
        self._data = dict()
        self._best_decoys = dict()
        while self._num_fakes - len(fakes) > 0:
            # Bookkeeping
            iter_count = len(fakes) + 1
            self._data[iter_count] = list()

            # Collect potential states that can be allocated as next fake
            potential_decoys = set(self._candidates.keys()) - fakes
            logger.info(f"Identified {len(potential_decoys)} potential candidates for fake target no. {iter_count}.")
            if len(potential_decoys) == 0:
                break

            iteration_vod_map = dict().fromkeys(potential_decoys)
            best_fake = None
            best_vod = 0.0
            fake_nodes = set.union(set(), *[self._candidates[fake] for fake in fakes])
            for candidate in potential_decoys:
                # Compute deceptive almost-sure winning region
                win = solver(self._p1game, final=self._true_final, traps=set(), fakes=fake_nodes | self._candidates[candidate])
                win.solve()

                # Update data
                # self._data[iter_count][str(fakes | {candidate})] = win.vod()
                self._data[iter_count].append({"traps": traps | {candidate}, "fakes": fakes, "vod": win.vod})
                logger.info(f"Explored candidate {candidate} for fake no. {iter_count}: "
                            f"fakes={fakes} and traps={traps}. VoD: {win.vod}")

                # Update best fake and vod
                iteration_vod_map[candidate] = win.vod
                if win.vod > best_vod:
                    best_vod = win.vod
                    best_fake = candidate

            # intermediate_vod_fakes.append(iteration_vod_map)
            fakes.add(best_fake)
            self._best_decoys[iter_count] = (best_fake, best_vod)
            logger.info(f"Selected {best_fake} for fake no. {iter_count}: fakes={fakes} and traps={traps}. Resulting VoD: {best_vod}")

        # 2. ALLOCATE TRAPS
        while self._num_traps - len(traps) > 0:
            # Bookkeeping
            iter_count = len(traps) + 1
            self._data[iter_count] = list()

            # Collect potential states that can be allocated as next trap
            potential_decoys = set(self._candidates.keys()) - fakes - traps
            logger.info(f"Identified {len(potential_decoys)} potential candidates for trap no. {iter_count}.")
            if len(potential_decoys) == 0:
                break

            iteration_vod_map = dict().fromkeys(potential_decoys)
            best_trap = None
            best_vod = 0.0
            fake_nodes = set.union(set(), *[self._candidates[fake] for fake in fakes])
            trap_nodes = set.union(set(), *[self._candidates[trap] for trap in traps])
            for candidate in potential_decoys:
                # Compute deceptive almost-sure winning region
                win = solver(
                    self._p1game,
                    final=self._true_final,
                    traps=trap_nodes | self._candidates[candidate],
                    fakes=fake_nodes
                )
                win.solve()

                # Update data
                self._data[iter_count].append({"traps": traps | {candidate}, "fakes": fakes, "vod": win.vod})

                # Update best fake and vod
                iteration_vod_map[candidate] = win.vod
                if win.vod > best_vod:
                    best_vod = win.vod
                    best_trap = candidate
                logger.info(f"Explored candidate {candidate} for trap no. {iter_count}: "
                            f"fakes={fakes} and traps={traps}. VoD: {win.vod}")

            # intermediate_vod_fakes.append(iteration_vod_map)
            traps.add(best_trap)
            self._best_decoys[iter_count] = (best_trap, best_vod)
            logger.info(f"Selected {best_trap} for trap no. {iter_count}: fakes={fakes} and traps={traps}. Resulting VoD: {best_vod}")

    def solve_enumerative(self, algo):
        pass


class DSWinReach:
    def __init__(self, base_game_graph, final, traps, fakes, base_game_sol=None):
        """
        Computes deceptive sure winning region for P1 in a reachability game.

        :param base_game_graph: Base game graph.
        :param final: Set of final states in base game.
        :param traps: Set of states allocated as traps.
        :param fakes: Set of states allocated as fakes.
        :param base_game_sol: Solution of P2 game. If None, then P2's game will be constructed and solved.

        :note: `final, traps, fakes` are nodes in base_game_graph
        """
        # Input parameters:
        self.graph = base_game_graph
        self.final = final
        self.traps = traps
        self.fakes = fakes
        self.base_game_sol = base_game_sol
        self.p2_game_sol = None
        self.hypergame = None
        self.hypergame_sol = None

        # Solver parameters:
        self._is_solved = False

        # Output parameters:
        self.vod = None
        self.sr_acts = None
        self.winning_nodes = {1: set(), 2: set()}
        self.winning_edges = {1: set(), 2: set()}

    def gen_sr_acts(self):
        """
        Assume: P2's game is solved.
        :return: (dict) A map of states to SR actions.
        """
        # Construct a rank dictionary.
        rank = {state: level for level, states in self.p2_game_sol.level_set.items() for state in states}
        for state in self.p2_game_sol.winning_nodes[1]:
            rank[state] = float("inf")

        # Use SRActs definition before Def. 8 in paper to construct SRActs.
        sr_acts = dict()
        for state in self.p2_game_sol.winning_nodes[2]:
            sr_acts[state] = set()
            for _, next_state, action in self.graph.out_edges(state, keys=True):
                if rank[next_state] < rank[state]:
                    sr_acts[state].add(action)

        # Return SRActs.
        return sr_acts

    def construct_hypergame(self, sr_acts):
        hgame = nx.MultiDiGraph()

        # Add states to hypergame.
        for state in self.base_game_sol.winning_nodes[2]:
            hgame.add_node(state, turn=self.graph.nodes[state]["turn"], label=self.graph.nodes[state]["label"])

        # Add edges to hypergame.
        for state in hgame.nodes():
            for _, next_state, action in self.graph.out_edges(state, keys=True):
                # If the next state is not in P2's winning nodes, then skip.
                if not hgame.has_node(next_state):
                    continue

                # If state is final or decoy, mark it sink.
                if state in self.traps | self.fakes | self.final:
                    hgame.add_edge(state, state, key=action, action=action)
                    continue

                # If action is not SR, then skip.
                if action not in sr_acts.get(state, set()):
                    continue

                # Else, add the transition as is.
                hgame.add_edge(state, next_state, key=action, action=action)

        # Return hypergame.
        return hgame

    def solve(self, force=False, silent=False):
        # If the game is solved and force is False, then warn user.
        if self._is_solved and not force:
            if not silent:
                logger.warning(f"Game is solved. To solve again, call `solve(force=True)`.")
            return

        # If Base game is not solved, then solve it.
        logger.debug("Solving base game.")
        if self.base_game_sol is None:
            self.base_game_sol = solve_base_game(self.graph, self.final)

        # If P2's game is not solved, then solve it.
        self.p2_game_sol = solve_p2game(self.graph, self.final, self.fakes)

        # Determine subjectively rationalizable actions for P2.
        self.sr_acts = self.gen_sr_acts()

        # Construct hypergame.
        self.hypergame = self.construct_hypergame(self.sr_acts)
        p1_final = self.traps | self.fakes
        if p1_final - set(self.hypergame.nodes()):
            logger.critical(
                f"The following decoy states are not in hypergame: {p1_final - set(self.hypergame.nodes())}. "
                f"Setting p1_final = {set.intersection(p1_final, set(self.hypergame.nodes()))=}."
            )
            p1_final = set.intersection(p1_final, set(self.hypergame.nodes()))

        self.hypergame_sol = dtptb.SWinReach(self.hypergame, final=p1_final, player=1)
        self.hypergame_sol.solve()
        logger.debug(f"Hypergame: \nNodes:{self.hypergame.nodes(data=True)}, \nEdges:{self.hypergame.edges(keys=True)}")
        logger.debug(
            f"Base game solved. "
            f"\nFinal: {p1_final}."
            f"\nWinning nodes P2: {self.hypergame_sol.winning_nodes[2]}."
            f"\nWinning nodes P1: {self.hypergame_sol.winning_nodes[1]}."
        )

        # Save solutions
        self.winning_nodes[1] = self.hypergame_sol.winning_nodes[1]
        self.winning_nodes[2] = self.hypergame_sol.winning_nodes[2]
        self.winning_edges[1] = self.hypergame_sol.winning_edges[1]
        self.winning_edges[2] = None

        # Compute value of deception.
        try:
            self.vod = len(self.winning_nodes[1]) / (self.hypergame.number_of_nodes() - len(self.final))
        except ZeroDivisionError:
            self.vod = 0
        logger.debug(f"Value of deception: {self.vod}")

        # Mark the game as solved
        self._is_solved = True


class DASWinReach:
    def __init__(self, base_game_graph, final, traps, fakes, base_game_sol=None):
        """
        Computes deceptive sure winning region for P1 in a reachability game.

        :param base_game_graph: Base game graph.
        :param final: Set of final states in base game.
        :param traps: Set of states allocated as traps.
        :param fakes: Set of states allocated as fakes.
        :param base_game_sol: Solution of P2 game. If None, then P2's game will be constructed and solved.

        :note: `final, traps, fakes` are nodes in base_game_graph
        """
        # Input parameters:
        self.graph = base_game_graph
        self.final = final
        self.traps = traps
        self.fakes = fakes
        self.base_game_sol = base_game_sol
        self.p2_game_sol = None
        self.hypergame = None
        self.hypergame_sol = None

        # Solver parameters:
        self._is_solved = False

        # Output parameters:
        self.vod = None
        self.sr_acts = None
        self.winning_nodes = {1: set(), 2: set()}
        self.winning_edges = {1: set(), 2: set()}

    def gen_sr_acts(self):
        """
        Assume: P2's game is solved.
        :return: (dict) A map of states to SR actions.
        """
        # Use SRActs definition in Sect. 4.5 to construct SRActs.
        sr_acts = dict()
        win2 = self.p2_game_sol.winning_nodes[2]
        for state in win2:
            sr_acts[state] = set()
            if state in self.final:
                continue
            for _, next_state, action in self.graph.out_edges(state, keys=True):
                if next_state in win2:
                    sr_acts[state].add(action)

        # Return SRActs.
        return sr_acts

    def construct_hypergame(self, sr_acts):
        """
        Construct hypergame from base game and SRActs.

        The implemented construction is not the same as the one in the paper, but equivalent.
        The reason behind this is that the existing MDP solvers do not support explicit nature states.
        Thus, we transform the given game into a qualitative MDP with no nature states, but non-deterministic transitions.


        Transformation
        --------------
        1. MDP includes only P1's "non-final" states.
        2. For a P1 states `u, u'` and P2 state v, if (u, a, v) and (v, a', u') are valid transitions in the base game,
            then (u, a, u') is a valid transition in MDP.
        [Note: Here, we assume strict alternation of turns in the base game.]
        3. Introduce a single sink state `sink`. Any transition reaching a final state in base game is redirected to `sink`.
        3. Introduce a single final state `qF`. Any transition reaching a decoy state in P1's game is redirected to `qF`.
        3. Introduce a single final state `p1win`. Any SRAct that leads to P1's winning region in base game is redirected to `p1win`.
        """
        # Initialize a MDP graph.
        hgame = nx.MultiDiGraph()

        # Add states to hypergame.
        hgame.add_nodes_from((
            u for u in self.base_game_sol.winning_nodes[2]
            if u not in self.final | self.fakes | self.traps and self.graph.nodes[u]["turn"] == 1
        ))

        # hgame.add_node("qF", turn=1, label={"final"})
        # hgame.add_node("sink", turn=1, label={"sink"})
        hgame.add_node("qF")
        hgame.add_node("sink")
        hgame.add_node("p1win")

        # Add edges to hypergame.
        for u in hgame.nodes():
            # If u is final or decoy, it is sink. Self-edges at sink states are added outside this loop.
            if u == "qF" or u == "sink" or u == "p1win":
                continue

            # For each SR action of u, add a transition to the next state, if applicable.
            for a in sr_acts[u]:
                # Identify next state
                out_edges_u = self.graph.out_edges(u, keys=True)
                v = next(v for _, v, a_ in out_edges_u if a_ == a)

                # If the next state is decoy, redirect to qF.
                # If the next state is a final state in base game, redirect to sink.
                # Else, add transitions to successors of the next state.
                if v in self.traps | self.fakes:
                    hgame.add_edge(u, "qF", key=a)
                elif v in self.final:
                    hgame.add_edge(u, "sink", key=a)
                else:
                    # Get successors of v
                    successors_v = {v_ for _, v_, a_ in self.graph.out_edges(v, keys=True) if a_ in sr_acts[v]}

                    # Process each successor
                    for u_prime in successors_v:
                        # If u_prime is not in hypergame, then skip.
                        if u_prime not in hgame.nodes() and u_prime not in self.final | self.traps | self.fakes:
                            logger.critical(
                                f"Spurious transition: T({u}, {a}) -> {v}. State {v} is not in hypergame, but is reached under SRActs."
                            )
                            continue

                        # If u_prime is not P1 state, then skip. Warn that assumptions are violated.
                        # Assume 1. v must have at least one neighbor.
                        # Assume 2. u_prime is P1 state.
                        if self.graph.nodes[u_prime]["turn"] == 2:
                            logger.error(
                                f"Assumption violated: Base game is does not alternate turns. "
                                f"Spurious Transition T({v}, ??) -> {u_prime}, where {v}, {u_prime} are P2 states."
                            )
                            continue

                        if u_prime in self.traps | self.fakes:
                            hgame.add_edge(u, "qF", key=a)
                        elif u_prime in self.final:
                            hgame.add_edge(u, "sink", key=a)
                        else:
                            hgame.add_edge(u, u_prime, key=a)

            # Mark `qF` as sink.
            hgame.add_edge("qF", "qF", key="*")
            hgame.add_edge("sink", "sink", key="*")
            hgame.add_edge("p1win", "p1win", key="*")

        # Return hypergame.
        return hgame

    def compute_vod(self, sr_acts):
        """
        Computes value of deception by inverting the transformation in `construct_hypergame`.
        """
        # Get size of winning region
        daswin = self.winning_nodes[1]
        n_daswin = len(daswin)

        # Remove qF. `sink` will never be in DASWin, so we don't care about it.
        n_daswin -= 1

        # Add decoy states back.
        n_daswin += len(self.fakes) + len(self.traps)

        # Count every P2 state that has all subjectively rationalizable transitions leading into DASWin.
        win2 = self.p2_game_sol.winning_nodes[2]
        p2_states = (u for u in win2 if self.graph.nodes[u]["turn"] == 2)
        for u in p2_states:
            successors = (v for _, v, a in self.graph.out_edges(u, keys=True) if a in sr_acts[u])
            if all(v in daswin for v in successors):
                n_daswin += 1

        # Compute VOD
        return n_daswin / (len(win2) - len(self.final))

    def solve(self, force=False, silent=False):
        # If the game is solved and force is False, then warn user.
        if self._is_solved and not force:
            if not silent:
                logger.warning(f"Game is solved. To solve again, call `solve(force=True)`.")
            return

        # If Base game is not solved, then solve it.
        logger.debug("Solving base game.")
        if self.base_game_sol is None:
            self.base_game_sol = solve_base_game(self.graph, self.final)

        # If P2's game is not solved, then solve it.
        self.p2_game_sol = solve_p2game(self.graph, self.final, self.fakes)

        # Determine subjectively rationalizable actions for P2.
        self.sr_acts = self.gen_sr_acts()

        # Construct hypergame.
        self.hypergame = self.construct_hypergame(self.sr_acts)
        p1_final = {"qF"}
        self.hypergame_sol = mdp.ASWinReach(self.hypergame, final=p1_final)
        self.hypergame_sol.solve()
        logger.debug(
            f"Hypergame solved. "
            f"\nFinal: {p1_final}."
            f"\nWinning nodes P1: {self.hypergame_sol.winning_nodes[1]}."
        )

        # Determine P1's DASWin region by inverting the transformation to MDP.
        self.winning_nodes[1] = self.invert_projection(self.hypergame_sol, self.sr_acts)
        logger.debug(f"Hypergame: \nNodes:{self.hypergame.nodes(data=True)}, \nEdges:{self.hypergame.edges(keys=True)}")
        logger.debug(
            f"Hypergame solved. "
            f"\nFinal: {p1_final}."
            f"\nWinning nodes P1: {self.hypergame_sol.winning_nodes[1]}."
        )
        # # Save solutions
        # self.winning_nodes[1] = hypergame_sol.winning_nodes[1]
        # self.winning_nodes[2] = hypergame_sol.winning_nodes[2]
        # self.winning_edges[1] = hypergame_sol.winning_edges[1]
        # self.winning_edges[2] = None

        # Compute value of deception.
        try:
            self.vod = len(self.winning_nodes[1]) / (len(self.base_game_sol.winning_nodes[2]) - len(self.final))
        except ZeroDivisionError:
            self.vod = 0.0

        logger.debug(f"Value of deception: {self.vod}")

        # Mark the game as solved
        self._is_solved = True

    def invert_projection(self, hypergame_sol, sr_acts):
        # Get size of winning region
        daswin = hypergame_sol.winning_nodes[1]

        # Replace qF with all decoy states.
        # `sink` will never be in DASWin, so we don't care about it.
        # `p1win` will never be in DASWin, so we don't care about it.
        daswin -= {"qF"}
        daswin |= self.fakes | self.traps

        # Add every P2 state that has all subjectively rationalizable transitions leading into DASWin.
        win2 = self.p2_game_sol.winning_nodes[2] - self.final
        p2_states = (u for u in win2 if self.graph.nodes[u]["turn"] == 2)
        for u in p2_states:
            successors = (v for _, v, a in self.graph.out_edges(u, keys=True) if a in sr_acts[u])
            if all(v in daswin for v in successors):
                daswin.add(u)

        return daswin


def solve_p2game(base_game_graph, final, fakes):
    # p2game_model = p2_game(base_game_graph, traps, fakes)
    # p2game_graph = game.to_graph(p2game_model)
    # final = {st for st in p2game_graph.nodes() if "final" in p2game_graph.nodes[st]["label"]}
    if len(final | fakes) == 0:
        logger.warning("P2 game has no final states.")

    p2game_solver = dtptb.SWinReach(base_game_graph, final=final | fakes, player=2)
    p2game_solver.solve()
    logger.debug(
        f"P2 game solved. "
        f"\nFinal: {final}, Fakes: {fakes}"
        f"\nWinning nodes P2: {p2game_solver.winning_nodes[2]}."
        f"\nWinning nodes P1: {p2game_solver.winning_nodes[1]}."
    )
    return p2game_solver


def solve_base_game(base_game_graph, final):
    if len(final) == 0:
        logger.warning("Base game has no final states.")

    base_game_solver = dtptb.SWinReach(base_game_graph, final=final, player=2)
    base_game_solver.solve()
    logger.debug(
        f"Base game solved. "
        f"\nFinal: {final}."
        f"\nWinning nodes P2: {base_game_solver.winning_nodes[2]}."
        f"\nWinning nodes P1: {base_game_solver.winning_nodes[1]}."
    )
    return base_game_solver

#
# def p2_game(base_game_model, traps, fakes):
#     """
#     Constructs P2's game graph.
#
#     :param base_game_model: Base game model.
#     :param traps: Set of states allocated as traps.
#     :param fakes: Set of states allocated as fakes.
#     :return: P2's game model.
#     """
#     p2game_model = copy.deepcopy(base_game_model)
#     p2game_model["label"].update({state: {"final"} for state in fakes})
#     return p2game_model
