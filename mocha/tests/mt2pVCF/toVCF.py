
import click
import hail as hl
from cpg_utils.hail import output_path

BK_test_data = "gs://cpg-tob-wgs-test/mt/v7.mt"


from gnomad.utils.vcf import adjust_vcf_incompatible_types
from gnomad.utils.sparse_mt import default_compute_info

def mt_to_sites_only_ht(mt: hl.MatrixTable, cur_chr: str, n_partitions: int) -> hl.Table:
    """
    Convert matrix table (mt) into sites-only VCF-ready table (ht)
    :param mt: multi-sample matrix table
    :param n_partitions: number of partitions for the output table
    :return: hl.Table
    """

    mt = _filter_rows_and_add_tags(mt, cur_chr)
    ht = _create_info_ht(mt, n_partitions=n_partitions)
    ht = adjust_vcf_incompatible_types(ht)
    return ht


def _filter_rows_and_add_tags(mt: hl.MatrixTable, cur_chr: str) -> hl.MatrixTable:
    #mt = hl.experimental.densify(mt)

    # Filter to only non-reference sites.
    # An examle of a variant with hl.len(mt.alleles) > 1 BUT NOT
    # hl.agg.any(mt.LGT.is_non_ref()) is a variant that spans a deletion,
    # which was however filtered out, so the LGT was set to NA, however the site
    # was preserved to account for the presence of that spanning deletion.
    # locus   alleles    LGT
    # chr1:1 ["GCT","G"] 0/1
    # chr1:3 ["T","*"]   NA
    mt = mt.filter_rows((mt.locus.contig == cur_chr) & (mt.alleles.length() > 1) & (hl.agg.any(mt.LGT.is_non_ref())))

    # annotate site level DP as site_dp onto the mt rows to avoid name collision
    mt = mt.annotate_rows(site_dp=hl.agg.sum(mt.DP))

    # Add AN tag as ANS
    return mt.annotate_rows(ANS=hl.agg.count_where(hl.is_defined(mt.LGT)) * 2)



def _create_info_ht(mt: hl.MatrixTable, n_partitions: int) -> hl.Table:
    """Create info table from vcf matrix table"""
    info_ht = default_compute_info(mt, site_annotations=True, n_partitions=n_partitions)
    info_ht = info_ht.annotate(
        info=info_ht.info.annotate(DP=mt.rows()[info_ht.key].site_dp)
    )
    return info_ht



def outputVCF(mt, cur_chr, n_partition, output_path):
    ht = mt_to_sites_only_ht(mt, cur_chr, n_partition)
    hl.export_vcf(ht, output_path)


@click.command()
@click.option('--rerun', help='Whether to overwrite cached files', default=False)
def query(rerun):
    """Query script entry point."""

    hl.init(default_reference='GRCh38')

    mt = hl.read_matrix_table(BK_test_data)

    output_vcf = output_path('test_chr22.vcf.bgz')
    if rerun or not hl.hadoop_exists(output_vcf):
        mt = hl.read_matrix_table(BK_test_data)
        #mt22 = mt.filter_rows(mt.locus.contig == '22')
        cur_chr = 'chr22'
        outputVCF(mt, cur_chr, 5000, output_vcf)


if __name__ == '__main__':
    query()  # pylint: disable=no-value-for-parameter
