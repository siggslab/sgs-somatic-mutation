#!/usr/bin/env python3

import os
import hailtop.batch as hb
from cpg_utils.hail_batch import get_config, remote_tmpdir
from analysis_runner import dataproc

from cpg_utils.hail_batch import (
    authenticate_cloud_credentials_in_job,
    copy_common_env,
    remote_tmpdir,
    output_path
)

config = get_config()

service_backend = hb.ServiceBackend(
    billing_project=config['hail']['billing_project'], remote_tmpdir=remote_tmpdir()
)

batch = hb.Batch(name='mt test example', backend=service_backend)

cluster = dataproc.setup_dataproc(
    batch,
    max_age='2h',
    packages=['click', 'selenium', 'gnomad'],
    init=['gs://cpg-reference/hail_dataproc/install_common.sh'],
    cluster_name='My Cluster with max-age=2h',
)
cluster.add_job('test.py &> ', job_name='test')

# Don't wait, which avoids resubmissions if this job gets preempted.
batch.run(wait=False)
