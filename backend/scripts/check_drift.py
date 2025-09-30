import pandas as pd
import numpy as np
import sqlite3
import os
from scipy.stats import entropy

DB_PATH = os.getenv("DB_PATH", "app.db")
BASELINE_PATH = "backend/model/training_baseline.csv"  # generated during training


def population_stability_index(expected, actual, bins=10):
    expected_perc, _ = np.histogram(expected, bins=bins)
    actual_perc, _ = np.histogram(actual, bins=bins)
    expected_perc = expected_perc / expected_perc.sum()
    actual_perc = actual_perc / actual_perc.sum()
    return np.sum((expected_perc - actual_perc) * np.log((expected_perc + 1e-6) / (actual_perc + 1e-6)))


def main():
    if not os.path.exists(DB_PATH) or not os.path.exists(BASELINE_PATH):
        print("No DB or baseline found, skipping drift check.")
        return

    baseline = pd.read_csv(BASELINE_PATH)
    conn = sqlite3.connect(DB_PATH)
    prod = pd.read_sql("SELECT * FROM predictions", conn)
    conn.close()

    for col in baseline.columns:
        if col in prod.columns:
            psi = population_stability_index(baseline[col], prod[col])
            print(f"PSI for {col}: {psi:.3f}")
            if psi > 0.2:
                print(f"⚠️ Drift detected in {col}")


if __name__ == "__main__":
    main()
