#! /bin/sh
#
# test.sh
# Copyright (C) 2019 Chuanyi Zhang <chuanyi5@illinois.edu>
#
# Distributed under terms of the MIT license.
#

python vef_clf.py --happy ./data/NA12878_chr11.snp.vcf.gz.happy.vcf.gz --target ./data/NA12878_chr11.snp.vcf.gz --mode SNP
python vef_apl.py --clf_file ./data/NA12878_chr11.snp.vcf.gz.vef_snp.n_150.clf --subject ./data/NA12878_chr20.snp.vcf.gz --suffix vef --mode SNP
python vef_clf.py --happy ./data/NA12878_chr11.indel.vcf.gz.happy.vcf.gz --target ./data/NA12878_chr11.indel.vcf.gz --mode INDEL
python vef_apl.py --clf_file ./data/NA12878_chr11.indel.vcf.gz.vef_indel.n_150.clf --subject ./data/NA12878_chr20.indel.vcf.gz --suffix vef --mode INDEL


