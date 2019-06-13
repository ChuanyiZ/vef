#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2018 Chuanyi Zhang <chuanyi5@illinois.edu>
#
# Distributed under terms of the MIT license.

"""
Train and save VEF classifiers
"""
import argparse
from vef import VCFDataset, Classifier

def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''\
Train a filter
-------------------------
Example of use

python vef_clf.py --happy path/to/NA12878.vcf.happy.vcf --target path/to/NA12878.vcf --mode SNP --num_trees 150 --kind RF
            ''')
    requiredNamed = parser.add_argument_group("required named arguments")
    requiredNamed.add_argument("--happy", help="hap.py annoted target VCF file", required=True)
    requiredNamed.add_argument("--target", help="target pipeline VCF file", required=True)
    requiredNamed.add_argument("--mode", help="mode, SNP or INDEL", required=True)

    optional = parser.add_argument_group("optional arguments")
    optional.add_argument("-n", "--num_trees", help="number of trees", type=int, default=150)
    optional.add_argument("--kind", choices=["RF", "RandomForest", "AB", "AdaBoost", "GB", "GradientBoost"], type=str, default="RF",
            help="kind of ensemble methods, available values: RandomForest (RF), AdaBoost (AB), GradientBoost(GB); default = RF")

    args = parser.parse_args()
    vcf_hap = args.happy
    vcf_tgt = args.target
    mode = args.mode
    n_trees = args.num_trees
    kind = args.kind
    dataset = VCFDataset(vcf_hap, vcf_tgt, mode)
    X, y = dataset.get_dataset('*')

    clf = Classifier(dataset.features, n_trees, kind)
    clf.fit(X, y)
    clf.save(vcf_tgt + ".vef_{}_{}.n_{}.clf".format(mode.lower(), kind, n_trees))

if __name__ == '__main__':
    main()
