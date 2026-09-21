Synthetic data for Lab 3 (course repo: gwcbi/applied-computing-HDS).
- **Origin:** synthetic data from the course repo (`gwcbi/applied-computing-HDS`, Lab 3 data folder). Not real patient or sequence data. See the course's own `SOURCE.md` there for license and PHI/PII notes.
- **`messy_seqeunces.fasta`:** downloaded from the course repo
- **`messy_samples.csv`:** regenerated 2026-09-20 with generate_data.py. Downloaded from the course repo. 
- **`generate_data.py`:** copy of the course's generator (seed 42 for CSV, seed 7 for the FASTA). Unchanged in the course repo as of 09/21/2026, checked with GitHub blame.
**Verification:** the regenerated `messy_seuqences.fasta` matched the course copy (`diff` printed nothing), using Python 3.12. 
- **To regenerate:** run `python generate_data.py` in an empty folder.
- **Not related:** the `generate_data.py` in the course's Week 5 folder builds a different gene-expression teaching dataset and is not used here. 
