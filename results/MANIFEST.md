# File manifest

This maps each figure in the manuscript to the files behind it: the file the LaTeX source includes, the figure produced by the analysis workflow, the source data underlying it, and the script that generates both. Paths are relative to the repository root. Figure numbers follow the compiled manuscript (`paper/current/main.tex`, `paper/current/supp.tex`).

## Source Data file (journal submission)

`paper/current/source_data/Source Data.xlsx` holds the source data for every figure in the manuscript, one sheet per figure. The sheets are named "Figure 1" to "Figure 4" and "Supplementary Figure 1" to "Supplementary Figure 10". A further sheet, "Bayes factors (all tests)", holds every Bayes factor reported in the manuscript (`results/figs/tables/bayes_factors_all.csv`, computed by the `bayes_factors` rule, `workflow/scripts/statistics/compute_bayes_factors.R`). Sheets "Supplementary Table 1" (per-letter manual annotations, `results/figs/tables/supp_table1_annotations.csv`) and "Supplementary Table 20" (the table's reported values only, `results/figs/tables/supp_table20_letters_replies.csv`; its generating code has not been located) cover two tables that no workflow script produces. Another, "Supplementary Table 24", holds the Bayes factors (`results/figs/tables/bayes_factors.csv`, computed with the code in `notebooks/statistical-power-analysis.rmd`). A sheet "Test statistics (all tests)" holds the full frequentist statistics for every test (statistic, degrees of freedom or sample sizes, p-value, effect size and 95% CI; `results/figs/tables/test_statistics_all.csv`, computed by the `test_statistics` rule, `workflow/scripts/statistics/compute_test_statistics.R`). Each sheet gives the figure's title, a short description, and a glossary of columns, followed by the data. The data are identical to the workflow's source data files listed below; missing values are empty cells.

It is built by the `source_data` rule (`workflow/scripts/submission/build_source_data.py`). All submission files (statistics, SI table bodies in `paper/current/tables/`, main-figure PDFs, Source Data) are rebuilt from the `workflow/` directory with `make submission`, after `make results` and `make results_supplement`; the data export is built with `make export`.

## Main-text figures

The submission files are the indexed PDFs and source data files in `paper/current/`. Each PDF was rendered from the same plotting script and data as the workflow's PNG; the source data files are identical copies of the workflow's plotdata.

| Figure | Label | Submission figure | Submission source data | Workflow figure | Workflow source data | Script |
|---|---|---|---|---|---|---|
| Fig. 1 | `fig:paper-features` | `paper/current/figures/fig1.pdf` | `paper/current/source_data/fig1_source_data.csv` | `results/figs/paper_metrics_density.png` | `results/figs/plotdata/paper_metrics_density_plotdata.csv` | `workflow/scripts/plotting/plot_paper_metrics_density.R` |
| Fig. 2 | `fig:matched-results-impact` | `paper/current/figures/fig2.pdf` | `paper/current/source_data/fig2_source_data.csv` | `results/figs/matched_comparison_plot.png` | `results/figs/plotdata/matched_comparison_plot_plotdata.csv` | `workflow/scripts/plotting/plot_matched_comparison.R` |
| Fig. 3 | `fig:visibility` | `paper/current/figures/fig3.pdf` | `paper/current/source_data/fig3_source_data.csv` | `results/figs/impact_temporal_comparison.png` | `results/figs/plotdata/impact_temporal_comparison_plotdata.csv` | `workflow/scripts/plotting/plot_impact_temporal_comparison.R` |
| Fig. 4 | `fig:embedding` | `paper/current/figures/fig4.pdf` | `paper/current/source_data/fig4_source_data.csv` | `results/figs/embedding_cocite_density_plot.png` | `results/figs/plotdata/embedding_cocite_density_plot_plotdata.csv` | `workflow/scripts/plotting/plot_embedding_cocite_density.R` |

**Source data columns:**
- **Fig. 1:** `venue`; `type` (`letter` = paper targeted by a critical letter, filled densities; `article` = matched non-targeted paper, dashed densities); `id` (MAG paper ID); `rank` (percentile rank, 0–1); `metric` (Impact, Ref. Diversity, Cite. Diversity, Novelty). The KS statistics printed in the panels are in Supplementary Tables `si:table:paper-features-1sKS` and `si:table:paper-features-2sKS`.
- **Fig. 2:** `venue`; `panel` (A–E); `mean_diff` (mean ΔTreatment − ΔControl over matched pairs); `lower`, `upper` (95% confidence interval); `t.p.value` (paired t-test); `signif` (asterisks shown in the figure).
- **Fig. 3:** `venue`; `delta_year` (years since the critical letter); `mu` (panel A: mean citations per year; panel B: mean proportion of citing papers that co-cite the letter); `n` (targeted papers with at least one citation that year); `se` (standard error of the mean); `lower`, `upper` (95% confidence interval, mean ± 1.96 SE, drawn as error bars); `metric` (panel).
- **Fig. 4:** `venue`; `cited_id` (targeted paper); `citing_id` (paper citing both the target and the letter); `cosine_similarity` (title-embedding similarity); `rank` (percentile rank of similarity among all papers citing the target).

## Supplementary figures

These are included in the manuscript under their workflow file names.

| Figure | Label | Manuscript file | Workflow figure | Workflow source data | Script |
|---|---|---|---|---|---|
| Fig. S1 | `si:fig:impact-likelihood-scatter` | `paper/current/figures/impact_likelihood_scatter.png` | `results/figs/impact_likelihood_scatter.png` | `results/figs/plotdata/impact_likelihood_scatter_plotdata.csv` | `workflow/scripts/plotting/plot_impact_likelihood_scatter.R` |
| Fig. S2 | `si:fig:margins_first-auhor` | `paper/current/figures/paper_firstauthor_demographic_ame.png` | `results/figs/paper_firstauthor_demographic_ame.png` | `results/figs/plotdata/paper_firstauthor_demographic_ame_plotdata.csv` | `workflow/scripts/plotting/plot_paper_author_demographics_ame.R` |
| Fig. S3 | `si:fig:margins_last-auhor` | `paper/current/figures/paper_lastauthor_demographic_ame.png` | `results/figs/paper_lastauthor_demographic_ame.png` | `results/figs/plotdata/paper_lastauthor_demographic_ame_plotdata.csv` | `workflow/scripts/plotting/plot_paper_author_demographics_ame.R` |
| Fig. S4 | `si:fig:field-representation` | `paper/current/figures/field_representation_plot.png` | `results/figs/field_representation_plot.png` | `results/figs/plotdata/field_representation_plot_plotdata.csv` | `workflow/scripts/plotting/plot_field_representation.R` |
| Fig. S5 | `si:fig:media_engagement_proportion` | `paper/current/figures/paper_news_tweet_proportion.png` | `results/figs/paper_news_tweet_proportion.png` | `results/figs/plotdata/paper_news_tweet_proportion_plotdata.csv` | `workflow/scripts/plotting/plot_paper_news_tweet_proportion.R` |
| Fig. S6 | `si:fig:tweet_distribution` | `paper/current/figures/paper_tweet_distribution.png` | `results/figs/paper_tweet_distribution.png` | `results/figs/plotdata/paper_tweet_distribution_plotdata.csv` | `workflow/scripts/plotting/plot_paper_tweet_distribution.R` |
| Fig. S7 | `si:fig:diagnostics` | `paper/current/figures/matching_diagnostic_impact_plot.png` | `results/figs/diagnostics/matching_diagnostic_impact_plot.png` | `results/figs/plotdata/diagnostics/matching_diagnostic_impact_plot_plotdata.csv` | `workflow/scripts/plotting/plot_match_diagnostic_impact.R` |
| Fig. S8 | `si:fig:consequence_time-lag` | `paper/current/figures/matched_comparison_lagtype_plot.png` | `results/figs/matched_comparison_lagtype_plot.png` | `results/figs/plotdata/matched_comparison_lagtype_plot_plotdata.csv` | `workflow/scripts/plotting/plot_paper_comparison_lag.R` |
| Fig. S9 | `si:fig:statistical-power` | `paper/current/figures/statsitical-power-analysis.png` | — (not produced by the workflow) | `results/figs/plotdata/statistical_power_analysis_plotdata.csv` | `notebooks/statistical-power-analysis.rmd` |
| Fig. S10 | `si:fig:letter_altmetrics` | `paper/current/figures/letter_altmetric_comparison.png` | `results/figs/letter_altmetric_comparison.png` | `results/figs/plotdata/letter_altmetric_comparison_plotdata.csv` | `workflow/scripts/plotting/plot_letter_altmetric_comparison.R` |

## Notes
- **Fig. S9** is produced by a notebook outside the workflow. Its source data were recomputed by running the notebook's code up to the plotted values; they match the figure. The notebook already uses the current matches (±5% / ±1 year for papers, ±15% / ±15% for authors).
- **How the main-text PDFs were made:** by the `main_figure_pdfs` rule (`workflow/scripts/submission/render_main_figure_pdfs.R`). It reruns each plotting script on the current workflow data and writes the output as PDF. Text is drawn as vector outlines with the `showtext` package, because the Cairo PDF device is unavailable, and the theme's Helvetica is substituted with the metrically equivalent Arial. The four plotting scripts now set all figure text in plain weight, as the journal requires for display items, and Fig. 1 prints p-values below 0.001 as p < 0.001 (it previously rounded 0.00067 and 0.00094 up to 0.001). Figs. 2 and 3 also draw each point with a thin black outline, and Fig. 3 now shows 95% confidence intervals as error bars. The workflow PNGs for Figs. 2 and 3 were regenerated with these changes; those for Figs. 1 and 4 were not, and still show bold text. Otherwise the figures are identical.
- **Per-figure CSVs:** `paper/current/source_data/fig1_source_data.csv` to `fig4_source_data.csv` are superseded by `Source Data.xlsx` for submission, but kept for convenience.
- **Superseded files:** the PNG versions of the main-text figures remain in `paper/current/figures/` but are no longer referenced by `main.tex`.
- **Unused files:** `paper/current/figures/` also holds figures the manuscript does not include (`impact_rank_histogram.png`, `pairwise_*.png`, `ratio_original_letter_citations.png`, `visibility.png`, `SITeamSize.pdf`, and the `old/` folder).
