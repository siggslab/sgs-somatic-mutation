## Successful
input="gs://cpg-tob-wgs-test/mt/v7.mt"
outputDir="mt-call-rate-test"
chr=22
analysis-runner --dataset sgs-somatic-mtn --access-level test  --output-dir "$outputDir" --description "pVCF" sub_dataproc.py \
    --script "scripts/mt_vcf.py --dataset '$input' --chrom chr${chr} --output Check_chr${chr}.vcf.bgz" \
    --jobname convert$chr



#### run export pVCF
input="gs://cpg-tob-wgs-test/mt/v7.mt"
outputDir="mt-call-rate-test"
chr=22
analysis-runner --dataset sgs-somatic-mtn --access-level test  --output-dir "$outputDir" --description "test" sub_dataproc.py \
    --script "scripts/mt_vcf2.py --dataset '$input' --chrom chr${chr} --output CheckCheck_chr${chr}.vcf.bgz" \
    --jobname convert$chr


#### run export pVCF
input="gs://cpg-tob-wgs-test/mt/v7.mt"
outputDir="mt-call-rate-test"
chr=22
analysis-runner --dataset sgs-somatic-mtn --access-level test  --output-dir "$outputDir" --description "pVCF" sub_dataproc.py \
    --script "scripts/write_plot_data2.py --dataset '$input' --chrom chr${chr} --output call_rate_figure_data.csv" \
    --jobname convert$chr

