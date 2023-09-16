"""
In this experiment, we generate 1000 random games.
Solve each game using DSWinReach and DASWinReach algorithms.
Automatically compare the VoD.
"""

import game
import os, sys
import random
import vizutils as viz
from solvers import *
from game_generator import RandomGame
import matplotlib.pyplot as plt
import numpy as np

OUTPUT_DIRECTORY = os.path.join("out")
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add(os.path.join(OUTPUT_DIRECTORY, "exp2_randomgame.log"), level="INFO")


def solve_one_game(seed):
    n_nodes = 150
    n_max_out_degree = 5
    n_final = 10
    n_decoys = 5
    random.seed(seed)

    # ============================
    # Select one of the two blocks
    # ============================
    # Generate random game
    gm = RandomGame(n_nodes, n_max_out_degree, n_final, seed)
    model = gm.build_model()
    game.save_model(model, os.path.join(OUTPUT_DIRECTORY, f"game{seed}.model"))
    # ============================
    # model = game.load_model(os.path.join(OUTPUT_DIRECTORY, f"game{seed}.model"))
    # ============================

    # Solve base game
    base_game_graph = game.to_graph(model)
    final = {u for u in base_game_graph.nodes() if "goal" in base_game_graph.nodes[u]["label"]}
    base_game_sol = solve_base_game(base_game_graph, final)
    win2 = base_game_sol.winning_nodes[2]
    viz.save_base_game(base_game_graph, base_game_sol, os.path.join(OUTPUT_DIRECTORY, f"game{seed}_base_game_graph.png"), final=final)

    # Determine decoy candidates
    candidates = {u: {u} for u in win2 - final}

    # Solve using DSWin for fakes
    logger.info(f"---------------------- dswin_fakes: {seed}----------------------")
    dswin_fakes = DecoyAllocator(
        p1game=base_game_graph,
        true_final=final,
        n_traps=0,
        n_fakes=n_decoys,
        candidates=candidates,
        sol_concept=DecoyAllocator.SWin
    )
    dswin_fakes.solve()

    # Solve using DSWin for traps
    logger.info(f"---------------------- dswin_traps: {seed}----------------------")
    dswin_traps = DecoyAllocator(
        p1game=base_game_graph,
        true_final=final,
        n_traps=n_decoys,
        n_fakes=0,
        candidates=candidates,
        sol_concept=DecoyAllocator.SWin
    )
    dswin_traps.solve()

    # Solve using DASWin for fakes
    logger.info(f"---------------------- daswin_fakes: {seed}----------------------")
    daswin_fakes = DecoyAllocator(
        p1game=base_game_graph,
        true_final=final,
        n_traps=0,
        n_fakes=n_decoys,
        candidates=candidates,
        sol_concept=DecoyAllocator.ASWin
    )
    daswin_fakes.solve()

    # Solve using DASWin for traps
    logger.info(f"---------------------- daswin_traps: {seed}----------------------")
    daswin_traps = DecoyAllocator(
        p1game=base_game_graph,
        true_final=final,
        n_traps=n_decoys,
        n_fakes=0,
        candidates=candidates,
        sol_concept=DecoyAllocator.ASWin
    )
    daswin_traps.solve()

    # Compare the VoD
    return {
        "dswin, traps": dswin_traps.best_decoys(),
        "dswin, fakes": dswin_fakes.best_decoys(),
        "daswin, traps": daswin_traps.best_decoys(),
        "daswin, fakes": daswin_fakes.best_decoys()
    }


# TODO. Move to vizutils.py
def generate_plot(data, fpath):
    """
    Generates and saves the plot as PNG.
    :param data: (dict) {"dswin, traps": (best_decoy, vod), "dswin, fakes": (best_decoy, vod), ...}
    """
    # Load data
    data_dswin_traps = data["dswin, traps"]
    data_daswin_traps = data["daswin, traps"]
    data_dswin_fakes = data["dswin, fakes"]
    data_daswin_fakes = data["daswin, fakes"]

    # Plot VoD vs. number of decoys. Each plot has 4 lines (one for each solver).
    # Number of decoys placed
    n = len(data_daswin_traps)
    x = range(len(data_daswin_traps) + 1)

    label_dswin_traps = [""] + [data_dswin_traps[i][0] for i in range(1, n + 1)]
    vod_dswin_traps = [0] + [data_dswin_traps[i][1] for i in range(1, n + 1)]

    # label_daswin_traps = [""] + [data_daswin_traps[i][0] for i in range(1, n)]
    vod_daswin_traps = [0] + [data_daswin_traps[i][1] for i in range(1, n + 1)]

    label_dswin_fakes = [""] + [data_dswin_fakes[i][0] for i in range(1, n + 1)]
    vod_dswin_fakes = [0] + [data_dswin_fakes[i][1] for i in range(1, n + 1)]

    label_daswin_fakes = [""] + [data_daswin_fakes[i][0] for i in range(1, n + 1)]
    vod_daswin_fakes = [0] + [data_daswin_fakes[i][1] for i in range(1, n + 1)]

    # y = np.vstack([vod_dswin_traps, vod_daswin_traps, vod_dswin_fakes, vod_daswin_fakes])
    # ax.stackplot(x, y, labels=["dswin, traps", "daswin, traps", "dswin, fakes", "daswin, fakes"])
    fig, ax = plt.subplots()
    ax.plot(x, vod_dswin_traps, label="dswin, traps", color="blue", linestyle="--")
    ax.scatter(x, vod_dswin_traps, color="blue", marker=".", linewidths=4)
    for i, txt in enumerate(label_dswin_traps):
        plt.annotate(txt, (x[i], vod_dswin_traps[i]), textcoords='offset points', xytext=(0, 10), ha='center')

    ax.plot(x, vod_dswin_fakes, label="dswin, fakes", color="blue")
    ax.scatter(x, vod_dswin_fakes, color="blue", marker=".", linewidths=4)
    for i, txt in enumerate(label_dswin_fakes):
        plt.annotate(txt, (x[i], vod_dswin_fakes[i]), textcoords='offset points', xytext=(0, 10), ha='center')

    ax.plot(x, vod_daswin_fakes, label="daswin, fakes", color="green", alpha=0.7)
    ax.plot(x, vod_daswin_traps, label="daswin, traps", color="red", linestyle=":", linewidth=3)
    ax.scatter(x, vod_daswin_traps, color="red", marker=".", linewidths=4)
    ax.scatter(x, vod_daswin_fakes, color="green", marker=".", linewidths=2)
    for i, txt in enumerate(label_daswin_fakes):
        plt.annotate(txt, (x[i], vod_daswin_fakes[i]), textcoords='offset points', xytext=(0, 10), ha='center')

    ax.legend(loc='upper left')
    ax.set(xlim=(0, n + 1), ylim=(0, 1.25), xticks=np.arange(min(x), max(x) + 1, 1.0), yticks=np.arange(0, 1.25, 0.1))
    ax.set(xlabel="Number of decoys", ylabel="VoD", title=f"Random Seed {seed}")
    plt.savefig(fpath, format='png', dpi=300)


if __name__ == '__main__':
    # Solve 100 games
    n_games = random.sample(range(1000, 2000), 1)
    best_decoys = dict()
    for seed in n_games:
        logger.info(f"---------------------- NEW GAME: {seed}----------------------")
        best_decoys[seed] = solve_one_game(seed)
        generate_plot(best_decoys[seed], os.path.join(OUTPUT_DIRECTORY, f"game{seed}_plot.png"))

    # Print interesting experiments
    logger.success(f"{best_decoys=}")
