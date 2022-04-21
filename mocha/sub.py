#!/usr/bin/env python3
"""
Submit program to CPG
Suggested programmed by zzl<zzl09yan@gmail.com>
License: MIT
Please read the document from analysis-runner
https://anaconda.org/cpg/analysis-runner
"""

from cpg_utils.hail import output_path
from cpg_utils.hail import remote_tmpdir

from analysis_runner.git import (
  prepare_git_job,
  get_repo_name_from_current_directory,
  get_git_commit_ref_of_current_repository,
)

import hailtop.batch as hb

import click
import os

BILLING_PROJECT = os.getenv('HAIL_BILLING_PROJECT')
assert BILLING_PROJECT

def makeBatch():
    """
    make the batch backend
    """
    # Initializing Batch
    backend = hb.ServiceBackend(
        billing_project=BILLING_PROJECT, remote_tmpdir=remote_tmpdir()
    )
    return hb.Batch(backend=backend, default_image=os.getenv('DRIVER_IMAGE'))


@click.command()
@click.option('--cmd', help='command to run') 
@click.option('--jobname', help='job name')
@click.option('--time', default='', help='time to run', show_default=True)
@click.option("--image", default="", help='image name')
@click.option("--cpu", default=1, help='CPU')
@click.option("--mem", default='4Gi', help='Memory')
@click.option("--disk", default="10Gi", help="disk size")
@click.option("--mount", default="", help="mount")
@click.option("--readonly", default=True, help="mount read only")
def sub(cmd, jobname, time, image, cpu, mem, disk, mount, readonly):
    batch = makeBatch()
    j = batch.new_job(jobname)

    prepare_git_job(
            job=j,
            # you could specify a name here, like 'analysis-runner'
            repo_name=get_repo_name_from_current_directory(),
            # you could specify the specific commit here, eg: '1be7bb44de6182d834d9bbac6036b841f459a11a'
            commit=get_git_commit_ref_of_current_repository(),
            )

    j.command(f"{cmd} &> {j.output_log}")
    # set env
    if image != "":
        j.image(image)
    j.cpu(cpu)
    j.storage(disk)
    j.memory(mem)
    if time != "":
        j.timeout(time)

    if mount != "":
        mounts = mount.split(";")
        for mItem in mounts:
            mItems = mItem.split("=>")
            mItems = [x.strip() for x in mItems]
            if(len(mItems) != 2):
                continue
            else:
                j.cloudfuse(mItems[0], mItems[1], read_only=readonly)

    batch.write_output(j.output_log, output_path(jobname + ".log"))

    batch.run(wait=False)
    

if __name__ == '__main__':
    sub()
