#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2018 Chuanyi Zhang <chuanyi5@illinois.edu>
#
# Distributed under terms of the MIT license.

"""

"""
import numpy as np
from sklearn.metrics import roc_curve, roc_auc_score


class Metrics(object):
    def __init__(self, label, pred, pred_proba=None):
        if pred_proba is not None:
            self.fpr, self.tpr, _ = roc_curve(label, pred_proba)
            self.auc = roc_auc_score(label, pred_proba)
        else:
            self.auc = float('nan')
        self.TP = float(np.logical_and(label, pred).sum())
        self.FN = float(np.logical_and(label, np.logical_not(pred)).sum())
        self.FP = float(np.logical_and(np.logical_not(label), pred).sum())
        self.TN = float(np.logical_and(np.logical_not(label), np.logical_not(pred)).sum())
        self.accu = (self.TP + self.TN) / (self.TP+self.FP+self.TN+self.FN)
        self.preci = self.TP / (self.TP + self.FP)
        self.sensi = self.TP / (self.TP + self.FN)
        self.f1_measure = 2 * self.TP / (2 * self.TP + self.FP + self.FN)

    def __str__(self):
        return "{:5.0f}  | {:5.0f}  | {:5.0f}  | {:5.0f}  | {:6.2f}% | {:6.2f}% | {:6.2f}% | {:6.2f}% | {:5.3f}".format(
            self.TP, self.FP, self.FN, self.TN, self.accu * 100.0, self.preci * 100.0,
            self.sensi * 100.0, self.f1_measure * 100, self.auc)

    @staticmethod
    def header():
        return "{:6} | {:6} | {:6} | {:6} | {:7} | {:7} | {:7} | {:7} | {:5}".format(
                "TP", "FP", "FN", "TN", "Accurac", "Precisi", "Sensiti", "F1-meas", "AUC")
