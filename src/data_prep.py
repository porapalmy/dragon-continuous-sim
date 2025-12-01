"""
Robust data_prep: combine lore anchors (0-8yr) with any fan CSVs found in data/.
Saves: data/lore_points.csv
"""
import os
import glob
import pandas as pd

HERE = os.path.dirname(__file__)
DATA_DIR = os.path.join(HERE, "..", "data")
OUTPUT = os.path.join(DATA_DIR, "lore_points.csv")

def read_fan_csvs(data_dir):
    pattern = os.path.join(data_dir, "*.csv")
    files = [f for f in glob.glob(pattern) if os.path.abspath(f) != os.path.abspath(OUTPUT)]
    dfs = []
    for f in files:
        try:
            df = pd.read_csv(f)
            df['_source_file'] = os.path.basename(f)
            dfs.append(df)
        except Exception as e:
            print(f"Warning: failed to read {f}: {e}")
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    return pd.DataFrame()

def standardize_fan_df(df):
    # if empty, return empty standardized df
    if df.empty:
        return df
    # rename common columns to expected
    df = df.rename(columns={
        "age": "age_yr",
        "length": "length_m",
        "wingspan": "wingspan_m",
        "height": "height_m",
        "name": "name"
    })
    # keep only relevant columns if they exist, else add them
    for col in ["name","age_yr","length_m","wingspan_m","height_m"]:
        if col not in df.columns:
            df[col] = pd.NA
    # add mass & wing_area columns as NaN for now
    df["mass_kg"] = pd.NA
    df["wing_area_m2"] = pd.NA
    # reorder
    df = df[["name","age_yr","length_m","wingspan_m","height_m","mass_kg","wing_area_m2","_source_file"]]
    return df



def create_lore_df():
    lore_rows = [
        ("Lore", 0.0, 0.75, 1.88, 0.75, 29.0, 0.59),
        ("Lore", 1.0, 1.50, 3.75, 1.00, 117.0, 2.34),
        ("Lore", 2.5, 5.00, 12.50, 1.75, 1302.0, 26.04),
        ("Lore", 4.0, 13.50, 33.75, 2.00, 9492.0, 189.84),
        ("Lore", 8.0, 21.00, 52.50, 4.00, 22969.0, 459.38),
    ]
    cols = ["name", "age_yr", "length_m", "wingspan_m", "height_m", "mass_kg", "wing_area_m2"]
    df = pd.DataFrame(lore_rows, columns=cols)
    df["_source_file"] = "lore_anchors"
    return df

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    fan_raw = read_fan_csvs(DATA_DIR)
    fan_df = standardize_fan_df(fan_raw)
    lore_df = create_lore_df()

    if fan_df.empty:
        combined = lore_df.copy()
        print("No fan CSVs found — using only lore anchors.")
    else:
        combined = pd.concat([lore_df, fan_df], ignore_index=True)
        # drop duplicates that match on name, age, length, wingspan (keep first)
        combined = combined.drop_duplicates(subset=["name","age_yr","length_m","wingspan_m"], keep="first")

    combined = combined.sort_values(by=["age_yr","name"], na_position="last").reset_index(drop=True)
    # drop helper column before saving
    if "_source_file" in combined.columns:
        combined = combined.drop(columns=["_source_file"])
    combined.to_csv(OUTPUT, index=False)
    print(f"Saved combined lore CSV to {OUTPUT}")

if __name__ == "__main__":
    main()