#!/usr/bin/env python3

import click
import hail as hl
from cpg_utils.hail_batch import output_path

import pandas as pd
from pandas import Series, DataFrame
import numpy as np
import math
import collections


@click.command()
@click.option("--dataset", help="data to query")
@click.option("--chrom", help="chromsome")
@click.option("--cohort-size", help="sample size used to define the AF threshold")
@click.option(
    "--repeat-region-file", help="simple repeat regions needed to be excluded"
)
@click.option("--gnomAD-file", help="annotate variants with pop AF")
@click.option("--output", help="output name")
@click.option("--rerun", help="Whether to overwrite cached files", default=False)
def main(dataset, chrom, cohort_size, repeat_region_file, gnomAD_file, output, rerun):
    p_out = output_path(output)
    log_out = output_path(output + ".log")

    hl.init(default_reference="GRCh38")
    hl.context.warning("inited")
    hl.copy_log(log_out)

    if rerun or not hl.hadoop_exists(p_out):

        # Step 1 - Read dataset
        mt = hl.read_matrix_table(dataset)
        mt = mt.filter_rows(mt.locus.contig == chrom)
        mt = hl.experimental.densify(mt)
        mt = hl.variant_qc(mt)

        #  Step 2 - Sample-level QC
        mt = hl.sample_qc(mt)

        # Restricted to samples with imputed sex == XX (female) or XY (male)
        # Sample-level call rate >= 0.99
        # mean coverage >= 20X
        filter_conditions = (
            ((mt.meta.sex_karyotype == "XX") | (mt.meta.sex_karyotype == "XY"))
            & (mt["sample_qc"].call_rate >= 0.99)
            & (mt["sample_qc"].dp_stats.mean >= 20)
        )
        mt = mt.filter_cols(filter_conditions, keep=True)

        # Exclude related samples
        mt = mt.filter_cols(mt["meta"].related, keep=False)

        # Skip ancestry check

        # Step 3 - Variant-level QC

        mt = hl.variant_qc(mt)

        # Apply AS_VQSR filters
        # Restricted to bi-alleleic variants
        # Exclude variants with inbreeding Coefficient < -0.3
        filter_conditions = (
            (hl.is_missing(mt["allele_type"]))
            | (
                (hl.is_defined(mt["allele_type"]))
                & (mt["allele_type"] == "snv")
                & (mt["AS_VQSLOD"] < mt["filtering_model"].snv_cutoff.min_score)
            )
            | (
                (hl.is_defined(mt["allele_type"]))
                & (mt["allele_type"] == "ins")
                & (mt["AS_VQSLOD"] < mt["filtering_model"].indel_cutoff.min_score)
            )
            | (hl.len(mt.alleles) != 2)
            | ((hl.len(mt.alleles) == 2) & (mt.n_unsplit_alleles != 2))
            | (hl.is_missing(mt["InbreedingCoeff"]))
            | ((hl.is_defined(mt["InbreedingCoeff"])) & (mt["InbreedingCoeff"] < -0.3))
        )
        mt = mt.filter_rows(filter_conditions, keep=False)

        # Restricted to high quality variants (GQ>=20, DP>=10)
        filter_condition = (mt.DP >= 10) & (mt.GQ >= 20)
        mt = hl.variant_qc(mt.filter_entries(filter_condition, keep=True))

        # Step 4 - deCODE specific filter

        # Exclude variants with call rate < 0.99 (not in deCODE paper)
        mt = mt.filter_rows(mt.variant_qc.call_rate >= 0.99)

        # Identify singleton mutations with filters
        # sequence depth >= 16 & GQ >= 90
        # >=3 indepedent reads containing a variant allele required
        filter_condition = (mt.DP >= 16) & (mt.GQ >= 90) & (mt.AD[1] >= 3)
        mt = hl.variant_qc(mt.filter_entries(filter_condition, keep=True))
        mt = mt.filter_rows(mt.variant_qc.n_non_ref == 1)

        # gnomAD allele frequency
        ref_ht = hl.read_table(gnomAD_file)

        # Annotate variants with CADD scores, gnomAD etc.
        mt = mt.annotate_rows(
            cadd=ref_ht[mt.row_key].cadd,
            gnomad_genomes=ref_ht[mt.row_key].gnomad_genomes,
            gnomad_genome_coverage=ref_ht[mt.row_key].gnomad_genome_coverage,
        )

        del ref_ht

        # Apply gnomAD AF filter
        AF_cutoff = 1 / (cohort_size * 2)
        mt = mt.filter_rows(mt.gnomad_genomes.AF_POPMAX_OR_GLOBAL <= AF_cutoff)

        # Exclude variants in simple repeat regions
        # simple repeat regions - combining the entire Simple Tandem Repeats by TRF track in UCSC hg38 with all homopolymer regions in hg38 of length 6bp or more

        # Read the (Combined) Simple Repeat Regions
        interval_table = hl.import_bed(repeat_region_file, reference_genome="GRCh38")

        mt = hl.variant_qc(
            mt.filter_rows(hl.is_defined(interval_table[mt.locus]), keep=False)
        )

        # Step 5 - Export to a pVCF file
        output = mt.select_rows(mt.rsid, mt.qual)
        output = output.select_entries(output.GT, output.DP, output.AD, output.GQ)

        metadata = {
            "filter": {
                "InbreedingCoeff": {"Description": ""},
                "VQSR": {"Description": ""},
                "AC0": {"Description": ""},
                "PASS": {"Description": ""},
            },
            "format": {"AD": {"Description": "AD", "Number": "R", "Type": "Integer"}},
        }

        hl.export_vcf(output, p_out, metadata=metadata)
        hl.copy_log(log_out)

    hl.context.warning("done")
    hl.copy_log(log_out)


if __name__ == "__main__":
    main()
