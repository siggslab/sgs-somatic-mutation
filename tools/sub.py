#!/usr/bin/env python3

"""
Suggested and programmed by Zhili<zhilizheng@outlook.com>
License: MIT

# Usage - an example
## chrom="22"
## vcf="/data/test/chr${chrom}.vcf.bgz"
## ovcf="/data/test/chr${chrom}_gc.vcf.gz"
## ref="/ref/GRCh38/GCA_000001405.15_GRCh38_no_alt_analysis_set.fna"
## docker="us.gcr.io/mccarroll-mocha"
## image="bcftools:1.14-20220112"
## analysis-runner --dataset sgs-somatic-mtn --access-level test  --output-dir "test" --description "test" sub.py \
## --cmd "bcftools +mochatools $vcf -Oz -o $ovcf -- -t GC -f $ref" \
## --image "$docker/$image" \
## --mount "cpg-sgs-somatic-mtn-test => /data; cpg-sgs-somatic-mtn-test-upload => /ref" \
## --readonly false \
## --jobname GC${chrom}
"""

import os
import click
import hailtop.batch as hb

from cpg_utils.hail_batch import output_path, remote_tmpdir

from analysis_runner.git import (
    prepare_git_job,
    get_repo_name_from_current_directory,
    get_git_commit_ref_of_current_repository,
)


def makeBatch():
    """
    make the batch backend
    """
    config = get_config()
    backend = hb.ServiceBackend(
        billing_project=config["hail"]["billing_project"],
        remote_tmpdir=remote_tmpdir(),
    )
    return hb.Batch(backend=backend, default_image=config["workflow"]["driver_image"])


@click.command()
@click.option("--cmd", help="command to run")
@click.option("--jobname", help="job name")
@click.option("--time", default="", help="time to run", show_default=True)
@click.option("--image", default="", help="image name")
@click.option("--cpu", default=1, help="CPU")
@click.option("--mem", default="4Gi", help="Memory")
@click.option("--disk", default="10Gi", help="disk size")
@click.option("--mount", default="", help="mount")
@click.option("--readonly", default=True, help="mount read only")
def sub(cmd, jobname, time, image, cpu, mem, disk, mount, readonly):
    batch = makeBatch()
    j = batch.new_job(jobname)

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
            if len(mItems) != 2:
                continue
            else:
                j.cloudfuse(mItems[0], mItems[1], read_only=readonly)
    j.command(f"{cmd} &> {j.output_log}")
    batch.write_output(j.output_log, output_path(jobname + ".log"))
    batch.run(wait=False)


if __name__ == "__main__":
    sub()
