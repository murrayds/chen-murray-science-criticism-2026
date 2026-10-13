library(readr)
suppressPackageStartupMessages(library(dplyr))

source("scripts/plotting/theme.R")
source(snakemake@config[["venues_file"]])
source("scripts/common.R")


annotated <- read_csv(snakemake@params[[1]], col_types = cols()) %>%
  filter(Interest == "High") %>%
  # Annotations use the full journal name for PRL
  mutate(journal = ifelse(journal == "Physical Review Letters", "PRL", journal)) %>%
  filter(journal %in% venue_levels()) %>%
  select(letter_id, original_id)

df_matched <- read_csv(snakemake@input[[1]], col_types = cols()) %>%
  mutate(venue = factor(venue, levels = venue_levels())) %>%
  mutate(growth = log(growth)) %>%
  group_by(match.group) %>%
  filter(any(id %in% annotated$original_id)) %>%
  ungroup()

# We will assemble data for each lag parameter...
lag0 <- df_matched %>%
  filter(lag == 0) %>%
  mutate(lagtype = "lag0")

lag1plus <- df_matched %>%
  filter(lag > 0) %>%
  mutate(lagtype = "lag1plus")

df_matched$lagtype <- "lagall"

df_matched <- data.table::rbindlist(list(df_matched, lag1plus, lag0))

# First, perform statistical test...
tests <- df_matched %>%
  mutate(venue = factor(venue, levels = venue_levels())) %>%
  group_by(venue, lagtype) %>%
  arrange(match.group, type) %>%
  do(
    # A paired test needs at least two matched pairs (e.g., PRL with lag 0)
    t = if (sum(.$type == "Control") > 1) {
      t.test(
        .$growth[.$type == "Control"],
        .$growth[.$type == "Treatment"],
        paired = TRUE
      )
    } else {
      list(p.value = NA_real_)
    }
  ) %>%
  summarize(
    venue = venue,
    lagtype = lagtype,
    t.p.value = round(t$p.value, 4),
  )

plotdata <- df_matched %>%
  mutate(
    venue = factor(venue, levels = rev(venue_levels())),
    type = factor(type, levels = c("Treatment", "Control"))
  ) %>%
  group_by(venue, type, lagtype) %>%
  summarize(
    mu_growth = mean(growth),
    interval = sd(growth) / sqrt(n()),
    upper = mu_growth + interval,
    lower = mu_growth - interval
  )

plotdata <- df_matched %>%
  arrange(venue, match.group, type) %>%
  group_by(venue, lagtype, match.group) %>%
  summarize(
    diff = last(growth) - first(growth),
    .groups = "drop"
  ) %>%
  group_by(venue, lagtype) %>%
  summarize(
    num = n(),
    mean_diff = mean(diff),
    interval = 1.96 * sd(diff) / sqrt(n()),
    upper = mean_diff + interval,
    lower = mean_diff - interval,
    .groups = "drop"
  ) %>%
  mutate(
    venue = factor(venue, levels = rev(venue_levels())),
  ) %>%
  left_join(tests, by = c("venue", "lagtype"))

write_csv(plotdata, snakemake@output[[1]])