import game
import ioutils
import os
import sys

from solvers import *
from gwutils import *
from loguru import logger

# PARAMETERS FOR GAME GENERATION
DIM = (7, 7)
REAL_CHEESE = [(1, 6), (4, 6)]
OBS = [(0, 4), (2, 4), (4, 4), (6, 4)]

# OUTPUT DIRECTORY
OUTPUT_DIRECTORY = os.path.join("out")

# LOGGER CONFIGURATION
logger.remove()
logger.add(
    sys.stderr,
    level="INFO",
    filter=lambda record: "The following decoy states are not in hypergame" not in record["message"]
)

logger.add(os.path.join(OUTPUT_DIRECTORY, "exp1_gridworld.log"), level="DEBUG")


class Gridworld(game.Game):
    def __init__(self, dim, obs, real_cheese):
        super(Gridworld, self).__init__(type_game=game.TYPE_DTPTB)
        self.rows = dim[0]
        self.cols = dim[1]
        self.obs = obs
        self.real_cheese = real_cheese

    def __str__(self):
        delta = {(st, a): self.delta(st, a) for st in self.states() for a in self.actions(st)}
        final = {st for st in self.states() if self.final(st)}
        return f"{self.states()=}\n" \
               f"{delta=}\n" \
               f"{final=}\n"

    def init_states(self):
        """ (r1, c1): tom (defender), (r2, c2): jerry (attacker) """
        return [(r1, c1, r2, c2, t)
                for r1 in range(self.rows)
                for c1 in range(self.cols)
                for r2 in range(self.rows)
                for c2 in range(self.cols)
                for t in [1, 2]
                if (r1, c1) not in self.obs and (r2, c2) not in self.obs
                ]

    def is_state_valid(self, state) -> bool:
        r1, c1, r2, c2, t = state
        if (r1, c1) in self.obs and (r2, c2) in self.obs:
            return False

        if 0 <= r1 < self.rows and 0 <= c1 < self.cols and 0 <= r2 < self.rows and 0 <= c2 < self.cols:
            return True

    def turn(self, state):
        return state[-1]

    def actions(self, state=None):
        return [GW_ACT_N, GW_ACT_E, GW_ACT_S, GW_ACT_W]

    def delta(self, state, act):
        turn = self.turn(state)

        if state[0:2] == state[2:4]:
            return state[0:4] + ((1,) if turn == 2 else (2,))

        if turn == 1:
            r, c = state[0:2]
        else:
            r, c = state[2:4]

        next_r, next_c = move((r, c), act)
        next_r, next_c = bouncy_wall((r, c), [(next_r, next_c)], (self.rows, self.cols))[0]
        next_r, next_c = bouncy_obstacle((r, c), [(next_r, next_c)], self.obs)[0]

        if turn == 1:
            return (next_r, next_c) + state[2:4] + (2,)
        else:
            return state[0:2] + (next_r, next_c) + (1,)

    def final(self, state):
        return state in [(r1, c1, r2, c2, t)
                         for r2, c2 in self.real_cheese
                         for r1 in range(self.rows)
                         for c1 in range(self.cols)
                         for t in range(1, 3)
                         if (r2, c2) not in self.obs and (r1, c1) not in self.obs
                         ]

    def jerry_equiv(self, cell):
        """ Returns states in which Jerry is at given cell """
        return {
            (r1, c1) + cell + (t,)
            for r1 in range(self.rows)
            for c1 in range(self.cols)
            for t in range(1, 3)
            if (r1, c1) not in self.obs
        }

    def atoms(self):
        return {"caught", "cheese"}

    def label(self, state):
        r1, c1, r2, c2, t = state
        if (r1, c1) == (r2, c2):
            return {"caught"}
        elif (r2, c2) in self.real_cheese:
            return {"cheese"}
        else:
            return set()


def main():
    # Instantiate gridworld game
    gw = Gridworld(DIM, OBS, REAL_CHEESE)
    model = gw.build_model()
    ioutils.to_json(os.path.join(OUTPUT_DIRECTORY, "gridworld.json"), model)

    # Solve base game
    base_game_graph = game.to_graph(model)
    final = {uid for uid, u in model["states"].items() if u[2:4] in REAL_CHEESE}
    # base_game_sol = solve_base_game(base_game_graph, final)

    # Determine decoy candidates
    candidates = dict()
    blocked_cells = OBS + REAL_CHEESE
    state2node = {state: node for node, state in model["states"].items()}
    for cell in {(r, c) for r in range(7) for c in range(7) if (r, c) not in blocked_cells}:
        candidates[cell] = {state2node[state] for state in gw.jerry_equiv(cell)}

    # # Uncomment to verify candidates
    # for key, value in candidates.items():
    #     print(f"\n{key}: {[model['states'][i] for i in value]}")

    # Allocate decoys: 3 cases
    # Case I: 2 fake, 0 trap
    logger.info(f"---------------------- Fakes: 2, Traps: 0 ----------------------")
    dswin_f2t0 = DecoyAllocator(
        p1game=base_game_graph,
        true_final=final,
        n_traps=0,
        n_fakes=2,
        candidates=candidates,
        sol_concept=DecoyAllocator.SWin
    )
    dswin_f2t0.solve()

    # Case II: 1 fake, 1 trap
    logger.info(f"---------------------- Fakes: 1, Traps: 1 ----------------------")
    dswin_f1t1 = DecoyAllocator(
        p1game=base_game_graph,
        true_final=final,
        n_traps=1,
        n_fakes=1,
        candidates=candidates,
        sol_concept=DecoyAllocator.SWin
    )
    dswin_f1t1.solve()

    # # Case III: 0 fake, 2 trap
    logger.info(f"---------------------- Fakes: 0, Traps: 2 ----------------------")
    dswin_f0t2 = DecoyAllocator(
        p1game=base_game_graph,
        true_final=final,
        n_traps=2,
        n_fakes=0,
        candidates=candidates,
        sol_concept=DecoyAllocator.SWin
    )
    dswin_f0t2.solve()

    # Print results
    print(f"{dswin_f2t0.best_decoys()=}")
    print(f"{dswin_f1t1.best_decoys()=}")
    print(f"{dswin_f0t2.best_decoys()=}")

    ioutils.to_json(os.path.join(OUTPUT_DIRECTORY, "dswin_f2t0_data.json"), dswin_f2t0.data())
    ioutils.to_json(os.path.join(OUTPUT_DIRECTORY, "dswin_f1t1_data.json"), dswin_f1t1.data())
    ioutils.to_json(os.path.join(OUTPUT_DIRECTORY, "dswin_f0t2_data.json"), dswin_f0t2.data())

    ioutils.to_json(os.path.join(OUTPUT_DIRECTORY, "dswin_f2t0_decoys.json"), dswin_f2t0.best_decoys())
    ioutils.to_json(os.path.join(OUTPUT_DIRECTORY, "dswin_f1t1_decoys.json"), dswin_f1t1.best_decoys())
    ioutils.to_json(os.path.join(OUTPUT_DIRECTORY, "dswin_f0t2_decoys.json"), dswin_f0t2.best_decoys())


if __name__ == '__main__':
    main()
