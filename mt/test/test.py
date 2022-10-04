import hail as hl
from bokeh.io.export import get_screenshot_as_png
from cloudpathlib import AnyPath
from cpg_utils.config import get_config
from cpg_utils.hail_batch import (
    authenticate_cloud_credentials_in_job,
    copy_common_env,
    remote_tmpdir,
    output_path
)

def test():
    with AnyPath(output_path('test.txt')).open('w+') as f:
    f.write('test contents')

if __name__ == "__main__":
    test()
