# VEF

Variant Ensemble Filter, an ensemble based filter for VCF files.

VEF is designed for filtering variants of single non-cancerous samples.

**bioRxiv**: <https://doi.org/10.1101/540286>

All VCF files used for analysis of VEF can be accessed here: <https://doi.org/10.13012/B2IDB-9401259_V1>

## Installation

Installation in a virtual environment is recommended, e.g., [conda](https://conda.io/projects/conda/en/latest/user-guide/getting-started.html).
If you're not using a virtual environment and encounter permission issues when installing packages, please try installing with `--user` option, e.g., `pip install --user -r requirement.txt`.

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

Example python scripts are located in the `example/` directory. There's a `test.sh` script to run them. VCF files for testing are located in `example/data`, including chromosome 11 and 20 of Human sample NA12878 (HG001) (SNPs and INDELs are already separated). You can also download the corresponding BAM files from [ftp://ftp-trace.ncbi.nlm.nih.gov/giab/ftp/data/NA12878/10XGenomics/](ftp://ftp-trace.ncbi.nlm.nih.gov/giab/ftp/data/NA12878/10XGenomics/) and generate the VCF files on your own by running GATK's [best practice pipeline](https://software.broadinstitute.org/gatk/best-practices/).

```bash
cd example
./test.sh
```

This bash script calls example script `vef_clf.py` and `vef_apl.py` located in the `example/` directory to train and apply the filter, respectively. After running `test.sh`, there will be 2 filter models in `example/data` with the `.clf` extension, along with 2 filtered VCF files with the `.vef.vcf` extension.

The generated `*.vef.vcf` files include a `VEF` score in the INFO field for each variant. This score represents the probability of the variant being correct, calculated by the model. In particular, if $P$ is the probability of being correct, VEF reports the score $\ln(P)$ as `VEF` score. VEF also specifies `VEF_FILTERED` in the FILTER field of the variants that VEF estimates are incorrectly called.

## Usage

### Splitting VCF file into SNPs and INDELs

Use GATK SelectVariants tool to split the target VCF file into two files containing SNPs and INDELs separately. For example, if we have a target VCF file `specimen.vcf`:

```bash
java -jar GenomeAnalysisTK.jar -T SelectVariants -R reference.fasta -V specimen.vcf -selectType SNP -o specimen.snp.vcf
java -jar GenomeAnalysisTK.jar -T SelectVariants -R reference.fasta -V specimen.vcf -selectType INDEL -o specimen.indel.vcf
```

For detailed documentation of `SelectVariants`, please go to [GATK's site](https://software.broadinstitute.org/gatk/documentation/tooldocs/3.8-0/org_broadinstitute_gatk_tools_walkers_variantutils_SelectVariants.php)

### Training

Input files:

- `gold_standard.vcf`, `gold_standard.bed`, `reference.fasta`: for example, GIAB's NA12878 Gold Standard's VCF and BED files, and the corresponding reference file.
- `specimen.snp.vcf` or `specimen.indel.vcf`: for example, a VCF file from sample NA12878 produced by the sequencing technology and analysis pipeline of interest.

Steps:

1. Use [hap.py](https://github.com/Illumina/hap.py) to compare `specimen.snp.vcf` (or `specimen.indel.vcf`) against the `gold_standard.vcf`, and output `compare.snp.vcf` (or `compare.indel.vcf`). Example:

    ```bash
    python2 hap.py gold_standard.vcf specimen.snp.vcf -f gold_standard.bed -o compare.snp.vcf -r reference.fasta --no-roc
    ```

2. Use `vef_clf.py` in the `example/` folder (recommended), where you can specify *number of trees* (default 150) and the *ensemble method* (default RF).

    ```bash
    python vef_clf.py --happy compare.snp.vcf --target specimen.snp.vcf --mode SNP --kind <MODEL_NAME> --n <NUM_TREES>

    required named arguments:
      --happy HAPPY         annotated training VCF file (from hap.py)
      --target TARGET       training VCF file
      --mode {SNP,INDEL}    mode: SNP or INDEL

    optional arguments:
      -n NUM_TREES, --num_trees NUM_TREES
                              number of trees, default = 150
      --kind {RF,RandomForest,AB,AdaBoost,GB,GradientBoost}
                              kind of ensemble method, available options:
                              RandomForest (RF), AdaBoost (AB), GradientBoost(GB);
                              default = RF
      -h, --help            show this help message and exit
    ```

    MODE must be either SNP or INDEL, model is RF (Random Forest), AB (AdaBoost), or GB (GradientBoost), and NUM_TREES should be an integer. By default, RF with 150 base learners is used. See help message for details.

Otherwise you can directly write your own Python script, example snippet as follows.

```python
from vef import VCFDataset, Classifier
dataset = VCFDataset(path_to_compare_vcf, path_to_specimen_vcf, 'SNP')
X, y = dataset.get_dataset('*')

clf = Classifier(dataset.features, num_trees, "RF")
clf.fit(X, y)
clf.save(path_to_specimen_vcf + ".vef_snp.clf")
```

### Applying

Input files:

- `classifier.clf`: pre-trained classifier.
- `target.snp.vcf` or `target.indel.vcf`: target VCF file.

Use `vef_apl.py` in `example/` folder (recommended).

```bash
python vef_apl.py --clf_file classifier.clf --subject target.snp.vcf --suffix vef --mode SNP

optional arguments:
  -h, --help           show this help message and exit

required named arguments:
  --clf_file CLF_FILE  VEF filter pre-trained model
  --subject SUBJECT    target VCF file
  --suffix SUFFIX      suffix of filtered VCF file
  --mode {SNP,INDEL}   mode: SNP or INDEL

```

MODE must be either SNP or INDEL.

Alternatively, use the VEF package to apply the pre-trained model on the target VCF file. Example snippet as follows.

```python
from vef import VCFApply, Classifier
clf = Classifier.load(clf_file)
apply = VCFApply(target_vcf, clf, 'SNP')
apply.apply()
apply.write_filtered(target_vcf + ".vef_snp.vcf")
```

### Grid Search of Hyperparameters

See example script `vef_grid_search.py` in the `example/` folder.
This script will run K-fold cross-validation on the given VCF files and determine the best number of trees and learning rate.

Input files: (same as training)

- `gold_standard.vcf`, `gold_standard.bed`, `reference.fasta`: for example, GIAB's NA12878 Gold Standard's VCF and BED files, and the corresponding reference file.
- `specimen.snp.vcf` or `specimen.indel.vcf`: for example, a VCF file from sample NA12878 produced by the sequencing technology and analysis pipeline of interest.

Steps: (similar to training)

1. Use [hap.py](https://github.com/Illumina/hap.py) to compare `specimen.snp.vcf` (or `specimen.indel.vcf`) against `gold_standard.vcf`, output `compare.snp.vcf` (or `compare.indel.vcf`).

    ```bash
    python2 hap.py gold_standard.vcf specimen.vcf -f gold_standard.bed -o compare.vcf -r reference.fasta --no-roc
    ```

2. Use `vef_grid_search.py` in `example/` folder, where you can specify the *ensemble method* (default RF).

    ```bash
    python vef_grid_search.py --happy compare.snp.vcf --target specimen.snp.vcf --mode SNP --fold 5 --jobs 2 --kind <MODEL_NAME>

    optional arguments:
    -h, --help            show this help message and exit

    required named arguments:
    --happy HAPPY         annotated training VCF file (by hap.py)
    --target TARGET       training VCF file
    --mode MODE           mode: SNP or INDEL

    optional arguments:
    --fold FOLD           number of k-fold cross validation, default = 5
    --jobs JOBS           number of parallel processes, default = 1
    --kind {RF,RandomForest,AB,AdaBoost,GB,GradientBoost}
                            kind of ensemble method, available options:
                            RandomForest (RF), AdaBoost (AB), GradientBoost(GB);
                            default = RF
    ```

    MODE must be either SNP or INDEL; FOLD and JOBS are integers, and the number of parallel jobs (processes) should be less than or equal to the number of virtual cores on your computer.

