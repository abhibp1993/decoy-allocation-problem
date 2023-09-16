import json
import matplotlib.pyplot as plt
import os
import numpy as np

OUTPUT_DIR = os.path.join('out')


def generate_plot(data, seed, fpath):
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

    label_dswin_traps = [""] + [data_dswin_traps[str(i)][0] for i in range(1, n + 1)]
    vod_dswin_traps = [0] + [data_dswin_traps[str(i)][1] for i in range(1, n + 1)]

    # label_daswin_traps = [""] + [data_daswin_traps[i][0] for i in range(1, n)]
    vod_daswin_traps = [0] + [data_daswin_traps[str(i)][1] for i in range(1, n + 1)]

    label_dswin_fakes = [""] + [data_dswin_fakes[str(i)][0] for i in range(1, n + 1)]
    vod_dswin_fakes = [0] + [data_dswin_fakes[str(i)][1] for i in range(1, n + 1)]

    label_daswin_fakes = [""] + [data_daswin_fakes[str(i)][0] for i in range(1, n + 1)]
    vod_daswin_fakes = [0] + [data_daswin_fakes[str(i)][1] for i in range(1, n + 1)]

    # y = np.vstack([vod_dswin_traps, vod_daswin_traps, vod_dswin_fakes, vod_daswin_fakes])
    # ax.stackplot(x, y, labels=["dswin, traps", "daswin, traps", "dswin, fakes", "daswin, fakes"])
    fig, ax = plt.subplots()

    ax.plot(x, vod_dswin_fakes, label="dswin, fakes", color="blue")
    ax.plot(x, vod_dswin_traps, label="dswin, traps", color="blue", linestyle="--", linewidth=2)
    ax.plot(x, vod_daswin_fakes, label="daswin, fakes", color="green", alpha=0.7)
    ax.plot(x, vod_daswin_traps, label="daswin, traps", color="red", linestyle=":", linewidth=3)
    ax.scatter(x, vod_daswin_fakes, color="green", marker=".", linewidths=2)
    ax.scatter(x, vod_daswin_traps, color="red", marker=".", linewidths=4)
    ax.scatter(x, vod_dswin_fakes, color="blue", marker=".", linewidths=4)
    ax.scatter(x, vod_dswin_traps, color="blue", marker=".", linewidths=4)

    ax.legend(loc='upper left')
    ax.set(xlim=(0, n + 1), ylim=(0, 1.25), xticks=np.arange(min(x), max(x) + 1, 1.0), yticks=np.arange(0, 1.25, 0.1))
    ax.set(xlabel="Number of decoys", ylabel="VoD", title=f"Random Seed {seed}")
    plt.savefig(fpath, format='png', dpi=300)


if __name__ == '__main__':
    with open(os.path.join(OUTPUT_DIR, 'results.json'), 'r') as f:
        data = json.load(f)

    results = data['best_decoys']

    r1476 = results['1476']
    r1044 = results['1044']
    r1357 = results['1357']
    r1745 = results['1745']

    generate_plot(r1476, '1476', os.path.join(OUTPUT_DIR, 'r1476.png'))
    generate_plot(r1044, '1044', os.path.join(OUTPUT_DIR, 'r1044.png'))
    generate_plot(r1357, '1357', os.path.join(OUTPUT_DIR, 'r1357.png'))
    generate_plot(r1745, '1745', os.path.join(OUTPUT_DIR, 'r1745.png'))

    print(r1476)
    print(r1044)
    print(r1357)
    print(r1745)
