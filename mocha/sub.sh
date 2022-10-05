#### run export pVCF
input="gs://cpg-tob-wgs-test/mt/v7.mt"
outputDir=""
analysis-runner --dataset sgs-somatic-mtn --access-level test  --output-dir "$outputDir" --description "Call rate test" sub_dataproc.py \
    --script "tests/shyam.py --dataset '$input'" \
    --jobname convert_test

#### run export pVCF
input="gs://cpg-tob-wgs-test/mt/v7.mt"
outputDir="mt-call-rate-test"
chr=22
analysis-runner --dataset sgs-somatic-mtn --access-level test  --output-dir "$outputDir" --description "pVCF" sub_dataproc.py \
    --script "scripts/write_plot_data2.py --dataset '$input' --chrom chr${chr} --output call_rate_figure_data.csv" \
    --jobname convert$chr

