#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2017 chuanyi5 <chuanyi5@illinois.edu>
#
# Distributed under terms of the MIT license.

"""

"""
import argparse
# from core import VCFDataset, VCFApply, Classifier
from vef.core import VCFDataset, VCFApply, Classifier

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("happy", help="hap.py annoted VCF file")
    parser.add_argument("target", help="target pipeline VCF file")
    parser.add_argument("subject", help="subject VCF file")

    args = parser.parse_args()
    vcf_hap = args.happy
    vcf_tgt = args.target
    vcf_sub = args.subject

    dataset = VCFDataset(vcf_hap, vcf_tgt, 'SNP')
    X, y = dataset.get_dataset('*')

    clf = Classifier(dataset.features)
    clf.fit(X, y)
    clf.save(vcf_tgt + ".RF")

    apply = VCFApply(vcf_sub, clf)
    apply.apply()
    apply.write_filtered(vcf_sub + ".VEFiltered.vcf")
