# Data for "Criticism in science targets highly cited papers but has limited consequence and reach"

This archive contains the data needed to reproduce the analyses in the paper and its Supplementary Information. The code is available at https://github.com/murrayds/science_criticism; it expects these files in a `data/` folder at the root of the repository.

The archive holds 243 data files (33.2 GB uncompressed), organized as follows:

- `raw/`: critical letters and targeted papers identified for this study, annotations of critical letters, and reference data.
- `downloaded/`: bibliographic data queried for the targeted papers, critical letters, citing papers, and authors.
- `derived/`: data computed from these sources and used directly in the analysis, including the matched samples.
- `supplement/`: the same data for the three supplementary journals.

## Sources and terms of use

- Bibliographic data are from the Microsoft Academic Graph (MAG), available under the Open Data Commons Attribution License (ODC-By); a snapshot is available on Zenodo (DOI 10.5281/zenodo.2593153).
- Citation links for Physical Review journals are derived from the 2020 American Physical Society (APS) citation dataset. The raw APS data are not included; they can be requested from the APS at https://journals.aps.org/datasets.
- Paper features, including altmetric counts, are from SciSciNet (DOI 10.6084/m9.figshare.c.6076908).
- University rankings are from the CWTS Leiden Ranking 2023 (https://www.leidenranking.com).
- The full texts of critical letters are protected by copyright and are not included; they are available from the respective publishers. Annotations of the letters are included with their identifiers.

Throughout, `Other APS` refers to Physical Review A through E, which are combined in the analysis. Paper and author identifiers are MAG identifiers unless a column name indicates otherwise.

## Critical letters and targeted papers

DOIs of critical letters and the papers they target, identified through bibliometric queries, web scraping, and manual efforts. Files for Geology, JCP, and EST cover the supplementary journals; the NEJM file covers a journal that was considered but not analyzed.

| File | Size |
|---|---|
| `raw/EST_letter_links.csv` | 12.9 KB |
| `raw/Geology_letter_links.csv` | 12.7 KB |
| `raw/JCP_letter_links.csv` | 7.4 KB |
| `raw/NEJM_letter_links.csv` | 223.9 KB |
| `raw/Nature_letter_links.csv` | 7.4 KB |
| `raw/PNAS_letter_links.csv` | 24.7 KB |
| `raw/PR-A_letter_links.csv` | 13.3 KB |
| `raw/PR-B_letter_links.csv` | 14.6 KB |
| `raw/PR-C_letter_links.csv` | 2.5 KB |
| `raw/PR-D_letter_links.csv` | 6.4 KB |
| `raw/PR-E_letter_links.csv` | 13.1 KB |
| `raw/PRL_letter_links.csv` | 64.4 KB |
| `raw/Science_letter_links.csv` | 19.1 KB |

Listings of Nature article types retrieved from the journal website, used to identify Matters Arising.

| File | Size |
|---|---|
| `raw/Nature_MR.csv` | 225.5 KB |
| `raw/Nature_OP.csv` | 53.0 KB |

## Annotations of critical letters

Manual annotations of critical letters (validity as criticism and presentation of new evidence), by DOI.

| File | Size |
|---|---|
| `raw/critical-letter_annotations.xlsx` | 16.8 KB |

Large language model annotations of critical letters (whether the letter is a valid instance of criticism, the type of critique, its level of interest, and the model's stated reasons), with letter and targeted-paper identifiers. The full text of the letters is not included.

| File | Size |
|---|---|
| `raw/letter_llm_annotated_data.csv` | 4.8 MB |

## Per-journal bibliographic data

Data for each journal queried from MAG, with citation links for Physical Review journals derived from the APS citation dataset: metadata of critical letters and targeted papers, paper citation impact, fields, citation trajectories of letters and targeted papers, and scite metrics.

| File | Size |
|---|---|
| `downloaded/EST/EST_letter_metadata.csv` | 11.8 KB |
| `downloaded/Geology/Geology_dual_cite_trajectories.csv` | 3.4 MB |
| `downloaded/Geology/Geology_fields.csv` | 348.3 KB |
| `downloaded/Geology/Geology_letter_metadata.csv` | 10.2 KB |
| `downloaded/Geology/Geology_paper_impact.csv` | 422.7 KB |
| `downloaded/Geology/Geology_scite_metrics.csv` | 262.8 KB |
| `downloaded/Nature/Nature_dual_cite_trajectories.csv` | 4.2 MB |
| `downloaded/Nature/Nature_fields.csv` | 3.1 MB |
| `downloaded/Nature/Nature_letter_metadata.csv` | 7.4 KB |
| `downloaded/Nature/Nature_paper_impact.csv` | 3.0 MB |
| `downloaded/Nature/Nature_scite_metrics.csv` | 2.4 MB |
| `downloaded/PNAS/PNAS_dual_cite_trajectories.csv` | 3.3 MB |
| `downloaded/PNAS/PNAS_fields.csv` | 4.1 MB |
| `downloaded/PNAS/PNAS_letter_metadata.csv` | 19.8 KB |
| `downloaded/PNAS/PNAS_paper_impact.csv` | 5.2 MB |
| `downloaded/PNAS/PNAS_scite_metrics.csv` | 3.2 MB |
| `downloaded/PR-A/PR-A_dual_cite_trajectories.csv` | 649.7 KB |
| `downloaded/PR-A/PR-A_fields.csv` | 2.7 MB |
| `downloaded/PR-A/PR-A_letter_metadata.csv` | 9.7 KB |
| `downloaded/PR-A/PR-A_paper_impact.csv` | 2.9 MB |
| `downloaded/PR-A/PR-A_scite_metrics.csv` | 2.2 MB |
| `downloaded/PR-B/PR-B_dual_cite_trajectories.csv` | 701.0 KB |
| `downloaded/PR-B/PR-B_fields.csv` | 5.8 MB |
| `downloaded/PR-B/PR-B_letter_metadata.csv` | 10.9 KB |
| `downloaded/PR-B/PR-B_paper_impact.csv` | 6.9 MB |
| `downloaded/PR-B/PR-B_scite_metrics.csv` | 5.0 MB |
| `downloaded/PR-C/PR-C_dual_cite_trajectories.csv` | 71.9 KB |
| `downloaded/PR-C/PR-C_fields.csv` | 1.2 MB |
| `downloaded/PR-C/PR-C_letter_metadata.csv` | 1.8 KB |
| `downloaded/PR-C/PR-C_paper_impact.csv` | 1.2 MB |
| `downloaded/PR-C/PR-C_scite_metrics.csv` | 953.6 KB |
| `downloaded/PR-D/PR-D_dual_cite_trajectories.csv` | 337.5 KB |
| `downloaded/PR-D/PR-D_fields.csv` | 3.4 MB |
| `downloaded/PR-D/PR-D_letter_metadata.csv` | 4.7 KB |
| `downloaded/PR-D/PR-D_paper_impact.csv` | 3.8 MB |
| `downloaded/PR-D/PR-D_scite_metrics.csv` | 2.7 MB |
| `downloaded/PR-E/PR-E_dual_cite_trajectories.csv` | 835.6 KB |
| `downloaded/PR-E/PR-E_fields.csv` | 2.6 MB |
| `downloaded/PR-E/PR-E_letter_metadata.csv` | 9.7 KB |
| `downloaded/PR-E/PR-E_paper_impact.csv` | 2.8 MB |
| `downloaded/PR-E/PR-E_scite_metrics.csv` | 2.2 MB |
| `downloaded/PRL/PRL_dual_cite_trajectories.csv` | 6.6 MB |
| `downloaded/PRL/PRL_fields.csv` | 3.7 MB |
| `downloaded/PRL/PRL_letter_metadata.csv` | 41.3 KB |
| `downloaded/PRL/PRL_paper_impact.csv` | 4.5 MB |
| `downloaded/PRL/PRL_scite_metrics.csv` | 3.3 MB |
| `downloaded/Science/Science_dual_cite_trajectories.csv` | 8.5 MB |
| `downloaded/Science/Science_fields.csv` | 3.4 MB |
| `downloaded/Science/Science_letter_metadata.csv` | 17.0 KB |
| `downloaded/Science/Science_paper_impact.csv` | 2.8 MB |
| `downloaded/Science/Science_scite_metrics.csv` | 3.2 MB |

## Citing papers

Titles of papers citing the targeted papers and critical letters, used to identify replies and to compute title embeddings.

| File | Size |
|---|---|
| `downloaded/citing_Geology_paper_titles.csv` | 3.7 MB |
| `downloaded/citing_Nature_paper_titles.csv` | 13.8 MB |
| `downloaded/citing_PNAS_paper_titles.csv` | 12.4 MB |
| `downloaded/citing_PR-A_paper_titles.csv` | 2.1 MB |
| `downloaded/citing_PR-B_paper_titles.csv` | 2.6 MB |
| `downloaded/citing_PR-C_paper_titles.csv` | 276.6 KB |
| `downloaded/citing_PR-D_paper_titles.csv` | 855.9 KB |
| `downloaded/citing_PR-E_paper_titles.csv` | 2.3 MB |
| `downloaded/citing_PRL_paper_titles.csv` | 20.9 MB |
| `downloaded/citing_Science_paper_titles.csv` | 28.7 MB |

## Authors

Author profiles and career histories from MAG, used for author matching and author characteristics.

| File | Size |
|---|---|
| `downloaded/author_profiles.csv` | 89.9 MB |
| `downloaded/career_histories.csv` | 2.2 GB |

## Paper fields and features

Fields of citing and referenced papers, used for the diversity measures, and SciSciNet paper features.

| File | Size |
|---|---|
| `downloaded/paper_field_cites.csv` | 958.8 MB |
| `downloaded/paper_field_refs.csv` | 1.2 GB |
| `downloaded/sciscinet_features.csv` | 31.3 MB |

## Bibliographic data for novelty

Yearly journal reference lists used to compute the novelty (atypicality) measure.

| File | Size |
|---|---|
| `downloaded/journal_refs/journal_refs_2000.csv` | 340.2 MB |
| `downloaded/journal_refs/journal_refs_2001.csv` | 367.0 MB |
| `downloaded/journal_refs/journal_refs_2002.csv` | 400.0 MB |
| `downloaded/journal_refs/journal_refs_2003.csv` | 437.7 MB |
| `downloaded/journal_refs/journal_refs_2004.csv` | 479.7 MB |
| `downloaded/journal_refs/journal_refs_2005.csv` | 537.2 MB |
| `downloaded/journal_refs/journal_refs_2006.csv` | 595.0 MB |
| `downloaded/journal_refs/journal_refs_2007.csv` | 645.8 MB |
| `downloaded/journal_refs/journal_refs_2008.csv` | 713.8 MB |
| `downloaded/journal_refs/journal_refs_2009.csv` | 789.9 MB |
| `downloaded/journal_refs/journal_refs_2010.csv` | 830.4 MB |
| `downloaded/journal_refs/journal_refs_2011.csv` | 914.7 MB |
| `downloaded/journal_refs/journal_refs_2012.csv` | 1004.6 MB |
| `downloaded/journal_refs/journal_refs_2013.csv` | 1.1 GB |
| `downloaded/journal_refs/journal_refs_2014.csv` | 1.1 GB |
| `downloaded/journal_refs/journal_refs_2015.csv` | 1.2 GB |
| `downloaded/journal_refs/journal_refs_2016.csv` | 1.3 GB |
| `downloaded/journal_refs/journal_refs_2017.csv` | 1.4 GB |
| `downloaded/journal_refs/journal_refs_2018.csv` | 1.3 GB |
| `downloaded/journal_refs/journal_refs_2019.csv` | 1.5 GB |
| `downloaded/journal_refs/target_journal_refs.csv` | 205.9 MB |

## Reference data

Hierarchy of Microsoft Academic Graph (MAG) field categories.

| File | Size |
|---|---|
| `raw/mag_field_hierarchy.csv` | 16.8 MB |

Paper-level features from SciSciNet: novelty, counts of tweets and news mentions, and team size.

| File | Size |
|---|---|
| `raw/paper_features.csv` | 7.4 MB |

## University rankings

The CWTS Leiden Ranking 2023, its mapping to GRID identifiers, and the derived list of top-ranked universities used for author affiliation.

| File | Size |
|---|---|
| `raw/CWTS Leiden Ranking 2023.xlsx` | 219.7 MB |
| `raw/elite_university_list.csv` | 34.2 KB |
| `raw/leiden_rankings_grid_ids.csv` | 2.9 KB |

## Analysis data

Aggregated inputs to the analysis: critical letters and targeted papers, non-targeted papers, fields, paper titles, citation trajectories, and scite metrics.

| File | Size |
|---|---|
| `derived/agg/agg_dual_cite_trajectories.csv` | 31.0 MB |
| `derived/agg/agg_fields.csv` | 50.8 MB |
| `derived/agg/agg_letters.csv` | 324.3 KB |
| `derived/agg/agg_nonletters.csv` | 29.1 MB |
| `derived/agg/agg_paper_titles.csv` | 88.7 MB |
| `derived/agg/agg_scite_metrics.csv` | 25.5 MB |

Similarity between the titles of citing papers and the targeted paper, computed with SPECTER embeddings.

| File | Size |
|---|---|
| `derived/embedding/Geology_title_embedding_similarities.csv` | 692.5 KB |
| `derived/embedding/Nature_title_embedding_similarities.csv` | 3.1 MB |
| `derived/embedding/PNAS_title_embedding_similarities.csv` | 2.6 MB |
| `derived/embedding/PR-A_title_embedding_similarities.csv` | 506.4 KB |
| `derived/embedding/PR-B_title_embedding_similarities.csv` | 576.7 KB |
| `derived/embedding/PR-C_title_embedding_similarities.csv` | 67.7 KB |
| `derived/embedding/PR-D_title_embedding_similarities.csv` | 228.0 KB |
| `derived/embedding/PR-E_title_embedding_similarities.csv` | 565.9 KB |
| `derived/embedding/PRL_title_embedding_similarities.csv` | 5.0 MB |
| `derived/embedding/Science_title_embedding_similarities.csv` | 6.4 MB |
| `derived/embedding/agg_title_embedding_similarities.csv` | 19.6 MB |

Average marginal effects of author characteristics on the likelihood of receiving a critical letter.

| File | Size |
|---|---|
| `derived/margins/margins_firstauthor.csv` | 2.2 KB |
| `derived/margins/margins_firstauthor_gender.csv` | 2.2 KB |
| `derived/margins/margins_lastauthor.csv` | 2.2 KB |
| `derived/margins/margins_lastauthor_gender.csv` | 2.2 KB |

Journal-pair z-scores and paper-level novelty scores.

| File | Size |
|---|---|
| `derived/novelty/agg_journal_zscores.pickle` | 3.0 GB |
| `derived/novelty/journal_z_scores.csv` | 117.4 MB |
| `derived/novelty/paper_zscores.csv` | 12.8 MB |

## Matched samples

Matched treatment and control papers and authors for each matching specification, and aggregated matching diagnostics. File names give the matching parameters (e.g. `3delay_0.05impact_1year` is a 3-year delay, 5% citation-impact tolerance, and 1-year publication-year tolerance).

| File | Size |
|---|---|
| `derived/matched/agg_author_match_citations_diagnostics.csv` | 7.9 KB |
| `derived/matched/agg_author_match_prod_diagnostics.csv` | 8.0 KB |
| `derived/matched/agg_paper_impact_match_diagnostics.csv` | 7.8 KB |
| `derived/matched/matched_first_authors_0.05impact_0.05prod.csv` | 372.8 KB |
| `derived/matched/matched_first_authors_0.05impact_0.15prod.csv` | 510.1 KB |
| `derived/matched/matched_first_authors_0.05impact_0.1prod.csv` | 463.2 KB |
| `derived/matched/matched_first_authors_0.15impact_0.05prod.csv` | 506.6 KB |
| `derived/matched/matched_first_authors_0.15impact_0.15prod.csv` | 589.1 KB |
| `derived/matched/matched_first_authors_0.15impact_0.1prod.csv` | 566.3 KB |
| `derived/matched/matched_first_authors_0.15impact_1.0prod.csv` | 280.1 KB |
| `derived/matched/matched_first_authors_0.1impact_0.05prod.csv` | 470.6 KB |
| `derived/matched/matched_first_authors_0.1impact_0.15prod.csv` | 566.5 KB |
| `derived/matched/matched_first_authors_0.1impact_0.1prod.csv` | 540.2 KB |
| `derived/matched/matched_last_authors_0.05impact_0.05prod.csv` | 676.3 KB |
| `derived/matched/matched_last_authors_0.05impact_0.15prod.csv` | 842.6 KB |
| `derived/matched/matched_last_authors_0.05impact_0.1prod.csv` | 793.8 KB |
| `derived/matched/matched_last_authors_0.15impact_0.05prod.csv` | 834.6 KB |
| `derived/matched/matched_last_authors_0.15impact_0.15prod.csv` | 932.8 KB |
| `derived/matched/matched_last_authors_0.15impact_0.1prod.csv` | 904.2 KB |
| `derived/matched/matched_last_authors_0.15impact_1.0prod.csv` | 421.3 KB |
| `derived/matched/matched_last_authors_0.1impact_0.05prod.csv` | 787.8 KB |
| `derived/matched/matched_last_authors_0.1impact_0.15prod.csv` | 909.6 KB |
| `derived/matched/matched_last_authors_0.1impact_0.1prod.csv` | 871.6 KB |
| `derived/matched/matched_papers_metricdensity_0.05impact_1year.csv` | 380.1 KB |
| `derived/matched/matched_papers_metricdensity_0.05impact_3year.csv` | 395.9 KB |
| `derived/matched/matched_papers_stage1_2delay_0.05impact_1year.csv` | 410.2 KB |
| `derived/matched/matched_papers_stage1_2delay_0.05impact_2year.csv` | 425.5 KB |
| `derived/matched/matched_papers_stage1_2delay_0.05impact_3year.csv` | 319.7 KB |
| `derived/matched/matched_papers_stage1_2delay_0.15impact_1year.csv` | 437.8 KB |
| `derived/matched/matched_papers_stage1_2delay_0.15impact_2year.csv` | 441.8 KB |
| `derived/matched/matched_papers_stage1_2delay_0.15impact_3year.csv` | 332.5 KB |
| `derived/matched/matched_papers_stage1_2delay_0.1impact_1year.csv` | 424.9 KB |
| `derived/matched/matched_papers_stage1_2delay_0.1impact_2year.csv` | 438.0 KB |
| `derived/matched/matched_papers_stage1_2delay_0.1impact_3year.csv` | 329.6 KB |
| `derived/matched/matched_papers_stage1_3delay_0.05impact_1year.csv` | 389.7 KB |
| `derived/matched/matched_papers_stage1_3delay_0.05impact_2year.csv` | 427.8 KB |
| `derived/matched/matched_papers_stage1_3delay_0.05impact_3year.csv` | 296.3 KB |
| `derived/matched/matched_papers_stage1_3delay_0.075impact_1year.csv` | 432.0 KB |
| `derived/matched/matched_papers_stage1_3delay_0.075impact_2year.csv` | 451.9 KB |
| `derived/matched/matched_papers_stage1_3delay_0.15impact_1year.csv` | 413.4 KB |
| `derived/matched/matched_papers_stage1_3delay_0.15impact_2year.csv` | 421.8 KB |
| `derived/matched/matched_papers_stage1_3delay_0.15impact_3year.csv` | 313.9 KB |
| `derived/matched/matched_papers_stage1_3delay_0.1impact_1year.csv` | 405.5 KB |
| `derived/matched/matched_papers_stage1_3delay_0.1impact_2year.csv` | 418.2 KB |
| `derived/matched/matched_papers_stage1_3delay_0.1impact_3year.csv` | 309.5 KB |
| `derived/matched/matched_papers_stage1_3delay_5mincite_0.1impact_1year.csv` | 315.8 KB |
| `derived/matched/matched_papers_stage1_3delay_5mincite_0.1impact_2year.csv` | 320.0 KB |
| `derived/matched/matched_papers_stage1_4delay_0.05impact_1year.csv` | 373.2 KB |
| `derived/matched/matched_papers_stage1_4delay_0.05impact_2year.csv` | 383.5 KB |
| `derived/matched/matched_papers_stage1_4delay_0.05impact_3year.csv` | 279.5 KB |
| `derived/matched/matched_papers_stage1_4delay_0.15impact_1year.csv` | 391.0 KB |
| `derived/matched/matched_papers_stage1_4delay_0.15impact_2year.csv` | 402.4 KB |
| `derived/matched/matched_papers_stage1_4delay_0.15impact_3year.csv` | 294.9 KB |
| `derived/matched/matched_papers_stage1_4delay_0.1impact_1year.csv` | 385.6 KB |
| `derived/matched/matched_papers_stage1_4delay_0.1impact_2year.csv` | 396.5 KB |
| `derived/matched/matched_papers_stage1_4delay_0.1impact_3year.csv` | 289.7 KB |

## Supplementary journals

Data for the supplementary analysis of Geology, the Journal of Chemical Physics (JCP), and Environmental Science & Technology (EST), with the same structure as the main `downloaded/` and `derived/` folders.

| File | Size |
|---|---|
| `supplement/derived/agg/agg_dual_cite_trajectories.csv` | 8.5 MB |
| `supplement/derived/agg/agg_fields.csv` | 9.2 MB |
| `supplement/derived/agg/agg_letters.csv` | 66.9 KB |
| `supplement/derived/agg/agg_nonletters.csv` | 4.8 MB |
| `supplement/derived/agg/agg_paper_titles.csv` | 14.4 MB |
| `supplement/derived/agg/agg_scite_metrics.csv` | 3.3 MB |
| `supplement/derived/embedding/EST_title_embedding_similarities.csv` | 1.5 MB |
| `supplement/derived/embedding/Geology_title_embedding_similarities.csv` | 692.5 KB |
| `supplement/derived/embedding/JCP_title_embedding_similarities.csv` | 429.7 KB |
| `supplement/derived/embedding/agg_title_embedding_similarities.csv` | 2.6 MB |
| `supplement/derived/margins/margins_firstauthor.csv` | 1.3 KB |
| `supplement/derived/margins/margins_lastauthor.csv` | 1.3 KB |
| `supplement/derived/matched/agg_author_match_citations_diagnostics.csv` | 630 B |
| `supplement/derived/matched/agg_author_match_prod_diagnostics.csv` | 635 B |
| `supplement/derived/matched/agg_paper_impact_match_diagnostics.csv` | 387 B |
| `supplement/derived/matched/matched_first_authors_0.05impact_0.1prod.csv` | 46.5 KB |
| `supplement/derived/matched/matched_first_authors_0.1impact_0.1prod.csv` | 71.8 KB |
| `supplement/derived/matched/matched_last_authors_0.1impact_0.1prod.csv` | 126.5 KB |
| `supplement/derived/matched/matched_papers_metricdensity_0.05impact_1year.csv` | 84.0 KB |
| `supplement/derived/matched/matched_papers_metricdensity_0.05impact_3year.csv` | 83.1 KB |
| `supplement/derived/matched/matched_papers_stage1_3delay_0.05impact_1year.csv` | 62.8 KB |
| `supplement/derived/matched/matched_papers_stage1_3delay_0.05impact_2year.csv` | 66.5 KB |
| `supplement/derived/matched/matched_papers_stage1_3delay_0.1impact_2year.csv` | 66.0 KB |
| `supplement/derived/novelty/agg_journal_zscores.pickle` | 3.0 GB |
| `supplement/derived/novelty/paper_zscores.csv` | 3.8 MB |
| `supplement/downloaded/EST/EST_dual_cite_trajectories.csv` | 4.4 MB |
| `supplement/downloaded/EST/EST_fields.csv` | 2.1 MB |
| `supplement/downloaded/EST/EST_letter_metadata.csv` | 11.8 KB |
| `supplement/downloaded/EST/EST_paper_impact.csv` | 1.9 MB |
| `supplement/downloaded/EST/EST_scite_metrics.csv` | 1.1 MB |
| `supplement/downloaded/Geology/Geology_dual_cite_trajectories.csv` | 3.4 MB |
| `supplement/downloaded/Geology/Geology_fields.csv` | 348.3 KB |
| `supplement/downloaded/Geology/Geology_letter_metadata.csv` | 10.2 KB |
| `supplement/downloaded/Geology/Geology_paper_impact.csv` | 422.7 KB |
| `supplement/downloaded/Geology/Geology_scite_metrics.csv` | 262.8 KB |
| `supplement/downloaded/JCP/JCP_dual_cite_trajectories.csv` | 744.1 KB |
| `supplement/downloaded/JCP/JCP_fields.csv` | 2.9 MB |
| `supplement/downloaded/JCP/JCP_letter_metadata.csv` | 9.3 KB |
| `supplement/downloaded/JCP/JCP_paper_impact.csv` | 3.1 MB |
| `supplement/downloaded/JCP/JCP_scite_metrics.csv` | 1.9 MB |
| `supplement/downloaded/author_profiles.csv` | 12.7 MB |
| `supplement/downloaded/career_histories.csv` | 387.3 MB |
| `supplement/downloaded/citing_EST_paper_titles.csv` | 8.6 MB |
| `supplement/downloaded/citing_Geology_paper_titles.csv` | 3.7 MB |
| `supplement/downloaded/citing_JCP_paper_titles.csv` | 2.1 MB |
| `supplement/downloaded/journal_refs/journal_refs_2001.csv` | 367.1 MB |
| `supplement/downloaded/journal_refs/journal_refs_2002.csv` | 400.1 MB |
| `supplement/downloaded/journal_refs/journal_refs_2012.csv` | 1004.8 MB |
| `supplement/downloaded/journal_refs/journal_refs_2013.csv` | 1.1 GB |
| `supplement/downloaded/journal_refs/journal_refs_2016.csv` | 1.3 GB |
| `supplement/downloaded/journal_refs/target_journal_refs.csv` | 62.1 MB |
| `supplement/downloaded/paper_field_cites.csv` | 96.3 MB |
| `supplement/downloaded/paper_field_refs.csv` | 290.8 MB |
| `supplement/downloaded/sciscinet_features.csv` | 5.0 MB |
