#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2018 Chuanyi Zhang <chuanyi5@illinois.edu>
#
# Distributed under terms of the MIT license.

"""

"""
import unittest
import numpy as np
import os
from numpy.testing import *
from vef.core import _VCFExtract

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


class Test_VCFExtract(unittest.TestCase):
    def setUp(self):
        self.test_features = np.array(range(9), dtype=float).reshape([1, -1]).repeat(10, axis=0)
        self.test_features[[3, 7, 2], [5, 6, 0]] = np.nan
        self.extract = _VCFExtract(os.path.join(THIS_DIR, 'test.vcf'))
        print('pass')

    def test_VCFExtract_init(self):
        # assert_array_equal()
        assert_array_equal(self.extract.fields,
                           ['variants/CHROM', 'variants/POS', 'variants/ID', 'variants/REF', 'variants/ALT',
                            'variants/QUAL', 'variants/AC', 'variants/AF', 'variants/AN', 'variants/BaseQRankSum',
                            'variants/ClippingRankSum', 'variants/DP', 'variants/DS', 'variants/ExcessHet',
                            'variants/FS',
                            'variants/HaplotypeScore', 'variants/InbreedingCoeff', 'variants/MLEAC', 'variants/MLEAF',
                            'variants/MQ', 'variants/MQRankSum', 'variants/QD', 'variants/ReadPosRankSum',
                            'variants/ReverseComplementedAlleles', 'variants/SOR', 'variants/SwappedAlleles',
                            'variants/FILTER_PASS', 'variants/FILTER_LowQual', 'variants/numalt', 'variants/svlen',
                            'variants/is_snp', 'calldata/AD', 'calldata/DP', 'calldata/GQ', 'calldata/GT',
                            'calldata/PL'])
        assert_array_equal(self.extract.samples, ['HG002'])

    def test_fetch_data(self):
        snp_data, snp_features, snp_index = self.extract.fetch_data('SNP')
        assert_array_equal(snp_data.shape, [180, len(snp_features)])
        assert_array_almost_equal(np.nanmean(snp_data, 0),
                                  [1.3833333333333333, 0.69166666666666665, 2.0, 0.1069292078635334, 0.0,
                                   16.222222222222221, 3.0102999210357666, 1.9231666498714024, np.nan, np.nan,
                                   1.3833333333333333, 0.69166666666666665, 57.938888910081651, -0.12651327529312234,
                                   19.085222208499907, 0.051823009876946435, 1.2972499992698432, 76299425.311111107,
                                   277.73833200666638])

    def test_mend_nan(self):
        _VCFExtract.mend_nan(self.test_features)
        assert_array_equal(self.test_features[[3, 7, 2], [5, 6, 0]], [5, 6, 0])


if __name__ == '__main__':
    unittest.main()