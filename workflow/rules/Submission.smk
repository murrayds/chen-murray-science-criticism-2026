####################
# STATISTICS AND SUBMISSION FILES
#
# These rules run with the main configuration (config.yaml) and combine its
# results with those of the supplementary journals, so the supplementary
# results must be computed first (`make results_supplement`). They produce
# the full test statistics and Bayes factors, the Supplementary Information
# statistics tables, the main-text figure PDFs, the Source Data file, and the
# public data export.
####################

import yaml

SUPP_CONFIG = yaml.safe_load(open(j(workflow.basedir, "config_supplement.yaml")))
SUPP_FIG_DIR = j(SUPP_CONFIG["fig_dir"], "figs")
SUPP_DERIVED_DIR = j(SUPP_CONFIG["data_dir"], "derived")

PAPER_DIR = j(workflow.basedir, "..", "paper", "current")
TABLES_DIR = j(FIG_DIR, "tables")

TEST_STATISTICS = j(TABLES_DIR, "test_statistics_all.csv")
BAYES_FACTORS_ALL = j(TABLES_DIR, "bayes_factors_all.csv")
SUPP_TABLE3_SOURCE = j(TABLES_DIR, "supp_table1_annotations.csv")
SUPP_TABLE14_SOURCE = j(TABLES_DIR, "supp_table20_letters_replies.csv")
MANUAL_ANNOTATIONS = j(RAW_DIR, "critical-letter_annotations.xlsx")

SI_TABLE_NAMES = [
    "ks_one_sample", "ks_two_sample", "ks_embedding",
    "ks_one_sample_supplementary", "ks_two_sample_supplementary",
    "ks_embedding_supplementary", "ttest_paper_robustness",
    "ttest_author_productivity_robustness", "ttest_author_citations_robustness",
    "ttest_high_interest", "ttest_aps_journals", "ttest_wilcoxon_full", "ame",
    "visibility_n",
]
SI_TABLES = expand(j(PAPER_DIR, "tables", "{name}.tex"), name = SI_TABLE_NAMES)
MAIN_FIGURE_PDFS = expand(j(PAPER_DIR, "figures", "fig{n}.pdf"), n = [1, 2, 3, 4])
SOURCE_DATA = j(PAPER_DIR, "source_data", "Source Data.xlsx")
FIGURE_SOURCE_DATA_CSVS = expand(j(PAPER_DIR, "source_data", "fig{n}_source_data.csv"), n = [1, 2, 3, 4])

DATA_EXPORT = j(config["data_dir"], "..", "science_criticism_data.zip")
DATA_MANIFEST = j(config["data_dir"], "MANIFEST.md")

# Outputs of the supplementary-journal run (config_supplement.yaml)
SUPP_PAPER_METRICS_DENSITY_PLOTDATA = j(SUPP_FIG_DIR, "plotdata", "paper_metrics_density_plotdata.csv")
SUPP_PAPER_METRICS_DENSITY_2SAMPLE_TABLE = j(SUPP_FIG_DIR, "tables", "paper_metrics_density_test_2sample_table.txt")
SUPP_EMBEDDING_PLOTDATA = j(SUPP_FIG_DIR, "plotdata", "embedding_cocite_density_plot_plotdata.csv")
SUPP_MATCHED_METRIC_DENSITY = j(SUPP_DERIVED_DIR, "matched", "matched_papers_metricdensity_0.05impact_3year.csv")
SUPP_MATCHED_PAPERS = j(SUPP_DERIVED_DIR, "matched", "matched_papers_stage1_3delay_0.05impact_1year.csv")

# Outputs of notebooks/statistical-power-analysis.rmd, which is not part of
# the workflow (Supplementary Fig. 9 and Supplementary Table 24)
POWER_ANALYSIS_PLOTDATA = j(FIG_DIR, "plotdata", "statistical_power_analysis_plotdata.csv")
POWER_ANALYSIS_BAYES_FACTORS = j(TABLES_DIR, "bayes_factors.csv")

# Matching specifications reported in the robustness tables
PAPER_ROBUSTNESS_MATCHES = [
    j(DERIVED_DIR, "matched", f"matched_papers_stage1_{d}delay_{c}impact_{y}year.csv")
    for d, c, y in [(2, 0.05, 2), (3, 0.05, 2), (4, 0.05, 2), (3, 0.1, 2), (3, 0.15, 2), (3, 0.05, 1)]
]
AUTHOR_ROBUSTNESS_MATCHES = [
    j(DERIVED_DIR, "matched", f"matched_{a}_authors_{c}impact_{p}prod.csv")
    for a in ["first", "last"]
    for c, p in [(0.05, 0.15), (0.1, 0.15), (0.15, 0.15), (0.15, 0.05), (0.15, 0.1)]
]
METRIC_DENSITY_MATCHES = [
    j(DERIVED_DIR, "matched", "matched_papers_metricdensity_0.05impact_3year.csv"),
    j(DERIVED_DIR, "matched", "matched_papers_metricdensity_0.05impact_1year.csv"),
]

rule test_statistics:
    input:
        script = "scripts/statistics/compute_test_statistics.R",
        rank_plotdata = [PAPER_METRICS_DENSITY_PLOT_PLOTDATA, SUPP_PAPER_METRICS_DENSITY_PLOTDATA],
        embedding_plotdata = [EMBEDDING_COCITE_DENSITY_PLOT_PLOTDATA, SUPP_EMBEDDING_PLOTDATA],
        rank_matches = [METRIC_DENSITY_MATCHES[0], SUPP_MATCHED_METRIC_DENSITY],
        paper_matches = PAPER_ROBUSTNESS_MATCHES + [SUPP_MATCHED_PAPERS],
        author_matches = AUTHOR_ROBUSTNESS_MATCHES,
        annotations = LLM_ANNOTATIONS,
        ame = expand(PAPER_AUTHOR_DEMOGRAPHIC_AME_PLOTDATA, authorship = AUTHORSHIP)
    output: TEST_STATISTICS
    conda: "../envs/r-submission.yaml"
    shell: "Rscript {input.script} {output}"

rule bayes_factors:
    input:
        script = "scripts/statistics/compute_bayes_factors.R",
        rank_plotdata = [PAPER_METRICS_DENSITY_PLOT_PLOTDATA, SUPP_PAPER_METRICS_DENSITY_PLOTDATA],
        embedding_plotdata = [EMBEDDING_COCITE_DENSITY_PLOT_PLOTDATA, SUPP_EMBEDDING_PLOTDATA],
        rank_matches = [METRIC_DENSITY_MATCHES[0], SUPP_MATCHED_METRIC_DENSITY],
        paper_matches = [PAPER_ROBUSTNESS_MATCHES[-1], SUPP_MATCHED_PAPERS],
        author_matches = [m for m in AUTHOR_ROBUSTNESS_MATCHES if "0.15impact_0.15prod" in m],
        annotations = LLM_ANNOTATIONS,
        authors = AUTHOR_PROFILES,
        histories = CAREER_HISTORIES,
        ame_matches = METRIC_DENSITY_MATCHES[1],
        elite = ELITE_UNIVERSITIES
    output: BAYES_FACTORS_ALL
    conda: "../envs/r-submission.yaml"
    shell: "Rscript {input.script} {output}"

rule si_tables:
    input:
        script = "scripts/submission/build_si_tables.py",
        stats = TEST_STATISTICS,
        bayes = BAYES_FACTORS_ALL,
        main_2s = PAPER_METRICS_DENSITY_PLOT_TEST_2SAMPLE_TABLE,
        supp_2s = SUPP_PAPER_METRICS_DENSITY_2SAMPLE_TABLE,
        temporal = IMPACT_TEMPORAL_COMPARISON_PLOTDATA
    output: SI_TABLES
    params: out_dir = j(PAPER_DIR, "tables")
    conda: "../envs/python-submission.yaml"
    shell:
        "python {input.script} {input.stats} {input.bayes} "
        "{input.main_2s} {input.supp_2s} {input.temporal} {params.out_dir}"

rule supp_table_sources:
    input:
        script = "scripts/submission/supp_table_sources.py",
        annotations = MANUAL_ANNOTATIONS
    output:
        table3 = SUPP_TABLE3_SOURCE,
        table14 = SUPP_TABLE14_SOURCE
    conda: "../envs/python-submission.yaml"
    shell: "python {input.script} {input.annotations} {output.table3} {output.table14}"

rule main_figure_pdfs:
    input:
        script = "scripts/submission/render_main_figure_pdfs.R",
        # The figures' data and workflow versions, which must be up to date
        figures = [PAPER_METRICS_DENSITY_PLOT, MATCHED_COMPARISON_PLOT,
                   IMPACT_TEMPORAL_COMPARISON, EMBEDDING_COCITE_DENSITY_PLOT]
    output: MAIN_FIGURE_PDFS
    params: out_dir = j(PAPER_DIR, "figures")
    conda: "../envs/r-submission.yaml"
    shell: "Rscript {input.script} config.yaml {params.out_dir}"

rule source_data:
    input:
        script = "scripts/submission/build_source_data.py",
        plotdata = [
            PAPER_METRICS_DENSITY_PLOT_PLOTDATA, MATCHED_COMPARISON_PLOT_PLOTDATA,
            IMPACT_TEMPORAL_COMPARISON_PLOTDATA, EMBEDDING_COCITE_DENSITY_PLOT_PLOTDATA,
            IMPACT_LIKELIHOOD_SCATTER_PLOTDATA,
            expand(PAPER_AUTHOR_DEMOGRAPHIC_AME_PLOTDATA, authorship = AUTHORSHIP),
            FIELD_REPRESENTATION_PLOT_PLOTDATA, PAPER_NEWS_TWEET_PROPORTION_PLOTDATA,
            PAPER_TWEET_DISTRIBUTION_PLOTDATA, MATCHING_DIAGNOSTIC_IMPACT_PLOT_PLOTDATA,
            LETTER_ALTMETRIC_COMPARISON_PLOT_PLOTDATA, PAPER_COMPARISON_LAGTYPE_PLOT_PLOTDATA,
            POWER_ANALYSIS_PLOTDATA
        ],
        tables = [SUPP_TABLE3_SOURCE, SUPP_TABLE14_SOURCE, POWER_ANALYSIS_BAYES_FACTORS,
                  BAYES_FACTORS_ALL, TEST_STATISTICS]
    output:
        workbook = SOURCE_DATA,
        csvs = FIGURE_SOURCE_DATA_CSVS
    params: plotdata_dir = j(FIG_DIR, "plotdata")
    conda: "../envs/python-submission.yaml"
    shell:
        # The per-figure CSVs are copies of the main figures' plot data
        "python {input.script} {params.plotdata_dir} '{output.workbook}' && "
        "cp {PAPER_METRICS_DENSITY_PLOT_PLOTDATA} {output.csvs[0]} && "
        "cp {MATCHED_COMPARISON_PLOT_PLOTDATA} {output.csvs[1]} && "
        "cp {IMPACT_TEMPORAL_COMPARISON_PLOTDATA} {output.csvs[2]} && "
        "cp {EMBEDDING_COCITE_DENSITY_PLOT_PLOTDATA} {output.csvs[3]}"

rule data_export:
    input:
        script = "scripts/submission/export_data.py",
        # The data to be exported, for both the main and supplementary journals
        download = rules.download.input,
        match = rules.match.input,
        margins = rules.margins.input,
        embedding = rules.embedding.input,
        novelty = PAPER_NOVELTY_SCORES,
        annotations = [LLM_ANNOTATIONS, MANUAL_ANNOTATIONS],
        supplement = [SUPP_MATCHED_METRIC_DENSITY, SUPP_MATCHED_PAPERS, SUPP_EMBEDDING_PLOTDATA]
    output:
        archive = DATA_EXPORT,
        manifest = DATA_MANIFEST
    params: data_dir = config["data_dir"]
    conda: "../envs/python-submission.yaml"
    shell: "python {input.script} --data-dir {params.data_dir} --output {output.archive}"
