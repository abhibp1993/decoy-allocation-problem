"""
The results for seed 831 in Experiment 5 violated assumptions.
VoD(dswin, traps) > VoD(daswin, fakes) was observed, but not expected.
This script investigates the cause of this violation.
"""

import game
import os
from solvers import *

logger.add(os.path.join("out", "investigate_seed1357.log"), level="DEBUG")

if __name__ == '__main__':
    n_nodes = 20
    n_max_out_degree = 3
    n_final = 2
    seed = 1357

    # Load model
    model = game.load_model(os.path.join("out", f"game{seed}.model"))

    # Solve base game
    base_game_graph = game.to_graph(model)
    final = {u for u in base_game_graph.nodes() if "goal" in base_game_graph.nodes[u]["label"]}
    base_game_sol = solve_base_game(base_game_graph, final)
    win2 = base_game_sol.winning_nodes[2]

    # Q. What is VoD if first fake was placed at where the first trap was placed?
    dswin = DSWinReach(base_game_graph, final=final, traps=set(), fakes={101}, base_game_sol=base_game_sol)
    dswin.solve()
    logger.success("Q. What is VoD if first fake was placed at where the first trap was placed?\n"
                   f"A. VoD(dswin, trap={{101}})=0.6805, VoD(dswin,fake={{101}})={dswin.vod}")

    # Q. What is VoD if first two fakes were placed at where the first two traps were placed?
    dswin = DSWinReach(base_game_graph, final=final, traps=set(), fakes={101, 74}, base_game_sol=base_game_sol)
    dswin.solve()
    logger.success("Q. What is VoD if first two fakes were placed at where the first two traps were placed?\n"
                   f"A. VoD(dswin, trap={{101,74}})=0.8055, VoD(dswin,fake={{101,74}})={dswin.vod}")

    # Q. What is VoD if first three fakes were placed at where the first three traps were placed?
    dswin = DSWinReach(base_game_graph, final=final, traps=set(), fakes={101, 74, 80}, base_game_sol=base_game_sol)
    dswin.solve()
    logger.success("Q. What is VoD if first three fakes were placed at where the first three traps were placed?\n"
                   f"A. VoD(dswin, trap={{101,74, 80}})=0.8472, VoD(dswin,fake={{101,74, 80}})={dswin.vod}")
