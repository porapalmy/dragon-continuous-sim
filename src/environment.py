"""
Dragon Farm Environment Module:
- Estimate personal space, total land area, and farm layout
- Use growth models to calculate length at each age
- Compute density and carrying capacity
"""

import numpy as np
import pandas as pd
import os

CSV_INPUT = os.path.join(os.path.dirname(__file__), "..", "data", "lore_points_energy.csv")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "..", "outputs", "tables", "farm_area_estimates.csv")

def length_poly(age_yr):
    return 4.973e-9*age_yr**4 + 7.748e-6*age_yr**3 - 5.467e-3*age_yr**2 + 1.351*age_yr + 8.335

results = length_poly(np.array([0,1,2,3,4,5,6,7,8,9,10, 20, 30, 50, 80, 100, 150, 200]))

print("Length estimates (m) for ages 0-10 years:", results)
def area_per_dragon(length_m):
    """
    Calculate square area required per dragon.
    Treat length as radius of personal circle, convert to square with factor.
    safety_factor allows extra room for comfort and movement
    """
    radius = length_m
    # circle_area = np.pi * radius**2
    square_area = (radius*2) * (radius*2)
    return square_area

def total_farm_area(df, safety_factor=1.2, prey_area=5000.0, hatching_area=1000.0):
    """
    Estimate total farm area:
    - df: dragon dataset with age_yr column
    - safety_factor: extra space multiplier
    - prey_area: area for sheep or other prey
    - hatching_area: space reserved for eggs/incubation
    """
    
    age_yrs = [0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 2,2,2,2,2,2,2,2,2,2,
                3,3,3,3,3,3,3,3,3,3, 4,4,4,4,4,4,4,4,4,4, 5,5,5,5,5,5,5,5,5,5,
                6,6,6,6,6,6,6,6,6,6, 7,7,7,7,7,7,7,7,7,7, 8,8,8,8,8,8,8,8,8,8, 
                9,9,9,9,9,9,9,9,9,9, 10,10,10,10,10,10,10,10,10,10, 11,11,11,11,11,11,11,11,11,11,
                12,12,12,12,12,12,12,12,12,12]
    # Expand df to represent individual dragons
    areas = []
    for age in age_yrs:
        L = length_poly(age)
        area = area_per_dragon(L)
        areas.append(area)
    
    df['personal_area_m2'] = areas
    total_dragons_area = df['personal_area_m2'].sum()
    total_area = total_dragons_area + prey_area + hatching_area
    return total_area, df

# def estimate_density(df, total_area):
#     """
#     Estimate dragon density (dragons per hectare)
#     """
#     n_dragons = df.shape[0]
#     hectares = total_area / 10000.0
#     density = n_dragons / hectares
#     return density

# if __name__ == "__main__":
#     os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
#     df = pd.read_csv(CSV_INPUT)
#     total_area, df_with_area = total_farm_area(df)
#     density = estimate_density(df_with_area, total_area)

#     df_with_area.to_csv(OUTPUT_FILE, index=False)
#     print(f"Saved farm area estimates to {OUTPUT_FILE}")
#     print(f"Total farm area required: {total_area:.0f} m^2")
#     print(f"Estimated dragon density: {density:.2f} dragons/hectare")
