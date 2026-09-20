"""Profile messy_samples.csv"""
from pathlib import Path
import pandas as pd

CSV = Path(__file__).resolve().parent.parent / "data/raw/lab3-messy-data/messy_samples.csv"

df = pd.read_csv(CSV, dtype=str, keep_default_na=False)
print("shape:", df.shape, "\n")

for col in ["sex", "enrollment_site", "glucose_unit", "notes"]:
    print(f"--- {col} ---")
    print(df[col].map(repr).value_counts().to_string(), "\n")

print("--- sample_id shapes ---")
print(df["sample_id"].str.replace(r"\d", "9", regex=True).value_counts().to_string(), "\n")

print("--- patient_name casing ---")
print(df["patient_name"].map(lambda s: "UPPER" if s.isupper() else "normal").value_counts().to_string(), "\n")

date_patterns = {
    "MM/DD/YYYY": r"^\d{2}/\d{2}/\d{4}$",
    "YYYY-MM-DD": r"^\d{4}-\d{2}-\d{2}$",
    "DD-Mon-YYYY": r"^\d{2}-[A-Za-z]{3}-\d{4}$",
    "MM.DD.YY": r"^\d{2}\.\d{2}\.\d{2}$",
}

print("--- dob formats ---")
matched = pd.Series(False, index=df.index)
for name, pat in date_patterns.items():
    hit = df["dob"].str.match(pat)
    print(f"{name:12s} {hit.sum():3d}")
    matched |= hit
print("unmatched:", (~matched).sum(), "\n")

print("--- glucose_vlaue shapes ---")
print(df["glucose_value"].str.replace(r"\d+\.\d", "9.9", regex=True).value_counts().to_string(), "\n")

print("--- numeric glucose by unit ---")
g = pd.to_numeric(df["glucose_value"], errors="coerce")
print(g.groupby(df["glucose_unit"].str.lower()).describe()[["count", "min", "mean", "max"]].round(1).to_string())
