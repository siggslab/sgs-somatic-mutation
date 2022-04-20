
import hailtop.batch as hb
import os

BILLING_PROJECT = os.getenv('HAIL_BILLING_PROJECT')
assert BILLING_PROJECT

from cpg_utils.hail import remote_tmpdir

def makeBatch():
    """
    make the batch backend
    """
    # Initializing Batch
    backend = hb.ServiceBackend(
        billing_project=BILLING_PROJECT, remote_tmpdir=remote_tmpdir()
    )
    return hb.Batch(backend=backend, default_image=os.getenv('DRIVER_IMAGE'))

