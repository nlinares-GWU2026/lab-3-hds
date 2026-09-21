"""Regex-based cleaning of messy_samples.csv (Lab 3, approach 1)"""
import re
from datetime import date
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data/raw/lab3-messy-data/messy_samples.csv"
OUT = ROOT / "data/processed/samples_clean_regex.csv"
MMOL_TO_MGDL = 18.016 # 1 mmol/L of glucose = 18.016 mg/dL
MMOL_MAX_PLAUSIBLE = 60 # A glucose above this cannot really be in mmol/L
MONTHS = {name: i for i, name in enumerate(
   ["jan", "feb", "mar", "apr", "may", "jun",
     "jul", "aug", "sep", "oct", "nov", "dec"], start=1)} 

def two_digit_year(yy):
    """Century rule (assumption): 00-26 -> 2000s, 27-99 -> 1900s"""
    yy = int(yy)
    return 2000 + yy if yy <=26 else 1900 + yy

def clean_dob(raw):
    """Any of the 4 date formats in the file -> 'YYYY-MM-DD' (or None)"""
    s = raw.strip()
    if m := re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", s):            # MM/DD/YYYY
        month, day, year = int(m[1]), int(m[2]), int(m[3])
    elif m := re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", s):          # YYYY-MM-DD
        year, month, day = int(m[1]), int(m[2]), int(m[3])
    elif m := re.fullmatch(r"(\d{2})-([A-Za-z]{3})-(\d{4})", s):    # DD-Mon-YYYY
        day, month, year = int(m[1]), MONTHS.get(m[2].lower()), int(m[3])
    elif m := re.fullmatch(r"(\d{2})\.(\d{2})\.(\d{2})", s):        # MM.DD.YY
        month, day, year = int(m[1]), int(m[2]), two_digit_year(m[3])
    else:
        return None
    try:
        return date(year, month, day).isoformat() # rejects impossible dates
    except (ValueError, TypeError):
        return None

# Standardizes sample ID strings into uppercase 'S' followed by a 4-digit number
# Regex: (r"[Ss]-?(\d{4})") -> 
# [Ss]: Matches either uppercase 'S' or lowercase 
# -?: Matches optional hyphen, meaning 0 or 1 hyphen
# (/d{4}): Capture group 1. Matches exactly 4 numeric digits (\d) and accessing m.group(1) retrieves 4 digits so can be reformatted as S+digits 
def clean_sample_id(raw):
    """'s-0003' or 'S0003' -> S0003"""
    m = re.fullmatch(r"[Ss]-?(\d{4})", raw.strip())
    if m is None:
        return None
    return f"S{m.group(1)}"

# Normalizes patient names formatted
# Regex:(r"([A-Za-z])\.\s+([A-Za-z]+)")
# ([A-Za-z]): Capture group 1. Matches single letter (uppercase or lowercase) representing the first initial
# \. Matches literal period
#\s+ Matches one or more whitespace spaces/tabs separating intial and last name
# ([A-Za-z]+): Capture group 2. Matches one or more consecutive letters representing last name.
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

# Maps inconsistent glucose unit labels into a uniform format
def clean_glucose_unit(raw):
    """'mg/dl', 'MG/DL', 'mg/dL' -> 'mg/dL'; 'mmol/L' -> 'mmol/L'."""
    s = raw.strip().lower()
    if re.fullmatch(r"mg/dl", s):
        return "mg/dL"
    if re.fullmatch(r"mmol/l", s):
        return "mmol/L"
    return None

# Takes raw text inputs for both the glucose value and the unit label. Standardizes the unit via 
    # clean_glucose_unit() and initializes an empty list 'flags' to record data-quality issues. If 
    # unit is invalid, it flags as 'unit unrecognized'
def clean_glucose(value_raw, unit_raw):
    """Return (glucose in mg/dL, unit as originally labelled, flag text)."""
    unit = clean_glucose_unit(unit_raw)
    flags = []
    if unit is None:
        flags.append("unit_unrecognized")

    # Strips leading/trailing whitespace from raw value and tests for missing entries or unparseable formats
    s = value_raw.strip()
    if re.fullmatch(r"n/?a", s, flags=re.IGNORECASE):
        return None, unit, ";".join(flags + ["missing"])
    m = re.fullmatch(r"(\d+(?:\.\d+)?)(\*)?", s)
    if m is None:
        return None, unit, ";".join(flags + ["unparsed"])

    # Converts the captured numeric option to a float
    # If group 2 captured an asterisk, it appends 'asterisk' to 'flags'
    # Handles unit conversion and joins all active flags into a semicolon-delimited string and returns tuple
    value = float(m[1])
    if m[2]:
        flags.append("asterisk")
    if unit == "mmol/L":
        if value > MMOL_MAX_PLAUSIBLE:
            flags.append("unit_label_implausible")   # treat value as mg/dL
        else:
            value = round(value * MMOL_TO_MGDL, 1)
    return value, unit, ";".join(flags)

# Loads raw CSV without converting empty cells to default NaN values
# Applies .map() each cleaning function to its corresponding column and saves the cleaned series into new df 'out'
# Prints first 8 rows of cleaned data, checks for missing/failed matches and summarizes category distributions
def main():
    df = pd.read_csv(RAW, dtype=str, keep_default_na=False)
    out = pd.DataFrame()
    out["sample_id"] = df["sample_id"].map(clean_sample_id)
    out["patient_name"] = df["patient_name"].map(clean_name)
    out["dob"] = df["dob"].map(clean_dob)
    out["sex"] = df["sex"].map(clean_sex)
    out["enrollment_site"] = df["enrollment_site"].map(clean_site)

    glucose = [clean_glucose(v, u) for v, u in zip(df["glucose_value"], df["glucose_unit"])]
    out["glucose_mg_dl"] = [g[0] for g in glucose]
    out["glucose_unit_original"] = [g[1] for g in glucose]
    out["glucose_flag"] = [g[2] for g in glucose]
    out["notes"] = df["notes"]

    print(out.head(8).to_string(), "\n")
    print("Missing values per column (only glucose_mg_dl should be non-zero):")
    print(out.isna().sum().to_string(), "\n")
    print("glucose_flag counts:")
    print(out["glucose_flag"].map(repr).value_counts().to_string(), "\n")
    print("glucose_mg_dl summary:")
    print(out["glucose_mg_dl"].describe().round(1).to_string(), "\n")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False)
    print(f"Wrote {len(out)} rows to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
    