rule download_decontamination_db:
    output:
        fasta    = "data/decontamination_db/remove_contam.fa.gz",
        metadata = "data/decontamination_db/remove_contam.tsv"
    threads:
        config["download_decontamination_db"]["memory"]
    resources:
        mem_mb = (
    lambda wildcards, attempt: attempt * config["download_decontamination_db"]["memory"]
            )
    params:
        script  = config["download_decontamination_db"]["perl_script"],
        out_dir = config["download_decontamination_db"]["out_dir"]
    log:
        "analysis/logs/download_decontamination_db.log"
    shell:
        """
        bash analysis/scripts/make_decontamination_db.sh {params.script} \
            {params.out_dir} \
            {output.fasta} \
            output.metadata 2> {log}
        """

rule index_decontamination_db:
    input:
        rules.download_decontamination_db.output.fasta
    output:
        index = "data/decontamination_db/remove_contam.{}.mmi".format(config["index_decontamination_db"]["preset"])
    threads: 1
    resources:
        mem_mb = (
            lambda wildcards, attempt: attempt * config["index_decontamination_db"]["memory"]
            )
    params:
        preset = config["index_decontamination_db"]["preset"],
        split  = config["index_decontamination_db"]["split"]
    singularity:
        config["index_decontamination_db"]["container"]
    log:
        "analysis/logs/index_decontamination_db.log"
    shell:
        """
        minimap2 -I {params.split} \
            -x {params.preset} \
            -d {output.index} \
            {input} 2> {log}
        """

rule mapping:
    input:
        index = rules.index_decontamination_db.output.index,
        query = "analysis/{region}/nanopore/{run}/trimmed/{sample}.trimmed.fastq.gz"
    output:
        temp("analysis/{region}/nanopore/{run}/mapped/{sample}.sam")
    threads:
        config["mapping"]["threads"]
    resources:
        mem_mb = (
            lambda wildcards, attempt: attempt * config["mapping"]["memory"]
            )
    params:
        preset = config["index_decontamination_db"]["preset"],
    singularity:
        config["mapping"]["container"]
    log:
        "analysis/logs/mapping_{region}_{run}_{sample}.log"
    shell:
        """
        minimap2 -t {threads} \
            -ax {params.preset} \
            {input.index} \
            {input.query} > {output} 2> {log}
        """

#
# rule samtools_sort:
#     input:
#         "data/mapped/{sample}.bam"
#     output:
#         "data/sorted/{sample}_sorted.bam"
#     threads:
#         config["threads"]
#     log:
#         "logs/samtools_sort_{sample}.log"
#     singularity:
#         config["containers"]["nanoporeqc"]
#     shell:
#         "samtools sort -@ {threads} {input} 2> {log} > {output}"
#
#
# rule samtools_index:
#     input:
#         "data/sorted/{sample}_sorted.bam"
#     output:
#         "data/sorted/{sample}_sorted.bam.bai"
#     log:
#         "logs/samtools_index_{sample}.log"
#     singularity:
#         config["containers"]["nanoporeqc"]
#     shell:
#         "samtools index -b {input} 2> {log}"
#
# rule bam_to_fastq:
#     input:
#         "data/sorted/{sample}_sorted.bam"
#     output:
#         "data/filtered/{sample}_filtered.fastq.gz"
#     log:
#         "logs/bam_to_fastq_{sample}.log"
#     singularity:
#         config["containers"]["nanoporeqc"]
#     shell:
#         "(samtools fastq -F 0x4 {input} | gzip > {output}) 2> {log}"
