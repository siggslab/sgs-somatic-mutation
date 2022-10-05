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
    --script "scripts/mt_vcf3.py --dataset '$input' --chrom chr${chr} --output densify_chr${chr}.vcf.bgz" \
    --jobname convert$chr

