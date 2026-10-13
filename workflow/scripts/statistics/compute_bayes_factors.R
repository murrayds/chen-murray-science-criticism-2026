#' Compute Bayes factors for the results reported in the manuscript
#'
#' Run by the `bayes_factors` rule (rules/Submission.smk). It complements
#' each frequentist test reported in the manuscript with a Bayes factor,
#' using the same default Cauchy prior as the existing analysis
#' (`notebooks/statistical-power-analysis.rmd`), and writes all results to a
#' single CSV.
#'
#' Bayesian counterparts of each test:
#'   - One-sample KS tests of percentile ranks against a uniform distribution
#'     (Figs. 1 and 4): one-sided Bayesian one-sample t-test of the mean
#'     percentile rank against 0.5.
#'   - Two-sample KS tests against matched papers (Fig. 1): one-sided Bayesian
#'     paired t-test on within-pair differences in percentile rank.
#'   - Paired t-tests of growth (Fig. 2, Fig. S8, high-interest, APS-journal,
#'     and supplementary-journal analyses): two-sided Bayesian paired t-test
#'     on within-pair differences in log growth.
#'   - Average marginal effects of author characteristics (Figs. S2-S3):
#'     BIC approximation comparing logistic models with and without each
#'     characteristic (Wagenmakers 2007).
#'
#' BF01 quantifies evidence for the null hypothesis relative to the
#' alternative; BF10 = 1 / BF01.
#'
#' Usage, run from the `workflow/` directory:
#'   Rscript scripts/statistics/compute_bayes_factors.R [output file]
#' Default output: `../results/figs/tables/bayes_factors_all.csv`.
#'
#' Requires readr, dplyr, tidyr, yaml, BayesFactor, and the packages used by
#' `scripts/plotting/gen_author_marginal_probabilities.R`.

suppressPackageStartupMessages({
  library(yaml)
  library(readr)
  library(dplyr)
  library(tidyr)
  library(BayesFactor)
})

args <- commandArgs(trailingOnly = TRUE)
out_file <- ifelse(
  length(args) >= 1, args[1], "../results/figs/tables/bayes_factors_all.csv"
)

main <- read_yaml("config.yaml")
supp <- read_yaml("config_supplement.yaml")
set.seed(main[["matching"]][["seed"]])

aps_journals <- c("PR-A", "PR-B", "PR-C", "PR-D", "PR-E")
collapse_venue <- function(v) ifelse(v %in% aps_journals, "Other APS", v)

#
# Helpers
#

# Bayes factor for a one-sample t-test on `x` against zero. When `one_sided`
# is TRUE, the alternative is restricted to positive effects.
bf_ttest <- function(x, one_sided = FALSE) {
  x <- x[is.finite(x)]
  if (length(x) < 2) {
    return(data.frame(n = length(x), estimate = NA, BF10 = NA))
  }
  if (one_sided) {
    bf10 <- extractBF(
      ttestBF(x, mu = 0, nullInterval = c(0, Inf)), onlybf = TRUE
    )[1]
  } else {
    bf10 <- extractBF(ttestBF(x, mu = 0), onlybf = TRUE)
  }
  data.frame(n = length(x), estimate = mean(x), BF10 = bf10)
}

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

results <- list()
add <- function(df, analysis, figure, sided, measure) {
  results[[length(results) + 1]] <<- df %>%
    mutate(
      analysis = analysis, figure = figure, sided = sided, measure = measure,
      .before = 1
    )
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

  # One-sample: mean percentile rank of targeted papers against 0.5
  one_sample <- plotdata %>%
    filter(type == "letter") %>%
    group_by(venue, comparison = metric) %>%
    group_modify(~ bf_ttest(.x$rank - 0.5, one_sided = TRUE)) %>%
    ungroup() %>%
    mutate(estimate = estimate + 0.5)
  add(one_sample, paste0(label, ": percentile rank vs. uniform"),
      ifelse(label == "Main", "Fig. 1", "Supp. journals (Table 1ks_extra)"),
      "one-sided", "mean percentile rank")

  # Two-sample: within-pair rank differences against matched papers
  two_sample <- plotdata %>%
    # the citation-impact metric is labelled "Citations" (formerly "Impact")
    filter(!metric %in% c("Impact", "Citations")) %>%
    inner_join(matched, by = "id") %>%
    group_by(venue, metric, match.group) %>%
    filter(n() > 1) %>%
    ungroup() %>%
    pivot_wider(id_cols = c(venue, metric, match.group),
                names_from = type, values_from = rank) %>%
    filter(!is.na(letter), !is.na(article)) %>%
    group_by(venue, comparison = metric) %>%
    group_modify(~ bf_ttest(.x$letter - .x$article, one_sided = TRUE)) %>%
    ungroup()
  add(two_sample, paste0(label, ": percentile rank vs. matched papers"),
      ifelse(label == "Main", "Fig. 1", "Supp. journals (Table 2ks_extra)"),
      "one-sided", "mean within-pair rank difference")
}
rank_analyses(main, "Main")
rank_analyses(supp, "Supplementary")

#
# 2. Similarity of co-citing papers (Fig. 4)
#
embedding <- read_csv(
  file.path(main[["fig_dir"]], "figs", "plotdata",
            "embedding_cocite_density_plot_plotdata.csv"),
  col_types = cols()
) %>%
  group_by(venue, comparison = "Similarity rank") %>%
  group_modify(~ bf_ttest(.x$rank - 0.5, one_sided = TRUE)) %>%
  ungroup() %>%
  mutate(estimate = estimate + 0.5)
add(embedding, "Main: co-citing similarity rank vs. uniform", "Fig. 4",
    "one-sided", "mean percentile rank")

# Supplementary journals; the plot data are written by the embedding plotting
# rule when the workflow is run with `config_supplement.yaml`
supp_embedding_file <- file.path(
  supp[["fig_dir"]], "figs", "plotdata",
  "embedding_cocite_density_plot_plotdata.csv"
)
if (file.exists(supp_embedding_file)) {
  supp_embedding <- read_csv(supp_embedding_file, col_types = cols()) %>%
    group_by(venue, comparison = "Similarity rank") %>%
    group_modify(~ bf_ttest(.x$rank - 0.5, one_sided = TRUE)) %>%
    ungroup() %>%
    mutate(estimate = estimate + 0.5)
  add(supp_embedding,
      "Supplementary: co-citing similarity rank vs. uniform",
      "Supp. journals (Table embedding_tests_extra)",
      "one-sided", "mean percentile rank")
}

#
# 3. Paper impact growth (Fig. 2A, Fig. S8, APS journals, high interest,
#    supplementary journals)
#
papers <- read_csv(
  file.path(main[["data_dir"]], "derived", "matched",
            "matched_papers_stage1_3delay_0.05impact_1year.csv"),
  col_types = cols()
)

by_lag <- bind_rows(
  papers %>% mutate(comparison = "All lags"),
  papers %>% filter(lag == 0) %>% mutate(comparison = "Lag = 0"),
  papers %>% filter(lag > 0) %>% mutate(comparison = "Lag > 0")
) %>%
  mutate(venue = collapse_venue(venue)) %>%
  group_by(venue, comparison) %>%
  group_modify(~ bf_ttest(growth_diff(.x))) %>%
  ungroup()
add(by_lag, "Main: paper impact growth", "Fig. 2A, Fig. S8", "two-sided",
    "mean difference in log growth")

aps <- papers %>%
  filter(venue %in% c("PRL", aps_journals)) %>%
  group_by(venue, comparison = "All lags") %>%
  group_modify(~ bf_ttest(growth_diff(.x))) %>%
  ungroup()
add(aps, "Main: paper impact growth by APS journal",
    "Table aps-journal-ttests", "two-sided", "mean difference in log growth")

annotated <- read_csv(
  file.path(main[["raw_dir"]], "letter_llm_annotated_data.csv"),
  col_types = cols()
) %>%
  filter(Interest == "High") %>%
  mutate(journal = ifelse(journal == "Physical Review Letters", "PRL", journal))
high_interest <- papers %>%
  group_by(match.group) %>%
  filter(any(id %in% annotated$original_id)) %>%
  ungroup() %>%
  filter(venue %in% c("Nature", "Science", "PNAS", "PRL")) %>%
  group_by(venue, comparison = "All lags") %>%
  group_modify(~ bf_ttest(growth_diff(.x))) %>%
  ungroup()
add(high_interest, "Main: paper impact growth, high-interest letters",
    "Table high-interest-analysis", "two-sided", "mean difference in log growth")

supp_papers <- read_csv(
  file.path(supp[["data_dir"]], "derived", "matched",
            "matched_papers_stage1_3delay_0.05impact_1year.csv"),
  col_types = cols()
) %>%
  group_by(venue, comparison = "All lags") %>%
  group_modify(~ bf_ttest(growth_diff(.x))) %>%
  ungroup()
add(supp_papers, "Supplementary: paper impact growth", "S6 Text", "two-sided",
    "mean difference in log growth")

#
# 4. Author productivity and impact growth (Fig. 2B-E)
#
for (authorship in c("first", "last")) {
  authors <- read_csv(
    file.path(main[["data_dir"]], "derived", "matched",
              sprintf("matched_%s_authors_0.15impact_0.15prod.csv", authorship)),
    col_types = cols()
  ) %>%
    mutate(venue = collapse_venue(venue))
  for (metric in c("frac_prod", "impact_raw")) {
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
    label <- paste(
      ifelse(authorship == "first", "First-author", "Last-author"),
      ifelse(metric == "frac_prod", "productivity", "impact")
    )
    res <- changes %>%
      group_by(venue, comparison = label) %>%
      group_modify(~ bf_ttest(.x$change[.x$treat == 1] - .x$change[.x$treat == 0])) %>%
      ungroup()
    add(res, "Main: author growth", "Fig. 2B-E", "two-sided",
        "mean difference in log growth")
  }
}

#
# 5. Author characteristics (Figs. S2-S3): BIC approximation
#
setClass("SM", representation(
  input = "list", output = "list", config = "list",
  wildcards = "list", params = "list"
))
predictors <- c(gender = "genderFemale", seniority = "senioritySenior",
                elite = "eliteElite")
for (authorship in c("first", "last")) {
  snakemake <- new(
    "SM",
    input = list(
      file.path(main[["data_dir"]], "downloaded", "author_profiles.csv"),
      file.path(main[["data_dir"]], "downloaded", "career_histories.csv"),
      file.path(main[["data_dir"]], "derived", "matched",
                "matched_papers_metricdensity_0.05impact_1year.csv")
    ),
    output = list(tempfile(fileext = ".csv")),
    config = list(venues_file = main[["venues_file"]]),
    wildcards = list(authorship),
    params = list(file.path(main[["raw_dir"]], "elite_university_list.csv"))
  )
  env <- new.env()
  suppressMessages(suppressWarnings(sys.source(
    "scripts/plotting/gen_author_marginal_probabilities.R", envir = env
  )))
  model_data <- env$targeted_df
  for (v in unique(as.character(model_data$venue))) {
    d <- model_data %>%
      filter(venue == v) %>%
      select(type, gender, seniority, elite, num_authors, impact, year) %>%
      na.omit()
    full <- glm(type ~ gender + seniority + elite + num_authors + impact + year,
                data = d, family = binomial)
    for (p in names(predictors)) {
      reduced <- update(full, as.formula(paste(". ~ . -", p)))
      results[[length(results) + 1]] <- data.frame(
        analysis = "Main: author characteristics",
        figure = ifelse(authorship == "first", "Fig. S2", "Fig. S3"),
        sided = "two-sided",
        measure = "logistic regression coefficient",
        venue = v,
        comparison = paste(
          ifelse(authorship == "first", "First author:", "Last author:"),
          predictors[[p]]
        ),
        n = nobs(full),
        estimate = unname(coef(full)[predictors[[p]]]),
        BF10 = exp((BIC(reduced) - BIC(full)) / 2)
      )
    }
  }
}

#
# Combine and label the strength of evidence (Jeffreys conventions)
#
evidence <- function(bf01) {
  case_when(
    is.na(bf01) ~ NA_character_,
    bf01 > 10 ~ "strong for null",
    bf01 > 3 ~ "moderate for null",
    bf01 > 1 ~ "anecdotal for null",
    bf01 > 1 / 3 ~ "anecdotal for alternative",
    bf01 > 1 / 10 ~ "moderate for alternative",
    TRUE ~ "strong for alternative"
  )
}

all_results <- bind_rows(results) %>%
  mutate(
    BF01 = 1 / BF10,
    evidence = evidence(BF01)
  ) %>%
  select(analysis, figure, venue, comparison, sided, measure, n, estimate,
         BF10, BF01, evidence)

dir.create(dirname(out_file), showWarnings = FALSE, recursive = TRUE)
write_csv(all_results, out_file)
message("Wrote ", nrow(all_results), " Bayes factors to ", out_file)
