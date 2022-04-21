import hailtop.batch as hb
from analysis_runner.git import (
  prepare_git_job,
  get_repo_name_from_current_directory,
  get_git_commit_ref_of_current_repository,
)

b = hb.Batch('do-some-analysis')
j = b.new_job('checkout_repo')
prepare_git_job(
  job=j,
  # you could specify a name here, like 'analysis-runner'
  repo_name=get_repo_name_from_current_directory(),
  # you could specify the specific commit here, eg: '1be7bb44de6182d834d9bbac6036b841f459a11a'
  commit=get_git_commit_ref_of_current_repository(),
)

# Now, the working directory of j is the checkout out repository
j.command(f'ls ./ &> {j.output_log}')
b.write_output(j.output_log, output_path("test_git.log"))
b.run(wait=False)


