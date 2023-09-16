"""
A class to represent a game on graph.
"""

from __future__ import annotations
import ioutils
import networkx as nx
import numpy as np
import pickle
from functools import partial
from loguru import logger
from tqdm import tqdm

__author__ = "Abhishek N. Kulkarni"
__date__ = "September 1, 2023"

# =============================================================================
# GLOBALS
# =============================================================================
# Game types
TYPE_TSYS = "TransitionSystem"
TYPE_MDP = "MDP"
TYPE_QUALITATIVE_MDP = "QualitativeMDP"
TYPE_DTPTB = "DTPTB"

# Type of transition functions
TRANS_DETERMINISTIC = "deterministic"
TRANS_NON_DETERMINISTIC = "non-deterministic"
TRANS_PROBABILISTIC = "probabilistic"


# =============================================================================
# Game class
# =============================================================================
class Game:
    __hash__ = object.__hash__

    def __init__(self, type_game=TYPE_TSYS, **kwargs):
        """
        Defines a game on graph.

        :param type_game: (str) Type of game.
            Supported types: {TSYS, MDP, QUALITATIVE_MDP, DTPTB}.
            When type is TSYS, user must provide the keyword argument `type_transitions`.
            In other cases, the type of transition function is inferred from the type of game.

        :param type_transitions: (str) Type of transition function.
            Supported types: {TRANS_DETERMINISTIC, TRANS_NON_DETERMINISTIC, TRANS_PROBABILISTIC}.

        :param states: (list) List of states.
        :param init_states: (list) List of initial states.
        :param transitions: (dict) Transition function. Format of transitions depends on type_transitions.
            * "deterministic": (dict) Format: {state: {action: next_state}}.
            * "non-deterministic": (dict) Format: {state: {action: {next_state}}}.
            * "probabilistic": (dict) Format: {state: {action: {next_state: probability}}}.
        :param actions: (dict/set) List of actions. Two formats are supported:
            * (dict) Format: {state: {action}}. Dictionary defines the set of actions enabled at given state.
            * (set) Set of actions. In this case, the given set of actions is assumed to be enabled at all states.
        :param atoms: (list) List of atomic propositions.
        :param label: (dict) Labeling function. Format: {state: {atom}}.
        :param turn: (dict) Turn function. Format: {state: player}.

        :note: There are two ways to define a game:
            1. Non-parameterized: All states, actions, transitions, etc. are explicitly defined.
                ```python
                g = Game(
                        type_game=DTPTB,
                        states=[1, 2, 3],
                        init_states=[1],
                        transitions={1: {1: 2, 2: 3}, 2: {1: 3}, 3: {1: 1}},
                        actions={1: {1, 2}, 2: {1}, 3: {1}},
                        atoms=[1, 2],
                        label={1: {1}, 2: {2}, 3: {1, 2}}
                        turn={1: 1, 2: 2, 3: 1}
                        )
                ```

            2. Parameterized: In this case, user must derive a class from Game and implement the abstract methods.
                ```python
                class MyGame(Game):
                    def __init__(self, param1, param2, **kwargs):
                        super().__init__(type_game=DTPTB, **kwargs)
                        self.param1 = param1
                        self.param2 = param2

                    def init_states(self):
                        return set(range(self.param1))

                    def actions(self, state):
                        return set(range(self.param2))

                    ...
                ```

        """
        # Game representation
        self._type_game = type_game
        self._type_transitions = kwargs.get("type_transitions", None)
        self._num_players = kwargs.get("num_players", None)

        # Non-parametric instantiation objects
        self._states = kwargs.get("states", None)
        self._actions = kwargs.get("actions", None)
        self._transitions = kwargs.get("transitions", None)
        self._init_states = kwargs.get("init_states", None)
        self._atoms = kwargs.get("atoms", None)
        self._label = kwargs.get("label", None)
        self._turn = kwargs.get("turn", None)

        # Basic setup based on type of game
        if self._type_game in TYPE_MDP:
            self._type_transitions = TRANS_PROBABILISTIC
            self._num_players = 1
        if self._type_game in TYPE_QUALITATIVE_MDP:
            self._type_transitions = TRANS_NON_DETERMINISTIC
            self._num_players = 1
        elif self._type_game == TYPE_DTPTB:
            self._type_transitions = TRANS_DETERMINISTIC
            self._num_players = 2
        elif self._type_game == TYPE_TSYS:
            self._num_players = None
            if self._type_transitions is None:
                raise ValueError("Type of transition function must be provided for TransitionSystem.")

    def __str__(self):
        return f"<{self._type_game} object at {id(self)}>"

    def __getstate__(self):
        return self.build_model()

    def __setstate__(self, state):
        raise NotImplementedError("Method not implemented.")

    def states(self) -> set:
        """
        The set of all states in the game.

        :note: Sometimes constructing a full game is not feasible. In such cases, it is recommended to define init_states() and
            is_state_valid() methods instead of states(). In this case, the build_model() will include only the states reachable from
            the initial states.

        :return: (set) Set of all states in the game.
        """
        if self._states is not None:
            return self._states
        raise NotImplementedError("Method not implemented.")

    def init_states(self) -> set:
        """
        Initial states of the game.

        :return: (set) Set of initial states.
        """
        if self._init_states is not None:
            return set(self._init_states)

        raise NotImplementedError("Must be implemented by user.")

    def is_state_valid(self, state) -> bool:
        """
        Returns True if the state is a valid state.
        """
        if self._states is not None:
            return True
        raise NotImplementedError("Must be implemented by user.")

    def actions(self, state) -> set | dict:
        """ Actions enabled at given state. """
        if self._actions is not None:
            if isinstance(self._actions, dict):
                return set(self._actions[state])
            return set(self._actions)
        raise NotImplementedError("Must be implemented by user.")

    def delta(self, state, action):
        """
        Transition function.

        :param state: A valid state.
        :param action: An action enabled at given state.
        :return: (state | set | dict) Next state(s) after taking given action at given state.
            Format depends on type_transitions. (See documentation of the class for details on the format of transition function.)

        """
        if self._transitions is not None:
            return self._transitions[state][action]
        raise NotImplementedError("Must be implemented by user.")

    def atoms(self):
        """
        Set of atomic propositions.
        :return: (set) Set of atomic propositions.
        """
        if self._atoms is not None:
            return set(self._atoms)
        raise NotImplementedError("Must be implemented by user.")

    def label(self, state):
        """
        Labeling function.

        :param state: A valid state
        :return: (set) Set of atomic propositions that evaluate to `true` at given state.
        """
        if self._label is not None:
            return self._label[state]
        raise NotImplementedError("Must be implemented by user.")

    def turn(self, state):
        """
        Returns the player who controls the staet. Applicable only to turn-based games. Otherwise, the function will be ignored.
        :param state: A valid state.
        :return: (int) Player whose turn it is at given state. `1` for player 1, `2` for player 2.
        """
        if self._turn is not None:
            return self._turn[state]
        raise NotImplementedError("Must be implemented by user.")

    def is_turn_based(self):
        if self._type_game == TYPE_DTPTB:
            return True
        return False

    def build_model(self, **kwargs):
        """
        Build the game model.

        :param validate_init_states: (bool) If False, the method will skip checking if the initial states are valid. Default: True.
        :param progress_bar: (bool) If True, the method will display a progress bar. Default: False.
        :param ignore_invalid_transitions: (bool) If True, the method will ignore invalid states. Default: False.
        :param get_states2index: (bool) If True, the method will return (model, states2index:dict). Default: False.
        """

        # Helper functions to process transitions
        def trans_deterministic(num_edges_):
            for a, v in result:
                if not is_state_valid(v):
                    logger.error(f"delta({u}, {a}) reaches invalid state {v}.")
                    if not kwargs.get("ignore_invalid_transitions", False):
                        continue
                    raise ValueError(f"delta({u}, {a}) reaches invalid state {v}.")

                if v not in states:
                    vid = len(states)
                    states[v] = vid
                    transitions[vid] = dict()
                    queue.append(vid)
                else:
                    vid = states[v]

                transitions[uid][a] = vid
                num_edges_ += 1

            return num_edges_

        def trans_non_deterministic(num_edges_):
            for a, next_states in result:
                invalid_next_states = {v for v in next_states if not is_state_valid(v)}
                if len(invalid_next_states) > 0:
                    logger.error(f"delta({u}, {a}) reaches invalid states {invalid_states}.")
                    if not kwargs.get("ignore_invalid_transitions", False):
                        raise ValueError(f"delta({u}, {a}) reaches invalid state {invalid_next_states}.")
                    next_states -= invalid_next_states

                for v in next_states:
                    if v not in states:
                        vid = len(states)
                        states[v] = vid
                        transitions[vid] = dict()
                        queue.append(vid)
                    else:
                        vid = states[v]

                    if a not in transitions[uid]:
                        transitions[uid][a] = set()

                    transitions[uid][a].add(vid)
                    num_edges_ += 1

            return num_edges_

        def trans_probabilistic(num_edges_):
            for a, next_states in result:
                invalid_next_states = {v for v in next_states if not is_state_valid(v)}
                if len(invalid_next_states) > 0:
                    logger.error(f"delta({u}, {a}) reaches invalid states {invalid_states}.")
                    if not kwargs.get("ignore_invalid_transitions", False):
                        raise ValueError(f"delta({u}, {a}) reaches invalid state {invalid_next_states}.")
                    next_states -= invalid_next_states

                if abs(sum(next_states.values()) - 1) > 1e-6:
                    logger.error(f"Probabilities of next states do not sum to 1. \n"
                                 f"delta({u}, {a}) -> {next_states}")
                    raise AssertionError("Probabilities of next states do not sum to 1.")

                for v, p in next_states.items():
                    if v not in states:
                        vid = len(states)
                        states[v] = vid
                        transitions[vid] = dict()
                        queue.append(vid)
                    else:
                        vid = states[v]

                    if a not in transitions[uid]:
                        transitions[uid][a] = dict()

                    transitions[uid][a].update({vid: p})
                    num_edges_ += 1

            return num_edges_

        # Default validity check
        def default_state_validity(state):
            return True

        # Initialize model
        model = dict()

        # Store game metadata
        model["type_game"] = self._type_game
        model["num_players"] = self._num_players
        model["type_transitions"] = self._type_transitions

        # Determine transition update function
        if self._type_transitions == TRANS_DETERMINISTIC:
            trans_update = trans_deterministic
        elif self._type_transitions == TRANS_NON_DETERMINISTIC:
            trans_update = trans_non_deterministic
        else:  # self._type_transitions == TRANS_DETERMINISTIC:
            trans_update = trans_probabilistic

        # Initialize states
        try:
            states = {state: idx for idx, state in enumerate(self.states())}
            is_state_valid = default_state_validity
        except NotImplementedError:
            states = {state: idx for idx, state in enumerate(self.init_states())}
            is_state_valid = self.is_state_valid

        # Check validity of initial states
        if kwargs.get("validate_init_states", True):
            invalid_states = {state for state in states.keys() if not is_state_valid(state)}
            if len(invalid_states) > 0:
                raise ValueError(f"Invalid initial states: {invalid_states}")

        # Reachable states computation
        queue = list(states.keys())
        transitions = {uid: dict() for uid in states.values()}
        actions = set()
        num_edges = 0

        with tqdm(total=1, desc="Building model...",
                  disable=not kwargs.get("progress_bar", False)) as pbar:
            while len(queue) > 0:
                # Update progress_bar
                pbar.total = len(queue) + len(states)
                pbar.update(1)

                # Pop state from queue
                u = queue.pop(0)
                uid = states[u]

                # Get enabled actions at the state
                act_u = self.actions(u)
                actions.update(act_u)

                # Apply each action to state
                result = zip(act_u, map(self.delta, [u] * len(act_u), act_u))

                # Update newly visited states and transitions
                num_edges = trans_update(num_edges)

        # Populate other aspects of model
        model["states"] = {idx: state for state, idx in states.items()}
        model["init_states"] = [states[state] for state in self.init_states()]
        model["actions"] = actions
        model["transitions"] = transitions
        model["num_transitions"] = num_edges

        if self.is_turn_based():
            model["turn"] = {states[state]: self.turn(state) for state in states}

        try:
            model["atoms"] = set(self.atoms())
        except NotImplementedError:
            model["atoms"] = set()

        try:
            model["label"] = {states[u]: self.label(u) for u in states}
        except NotImplementedError:
            if len(model["atoms"]) > 0:
                logger.critical("Labeling function could not be serialized. NotImplementedError occurred.")

        # Show log message and return model
        logger.success(
            f"Built model with "
            f"|V|={len(states)}, "
            f"|E|={num_edges}, "
            f"|A|={len(model['actions'])}, "
            f"|AP|={len(model['atoms'])}."
        )
        if kwargs.get("get_states2index", False):
            return model, states
        return model


# =============================================================================
# Utility classes
# =============================================================================
class MDP(Game):
    def __init__(self, **kwargs):
        super().__init__(type_game=TYPE_MDP, **kwargs)


class QualitativeMDP(Game):
    def __init__(self, **kwargs):
        super().__init__(type_game=TYPE_QUALITATIVE_MDP, **kwargs)


class DTPTB(Game):
    def __init__(self, **kwargs):
        super().__init__(type_game=TYPE_DTPTB, **kwargs)


class TransitionSystem(Game):
    def __init__(self, **kwargs):
        super().__init__(type_game=TYPE_TSYS, **kwargs)


# =============================================================================
# Utility functions
# =============================================================================
def to_graph(model):
    """
    Converts the model to an equivalent graph. The generated graph carries all model properties as node and graph attributes.

    :param model: (dict) Model representing a game on graph.
    :return: (nx.MultiDiGraph) Graph representation of the model.
    """
    # Preprocessing
    states = model["states"]
    type_game = model["type_game"]
    type_transitions = model["type_transitions"]

    # Initialize graph
    graph = nx.MultiDiGraph()

    # Add nodes
    if "turn" in model:
        turn = model["turn"]
        graph.add_nodes_from(((u, {"state": state, "turn": turn[u]}) for u, state in states.items()))
    else:
        graph.add_nodes_from(((u, {"state": state}) for u, state in states.items()))

    # Add edges
    transitions = model["transitions"]
    if type_transitions == TRANS_DETERMINISTIC:
        graph.add_edges_from((
            (u, transitions[u][a], a, {"action": a})
            for u in transitions
            for a in transitions[u]
        ))
    elif type_transitions == TRANS_NON_DETERMINISTIC:
        graph.add_edges_from((
            (u, v, a, {"action": a})
            for u in transitions
            for a in transitions[u]
            for v in transitions[u][a]
        ))
    elif type_transitions == TRANS_PROBABILISTIC:
        graph.add_edges_from((
            (u, v, a, {"action": a, "probability": p})
            for u in transitions
            for a in transitions[u]
            for v, p in transitions[u][a].items()
        ))
    else:
        raise ValueError(f"Invalid type of transition function: {type_transitions}")

    # Sanity check
    assert graph.number_of_edges() == model["num_transitions"], \
        "Sanity check failed. Number of edges in graph does not match the number of transitions in model."

    # Property: label
    if "label" in model:
        for u in graph.nodes():
            graph.nodes[u]["label"] = model["label"][u]

    # Property: atoms
    if "atoms" in model:
        graph.graph["atoms"] = model["atoms"]

    # Property: type_game, type_transitions, init_states and num_players
    graph.graph["type_game"] = type_game
    graph.graph["type_transitions"] = type_transitions
    graph.graph["num_players"] = model["num_players"]
    graph.graph["init_states"] = model["init_states"]

    return graph


def to_matrix(model):
    """
    Converts the model to adjacency matrix representation of the game on graph.

    :param model: (dict) Model representing a game on graph.
    :return: (tuple[np.ndarray, dict]) An M x M x A matrix. The third dimension is the action dimension.
        The second element in the tuple maps the third dimension of matrix to the action.

        For deterministic models, the matrix is a binary matrix.
        For non-deterministic models, the matrix is a boolean matrix. Each non-zero element indicates the presence of an edge.
        For probabilistic models, the matrix is a float matrix. Each non-zero element indicates the probability of the edge.
    """
    # Preprocess input model
    actions = {a: idx for idx, a in enumerate(model["actions"])}
    states = model["states"]
    transitions = model["transitions"]
    type_transitions = model["type_transitions"]

    # Initialize matrix
    if type_transitions in [TRANS_DETERMINISTIC, TRANS_NON_DETERMINISTIC]:
        mat = np.zeros((len(states), len(states), len(actions)), dtype=np.uint8)
    else:
        mat = np.zeros((len(states), len(states), len(actions)), dtype=np.float32)

    # Populate matrix
    for u in transitions:
        for a in transitions[u]:
            if type_transitions == TRANS_DETERMINISTIC:
                mat[u, transitions[u][a], actions[a]] = 1

            elif type_transitions == TRANS_NON_DETERMINISTIC:
                for v in transitions[u][a]:
                    mat[u, v, actions[a]] = 1

            elif type_transitions == TRANS_PROBABILISTIC:
                for v, p in transitions[u][a].items():
                    mat[u, v, actions[a]] = p

    return mat, actions


def save_model(model, fname, protocol="json"):
    """
    Saves the model to a file.

    :param model: (dict) Model dictionary.
    :param fname: (str) Path to file.
    :param protocol: (str) Serialization protocol. {"json", "pickle"}
    """
    if protocol == "json":
        ioutils.to_json(fname, model)
    elif protocol == "pickle":
        with open(fname, "wb") as f:
            pickle.dump(model, f)
    else:
        raise NotImplementedError(f"Protocol '{protocol}' is not supported by Game.save_model() method.")


def load_model(fname, protocol="json"):
    """
    Loads the model from a file.

    :param fname: (str) Path to file.
    :param protocol: (str) Serialization protocol. {"json", "pickle"}
    :return: (dict) Model dictionary.
    """
    if protocol == "json":
        model = ioutils.from_json(fname)

        model["states"] = {int(uid): state for uid, state in model["states"].items()}
        model["label"] = {int(uid): label for uid, label in model["label"].items()}
        # model["actions"] = {int(uid): action for uid, action in model["actions"]}
        # model["atoms"] = {int(uid): atom for uid, atom in model["atoms"]}

        serialized_trans = model["transitions"]
        trans = dict()
        for uid, uid_dict in serialized_trans.items():
            trans[int(uid)] = dict()
            for action, aid_value in uid_dict.items():
                trans[int(uid)][action] = dict()
                if isinstance(aid_value, dict):
                    for vid, prob in aid_value.items():
                        trans[int(uid)][action].update({int(vid): prob})
                else:
                    trans[int(uid)][action] = int(aid_value)
        model["transitions"] = trans

        if "turn" in model:
            model["turn"] = {int(uid): turn for uid, turn in model["turn"].items()}

        return model

    elif protocol == "pickle":
        with open(fname, "rb") as f:
            return pickle.load(f)

    else:
        raise NotImplementedError(f"Protocol '{protocol}' is not supported by Game.load_model() method.")
