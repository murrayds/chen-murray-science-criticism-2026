"""Assemble the journal's Source Data file from the workflow's plotdata.

Run by the `source_data` rule (rules/Submission.smk). It writes a single
Excel workbook with one sheet per manuscript figure (main text and
Supplementary Information). Each sheet opens with the figure label, its title,
a short description, and a glossary of columns, followed by the data exactly
as written by the workflow.

Usage, run from the `workflow/` directory:
    python scripts/submission/build_source_data.py [plotdata directory] [output file]
Defaults: `../results/figs/plotdata` and `../paper/current/source_data/Source Data.xlsx`.

Requires pandas and openpyxl.
"""

import os
import sys

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font

PLOTDATA = sys.argv[1] if len(sys.argv) > 1 else "../results/figs/plotdata"
OUTPUT = sys.argv[2] if len(sys.argv) > 2 else "../paper/current/source_data/Source Data.xlsx"

VENUE = ("venue", "Journal: Nature, Science, PNAS, PRL, or Other APS "
         "(Physical Review A-E combined).")

# (sheet name, figure title, description, plotdata file, column glossary)
SHEETS = [
    ("Figure 1",
     "Characterizing the population of papers targeted by critical letters",
     "Percentile ranks of papers targeted by critical letters and of matched "
     "non-targeted papers, by journal and metric. Ranks are computed within "
     "journal, period, and field. The figure shows kernel density estimates of "
     "these values; the Kolmogorov-Smirnov test results printed in each panel "
     "are reported in the Supplementary Tables.",
     "paper_metrics_density_plotdata.csv",
     [VENUE,
      ("type", "letter = paper targeted by a critical letter (filled "
               "densities); article = matched non-targeted paper (dashed "
               "densities, shown for diversity and novelty only)."),
      ("id", "Microsoft Academic Graph paper ID."),
      ("rank", "Percentile rank of the paper on the metric (0-1)."),
      ("metric", "Citations (panels A), Ref. Diversity (B), Cite. Diversity (C), "
                 "or Novelty (D).")]),
    ("Figure 2",
     "The consequences of criticism",
     "Difference in growth between papers or authors that received a critical "
     "letter (treatment) and their matched controls, averaged over matched "
     "pairs, with 95% confidence intervals and paired t-test p-values.",
     "matched_comparison_plot_plotdata.csv",
     [VENUE,
      ("mean_diff", "Mean of (growth of treatment - growth of control) over "
                    "matched pairs, where growth is the log of the ratio of "
                    "the metric after vs. before the critical letter."),
      ("upper", "Upper bound of the 95% confidence interval."),
      ("lower", "Lower bound of the 95% confidence interval."),
      ("t.p.value", "p-value of a paired t-test."),
      ("panel", "Figure panel (A) to (E)."),
      ("signif", "Significance marker shown in the figure (* p < 0.05, "
                 "** p < 0.01, *** p < 0.001); blank if not significant.")]),
    ("Figure 3",
     "Critical letters are rarely co-cited despite continued citation to "
     "criticized papers",
     "Annual citations received by papers targeted by a critical letter, and "
     "the proportion of those citations that also cite the letter, by years "
     "since the letter. Values are means across papers with 95% confidence "
     "intervals (mean +/- 1.96 standard errors). Self-citations and replies "
     "are excluded.",
     "impact_temporal_comparison_plotdata.csv",
     [VENUE,
      ("delta_year", "Years since receipt of the critical letter."),
      ("mu", "Panel (A): mean citations received that year; panel (B): mean "
             "proportion of citing papers that also cite the critical "
             "letter."),
      ("n", "Number of targeted papers with at least one citation that year."),
      ("se", "Standard error of the mean."),
      ("lower", "Lower bound of the 95% confidence interval (error bar)."),
      ("upper", "Upper bound of the 95% confidence interval (error bar)."),
      ("metric", "Figure panel.")]),
    ("Figure 4",
     "Papers similar to the criticized study co-cite the critical letter",
     "Each row is a paper that cites both a criticized paper and its critical "
     "letter, with the percentile rank of its title-embedding similarity to "
     "the criticized paper among all papers citing that paper. The figure "
     "shows kernel density estimates of the ranks.",
     "embedding_cocite_density_plot_plotdata.csv",
     [VENUE,
      ("cited_id", "Microsoft Academic Graph ID of the criticized paper."),
      ("citing_id", "Microsoft Academic Graph ID of the co-citing paper."),
      ("cosine_similarity", "Cosine similarity of SPECTER title embeddings."),
      ("rank", "Percentile rank (0-1) of the similarity among all papers "
               "citing the criticized paper; blank where the criticized "
               "paper has a single citing paper.")]),
    ("Supplementary Figure 1",
     "Receipt of critical letters is associated with impact",
     "Ratio r(k) between the share of targeted papers and the share of "
     "non-targeted papers falling in each logarithmic bin of 3-year citation "
     "impact.",
     "impact_likelihood_scatter_plotdata.csv",
     [("binedge", "Right-hand edge of the citation-impact bin (3-year "
                  "citations)."),
      VENUE,
      ("p_with_letter", "Share of targeted papers in the bin."),
      ("p_no_letter", "Share of non-targeted papers in the bin."),
      ("p_ratio", "r(k) = p_with_letter / p_no_letter."),
      ("count", "Number of papers in the bin.")]),
    ("Supplementary Figure 2",
     "Average marginal effects of first-author characteristics on receipt of "
     "criticism",
     "Average marginal effects from a per-journal logistic regression of "
     "receipt of a critical letter on first-author gender, seniority, and "
     "affiliation prestige, with controls.",
     "paper_firstauthor_demographic_ame_plotdata.csv",
     [("factor", "Characteristic, (A) to (C)."),
      ("AME", "Average marginal effect on the probability of receiving a "
              "critical letter."),
      ("SE", "Standard error."),
      ("z", "z statistic."),
      ("p", "p-value."),
      ("lower", "Lower bound of the 95% confidence interval."),
      ("upper", "Upper bound of the 95% confidence interval."),
      VENUE,
      ("n", "Number of papers in the model.")]),
    ("Supplementary Figure 3",
     "Average marginal effects of last-author characteristics on receipt of "
     "criticism",
     "As Supplementary Figure 2, for last authors.",
     "paper_lastauthor_demographic_ame_plotdata.csv",
     [("factor", "Characteristic, (A) to (C)."),
      ("AME", "Average marginal effect on the probability of receiving a "
              "critical letter."),
      ("SE", "Standard error."),
      ("z", "z statistic."),
      ("p", "p-value."),
      ("lower", "Lower bound of the 95% confidence interval."),
      ("upper", "Upper bound of the 95% confidence interval."),
      VENUE,
      ("n", "Number of papers in the model.")]),
    ("Supplementary Figure 4",
     "Field representation of papers targeted by critical letters",
     "Ratio of the share of targeted papers in each field to the share of "
     "non-targeted papers in that field, within each journal.",
     "field_representation_plot_plotdata.csv",
     [VENUE,
      ("field", "Top-level Microsoft Academic Graph field."),
      ("todrop", "Internal filter flag; all shown rows are FALSE."),
      ("count", "Number of targeted papers in the field (n in the figure)."),
      ("ratio", "Share of targeted papers / share of non-targeted papers."),
      ("ratio_sign", "TRUE if the ratio exceeds 1 (bar shading).")]),
    ("Supplementary Figure 5",
     "Criticized papers more likely to have news coverage or social media "
     "engagement",
     "Share of criticized papers and of matched control papers with at least "
     "one tweet or at least one news mention.",
     "paper_news_tweet_proportion_plotdata.csv",
     [VENUE,
      ("type", "Treatment = criticized paper; Control = matched paper."),
      ("metric", "Figure panel: (A) at least one tweet, (B) at least one news "
                 "mention."),
      ("prop", "Proportion of papers.")]),
    ("Supplementary Figure 6",
     "Criticized papers are concentrated among those with the most "
     "engagement on Twitter/X",
     "Share of criticized papers among the top 10%, 5%, and 1% of papers by "
     "tweet count within each journal (among papers with at least one "
     "tweet).",
     "paper_tweet_distribution_plotdata.csv",
     [VENUE,
      ("type", "letter = criticized papers."),
      ("metric", "Figure panel: top 10%, top 5%, or top 1%."),
      ("prop_hit", "Proportion of criticized papers in that group.")]),
    ("Supplementary Figure 7",
     "Matches for papers by paper impact are high quality",
     "Pre-letter citation impact of each criticized paper (Treatment) and its "
     "matched control (Control).",
     "diagnostics/matching_diagnostic_impact_plot_plotdata.csv",
     [("id", "Microsoft Academic Graph paper ID."),
      VENUE,
      ("treat", "Treatment = criticized paper; Control = matched paper."),
      ("match.group", "Identifier of the matched pair."),
      ("impact_before", "Citations received before the critical letter.")]),
    ("Supplementary Figure 8",
     "Comparison of the matched papers against matched control by time lag",
     "As Figure 2(A), for all letters (A), letters published in the same year "
     "as their target (B), and letters published one or more years later "
     "(C).",
     "matched_comparison_lagtype_plot_plotdata.csv",
     [VENUE,
      ("lagtype", "Figure panel (A) to (C)."),
      ("mean_diff", "Mean of (growth of treatment - growth of control) over "
                    "matched pairs (log growth)."),
      ("interval", "Half-width of the 95% confidence interval."),
      ("upper", "Upper bound of the 95% confidence interval."),
      ("lower", "Lower bound of the 95% confidence interval."),
      ("t.p.value", "p-value of a paired t-test."),
      ("signif", "Significance marker shown in the figure; blank if not "
                 "significant.")]),
    ("Supplementary Figure 9",
     "Analysis of statistical power",
     "Statistical power of a two-sided paired t-test (alpha = 0.05) to detect "
     "a given relative difference in growth between treatment and matched "
     "control, by outcome and journal.",
     "statistical_power_analysis_plotdata.csv",
     [("n", "Number of matched pairs."),
      ("sig.level", "Significance level."),
      ("power", "Probability of detecting the effect (y-axis)."),
      ("d", "Cohen's d = sesoi_log / sd."),
      ("diff", "Detectable effect: relative difference in growth (x-axis; "
               "e.g., 0.1 = 10%)."),
      VENUE,
      ("sesoi_log", "Effect on the log scale, log(1 + diff)."),
      ("sd", "Standard deviation of paired differences in log growth."),
      ("population", "Figure column: papers, or first/last authors' "
                     "citations (cite) or productivity (prod).")]),
    ("Supplementary Figure 10",
     "Altmetrics of critical letters compared to their target",
     "Distribution of tweets (A) and news mentions (B) received by critical "
     "letters, conditional on those received by the papers they target.",
     "letter_altmetric_comparison_plotdata.csv",
     [("panel", "Figure panel."),
      ("original_bin", "Range of tweets or news mentions received by the "
                       "targeted paper (y-axis)."),
      ("letter_bin", "Range received by the critical letter (x-axis)."),
      ("count", "Number of letter-target pairs."),
      ("prop", "Proportion within the row (targeted-paper range).")]),
    ("Supplementary Table 1",
     "Results of the manual annotation of critical letters",
     "Manual annotation of a sample of critical letters published in Nature, "
     "Science, and PNAS (Supplementary Note 3). Each row is one letter. The "
     "table reports, for each journal, the number of letters and the "
     "proportions annotated as valid and as presenting new evidence.",
     "../tables/supp_table1_annotations.csv",
     [("journal", "Journal."),
      ("doi", "DOI of the critical letter."),
      ("is_valid", "1 if the letter was annotated as a valid instance of criticism, 0 otherwise."),
      ("new_evidence", "1 if the letter was annotated as presenting new evidence, 0 otherwise.")]),
    ("Supplementary Table 20",
     "Replies have lower visibility than their associated critical letters",
     "Values reported in the table: average 3-year citations and number of "
     "tweets of critical letters and of the replies to them, for letters "
     "that could be linked to a reply.",
     "../tables/supp_table20_letters_replies.csv",
     [VENUE[0:1] + ("Journal.",),
      ("n", "Number of letters linked to a reply."),
      ("letter_3yr_citations", "Average 3-year citations of the critical letters."),
      ("reply_3yr_citations", "Average 3-year citations of the replies."),
      ("letter_tweets", "Average number of tweets of the critical letters."),
      ("reply_tweets", "Average number of tweets of the replies.")]),
    ("Supplementary Table 24",
     "Results of Bayes Factor Analysis",
     "Bayes factors for the null hypothesis of no difference in growth between "
     "treatment and matched control populations, from a Bayesian one-sample "
     "T-test on paired differences in log growth with a default Cauchy prior. "
     "BF01 > 10 indicates strong, > 3 moderate, and > 1 anecdotal or weak "
     "evidence in favor of the null hypothesis; BF01 < 1 favors the "
     "alternative.",
     "../tables/bayes_factors.csv",
     [VENUE,
      ("outcome", "Outcome compared between treatment and control: paper "
                  "impact, or first/last authors' impact or productivity."),
      ("BF01", "Bayes factor in favor of the null hypothesis.")]),
    ("Bayes factors (all tests)",
     "Bayes factors for all statistical tests reported in the manuscript",
     "Bayes factors complementing each statistical test, computed with "
     "workflow/compute_bayes_factors.R. Percentile-rank comparisons use "
     "one-sided Bayesian t-tests of the mean rank; growth comparisons use "
     "two-sided Bayesian paired t-tests; author characteristics use a BIC "
     "approximation. BF01 > 10 indicates strong, > 3 moderate, and > 1 "
     "anecdotal or weak evidence in favor of the null hypothesis; BF01 < 1 "
     "favors the alternative.",
     "../tables/bayes_factors_all.csv",
     [("analysis", "Analysis the test belongs to."),
      ("figure", "Figure or table reporting the corresponding test."),
      VENUE[0:1] + ("Journal.",),
      ("comparison", "Metric, lag subset, outcome, or author characteristic."),
      ("sided", "One-sided (alternative restricted to positive effects) or two-sided."),
      ("measure", "Quantity tested."),
      ("n", "Number of observations (papers, matched pairs, or authors)."),
      ("estimate", "Estimate of the measure (mean, mean difference, or coefficient)."),
      ("BF10", "Bayes factor in favor of the alternative hypothesis."),
      ("BF01", "Bayes factor in favor of the null hypothesis (1 / BF10)."),
      ("evidence", "Strength of evidence by conventional thresholds.")]),
    ("Test statistics (all tests)",
     "Full statistics for all frequentist tests reported in the manuscript",
     "Test statistic, degrees of freedom or sample sizes, p-value, effect size, "
     "and 95% confidence interval for each frequentist test, computed with "
     "workflow/compute_test_statistics.R. Kolmogorov-Smirnov tests report "
     "sample sizes in place of degrees of freedom and bootstrap CIs of the "
     "mean (difference in) percentile rank; paired t-tests and Wilcoxon "
     "signed-rank tests are computed on within-pair differences in log growth "
     "(treatment minus control).",
     "../tables/test_statistics_all.csv",
     [("analysis", "Analysis the test belongs to."),
      ("figure", "Figure or table reporting the corresponding test."),
      ("spec", "Matching specification (main, or the robustness specification)."),
      VENUE[0:1] + ("Journal.",),
      ("comparison", "Metric, lag subset, outcome, or author characteristic."),
      ("test", "Statistical test."),
      ("statistic_name", "Name of the test statistic (D, t, V, or z)."),
      ("statistic", "Value of the test statistic."),
      ("df", "Degrees of freedom (paired t-tests only)."),
      ("n", "Number of observations (targeted papers, co-citing pairs, matched pairs, or authors)."),
      ("n2", "Number of observations in the second sample (two-sample KS tests only)."),
      ("p", "P-value."),
      ("effect_name", "Name of the effect size."),
      ("effect", "Effect size (mean percentile rank, mean difference, Hodges-Lehmann estimate, or AME)."),
      ("ci_low", "Lower bound of the 95% confidence interval of the effect size."),
      ("ci_high", "Upper bound of the 95% confidence interval of the effect size."),
      ("std_effect_name", "Name of the standardized effect size (d_z or r), if any."),
      ("std_effect", "Standardized effect size (Cohen's d_z for t-tests, r for Wilcoxon tests).")]),
]


def write_sheet(wb, name, title, description, path, columns):
    # R writes missing values as "NA"; leave them as empty cells
    df = pd.read_csv(os.path.join(PLOTDATA, path), keep_default_na=False,
                     na_values=["", "NA"])
    glossary = dict(columns)
    missing = [c for c in df.columns if c not in glossary]
    if missing:
        raise ValueError(f"{name}: no description for columns {missing}")

    ws = wb.create_sheet(name)
    ws.append([name])
    ws["A1"].font = Font(bold=True, size=12)
    ws.append([title])
    ws["A2"].font = Font(bold=True)
    ws.append([description])
    ws.append([])
    ws.append(["Columns"])
    ws.cell(row=ws.max_row, column=1).font = Font(bold=True)
    for col in df.columns:
        ws.append([col, glossary[col]])
    ws.append([])

    ws.append(list(df.columns))
    for cell in ws[ws.max_row]:
        cell.font = Font(bold=True)
    for row in df.itertuples(index=False):
        ws.append([None if pd.isna(v) else v for v in row])

    for row in ws.iter_rows(min_row=1, max_row=3, max_col=1):
        for cell in row:
            cell.alignment = Alignment(wrap_text=False)
    ws.column_dimensions["A"].width = 18
    ws.column_dimensions["B"].width = 18
    return len(df)


def main():
    wb = Workbook()
    wb.remove(wb.active)
    for spec in SHEETS:
        n = write_sheet(wb, *spec)
        print(f"{spec[0]}: {n} rows")
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    wb.save(OUTPUT)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
