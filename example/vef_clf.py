#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright ÃÂÃÂÃÂÃÂ© 2018 chuanyi5 <chuanyi5@illinois.edu>
#
# Distributed under terms of the MIT license.

"""
Train and save VEF classifiers
"""
import argparse
from vef.core import VCFDataset, Classifier

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("happy", help="hap.py annoted VCF file")
    parser.add_argument("target", help="target pipeline VCF file")
    parser.add_argument("--mode", help="mode, SNP or INDEL")

    args = parser.parse_args()
    vcf_hap = args.happy
    vcf_tgt = args.target
    mode = args.mode
    dataset = VCFDataset(vcf_hap, vcf_tgt, mode)
    X, y = dataset.get_dataset('*')

    clf = Classifier(dataset.features)
    clf.fit(X, y)
    clf.save(vcf_tgt + f".RF.n_150.{mode}.clf")

if __name__ == '__main__':
    main()
