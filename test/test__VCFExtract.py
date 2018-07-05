#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2018 Chuanyi Zhang <chuanyi5@illinois.edu>
#
# Distributed under terms of the MIT license.

"""

"""
from unittest import TestCase
from vef.core import _VCFExtract
import numpy as np
from numpy.testing import *


class Test_VCFExtract(TestCase):
    def setUp(self):
        self.test_features = np.array(range(9), dtype=float).reshape([1, -1]).repeat(10, axis=0)
        self.test_features[[3, 7, 2], [5, 6, 0]] = np.nan

    def test_fetch_data(self):
        self.fail()

    def test_mend_nan(self):
        _VCFExtract.mend_nan(self.test_features)
        assert_array_equal(self.test_features[[3, 7, 2], [5, 6, 0]], [5, 6, 0])
