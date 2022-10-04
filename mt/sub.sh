cd /Users/zheqia/Documents/Projects/sgs-somatic-mutation/mt

analysis-runner \
--dataset sgs-somatic-mtn \
--access-level test \
--output-dir "$(whoami)-test" \
--description "mt call rate test" \
main.py

# export pVCF
input="gs://cpg-tob-wgs-test/mt/v7.mt"
outputDir="mt-call-rate-test"
analysis-runner --dataset sgs-somatic-mtn --access-level test  --output-dir "$outputDir" --description "mt call rate test on chr22" sub_dataproc.py \
    --script "shyam.py --dataset '$input'" \
    --jobname convert22

analysis-runner --dataset sgs-somatic-mtn --access-level test  --output-dir "$outputDir" --description "pVCF test" sub_dataproc.py \
    --script "shyam.py --dataset '$input' --output test_pVCF.vcf.bgz" \
    --jobname convert22

