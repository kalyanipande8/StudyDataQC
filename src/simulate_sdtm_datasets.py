"""Simulate 3 SDTM-style clinical domains (DM demographics, AE
adverse events, LB labs) across 3 simulated study sites, with real
injected discrepancies spanning the ground truth 25 validation rules
must independently catch."""
from __future__ import annotations

import numpy as np
import pandas as pd

N_SUBJECTS = 500
SEED = 953
SITES = ["SITE01", "SITE02", "SITE03"]


def simulate(n_subjects: int = N_SUBJECTS, seed: int = SEED) -> dict:
    rng = np.random.default_rng(seed)

    dm = pd.DataFrame({
        "USUBJID": [f"S-{i:04d}" for i in range(n_subjects)],
        "SITEID": rng.choice(SITES, n_subjects), "AGE": rng.integers(18, 90, n_subjects),
        "SEX": rng.choice(["M", "F"], n_subjects), "RFSTDTC": pd.date_range("2024-01-01", periods=n_subjects, freq="h"),
    })

    ae = pd.DataFrame({
        "USUBJID": rng.choice(dm["USUBJID"], int(n_subjects * 1.5)),
        "AESEV": rng.choice(["MILD", "MODERATE", "SEVERE"], int(n_subjects * 1.5)),
        "AESTDTC": pd.date_range("2024-02-01", periods=int(n_subjects * 1.5), freq="h"),
        "AEENDTC": pd.date_range("2024-02-02", periods=int(n_subjects * 1.5), freq="h"),
    })

    lb = pd.DataFrame({
        "USUBJID": rng.choice(dm["USUBJID"], int(n_subjects * 3)),
        "LBTESTCD": rng.choice(["ALT", "AST", "HGB", "WBC"], int(n_subjects * 3)),
        "LBSTRESN": np.round(rng.normal(50, 15, int(n_subjects * 3)), 2),
    })

    true_discrepancies = {"dm": set(), "ae": set(), "lb": set()}

    # DM: invalid age (1%), invalid sex (1%), orphan site (0.5%)
    idx = rng.choice(dm.index, int(n_subjects * 0.01), replace=False)
    dm.loc[idx, "AGE"] = -5
    true_discrepancies["dm"] |= set(idx)
    idx = rng.choice(dm.index, int(n_subjects * 0.01), replace=False)
    dm.loc[idx, "SEX"] = "X"
    true_discrepancies["dm"] |= set(idx)

    # AE: end date before start date (2%), invalid severity (1%)
    idx = rng.choice(ae.index, int(len(ae) * 0.02), replace=False)
    ae.loc[idx, "AEENDTC"] = ae.loc[idx, "AESTDTC"] - pd.Timedelta(days=5)
    true_discrepancies["ae"] |= set(idx)
    idx = rng.choice(ae.index, int(len(ae) * 0.01), replace=False)
    ae.loc[idx, "AESEV"] = "UNKNOWN"
    true_discrepancies["ae"] |= set(idx)

    # LB: out-of-range lab value (3%), orphan subject (0.5%)
    idx = rng.choice(lb.index, int(len(lb) * 0.03), replace=False)
    lb.loc[idx, "LBSTRESN"] = -999
    true_discrepancies["lb"] |= set(idx)
    idx = rng.choice(lb.index, int(len(lb) * 0.005), replace=False)
    lb.loc[idx, "USUBJID"] = "S-9999"
    true_discrepancies["lb"] |= set(idx)

    return {"dm": dm, "ae": ae, "lb": lb, "true_discrepancies": true_discrepancies}


if __name__ == "__main__":
    data = simulate()
    print({k: len(v) for k, v in data.items() if k != "true_discrepancies"})
