#' Render the main-text figures as vector PDFs for journal submission
#'
#' Run by the `main_figure_pdfs` rule (rules/Submission.smk). It re-runs the
#' unchanged plotting scripts for Figs. 1-4 on the current workflow data and
#' writes `fig1.pdf` ... `fig4.pdf`. The scripts' other outputs (tables and
#' plotdata) are written to a temporary directory and discarded, so nothing in
#' the workflow's results is modified.
#'
#' Text is drawn as vector outlines with `showtext`, so Unicode labels (mu,
#' Delta) render without the Cairo device. The theme's "Helvetica" is mapped to
#' the metric-compatible Arial, which provides separate bold and italic faces.
#'
#' Usage, run from the `workflow/` directory:
#'   Rscript scripts/submission/render_main_figure_pdfs.R [config.yaml] [output directory]
#' Defaults: `config.yaml` and `../paper/current/figures`.
#'
#' Requires the R packages used by the plotting scripts plus `showtext` and
#' `yaml`, and the Arial fonts shipped with macOS (see `font_dir` below).

suppressPackageStartupMessages({
  library(yaml)
  library(showtext)
})

args <- commandArgs(trailingOnly = TRUE)
config_file <- ifelse(length(args) >= 1, args[1], "config.yaml")
out_dir <- ifelse(length(args) >= 2, args[2], "../paper/current/figures")
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

config <- read_yaml(config_file)
data_dir <- config[["data_dir"]]
plotdata_dir <- file.path(config[["fig_dir"]], "figs", "plotdata")
scratch_dir <- tempdir()

# Draw text as outlines, mapping "Helvetica" to Arial
font_dir <- "/System/Library/Fonts/Supplemental/"
font_add(
  "Helvetica",
  regular = file.path(font_dir, "Arial.ttf"),
  bold = file.path(font_dir, "Arial Bold.ttf"),
  italic = file.path(font_dir, "Arial Italic.ttf"),
  bolditalic = file.path(font_dir, "Arial Bold Italic.ttf")
)
showtext_auto()
showtext_opts(dpi = 300)

# The plotting scripts call ggsave(); route their output to the PDF device
ggsave <- function(...) ggplot2::ggsave(..., device = "pdf")

# Stand-in for the object Snakemake passes to R scripts
setClass("SM", representation(input = "list", output = "list", config = "list"))

agg <- function(f) file.path(data_dir, "derived", "agg", f)

# Inputs are listed in the same order as in rules/Results.smk; `extra` names
# the scripts' outputs beyond the figure itself
figures <- list(
  fig1 = list(
    script = "scripts/plotting/plot_paper_metrics_density.R",
    input = c(
      agg("agg_letters.csv"),
      agg("agg_nonletters.csv"),
      agg("agg_fields.csv"),
      file.path(data_dir, "downloaded", "paper_field_refs.csv"),
      file.path(data_dir, "downloaded", "paper_field_cites.csv"),
      file.path(data_dir, "derived", "novelty", "paper_zscores.csv"),
      file.path(data_dir, "derived", "matched",
                "matched_papers_metricdensity_0.05impact_3year.csv")
    ),
    extra = c("table_1s.txt", "table_2s.txt", "plotdata.csv")
  ),
  fig2 = list(
    script = "scripts/plotting/plot_matched_comparison.R",
    input = file.path(plotdata_dir, c(
      "paper_impact_comparison_plotdata.csv",
      "first-author_citations_comparison_authors.csv",
      "first-author_prod_comparison_authors.csv",
      "last-author_citations_comparison_authors.csv",
      "last-author_prod_comparison_authors.csv"
    )),
    extra = "plotdata.csv"
  ),
  fig3 = list(
    script = "scripts/plotting/plot_impact_temporal_comparison.R",
    input = c(
      agg("agg_letters.csv"),
      agg("agg_dual_cite_trajectories.csv"),
      agg("agg_paper_titles.csv")
    ),
    extra = "plotdata.csv"
  ),
  fig4 = list(
    script = "scripts/plotting/plot_embedding_cocite_density.R",
    input = c(
      agg("agg_letters.csv"),
      agg("agg_paper_titles.csv"),
      agg("agg_dual_cite_trajectories.csv"),
      file.path(data_dir, "derived", "embedding",
                "agg_title_embedding_similarities.csv")
    ),
    extra = c("table.txt", "plotdata.csv")
  )
)

for (name in names(figures)) {
  fig <- figures[[name]]
  missing <- fig$input[!file.exists(fig$input)]
  if (length(missing) > 0) {
    stop("Missing inputs for ", name, ": ", paste(missing, collapse = ", "))
  }

  outputs <- c(
    file.path(out_dir, paste0(name, ".pdf")),
    file.path(scratch_dir, paste0(name, "_", fig$extra))
  )
  snakemake <- new(
    "SM",
    input = as.list(fig$input),
    output = as.list(outputs),
    config = list(venues_file = config[["venues_file"]])
  )

  suppressMessages(suppressWarnings(source(fig$script, local = TRUE)))
  message("Wrote ", outputs[1])
}
