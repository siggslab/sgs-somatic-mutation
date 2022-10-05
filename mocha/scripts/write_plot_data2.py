#!/usr/bin/env python3

import click
import hail as hl
import pandas as pd
from cloudpathlib import AnyPath

from cpg_utils.hail_batch import output_path

@click.command()
@click.option('--dataset', help="data to query")
@click.option('--chrom', help="chromsome")
@click.option('--output', help="output name")
@click.option('--rerun', help='Whether to overwrite cached files', default=False)
def query(dataset, chrom, output, rerun):
    output_filename = AnyPath(output_path(output))
 
    hl.init(default_reference='GRCh38')
    hl.context.warning("inited")

    if rerun or not hl.hadoop_exists(output_filename):
        mt = hl.read_matrix_table(dataset)
        mt = mt.filter_rows((mt.locus.contig == chrom) & (mt.alleles.length() > 1))
        
        # Densify chr22 sparse matrix 
        mt = hl.experimental.densify(mt) 
        mt = hl.variant_qc(mt)
 
        percents = [0.0, 0.5, 0.8, 1]
        callrates = []
        for per in percents:
            callrate_mt = mt.filter_rows(mt.variant_qc.call_rate >= per)
            callrates.append(callrate_mt.count_rows())

        results_data = {
            'call_rate': percents,
            'variants': callrates,
        }

        df = pd.DataFrame(results_data)
        with output_filename.open('w') as of:
            df.to_csv(of, index=False)
        
    hl.context.warning("done")

if __name__ == "__main__":
    query()
