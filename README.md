# Lab 3: Parsing Messy Health Data

## Setup

Environment (Python 3.12, conda/mamba):
```bash
mamba env create -f environment.yml
conda activate lab-3-hds
```

## Data
`data/raw/lab3-messy-data/` - synthetic course data. See `SOURCE.md` for provenance.

## Run

Profile the raw files (optional, for inspection):

```bash
python src/explore_samples.py
python src/explore_sequences.py
```

Regex-based cleaning:

```bash
python src/clean_samples_regex.py    # -> data/processed/samples_clean_regex.csv
python src/clean_sequencesregex.py   # -> data/processed/sequences_clean_regex.csv
```

Build the samples x features x metadata table (graduate addendum):

```bash
python src/build_analytic_table.py   # -> data/processed/samples_analytic.csv
```

AI-assisted cleaning: prompts and raw model output are in `AI_USAGE.md`; outputs are `data/processed/samples_clean_ai.csv` and `data/processed/sequences_clean_ai.csv`.

Comparison and failure-mode analysis: `docs/COMPARISON.md`

## Project structure

```
lab-3-hds/
├── README.md
├── AI_USAGE.md
├── environment.yml
├── .gitignore
├── src/
│   ├── explore_samples.py
│   ├── explore_sequences.py
│   ├── clean_samples_regex.py
│   ├── clean_sequences_regex.py
│   └── build_analytic_table.py
├── data/
│   ├── raw/lab3-messy-data/
|       ├── SOURCE.md
|       ├── generate_data.py
|       ├── messy_samples.csv
|       ├── messy_sequences.fasta
│   └── processed/
|       ├── samples_analytic.csv
|       ├── samples_clean_regex.csv
|       ├── sequences_clean_regex.csv
└── docs/
    └── COMPARISON.md
```
