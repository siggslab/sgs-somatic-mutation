
import click
import hail as hl
import matplotlib.pyplot as plt
from bokeh.io.export import get_screenshot_as_png
from cpg_utils.hail import output_path

TOB_test_data = "gs://cpg-tob-wgs-test/mt/v7.mt"

@click.command()
@click.option('--rerun', help='Whether to overwrite cached files', default=False)

def plot_call_rate(mt):
    """Test script entry point."""
          
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
    plt.show()
    
# Subset mt to chr22
mt = hl.read_matrix_table(TOB_test_data)

intervals = ["chr22"]
filtered_mt = hl.filter_intervals(mt, [hl.parse_locus_interval(x, reference_genome='GRCh38') for x in intervals

# Densify chr22 sparse matrix
filtered_mt = hl.experimental.densify(filtered_mt)

# Run varient QC
filtered_mt = hl.variant_qc(filtered_mt)

# Plot the call rate
plot_call_rate(filtered_mt)

if __name__ == '__main__':
    plot_call_rate()  # pylint: disable=no-value-for-parameter
