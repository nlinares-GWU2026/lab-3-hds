 # Lab 3 Comparison: Regex vs. AI-Assisted Cleaning

## 1. What I did
- **Data:** `messy_samples.csv` (60 records) and `messy_sequences.fasta` (8 records). See `data/raw/lab3-messy-data/SOURCE.md`.
- **Regex approach:** `src/clean_samples_regex.py` -> `data/processed/samples_clean_regex.csv` and `src/clean_sequences_regex.py` ->`data/processed/sequences_clean_regex.csv`.
- **AI approach:** Google Gemini Flash, prompts in `AI_USAGE.md` -> `data/processed/samples_clean_ai.csv` and `data/processed/sequences_clean_ai.csv`.
- **Effort:** regex took about 8-9 hours, including debugging; the AI round took about 2-3 hours.

## 2. Assumptions Regex
### `messy_samples.csv`
- Slash and dot dates are month-first, inferred from rows where the first number exceeds 12. Rows with both numbers <= 12 (for example `10/01/1951`) are inherently ambiguous.
- Two-digit years: 00-26 -> 2000s, 27-99 -> 1900s. Safe here because birth dates run 1951-2018, but not justified in general.
- Sex: `M`/`F`; blank, `U` and `unknown` all become `U`. This loses the difference between "not recorded" and "unknown". I judged that acceptable here.
- Glucose `*`: value kept, row flagged `asterisk`. The meaning of `*` isn't documented.
- `mmol/L` labels: values above 60 can't be mmol/L, so they're kept as-is, treated as mg/dL, and flagged `unit_label_implausible`. The conversion (x 18.016) exists but never triggers on this data.
### `messy_sequences.fasta`
- FASTA sample IDs: `seq6` is treated as sample 6, assuming `seq` and `sample` share one numbering space.
- Organism: `H.sapiens` and `Hsapiens` are expanded to `Homo sapiens`, based on the other six records using that spelling.
- Gene: an unlabelled gene symbol is read from the field right after the organism name. This can work because it is true for every record in this file, but it would fail on a header where the gene came first.
- Declared length: captured from any of three header forms (`len=`, `length=...bp`, a plain `NNN bp`); `len:NA` and headers with no length become blank rather than the text "NA" to keep the column numeric. 

## 3. Where Regex vs. AI-assisted agreed and disagreed
```bash
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
| File | Column | Agreed | Disagreed |
|---|---|---|---|
| messy_samples.csv | patient_name | 60 | 0 |
| messy_samples.csv | dob | 60 | 0 |
| messy_samples.csv | sex | 60 | 0 |
| messy_samples.csv | enrollment_site | 60 | 0 |
| messy_samples.csv | notes | 60 | 0 |
| messy_samples.csv | glucose_mg_dl | 48 | 12 |
| messy_sequences.fasta | organism | 8 | 0 |
| messy_sequences.fasta | gene | 8 | 0 |
| messy_sequences.fasta | note | 8 | 0 |
| messy_sequences.fasta | declared_length_bp | 8 | 0 |

Agreement was complete on every text/categorical field in both files. Name casing, date reformatting, sex/site normalization, and FASTA header field extraction all matched exactly. The only disagreement is glucose values on the 12 rows regex flagged as `unit_label_implausible`. The AI attempted a unit conversion on every row regardless of plausibility, while the regex approach left those 12 as-is because the labelled unit could not be trusted. 

## 4. Which approach caught edge cases the other missed
- **Glucose unit plausibility (regex caught, AI missed):** The regex script checks whether an `mmol/L` labelled value is physiologically possible before converting it. The AI converted all 12 implausible rows anyway, and did so with a factor of 1.80182 instead of the correct 18.0182. See failure mode below.
- **Sequence length mismatch (regex caught, AI missed):** The regex script computes the actual sequence length from the bases themselves and compares it to the header's declared length, flagging `sample_003` and `sample_005` as `mismatch`. The AI's output only reports the declared length as given, with no way to tell if it might be wrong.
- **Column-level profiling (AI's strength):** Once prompted to describe patterns rather than transcribe all 60 rows, Gemini's summary of the file's real inconsistencies (date formats, sex codes, site variants, unit mismatches) was accurate and well-organized (second attempt). Its failure mode was specifically in bulk row-by-row transcription, not pattern recognition. 

## 5. Failure modes (at least 2 per file)
### S0011: glucose unit conversion, wrong factor
- Raw: `99.7` labelled `mmol/L`
- Regex produced: `99.7` (flagged `unit_label_implausible`, left unconverted)
- AI produced: `179.6`
- Why it went wrong / is ambiguous: A real value of 99.7 mmol/L is not physiologically possible, so the regex script's plausibility check treats it as already being in mg/dL. The AI instead converted it but used 1.80182 rather than the correct 18.0182 - this is a slip by a factor of 10. Verified: 99.7 x 1.80182 = 179.6, matching the AI's output exactly. The same factor reproduces all 12 affected rows.

 ### S0010: ambiguous date order
 - Raw: `10/01/1951`
 - Regex produced: `1951-10-01 ` (Oct 1)
 - AI produced: `1951-10-01`
 - Why: Both day and month values are <=12, so the raw string is genuinely ambiguous between Oct 1 and Jan 10. Both approaches resolved it the same way assuming month-first order, but neither can confirm this against the data itself. It is an assumption, not verified.

### sample_003: declared vs. actual sequence length
- Raw header: `...| length=150bp`; actual sequence: 157 bases
- Regex produced: `declared_length_bp=150`, `actual_length_bp=157`,
  `length_flag=mismatch`
- AI produced: `declared_length_bp=150` (no flag, no actual-length check)
- Why: The header's stated length does not match the real sequence. The regex script catches this because it independently measures the sequence. The AI's output has no way to reveal the discrepancy since it was not asked to count bases. 

### sample_005: declared vs. actual sequence length (same issue as sample_003)
- Raw header: `...; 130 bp`; actual sequence: 144 bases
- Regex produced: `declared_length_bp=130`, `actual_length_bp=144`,
  `length_flag=mismatch`
- AI produced: `declared_length_bp=130` (no flag) 
- Why: same as sample_003 — a second instance of the header's declared
  length disagreeing with the true sequence.

## 6. Which would I trust on a real dataset, and why?
Based on both approaches, if I had to pick one to trust, it would be the regex approach. Despite the amount of time that went into developing it, I would rather spend more time developing an approach than have a quicker approach produce inaccurate results (Gemini glucose conversion). This comes with the caveat of inheriting my own biases and assumptions, but I can follow the logic path and accurately predict return values. It would take longer to adjust the regexes used if it was decided to change an assumption or include/exclude other factors, but I still think for reliability that the regex approach is more trustworthy. Ideally, a combined approach would be my top pick because, with AI, you can cut the production time in half, open an opportunity to improve the regex method you did not see before as well as check the biases/assumptions you have.

## 7. Graduate addendum: samples x features x metadata
| Group | Columns |
|---|---|
| Identifier | `sample_id` |
| Feature | `glucose_mg_dl` |
| Metadata | `sex`, `enrollment_site`, `age_years`, `notes`, `glucose_flag`, `glucose_unit_original` |
 ```bash
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

**Analytic readiness:** 
- **Types:** consistent - `glucose_mg_dl` and `age_years` are numeric, categorical fields (`sex`, `enrollment_site`) use a small fixed set of values.
- **Missingness:** documented, not dropped - the 2 missing glucose values come from raw `N/A` entries and remain blank rather than imputed. I would want to know whether `N/A` meant "not measured" or "result lost", and would ask whoever did the measurements.
- **Metadata/feature separation:** `glucose_flag` and `glucose_unit_original` are kept as metadata annotations about the measurement, not mixed into the feature itself so a model would not train on them by accident.
- **Units:** resolved to a single unit/system (mg/dL), but for the 12 `unit_label_implausible` rows this rests on my assumption (that the label was wrong, not the value) that I could not verify from the data alone. I would ask whoever did the measurements.
- **Not yet resolved:** the `sex` column collapses "blank" and "unknown" into one `U` code, so the distinction between "not recorded" and "recorded as unknown" is lost before this table is built. 
