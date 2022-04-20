#!/usr/bin/env python3

import click
import hail as hl

from cpg_utils.hail import output_path

@click.command()
@click.option('--dataset', help="data to query")
@click.pition('--chrom')
@click.option('--output', help="output name")
@click.option('--rerun', help='Whether to overwrite cached files', default=False)
def query(dataset, chrom, output, rerun):

    hl.init(default_reference='GRCh38')

    p_out = output_path(output)
    if rerun or not hl.hadoop_exists(p_out):
        mt = hl.read_matrix_table(dataset)
        # filter alleles
        mt2 = mt.filter_rows((mt.locus.contig == chrom) & (mt.alleles.length() > 1))
        # filter further
        ab = mt.AD[1] / hl.sum(mt.AD)
        filter_condition = ((mt.GT.is_hom_ref() & (ab <= 0.1)) |
                        (mt.GT.is_het() & (ab >= 0.25) & (ab <= 0.75)) |
                        (mt.GT.is_hom_var() & (ab >= 0.9))) & (mt.DP >= 10) & (mt.GQ >= 20)
        mt2 = hl.variant_qc(mt.filter_entries(filter_condition))

        mt3 = mt2.filter_rows((mt2.variant_qc.AC[0] != 0) & (mt2.variant_qc.AC[1] != 0) & (mt2.variant_qc.call_rate > 0.95))

        mt3_out = mt3.select_rows(mt3.rsid, mt3.qual, mt3.filters, mt3.info )

        mt3_out = mt3_out.select_entries(mt3_out.GT, mt3_out.DP, mt3_out.AD,  mt3_out.GQ )
        hl.export_vcf(mt3_out, p_out)

    hl.copy_log(output_path(output + ".log"))


if __name__ == "__main__":
    query()
