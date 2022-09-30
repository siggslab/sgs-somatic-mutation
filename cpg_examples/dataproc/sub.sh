cd examples/dataproc

analysis-runner \
--dataset fewgenomes \
--access-level test \
--output-dir "$(whoami)-dataproc-example" \
--description "dataproc example" \
main.py
 
