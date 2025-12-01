"""
Energetics module for dragons:
 - Kleiber RER: RER = 70 * M^0.75 (kcal/day)
 - MER = alpha * RER
 - Flight power scaling P_flight = phi * M^1.1 (kcal/day for 24h)
 - Fire energy: E_fire_burst = delta * V_gas * C_comb (kcal)
 - Thermoregulation (Scholander)
"""

import os
import pandas as pd
import numpy as np

CSV_INPUT = os.path.join(os.path.dirname(__file__), "..", "data", "lore_points_filled.csv")
CSV_OUTPUT = os.path.join(os.path.dirname(__file__), "..", "data", "lore_points_energy.csv")

def RER(M_kg):
    return 70.0 * (M_kg**0.75)

def MER(M_kg, alpha=2.0):
    return alpha * RER(M_kg)

def flight_power(M_kg, phi=0.01, exponent=1.1):
    return phi * (M_kg**exponent)

def flight_energy(M_kg, hours_per_day=3.0, phi=0.01, exponent=1.1):
    Pf24 = flight_power(M_kg, phi=phi, exponent=exponent)
    return Pf24 * (hours_per_day / 24.0)

def fire_burst_energy(V_liters, delta=0.8, C_comb_kcal_per_L=9.3):
    return delta * V_liters * C_comb_kcal_per_L

def fire_daily_energy(n_bursts, V_liters_per_burst, delta=0.8, C_comb_kcal_per_L=9.3):
    return n_bursts * fire_burst_energy(V_liters_per_burst, delta=delta, C_comb_kcal_per_L=C_comb_kcal_per_L)

def scholander_delta_per_deg(RER_kcal_day, Tb_minus_Ta):
    W_per_kcalday = 4184.0 / 86400.0
    power_W = RER_kcal_day * W_per_kcalday
    C = power_W / Tb_minus_Ta
    kcal_per_day_per_deg = (C * 86400.0) / 4184.0
    return C, kcal_per_day_per_deg

def compute_energy(csv_path=CSV_INPUT, save_path=CSV_OUTPUT):
    df = pd.read_csv(csv_path)

    # only compute energetics for rows that have mass
    df['RER_kcal_day'] = df['mass_kg'].apply(lambda m: RER(m))
    df['MER_kcal_day'] = df['mass_kg'].apply(lambda m: MER(m))
    df['flight_energy_3h_kcal'] = df['mass_kg'].apply(lambda m: flight_energy(m, hours_per_day=3.0, phi=0.02))
    
    df['fire_daily_kcal'] = df['mass_kg'].apply(lambda m: fire_daily_energy(2, 100.0))
    
    C_kcal_per_deg_list = []
    for rer in df['RER_kcal_day']:
        _, kcal_per_deg = scholander_delta_per_deg(rer, Tb_minus_Ta=28.0)
        C_kcal_per_deg_list.append(kcal_per_deg)
    df['thermo_kcal_per_degC'] = C_kcal_per_deg_list

    df.to_csv(save_path, index=False)
    print(f"Saved energetics table to {save_path}")

if __name__ == "__main__":
    compute_energy()
