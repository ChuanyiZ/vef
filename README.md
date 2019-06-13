# VEF

Variant Ensemble Filter, an ensemble based filter for VCF files.

VEF is designed for filtering variants of single non-cancerous samples.

## Installation

Installation in a virtual environment is recommended, e.g. [conda](https://conda.io/projects/conda/en/latest/user-guide/getting-started.html).
If you're not using a virtual environment and encounter permission issues when installing packages, please try installing with `--user` option, e.g. `pip install --user -r requirement.txt`.

1. Download
    ```bash
    git clone https://github.com/ChuanyiZ/vef.git
    ```
2. install requirements
    ```bash
    cd vef
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
## Example scripts

Example python scripts are located in `example` directory. There's a `test.sh` script to run them. VCF files for testing are located in `example/data`, including chromosome 11 and 20 of Human sample NA12878 (HG001) (SNPs and INDELs are already separated). You can also download BAM files from [ftp://ftp-trace.ncbi.nlm.nih.gov/giab/ftp/data/NA12878/10XGenomics/](ftp://ftp-trace.ncbi.nlm.nih.gov/giab/ftp/data/NA12878/10XGenomics/) and generate VCF of your own by running GATK's [best practice pipeline](https://software.broadinstitute.org/gatk/best-practices/).

```bash
cd example
./test.sh
```

This bash script calls example script `vef_clf.py` and `vef_apl.py` in `example` directory to train and apply the filter. After running `test.sh`, there will be 2 filter models in `example/data` with `.clf` extension, along with 2 filtered VCF files with `.vef.vcf` extension.

## Usage

### Splitting VCF file into SNPs and INDELs

Use GATK SelectVariants tool to split target VCF file into two files containing SNPs and INDELs separately.

```bash
java -jar <path/to/GenomeAnalysisTK.jar> -T SelectVariants -R <path/to/human_g1k_v37.fasta> -V <path/to/target/vcf> -selectType SNP -o output.snp.vcf
java -jar <path/to/GenomeAnalysisTK.jar> -T SelectVariants -R <path/to/human_g1k_v37.fasta> -V <path/to/target/vcf> -selectType INDEL -o output.indel.vcf
```

For detailed documentation of `SelectVariants`, please go to [GATK's site](https://software.broadinstitute.org/gatk/documentation/tooldocs/3.8-0/org_broadinstitute_gatk_tools_walkers_variantutils_SelectVariants.php)

### Training

Input files:

- `gold_standard.vcf`: GIAB's NA12878 Gold Standard VCF
- `specimen.vcf`: Your NA12878 VCF of produced by sequencing technology, alignment tool, pre-processing tool and variant caller you are using.

1. Use [hap.py](https://github.com/Illumina/hap.py) to compare `specimen.vcf` against `gold_standard.vcf`, output `compare.vcf`.
2. Use `vef_clf.py` in `/example` folder (recommended), where you can specify *number of trees* (default 150) and *name of ensemble methods* (default Random Forest), and see help message for details. Otherwise you can use the VEF package in Python, example snippet as follows.
    ```python
    dataset = VCFDataset(path_to_compare_vcf, path_to_specimen_vcf, 'SNP')
    X, y = dataset.get_dataset('*')

    clf = Classifier(dataset.features, num_trees, "RF")
    clf.fit(X, y)
    clf.save(path_to_specimen_vcf + ".vef_snp.clf")
    ```

### Applying

Input files:

- `classifier.clf`: pre-trained classifier.
- `target.vcf`: target VCF file.

Use `vef_apl.py` in `/example` folder (recommended), or use the VEF package to apply pretrained model on target VCF file, example snippet as follows.

```python
clf = Classifier.load(clf_file)
apply = VCFApply(target_vcf, clf, 'SNP')
apply.apply()
apply.write_filtered(target_vcf + ".vef_snp.vcf")
```

### Grid Search of Hyper-Parameters

See example script `vef_grid_search.py` in `example` folder.
This script will run K-fold cross-validation on the given VCF files and determine the best number of trees and learning rate (for AdaBoost and GBDT).

Input files:

- `gold_standard.vcf`: GIAB's NA12878 Gold Standard VCF.
- `specimen.vcf`: Your NA12878 VCF of produced by sequencing technology, alignment tool, pre-processing tool and variant caller you are using.

Options:

- fold: K-fold cross-validation.
- kind: name of ensemble method.
- jobs: number of parallel jobs.


