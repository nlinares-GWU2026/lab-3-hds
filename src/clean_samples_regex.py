"""Regex-based cleaning of messy_samples.csv (Lab 3, approach 1)"""
import re
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data/raw/lab3-messy-data/messy_samples.csv"

# Standardizes sample ID strings into uppercase 'S' followed by a 4-digit number
# Regex: (r"[Ss]-?(\d{4})") -> 
# [Ss]: Matches either uppercase 'S' or lowercase 
# -?: Matches optional hyphen, meaning 0 or 1 hyphen
# (/d{4}): Capture group 1. Matches exactly 4 numeric digits (\d) and accessing m.group(1) retrieves 4 digits so can be reformatted as S+digits 
def clean_sample_id(raw):
    """'s-0003' or 'S0003' -> S0003"""
    m = re.match(r"^[sS]-?(\d+)$", raw.strip())
    if m is None:
        return None
    return f"S{m.group(1)}"

# Normalizes patient names formatted
# Regex:(r"([A-Za-z])\.\s+([A-Za-z]+)")
# ([A-Za-z]): Capture group 1. Matches single letter (uppercase or lowercase) representing the first initial
# \. Matches literal period
#\s+ Matches one or more whitespace spaces/tabs separating intial and last name
# ([A-Za-z])+: Capture group 2. Matches one or more consecutive letters representing last name.
def clean_name(raw):
    """'A. NGUYEN' or 'A. Nguyen' -> 'A. Nguyen'"""
    m = re.fullmatch(r"([A-Za-z])\.\s+([A-Za-z]+)", raw.strip())
    if m is None:
        return None
    return f"{m.group(1).upper()}. {m.group(2).capitalize()}"

# Standardizes sex entries into single char codes 
# Regex: 
# r"m(ale)?": Matches m alone or male (the ? makes 'ale' optional)
# r"f(emale)?": Matches f alone or female (the ? makes 'emale' optional)
# r"(u|unknown)?": Matches u, unknown or an empty string "" with unrecognized values return None
def clean_sex(raw):
    """'M/m/Male -> M'; F/f/Female -> 'F'; U/unknown/blank -> 'U'"""
    s = raw.strip().lower()
    if re.fullmatch(r"m(ale)?", s):
        return "M"
    if re.fullmatch(r"f(emale)?", s):
        return "F"
    if re.fullmatch(r"(u|unknown)?", s):
        return "U"
    return None

# Maps inconsistent enrollment site labels into a uniform format
# Regex: (r"site[\s_-]*([abc])")
# site: Matches literal word "site" (case-insensitive due to flags=re.IGNORECASE)
# [\s_-]*: Matches zero or more spaces, hyphens, or underscores separating "site" from the location letter
# ([abc]): Capture group 1. Matches a single letter a, b, or c (upper/lower case versions)
# m.group(1).upper(): Normalizes this letter to uppercase.
def clean_site(raw):
    """'siteB', 'Site C', 'SITE-A', 'site-a' -> 'Site A' / 'Site B' / 'Site C'"""
    m = re.fullmatch(r"site[\s_-]*([abc])", raw.strip(), flags=re.IGNORECASE)
    if m is None:
        return None
    return f"Site {m.group(1).upper()}"

# Loads raw CSV without converting empty cells to default NaN values
# Applies .map() each cleaning function to its corresponding column and saves the cleaned series into new df 'out'
# Prints first 8 rows of cleaned data, checks for missing/failed matches and summarizes category distributions
def main():
    df = pd.read_csv(RAW, dtype=str, keep_default_na=False)
    out = pd.DataFrame()
    out["sample_id"] = df["sample_id"].map(clean_sample_id)
    out["patient_name"] = df["patient_name"].map(clean_name)
    out["sex"] = df["sex"].map(clean_sex)
    out["enrollment_site"] = df["enrollment_site"].map(clean_site)

    print(out.head(8).to_string(), "\n")
    print("Rows that failed to match (should all be 0):")
    print(out.isna().sum().to_string(), "\n")
    print(out["sex"].value_counts().to_string(), "\n")
    print(out["enrollment_site"].value_counts().to_string())


if __name__ == "__main__":
    main()
    