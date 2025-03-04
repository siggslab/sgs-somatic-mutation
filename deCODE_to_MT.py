#!/usr/bin/env python3

"""
This script is to find singleton mutations in TOB
"""

import click
import hail as hl

from cpg_utils.config import get_config
from cpg_utils.hail_batch import dataset_path, output_path, init_batch, remote_tmpdir
from gnomad.utils.annotations import bi_allelic_site_inbreeding_expr


@click.command()
@click.option("--input-mt")
@click.option("--chrom")
@click.option("--cohort-size", help="sample size used to decide the AF threshold")
@click.option("--gnomad-file", help="annotate variants with pop AF from gnomAD")
@click.option("--regions-file", help="simple repeat regions needed to be excluded")
@click.option("--output-mt")
def main(
    input_mt: str,
    chrom: str,
    cohort_size: int,
    gnomad_file: str,
    regions_file: str,
    output_mt: str,
):
    init_batch()

    dataset = dataset_path(input_mt, dataset="tob-wgs")

    """
    Step 1 - Read & Densify mt dataset
    """
    mt = hl.read_matrix_table(dataset)
    mt = mt.filter_rows(mt.locus.contig == chrom)
    mt = hl.experimental.densify(mt)
    mt = hl.variant_qc(mt)

    """
    Step 2 - Sample-level QC
    1. Restricted to samples with imputed sex equals to XX (Female) or XY (Male)
    2. Restricted to samples with call rate >= 0.99
    3. Restricted to samples with mean coverage >= 20X
    4. Excluded related samples
    5. Skip ancestry check
    """

    mt = hl.sample_qc(mt)

    # Restricted to samples with imputed sex == XX or XY
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

    """
    Step 3 - Variant-level QC
    1. Apply AS_VQSR cutoffs (different threshold for indels/snvs)
    2. Restricted to bi-allelic variants
    3. Exclude variants with inbreeding coeff < -0.3
    4. Restricted to high quality variants (GQ>=20, DP>=10)
    """

    # Apply AS_VQSR filters
    # Restricted to bi-allelic variants
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
    )
    mt = mt.filter_rows(filter_conditions, keep=False)

    # Exclude variants with inbreeding coefficient < -0.3

    # InbreedingCoeff was calculated by function 'bi_allelic_site_inbreeding_expr'
    mt = mt.annotate_rows(InbreedingCoeff=bi_allelic_site_inbreeding_expr(mt.GT))

    # Filter variants with InbreedingCoeff (keep >= -0.3, exclude < -0.3)
    mt = mt.filter_rows(mt.InbreedingCoeff >= -0.3, keep=True)

    # Restricted to high quality variants (GQ>=20, DP>=10)
    filter_condition = (mt.DP >= 10) & (mt.GQ >= 20)
    mt = hl.variant_qc(mt.filter_entries(filter_condition, keep=True))

    """
    Step 4 - deCODE specific filter
    1. Exclude variants with call rate < 0.99
    2. Identify singleton mutations
    3. Apply deCODE specific filter (DP >= 16, GQ >= 90, >=3 indepedent reads for alt allele, not in simple repeat regions, very low AF at population level[use deCODE sample size as a ref])
    """

    # Exclude variants with call rate < 0.99 (not in deCODE paper)
    mt = mt.filter_rows(mt.variant_qc.call_rate >= 0.99)

    # Identify singleton mutations
    mt = mt.filter_rows(mt.variant_qc.n_non_ref == 1)

    # Apply strict filters to singleton mutations
    # DP >= 16 & GQ >= 90
    # >=3 indepedent reads containing a variant allele required
    filter_condition = (mt.DP >= 16) & (mt.GQ >= 90) & (mt.AD[1] >= 3)
    mt = hl.variant_qc(mt.filter_entries(filter_condition, keep=True))
    mt = mt.filter_rows(mt.variant_qc.n_non_ref == 1)

    # Read gnomAD allele frequency
    ref_ht = hl.read_table(gnomad_file)

    # Annotate variants with CADD scores, gnomAD etc.
    mt = mt.annotate_rows(
        cadd=ref_ht[mt.row_key].cadd,
        gnomad_genomes=ref_ht[mt.row_key].gnomad_genomes,
        gnomad_genome_coverage=ref_ht[mt.row_key].gnomad_genome_coverage,
    )

    # Delete gnomAD file to save space
    del ref_ht

    # Apply gnomAD AF filter (very low MAF)
    AF_cutoff = 1 / (int(cohort_size) * 2)
    mt = mt.filter_rows(mt.gnomad_genomes.AF_POPMAX_OR_GLOBAL <= AF_cutoff)

    # Exclude mutations in simple repeat regions
    # simple repeat regions - combining the entire Simple Tandem Repeats by TRF track in UCSC hg38 with all homopolymer regions in hg38 of length 6bp or more

    # Read the (Combined) Simple Repeat Regions
    interval_table = hl.import_bed(regions_file, reference_genome="GRCh38")

    # Exclude mutations in these regions
    mt = hl.variant_qc(
        mt.filter_rows(hl.is_defined(interval_table[mt.locus]), keep=False)
    )

    """
    Step 5 - Export to Hail MT
    Select the following fields & export to a Hail MatrixTable
    """
    mt = mt.select_rows(mt.rsid, mt.qual)
    mt = mt.select_entries(mt.GT, mt.DP, mt.AD, mt.GQ)

    file_out = output_path(output_mt, "analysis")
    mt.write(file_out, overwrite=True)


if __name__ == "__main__":
    main()
