#! /bin/sh
#
# test.sh
# Copyright (C) 2019 Chuanyi Zhang <chuanyi5@illinois.edu>
#
# Distributed under terms of the MIT license.
#

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Showcase of how to use VEF
#
# This bash script calls example script `vef_clf.py` and `vef_apl.py` in
# `example` directory to train and apply the filter. After running `test.sh`,
# there will be 2 filter models in `example/data` with `.clf` extension, along
# with 2 filtered VCF file with `.vef.vcf` extension
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

## SNP
#  Train a model
python vef_clf.py --happy ./data/NA12878_chr11.snp.vcf.gz.happy.vcf.gz \
                  --target ./data/NA12878_chr11.snp.vcf.gz \
                  --mode SNP
# Apply the model
python vef_apl.py --clf_file ./data/NA12878_chr11.snp.vcf.gz.vef_snp.n_150.clf \
                  --subject ./data/NA12878_chr20.snp.vcf.gz \
                  --suffix vef \
                  --mode SNP

## INDEL
#  Train a model
python vef_clf.py --happy ./data/NA12878_chr11.indel.vcf.gz.happy.vcf.gz \
                  --target ./data/NA12878_chr11.indel.vcf.gz \
                  --mode INDEL
#  Apply the model
python vef_apl.py --clf_file ./data/NA12878_chr11.indel.vcf.gz.vef_indel.n_150.clf \
                  --subject ./data/NA12878_chr20.indel.vcf.gz \
                  --suffix vef \
                  --mode INDEL


