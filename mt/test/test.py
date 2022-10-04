import hail as hl
import matplotlib.pyplot as plt
from bokeh.io.export import get_screenshot_as_png
from cpg_utils.hail import output_path
from cloudpathlib import AnyPath

def test():
    out = output_path('test.txt')

    with AnyPath(output_path('test.txt')).open('w+') as f:
    f.write('test contents')

if __name__ == "__main__":
    test()
