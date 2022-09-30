cd /Users/zheqia/Documents/Projects/sgs-somatic-mutation/mt

analysis-runner \
--dataset sgs-somatic-mtn \
--access-level test \
--output-dir "$(whoami)-test" \
--description "mt call rate test" \
main.py
