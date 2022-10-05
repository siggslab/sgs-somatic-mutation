#!/usr/bin/env python3

import click
import hail as hl
import pandas as pd
from cpg_utils.hail_batch import output_path, init_batch, output_path, reference_path
from cloudpathlib import AnyPath


@click.command()
@click.option('--dataset', help="data to query")
@click.option('--chrom', help="chromsome")
@click.option('--output', help="output name")
@click.option('--rerun', help='Whether to overwrite cached files', default=False)
def main():
    
    init_batch()
 
    # define output filename
    output_filename = AnyPath(output_path('call_rate_figure_data.csv'))

    dataset = 'gs://cpg-tob-wgs-test/mt/v7.mt'    
    mt = hl.read_matrix_table(dataset)
    mt = hl.filter_intervals(
         mt, 
         [hl.parse_locus_interval('chr22', reference_genome='GRCh38')],
    )
    
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
 
if __name__ == "__main__":
    main()
