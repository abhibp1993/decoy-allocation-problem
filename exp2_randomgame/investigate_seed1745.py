"""
The results for seed 831 in Experiment 5 violated assumptions.
VoD(dswin, traps) > VoD(daswin, fakes) was observed, but not expected.
This script investigates the cause of this violation.
"""

import game
import os
from solvers import *

logger.add(os.path.join("out", "investigate_seed1745_.log"), level="DEBUG")

if __name__ == '__main__':
    n_nodes = 20
    n_max_out_degree = 3
    n_final = 2
    seed = 1745

    # Load model
    model = game.load_model(os.path.join("out", f"game{seed}.model"))

    # Solve base game
    base_game_graph = game.to_graph(model)
    final = {u for u in base_game_graph.nodes() if "goal" in base_game_graph.nodes[u]["label"]}
    base_game_sol = solve_base_game(base_game_graph, final)
    win2 = base_game_sol.winning_nodes[2]

    # Q. What is VoD if first fake was placed at where the first trap was placed?
    dswin = DSWinReach(base_game_graph, final=final, traps=set(), fakes={105}, base_game_sol=base_game_sol)
    dswin.solve()
    logger.success("Q. What is VoD if first fake was placed at where the first trap was placed?\n"
                   f"A. VoD(daswin, trap={{105}})=0.7113, VoD(dswin,fake={{105}})={dswin.vod}")

    # Q. What is VoD if first two fakes were placed at where the first two traps were placed?
    dswin = DSWinReach(base_game_graph, final=final, traps=set(), fakes={105, 123}, base_game_sol=base_game_sol)
    dswin.solve()
    logger.success("Q. What is VoD if first two fakes were placed at where the first two traps were placed?\n"
                   f"A. VoD(daswin, trap={{105, 123}})=0.8969, VoD(dswin,fake={{105, 123}})={dswin.vod}")

    # Q. What is VoD if first three fakes were placed at where the first three traps were placed?
    dswin = DSWinReach(base_game_graph, final=final, traps=set(), fakes={105, 123, 130}, base_game_sol=base_game_sol)
    dswin.solve()
    logger.success("Q. What is VoD if first three fakes were placed at where the first three traps were placed?\n"
                   f"A. VoD(dswin, trap={{105, 123, 130}})=0.9381, VoD(dswin,fake={{105, 123, 130}})={dswin.vod}")
