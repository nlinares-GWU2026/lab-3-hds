# AI Usage Log
## Entry 1: Discovering Use of .py script for CSV generation
**Model:** Gemini (Flash)
**What I was doing:** I was exploring the data folder on the applied-computing-HDS GitHub. I found that there was a `messy_sequences.fasta` but no `messy_samples.csv` so I wanted to know if I could generate my own to work on the lab with the provided script. It seemed like I would be able to. 
**What I asked first:** "What does this code do? (pasted `generate_data.py`)."
**Exact output (verbatim):** 
This script serves as a **synthetic data generator** for testing or practicing data-cleaning pipelines. It generates two intentionally "messy" files:

---

### 1. `messy_samples.csv` (`gen_samples_csv`)

Creates a CSV table containing $60$ rows (by default) of mock clinical or biological sample records. It introduces realistic messy formatting and irregularities, including:

* **Inconsistent IDs:** Variations like `S0001` vs. `s-0001`.


* **Capitalization issues:** Random uppercase names.


* **Mixed Date Formats:** Mixed representations of dates of birth (e.g., `MM/DD/YYYY`, `YYYY-MM-DD`, `DD-Mon-YYYY`, `MM.DD.YY`).


* **Varied Categorical Values:** Mixed sex formats (`M`, `Female`, `f`, `U`, `unknown`, or empty strings) and site naming variations (`Site A`, `site_a`, `SITE-A`, `Site   C`).


* **Messy Numerical Data:** Glucose values with trailing asterisks (e.g., `120.5*`), missing values represented as `"N/A"`, or mixed measurement units (`mg/dL`, `mmol/L`).



---

### 2. `messy_sequences.fasta` (`gen_fasta`)

Creates a FASTA file containing mock DNA sequence data with realistic header inconsistencies:

* **Heterogeneous Headers:** Header metadata formatted in incompatible key-value styles (using combinations of `=`, `:`, `;`, `|`, spaces, and different casing).


* **Random DNA Sequences:** Generates random nucleotide sequences ($A, C, G, T$) wrapped at $60$ characters per line.



---

### Execution

When executed directly (`python generate_data.py`), it sets fixed random seeds (`seed=42` and `seed=7`) to deterministically produce the exact same two messy output files every time.
**How I verified:** I eventually did run the script (see Entry 2) and the outputs Google Gemini told me to expect were created.

## Entry 2: How to run the `generate_data.py` script and check FASTA generated against professor's existing version
**Model:** Claude (Sonnet 5)
**What I was doing:** I found out that the script created both FASTA and CSV documents that I needed to complete the lab so I wanted a way to run it and check the outputted FASTA against the professor's version so I could at least somewhat confidently move forward with the lab. 
**What I asked first:** "How can I run this script given my current set up (gave my file path: C:\Users\nelin\Desktop\GWU Information\GWU Fall 2026\Applied_Computing\lab-3-hds\data\raw\lab3-messy-data) and check the existing FASTA (professor's) against the new one?"
**Exact output (verbatim):**  
You need `messy_samples.csv`, and the instructor's repo doesn't have it. It does have the program that made it, `generate_data.py`, so we re-run that program to get the file back.

## Why re-running the program gives the same file

The script makes "random" fake data, but it starts each function with `random.seed(42)` (CSV) or `random.seed(7)` (FASTA). A seed fixes the sequence of random numbers, like a deck of cards shuffled the same way every time. Same script, same seed, same Python random generator means the exact same output. That's why the instructor's README calls the data "generator-seeded".

## What the steps do

1. **Make a scratch folder and copy the script into it.** The script writes `messy_samples.csv` and `messy_sequences.fasta` into whatever folder you run it from. If you ran it inside your repo's `lab3-messy-data` folder, it would overwrite the instructor's FASTA that you downloaded. `/tmp/regen` is a throwaway folder where nothing can be damaged.

   ```bash
   mkdir -p /tmp/regen
   cp data/raw/lab3-messy-data/generate_data.py /tmp/regen/
   cd /tmp/regen
   ```

2. **Run the generator there.** It produces a fresh CSV and a fresh FASTA in the scratch folder.

   ```bash
   python generate_data.py
   ```

3. **Compare the regenerated FASTA to the instructor's FASTA.** `diff` prints nothing if two files are identical. This is the check.

   ```bash
   diff /tmp/regen/messy_sequences.fasta data/raw/lab3-messy-data/messy_sequences.fasta && echo "FASTA matches"
   ```

4. **Copy the CSV into your repo.** The CSV is the file you were missing.

   ```bash
   cp /tmp/regen/messy_samples.csv data/raw/lab3-messy-data/
   ```

## What the diff proves, and what it doesn't

You have the instructor's real FASTA but no real CSV, so you can only test the generator against the FASTA. If your run reproduces his FASTA exactly, your Python and his generate the same random numbers from the same seeds. That is strong evidence the CSV matches his too, because the same script and the same kind of random calls produced it. It isn't absolute proof, since the CSV uses a different seed and a few different random functions. That's why the `SOURCE.md` note says the CSV was regenerated rather than downloaded. If he uploads his CSV later, a `diff` against yours settles it.

This is the same reproducibility idea as `environment.yml` from Lab 1. The recipe (script plus seed) recreates the result, and you check that it worked by comparing the result to something known.
**How I verified:** I manually opened both FASTA and did a visual inspection to see if there were indeed any differences. I additionally checked that the folders, files, and paths were correct on my computer. 

## Entry 3: Exploring data prior to cleaning
**Model:** Claude (Sonnet 5)
**What I was doing:** I wanted to know what the data looked like prior to generating a cleaner script and have a layout of all the different formats of entries.
**What I asked first:** "Can you write me a script that profiles this data before we build a cleaner regex script?"
**Exact output (verbatim):**
Phase 2 starts with profiling. Before writing any cleaning code, we look at exactly how the data is messy. Each regex you write later is a response to something you've seen, and it gets checked against what you found.

## Step 1: Create the profiling script

From the repo root (`conda activate lab-3-hds` first if this is a new terminal):

```bash
cat > src/explore_samples.py << 'EOF'
"""Profile messy_samples.csv: what different 'shapes' of mess does each column have?"""
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

print("--- glucose_value shapes ---")
print(df["glucose_value"].str.replace(r"\d+\.\d", "9.9", regex=True).value_counts().to_string(), "\n")

print("--- numeric glucose by unit ---")
g = pd.to_numeric(df["glucose_value"], errors="coerce")
print(g.groupby(df["glucose_unit"].str.lower()).describe()[["count", "min", "mean", "max"]].round(1).to_string())
EOF
```
```bash
python src/explore_samples.py
```

## Why the script is written this way

- **`dtype=str, keep_default_na=False`** makes pandas read everything as raw text. By default it would quietly turn `N/A` and blanks into `NaN`, tidying up some of the mess before you can see it.
- **`.map(repr)`** prints values with quote marks, so a trailing or double space shows up (`'Site C '`). Without it, `Site C` and `Site C ` look identical in the output.
- **`str.replace(r"\d", "9", ...)`** replaces every digit with `9`, so `S0003` and `s-0003` become `S9999` and `s-9999`. This is shape profiling: you count the patterns instead of reading 60 values.
- **The date patterns** use `^` for start of string, `$` for end, and `\d{2}` for exactly two digits. Every row should match exactly one pattern, so the counts should add up to 60 with `unmatched: 0`. That is a coverage check. If a row matches nothing, your regex is missing a format, and you find out now instead of after cleaning.
- **`Path(__file__)`** makes the script find the CSV relative to itself, so it runs from any folder. This matters because the grader may run your scripts from a different working directory than you do.

Your date counts should be 18 / 16 / 12 / 14 with `unmatched: 0`, and the shape should be `(60, 8)`. If so, your regenerated CSV matches mine.

## Step 2: Read the output and decide what "clean" means

Every column has a mess type, and each needs a target format:

| Column | What you'll see | Target |
|---|---|---|
| `sample_id` | `S0001` and `s-0003` | one consistent form |
| `patient_name` | a few ALL CAPS | consistent casing |
| `dob` | four different formats | ISO `YYYY-MM-DD` |
| `sex` | `M`, `m`, `Male`, `U`, `unknown`, and blanks | a small fixed set of codes |
| `enrollment_site` | case, spacing and punctuation variants | `Site A` / `Site B` / `Site C` |
| `glucose_value` | numbers, `N/A`, and values with `*` | numeric column |
| `glucose_unit` | case variants, plus `mmol/L` | one unit |


## Step 3: Commit

```bash
git add src/explore_samples.py
git commit -m "Add profiling script for messy_samples.csv"
git push
```

Run the script and paste the output, or just your answers to the four decisions. Once they're settled, we write `clean_samples_regex.py` one field at a time, starting with the easy ones (ID, sex, site) and ending with dates and glucose.

**How I verified:** I manually examined the output of the code:
```
explore_samples.py
shape: (60, 8)

--- sex ---
sex
'M'          10
'U'           9
'F'           8
'm'           8
'unknown'     6
'f'           5
'Female'      5
'Male'        5
''            4

--- enrollment_site ---
enrollment_site
'Site C '    12
'siteB'      12
'Site B'      9
'Site  C'     8
'SITE-A'      8
'Site A'      7
'site_a'      4

--- glucose_unit ---
glucose_unit
'mg/dl'     18
'MG/DL'     15
'mg/dL'     14
'mmol/L'    13

--- notes ---
notes
''                     55
're-draw requested'     5

--- sample_id shapes ---
sample_id
S9999     51
s-9999     9

--- patient_name casing ---
patient_name
normal    57
UPPER      3

--- dob formats ---
MM/DD/YYYY    18
YYYY-MM-DD    16
DD-Mon-YYYY   12
MM.DD.YY      14
unmatched: 0

--- glucose_vlaue shapes ---
glucose_value
9.9     56
N/A      2
9.9*     2

--- numeric glucose by unit ---
              count   min   mean    max
glucose_unit
mg/dl          44.0  75.4  166.1  249.3
mmol/l         12.0  74.9  145.6  249.2
```
