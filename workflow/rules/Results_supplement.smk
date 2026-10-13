rule plotdata_paper_comparison_filtered:
    input: 
        expand(
            rules.match_papers_for_impact_comparison.output,
            delay = 3,
            cite_tolerance = 0.05,
            year_tolerance = 1
        )
    params: LLM_ANNOTATIONS
    output:
        PAPER_IMPACT_COMPARISON_PLOTDATA_FILTERED
    conda: "../envs/r-conda.yaml"
    script: "../scripts/plotting/plotdata_paper_impact_comparison_filtered.R"