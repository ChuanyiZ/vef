#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright ÃÂÃÂ© 2018 chuanyi5 <chuanyi5@illinois.edu>
#
# Distributed under terms of the MIT license.

"""
Apply classifiers
"""

import argparse
from vef.core import VCFApply, Classifier

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("clf_file", help="target pipeline VCF file")
    parser.add_argument("subject", help="subject VCF file")
    parser.add_argument("suffix", help="suffix of filtered VCF file")
    parser.add_argument("--mode", help="mode, SNP or INDEL")

    args = parser.parse_args()
    clf_file = args.clf_file
    vcf_sub = args.subject
    suf = args.suffix
    mode = args.mode

    clf = Classifier.load(clf_file)
    apply = VCFApply(vcf_sub, clf, mode)
    apply.apply()
    apply.write_filtered(vcf_sub + f".{suf}.vcf")

if __name__ == '__main__':
    main()
