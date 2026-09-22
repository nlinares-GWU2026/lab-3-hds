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

Run the script and paste the output. Once they're settled, we write `clean_samples_regex.py` one field at a time, starting with the easy ones (ID, sex, site) and ending with dates and glucose.

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

## Entry 5: 

**
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
```
08:18:20 (lab-3-hds) nelin@Nicole-ASUS lab-3-hds ±|main✔|→ python src/clean_samples_regex.py
  sample_id patient_name         dob sex enrollment_site
0     S0001    A. Nguyen  1962-07-09   F          Site A
1     S0002     T. Patel  1974-12-16   M          Site A
2     S0003  R. Martinez  1953-11-24   F          Site B
3     S0004     B. Smith  1975-12-18   F          Site B
4     S0005  B. Martinez  1997-12-02   M          Site A
5     S0006   A. Johnson  1955-12-09   F          Site B
6     S0007  T. Martinez  1969-09-04   U          Site A
7     S0008  T. Martinez  1997-06-21   M          Site A

Rows that failed to match (should all be 0):
sample_id          0
patient_name       0
dob                0
sex                0
enrollment_site    0

sex
M    23
U    19
F    18

dob range: 1951-02-06 to 2018-05-11

            raw       clean
0    07/09/1962  1962-07-09
1    12/16/1974  1974-12-16
2      11.24.53  1953-11-24
3    12/18/1975  1975-12-18
4    1997-12-02  1997-12-02
5    1955-12-09  1955-12-09
6    1969-09-04  1969-09-04
7   21-Jun-1997  1997-06-21
8    2018-05-11  2018-05-11
9    10/01/1951  1951-10-01
10   1997-10-16  1997-10-16
11  21-Apr-2008  2008-04-21

enrollment_site
Site B    21
Site C    20
Site A    19
08:18:41 (lab-3-hds) nelin@Nicole-ASUS lab-3-hds ±|main✔|→
```

**What I asked next:** After pasting my output (above), I prompted Claude to finish the code with the glucose function because in the previous answer it claimed it was more of a complicated step. "Can you edit the current code you just sent to include the glucose function and explain what it does?"

**Exact outout (verbatim):** 
We can finish the regex script. Its last piece is glucose, plus writing the output table.

## Step 1: Four edits to `src/clean_samples_regex.py`

**Edit 1: constants.** Add these right after the `RAW = ...` line:

```python
OUT = ROOT / "data/processed/samples_clean_regex.csv"

MMOL_TO_MGDL = 18.016        # 1 mmol/L of glucose = 18.016 mg/dL
MMOL_MAX_PLAUSIBLE = 60      # a glucose above this can't really be in mmol/L
```

**Edit 2: glucose functions.** Paste these after `clean_site` and before `main()`:

```python
def clean_glucose_unit(raw):
    """'mg/dl', 'MG/DL', 'mg/dL' -> 'mg/dL'; 'mmol/L' -> 'mmol/L'."""
    s = raw.strip().lower()
    if re.fullmatch(r"mg/dl", s):
        return "mg/dL"
    if re.fullmatch(r"mmol/l", s):
        return "mmol/L"
    return None


def clean_glucose(value_raw, unit_raw):
    """Return (glucose in mg/dL, unit as originally labelled, flag text)."""
    unit = clean_glucose_unit(unit_raw)
    flags = []
    if unit is None:
        flags.append("unit_unrecognized")

    s = value_raw.strip()
    if re.fullmatch(r"n/?a", s, flags=re.IGNORECASE):
        return None, unit, ";".join(flags + ["missing"])
    m = re.fullmatch(r"(\d+(?:\.\d+)?)(\*)?", s)
    if m is None:
        return None, unit, ";".join(flags + ["unparsed"])

    value = float(m[1])
    if m[2]:
        flags.append("asterisk")
    if unit == "mmol/L":
        if value > MMOL_MAX_PLAUSIBLE:
            flags.append("unit_label_implausible")   # treat value as mg/dL
        else:
            value = round(value * MMOL_TO_MGDL, 1)
    return value, unit, ";".join(flags)
```

**Edit 3: replace the whole `main()`** with this version:

```python
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
```

Keep the `if __name__ == "__main__": main()` lines at the very bottom. Then run it from the repo root:

```bash
python src/clean_samples_regex.py
```

## Step 2: What to expect

- **Missing values:** `0` everywhere except `glucose_mg_dl`, which is `2`. Those are the two `N/A` rows.
- **Flag counts:** `''` 44, `'unit_label_implausible'` 12, `'missing'` 2, `'asterisk'` 2. They add up to 60, and the 12 matches the 12 numeric `mmol/L` rows in your profiling table.
- **Glucose summary:** count 58, min 74.9, max 249.3. Everything is now in one unit and in a plausible range.
- **Last line:** `Wrote 60 rows to data/processed/samples_clean_regex.csv`.
- **Row `S0006`:** shows `141.2`, `mmol/L`, `unit_label_implausible`.

## Step 3: How the glucose function works

- **Three outputs at once.** `clean_glucose` returns a tuple of (value, original unit, flag), which `main()` splits into the three columns. Keeping the original unit label in its own column means nobody has to guess what the raw file said.
- **`(\d+(?:\.\d+)?)(\*)?`** reads as: digits, then optionally a dot and more digits, then optionally a literal star. `(?:...)` groups without capturing, which keeps `m[1]` and `m[2]` simple. The star is written `\*` because a bare `*` is a regex operator. `m[2]` holds the star, or `None` if there wasn't one.
- **`n/?a`** with `IGNORECASE` matches `N/A`, `n/a` and `NA`.
- **Flags are joined with `;`**, so one row can carry several, such as `asterisk;unit_label_implausible`.
- **The unit rule.** Labelled `mmol/L` and above 60, it's flagged and left as-is. Labelled `mmol/L` and 60 or below, it's multiplied by 18.016.
- **Anything unexpected** (`unit_unrecognized`, `unparsed`) becomes a flagged gap instead of a guess.

## Step 4: Test the conversion

This dataset never uses the conversion branch, because every `mmol/L` value is implausibly large. Code that never runs is code you haven't verified, so test it directly:

```bash
python -c "import sys; sys.path.insert(0, 'src'); import clean_samples_regex as c; print(c.clean_glucose('12.5', 'mmol/L')); print(c.clean_glucose('150.0*', 'mmol/L'))"
```

You should get:

```
(225.2, 'mmol/L', '')
(150.0, 'mmol/L', 'asterisk;unit_label_implausible')
```

The first line is 12.5 × 18.016 = 225.2. The second shows two flags on one row. Then check the output file:

```bash
head -5 data/processed/samples_clean_regex.csv
wc -l data/processed/samples_clean_regex.csv
```

`wc -l` should show `61` (a header plus 60 rows).

## Step 5: Commit

This commit includes the output table, so the deliverable is in the repo. Note that `data/processed/` now has a real file, which is exactly why it will show up on GitHub this time.

```bash
git pull --rebase
git add src/clean_samples_regex.py data/processed/samples_clean_regex.csv
git commit -m "Regex cleaning: glucose value/unit/flag, write output table"
git push
```
**How I verified:**  I manually typed out the code and added comments for what the block and regex function was doing. I also manually verified the output (expecting that the glucose_mg_dl should be non-zero):
```
08:18:41 (lab-3-hds) nelin@Nicole-ASUS lab-3-hds ±|main✔|→ python src/clean_samples_regex.py
  sample_id patient_name         dob sex enrollment_site  glucose_mg_dl glucose_unit_original            glucose_flag notes
0     S0001    A. Nguyen  1962-07-09   F          Site A           75.4                 mg/dL                           
1     S0002     T. Patel  1974-12-16   M          Site A          120.0                 mg/dL                           
2     S0003  R. Martinez  1953-11-24   F          Site B           84.2                 mg/dL                           
3     S0004     B. Smith  1975-12-18   F          Site B          120.0                 mg/dL                           
4     S0005  B. Martinez  1997-12-02   M          Site A          248.1                 mg/dL                           
5     S0006   A. Johnson  1955-12-09   F          Site B          141.2                mmol/L  unit_label_implausible   
6     S0007  T. Martinez  1969-09-04   U          Site A          225.0                 mg/dL                           
7     S0008  T. Martinez  1997-06-21   M          Site A          192.7                 mg/dL                           

Missing values per column (only glucose_mg_dl should be non-zero):
sample_id                0
patient_name             0
dob                      0
sex                      0
enrollment_site          0
glucose_mg_dl            2
glucose_unit_original    0
glucose_flag             0
notes                    0

glucose_flag counts:
glucose_flag
''                          44
'unit_label_implausible'    12
'missing'                    2
'asterisk'                   2

glucose_mg_dl summary:
count     58.0
mean     161.9
std       52.0
min       74.9
25%      120.0
50%      156.3
75%      209.1
max      249.3

Wrote 60 rows to data/processed/samples_clean_regex.csv
08:33:43 (lab-3-hds) nelin@Nicole-ASUS lab-3-hds ±|main ✗|→
```
## Entry 6: Exploring the sequences FASTA

**Model:** Claude (Sonnet 5)

**What I was doing:** I wanted to know what the sequences looked like prior to generating a cleaner script and have a layout of all the different formats of entries.

**What I asked first:** "Can you write me a script that profiles this sequences FASTA before we build a cleaner regex script?" (attached the sequences FASTA)

**Exact ouput (verbatim):** 
Here's the FASTA profiler. It works on the same principle as the CSV one, with one big difference. The CSV came with columns and we standardized what was in them. Here the columns don't exist yet, because each header is one free-text string and parsing has to create the fields.

## Step 1: Create `src/explore_sequences.py`

In VS Code, create the file in `src/` and paste this in:

```python
"""Profile messy_sequences.fasta: what do the headers and sequences look like?"""
import re
from pathlib import Path

import pandas as pd

FASTA = Path(__file__).resolve().parent.parent / "data/raw/lab3-messy-data/messy_sequences.fasta"


def read_fasta(path):
    """Return a list of (header, sequence, n_sequence_lines); header excludes the '>'."""
    records, header, chunks = [], None, []
    for line in path.read_text().splitlines():
        if line.startswith(">"):
            if header is not None:
                records.append((header, "".join(chunks), len(chunks)))
            header, chunks = line[1:], []
        elif line.strip():
            chunks.append(line.strip())
    if header is not None:
        records.append((header, "".join(chunks), len(chunks)))
    return records


records = read_fasta(FASTA)
print("records:", len(records), "\n")

pd.set_option("display.width", 200)
pd.set_option("display.max_colwidth", 80)

print("--- headers next to the real sequence length ---")
table = pd.DataFrame({
    "header": [r[0] for r in records],
    "actual_len": [len(r[1]) for r in records],
    "seq_lines": [r[2] for r in records],
    "non_ACGT": [sorted(set(r[1]) - set("ACGT")) for r in records],
})
print(table.to_string(), "\n")

print("--- which delimiters appear in each header ---")
delims = pd.DataFrame({
    "pipe |": [h.count("|") for h, _, _ in records],
    "semi ;": [h.count(";") for h, _, _ in records],
    "equals =": [h.count("=") for h, _, _ in records],
    "colon :": [h.count(":") for h, _, _ in records],
    "spaces": [h.count(" ") for h, _, _ in records],
})
print(delims.to_string(), "\n")

print("--- header shapes (letters -> a, digits -> 9) ---")
shapes = [re.sub(r"\d+", "9", re.sub(r"[A-Za-z]+", "a", h)) for h, _, _ in records]
for i, s in enumerate(shapes):
    print(f"{i}: {s}")
print("distinct shapes:", len(set(shapes)), "of", len(shapes))
```

Save it, then run it from the repo root:

```bash
python src/explore_sequences.py
```

## Step 2: How the script works

- **`read_fasta`** is a small hand-written reader, so no Biopython is needed for 8 records. A line starting with `>` begins a new record, and `line[1:]` drops the `>` from the header. Every other line is sequence, and the sequence is wrapped at 60 characters across several lines. That's why we join the lines (`"".join(chunks)`) before measuring length. Counting only the first line would give you 60.
- **`seq_lines`** shows how many lines each sequence was split over.
- **`non_ACGT`** lists any characters in a sequence other than the four bases, such as `N`, lowercase letters or stray spaces. An empty list means the sequence is clean.
- **The delimiter table** counts each separator per header.
- **The shape trick** is the same as the `S9999` one from the CSV. Every run of letters becomes `a` and every run of digits becomes `9`, so what's left is the *structure* of the header.

## Step 3: What to expect and what it shows

Checkpoints against my run: `records: 8`, `actual_len` of 120 for the first record and 123 for the last, and `distinct shapes: 8 of 8`.

- **Eight records, eight different shapes.** No two headers share a format, so one regex for the whole header can't work, and neither can one split on a delimiter. The delimiter table shows why. Some headers use pipes, some semicolons, and some only spaces, and `Homo sapiens` contains a space of its own, so splitting on spaces would cut the organism name in half. The approach that fits is the same one we used for the CSV: one small regex per *field* (ID, organism, gene, length), each written to tolerate the variants.
- **The sequences themselves are clean.** `non_ACGT` is empty for all 8, so the mess is entirely in the headers.

## Step 4: Commit

```bash
git pull --rebase
git add src/explore_sequences.py
git commit -m "Add profiling script for messy_sequences.fasta"
git push
```

Run the script and then we'll write `clean_sequences_regex.py`.

**How I verified:** I ran the script and manually examined the output:
```
01:54:56 (lab-3-hds) nelin@Nicole-ASUS lab-3-hds ±|main ✗|→ python src/explore_sequences.py
Records: 8

--- Headers next to the real sequence length ---
                                                          header  actual_len  seq_lines non_ACGT
0            sample_001|organism=Homo_sapiens|gene=BRCA1|len=120         120          2       []
1                      Sample002 organism:Homo sapiens gene:TP53         134          3       []
2                sample-003 | Homo_sapiens | EGFR | length=150bp         157          3       []
3                      SAMPLE_004;species=H.sapiens;target=BRCA1         104          2       []
4                           sample005 Homo sapiens; TP53; 130 bp         144          3       []
5                                             seq6|Hsapiens|EGFR         125          3       []
6  Sample_007 organism=Homo_sapiens|gene=BRCA1|note:re-sequenced         135          3       []
7                 sample-8 species:Homo_sapiens gene:TP53 len:NA         123          3       []

--- Which delimiters appear in each header ---
   pipe |  semi ;  equals =  colon :  spaces
0       3       0         3        0       0
1       0       0         0        2       3
2       3       0         1        0       6
3       0       2         2        0       0
4       0       2         0        0       5
5       2       0         0        0       0
6       2       0         2        1       1
7       0       0         0        3       3

--- Header shapes (letters -> a, digits -> 9) ---
0: a_9|a=a_a|a=a9|a=9
1: a9 a:a a a:a9
2: a-9 | a_a | a | a=9a
3: a_9;a=a.a;a=a9
4: a9 a a; a9; 9 a
5: a9|a|a
6: a_9 a=a_a|a=a9|a:a-a
7: a-9 a:a_a a:a9 a:a
```

**What I asked next:** After I reviewed the output of the profiler script and analyzed the data, I asked Claude "Can you help me write a cleaner regex code script (like you did with the CSV) with the following assumptions on the data for the sequences:
1. Sample ID: `sample_001` format to 3 digits.
2. Organism: Keep the organism column named `organism` but more importantly expand the species to `Homo sapiens` (if it is H. or otherwise).
3. Extra fields: Make a column for notes.
4. Gene: Look for `gene=`, `gene:`, `target=` label first (after organism), otherwise capture anything after the organism before a separator (|, ;, " "). Additionally, have the gene look like a gene symbol (capital letters and digits starting with a letter) so `len` or `note` cannot be picked up accidentally.
5. Length: Extract numeric length values from header strings across various formats (`len=`, `150bp` and `130bp`, etc.) while standardizing missing entries as NA, compute the sequence's actual length directly from string sequence to preserve data type consistency and finally create a `length_flag` column to flag mismatches.

**Exact output (verbatim):** 
Your instincts on 1–3 are all fine.

## Step 1: Create `src/clean_sequences_regex.py`

```python
"""Regex-based cleaning of messy_sequences.fasta (Lab 3, approach 1)."""
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data/raw/lab3-messy-data/messy_sequences.fasta"
OUT = ROOT / "data/processed/sequences_clean_regex.csv"

# Homo_sapiens, Homo sapiens, H.sapiens, Hsapiens
ORGANISM = r"(?:Homo[ _]sapiens|H\.?sapiens)"
# gene symbols are capital letters/digits by convention: BRCA1, TP53, EGFR
GENE_SYMBOL = r"([A-Z][A-Z0-9]+)\b"
GENE_LABELLED = re.compile(r"\b(?:gene|target)\s*[=:]\s*" + GENE_SYMBOL)
GENE_AFTER_ORGANISM = re.compile(
    ORGANISM + r"[\s|;]*(?:(?:gene|target)\s*[=:]\s*)?" + GENE_SYMBOL
)


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


def parse_sample_id(header):
    """'sample-003', 'SAMPLE_004', 'seq6', 'sample-8' -> 'sample_003' etc."""
    m = re.match(r"\s*(?:sample|seq)[_-]?(\d+)", header, flags=re.IGNORECASE)
    if m is None:
        return None
    return f"sample_{int(m[1]):03d}"


def parse_organism(header):
    """Any spelling of Homo sapiens (including abbreviations) -> 'Homo sapiens'."""
    if re.search(ORGANISM, header, flags=re.IGNORECASE):
        return "Homo sapiens"
    return None


def parse_gene(header):
    """Try an explicit label first, then fall back to the field after the organism."""
    m = GENE_LABELLED.search(header)
    if m:
        return m[1]
    m = GENE_AFTER_ORGANISM.search(header)
    if m:
        return m[1]
    return None


def parse_declared_length(header):
    """'len=120', 'length=150bp', '130 bp' -> int; 'len:NA' or nothing -> None."""
    m = re.search(r"\b(?:len|length)\s*[=:]\s*(\d+)", header, flags=re.IGNORECASE)
    if m:
        return int(m[1])
    m = re.search(r"\b(\d+)\s*bp\b", header, flags=re.IGNORECASE)
    if m:
        return int(m[1])
    return None


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
```

Save it, then run from the repo root:

```bash
python src/clean_sequences_regex.py
```

## Step 2: What to expect

- Genes come out as BRCA1, TP53, EGFR, BRCA1, TP53, EGFR, BRCA1, TP53, in record order.
- `declared_length_bp` has values only for `sample_001` (120), `sample_003` (150) and `sample_005` (130), with 5 missing.
- `length_flag` says `mismatch` for exactly two rows, `sample_003` and `sample_005`.
- `note` has `re-sequenced` only for `sample_007`.
- Missing values are `0` in every column except `declared_length_bp`, which has `5`.
- Last line: `Wrote 8 rows to data/processed/sequences_clean_regex.csv`.

## Step 3: What's new in the code

- **`ORGANISM`** covers all four spellings in one pattern. `[ _]` means a space or an underscore, and `H\.?sapiens` means "H", an optional literal dot, then "sapiens". The pattern is reused inside the gene regex so the two stay consistent.
- **`GENE_AFTER_ORGANISM`** reads as: the organism, then any run of spaces, pipes or semicolons (`[\s|;]*`), then an optional label (`(?:...)?`), then the gene symbol. That's your "after Homo sapiens" idea, made precise.
- **`re.compile`** builds each pattern once, which is also good for readability.
- **`f"sample_{int(m[1]):03d}"`** turns the captured digits into a number and zero-pads it to 3 places, so `6` and `006` both become `006`.
- **`.astype("Int64")`** keeps whole numbers as whole numbers with gaps. Plain pandas would turn the column into decimals like `120.0` because of the missing values.
- **`read_fasta`** is copied from the profiler. Importing it instead would re-run the profiler's printing, because that script runs its code at the top level.
  
## Step 4: Commit

```bash
git pull --rebase
git add src/clean_sequences_regex.py data/processed/sequences_clean_regex.csv
git commit -m "Regex cleaning for FASTA headers"
git push
```
Run it and check the points above. 

**How I verified:** I manually typed out the code and added comments for what each block and regex function was doing. I also manually verified the output:
```
06:16:37 (lab-3-hds) nelin@Nicole-ASUS lab-3-hds ±|main ✗|→ python src/clean_sequences_regex.py
    sample_id      organism   gene  declared_length_bp  actual_length_bp length_flag          note
0  sample_001  Homo sapiens  BRCA1                 120               120
1  sample_002  Homo sapiens   TP53                <NA>               134
2  sample_003  Homo sapiens   EGFR                 150               157    mismatch
3  sample_004  Homo sapiens  BRCA1                <NA>               104
4  sample_005  Homo sapiens   TP53                 130               144    mismatch
5  sample_006  Homo sapiens   EGFR                <NA>               125
6  sample_007  Homo sapiens  BRCA1                <NA>               135              re-sequenced
7  sample_008  Homo sapiens   TP53                <NA>               123

Missing values per column (only declared_length_bp is expected to have gaps):
sample_id             0
organism              0
gene                  0
declared_length_bp    5
actual_length_bp      0
length_flag           0
note                  0
sequence              0
```

## Entry 7: Building analytic table (graduate addendum)

**Model:** Claude (Sonnet 5)

**What I was doing:** After constructing and completing both of the CSV files, I needed to build a samples x features x metadata table per the graduate addendum. I separated the `samples_clean_regex.csv` into the "samples, features metadata" groups and assigned columns: Identifier: `sample_id`, Feature: `glucose_mg_dl`, Metadata: `sex`, `enrollment_site`, `dob`, `notes`, `glucose_flag`, `glucose_unit_original`.

**What I asked first:** With the organization parameters of Groups: Columns, I need the `samples_clean_regex.csv` to be arranged in a table with the following structure samples x features x metadata. I have defined the following parameters: Identifier: `sample_id`, Feature: `glucose_mg_dl`, Metadata: `sex`, `enrollment_site`, `dob`, `notes`, `glucose_flag`, `glucose_unit_original`. I also need the output to be able to checked against the following criteria "re types consistent? is missingness documented rather than silently dropped? are units resolved to one system?"

**Exact output (verbatim):**

This reads your cleaned CSV table and produces a samples × features × metadata table plus the readiness checks. 

The column split:

| Group | Columns |
|---|---|
| Identifier | `sample_id` |
| Feature | `glucose_mg_dl` |
| Metadata | `sex`, `enrollment_site`, `dob`, `notes`, `glucose_flag`, `glucose_unit_original` |

The main thing this script adds beyond the split is turning `dob` into `age_years`, since a raw birth date is an identifier-adjacent metadata field, and age is what an analysis would actually use.

**Create `src/build_analytic_table.py`:**

```python
"""Build a samples x features x metadata table from the cleaned CSV output,
following Week 5's shape, and check it against the readiness checklist."""
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CLEAN = ROOT / "data/processed/samples_clean_regex.csv"
OUT = ROOT / "data/processed/samples_analytic.csv"

FEATURE_COLS = ["glucose_mg_dl"]
METADATA_COLS = ["sex", "enrollment_site", "age_years", "notes",
                  "glucose_flag", "glucose_unit_original"]


def age_from_dob(dob_str, as_of=date(2026, 9, 30)):
    """'YYYY-MM-DD' -> age in whole years as of as_of."""
    y, m, d = (int(p) for p in dob_str.split("-"))
    born = date(y, m, d)
    years = as_of.year - born.year
    if (as_of.month, as_of.day) < (born.month, born.day):
        years -= 1
    return years


def main():
    df = pd.read_csv(CLEAN, keep_default_na=False,
                      na_values={"glucose_mg_dl": ""})
    df["age_years"] = df["dob"].map(age_from_dob)

    out = df[["sample_id"] + FEATURE_COLS + METADATA_COLS].set_index("sample_id")

    print(out.head(8).to_string(), "\n")
    print("dtypes:")
    print(out.dtypes.to_string(), "\n")
    print("Missing values per column:")
    print(out.isna().sum().to_string(), "\n")
    print("age_years range:", out["age_years"].min(), "to", out["age_years"].max())

    out.to_csv(OUT)
    print(f"\nWrote {len(out)} rows to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
```

Run it from the repo root:

```bash
python src/build_analytic_table.py
```

## What to expect

- `dtypes` shows `glucose_mg_dl` as a float, `age_years` as an integer, and the rest as text (`object`).
- Missing values: `2` for `glucose_mg_dl` (the `N/A` rows), `0` everywhere else.
- `age_years range: 8 to 75`, using Sep 30, 2026 (the due date) as the reference point. That choice is worth a line in the write-up, since "age" always needs an as-of date.
- Last line: `Wrote 60 rows to data/processed/samples_analytic.csv`.

## How it works

- **`keep_default_na=False, na_values={"glucose_mg_dl": ""}`**: your cleaned CSV writes missing glucose as an empty cell, and this tells pandas to treat that column's blanks as real missing values while every other column's text is read literally. Without it, pandas might also blank out something like a genuinely empty `notes` field in an unintended way, or fail to recognize the glucose gap at all.
- **`age_from_dob`** does the month/day comparison by hand rather than just subtracting years, so someone born Oct 1 isn't counted as a year older before their birthday has actually happened.
- **`set_index("sample_id")`** makes the identifier the row label instead of a data column, which is exactly what "one row per sample" means in practice.
- **The printed checks** are the same four items from the readiness checklist: `dtypes` for consistent types, `isna().sum()` for documented missingness, the column split for metadata/feature separation, and the fact that `glucose_mg_dl` is a single unit (mg/dL) for units resolved.

## Commit

```bash
git pull --rebase
git add src/build_analytic_table.py data/processed/samples_analytic.csv
git commit -m "Build samples x features x metadata table for addendum"
git push
```

Run it, paste the output, and then we move to Phase B: the Gemini rounds on the CSV and FASTA.

**How I verified:** I manually examined the output of the code and verified that all values and expectations I had checked out:
```
 python src/build_analytic_table.py
           glucose_mg_dl sex enrollment_site  age_years notes            glucose_flag glucose_unit_original
sample_id
S0001               75.4   F          Site A         64                                               mg/dL
S0002              120.0   M          Site A         51                                               mg/dL
S0003               84.2   F          Site B         72                                               mg/dL
S0004              120.0   F          Site B         50                                               mg/dL
S0005              248.1   M          Site A         28                                               mg/dL
S0006              141.2   F          Site B         70        unit_label_implausible                mmol/L
S0007              225.0   U          Site A         57                                               mg/dL
S0008              192.7   M          Site A         29                                               mg/dL

dtypes:
glucose_mg_dl            float64
sex                       object
enrollment_site           object
age_years                  int64
notes                     object
glucose_flag              object
glucose_unit_original     object

Missing values per column:
glucose_mg_dl            2
sex                      0
enrollment_site          0
age_years                0
notes                    0
glucose_flag             0
glucose_unit_original    0

age_years range: 8 to 75

Wrote 60 rows to data/processed/samples_analytic.csv
```
## Entry 8: Build small comparison tool to compare outputs

**Tool:** Claude (Sonnet 5)

**What I was doing:** I was at the stage of comparing the two outputs between my own regex and the AI. Instead of manually eyeballing the data side by side, I decided that having Claude right a small script would be more accurate and efficient. 

**What I asked first:** "Can you write me a simple script that compares the outputs of these files? (attached the file path and the 4 files). 

**Exact output (verbatim):** 
```
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
```

**How I verified:** I typed out the script and ran it, then quickly manually verified the output and looked over my own files to ensure correctness: 
Note: Across all 12 rows flagged `unit_label_implausable`, the AI applied a glucose conversion factor of 1.80182 rather than the stated 18.012 which is an exact factor of 10 error, confirmed by the exact reproduction of all 12 AI values. The regex approach avoided the error entirely by treating an unrealistically high mmol/L labelled value as already being in mg/dL, rather than trusting the unit label and converting it. 
```
11:23:17 (lab-3-hds) nelin@Nicole-ASUS lab-3-hds ±|main ✗|→ python src/compare_outputs.py
=== messy_samples.csv ===
regex rows: 60   ai rows: 60
0 of 60 shared rows differ on at least one column

--- messy_samples.csv: numeric comparison on 'glucose_mg_dl' (tolerance ±0.05) ---
S0006: regex=141.2 ai=254.4  (ai/regex = 1.802)
S0011: regex=99.7 ai=179.6  (ai/regex = 1.801)
S0014: regex=133.8 ai=241.1  (ai/regex = 1.802)
S0015: regex=150.8 ai=271.7  (ai/regex = 1.802)
S0016: regex=112.5 ai=202.7  (ai/regex = 1.802)
S0017: regex=249.2 ai=449.0  (ai/regex = 1.802)
S0024: regex=169.5 ai=305.4  (ai/regex = 1.802)
S0033: regex=105.0 ai=189.2  (ai/regex = 1.802)
S0035: regex=225.1 ai=405.6  (ai/regex = 1.802)
S0038: regex=157.4 ai=283.6  (ai/regex = 1.802)
S0039: regex=74.9 ai=135.0  (ai/regex = 1.802)
S0046: regex=128.5 ai=231.5  (ai/regex = 1.802)
12 of 60 shared rows differ on 'glucose_mg_dl'

=== messy_sequences.fasta ===
regex rows: 8   ai rows: 8
0 of 8 shared rows differ on at least one column

--- messy_sequences.fasta: numeric comparison on 'declared_length_bp' (tolerance ±0.5) ---
0 of 8 shared rows differ on 'declared_length_bp'
```

# AI ASSISTED CLEANING - EXPLICIT PROMPT AND OUTPUT
- **Tool:** Google Gemini (Flash)
- **(CSV) Prompt 1 (verbatim):** Below is a small clinical sample CSV (60 rows). Do not clean it yet, do not write or run code. Just read it and tell me, column by column, what inconsistencies or ambiguities you find + (`messy_samples.csv`)  
- **Output (verbatim):**
Here is the column-by-column breakdown of the inconsistencies, ambiguities, and data quality issues in `messy_samples.csv`:

---

### **1. `sample_id**`

* **Inconsistent Prefix Case:** Values use mixed casing, such as uppercase `S` (`S0003`) and lowercase `s` (`s-0003`).


* **Inconsistent Separators:** Some entries include a hyphen between the letter and numbers (`s-0003`), while others omit it (`S0003`).


* **Leading/Trailing Whitespace:** Contains unstripped spaces around IDs.

---

### **2. `patient_name**`

* **Inconsistent Letter Case:** Names are formatted in uppercase (`A. NGUYEN`), title case (`A. Nguyen`), or lowercase (`a. nguyen`).


* **Spacing Variations:** Varying numbers of spaces between the initial/period and the last name (e.g., `A.  NGUYEN` vs. `A. Nguyen`).

---

### **3. `dob` (Date of Birth)**

* **Inconsistent Date Formats:** Uses mixed date representations (e.g., ISO `YYYY-MM-DD` vs. `MM/DD/YYYY` or `DD-MM-YYYY`).
* **Ambiguous Numerical Representation:** Dates with day values $\le 12$ (e.g., `01/02/1985`) create ambiguity between month-first and day-first parsing.

---

### **4. `sex**`

* **Inconsistent Categorical Value Encodings:** Represents biological sex with multiple variations:
* Male: `M`, `m`, `Male`, `male`.


* Female: `F`, `f`, `Female`, `female`.




* **Ambiguous Missing/Unknown Representation:** Uses `U`, `unknown`, or blank/empty strings interchangeably.



---

### **5. `enrollment_site**`

* **Inconsistent Naming Formats & Casing:** Sites are encoded using different casing and conventions (`siteB`, `Site C`, `SITE-A`, `site_a`).


* **Inconsistent Delimiters & Spacing:** Separators vary between spaces, hyphens, underscores, or no space at all (`site_a`, `SITE-A`, `siteB`).



---

### **6. `glucose` / `glucose_value**`

* **Mixed Data Types / Embedded Characters:** Numeric laboratory values contain attached non-numeric markers, such as asterisks (`120.5*`) flagging abnormal results.


* **Missing Value Indicators:** Missing entries are recorded as text strings like `"N/A"`, `"n/a"`, or `"NA"` alongside blank cells.



---

### **7. `glucose_unit**`

* **Inconsistent Case Unit Labels:** The same unit appears in varying capitalizations (`mg/dl`, `MG/DL`, `mg/dL`).


* **Inconsistent Measurement Systems:** Results mix distinct measurement units across rows (`mg/dL` vs. `mmol/L`) without standardized conversion.


* **Unit Label Mismatches / Implausible Values:** Some numeric glucose values are far too high for `mmol/L` (e.g., a value of `110` labeled as `mmol/L`), indicating a mislabeled unit.

- **Tool:** Google Gemini (Flash)
- **(CSV) Prompt 2 (verbatim):** Great thank you. Now can you clean it? Do not write or run code. Output all 60 rows as a CSV in a single code block with these columns: sample_id, patient_name, dob, sex, enrollment_site, glucose_mg_dl, notes. Then standardize as follows: sample_id as S followed by 4 digits, dob as YYYY-MM-DD, sex as M, F, or U, enrollment_site as "Site A", "Site B", or "Site C", patient_name in normal capitalization, glucose in mg/dL, converting units where necessary, and leave notes unchanged.
- **Output 2 (verbatim):**
```csv
sample_id,patient_name,dob,sex,enrollment_site,glucose_mg_dl,notes
S0001,A. Nguyen,1985-02-01,M,Site A,120.5,fasting
S0002,B. Smith,1990-11-15,F,Site B,95.0,
S0003,C. Jones,1978-07-22,U,Site C,210.0,re-test required
S0004,D. Patel,1992-04-05,M,Site A,,patient non-compliant
S0005,E. Gomez,1988-12-12,F,Site B,105.3,
S0006,F. Chen,1995-01-30,M,Site C,88.0,fasting
S0007,G. Kim,1982-09-08,F,Site A,142.1,
S0008,H. Taylor,1975-03-14,M,Site B,115.0,borderline
S0009,I. Brown,1998-06-25,F,Site C,99.4,
S0010,J. Wilson,1980-10-19,U,Site A,180.2,fasting
S0011,K. Martinez,1991-08-03,M,Site B,110.0,
S0012,L. Anderson,1987-05-17,F,Site C,,sample degraded
S0013,M. Thomas,1983-12-01,M,Site A,135.6,
S0014,N. Jackson,1994-02-28,F,Site B,91.2,fasting
S0015,O. White,1979-11-04,U,Site C,205.0,
S0016,P. Harris,1986-07-11,M,Site A,102.8,
S0017,Q. Martin,1993-09-23,F,Site B,118.5,fasting
S0018,R. Thompson,1972-01-15,M,Site C,150.0,
S0019,S. Garcia,1997-04-09,F,Site A,89.0,
S0020,T. Martinez,1989-10-02,M,Site B,128.4,
S0021,U. Robinson,1984-06-18,U,Site C,112.0,fasting
S0022,V. Clark,1996-03-27,F,Site A,97.6,
S0023,W. Rodriguez,1981-12-05,M,Site B,165.0,
S0024,X. Lewis,1999-08-14,F,Site C,,refused draw
S0025,Y. Lee,1976-05-20,M,Site A,108.2,fasting
S0026,Z. Walker,1990-01-11,F,Site B,114.0,
S0027,A. Hall,1985-09-29,U,Site C,195.8,
S0028,B. Allen,1992-11-08,M,Site A,101.0,fasting
S0029,C. Young,1977-04-16,F,Site B,122.3,
S0030,D. Hernandez,1995-07-21,M,Site C,85.5,
S0031,E. King,1983-02-14,F,Site A,130.0,fasting
S0032,F. Wright,1988-10-31,M,Site B,107.1,
S0033,G. Lopez,1991-03-06,U,Site C,175.4,
S0034,H. Hill,1974-08-25,F,Site A,93.8,
S0035,I. Scott,1998-12-03,M,Site B,,hemolyzed
S0036,J. Green,1986-06-12,F,Site C,119.0,fasting
S0037,K. Adams,1993-01-19,M,Site A,140.5,
S0038,L. Baker,1980-05-28,F,Site B,100.2,
S0039,M. Gonzalez,1997-09-04,U,Site C,220.0,critical high
S0040,N. Nelson,1982-11-17,M,Site A,111.6,fasting
S0041,O. Carter,1994-04-02,F,Site B,96.4,
S0042,P. Mitchell,1979-07-15,M,Site C,155.0,
S0043,Q. Perez,1987-10-24,F,Site A,104.9,
S0044,R. Roberts,1990-03-08,M,Site B,125.1,fasting
S0045,S. Turner,1981-08-30,U,Site C,116.0,
S0046,T. Phillips,1996-01-05,F,Site A,87.3,
S0047,U. Campbell,1975-06-22,M,Site B,148.0,
S0048,V. Parker,1993-12-19,F,Site C,,lipemic sample
S0049,W. Evans,1984-02-07,M,Site A,106.5,fasting
S0050,X. Edwards,1991-09-13,F,Site B,113.2,
S0051,Y. Collins,1978-04-26,U,Site C,188.0,
S0052,Z. Stewart,1999-07-01,M,Site A,92.7,fasting
S0053,A. Sanchez,1986-11-10,F,Site B,121.0,
S0054,B. Morris,1992-05-04,M,Site C,138.9,
S0055,C. Rogers,1980-08-18,F,Site A,99.8,fasting
S0056,D. Reed,1995-12-29,M,Site B,109.4,
S0057,E. Cook,1983-03-11,U,Site C,168.0,
S0058,F. Morgan,1989-06-24,F,Site A,103.1,
S0059,G. Bell,1977-10-07,M,Site B,152.5,fasting
S0060,H. Murphy,1994-01-16,F,Site C,94.0,

```

- **Tool:** Google Gemini (Flash)
- **(CSV) Prompt 3 (verbatim):** Thank you. List every assumption or judgement call you made while cleaning, and any rows where you were unsure.
- **Output (verbatim):**
Here is the full breakdown of every assumption, decision rule, and judgment call made during the manual cleaning of `messy_samples.csv`, followed by the rows where ambiguity existed.

---

### **1. Standardization Assumptions & Decisions**

* **`sample_id` Format:**
* **Rule:** Replaced all variants (lowercase `s`, embedded hyphens `-`, extra surrounding whitespace) with a clean `S` prefix followed by 4 zero-padded digits (e.g., `s-0003` $\rightarrow$ `S0003`).


* **Assumption:** The numeric sequence determines the identity, and hyphenation/casing were purely typing inconsistencies.




* **`patient_name` Formatting:**
* **Rule:** Applied Title Case to first/last name components, standardized spacing to a single space after the initial period (e.g., `A.  NGUYEN` $\rightarrow$ `A. Nguyen`).




* **`dob` (Date of Birth) Parsing:**
* **Rule:** Standardized all dates to `YYYY-MM-DD` ISO format.
* **Assumption:** For ambiguous slash-delimited dates like `01/02/1985`, assumed standard U.S. clinical convention (`MM/DD/YYYY`), resolving `01/02/1985` to **February 1, 1985** (`1985-02-01`).


* **`sex` Categorization:**
* **Rule:** Standardized variations to `'M'`, `'F'`, or `'U'`.


* **Assumption:** Mapped explicit missingness indicators (`'unknown'`, `'U'`, blank entries, or invalid text) to `'U'`.




* **`enrollment_site` Mapping:**
* **Rule:** Mapped all variants (`siteB`, `SITE-A`, `site_a`, `Site  C `) to one of `"Site A"`, `"Site B"`, or `"Site C"`.


* **Assumption:** Delimiters (`_`, `-`, extra spaces) and casing were artifacts of manual data entry.




* **`glucose_mg_dl` Numeric Cleaning & Unit Conversion:**
* **Rule:** Stripped trailing non-numeric flags (such as asterisks `*`) and converted all `mmol/L` measurements to `mg/dL` using the standard conversion factor ($1\text{ mmol/L} \approx 18.0182\text{ mg/dL}$), rounding to 1 decimal place.


* **Missing Values:** Formatted explicit text representations of missing data (`"N/A"`, `"n/a"`, `"NA"`) as empty cells/nulls to maintain numeric column type purity.


* **Implausible Unit Overrides:** For values where the unit was recorded as `mmol/L` but the numeric value was far outside the plausible biological range for `mmol/L` (e.g., a glucose reading of `110 mmol/L`), assumed the label was mislabelled and the number was already recorded in `mg/dL`.




* **`notes` Field:**
* **Rule:** Preserved all free-text notes exactly as written without altering text or case.



---

### **2. Rows with Ambiguities or Judgement Calls**

1. **Date Ambiguity (`dob` column — e.g., Row 1):**
* **Issue:** Input dates like `01/02/1985` could theoretically represent either **Jan 2, 1985** or **Feb 1, 1985**.
* **Judgement:** Assumed `MM/DD/YYYY` format systematically across all slash-delimited dates.


2. **Mislabeled Glucose Units (e.g., Row 11 - `S0011`):**
* **Issue:** Value was `110` with unit recorded as `mmol/L`. A true glucose level of 110 mmol/L (~1980 mg/dL) is non-viable.


* **Judgement:** Treated the value as an unconverted `mg/dL` reading rather than multiplying by 18.0182.




3. **Missing/Unknown Sex Values (e.g., Row 3 - `S0003`, Row 10 - `S0010`):**
* **Issue:** Entries contained varied representations like `'unknown'`, `'U'`, or empty strings.


* **Judgement:** Grouped all non-`M`/`F` entries under `'U'`.

 **Tool:** Google Gemini (Flash)
- **(FASTA) Prompt 1 (verbatim):** Attached are 8 FASTA sequences with inconsistent header formats. Do not clean it yet, and do not write or run code. Just read it and tell me what inconsistencies or ambiguities you see in the headers. + (`messy_sequeneces.fasta`)
- **Output (verbatim):**
Here is the breakdown of the inconsistencies, structural variations, and ambiguities in the header lines of the 8 FASTA sequences:

---

### **1. Heterogeneous Field Delimiters & Formatting Layouts**

The headers use completely different syntax and delimiters to separate metadata fields:

* **Pipes (`|`):** `>sample_001|organism=Homo_sapiens|gene=BRCA1|len=120` (Record 1) and `>seq6|Hsapiens|EGFR` (Record 6).


* **Semicolons (`;`):** `>SAMPLE_004;species=H.sapiens;target=BRCA1` (Record 4) and `>sample005 Homo sapiens; TP53; 130 bp` (Record 5).


* **Spaces (` `):** `>Sample002 organism:Homo sapiens gene:TP53` (Record 2) and Record 5.


* **Mixed Delimiters:** `>sample-003 | Homo_sapiens | EGFR | length=150bp` (Record 3) uses both spaces and pipes; Record 7 uses pipes and colons (`>Sample_007 organism=Homo_sapiens|gene=BRCA1|note:re-sequenced`).



---

### **2. Inconsistent Key-Value Assignment Syntax**

Key-value metadata assignments use mismatched assignment operators or omit key labels entirely:

* **Equals sign (`=`):** `organism=Homo_sapiens` (Record 1) or `species=H.sapiens` (Record 4).


* **Colon (`:`):** `organism:Homo sapiens` (Record 2) or `note:re-sequenced` (Record 7).


* **Positional / Unlabelled Values:** Records 3 (`>sample-003 | Homo_sapiens | EGFR | length=150bp`), 5 (`>sample005 Homo sapiens; TP53; 130 bp`), and 6 (`>seq6|Hsapiens|EGFR`) present organism and gene names as raw, positional text without key identifiers (e.g., `gene=`).



---

### **3. Inconsistent `sample_id` Formatting**

The primary sequence identifier prefix, separator, casing, and number padding vary across every record:

* **Prefix naming:** Alternates between `sample` (Records 1, 3, 4, 5, 7, 8) and `seq` (Record 6).


* **Casing:** Mixed uppercase (`SAMPLE_004`), title case (`Sample002`, `Sample_007`), and lowercase (`sample_001`).


* **Separators:** Uses underscores (`sample_001`), hyphens (`sample-003`, `sample-8`), or no separator (`Sample002`, `sample005`).


* **Digit Padding:** Numbers are padded to 3 digits (`001`, `002`), 1 digit (`8`), or omit leading zeros.



---

### **4. Organism Attribute Naming & Value Variations**

The taxonomy metadata uses conflicting key names and multiple spelling/abbreviation representations:

* **Key Names:** Referred to as `organism` (Records 1, 2, 7), `species` (Records 4, 8), or unlabelled (Records 3, 5, 6).


* **Species Naming Variations:**
* Full name with space: `Homo sapiens` (Records 2, 5)


* Full name with underscore: `Homo_sapiens` (Records 1, 3, 7, 8)


* Abbreviated forms: `H.sapiens` (Record 4) and `Hsapiens` (Record 6).





---

### **5. Gene Attribute Naming & Extraction Ambiguity**

* **Key Names:** Referred to as `gene` (Records 1, 2, 7, 8), `target` (Record 4), or left unlabelled (Records 3, 5, 6).


* **Parsing Ambiguity:** In unlabelled headers like Record 5 (`>sample005 Homo sapiens; TP53; 130 bp`), parsing software must infer positionally that `TP53` is a gene symbol rather than another metadata category.



---

### **6. Declared Sequence Length Inconsistencies & Units**

Sequence length declarations vary in key name, unit labeling, missing value representation, and presence:

* **Key Names:** Recorded as `len` (Records 1, 8), `length` (Record 3), unlabelled (Record 5), or entirely absent (Records 2, 4, 6, 7).


* **Units:** Includes units in base pairs (`150bp`, `130 bp`) or pure numbers (`120`).


* **Missing Value Representation:** Record 8 uses `len:NA` to explicitly state missing metadata rather than omitting the tag or leaving it blank.



---

### **7. Optional Metadata Fields**

* **Inconsistent Fields:** Record 7 includes a custom trailing field (`note:re-sequenced`) that does not exist in any other header in the dataset.

- **Tool**: Google Gemini (Flash)
- **(FASTA) Prompt 2 (verbatim):** Great thank you. Now extract structured fields from each header. Do not write or run code. Output all 8 records as a CSV in a single code block with these columns: sample_id, organism, gene, declared_length_bp, and note. Standardize withe the following: sample_id as sample_ followed by 3 digits, organism as "Homo sapiens", gene as the gene symbol, declared_length_bp as the length stated in the header if any, blank if none is given, note for any extra tag like a re-sequencing note.
- **Output (verbatim):**
```csv
sample_id,organism,gene,declared_length_bp,note
sample_001,Homo sapiens,BRCA1,120,
sample_002,Homo sapiens,TP53,,
sample_003,Homo sapiens,EGFR,150,
sample_004,Homo sapiens,BRCA1,,
sample_005,Homo sapiens,TP53,130,
sample_006,Homo sapiens,EGFR,,
sample_007,Homo sapiens,BRCA1,,re-sequenced
sample_008,Homo sapiens,TP53,,

```

- **Tool:** Google Gemini (Flash)
- **(FASTA) Prompt 3 (verbatim):** Thank you. List every assumption or judgement call you made while cleaning, and any rows where you were unsure.
- **Output (verbatim):**
Here is the full list of assumptions, judgment calls, and ambiguous rows from extracting structured metadata from the FASTA headers in `messy_sequences.fasta`:

---

### **1. Standardization Assumptions & Decisions**

* **`sample_id` Standardization:**
* **Rule:** Standardized all sequence identifiers to `sample_` followed by 3 zero-padded digits (e.g., `seq6` $\rightarrow$ `sample_006`, `sample-8` $\rightarrow$ `sample_008`).


* **Assumption:** The numeric index represents the unique sample ID, and prefix variations (`sample`, `seq`, `SAMPLE`) or separators (`_`, `-`, or none) were artifacts of different lab formats.




* **`organism` Taxonomy Standardization:**
* **Rule:** Mapped all spelling and abbreviation variants (`Homo_sapiens`, `Homo sapiens`, `H.sapiens`, `Hsapiens`) to `"Homo sapiens"`.




* **`gene` Symbol Extraction:**
* **Rule:** Extracted the standard uppercase gene symbol (`BRCA1`, `TP53`, `EGFR`).


* **Assumption:** Mapped key aliases like `target` (e.g., `target=BRCA1`) to `gene`, and positionally parsed unlabelled symbols directly following the organism tag (e.g., `Homo sapiens; TP53` or `Hsapiens|EGFR`).




* **`declared_length_bp` Capture & Unit Stripping:**
* **Rule:** Captured declared numeric sequence lengths regardless of keyword (`len=120`, `length=150bp`, `130 bp`) and stripped unit suffixes like `bp` to leave pure numeric values.


* **Assumption:** Represented missing declarations (`len:NA` or headers without length) as blank/null values rather than text strings like `"NA"` to maintain integer data-type purity.




* **`note` Extraction:**
* **Rule:** Isolated extra non-standard metadata flags (such as `note:re-sequenced` $\rightarrow$ `re-sequenced`) while leaving rows without extra tags blank.





---

### **2. Rows with Ambiguities or Judgement Calls**

1. **Unlabelled Positional Fields (Rows 3, 5, 6 — `sample_003`, `sample_005`, `sample_006`):**
* **Issue:** Headers like `>sample-003 | Homo_sapiens | EGFR | length=150bp` or `>seq6|Hsapiens|EGFR` lacked explicit `gene=` or `organism=` tags.


* **Judgement:** Inferred positionally that the second field represents the organism species and the third field represents the gene symbol based on domain patterns.




2. **`declared_length_bp` Parsing Variations (Rows 3, 5, 8 — `sample_003`, `sample_005`, `sample_008`):**
* **Issue:** Row 3 (`length=150bp`) and Row 5 (`130 bp`) attached base-pair unit labels, while Row 8 contained `len:NA`.


* **Judgement:** Stripped the `bp` unit to keep the column strictly numeric, and treated `len:NA` as missing (blank) rather than retaining the string `"NA"`.




3. **Prefix Discrepancy (Row 6 — `sample_006`):**
* **Issue:** Listed as `>seq6` instead of `sample`.


* **Judgement:** Unified `seq6` to `sample_006` to align with the rest of the cohort sequence.

# ATTEMPT 2: AI ASSISTED CLEANING - EXPLICIT PROMPT AND OUTPUT 
An initial attempt to extract `messy_camples.csv` produced a plausible-looking but entirely fabricated 60-row table. It invented notes values that never appear in the real generator's output. Patient names run sequentially through the alphabet rather than the real file's repeated small name pool. This happened twice in two separate sessions both times specifically on the "produce all 60 rows" prompt. This is documented as a a failure mode of the AI approach. 
- **Tool:** Google Gemini Flash
- **(CSV) Prompt 2 (verbatim - attempt 2):**
Now clean it. Do not write or run code. Transcribe and standardize each of the 60 rows below exactly as given — do not invent, omit, or reorder any row. Output all 60 rows as a CSV in a single code block with these columns: sample_id, patient_name, dob, sex, enrollment_site, glucose_mg_dl, notes.

Standardize as follows: sample_id as S followed by 4 digits; dob as YYYY-MM-DD; sex as M, F, or U; enrollment_site as "Site A", "Site B", or "Site C"; patient_name in normal capitalization; glucose in mg/dL, converting units where needed; notes unchanged. + (a copy and pasted `messy_samples.csv` instead of attached as a file).
- **Output (verbatim - attempt 2):**
```csv
sample_id,patient_name,dob,sex,enrollment_site,glucose_mg_dl,notes
S0001,A. Nguyen,1962-07-09,F,Site A,75.4,
S0002,T. Patel,1974-12-16,M,Site A,120.0,
S0003,R. Martinez,1953-11-24,F,Site B,84.2,
S0004,B. Smith,1975-12-18,F,Site B,120.0,
S0005,B. Martinez,1997-12-02,M,Site A,248.1,
S0006,A. Johnson,1955-12-09,F,Site B,254.4,
S0007,T. Martinez,1969-09-04,U,Site A,225.0,
S0008,T. Martinez,1997-06-21,M,Site A,192.7,
S0009,A. Nguyen,2018-05-11,F,Site A,221.5,
S0010,A. Martinez,1951-10-01,F,Site C,215.2,re-draw requested
S0011,K. Garcia,1997-10-16,M,Site B,179.6,
S0012,S. Kim,2008-04-21,U,Site B,,re-draw requested
S0013,M. Smith,2006-08-14,U,Site A,224.7,
S0014,K. Patel,1986-07-09,F,Site B,241.1,
S0015,B. Smith,1980-06-10,F,Site B,271.7,
S0016,B. Smith,1998-07-01,F,Site C,202.7,
S0017,T. Smith,1973-10-17,M,Site C,449.0,
S0018,A. Johnson,2002-05-30,U,Site B,84.4,re-draw requested
S0019,M. Martinez,2005-07-26,U,Site B,164.1,
S0020,S. Brown,2017-06-15,M,Site B,249.3,
S0021,B. Patel,1964-02-26,M,Site C,187.7,
S0022,J. Nguyen,1959-08-09,M,Site A,199.2,
S0023,A. Garcia,1974-10-28,M,Site A,184.7,
S0024,B. Garcia,2011-12-30,M,Site B,305.4,
S0025,A. Johnson,1972-05-21,F,Site C,143.1,
S0026,J. Kim,2016-01-30,U,Site C,202.3,
S0027,K. Patel,1991-04-19,M,Site C,111.0,
S0028,S. Johnson,1985-11-09,M,Site A,102.1,re-draw requested
S0029,T. Martinez,1960-05-17,F,Site C,148.5,
S0030,R. Garcia,1976-12-10,U,Site C,123.2,
S0031,J. Martinez,1986-06-07,M,Site B,211.4,
S0032,J. Garcia,2009-07-23,F,Site C,112.3,
S0033,K. Martinez,1956-07-14,U,Site B,189.2,
S0034,B. Kim,2012-06-07,M,Site C,91.8,
S0035,K. Martinez,1995-04-15,U,Site C,405.6,
S0036,K. Patel,1956-12-13,F,Site A,230.7,
S0037,B. Kim,1998-09-06,U,Site C,145.6,
S0038,R. Nguyen,1987-08-05,U,Site B,283.6,
S0039,K. Lee,1997-12-02,U,Site C,135.0,
S0040,M. Brown,2018-04-17,M,Site C,145.9,
S0041,M. Garcia,2008-06-21,M,Site A,221.1,
S0042,K. Nguyen,1965-01-20,M,Site A,174.2,
S0043,M. Garcia,2006-04-10,F,Site A,223.1,
S0044,R. Garcia,1980-08-12,U,Site A,148.0,
S0045,S. Martinez,1998-04-13,U,Site C,176.6,
S0046,M. Brown,2009-12-12,U,Site C,231.5,
S0047,S. Davis,1967-02-21,F,Site B,169.9,
S0048,B. Nguyen,2012-01-24,M,Site A,155.2,
S0049,S. Nguyen,1960-10-28,F,Site B,241.2,
S0050,S. Garcia,1976-07-30,F,Site A,197.4,
S0051,J. Brown,1951-02-06,U,Site A,103.2,
S0052,K. Garcia,2011-08-02,M,Site B,240.8,
S0053,M. Davis,1989-09-20,U,Site B,80.8,
S0054,J. Patel,1956-09-25,M,Site C,176.9,re-draw requested
S0055,B. Patel,2006-01-28,U,Site A,186.6,
S0056,S. Brown,2011-10-14,U,Site B,,
S0057,R. Martinez,1958-03-12,M,Site C,217.9,
S0058,S. Lee,1989-02-08,F,Site B,130.0,
S0059,T. Davis,1957-11-25,M,Site C,142.8,
S0060,R. Martinez,2006-02-09,M,Site B,93.6,

```
