library(readr)
suppressPackageStartupMessages(library(dplyr))
suppressPackageStartupMessages(library(ggplot2))

source("scripts/plotting/theme.R")
source(snakemake@config[["venues_file"]])
source("scripts/common.R")

papers <- read_csv(snakemake@input[[1]], col_types = cols()) %>%
  filter(lagtype == "lagall") %>%
  select(venue, mean_diff, upper, lower, t.p.value) %>%
  mutate(
    panel = "papers"
  )

authors <- rbind(
  read_csv(snakemake@input[[2]], col_types = cols()),
  read_csv(snakemake@input[[3]], col_types = cols()),
  read_csv(snakemake@input[[4]], col_types = cols()),
  read_csv(snakemake@input[[5]], col_types = cols())
) %>%
  mutate(
    panel = paste0(authorship, "-", metric)
  ) %>%
  select(venue, mean_diff, upper, lower, t.p.value, panel)

plotdata <- rbind(authors, papers) %>%
  mutate(
    signif = case_when(
      t.p.value > 0.05 ~ "",
      t.p.value > 0.01 ~ "*",
      t.p.value > 0.001 ~ "**",
      !is.na(t.p.value) ~ "***",
      TRUE ~ NA_character_
    ),
    venue = factor(venue, levels = rev(venue_levels())),
    panel = factor(
      panel,
      levels = c(
        "papers",
        "first-frac_prod",
        "last-frac_prod",
        "first-impact_raw",
        "last-impact_raw"
      ),
      labels = c(
        "(A) Paper citations",
        "(B) First author productivity",
        "(C) Last author productivity",
        "(D) First author citations",
        "(E) Last author citations"
      )
    )
  )

print(plotdata)
p <- plotdata %>%
  ggplot(aes(x = mean_diff, y = venue, color = venue)) +
  geom_errorbar(aes(xmin = lower, xmax = upper), width = 0) +
  geom_point(
    aes(fill = venue),
    shape = 21, color = "black", stroke = 0.3, size = 3
  ) +
  geom_vline(xintercept = 0, linetype = "dashed") +
  geom_text(
    aes(label = signif, x = upper),
    nudge_x = 0.075,
    nudge_y = -0.1,
    size = 6,
  ) +
  facet_wrap(~panel, scale = "free_x", nrow = 1) +
  scale_color_manual(values = venue_colors(), guide = "none") +
  scale_fill_manual(values = venue_colors(), guide = "none") +
  theme_criticism() +
  # Plain-weight text throughout (journal style: no bold in display items)
  theme(
    axis.title = element_text(face = "plain"),
    legend.text = element_text(face = "plain"),
    strip.text = element_text(face = "plain")
  ) +
  theme(
    legend.position = c(0.25, 0.75),
    panel.spacing.x = unit(0.30, "cm", data = NULL),
    strip.text = element_text(angle = 0, hjust = 0),
    strip.text.y = element_text(size = 13),
    axis.title.y = element_blank(),
    axis.text.y = element_text(face = "plain")
  ) +
  xlab("ΔTreatment - ΔControl")

# Save the figure output
ggsave(
  p,
  filename = snakemake@output[[1]],
  width = 10.5,
  height = 3,
  bg = "white"
)

# Save the data underlying the plot
write_csv(plotdata, snakemake@output[[2]])
