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

## Entry 4:
**Model:** Claude (Sonnet 5)
**What I was doing:** I needed help writing a cleaner regex code script after making my assumptions on what the data is truly trying to show. I examined the numbers of how many formats appeared per group. 
**What I asked first:** Can you help me write a cleaner regex code script with the following assumptions on the data:
1. Collapse male/M/m and female/F/f into a fixed set and collapse all other unknown/U/'' into "U" for those not recorded (understanding unknown and not recorded are two different things).
2. Turn the enrollment site into a fixed casing with no spacing.
3. First convert any mmol/L into mg/dL to see if it exceeds the 250 cap mark specified in the script (no glucose reading should be in the thousands - deduced that the units were input wrong) and fix case the md/dL/mg/dl/MG/DL.
4. Leave notes as is.
5. Sample id's become all fixed and no spaces or hyphens.
6. Normal case the patient names.
7. Change the DOB formats to be YYYY-MM-DD and read the current dates as month, date, year with cut offs for 1900's beginning at 27-99 and for 2000's 00-26.
8. Leave glucose values that are N/A/* as a `glucose_flag`.
**Exact output (verbatim):**
Those are good decisions. Two notes before we code.

**Date order.** Your conclusion is right: the slash and dot formats are month-first. To be precise, the file has `MM/DD/YYYY` (four-digit year) and `MM.DD.YY` (two-digit year), not dashes. `DD-Mon-YYYY` (like `21-Jun-1997`) uses a month name, so it can't be misread, and `YYYY-MM-DD` is already ISO.

**The `mmol/L` rows.** Your reasoning is sound, and this file lets us confirm it. In `generate_data.py`, the glucose value is drawn uniformly from 70–250 and the unit is picked separately with `random.choice`, so the unit label is noise here. That is a stronger check than the file gives on its face, and real data wouldn't come with one. In a real study you couldn't be sure, and you'd ask whoever collected the data.

That points to the design for the glucose column. We still write a real mmol/L → mg/dL converter (the task asks for "conversion where needed"), but it first checks whether the value is plausible for its label. A glucose above roughly 60 mmol/L is physiologically impossible, so those rows get treated as mg/dL, keep their original label in a separate column, and are flagged. Then document it as an assumption.

## Step 1: Start `src/clean_samples_regex.py`

In VS Code, create `src/clean_samples_regex.py` and paste this in. It handles the four mechanical columns first. Dates and glucose come next, once these work.

```python
"""Regex-based cleaning of messy_samples.csv (Lab 3, approach 1)."""
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data/raw/lab3-messy-data/messy_samples.csv"


def clean_sample_id(raw):
    """'s-0003' or 'S0003' -> 'S0003'."""
    m = re.fullmatch(r"[Ss]-?(\d{4})", raw.strip())
    if m is None:
        return None
    return f"S{m.group(1)}"


def clean_name(raw):
    """'A. NGUYEN' or 'A. Nguyen' -> 'A. Nguyen'."""
    m = re.fullmatch(r"([A-Za-z])\.\s+([A-Za-z]+)", raw.strip())
    if m is None:
        return None
    return f"{m.group(1).upper()}. {m.group(2).capitalize()}"


def clean_sex(raw):
    """M/m/Male -> 'M'; F/f/Female -> 'F'; U/unknown/blank -> 'U'."""
    s = raw.strip().lower()
    if re.fullmatch(r"m(ale)?", s):
        return "M"
    if re.fullmatch(r"f(emale)?", s):
        return "F"
    if re.fullmatch(r"(u|unknown)?", s):
        return "U"
    return None


def clean_site(raw):
    """'siteB', 'Site  C ', 'SITE-A', 'site_a' -> 'Site A' / 'Site B' / 'Site C'."""
    m = re.fullmatch(r"site[\s_-]*([abc])", raw.strip(), flags=re.IGNORECASE)
    if m is None:
        return None
    return f"Site {m.group(1).upper()}"


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
```

Save it, then run from the repo root (use `cd ..` if you're still inside `src`):

```bash
python src/clean_samples_regex.py
```

## Step 2: What to expect

- The first 8 rows show clean values, for example `S0003`, `Site B` and `A. Nguyen`.
- Every "failed to match" count is `0`.
- Sex counts: `M 23`, `U 19`, `F 18`.
- Site counts: `Site A 19`, `Site B 21`, `Site C 20`.

Those counts should equal what you get by adding up the variants from your profiling output. For example, `M` + `m` + `Male` = 10 + 8 + 5 = 23. Check at least one by hand. Comparing raw counts to cleaned counts is how you verify a cleaning step, so put that check in your write-up.

## Step 3: What each regex does

- **`re.fullmatch`** requires the *entire* string to fit the pattern. `match` and `search` would accept `S0003xyz` because part of it fits.
- **`[Ss]-?(\d{4})`**: `[Ss]` is either case of the letter, `-?` is an optional hyphen (which is why `S0003` and `s-0003` both work), and `(\d{4})` is exactly four digits. The parentheses capture those digits so `m.group(1)` returns them.
- **Names**: `\.` is a literal dot (a bare `.` means "any character"), and `\s+` is one or more spaces. `.capitalize()` turns `NGUYEN` into `Nguyen`.
- **Sex**: lowercasing first (`.lower()`) means we only write lowercase patterns. `m(ale)?` is "m", optionally followed by "ale". `(u|unknown)?` makes the whole group optional, so it also matches an empty string, which covers the blanks.
- **Site**: `[\s_-]*` means "any number of spaces, underscores or hyphens, including none". One pattern covers `siteB`, `Site  C` (double space), `SITE-A` and `site_a`, and `re.IGNORECASE` handles the capitals. `.strip()` removes the trailing space in `'Site C '`.
- **Returning `None` on no match** makes a bad value show up as a visible gap instead of a silent wrong guess. That is why the "failed to match" check exists.

## Step 4: Commit

```bash
git add src/clean_samples_regex.py
git commit -m "Regex cleaning: sample_id, name, sex, site"
git push
```

Once your output matches, tell me and we'll add the date function, which has the most decisions in it.
**How I verified:** I manually typed out the code and added comments for what each block and regex function was doing. I also manually verified the output:
```
07:56:01 (lab-3-hds) nelin@Nicole-ASUS lab-3-hds ±|main✔|→ python src/clean_samples_regex.py
  sample_id patient_name sex enrollment_site
0     S0001    A. Nguyen   F          Site A
1     S0002     T. Patel   M          Site A
2     S0003  R. Martinez   F          Site B
3     S0004     B. Smith   F          Site B
4     S0005  B. Martinez   M          Site A
5     S0006   A. Johnson   F          Site B
6     S0007  T. Martinez   U          Site A
7     S0008  T. Martinez   M          Site A

Rows that failed to match (should all be 0):
sample_id          0
patient_name       0
sex                0
enrollment_site    0

sex
M    23
U    19
F    18

enrollment_site
Site B    21
Site C    20
Site A    19
```
**What I asked next:** After pasting my output (above), I prompted Claude to finish the code with the date function because in the previous answer it claimed it was more of a complicated step requiring decisions. "Can you edit the current code you just sent to include the date/time function and explain what it does?" 
**Exact output (verbatim):***
Your output matches mine on every check. Next is the date function, which takes more care than the other columns.

## Step 1: Three edits to `src/clean_samples_regex.py`

**Edit 1: imports.** At the top, add one line so the imports read:

```python
import re
from datetime import date
from pathlib import Path
```

**Edit 2: helpers.** Paste this block right after the `RAW = ...` line and before `def clean_sample_id`:

```python
MONTHS = {name: i for i, name in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun",
     "jul", "aug", "sep", "oct", "nov", "dec"], start=1)}


def two_digit_year(yy):
    """Century rule (our assumption): 00-26 -> 2000s, 27-99 -> 1900s."""
    yy = int(yy)
    return 2000 + yy if yy <= 26 else 1900 + yy


def clean_dob(raw):
    """Any of the 4 date formats in the file -> 'YYYY-MM-DD' (or None)."""
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
        return date(year, month, day).isoformat()   # rejects impossible dates
    except (ValueError, TypeError):
        return None
```

**Edit 3: replace the whole `main()`** with this version, which adds the `dob` column and some checks:

```python
def main():
    df = pd.read_csv(RAW, dtype=str, keep_default_na=False)
    out = pd.DataFrame()
    out["sample_id"] = df["sample_id"].map(clean_sample_id)
    out["patient_name"] = df["patient_name"].map(clean_name)
    out["dob"] = df["dob"].map(clean_dob)
    out["sex"] = df["sex"].map(clean_sex)
    out["enrollment_site"] = df["enrollment_site"].map(clean_site)

    print(out.head(8).to_string(), "\n")
    print("Rows that failed to match (should all be 0):")
    print(out.isna().sum().to_string(), "\n")
    print(out["sex"].value_counts().to_string(), "\n")
    print("dob range:", out["dob"].min(), "to", out["dob"].max(), "\n")
    print(pd.DataFrame({"raw": df["dob"], "clean": out["dob"]}).head(12).to_string(), "\n")
    print(out["enrollment_site"].value_counts().to_string())
```

Save and run from the repo root:

```bash
python src/clean_samples_regex.py
```

## Step 2: What to expect

- All the "failed to match" counts are `0`, now including `dob`.
- `dob range: 1951-02-06 to 2018-05-11`.
- In the raw → clean table, row 1 is `12/16/1974` → `1974-12-16` and row 2 is `11.24.53` → `1953-11-24`. Those are the two rows you used to settle the date order.

## Step 3: How the date function works

- **One function, four patterns, tried in order.** Each format is recognized by its shape. The parentheses capture three numbers, and the code puts them back in a fixed year, month, day order. The capture order differs per format, and getting that right is the whole job. `MM/DD/YYYY` captures month first, while `YYYY-MM-DD` captures year first.
- **`:=`** (the "walrus") tests the match and stores it in `m` in one step, so each `elif` can immediately use `m[1]`, `m[2]` and so on.
- **`two_digit_year` is its own function** so your century assumption lives in exactly one place. It's easy to find, change and document.
- **`date(year, month, day)` is a second safety net.** A regex only checks *shape*: `\d{2}` accepts `13` or `99` as a month. It can't know that `02/30/1960` isn't a real date. Building an actual date object rejects impossible dates, and the `except` turns them into a visible `None` gap instead of a bad value. It also catches an unknown month abbreviation, where `MONTHS.get` returns `None`.

## Step 4: Verify it three ways

1. Zero failures across all columns.
2. The range check. If the century rule were wrong, the maximum would show up in the 2050s or 2060s. Yours ends in 2018.
3. Spot-check the two rows above against the raw CSV.

## Step 5: Commit

```bash
git add src/clean_samples_regex.py
git commit -m "Regex cleaning: add dob standardization"
git push
```

Next is glucose: the value, the `N/A` and `*` handling with the flag column, and the unit-plausibility logic we designed. Then we write the output table.
**How I verified:** I manually typed out the code and added comments for what the block and regex function was doing. I also manually verified the output:

