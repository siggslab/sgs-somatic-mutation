#!/usr/bin/env python3
"""
submit to dataproc
Suggested programmed by zzl<zzl09yan@gmail.com>
License: MIT
Please read the document from analysis-runner
https://anaconda.org/cpg/analysis-runner
"""

import os
import hailtop.batch as hb
from cpg_utils.hail import remote_tmpdir
from analysis_runner import dataproc
import click

service_backend = hb.ServiceBackend(
    billing_project=os.getenv('HAIL_BILLING_PROJECT'), remote_tmpdir=remote_tmpdir()
)

batch = hb.Batch(name='Dataproc batch', backend=service_backend)

@click.command()
@click.option("--script", help="script to run")
@click.option("--jobname", help="jobname")
@click.option("--time", default='2h', help="max time")
@click.option("--nworker", default=2, help="number of worker")
@click.option("--worker", default=None, help="type of worker: e.g. 'n1-highmem-8'")
def submit(script, jobname, time, nworker, worker):
    cluster = dataproc.setup_dataproc(
            batch,
            max_age=time,
            packages=['click', 'selenium'],
            init=['gs://cpg-reference/hail_dataproc/install_common.sh'],
            cluster_name='Dataproc cluster',
            )
    cluster.add_job(script, job_name=jobname)
    # Don't wait, which avoids resubmissions if this job gets preempted.
    batch.run(wait=False)

if __name__ == "__main__":
    submit()

