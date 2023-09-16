import itertools
import os.path
import pickle
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

import ioutils

# OUTPUT DIRECTORY
OUTPUT_DIRECTORY = os.path.join("out")


def plot_heatmap(mat, fpath):
    sns.set(font_scale=1.4)
    sns.heatmap(mat, annot=True, annot_kws={"size": 11})
    plt.savefig(fpath)


def plot_f2t0(data, decoys):
    # First iteration
    plt.figure()
    mat = np.zeros((7, 7))
    for d in data["1"]:
        r, c = d["fakes"].pop()
        mat[r, c] = d["vod"]

    plot_heatmap(mat, os.path.join(OUTPUT_DIRECTORY, "f2t0_1.svg"))
    plt.show(block=False)

    # Second iteration
    plt.figure()
    mat = np.zeros((7, 7))
    for d in data["2"]:
        r, c = (d["fakes"] - {decoys["1"][0]}).pop()
        mat[r, c] = d["vod"]

    plot_heatmap(mat, os.path.join(OUTPUT_DIRECTORY, "f2t0_2.svg"))
    plt.show(block=False)


def plot_f1t1(data, decoys):
    # First iteration
    plt.figure()
    mat = np.zeros((7, 7))
    for d in data["1"]:
        r, c = d["fakes"].pop()
        mat[r, c] = d["vod"]

    plot_heatmap(mat, os.path.join(OUTPUT_DIRECTORY, "f1t1_1.svg"))
    plt.show(block=False)

    # Second iteration
    plt.figure()
    mat = np.zeros((7, 7))
    for d in data["2"]:
        r, c = d["traps"].pop()
        mat[r, c] = d["vod"]

    plot_heatmap(mat, os.path.join(OUTPUT_DIRECTORY, "f1t1_2.svg"))
    plt.show(block=False)


def plot_f0t2(data, decoys):
    # First iteration
    plt.figure()
    mat = np.zeros((7, 7))
    for d in data["1"]:
        r, c = d["traps"].pop()
        mat[r, c] = d["vod"]

    plot_heatmap(mat, os.path.join(OUTPUT_DIRECTORY, "f0t2_1.svg"))
    plt.show(block=False)

    # Second iteration
    plt.figure()
    mat = np.zeros((7, 7))
    for d in data["2"]:
        r, c = (d["traps"] - {decoys["1"][0]}).pop()
        mat[r, c] = d["vod"]

    plot_heatmap(mat, os.path.join(OUTPUT_DIRECTORY, "f0t2_2.svg"))
    plt.show(block=False)


def main():
    data = ioutils.from_json(os.path.join("out", "dswin_f2t0_data.json"))
    plot_f2t0(data, {"1": ((3, 3), 0.48681366191093817), "2": ((4, 5), 0.6575875486381323)})

    data = ioutils.from_json(os.path.join("out", "dswin_f1t1_data.json"))
    plot_f1t1(data, {"1": ((3, 3), 0.48681366191093817), "2": ((5, 6), 0.5659316904453091)})

    data = ioutils.from_json(os.path.join("out", "dswin_f0t2_data.json"))
    plot_f0t2(data, {"1": ((1, 5), 0.2797233030696066), "2": ((5, 5), 0.49978383052313013)})


if __name__ == '__main__':
    main()
