"""
Fitting utilities:
 - polynomial fits (numpy.polyfit)
 - logistic fits (scipy curve_fit)
 - create dense interpolated arrays for plotting and downstream fitting
"""
import os
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

def poly_fit(x, y, deg=4):
    coeffs = np.polyfit(x, y, deg)
    p = np.poly1d(coeffs)
    # compute R^2
    yhat = p(x)
    ss_res = np.sum((y - yhat)**2)
    ss_tot = np.sum((y - np.mean(y))**2)
    r2 = 1 - ss_res / ss_tot
    return p, r2

def logistic(t, Smax, k, t0):
    return Smax / (1.0 + np.exp(-k*(t - t0)))

def fit_logistic_from_points(x, y, Smax_init=None):
    # Smax initial guess: max(y) or provided
    if Smax_init is None:
        Smax_init = max(y)*1.1
    p0 = [Smax_init, 1.0, np.median(x)]
    bounds = (0, [Smax_init*10, 10, max(x)*2])
    popt, pcov = curve_fit(logistic, x, y, p0=p0, bounds=bounds, maxfev=10000)
    return popt, pcov

def dense_from_poly(p, x_min=0, x_max=20, n=200):
    xs = np.linspace(x_min, x_max, n)
    ys = p(xs)
    return xs, ys

def load_lore(csv_path):
    df = pd.read_csv(csv_path)
    return df

if __name__ == "__main__":
    # quick test
    csv = os.path.join(os.path.dirname(__file__), "..", "data", "lore_points.csv")
    df = load_lore(csv)
    for col in ["length_m","height_m","wingspan_m","mass_kg","wing_area_m2"]:
        x = df["age_yr"].values
        y = df[col].values
        p, r2 = poly_fit(x, y, deg=4)
        print(f"{col}: poly4 r2={r2:.4f}")
        popt, _ = fit_logistic_from_points(x, y)
        print(f" logistic params (Smax,k,t0) = {popt}")
