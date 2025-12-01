"""
Stage-structured ODE model for H, Y, R, A compartments.
Uses dragon energetics and growth stages to inform survival and reproduction.
Also computes R0 (net reproductive ratio).
"""

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
import os
import matplotlib.pyplot as plt

CSV_INPUT = os.path.join(os.path.dirname(__file__), "..", "data", "lore_points_energy.csv")
FIGURE_OUTPUT = os.path.join(os.path.dirname(__file__), "..", "outputs", "figures", "population_sim.png")

# ode
def population_odes(t, y, params):
    H, Y, R, A = y
    b, g = params['b'], params['g']
    sigma_H, sigma_Y, sigma_R = params['sigma_H'], params['sigma_Y'], params['sigma_R']
    d_h, d_y, d_r, d_a = params['d_h'], params['d_y'], params['d_r'], params['d_a']
    dHdt = b * g * A - (d_h + sigma_H) * H
    dYdt = sigma_H * H - (d_y + sigma_Y) * Y
    dRdt = sigma_Y * Y - (d_r + sigma_R) * R
    dAdt = sigma_R * R - d_a * A
    return [dHdt, dYdt, dRdt, dAdt]

# sim
def simulate_population(params, y0=None, t_span=(0,100), t_eval=None):
    # if y0 is None:
    #     y0 = [3, 0, 0, 0]  # initial counts for H, Y, R, A
    # if t_eval is None:
    #     t_eval = np.linspace(t_span[0], t_span[1], 500)
    sol = solve_ivp(population_odes, t_span, y0, t_eval=t_eval, args=(params,), dense_output=True)
    return sol

# r0
def compute_R0(params):
    b, g = params['b'], params['g']
    sigma_H, sigma_Y, sigma_R = params['sigma_H'], params['sigma_Y'], params['sigma_R']
    d_h, d_y, d_r, d_a = params['d_h'], params['d_y'], params['d_r'], params['d_a']
    num = b * g * sigma_H * sigma_Y * sigma_R
    den = (d_h + sigma_H)*(d_y + sigma_Y)*(d_r + sigma_R)*d_a
    return num / den


def run_population_from_data(csv_path=CSV_INPUT):
    df = pd.read_csv(csv_path)

    # Estimate adult count: number of dragons 8+ years
    adults = df[df['age_yr'] >= 8].shape[0]
    print(f"Estimated adult dragons (8+ yrs): {adults}")

    # Set stage-specific mortality/survival rates using energetics
    # Here we can scale death rates based on MER or flight energy if desired
    params = {
        'b': 4.0, 'g': 0.2,                  # fecundity * survival of eggs
        'sigma_H': 1.0, 'sigma_Y': 1.0/3.0, 'sigma_R': 1.0/4.0,
        'd_h': 0.25, 'd_y': 0.10, 'd_r': 0.10, 'd_a': 0.50
    }

    # Initial counts: H,Y,R,A
    # y0 = [adults*2, adults, adults//2, adults]  # rough scaling
    y0 = [10, 3, 1, 0]
    
    sol = simulate_population(params, y0=y0, t_span=(0,50))

    plt.figure(figsize=(8,5))
    plt.plot(sol.t, sol.y.T)
    plt.legend(['H','Y','R','A'])
    plt.xlabel('Years')
    plt.ylabel('Individuals')
    plt.title('Dragon stage-structured population dynamics')
    os.makedirs(os.path.dirname(FIGURE_OUTPUT), exist_ok=True)
    plt.savefig(FIGURE_OUTPUT, dpi=200)
    plt.close()
    print(f"Saved population figure to {FIGURE_OUTPUT}")
    print("R0:", compute_R0(params))

if __name__ == "__main__":
    run_population_from_data()
