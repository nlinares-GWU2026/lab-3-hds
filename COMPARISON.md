# Lab 3 Comparison: Regex vs. AI-Assisted Cleaning

## 1. What I did
- **Data:** `messy_samples.csv` (60 records) and `messy_sequences.fasta` (8 records). See `data/raw/lab3-messy-data/SOURCE.md`.
- **Regex approach:** `src/clean_samples_regex.py` -> `data/processed/samples_clean_regex.csv` <and the FASTA equivalent>.
- **AI approach:** Google Gemini Flash, prompts in `AI_USAGE.md` -> `data/processed/samples_clean_ai.csv` <and the FASTA equivalent>.
- **Effort:** regex took about 6 hours including debugging; the AI round took about <time, including checking>.

## 2. Assumptions in the regex version
- Slash and dot dates are month-first, inferred from rows where the first number exceeds 12. Rows with both numbers <= 12 (for example `10/01/1951`) are inherently ambiguous.
- Two-digit years: 00-26 -> 2000s, 27-99 -> 1900s. Safe here because birth dates run 1951-2018, but not justified in general.
- Sex: `M`/`F`; blank, `U` and `unknown` all become `U`. This loses the difference between "not recorded" and "unknown". I judged that acceptable here.
- Glucose `*`: value kept, row flagged `asterisk`. The meaning of `*` isn't documented.
- `mmol/L` labels: values above 60 can't be mmol/L, so they're kept as-is, treated as mg/dL, and flagged `unit_label_implausible`. The conversion (x 18.016) exists but never triggers on this data.

## 3. Where they agreed and disagreed
<Table: per column, how many rows agree/disagree. Then 2-3 sentences on the pattern.>

## 4. Which caught edge cases the other missed
<For each: who caught it, which record.>

## 5. Failure modes (at least 2 per file)
### <Record ID: short title>
- Raw: `<value>`
- Regex produced: `<value>`   AI produced: `<value>`
- Why it went wrong / is ambiguous: <explanation>

## 6. Which would I trust on a real dataset, and why?
<Your judgement, based on previous sections.>

## 7. Graduate addendum: samples x features x metadata
<Table layout, then add readiness notes using the four checks: types, missingness, leakage, units. For missing values, say what you would need to know and who you would ask.>
