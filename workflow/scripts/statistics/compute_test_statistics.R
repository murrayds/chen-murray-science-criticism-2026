#' Compute full frequentist statistics for the results reported in the manuscript
#'
#' Run by the `test_statistics` rule (rules/Submission.smk). It re-runs each
#' frequentist test reported in the manuscript with the same data, test, and
#' seed as the workflow, and reports for each the test statistic, its degrees
#' of freedom (or sample sizes, for tests without degrees of freedom), the
#' p-value, an effect size, and a 95% confidence interval. Results are written
#' to a single CSV.
#'
#' Tests and the effect sizes reported for each:
#'   - One-sample, one-sided KS tests of percentile ranks against a uniform
#'     distribution (Figs. 1 and 4, supplementary journals): D with n; effect
#'     size is the mean percentile rank, with a 95% percentile bootstrap CI.
#'   - Two-sample, one-sided KS tests against matched papers (Fig. 1,
#'     supplementary journals): D with n1 and n2; effect size is the mean
#'     within-pair difference in percentile rank (targeted - matched), with a
#'     95% percentile bootstrap CI.
#'   - Two-sided paired t-tests of growth (Fig. 2, Fig. S8, robustness tables,
#'     high-interest, APS-journal, and supplementary-journal analyses): t with
#'     df; effect size is the mean difference in log growth (treatment -
#'     control) with its 95% t-based CI, and Cohen's d_z.
#'   - Wilcoxon signed-rank tests (robustness check of the paired t-tests): V
#'     with n; effect size is the Hodges-Lehmann estimate with its 95% CI, and
#'     r = |Z| / sqrt(n).
#'   - Average marginal effects of author characteristics (Figs. S2-S3): z;
#'     effect size is the AME with its 95% CI (taken from the workflow output).
#'
#' Usage, run from the `workflow/` directory (normally via Snakemake):
#'   Rscript scripts/statistics/compute_test_statistics.R [output file]
#' Default output: `../results/figs/tables/test_statistics_all.csv`.
#'
#' Requires readr, dplyr, tidyr, and yaml.

suppressPackageStartupMessages({
  library(yaml)
  library(readr)
  library(dplyr)
  library(tidyr)
})

args <- commandArgs(trailingOnly = TRUE)
out_file <- ifelse(
  length(args) >= 1, args[1], "../results/figs/tables/test_statistics_all.csv"
)

main <- suppressWarnings(read_yaml("config.yaml"))
supp <- suppressWarnings(read_yaml("config_supplement.yaml"))
seed <- main[["matching"]][["seed"]]
n_boot <- 10000

aps_journals <- c("PR-A", "PR-B", "PR-C", "PR-D", "PR-E")
collapse_venue <- function(v) ifelse(v %in% aps_journals, "Other APS", v)

#
# Helpers
#

# 95% percentile bootstrap CI of the mean of `x`
boot_ci <- function(x) {
  means <- replicate(n_boot, mean(sample(x, replace = TRUE)))
  unname(quantile(means, c(0.025, 0.975)))
}

# One-sample, one-sided KS test of percentile ranks against a uniform
# distribution, as in the workflow. `x` has already been jittered.
ks_one_sample <- function(x) {
  ks <- ks.test(x, "punif", min = 0, max = 1, alternative = "less")
  ci <- boot_ci(x)
  data.frame(
    test = "1s KS", statistic_name = "D", statistic = unname(ks$statistic),
    df = NA, n = length(x), n2 = NA, p = ks$p.value,
    effect_name = "mean percentile rank", effect = mean(x),
    ci_low = ci[1], ci_high = ci[2], std_effect_name = NA, std_effect = NA
  )
}

# Two-sample, one-sided KS test of targeted against matched papers, as in the
# workflow. `letter` and `article` are aligned by match group.
ks_two_sample <- function(letter, article) {
  ks <- ks.test(letter, article, alternative = "less")
  diff <- letter - article
  ci <- boot_ci(diff)
  data.frame(
    test = "2s KS", statistic_name = "D", statistic = unname(ks$statistic),
    df = NA, n = length(letter), n2 = length(article), p = ks$p.value,
    effect_name = "mean within-pair rank difference", effect = mean(diff),
    ci_low = ci[1], ci_high = ci[2], std_effect_name = NA, std_effect = NA
  )
}

# Two-sided paired t-test on within-pair differences (treatment - control)
paired_t <- function(diff) {
  diff <- diff[is.finite(diff)]
  if (length(diff) < 2) return(NULL)
  t <- t.test(diff)
  data.frame(
    test = "paired t-test", statistic_name = "t",
    statistic = unname(t$statistic), df = unname(t$parameter),
    n = length(diff), n2 = NA, p = t$p.value,
    effect_name = "mean difference in log growth", effect = mean(diff),
    ci_low = t$conf.int[1], ci_high = t$conf.int[2],
    std_effect_name = "d_z", std_effect = mean(diff) / sd(diff)
  )
}

# Two-sided Wilcoxon signed-rank test on within-pair differences
wilcoxon <- function(diff) {
  diff <- diff[is.finite(diff)]
  if (length(diff) < 2) return(NULL)
  w <- wilcox.test(diff, conf.int = TRUE, exact = FALSE)
  data.frame(
    test = "Wilcoxon signed-rank", statistic_name = "V",
    statistic = unname(w$statistic), df = NA, n = length(diff), n2 = NA,
    p = w$p.value, effect_name = "Hodges-Lehmann estimate",
    effect = unname(w$estimate), ci_low = w$conf.int[1],
    ci_high = w$conf.int[2], std_effect_name = "r",
    std_effect = abs(qnorm(w$p.value / 2)) / sqrt(length(diff))
  )
}

# Both tests of paired growth differences
paired_tests <- function(diff) bind_rows(paired_t(diff), wilcoxon(diff))

# Paired differences in log growth (treatment - control) within match groups
growth_diff <- function(df) {
  df <- df %>%
    group_by(match.group) %>%
    filter(n() == 2) %>%
    ungroup() %>%
    arrange(match.group, type)
  log(df$growth[df$type == "Treatment"]) -
    log(df$growth[df$type == "Control"])
}

# Paired differences in log author growth (treatment - control)
author_diff <- function(authors, metric) {
  changes <- authors %>%
    rename(value = all_of(metric)) %>%
    select(AuthorId, venue, treat, match.group, partition, value) %>%
    pivot_wider(names_from = partition, values_from = value) %>%
    mutate(change = log(after / before)) %>%
    filter(!is.na(change)) %>%
    group_by(venue, match.group) %>%
    filter(n() > 1) %>%
    ungroup() %>%
    arrange(venue, match.group, treat)
  changes %>%
    group_by(venue) %>%
    summarize(diff = list(change[treat == 1] - change[treat == 0]),
              .groups = "drop")
}

results <- list()
add <- function(df, analysis, figure, spec = "main") {
  results[[length(results) + 1]] <<- df %>%
    mutate(analysis = analysis, figure = figure, spec = spec, .before = 1)
}

#
# 1. Percentile-rank analyses (Fig. 1 and supplementary journals)
#
rank_analyses <- function(cfg, label) {
  fig_dir <- file.path(cfg[["fig_dir"]], "figs")
  plotdata <- read_csv(
    file.path(fig_dir, "plotdata", "paper_metrics_density_plotdata.csv"),
    col_types = cols()
  )
  matched <- read_csv(
    file.path(cfg[["data_dir"]], "derived", "matched",
              "matched_papers_metricdensity_0.05impact_3year.csv"),
    col_types = cols()
  ) %>%
    distinct(id, match.group)
  figure <- ifelse(label == "Main", "Fig. 1", "Supp. journals")

  # The workflow seeds the jitter and applies it first to the targeted papers,
  # in the order in which they are saved in the plot data
  set.seed(seed)
  letters <- plotdata %>%
    filter(type == "letter") %>%
    mutate(rank = jitter(rank, factor = 1e-8))
  one_sample <- letters %>%
    group_by(venue, comparison = metric) %>%
    group_modify(~ ks_one_sample(.x$rank)) %>%
    ungroup()
  add(one_sample, paste0(label, ": percentile rank vs. uniform"), figure)

  two_sample <- plotdata %>%
    filter(metric != "Citations") %>%
    mutate(rank = jitter(rank, factor = 1e-8)) %>%
    inner_join(matched, by = "id") %>%
    group_by(venue, metric, match.group) %>%
    filter(n() > 1) %>%
    ungroup() %>%
    pivot_wider(id_cols = c(venue, metric, match.group),
                names_from = type, values_from = rank) %>%
    filter(!is.na(letter), !is.na(article)) %>%
    arrange(venue, match.group) %>%
    group_by(venue, comparison = metric) %>%
    group_modify(~ ks_two_sample(.x$letter, .x$article)) %>%
    ungroup()
  add(two_sample, paste0(label, ": percentile rank vs. matched papers"), figure)
}
rank_analyses(main, "Main")
rank_analyses(supp, "Supplementary")

#
# 2. Similarity of co-citing papers (Fig. 4)
#
set.seed(seed)
embedding <- read_csv(
  file.path(main[["fig_dir"]], "figs", "plotdata",
            "embedding_cocite_density_plot_plotdata.csv"),
  col_types = cols()
) %>%
  filter(!is.na(rank)) %>%
  mutate(rank = jitter(rank, factor = 1e-8)) %>%
  group_by(venue, comparison = "Similarity rank") %>%
  group_modify(~ ks_one_sample(.x$rank)) %>%
  ungroup()
add(embedding, "Main: co-citing similarity rank vs. uniform", "Fig. 4")

# The supplementary journals' plot data are written by the same plotting rule
# when the workflow is run with `config_supplement.yaml`
supp_embedding_plotdata <- file.path(
  supp[["fig_dir"]], "figs", "plotdata",
  "embedding_cocite_density_plot_plotdata.csv"
)
set.seed(seed)
supp_embedding <- read_csv(supp_embedding_plotdata, col_types = cols()) %>%
  filter(!is.na(rank)) %>%
  mutate(rank = jitter(rank, factor = 1e-8)) %>%
  group_by(venue, comparison = "Similarity rank") %>%
  group_modify(~ ks_one_sample(.x$rank)) %>%
  ungroup()
add(supp_embedding, "Supplementary: co-citing similarity rank vs. uniform",
    "Supp. journals")

#
# 3. Paper impact growth (Fig. 2A, Fig. S8, robustness, APS journals, high
#    interest, supplementary journals)
#
set.seed(seed)
read_papers <- function(cfg, delay, impact, year) {
  read_csv(
    file.path(cfg[["data_dir"]], "derived", "matched",
              sprintf("matched_papers_stage1_%sdelay_%simpact_%syear.csv",
                      delay, impact, year)),
    col_types = cols()
  )
}
papers <- read_papers(main, 3, 0.05, 1)

by_lag <- bind_rows(
  papers %>% mutate(comparison = "All lags"),
  papers %>% filter(lag == 0) %>% mutate(comparison = "Lag = 0"),
  papers %>% filter(lag > 0) %>% mutate(comparison = "Lag > 0")
) %>%
  mutate(venue = collapse_venue(venue)) %>%
  group_by(venue, comparison) %>%
  group_modify(~ paired_tests(growth_diff(.x))) %>%
  ungroup()
add(by_lag, "Main: paper impact growth", "Fig. 2A, Fig. S8")

# Robustness across matching specifications (Table paper-matched-ttest)
specs <- tribble(
  ~delay, ~impact, ~year,
  2, 0.05, 2,
  3, 0.05, 2,
  4, 0.05, 2,
  3, 0.1, 2,
  3, 0.15, 2,
  3, 0.05, 1
)
for (i in seq_len(nrow(specs))) {
  s <- specs[i, ]
  res <- read_papers(main, s$delay, s$impact, s$year) %>%
    mutate(venue = collapse_venue(venue)) %>%
    group_by(venue, comparison = "All lags") %>%
    group_modify(~ paired_tests(growth_diff(.x))) %>%
    ungroup()
  add(res, "Robustness: paper impact growth", "Table paper-matched-ttest",
      sprintf("delay %s, citations %s%%, year %s",
              s$delay, s$impact * 100, s$year))
}

aps <- papers %>%
  filter(venue %in% c("PRL", aps_journals)) %>%
  group_by(venue, comparison = "All lags") %>%
  group_modify(~ paired_t(growth_diff(.x))) %>%
  ungroup()
add(aps, "Main: paper impact growth by APS journal", "Table aps-journal-ttests")

annotated <- read_csv(
  file.path(main[["raw_dir"]], "letter_llm_annotated_data.csv"),
  col_types = cols()
) %>%
  filter(Interest == "High")
high_interest <- papers %>%
  group_by(match.group) %>%
  filter(any(id %in% annotated$original_id)) %>%
  ungroup() %>%
  filter(venue %in% c("Nature", "Science", "PNAS", "PRL")) %>%
  group_by(venue, comparison = "All lags") %>%
  group_modify(~ paired_t(growth_diff(.x))) %>%
  ungroup()
add(high_interest, "Main: paper impact growth, high-interest letters",
    "Table high-interest-analysis")

supp_papers <- read_papers(supp, 3, 0.05, 1) %>%
  group_by(venue, comparison = "All lags") %>%
  group_modify(~ paired_t(growth_diff(.x))) %>%
  ungroup()
add(supp_papers, "Supplementary: paper impact growth", "S6 Text")

#
# 4. Author productivity and impact growth (Fig. 2B-E and robustness)
#
author_specs <- tribble(
  ~impact, ~prod,
  0.05, 0.15,
  0.1, 0.15,
  0.15, 0.15,
  0.15, 0.05,
  0.15, 0.1
)
for (authorship in c("first", "last")) {
  for (i in seq_len(nrow(author_specs))) {
    s <- author_specs[i, ]
    authors <- read_csv(
      file.path(main[["data_dir"]], "derived", "matched",
                sprintf("matched_%s_authors_%simpact_%sprod.csv",
                        authorship, s$impact, s$prod)),
      col_types = cols()
    ) %>%
      mutate(venue = collapse_venue(venue))
    is_main <- s$impact == 0.15 && s$prod == 0.15
    for (metric in c("frac_prod", "impact_raw")) {
      label <- paste(
        ifelse(authorship == "first", "First-author", "Last-author"),
        ifelse(metric == "frac_prod", "productivity", "citations")
      )
      diffs <- author_diff(authors, metric)
      res <- diffs %>%
        group_by(venue, comparison = label) %>%
        group_modify(~ paired_tests(.x$diff[[1]])) %>%
        ungroup()
      add(res,
          ifelse(is_main, "Main: author growth", "Robustness: author growth"),
          ifelse(is_main, "Fig. 2B-E",
                 ifelse(metric == "frac_prod",
                        "Table authors-matched-productivity-ttest",
                        "Table authors-matched-impact-ttest")),
          sprintf("citations %s%%, productivity %s%%",
                  s$impact * 100, s$prod * 100))
    }
  }
}

#
# 5. Author characteristics (Figs. S2-S3): average marginal effects
#
for (authorship in c("first", "last")) {
  ame <- read_csv(
    file.path(main[["fig_dir"]], "figs", "plotdata",
              sprintf("paper_%sauthor_demographic_ame_plotdata.csv",
                      authorship)),
    col_types = cols()
  ) %>%
    transmute(
      venue, comparison = factor,
      test = "average marginal effect", statistic_name = "z", statistic = z,
      df = NA, n, n2 = NA, p,
      effect_name = "AME", effect = AME, ci_low = lower, ci_high = upper,
      std_effect_name = NA, std_effect = NA
    )
  add(ame, "Main: author characteristics",
      ifelse(authorship == "first", "Fig. S2", "Fig. S3"))
}

#
# Combine
#
all_results <- bind_rows(results) %>%
  select(analysis, figure, spec, venue, comparison, test, statistic_name,
         statistic, df, n, n2, p, effect_name, effect, ci_low, ci_high,
         std_effect_name, std_effect)

dir.create(dirname(out_file), showWarnings = FALSE, recursive = TRUE)
write_csv(all_results, out_file)
message("Wrote ", nrow(all_results), " test results to ", out_file)
