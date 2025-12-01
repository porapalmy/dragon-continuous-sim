"""
Plotting utilities for growth and energetics.
Saves plots to outputs/figures
"""
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
sns.set(style="whitegrid", context="talk")

OUTDIR = os.path.join(os.path.dirname(__file__), "..", "outputs", "figures")
os.makedirs(OUTDIR, exist_ok=True)

def plot_growth(xs, ys_dict, filename="growth.png", xlabel="Age (yr)"):
    """
    ys_dict: dict name -> array of same length as xs
    """
    plt.figure(figsize=(10,6))
    for name, ys in ys_dict.items():
        plt.plot(xs, ys, label=name, linewidth=2)
    plt.xlabel(xlabel)
    plt.ylabel("Size / measurement")
    plt.legend()
    plt.tight_layout()
    fp = os.path.join(OUTDIR, filename)
    plt.savefig(fp, dpi=200)
    plt.close()
    print("Saved", fp)

def plot_population(sol, filename="population.png"):
    plt.figure(figsize=(9,6))
    for i, name in enumerate(['H','Y','R','A']):
        plt.plot(sol.t, sol.y[i], label=name)
    plt.xlabel("Time (yr)")
    plt.ylabel("Individuals")
    plt.legend()
    plt.tight_layout()
    fp = os.path.join(OUTDIR, filename)
    plt.savefig(fp, dpi=200)
    plt.close()
    print("Saved", fp)

if __name__ == "__main__":
    # quick example
    xs = np.linspace(0,10,200)
    ys = {'length': 0.5 + xs**1.2, 'wingspan': 1.0 + xs**1.6}
    plot_growth(xs, ys, filename="demo_growth.png")
