"""
Allometry rules for dragons:
 - Mass from length: M = k_L * L³
 - Wing area from wingspan: A = k_b * b^β

Reads the dataset (lore_points.csv), fills in missing mass and wing area
using adult reference points, and saves the completed CSV.
"""

import os
import pandas as pd
import numpy as np


CSV_INPUT = os.path.join(os.path.dirname(__file__), "..", "data", "lore_points.csv")
CSV_OUTPUT = os.path.join(os.path.dirname(__file__), "..", "data", "lore_points_filled.csv")

def estimate_kappa_L(L_adult: float, M_adult: float) -> float:
    return M_adult / (L_adult ** 3)

def estimate_kappa_b(b_adult: float, a_adult: float, beta: float = 2.0) -> float:
    return a_adult / (b_adult ** beta)

def mass_from_length(L: np.ndarray, kappa_L: float) -> np.ndarray:
    return kappa_L * (L ** 3)

def wing_area_from_span(b: np.ndarray, kappa_b: float, beta: float = 2.0) -> np.ndarray:
    return kappa_b * (b ** beta)

def fill_missing_allometry(csv_path=CSV_INPUT, save_path=CSV_OUTPUT):
    df = pd.read_csv(csv_path)

    # 1. define adult reference point from lore (last known stage)
    lore_adult = df[df['age_yr'] == 8.0].iloc[0]  # 8 yr stage
    L_adult = lore_adult['length_m']
    M_adult = 35000.0      # kg, full-grown dragon
    b_adult = lore_adult['wingspan_m']
    A_adult = 700.0        # m²

    # 2. compute scaling constants
    kL = estimate_kappa_L(L_adult, M_adult)
    kb = estimate_kappa_b(b_adult, A_adult)

    # 3. fill missing columns
    if 'mass_kg' not in df.columns:
        df['mass_kg'] = pd.NA
    if 'wing_area_m2' not in df.columns:
        df['wing_area_m2'] = pd.NA

    # only fill missing values
    df.loc[df['mass_kg'].isna(), 'mass_kg'] = mass_from_length(
        df.loc[df['mass_kg'].isna(), 'length_m'], kL
    )
    df.loc[df['wing_area_m2'].isna(), 'wing_area_m2'] = wing_area_from_span(
        df.loc[df['wing_area_m2'].isna(), 'wingspan_m'], kb
    )

    df.to_csv(save_path, index=False)
    print(f"Saved filled CSV with mass and wing_area to {save_path}")

if __name__ == "__main__":
    fill_missing_allometry()
