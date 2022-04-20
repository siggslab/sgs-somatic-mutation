#!/usr/bin/env python3

import os
import hailtop.batch as hb
from cpg_utils.hail import remote_tmpdir
from analysis_runner import dataproc

service_backend = hb.ServiceBackend(
    billing_project=os.getenv('HAIL_BILLING_PROJECT'), remote_tmpdir=remote_tmpdir()
)

batch = hb.Batch(name='stdout tests', backend=service_backend)


cluster = dataproc.setup_dataproc(
    batch,
    max_age='1h',
    packages=['click', 'selenium'],
    init=['gs://cpg-reference/hail_dataproc/install_common.sh'],
    cluster_name='My Cluster with max-age=1h',
)
cluster.add_job('test.py &> ', job_name='example1')


# Don't wait, which avoids resubmissions if this job gets preempted.
batch.run(wait=False)
