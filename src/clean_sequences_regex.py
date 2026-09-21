""" Regex cleaning of messy_seqeuences.fasta (Lab 3, approach 1)"""
import re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data/raw/lab3-messy-data/messy_sequences.fasta"
OUT = ROOT / "data/processed/sequences_clean_regex.csv"

# Homo_sapiens, Homo sapiens, H.sapiens, Hsapiens
ORGANISM = r"(?:Homo[ _]sapiens|H\.?sapiens)"
# (?: ... ): Non-capturing group used purely for grouping logical | (OR) 
# choices without creating a regex capture group
# Homo[ _]sapiens: Matches "Homo sapiens" or "Homo_sapiens"
# H\.?sapiens: Matches "Hsapiens" or "H.sapiens" (\.? means an optional literal period)

# Gene symbols are capital letters/digits (BRCA1, TP52, EGFR)
GENE_SYMBOL = r"([A-Z][A-Z0-9]+)\b"
# ([A-Z][A-Z0-9]+): Capture Group 1. Matches standard uppercase gene symbols (starts with an uppercase letter, 
# followed by one or more uppercase letters or numbers, e.g., BRCA1, TP53)
# \b: Word boundary ensuring it doesn't match halfway through a word
GENE_LABELLED = re.compile(r"\b(?:gene|target)\s*[=:]\s*" + GENE_SYMBOL)
# \b(?:gene|target): Looks for the word "gene" or "target"
#\s*[=:]\s*: Matches zero or more spaces surrounding an = or : assignment operator
GENE_AFTER_ORGANISM = re.compile(
    ORGANISM + r"[\s|;]*(?:(?:gene|target)\s*[=:]\s*)?" + GENE_SYMBOL
)
# ORGANISM: Matches any organism variant defined above
# [\s|;]*: Matches zero or more space, pipe |, or semicolon ; delimiters
# (?:(?:gene|target)\s*[=:]\s*)?: An optional non-capturing group for key tags like "gene="

# Parses entries by splitting header lines which start with `>` from 
# multi-line sequence data, returning list of (header, sequence) tuples
def read_fasta(path):
    """Return a list of (header, sequence); header excludes the '>'."""
    records, header, chunks = [], None, []
    for line in path.read_text().splitlines():
        if line.startswith(">"):
            if header is not None:
                records.append((header, "".join(chunks)))
            header, chunks = line[1:], []
        elif line.strip():
            chunks.append(line.strip())
    if header is not None:
        records.append((header, "".join(chunks)))
    return records

# Normalizes sample ID fields into a uniform string format 
# Regex: (r"\s*(?:sample|seq)[_-]?(\d+)")
# \s*: Matches optional leading whitespace
# (?:sample|seq): Non-capturing group matching either "sample" or "seq" 
    # (case-insensitive due to flags=re.IGNORECASE)
# [_-]?: Matches an optional underscore _ or hyphen -
# (\d+): Capture Group 1. Matches one or more digits representing the sample number and 
    # reformats this integer to 3 digits padded with leading zeros)
def parse_sample_id(header):
    """'sample-003', 'SAMPLE_004', 'seq6', 'sample-8' -> 'sample_003' etc."""
    m = re.match(r"\s*(?:sample|seq)[_-]?(\d+)", header, flags=re.IGNORECASE)
    if m is None:
        return None
    return f"sample_{int(m[1]):03d}"

# Searches the header text using the `ORGANISM` pattern previously defined and standardizes 
def parse_organism(header):
    """Any spelling of Homo sapiens (including abbreviations) -> 'Homo sapiens'."""
    if re.search(ORGANISM, header, flags=re.IGNORECASE):
        return "Homo sapiens"
    return None

# Extracts the gene symbol, attempts to match an explicitly labelled gene field
# If missing, falls back to parsing positional text directly following organism name
def parse_gene(header):
    """Try an explicit label first, then fall back to the field after the organism."""
    m = GENE_LABELLED.search(header)
    if m:
        return m[1]
    m = GENE_AFTER_ORGANISM.search(header)
    if m:
        return m[1]
    return None

# Extracts seq length metadata stored within header string, converting to integer
# Regex: (r"\b(?:len|length)\s*[=:]\s*(\d+)")
# \s*[=:]\s*: Matches surrounding spsaces and assignment characters (= or :)
# (\d+): Capture group 1. Mathces one or more digits
# Fallback Regex: (r"\b(\d+)\s*bp\b")
# (\d+): Capture Group 1. Matches digits
# \s*bp\b: Matches optional spacing followed by the word "bp" (base pairs)
def parse_declared_length(header):
    """'len=120', 'length=150bp', '130 bp' -> int; 'len:NA' or nothing -> None."""
    m = re.search(r"\b(?:len|length)\s*[=:]\s*(\d+)", header, flags=re.IGNORECASE)
    if m:
        return int(m[1])
    m = re.search(r"\b(\d+)\s*bp\b", header, flags=re.IGNORECASE)
    if m:
        return int(m[1])
    return None

# Extracts free-text note annotations attached to a header 
# Regex: (r"\bnote\s*[=:]\s*([^|;]+)")
# \bnote\s*[=:]\s*: Matches "note" followed by optional spaces and = or :
# ([^|;]+): Capture Group 1. Matches one or more characters that are NOT a pipe | or semicolon ; ([^...] is a negated character class)
# This ensures the note capture stops before reaching the next metadata field delimiter
def parse_note(header):
    """'note:re-sequenced' -> 're-sequenced'; no note -> ''."""
    m = re.search(r"\bnote\s*[=:]\s*([^|;]+)", header, flags=re.IGNORECASE)
    return m[1].strip() if m else ""

def main():
    records = read_fasta(RAW)
    rows = []
    for header, seq in records:
        declared = parse_declared_length(header)
        actual = len(seq)
        rows.append({
            "sample_id": parse_sample_id(header),
            "organism": parse_organism(header),
            "gene": parse_gene(header),
            "declared_length_bp": declared,
            "actual_length_bp": actual,
            "length_flag": "mismatch" if declared is not None and declared != actual else "",
            "note": parse_note(header),
            "sequence": seq,
        })
    out = pd.DataFrame(rows)
    out["declared_length_bp"] = out["declared_length_bp"].astype("Int64")

    print(out.drop(columns="sequence").to_string(), "\n")
    print("Missing values per column (only declared_length_bp is expected to have gaps):")
    print(out.isna().sum().to_string(), "\n")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False)
    print(f"Wrote {len(out)} rows to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()