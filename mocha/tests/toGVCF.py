
import click
import hail as hl
from bokeh.io.export import get_screenshot_as_png
from cpg_utils.hail import output_path

BK_test_data = "gs://cpg-tob-wgs-test/mt/v7.mt"


@click.command()
@click.option('--rerun', help='Whether to overwrite cached files', default=False)
def query(rerun):
    """Query script entry point."""

    hl.init(default_reference='GRCh38')

    mt = hl.read_matrix_table(BK_test_data)

    output_vcf = output_path('sample_qc.mt')
    if rerun or not hl.hadoop_exists(sample_qc_path):
        mt = hl.read_matrix_table(BK_test_data)
        mt_filter = filter_rows(dt.alleles.length() > 1)
        hl.export_vcf(mt_filter, sample_qc_path)

if __name__ == '__main__':
    query()  # pylint: disable=no-value-for-parameter
