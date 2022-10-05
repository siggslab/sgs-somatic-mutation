#!/usr/bin/env python3

import click
import hail as hl

from cpg_utils.hail_batch import output_path

@click.command()
@click.option('--dataset', help="data to query")
@click.option('--chrom', help="chromsome")
@click.option('--output', help="output name")
@click.option('--rerun', help='Whether to overwrite cached files', default=False)
def query(dataset, chrom, output, rerun):
    p_out = output_path(output)
    log_out = output_path(output + ".log")
 
    hl.init(default_reference='GRCh38')
    hl.context.warning("inited")
    hl.copy_log(log_out)

    if rerun or not hl.hadoop_exists(p_out):
        mt = hl.read_matrix_table(dataset)
        # filter alleles
        mt = mt.filter_rows(mt.locus.contig == chrom)
        mt = hl.experimental.densify(mt)
        mt = hl.variant_qc(mt)
        
        mt.write(p_out)
         
        percents = [0.0, 0.5, 0.8, 1]
        callrates = []
        for per in percents:
            callrate_mt = mt.filter_rows(mt.variant_qc.call_rate >= per)
            callrates.append(callrate_mt.count_rows())
        
        print(f'Unpacked call rate list: {*callrates,}')

        hl.context.warning("Calculation")
        hl.copy_log(log_out)

    hl.context.warning("done")
    hl.copy_log(log_out)


if __name__ == "__main__":
    query()
