"""Diff the regex and AI-assisted outputs, row by row, for both files."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "data/processed"


def diff_table(regex_path, ai_path, key, compare_cols, label):
    regex = pd.read_csv(regex_path, dtype=str, keep_default_na=False).set_index(key)
    ai = pd.read_csv(ai_path, dtype=str, keep_default_na=False).set_index(key)

    print(f"=== {label} ===")
    print(f"regex rows: {len(regex)}   ai rows: {len(ai)}")
    only_regex = regex.index.difference(ai.index)
    only_ai = ai.index.difference(regex.index)
    if len(only_regex):
        print("in regex only:", list(only_regex))
    if len(only_ai):
        print("in AI only:", list(only_ai))

    shared = regex.index.intersection(ai.index)
    n_diff_rows = 0
    for idx in shared:
        row_diffs = []
        for col in compare_cols:
            r_val = regex.loc[idx, col] if col in regex.columns else "<no column>"
            a_val = ai.loc[idx, col] if col in ai.columns else "<no column>"
            if r_val != a_val:
                row_diffs.append(f"{col}: regex={r_val!r} ai={a_val!r}")
        if row_diffs:
            n_diff_rows += 1
            print(f"{idx}: " + " | ".join(row_diffs))

    print(f"{n_diff_rows} of {len(shared)} shared rows differ on at least one column\n")

def diff_numeric(regex_path, ai_path, key, col, label, tol=0.05):
    regex = pd.read_csv(regex_path, dtype=str, keep_default_na=False).set_index(key)
    ai = pd.read_csv(ai_path, dtype=str, keep_default_na=False).set_index(key)
    shared = regex.index.intersection(ai.index)

    print(f"--- {label}: numeric comparison on '{col}' (tolerance ±{tol}) ---")
    n_diff = 0
    for idx in shared:
        r_raw = regex.loc[idx, col] if col in regex.columns else ""
        a_raw = ai.loc[idx, col] if col in ai.columns else ""
        r_val = float(r_raw) if r_raw not in ("", None) else None
        a_val = float(a_raw) if a_raw not in ("", None) else None
        if r_val is None and a_val is None:
            continue
        if r_val is None or a_val is None or abs(r_val - a_val) > tol:
            ratio = f"  (ai/regex = {a_val / r_val:.3f})" if r_val not in (None, 0) and a_val is not None else ""
            print(f"{idx}: regex={r_val} ai={a_val}{ratio}")
            n_diff += 1
    print(f"{n_diff} of {len(shared)} shared rows differ on '{col}'\n")

def main():
    diff_table(
        PROC / "samples_clean_regex.csv",
        PROC / "samples_clean_ai.csv",
        key="sample_id",
        compare_cols=["patient_name", "dob", "sex", "enrollment_site", "notes"],
        label="messy_samples.csv",
    )
    diff_numeric(
        PROC / "samples_clean_regex.csv",
        PROC / "samples_clean_ai.csv",
        key="sample_id",
        col="glucose_mg_dl",
        label="messy_samples.csv",
    )

    diff_table(
        PROC / "sequences_clean_regex.csv",
        PROC / "sequences_clean_ai.csv",
        key="sample_id",
        compare_cols=["organism", "gene", "note"],
        label="messy_sequences.fasta",
    )
    diff_numeric(
        PROC / "sequences_clean_regex.csv",
        PROC / "sequences_clean_ai.csv",
        key="sample_id",
        col="declared_length_bp",
        label="messy_sequences.fasta",
        tol=0.5,
    )


if __name__ == "__main__":
    main()