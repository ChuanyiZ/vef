# VEF

Variant Ensemble Filter, an ensemble based filter for VCF files.

## Installation

Installing in a virtual environmant is recommended.

1. Download
    ```bash
    git clone git@github.com:ChuanyiZ/vef.git
    ```
2. install requirements
    ```bash
    cd <path/to/vef>
    pip install -r requirements.txt
    ```
3. install scikit-allel
    ```bash
    pip install scikit-allel
    ```
4. install VEF using pip
    ```bash
    pip install ./
    ```

## Usage

Use GATK SelectVariants tool to split target VCF file into two files containing SNPs and INDELs separately.

```bash
java -jar <path/to/GenomeAnalysisTK.jar> -T SelectVariants -R <path/to/human_g1k_v37.fasta> -V <path/to/target/vcf> -selectType SNP -o output.snp.vcf
java -jar <path/to/GenomeAnalysisTK.jar> -T SelectVariants -R <path/to/human_g1k_v37.fasta> -V <path/to/target/vcf> -selectType INDEL -o output.indel.vcf
```

For detail document, go to [GATK's site](https://software.broadinstitute.org/gatk/documentation/tooldocs/3.8-0/org_broadinstitute_gatk_tools_walkers_variantutils_SelectVariants.php)

### Training

Ingredients:

- `gold_standard.vcf`: GIAB's NA12878 Gold Standard VCF
- `specimen.vcf`: Your NA12878 VCF of produced by sequencing technology, alignment tool, pre-processing tool and variant caller you are using.

1. Use [hap.py](https://github.com/Illumina/hap.py) to compare `specimen.vcf` against `gold_standard.vcf`, output `compare.vcf`.
2. Use the VEF package, example snippet as follows, or see `vef_clf.py` in `/example` folder.
    ```python
    dataset = VCFDataset(path_to_compare_vcf, path_to_specimen_vcf, 'SNP')
    X, y = dataset.get_dataset('*')

    clf = Classifier(dataset.features)
    clf.fit(X, y)
    clf.save(path_to_specimen_vcf + ".vef_snp.clf")
    ```

### Applying

- `classifier.clf`: pre-trained classifier.
- `target.vcf`: target VCF file.

```python
clf = Classifier.load(clf_file)
apply = VCFApply(target_vcf, clf, 'SNP')
apply.apply()
apply.write_filtered(target_vcf + ".vef_snp.vcf")
```

## Caveats

- [hap.py](https://github.com/Illumina/hap.py) needed
- Currently only works for single samples
