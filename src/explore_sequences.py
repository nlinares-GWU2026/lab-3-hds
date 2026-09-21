"""Profile messy_sequences.fasta"""
import re
from pathlib import Path
import pandas as pd

FASTA = Path(__file__).resolve().parent.parent / "data/raw/lab3-messy-data/messy_sequences.fasta"

# Parser loops through line-by-line and when it sees a header starting with ">"
# it saves previous sequence data (header string, concat sequence string, and line count of seq chunks)
# into records. Print total number of FASTA records parsed
def read_fasta(path):
    """Return a list of (header, sequence, n_sequence_lines); header excludes the '>'."""
    records, header, chunks = [], None, []
    for line in path.read_text().splitlines():
        if line.startswith(">"):
            if header is not None:
                records.append((header, "".join(chunks),len(chunks)))
            header, chunks = line[1:], []
        elif line.strip():
            chunks.append(line.strip())
    if header is not None: 
        records.append((header, "".join(chunks), len(chunks)))
    return records

records = read_fasta(FASTA)
print("Records:", len(records), "\n")

# Builds df summarizing sequence metadata across all records 
print("--- Headers next to the real sequence length ---")
table = pd.DataFrame({
    "header": [r[0] for r in records], # 
    "actual_len": [len(r[1]) for r in records], # Total char length of seq
    "seq_lines": [r[2] for r in records], # How many lines raw text made up seq entry
    "non_ACGT": [sorted(set(r[1]) - set("ACGT")) for r in records], # Set subtraction to detect non-standard DNA char (like N) or lowercase
})
print(table.to_string(), "\n")

# Profile header structural inconsistencies by counting common metadata
# delimiter chars (|, ;, =, :, " ")
print("--- Which delimiters appear in each header ---")
delims = pd.DataFrame({
    "pipe |": [h.count("|") for h, _, _ in records],
    "semi ;": [h.count(";") for h, _, _ in records],
    "equals =": [h.count("=") for h, _, _ in records],
    "colon :": [h.count(":") for h, _, _ in records],
    "spaces": [h.count(" ") for h, _, _ in records],
})
print(delims.to_string(), "\n")

# Generate structural "shape" for each header line by converting letter seqs to 
# 'a' and the number seqs to '9'. Prints the shape and calculates how many distinct pattern layouts across the file 
# Regex: (re.sub(r"[A-Za-z]+", "a", h))
# [A-Za-z]+: Matches one or more consecutive uppercase or lowercase letters
# re.sub(..., "a", h): Replaces any block of contiguous letters with a single char 'a'
# \d+: Matches one or more consecutive numeric digits (0-9)
# re.sub(..., "9", ...): Replaces any block of contiguous numbers with a single char
print("--- Header shapes (letters -> a, digits -> 9) ---")
shapes = [re.sub(r"\d+", "9", re.sub(r"[A-Za-z]+", "a", h)) for h, _, _ in records]
for i, s in enumerate(shapes):
    print(f"{i}: {s}")
print("Distinct shapes:", len(set(shapes)), "of", len(shapes))
    