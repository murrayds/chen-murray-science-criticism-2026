Workflow scripts that process data, run simulations, and draw figures.

Recommended workflow tool: [`snakemake`](https://snakemake.readthedocs.io/en/stable/). 

## Running the workflow

Run from this directory, in order (see `Makefile`):

1. `make download`, `make novelty`, `make match`, `make results`: data, matching, and figures for the main journals (`config.yaml`).
2. `make download_supplement`, `make match_supplement`, `make results_supplement`: the same for the supplementary journals (`config_supplement.yaml`).
3. `make submission`: full test statistics and Bayes factors (`scripts/statistics/`), the Supplementary Information table bodies (`paper/current/tables/`), the main-figure PDFs, and the Source Data file (`scripts/submission/`). These rules (`rules/Submission.smk`) combine the main and supplementary results.
4. `make export`: the public data archive (`science_criticism_data.zip`, next to `data/`) and its manifest (`data/MANIFEST.md`).

The matched samples in `data/derived/matched/` were generated before a random seed was added to `scripts/matching/match_papers_for_impact_comparison.R` (used to pick one field for papers with several fields). Re-running that rule will therefore produce slightly different matches from those reported; use the deposited matched files to reproduce the published results exactly.

Two Source Data inputs come from `notebooks/statistical-power-analysis.rmd`, which is run separately: `results/figs/plotdata/statistical_power_analysis_plotdata.csv` (Supplementary Fig. 9) and `results/figs/tables/bayes_factors.csv` (Supplementary Table 24).
