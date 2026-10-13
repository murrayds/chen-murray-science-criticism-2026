"""Write the bodies of the Supplementary Information statistics tables.

Run by the `si_tables` rule (rules/Submission.smk). For each statistics table
in the Supplementary Information, it writes the table body (the tabular
environment, with any resizing) to a separate LaTeX file, which `supp.tex`
includes with \\input. Captions and labels stay in `supp.tex`.

The values come from the full test statistics (`compute_test_statistics.R`),
the Bayes factors (`compute_bayes_factors.R`), and, for the mean ranks of
targeted and matched papers in the two-sample Kolmogorov-Smirnov tables, the
tables written by the workflow's `plot_paper_metrics_density.R`.

The number of papers behind each point of Fig. 3 comes from that figure's
plot data.

Usage, run from the `workflow/` directory (normally via Snakemake):
    python scripts/submission/build_si_tables.py TEST_STATS BAYES_FACTORS \\
        MAIN_2S_TABLE SUPP_2S_TABLE TEMPORAL_PLOTDATA OUTPUT_DIR
"""
import csv
import os
import sys

VENUES = ["Nature", "Science", "PNAS", "PRL", "Other APS"]
SUPP_VENUES = ["Geology", "JCP", "EST"]
METRICS = ["Citations", "Ref. Diversity", "Cite. Diversity", "Novelty"]

# Output file names, keyed by the label of the table in supp.tex
FILES = {
    "si:table:paper-features-1sKS": "ks_one_sample.tex",
    "si:table:paper-features-2sKS": "ks_two_sample.tex",
    "si:table:embedding-tests": "ks_embedding.tex",
    "si:tab:paper-matched-ttest": "ttest_paper_robustness.tex",
    "si:tab:authors-matched-productivity-ttest": "ttest_author_productivity_robustness.tex",
    "si:tab:authors-matched-impact-ttest": "ttest_author_citations_robustness.tex",
    "si:table:density-tests_1ks_extra": "ks_one_sample_supplementary.tex",
    "si:table:density_tests_2ks_extra": "ks_two_sample_supplementary.tex",
    "si:table:embedding_tests_extra": "ks_embedding_supplementary.tex",
    "si:table:high-interest-analysis": "ttest_high_interest.tex",
    "si:table:aps-journal-ttests": "ttest_aps_journals.tex",
    "si:tab:wilcoxon": "ttest_wilcoxon_full.tex",
    "si:tab:ame": "ame.tex",
    "si:tab:visibility-n": "visibility_n.tex",
}


def fp(p):
    p = float(p)
    return "$<$0.001" if p < 0.001 else f"{p:.3f}"


def fbf(x):
    x = float(x)
    if x < 0.01:
        return "$<$0.01"
    return f"{x:.2f}" if x < 1 else f"{x:.1f}"


def fnum(x, d=3):
    x = float(x)
    if x != 0 and abs(x) < 0.5 * 10 ** -d:
        return f"{x:.1g}".replace("e-05", "e-5")
    return f"{x:.{d}f}"


def ci(lo, hi, d=3, scale=1):
    return f"[{fnum(float(lo) * scale, d)}, {fnum(float(hi) * scale, d)}]"


def main(test_stats, bayes_factors, main_2s, supp_2s, temporal_plotdata, out_dir):
    T = list(csv.DictReader(open(test_stats)))
    B = list(csv.DictReader(open(bayes_factors)))

    def row(analysis, venue, comparison, test, spec="main"):
        m = [r for r in T if r["analysis"] == analysis and r["venue"] == venue
             and r["comparison"] == comparison and r["test"].startswith(test)
             and r["spec"] == spec]
        assert len(m) == 1, (analysis, venue, comparison, test, spec, len(m))
        return m[0]

    def bf(analysis, venue, comparison):
        m = [r for r in B if r["analysis"] == analysis and r["venue"] == venue
             and r["comparison"] == comparison]
        assert len(m) == 1, (analysis, venue, comparison, len(m))
        return fbf(m[0]["BF01"])

    # Mean ranks of targeted and matched papers from the workflow's 2s KS tables
    def mean_ranks(path):
        out = {}
        for line in open(path):
            cells = [c.strip() for c in line.replace("\\\\", "").split("&")]
            if len(cells) == 7 and cells[0] != "Metric":
                out[(cells[0], cells[1])] = (cells[3], cells[4])
        return out

    bodies = {}

    def ks1(analysis, venues, metric_key):
        lines = ["\\begin{tabular}{llrrrrrr}", "  \\toprule",
                 "Metric & Venue & N & $D$ & P Value & Mean Rank & 95\\% CI & $BF_{01}$ \\\\ ",
                 "  \\midrule"]
        for m in METRICS:
            for v in venues:
                key = metric_key.get(m, m)
                r = row(analysis, v, key, "1s")
                lines.append(
                    f"  {m} & {v} & {int(r['n'])} & {float(r['statistic']):.4f} & {fp(r['p'])} & "
                    f"{float(r['effect']) * 100:.1f} & {ci(r['ci_low'], r['ci_high'], 1, 100)} & "
                    f"{bf(analysis, v, key)} \\\\ ")
        lines += ["   \\bottomrule", "\\end{tabular}", ""]
        return "\n".join(lines)

    def ks2(analysis, venues, ranks):
        lines = ["\\resizebox{\\textwidth}{!}{%", "\\begin{tabular}{llrrrrrrrr}", "  \\toprule",
                 "Metric & Venue & N (pairs) & Mean Rank (Criticism) & Mean Rank (¬Criticism) & $D$ & P Value & $\\Delta\\mu_{rank}$ & 95\\% CI & $BF_{01}$ \\\\ ",
                 "  \\midrule"]
        for m in METRICS[1:]:
            for v in venues:
                r = row(analysis, v, m, "2s")
                a, b = ranks[(m, v)]
                lines.append(
                    f"  {m} & {v} & {int(r['n'])} & {a} & {b} & {float(r['statistic']):.4f} & {fp(r['p'])} & "
                    f"{float(r['effect']) * 100:.1f} & {ci(r['ci_low'], r['ci_high'], 1, 100)} & "
                    f"{bf(analysis, v, m)} \\\\ ")
        lines += ["\\bottomrule", "\\end{tabular}%", "}", ""]
        return "\n".join(lines)

    def emb(analysis, venues):
        lines = ["\\begin{tabular}{lrrrrrr}", "  \\toprule",
                 "Venue & N & $D$ & P Value & Mean Rank & 95\\% CI & $BF_{01}$ \\\\ ", "  \\midrule"]
        for v in venues:
            r = row(analysis, v, "Similarity rank", "1s")
            lines.append(
                f"{v} & {int(r['n'])} & {float(r['statistic']):.4f} & {fp(r['p'])} & "
                f"{float(r['effect']) * 100:.1f} & {ci(r['ci_low'], r['ci_high'], 1, 100)} & "
                f"{bf(analysis, v, 'Similarity rank')} \\\\ ")
        lines += ["   \\bottomrule", "\\end{tabular}", ""]
        return "\n".join(lines)

    bodies["si:table:paper-features-1sKS"] = ks1("Main: percentile rank vs. uniform", VENUES, {})
    bodies["si:table:paper-features-2sKS"] = ks2("Main: percentile rank vs. matched papers", VENUES, mean_ranks(main_2s))
    bodies["si:table:density-tests_1ks_extra"] = ks1("Supplementary: percentile rank vs. uniform", SUPP_VENUES, {"Citations": "Impact"})
    bodies["si:table:density_tests_2ks_extra"] = ks2("Supplementary: percentile rank vs. matched papers", SUPP_VENUES, mean_ranks(supp_2s))
    bodies["si:table:embedding-tests"] = emb("Main: co-citing similarity rank vs. uniform", VENUES)
    bodies["si:table:embedding_tests_extra"] = emb("Supplementary: co-citing similarity rank vs. uniform", SUPP_VENUES)

    # Robustness t-tests: cells give t(df), p / d_z, CI; treatment minus control
    def cell(r):
        return ("\\begin{tabular}[c]{@{}c@{}}"
                f"$t({int(float(r['df']))}) = {float(r['statistic']):.2f}$, $p = {fp(r['p']).replace('$<$', '<')}$"
                "\\\\"
                f"$d_z = {float(r['std_effect']):.2f}$, ${ci(r['ci_low'], r['ci_high'])}$"
                "\\end{tabular}").replace("$p = <", "$p < ")

    paper_specs = [(2, 5, 2), (3, 5, 2), (4, 5, 2), None, (3, 5, 2), (3, 10, 2), (3, 15, 2), None, (3, 5, 1), (3, 5, 2)]
    lines = ["\\resizebox{\\linewidth}{!}{%", "\\begin{tabular}{lllccccc}", "  \\toprule",
             "Delay & Citations $\\pm$ $\\epsilon$ & Year $\\pm$ $\\epsilon$ & Nature & Science & PNAS & PRL & Other APS \\\\ ",
             "  \\midrule"]
    for sp in paper_specs:
        if sp is None:
            lines.append("  \\midrule")
            continue
        d, c, y = sp
        spec = f"delay {d}, citations {c}%, year {y}"
        cells = [cell(row("Robustness: paper impact growth", v, "All lags", "paired t", spec)) for v in VENUES]
        lines.append(f"  {d} & {c}\\% & {y} & " + " & ".join(cells) + " \\\\ ")
    lines += ["   \\bottomrule", "\\end{tabular}%", "}", ""]
    bodies["si:tab:paper-matched-ttest"] = "\n".join(lines)

    def author_table(metric_label):
        lines = ["\\centering", "\\resizebox{\\linewidth}{!}{%", "\\begin{tabular}{lllccccc}", "  \\toprule",
                 "Authorship & Citations $\\pm$ $\\epsilon$ & Productivity $\\pm$ $\\epsilon$ & Nature & Science & PNAS & PRL & Other APS \\\\ ",
                 "  \\midrule"]
        for block in ([(5, 15), (10, 15), (15, 15)], [(15, 5), (15, 10), (15, 15)]):
            for who in ("first", "last"):
                for c, p in block:
                    comp = f"{'First' if who == 'first' else 'Last'}-author {metric_label}"
                    spec = f"citations {c}%, productivity {p}%"
                    an = "Main: author growth" if (c, p) == (15, 15) else "Robustness: author growth"
                    cells = [cell(row(an, v, comp, "paired t", spec)) for v in VENUES]
                    lines.append(f"{who} & {c}\\% & {p}\\% & " + " & ".join(cells) + " \\\\ ")
            lines.append("  \\midrule")
        lines[-1] = "   \\bottomrule"
        lines += ["\\end{tabular}%", "}", ""]
        return "\n".join(lines)

    bodies["si:tab:authors-matched-productivity-ttest"] = author_table("productivity")
    bodies["si:tab:authors-matched-impact-ttest"] = author_table("citations")

    def t_table(analysis, venues, first_col):
        hdr = ("\\textbf{%s} & \\textbf{N} & \\textbf{df} & \\textbf{$t$} & \\textbf{P-value} & \\textbf{$d_z$} & "
               "\\textbf{Difference} & \\textbf{95\\%% CI} & \\textbf{$BF_{01}$} \\\\") % first_col
        lines = ["\\begin{tabular}{lrrrrrrrr}", "\\toprule", hdr, "\\midrule"]
        for v in venues:
            r = row(analysis, v, "All lags", "paired t")
            lines.append(
                f"{v} & {int(r['n'])} & ${int(float(r['df']))}$ & {float(r['statistic']):.2f} & {fp(r['p'])} & "
                f"{float(r['std_effect']):.2f} & {float(r['effect']):.3f} & {ci(r['ci_low'], r['ci_high'])} & "
                f"{bf(analysis, v, 'All lags')} \\\\")
        lines += ["\\bottomrule", "\\end{tabular}%", ""]
        return "\n".join(lines)

    bodies["si:table:high-interest-analysis"] = t_table(
        "Main: paper impact growth, high-interest letters", ["Nature", "PNAS", "Science", "PRL"], "Journal")
    bodies["si:table:aps-journal-ttests"] = t_table(
        "Main: paper impact growth by APS journal", ["PRL", "PR-A", "PR-B", "PR-C", "PR-D", "PR-E"], "Venue")

    # Full paired t-test and Wilcoxon statistics for Fig. 2 and Supplementary Fig. 8
    comparisons = [
        ("(A) Paper citations", "Main: paper impact growth", "All lags"),
        ("Paper citations, lag $= 0$", "Main: paper impact growth", "Lag = 0"),
        ("Paper citations, lag $> 0$", "Main: paper impact growth", "Lag > 0"),
        ("(B) First-author productivity", "Main: author growth", "First-author productivity"),
        ("(C) Last-author productivity", "Main: author growth", "Last-author productivity"),
        ("(D) First-author citations", "Main: author growth", "First-author citations"),
        ("(E) Last-author citations", "Main: author growth", "Last-author citations"),
    ]
    lines = ["\\resizebox{\\linewidth}{!}{%", "\\begin{tabular}{llrrrrrcrrrcr}", "\\toprule",
             " & & & \\multicolumn{5}{c}{Paired $t$-test} & \\multicolumn{4}{c}{Wilcoxon signed-rank test} & \\\\",
             "\\cmidrule(lr){4-8} \\cmidrule(lr){9-12}",
             "Comparison & Journal & N & $t$ (df) & P-value & $d_z$ & Mean difference & 95\\% CI & $V$ & P-value & $r$ & Hodges--Lehmann [95\\% CI] & $BF_{01}$ \\\\",
             "\\midrule"]
    for k, (label, an, comp) in enumerate(comparisons):
        for v in VENUES:
            spec = "citations 15%, productivity 15%" if an == "Main: author growth" else "main"
            t = row(an, v, comp, "paired t", spec)
            w = row(an, v, comp, "Wilcoxon", spec)
            # Bayes factors label author citation growth as "impact"
            bf_comp = comp.replace("citations", "impact")
            lines.append(
                f"{label if v == 'Nature' else ''} & {v} & {int(t['n'])} & "
                f"{float(t['statistic']):.2f} ({int(float(t['df']))}) & {fp(t['p'])} & {float(t['std_effect']):.2f} & "
                f"{float(t['effect']):.3f} & {ci(t['ci_low'], t['ci_high'])} & "
                f"{float(w['statistic']):g} & {fp(w['p'])} & {float(w['std_effect']):.2f} & "
                f"{float(w['effect']):.3f} {ci(w['ci_low'], w['ci_high'])} & {bf(an, v, bf_comp)} \\\\")
        if k < len(comparisons) - 1:
            lines.append("\\midrule")
    lines += ["\\bottomrule", "\\end{tabular}%", "}", ""]
    bodies["si:tab:wilcoxon"] = "\n".join(lines)

    # Average marginal effects (Supplementary Figs. 2-3)
    factors = [("(A) Inferred gender is woman", "Gender (woman)", "genderFemale"),
               ("(B) Is a senior researcher", "Senior researcher", "senioritySenior"),
               ("(C) Elite affiliation", "Elite affiliation", "eliteElite")]
    lines = ["\\begin{tabular}{lllrrrrrr}", "\\toprule",
             "Characteristic & Author & Journal & N & $z$ & P-value & AME & 95\\% CI & $BF_{01}$ \\\\", "\\midrule"]
    for k, (fac, name, coef) in enumerate(factors):
        for who, fig in (("First", "Fig. S2"), ("Last", "Fig. S3")):
            for v in VENUES:
                r = [x for x in T if x["analysis"] == "Main: author characteristics" and x["figure"] == fig
                     and x["venue"] == v and x["comparison"] == fac]
                assert len(r) == 1, (fac, fig, v)
                r = r[0]
                b = [x for x in B if x["analysis"] == "Main: author characteristics" and x["figure"] == fig
                     and x["venue"] == v and x["comparison"] == f"{who} author: {coef}"]
                assert len(b) == 1, (who, coef, v)
                first = name if (who == "First" and v == "Nature") else ""
                author = who if v == "Nature" else ""
                lines.append(f"{first} & {author} & {v} & {int(r['n'])} & {float(r['statistic']):.2f} & {fp(r['p'])} & "
                             f"{float(r['effect']):.3f} & {ci(r['ci_low'], r['ci_high'])} & {fbf(b[0]['BF01'])} \\\\")
        if k < len(factors) - 1:
            lines.append("\\midrule")
    lines += ["\\bottomrule", "\\end{tabular}", ""]
    bodies["si:tab:ame"] = "\n".join(lines)

    # Number of papers behind each point of Fig. 3, by panel, journal, and year
    P = list(csv.DictReader(open(temporal_plotdata)))
    years = sorted({int(r["delta_year"]) for r in P})
    panels = [("(A) citations received", "(A) Citations received"),
              ("(B) proportion co-citing", "(B) Proportion co-citing")]
    lines = ["\\begin{tabular}{ll" + "r" * len(years) + "}", "\\toprule",
             f" & & \\multicolumn{{{len(years)}}}{{c}}{{Years since receipt of critical letter}} \\\\",
             f"\\cmidrule(lr){{3-{len(years) + 2}}}",
             "Panel & Journal & " + " & ".join(str(y) for y in years) + " \\\\", "\\midrule"]
    for k, (metric, label) in enumerate(panels):
        for v in VENUES:
            n = {int(r["delta_year"]): r["n"] for r in P if r["metric"] == metric and r["venue"] == v}
            assert len(n) == len(years), (metric, v)
            lines.append(f"{label if v == 'Nature' else ''} & {v} & " + " & ".join(n[y] for y in years) + " \\\\")
        if k < len(panels) - 1:
            lines.append("\\midrule")
    lines += ["\\bottomrule", "\\end{tabular}", ""]
    bodies["si:tab:visibility-n"] = "\n".join(lines)

    os.makedirs(out_dir, exist_ok=True)
    for label, body in bodies.items():
        with open(os.path.join(out_dir, FILES[label]), "w") as fh:
            fh.write(body)
    print(f"Wrote {len(bodies)} table bodies to {out_dir}")
    return bodies


if __name__ == "__main__":
    if len(sys.argv) != 7:
        sys.exit(__doc__)
    main(*sys.argv[1:])
