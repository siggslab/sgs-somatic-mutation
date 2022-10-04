#!/usr/bin/env python3

import click
import hail as hl
import matplotlib.pyplot as plt
from bokeh.io.export import get_screenshot_as_png
from cpg_utils.hail_batch import output_path, init_batch

def plot_call_rate(mt):
    percents = [0.0, 0.5, 0.8, 1]
    callrates = []
    for per in percents:
        callrate_mt = mt.filter_rows(mt.variant_qc.call_rate >= per)
        callrates.append(callrate_mt.count_rows())
    fig = plt.figure()
    ax = fig.add_axes([0,0,1,1])
    ax.bar(percents, callrates)
    ax.set_ylabel('Variants')
    ax.set_xlabel('Call Rate')
    plt.savefig('save_mt_call_rate_test.png')
    figure_filename = output_path('mt_call_rate_test.png', 'web')
    with hl.hadoop_open(figure_filename, 'wb') as f:
        get_screenshot_as_png(fig).save(f, format='PNG')

@click.command()
@click.option('--dataset', help="data to query")
@click.option('--output', help="output name")
@click.option('--rerun', help='Whether to overwrite cached files', default=False)
def query(dataset, output, rerun):    
#    p_out = output_path(output)
    log_out = ouptut_path(output + ".log")
    
    hl.init(default_reference='GRCh38')
    hl.context.warning("inited")
    hl.copy_log(log_out)
    
    if rerun or not hl.hadoop_exists(p_out):
        mt = hl.read_matrix_table(dataset)
        mt = hl.filter_intervals(
            mt, 
            [hl.parse_locus_interval('chr22', reference_genome='GRCh38')],
        )
        # Densify chr22 sparse matrix 
        mt = hl.experimental.densify(mt)
        mt = hl.variant_qc(mt)
        
        plot_call_rate(mt)    
        plt.savefig('save_mt_call_rate_test.png')
        figure_filename = output_path('mt_call_rate_test_hail.png', 'web')
        with hl.hadoop_open(figure_filename, 'wb') as f:
            get_screenshot_as_png(fig).save(f, format='PNG')
        
    hl.context.warning("done")
    hl.copy_log(log_out)


if __name__ == "__main__":
    query()

