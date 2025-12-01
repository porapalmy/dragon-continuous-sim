"""
Run polynomial + logistic growth fits for core dragon traits:
  - length_m
  - wingspan_m
  - height_m
Saves figures and a summary table under outputs/.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from fits import poly_fit, fit_logistic_from_points, dense_from_poly, logistic, load_lore

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs")
FIG_DIR = os.path.join(OUT_DIR, "figures")
TAB_DIR = os.path.join(OUT_DIR, "tables")
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(TAB_DIR, exist_ok=True)

def run_all_fits(csv_path):
    df = load_lore(csv_path)
    results = []

    for col in ["length_m", "wingspan_m", "height_m"]:
        sub = df[["age_yr", col]].dropna()
        if len(sub) < 3:
            print(f"⚠️ Skipping {col} (too few valid points)")
            continue

        x = sub["age_yr"].values
        y = sub[col].values

        # Polynomial fit
        p, r2 = poly_fit(x, y, deg=4)

        # Logistic fit
        try:
            popt, _ = fit_logistic_from_points(x, y)
            Smax, k, t0 = popt
        except Exception as e:
            print(f"⚠️ Logistic fit failed for {col}: {e}")
            Smax = k = t0 = np.nan

        results.append({
            "variable": col,
            "poly_r2": r2,
            "logi_Smax": Smax,
            "logi_k": k,
            "logi_t0": t0
        })

        # Generate polynomial curve
        xs, ys_poly = dense_from_poly(p, x_min=min(x), x_max=max(x))
        plt.figure(figsize=(7, 5))
        plt.scatter(x, y, color="black", label="Data", zorder=3)
        plt.plot(xs, ys_poly, label=f"Poly4 (R²={r2:.3f})", color="tab:blue")

        # Add logistic curve if available
        if not np.isnan(Smax):
            ys_logi = logistic(xs, *popt)
            plt.plot(xs, ys_logi, "--", label="Logistic", color="tab:orange")

        plt.title(f"{col.replace('_',' ').title()} vs Age")
        plt.xlabel("Age (years)")
        plt.ylabel(col.replace("_", " ").title())
        plt.legend()
        plt.grid(alpha=0.3)

        fig_path = os.path.join(FIG_DIR, f"{col}_fit.png")
        plt.savefig(fig_path, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"Saved {fig_path}")

    res_df = pd.DataFrame(results)
    table_path = os.path.join(TAB_DIR, "growth_fits.csv")
    res_df.to_csv(table_path, index=False)
    print(f"\n Saved summary table: {table_path}")

if __name__ == "__main__":
    csv = os.path.join(os.path.dirname(__file__), "..", "data", "lore_points.csv")
    run_all_fits(csv)
