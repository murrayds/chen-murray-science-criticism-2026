"""Write the source data for Supplementary Tables 1 and 20.

Run by the `supp_table_sources` rule (rules/Submission.smk).

  - Supplementary Table 1 summarizes the manual annotation of critical
    letters; its source data are the per-letter annotations (journal, DOI,
    validity, new evidence), without the annotator's free-text notes.
  - Supplementary Table 20 compares the visibility of critical letters and
    their replies. The code that produced it has not been located, so its
    source data are the values reported in the table, transcribed here.

Usage, run from the `workflow/` directory (normally via Snakemake):
    python scripts/submission/supp_table_sources.py ANNOTATIONS_XLSX TABLE1_CSV TABLE20_CSV
"""
import sys

import pandas as pd

annotations, table3, table14 = sys.argv[1:4]

d = pd.read_excel(annotations)[["journal", "doi", "is_valid", "new_evidence"]]
d.sort_values(["journal", "doi"]).to_csv(table3, index=False)

# Values reported in Supplementary Table 20
pd.DataFrame({
    "venue": ["Nature", "PNAS", "PRL", "Other APS"],
    "n": [126, 229, 188, 158],
    "letter_3yr_citations": [25.97, 9.46, 7.10, 6.72],
    "reply_3yr_citations": [4.37, 2.88, 3.52, 3.35],
    "letter_tweets": [5.52, 1.83, 0.01, 0.04],
    "reply_tweets": [2.64, 0.59, 0.02, 0.03],
}).to_csv(table14, index=False)
print(f"Wrote {table3} and {table14}")
