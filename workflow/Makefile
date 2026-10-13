all:
	snakemake -j 4

download:
	snakemake -j 1 download --rerun-triggers mtime --use-conda --conda-frontend conda --configfile config.yaml

novelty:
	snakemake -j 2 novelty --rerun-triggers mtime --use-conda --conda-frontend conda --configfile config.yaml

novelty-hpc:
	snakemake -j 20 novelty --force --use-conda --conda-frontend conda --configfile config.yaml

match:
	snakemake -j 2 match --rerun-triggers mtime --use-conda --conda-frontend conda --configfile config.yaml

results:
	snakemake -j 4 results --rerun-triggers mtime --use-conda --conda-frontend conda --configfile config.yaml

download_supplement:
	snakemake -j 1 download --rerun-triggers mtime --use-conda --conda-frontend conda --configfile config_supplement.yaml

match_supplement:
	snakemake -j 2 match --rerun-triggers mtime --use-conda --conda-frontend conda --configfile config_supplement.yaml

results_supplement:
	snakemake -j 2 results --rerun-triggers mtime --use-conda --conda-frontend conda --configfile config_supplement.yaml
stats:
	snakemake -j 2 stats --rerun-triggers mtime --use-conda --conda-frontend conda --configfile config.yaml

submission:
	snakemake -j 2 submission --rerun-triggers mtime --use-conda --conda-frontend conda --configfile config.yaml

export:
	snakemake -j 1 export --rerun-triggers mtime --use-conda --conda-frontend conda --configfile config.yaml
