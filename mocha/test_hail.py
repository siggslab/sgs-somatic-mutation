#!/usr/bin/env python3

import click
import hail as hl
import sys

from cpg_utils.hail import output_path

@click.command()
@click.option('--dataset', help="data to query")
@click.option('--output', help="output name")
@click.option('--rerun', help='Whether to overwrite cached files', default=False)
def query(dataset, output, rerun):

    logfile = output_path(output + ".log")
    sys.stdout = open(logfile, 'w')
    sys.stderr = sys.stdout

    print("init")
    hl.init(default_reference='GRCh38')

    sample_qc_path1 = output_path(output)
    if rerun or not hl.hadoop_exists(sample_qc_path1):
        print("read")
        mt = hl.read_matrix_table(dataset)
        print(mt.count())
        mt1 = mt.head(10)
        print(mt1.count())
        mt_qc = hl.sample_qc(mt1)
        mt_qc.write(sample_qc_path1)
        print("done")

if __name__ == "__main__":
    query()
