#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2018 Chuanyi Zhang <chuanyi5@illinois.edu>
#
# Distributed under terms of the MIT license.

"""
Apply classifiers
"""

import argparse
from vef import VCFApply, Classifier

def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''\
Apply a pre-trained filter
-------------------------
Example of use

python vef_apl.py --clf_file path/to/NA12878.vcf.vef_snp.clf --subject path/to/subject.snp.vcf --suffix vef --mode SNP
            ''')
    requiredNamed = parser.add_argument_group("required named arguments")
    requiredNamed.add_argument("--clf_file", help="target pipeline VEF filter model", required=True)
    requiredNamed.add_argument("--subject", help="subject VCF file", required=True)
    requiredNamed.add_argument("--suffix", help="suffix of filtered VCF file", required=True)
    requiredNamed.add_argument("--mode", help="mode, SNP or INDEL", choices=["SNP", "INDEL"], required=True)

    args = parser.parse_args()
    clf_file = args.clf_file
    vcf_sub = args.subject
    suf = args.suffix
    mode = args.mode

    clf = Classifier.load(clf_file)
    apply = VCFApply(vcf_sub, clf, mode)
    apply.apply()
    apply.write_filtered(vcf_sub + ".{}.vcf".format(suf))

if __name__ == '__main__':
    main()
