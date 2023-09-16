import game
import random


class RandomGame(game.DTPTB):
    def __init__(self, n_nodes, max_outdegree, n_final, seed=None, **kwargs):
        super().__init__(**kwargs)
        self.n_nodes = n_nodes
        self.max_outdegree = max_outdegree
        self._final = {f"s{i}" for i in random.choices(range(n_nodes), k=n_final)}
        self._seed = random.randint(0, 1000) if seed is None else seed

        random.seed(seed)
        self._states = {f"s{i}" for i in range(self.n_nodes)}
        self._turn = {f"s{i}": 1 if i % 2 == 1 else 2 for i in range(self.n_nodes)}
        self._actions = dict()
        for state in self._states:
            n_actions = random.randint(1, self.max_outdegree)
            if self._turn[state] == 1:
                self._actions[state] = {f"a{i}" for i in range(n_actions)}
            else:
                self._actions[state] = {f"b{i}" for i in range(n_actions)}
        self._delta = dict()
        for state in self._states:
            self._delta[state] = dict()
            for action in self._actions[state]:
                iter_count = 0
                while iter_count < 100:
                    iter_count += 1
                    next_state_id = random.randint(0, self.n_nodes - 1)
                    if (self.turn(state) == 1 and next_state_id % 2 == 0) or (self.turn(state) == 2 and next_state_id % 2 == 1):
                        self._delta[state][action] = f"s{next_state_id}"
        self._atoms = {"goal"}
        self._label = {state: {"goal"} if state in self._final else set() for state in self._states}

    def init_states(self):
        return self._states

    def is_state_valid(self, state):
        return True

    def turn(self, state):
        return self._turn[state]

    def actions(self, state):
        return self._actions[state]

    def delta(self, state, action):
        return self._delta[state][action]

    def atoms(self):
        return self._atoms

    def label(self, state):
        return self._label[state]
