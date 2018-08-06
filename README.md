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
    cd <path>
    pip install -r requirements.txt
    ```
3. install scikit-allel
    ```bash
    pip install scikit-allel
    ```
4. install using pip
    `pip install ./`

## Usage
Use GATK select-Variants tool to split SNPs and INDELS
```
TODO
```
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
    clf.save(path_to_specimen_vcf + ".RF.n_150.SNP.clf")
    ```

### Applying
- `classifier.clf`: pre-trained classifier.
- `target.vcf`: target VCF file.

```python
clf = Classifier.load(clf_file)
apply = VCFApply(target_vcf, clf, 'SNP')
apply.apply()
apply.write_filtered(target_vcf + ".VEF.vcf")
```

## Caveats
- [hap.py](https://github.com/Illumina/hap.py) needed
- Currently only works for single sample