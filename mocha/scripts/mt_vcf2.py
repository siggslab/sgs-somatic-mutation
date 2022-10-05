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
#        mt = hl.filter_intervals(
#             mt, 
#             [hl.parse_locus_interval('chr22', reference_genome='GRCh38')],
#        )
        
        # Densify chr22 sparse matrix 
        mt = hl.experimental.densify(mt) 

        # filter alleles
        mt = mt.filter_rows((mt.locus.contig == chrom) & (mt.alleles.length() > 1))
        hl.context.warning("filter")
        hl.copy_log(log_out)
        # filter further
        ab = mt.AD[1] / hl.sum(mt.AD)
        filter_condition = ((mt.GT.is_hom_ref() & (ab <= 0.1)) |
                        (mt.GT.is_het() & (ab >= 0.25) & (ab <= 0.75)) |
                        (mt.GT.is_hom_var() & (ab >= 0.9))) & (mt.DP >= 10) & (mt.GQ >= 20)
        mt2 = hl.variant_qc(mt.filter_entries(filter_condition))

        mt3 = mt2.filter_rows((mt2.variant_qc.AC[0] != 0) & (mt2.variant_qc.AC[1] != 0) & (mt2.variant_qc.call_rate >= 0.97) )

        mt3_out = mt3.select_rows(mt3.rsid, mt3.qual, mt3.filters)
        mt3_out = mt3_out.select_entries(mt3_out.GT, mt3_out.DP, mt3_out.AD,  mt3_out.GQ )

        mt3_out = hl.sample_qc(mt3_out)
        mt3_out = mt3_out.filter_cols(mt3_out.sample_qc.call_rate >= 0.97)

        hl.context.warning("done filter")
        hl.copy_log(log_out)

        metadata = {'filter': {'InbreedingCoeff':{'Description':''},
            'VQSR':{'Description':''},
            'AC0':{'Description':''}, 
            'PASS':{'Description':''}},

            'format': {'AD': {'Description':'AD',
                'Number':'R',
                'Type':'Integer'}}
            }
 
        hl.export_vcf(mt3_out, p_out, metadata=metadata)

    hl.context.warning("done")
    hl.copy_log(log_out)


if __name__ == "__main__":
    query()
