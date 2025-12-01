import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fits import load_lore, poly_fit, logistic, fit_logistic_from_points

CSV_INPUT = os.path.join(os.path.dirname(__file__), "..", "data", "lore_points_filled.csv")

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs")
FIG_DIR = os.path.join(OUT_DIR, "figures")
TAB_DIR = os.path.join(OUT_DIR, "tables")
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(TAB_DIR, exist_ok=True)


def best_fit(x, y):
    """Try linear, poly2-4, and logistic; return best fit function, type, R², and equation string."""
    best_r2 = -np.inf
    best_type = None
    best_func = None
    eqn_str = ""
    y = np.array(y)
    x = np.array(x)

    # Linear
    p_lin, r2_lin = poly_fit(x, y, deg=1)
    if r2_lin > best_r2:
        best_r2 = r2_lin
        best_type = "linear"
        best_func = p_lin
        eqn_str = f"y = {p_lin[1]:.4f} + {p_lin[0]:.4f} x"

    # Polynomial 2-4
    for deg in [2, 3, 4]:
        p, r2 = poly_fit(x, y, deg=deg)
        if r2 > best_r2:
            best_r2 = r2
            best_type = f"poly{deg}"
            best_func = p
            terms = [f"{coef:.4e}*x**{i}" for i, coef in enumerate(reversed(p.coefficients))]
            eqn_str = "y = " + " + ".join(terms)

    # Logistic
    try:
        popt, _ = fit_logistic_from_points(x, y)
        yhat = logistic(x, *popt)
        ss_res = np.sum((y - yhat)**2)
        ss_tot = np.sum((y - np.mean(y))**2)
        r2_log = 1 - ss_res / ss_tot
        if r2_log > best_r2:
            best_r2 = r2_log
            best_type = "logistic"
            best_func = lambda xx: logistic(xx, *popt)
            eqn_str = f"y = {popt[0]:.4f} / (1 + exp(-{popt[1]:.4f}*(x - {popt[2]:.4f})))"
    except Exception:
        pass

    return best_func, best_type, best_r2, eqn_str


def plot_raw_correlations(csv_input=CSV_INPUT, out_fig_dir=FIG_DIR, out_tab_dir=TAB_DIR):
    """Plot correlation matrix and pairwise scatterplots with best fit lines."""
    try:
        df = load_lore(csv_input)
    except Exception:
        df = pd.read_csv(csv_input)

    cols = ["length_m", "wingspan_m", "height_m", "mass_kg", "wing_area_m2"]
    cols = [c for c in cols if c in df.columns]
    df = df[cols].dropna()

    # === 1. Correlation Matrix ===
    corr_matrix = df.corr(method="pearson")
    plt.figure(figsize=(7, 6))
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", square=True)
    plt.title("Correlation Matrix (Pearson)")
    corr_path = os.path.join(out_fig_dir, "correlation_matrix_raw.png")
    plt.tight_layout()
    plt.savefig(corr_path, dpi=200)
    plt.close()

    # Pairwise Scatterplots with fits
    results = []
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            xcol, ycol = cols[i], cols[j]
            sub = df[[xcol, ycol]].dropna()
            x, y = sub[xcol].values, sub[ycol].values

            pearson_corr = float(sub.corr(method='pearson').iloc[0, 1])
            spearman_corr = float(sub.corr(method='spearman').iloc[0, 1])

            fig, ax = plt.subplots(figsize=(6, 4))
            ax.scatter(x, y, color="royalblue", alpha=0.7, edgecolor="white", s=40)
            ax.set_xlabel(xcol)
            ax.set_ylabel(ycol)

            # Best fit
            fit_func, fit_type, fit_r2, eqn_str = best_fit(x, y)
            xx = np.linspace(min(x), max(x), 200)
            ax.plot(xx, fit_func(xx), color="orange", lw=2, label=f"{fit_type} (R²={fit_r2:.3f})")
            ax.legend()
            ax.set_title(f"{ycol} vs {xcol}\n(Pearson={pearson_corr:.2f}, Spearman={spearman_corr:.2f})")
            fig.tight_layout()

            fig_path = os.path.join(out_fig_dir, f"{ycol}_vs_{xcol}_fit.png")
            fig.savefig(fig_path, dpi=200)
            plt.close(fig)

            print(f"Best fit for {ycol} vs {xcol}: {fit_type}, R²={fit_r2:.4f}")
            print(f"Equation: {eqn_str}")

            results.append({
                "x": xcol,
                "y": ycol,
                "n_points": int(len(x)),
                "pearson": pearson_corr,
                "spearman": spearman_corr,
                "best_fit_type": fit_type,
                "best_fit_r2": fit_r2,
                "best_fit_eqn": eqn_str,
                "figure": fig_path
            })

    tab_df = pd.DataFrame(results)
    tab_path = os.path.join(out_tab_dir, "correlations_fitted.csv")
    tab_df.to_csv(tab_path, index=False)

    print(f"Saved correlation matrix: {corr_path}")
    print(f"Saved scatterplots with fits: {out_fig_dir}")
    print(f"Saved results table: {tab_path}")
    return results


if __name__ == "__main__":
    plot_raw_correlations()
