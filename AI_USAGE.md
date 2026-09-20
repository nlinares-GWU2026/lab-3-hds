# AI Usage Log
## Entry 1: Discovering Use of .py script for CSV generation
**Model:** Gemini (Flash)
**What I was doing:** I was exploring the data folder on the applied-computing-HDS GitHub. I found that there was a `messy_sequences.fasta` but no `messy_samples.csv` so I wanted to know if I could generate my own to work on the lab with the provided script. It seemed like I would be able to. 
**What I asked first:** What does this code do? (pasted `generate_data.py`).
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
**What I asked first:** How can I run this script given my current set up (gave my file path: C:\Users\nelin\Desktop\GWU Information\GWU Fall 2026\Applied_Computing\lab-3-hds\data\raw\lab3-messy-data) and check the existing FASTA (professor's) against the new one?
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
