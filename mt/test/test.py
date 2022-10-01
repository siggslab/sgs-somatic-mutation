import hail as hl
import matplotlib.pyplot as plt
from bokeh.io.export import get_screenshot_as_png
from cpg_utils.hail import output_path

def test():
    out = output_path('test.txt')

    with open(out, 'w') as f:
        f.write('readme')

if __name__ == "__main__":
    test()
