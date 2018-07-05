#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2018 Chuanyi Zhang <chuanyi5@illinois.edu>
#
# Distributed under terms of the MIT license.

"""

"""
import vef
import argparse
from unittest import TestCase, main


class TestVCFDataset(TestCase):
    def setUp(self):
        pass

    def test_compare(self):
        self.fail()

    def test_get_dataset(self):
        self.fail()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("happy", help="hap.py annoted VCF file")
    parser.add_argument("target", help="target pipeline VCF file")

    args = parser.parse_args()
    vcf_hap = args.happy
    taget = args.target
    main()
