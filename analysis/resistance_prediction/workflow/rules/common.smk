from itertools import product
from typing import List

from snakemake.io import Wildcards


def infer_reads(wildcards, merged: bool = False):
    site = wildcards.site
    sample = wildcards.sample
    tech = wildcards.tech

    if tech == "nanopore":
        return QC(f"subsampled/{site}/{tech}/{sample}/{sample}.subsampled.fastq.gz")
    elif merged:
        return (
            RESULTS / f"drprg/mergepe/{tech}/{site}/{sample}/{sample}.merged.fastq.gz"
        )
    else:
        return QC(
            [
                f"subsampled/{site}/{tech}/{sample}/{sample}.subsampled.R{i}.fastq.gz"
                for i in [1, 2]
            ]
        )


def drprg_filter_args(wildcards: Wildcards) -> str:
    """Generate CLI args for drprg filters"""
    filters = config.get("filters", {})
    args = ""
    for (flag, key) in [
        ("-d", "min_covg"),
        ("-b", "min_strand_bias"),
        ("-g", "min_gt_conf"),
        ("-L", "max_indel"),
        ("-K", "min_frs"),
    ]:
        if key in filters:
            if key == "min_gt_conf":
                val = filters[key][wildcards.tech]
            else:
                val = filters[key]
            args += f"{flag} {val} "

    return args


def all_concordance_files(wildcards: Wildcards) -> List[str]:
    files = []
    for site, sample in zip(samplesheet["site"], samplesheet["sample"]):
        for tech, tool in product(TECHS, TOOLS):
            files.append(
                str(RESULTS / f"concordance/{tool}/{tech}/{site}/{sample}.{tool}.csv")
            )

    return files
