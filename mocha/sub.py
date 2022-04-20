#!/usr/bin/env python
"""
Submit program to CPG
Suggested programmed by zzl<zzl09yan@gmail.com>
License: MIT
Please read the document from analysis-runner
https://anaconda.org/cpg/analysis-runner
"""

from cpg_utils.hail import output_path
import click
import os
from common.hail import makeBatch

@click.command()
@click.option('--cmd', help='command to run') 
@click.option('--jobname', help='job name')
@click.option('--time', default='', help='time to run', show_default=True)
@click.option("--image", default="", help='image name')
@click.option("--cpu", default=1, help='CPU')
@click.option("--mem", default='4Gi', help='Memory')
@click.option("--disk", default="10Gi", help="disk size")
@click.option("--mount", default="", help="mount")
def sub(cmd, jobname, time, image, cpu, mem, disk, mount):
    batch = makeBatch()
    j = batch.new_job(jobname)
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
        mounts = mount.split()
        if len(mounts) != 2:
            print("error of mount")
        else:
            j.cloudfuse(mounts[0], mounts[1])

    batch.write_output(j.output_log, output_path(jobname + ".log"))

    batch.run(wait=False)

    

if __name__ == '__main__':
    sub()
