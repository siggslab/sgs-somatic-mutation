# deCODE method to detect CH in TOB (deCODE pipeline)
<br>

### What is deCODE method?

deCODE method refers to the method used to identify individuals with clonal hematopoiesis (CH) without candidate driver mutations. It was first described in the [CHIP paper](https://ashpublications.org/blood/article/130/6/742/36791/Clonal-hematopoiesis-with-and-without-candidate) from the deCODE consortium. 
> "CH arises when a substantial proportion of mature blood cells is derived from a single dominant HSC lineage. Somatic mutations in candidate driver (CD) genes are thought to be responsible for at least some cases of CH."    

Briefly, this method extracts (singleton) mutations that occurred only once in their cohort (WGS of 11,262 Icelanders) and imposes a VAF restrictions to identify mosaic somatic mutations. The reason is that for such a large cohort, they believed germline variants were most likely to be observed more than once in their samples. 
 
Although TOB has a much smaller sample size, we can impose a pop AF (allele frequency) restriction to singleton mutations and treated these variants as somatic mutations, which can be used to identify CH carriers.
<br><br>

### Details

First perform QC on TOB's Hail MatrixTable data (following [gnomAD's blog](https://gnomad.broadinstitute.org/news/2020-10-gnomad-v3-1-new-content-methods-annotations-and-data-availability/) and [genebass paper](https://www.sciencedirect.com/science/article/pii/S2666979X22001100?via%3Dihub)); and then apply deCODE method specific filters on the data. After QC, identify singleton mutations & export to a pVCF file used for downstream analysis (i.e., identify CH carriers).

* Step 1 - read & densify mt data
    * Alignment was done with DragMap (?)
    * Cram -> ... -> gVCF (sample-level) -> hail Matrix Table (mt.v7)
    * Read & density mt data 
* Step 2 - Sample-level QC
    * Restrict to samples with imputed sex equals to XX (Female) or XY (Male)
    * Exclude samples if call rate < 0.99 or mean coverage < 20X
    * Exclude related samples
    * Skip sample QC metric outlier filtering
    * Skip ancestry checks (all Europeans)
* Step 3 - Variant-level QC
    * Variant filtering with allele-specific version of GATK Variant Quality Score Recalibration (AS-VQSR, cutoff values can be found in the global fields in TOB-WGS mt data; thresholds differ between SNVs and INDELs)
    * Restrict to bi-allelic variants 
    * Exclude variants with inbreeding coefficient < -0.3 or low quality (GQ < 20, DP < 10)
* Step 4 - deCODE specific filters
    * Exclude variants with call rate < 0.99
    * Identify singleton mutations (mutations that occurred only once in our cohort)
    * Exclude variants with DP < 16 or GQ < 90
    * Exclude variants in simple repeat regions (i.e., defined by combining the entire Simple Tandem Repeats by TRF track in UCSC hg38 with all homopolymer regions in hg38 of length 6bp or more)
* Step 5 - Export to a pVCF file
<br><br>

### How to run this script?

```
# Make sure that one have logged into GCP
gcloud auth application-default login

# activate the environment for running analysis-runner
conda activate CPG
```

Example 1:
```
input="gs://cpg-tob-wgs-test/mt/v7.mt"
outputDir="deCODE"
chr="M"
output="deCODE_test_chr${chr}.vcf.bgz"
cohort_size=11262
simple_repeat_regions="gs://cpg-sgs-somatic-mtn-test-upload/Simple_Repeat_Regions_GRCh38_Excluded_Unmapped_Regions.bed"
ref_ht="gs://cpg-reference/seqr/v0-1/combined_reference_data_grch38-2.0.4.ht"

analysis-runner --dataset sgs-somatic-mtn --access-level test  --output-dir "$outputDir" --description "deCODE" ./tools/sub_dataproc.py \
    --script "deCODE_by_CHR.py --dataset '$input' --chrom chr${chr} --cohort-size ${cohort_size} --gnomad-file '${ref_ht}' --regions-file '${simple_repeat_regions}' --output '$output'" \
    --jobname deCODE_chr$chr
```

Example 2:
```
input="gs://cpg-tob-wgs-main/mt/v7.mt"
outputDir="deCODE"
cohort_size=11262
simple_repeat_regions="gs://cpg-sgs-somatic-mtn-test-upload/Simple_Repeat_Regions_GRCh38_Excluded_Unmapped_Regions.bed"
ref_ht="gs://cpg-reference/seqr/v0-1/combined_reference_data_grch38-2.0.4.ht"

for chr in {{1..22},{'X','Y','M'}}
do
output="deCODE_chr${chr}.vcf.bgz"
analysis-runner --dataset sgs-somatic-mtn --access-level main  --output-dir "$outputDir" --description "deCODE" ./tools/sub_dataproc.py \
    --script "deCODE_by_CHR.py --dataset '$input' --chrom chr${chr} --cohort-size ${cohort_size} --gnomad-file '${ref_ht}' --regions-file '${simple_repeat_regions}' --output '$output'" \
    --jobname deCODE_chr${chr}
done
```
