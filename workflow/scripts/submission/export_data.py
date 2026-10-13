"""Package the shareable data into a zip archive for public release.

Run by the `data_export` rule (rules/Submission.smk). It selects the files
in `data/` that can be shared, writes a public-facing `data/MANIFEST.md`
describing them, and writes both to a zip archive with a top-level `data/`
folder, mirroring the layout the workflow expects.

Excluded from the export:
  - `raw/letter_content/`: full texts of critical letters, which are protected
    by copyright;
  - the `full_text` column of `raw/letter_llm_annotated_data.csv` (the rest of
    the file, including letter and paper identifiers, is exported);
  - per-journal intermediate matching files (`derived/matched/_*`), which are
    combined into the files the analysis uses;
  - zip archives, `README.md` (a template), and system files.

Usage, run from the `workflow/` directory (normally via Snakemake):
  python scripts/submission/export_data.py [--data-dir DIR] [--output PATH] [--manifest-only]
Defaults: the repository's `data/` folder, and `science_criticism_data.zip` next to it.
"""
import argparse
import csv
import io
import os
import re
import sys
import zipfile

# Default data folder: <repository>/data, three levels above this script
DATA = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data"))

# Files that are never exported
EXCLUDE = [
    r"^raw/letter_content/",
    r"^(supplement/)?derived/matched/_",
    r"(^|/)\.DS_Store$",
    r"\.zip$",
    r"^README\.md$",
    r"^MANIFEST\.md$",
]

# Files exported with a column removed: path -> column
DROP_COLUMN = {"raw/letter_llm_annotated_data.csv": "full_text"}

V = r"(Nature|Science|PNAS|PRL|PR-[A-E]|Geology|EST|JCP|NEJM)"
# (pattern, section, description); the first match applies
GROUPS = [
    (r"^raw/letter_llm_annotated_data\.csv$", "Annotations of critical letters",
     "Large language model annotations of critical letters (whether the letter is a valid instance of criticism, the type of critique, its level of interest, and the model's stated reasons), with letter and targeted-paper identifiers. The full text of the letters is not included."),
    (r"^raw/critical-letter_annotations\.xlsx$", "Annotations of critical letters",
     "Manual annotations of critical letters (validity as criticism and presentation of new evidence), by DOI."),
    (rf"^raw/{V}_letter_links\.csv$", "Critical letters and targeted papers",
     "DOIs of critical letters and the papers they target, identified through bibliometric queries, web scraping, and manual efforts. Files for Geology, JCP, and EST cover the supplementary journals; the NEJM file covers a journal that was considered but not analyzed."),
    (r"^raw/Nature_(MR|OP)\.csv$", "Critical letters and targeted papers",
     "Listings of Nature article types retrieved from the journal website, used to identify Matters Arising."),
    (r"^raw/(CWTS Leiden Ranking 2023\.xlsx|leiden_rankings_grid_ids\.csv|elite_university_list\.csv)$", "University rankings",
     "The CWTS Leiden Ranking 2023, its mapping to GRID identifiers, and the derived list of top-ranked universities used for author affiliation."),
    (r"^raw/mag_field_hierarchy\.csv$", "Reference data",
     "Hierarchy of Microsoft Academic Graph (MAG) field categories."),
    (r"^raw/paper_features\.csv$", "Reference data",
     "Paper-level features from SciSciNet: novelty, counts of tweets and news mentions, and team size."),
    (rf"^downloaded/{V}/", "Per-journal bibliographic data",
     "Data for each journal queried from MAG, with citation links for Physical Review journals derived from the APS citation dataset: metadata of critical letters and targeted papers, paper citation impact, fields, citation trajectories of letters and targeted papers, and scite metrics."),
    (r"^downloaded/journal_refs/", "Bibliographic data for novelty",
     "Yearly journal reference lists used to compute the novelty (atypicality) measure."),
    (r"^downloaded/citing_.*_paper_titles\.csv$", "Citing papers",
     "Titles of papers citing the targeted papers and critical letters, used to identify replies and to compute title embeddings."),
    (r"^downloaded/(author_profiles|career_histories)\.csv$", "Authors",
     "Author profiles and career histories from MAG, used for author matching and author characteristics."),
    (r"^downloaded/(paper_field_cites|paper_field_refs|sciscinet_features)\.csv$", "Paper fields and features",
     "Fields of citing and referenced papers, used for the diversity measures, and SciSciNet paper features."),
    (r"^derived/agg/", "Analysis data",
     "Aggregated inputs to the analysis: critical letters and targeted papers, non-targeted papers, fields, paper titles, citation trajectories, and scite metrics."),
    (r"^derived/embedding/", "Analysis data",
     "Similarity between the titles of citing papers and the targeted paper, computed with SPECTER embeddings."),
    (r"^derived/margins/", "Analysis data",
     "Average marginal effects of author characteristics on the likelihood of receiving a critical letter."),
    (r"^derived/novelty/", "Analysis data",
     "Journal-pair z-scores and paper-level novelty scores."),
    (r"^derived/matched/", "Matched samples",
     "Matched treatment and control papers and authors for each matching specification, and aggregated matching diagnostics. File names give the matching parameters (e.g. `3delay_0.05impact_1year` is a 3-year delay, 5% citation-impact tolerance, and 1-year publication-year tolerance)."),
    (r"^supplement/", "Supplementary journals",
     "Data for the supplementary analysis of Geology, the Journal of Chemical Physics (JCP), and Environmental Science & Technology (EST), with the same structure as the main `downloaded/` and `derived/` folders."),
]

SECTIONS = [
    "Critical letters and targeted papers",
    "Annotations of critical letters",
    "Per-journal bibliographic data",
    "Citing papers",
    "Authors",
    "Paper fields and features",
    "Bibliographic data for novelty",
    "Reference data",
    "University rankings",
    "Analysis data",
    "Matched samples",
    "Supplementary journals",
]


def collect():
    files = []
    for d, _, fs in os.walk(DATA):
        for f in fs:
            rel = os.path.relpath(os.path.join(d, f), DATA).replace(os.sep, "/")
            if any(re.search(p, rel) for p in EXCLUDE):
                continue
            files.append(rel)
    return sorted(files)


def describe(rel):
    for pat, section, desc in GROUPS:
        if re.search(pat, rel):
            return section, desc
    sys.exit(f"No description for {rel}; add it to GROUPS before exporting")


def human(n):
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def write_manifest(files):
    by_section = {s: {} for s in SECTIONS}
    for rel in files:
        section, desc = describe(rel)
        by_section[section].setdefault(desc, []).append(rel)
    total = sum(os.path.getsize(os.path.join(DATA, f)) for f in files)

    L = [
        "# Data for \"Criticism in science targets highly cited papers but has limited consequence and reach\"",
        "",
        "This archive contains the data needed to reproduce the analyses in the paper and its Supplementary Information. "
        "The code is available at https://github.com/murrayds/science_criticism; it expects these files in a `data/` folder at the root of the repository.",
        "",
        f"The archive holds {len(files)} data files ({human(total)} uncompressed), organized as follows:",
        "",
        "- `raw/`: critical letters and targeted papers identified for this study, annotations of critical letters, and reference data.",
        "- `downloaded/`: bibliographic data queried for the targeted papers, critical letters, citing papers, and authors.",
        "- `derived/`: data computed from these sources and used directly in the analysis, including the matched samples.",
        "- `supplement/`: the same data for the three supplementary journals.",
        "",
        "## Sources and terms of use",
        "",
        "- Bibliographic data are from the Microsoft Academic Graph (MAG), available under the Open Data Commons Attribution License (ODC-By); a snapshot is available on Zenodo (DOI 10.5281/zenodo.2593153).",
        "- Citation links for Physical Review journals are derived from the 2020 American Physical Society (APS) citation dataset. The raw APS data are not included; they can be requested from the APS at https://journals.aps.org/datasets.",
        "- Paper features, including altmetric counts, are from SciSciNet (DOI 10.6084/m9.figshare.c.6076908).",
        "- University rankings are from the CWTS Leiden Ranking 2023 (https://www.leidenranking.com).",
        "- The full texts of critical letters are protected by copyright and are not included; they are available from the respective publishers. Annotations of the letters are included with their identifiers.",
        "",
        "Throughout, `Other APS` refers to Physical Review A through E, which are combined in the analysis. Paper and author identifiers are MAG identifiers unless a column name indicates otherwise.",
        "",
    ]
    for section in SECTIONS:
        groups = by_section[section]
        if not groups:
            continue
        L += [f"## {section}", ""]
        for desc, fs in groups.items():
            L += [desc, "", "| File | Size |", "|---|---|"]
            for f in fs:
                L.append(f"| `{f}` | {human(os.path.getsize(os.path.join(DATA, f)))} |")
            L.append("")
    path = os.path.join(DATA, "MANIFEST.md")
    with open(path, "w") as fh:
        fh.write("\n".join(L))
    print(f"Wrote {path} ({len(files)} files, {human(total)})")


def without_column(path, column):
    csv.field_size_limit(sys.maxsize)
    out = io.StringIO()
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fields = [c for c in reader.fieldnames if c != column]
        writer = csv.DictWriter(out, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in reader:
            row.pop(column, None)
            writer.writerow(row)
    return out.getvalue()


def write_zip(files, output):
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as z:
        z.write(os.path.join(DATA, "MANIFEST.md"), "data/MANIFEST.md")
        for i, rel in enumerate(files, 1):
            src = os.path.join(DATA, rel)
            if rel in DROP_COLUMN:
                z.writestr(f"data/{rel}", without_column(src, DROP_COLUMN[rel]))
            else:
                z.write(src, f"data/{rel}")
            if i % 25 == 0 or i == len(files):
                print(f"  {i}/{len(files)} files", flush=True)
    print(f"Wrote {output}")


def main():
    global DATA
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--data-dir", default=DATA)
    parser.add_argument("--output", default=None,
                        help="Defaults to science_criticism_data.zip next to the data folder")
    parser.add_argument("--manifest-only", action="store_true",
                        help="Write data/MANIFEST.md without building the archive")
    args = parser.parse_args()
    DATA = os.path.abspath(args.data_dir)
    if args.output is None:
        args.output = os.path.join(DATA, "..", "science_criticism_data.zip")

    files = collect()
    for rel in DROP_COLUMN:
        if rel not in files:
            sys.exit(f"Expected file is missing: {rel}")
    write_manifest(files)
    if not args.manifest_only:
        write_zip(files, os.path.abspath(args.output))


if __name__ == "__main__":
    main()
