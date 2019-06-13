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
Find best parameters for VEF
-------------------------
Example of use

python vef_grid_search.py --happy path/to/NA12878.vcf.happy.vcf --target path/to/NA12878.vcf --mode SNP --fold 5 --jobs 2 --kind RF
            ''')
    requiredNamed = parser.add_argument_group("required named arguments")
    requiredNamed.add_argument("--happy", help="hap.py annoted target VCF file", required=True)
    requiredNamed.add_argument("--target", help="target pipeline VCF file", required=True)
    requiredNamed.add_argument("--mode", help="mode, SNP or INDEL", required=True)

    optional = parser.add_argument_group("optional arguments")
    optional.add_argument("--fold", help="number of k-fold cross validation, default = 5", type=int, default=5)
    optional.add_argument("--jobs", help="number of parallel process, default = 1", type=int, default=1)
    optional.add_argument("--kind", choices=["RF", "RandomForest", "AB", "AdaBoost", "GB", "GradientBoost"], type=str, default="RF",
            help="kind of ensemble methods, available values: RandomForest (RF), AdaBoost (AB), GradientBoost(GB); default = RF")

    args = parser.parse_args()
    vcf_hap = args.happy
    vcf_tgt = args.target
    mode = args.mode
    kind = args.kind
    fold = args.fold
    jobs = args.jobs

    print(f"Kind: {kind}, fold: {fold}, jobs: {jobs}")

    dataset = VCFDataset(vcf_hap, vcf_tgt, mode)
    X, y = dataset.get_dataset('*')

    clf = Classifier(dataset.features, kind=kind)
    clf.gridsearch(X, y, fold, jobs)
    # clf.save(vcf_tgt + ".vef_{}_grid.clf".format(mode.lower()))

if __name__ == '__main__':
    main()
