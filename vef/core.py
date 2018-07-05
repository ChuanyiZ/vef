#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2018 Chuanyi ZHang <chuanyi5@illinois.edu>
#
# Distributed under terms of the MIT license.

"""

"""
import allel
import time
import logging
import csv
import os
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib

FORMAT = '%(levelname)-7s %(asctime)-15s %(name)-15s %(message)s'
logging.basicConfig(level='INFO', format=FORMAT)


class _VCFExtract:
    def __init__(self, filepath):
        self.filepath = filepath
        self.fields, self.samples, self.header, _ = allel.iter_vcf_chunks(filepath, fields='*')
        self.features = None
        self.variants = None
        self.logger = logging.getLogger(self.__class__.__name__)

    def fetch_data(self, mode, features=None):
        """
        Args:
            mode (str):
            features (list):

        Returns:
            data (Numpy.array):
            features (list):
            vartype_index (Numpy.array):
        """
        VAR_PREFIX = 'variants/'
        if features is None:
            # fields, samples, self.header, _ = allel.iter_vcf_chunks(self.filepath, fields='*')
            fields = [(VAR_PREFIX + k) for k in list(self.header.infos.keys()) + ['CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL']]
            data = allel.read_vcf(self.filepath, fields='*')
            self.features = [ftr for ftr in fields if np.issubdtype(data[ftr].dtype, np.number)]
        else:
            self.features = features
            # _features = [(VAR_PREFIX + ftr) if '/' not in ftr else ftr for ftr in self.features]
            # fields, samples, self.header, _ = allel.iter_vcf_chunks(self.filepath, fields='*')
            for i in list(self.features):
                if i not in self.fields:
                    self.logger.error("Error: {} field not in {}, we have {}".format(i, self.filepath, self.fields))
                    # print("Error: {} field not in {}".format(i, self.filepath))
                    exit(-1)
            data = allel.read_vcf(self.filepath, fields='*')
        if mode.upper() == 'SNP':
            is_vartype = data[VAR_PREFIX + 'is_snp']
        elif mode.upper() == 'INDEL':
            is_vartype = np.logical_not(data[VAR_PREFIX + 'is_snp'])
        elif mode.upper() == 'BOTH':
            is_vartype = np.repeat(True, data[VAR_PREFIX + 'is_snp'].shape[0])
        else:
            self.logger.warning("No such mode {}, using mode SNP.".format(mode))
            is_vartype = np.repeat(True, data[VAR_PREFIX + 'is_snp'].shape[0])
        vartype_index = np.where(is_vartype)[0]
        annotes = [data[ftr][is_vartype] for ftr in features]
        annotes = np.vstack((c if c.ndim == 1 else c[:, 0] for c in annotes))
        return annotes.transpose(), self.features, vartype_index

    @staticmethod
    def mend_nan(features, axis=1):
        mean = np.nanmean(features, axis=0)
        nan_idx = np.where(np.isnan(features))
        features[nan_idx] = mean[nan_idx[1]]


class VCFDataset:
    def __init__(self, hap_filepath, target_filepath, mode):
        self.hap_vcf = _VCFExtract(hap_filepath)
        self.target_vcf = _VCFExtract(target_filepath)
        self.dataset = {}
        self.contigs = []
        self.features = []
        self.logger = logging.getLogger(self.__class__.__name__)
        self._compare(mode)

    @staticmethod
    def _extract_factory(truth_idx, vartype):
        """
        Create function that check if this variant is vartype
        Args:
            truth_idx (Numpy.array): the index of 'TRUTH' in list of samples in outcome of hap.py
            vartype (str): variant type, SNP or INDEL

        Returns:
            function: the function that check if vartype
        """
        def inner(arr):
            if arr[truth_idx] == vartype and arr[1 - truth_idx] == vartype:
                return 1
            elif arr[truth_idx] == 'NOCALL' and arr[1 - truth_idx] == vartype:
                return 0
            else:
                return -1
        return inner

    def _compare(self, mode: str):
        self.logger.info("Start extracting label from {}".format(os.path.abspath(self.hap_vcf.filepath)))
        VAR_PREFIX = 'variants/'
        # fields, samples, headers, _ = allel.iter_vcf_chunks(self.hap_vcf, fields='*')
        mode_list = ['SNP', 'INDEL']
        data = allel.read_vcf(self.hap_vcf.filepath, fields=['calldata/BVT', 'variants/Regions', 'variants/POS', 'variants/CHROM'])
        conf_mask = data['variants/Regions'].astype(bool)
        # data, _, _ = self.hap_vcf.fetch_data('BOTH', ['calldata/BVT', 'variants/POS', 'variants/CHROM'])
        if mode.upper() in mode_list:
            extract_target_vartype = self._extract_factory(np.where(self.hap_vcf.samples == 'TRUTH')[0][0], mode.upper())
        else:
            self.logger.warning("Warning: mode {} not exist. Using SNP mode.".format(mode))
            extract_target_vartype = self._extract_factory(np.where(self.hap_vcf.samples == 'TRUTH')[0][0], 'SNP')
            # print("Warning: {}".format(mode))

        vartype = np.apply_along_axis(extract_target_vartype, 1, data['calldata/BVT'][conf_mask, :])
        label_list = np.vstack((data['variants/POS'][conf_mask], vartype))
        idx = (vartype != -1)
        label_list = label_list[:, idx]
        chrom_list = data['variants/CHROM'][conf_mask][idx]
        chroms = np.unique(chrom_list)
        label_list = {chrom: label_list[:, np.where(chrom_list == chrom)[0]] for chrom in chroms}
        for key in label_list:
            _, idx, cnt = np.unique(label_list[key][0, :], return_index=True, return_counts=True)
            label_list[key] = label_list[key][:, idx[cnt <= 1]]
        self.logger.info("Finish extracting label from file")
        # label_list = label_list[:, np.argsort(label_list[0, :], kind='mergesort')]

        # save
        # with open(truth_idx_file, 'wb') as f:
        #     pickle.dump(
        #         label_list, f, protocol=pickle.HIGHEST_PROTOCOL)
        # return label_list

        # fields, samples, headers, _ = allel.iter_vcf_chunks(self.target_vcf.filepath, fields='*')
        # fields = [k for k in list(headers.infos.keys()) + ['QUAL']]
        data = allel.read_vcf(self.target_vcf.filepath, fields='*')
        # data, fields, _ = self.target_vcf.fetch_data(mode)

        self.logger.info("Start extracting variants from {}".format(os.path.abspath(self.target_vcf.filepath)))
        # feature selection
        num_var = np.shape(data[VAR_PREFIX + 'REF'])[0]
        self.features = [(VAR_PREFIX + k) for k in list(self.target_vcf.header.infos.keys()) + ['QUAL']]
        self.features = [ftr for ftr in self.features if np.issubdtype(data[ftr].dtype, np.number)]
        self.features = [ftr for ftr in self.features if np.sum(np.isnan(data[ftr])) < 0.01 * num_var]
        self.features = [ftr for ftr in self.features if np.nanvar(data[ftr]) >= 0.1]
        features_avoid = [VAR_PREFIX + 'VQSLOD']
        for ftr in features_avoid:
            if ftr in self.features:
                self.features.remove(ftr)
        self.features.sort()

        # merge features, with CHROM, POS
        annotes = [data[ftr] for ftr in [VAR_PREFIX + 'POS'] + self.features]
        annotes = np.vstack((c if c.ndim == 1 else c[:, 0] for c in annotes))
        chrom_list = data[VAR_PREFIX + 'CHROM']
        self.contigs = list(label_list)
        annotes_chrom = {ch: annotes[:, np.where(chrom_list == ch)[0]] for ch in self.contigs}

        # # merge labels
        # if label_list is None:
        #     if truth_idx_file is not None:
        #         with open(truth_idx_file, 'rb') as of:
        #             label_list = pickle.load(of)
        #     else:
        #         print("ERR: no 'truth file' or 'truth index list' usable.")
        #         exit(1)

        for ch in self.contigs:
            if ch not in label_list:
                continue
            else:
                annotes_idx = np.where(np.isin(annotes_chrom[ch][0], label_list[ch][0]))[0]
                label_idx = np.where(np.isin(label_list[ch][0], annotes_chrom[ch][0]))[0]
                self.dataset[ch] = np.vstack((annotes_chrom[ch][1:, annotes_idx], label_list[ch][1, label_idx])).transpose()
                self.logger.debug("CHROM:{}, {} {}".format(ch, np.shape(annotes_chrom[ch][1:, annotes_idx]), np.shape(label_list[ch][1, label_idx])))
                idx = ~np.any(np.isnan(self.dataset[ch]), axis=1)
                self.dataset[ch] = {'X': self.dataset[ch][idx, :-1], 'y': self.dataset[ch][idx, -1]}
        # np.savez_compressed(dataset_file, infos=features, chrom_data=dataset)
        self.logger.info("Finish extracting variants from file")
        return self

    def get_dataset(self, contigs):
        """
        Return features and labels of request contigs. If contigs is '*', return all data.
        Args:
            contigs (str):

        Returns:

        """
        if '*' in list(contigs):
            contig_list = self.contigs
        else:
            contig_list = []
            if type(contigs) is not list:
                contigs = [contigs]
            for ctg in contigs:
                if ctg not in self.contigs:
                    self.logger.warning("Requested contig {} not exist.".format(ctg))
                contig_list.append(ctg)
        X = np.vstack((self.dataset[ctg]['X'] for ctg in contig_list))
        y = np.hstack((self.dataset[ctg]['y'] for ctg in contig_list))
        return X, y

    def save(self, output_filepath):
        np.savez_compressed(output_filepath, dataset=self.dataset)
        self.logger.info("Dataset saved to file {}".format(os.path.abspath(output_filepath)))

    @staticmethod
    def load(dataset_filepath):
        return np.load(dataset_filepath)


class Classifier(RandomForestClassifier):
    def __init__(self, features, n_trees=150):
        super().__init__(criterion='gini', max_depth=20, n_estimators=n_trees)
        self.features = features

    def fit(self, X, y, sample_weight=None):
        logger = logging.getLogger(self.__class__.__name__)
        logger.info("Begin training model")
        t0 = time.time()
        super().fit(X, y, sample_weight=sample_weight)
        logger.debug("Importance: {}".format(super().feature_importances_))
        t1 = time.time()
        logger.info("Finish training model")
        logger.info("Elapsed time {:.3f}s".format(t1 - t0))

    def save(self, output_filepath):
        logger = logging.getLogger(self.__class__.__name__)
        joblib.dump(self, output_filepath)
        logger.info("Classfier saved at {}".format(os.path.abspath(output_filepath)))

    @staticmethod
    def load(classifier_path):
        return joblib.load(classifier_path)


class VCFApply(_VCFExtract):
    def __init__(self, filepath, classifier: Classifier, vartype):
        super().__init__(filepath)
        self.classifier = classifier
        self.vartype = vartype
        self.data, _, self.vartype_index = self.fetch_data("BOTH", self.classifier.features) # temp
        self.mend_nan(self.data)
        self.predict_y = None
        self.logger = logging.getLogger(self.__class__.__name__)

        # check features
        this_feature = set(self.features)
        clf_feature = set(self.classifier.features)
        # sym_diff = this_feature.symmetric_difference(clf_feature)
        if this_feature != clf_feature:
            if len(clf_feature - this_feature) == 0:
                pass
            self.logger.warning("Features not match! Missing features: {}, excessive features: {}".format(this_feature - clf_feature, clf_feature - this_feature))

    def apply(self):
        self.predict_y = self.classifier.predict(self.data)
        self.predict_y_log_proba = self.classifier.predict_log_proba(self.data)

    def write_filtered(self, output_filepath):
        """
        Write filtered VCF file, SNPs only and change the FILTER field to PASS or VEF_FILTERED
        Args:
            output_filepath:

        Returns:

        """
        # pass_index = self.vartype_index[np.where(self.predict_y == 1)[0]]

        # if len(pass_index) == 0:
        if np.sum(self.predict_y) == 0:
            self.logger.error("No passed variants.")
            # print("Attention! No passed variants.")
            return
        # last_pass_index = max(pass_index)
        # is_pass = np.zeros(len_is_pass)
        # is_pass[pass_index] = 1
        chunk_size = 10000
        self.logger.info("Start output filtered result to file {}".format(os.path.abspath(output_filepath)))
        t0 = time.time()
        chunk = []
        with open(self.filepath, 'r') as infile, open(output_filepath, 'w') as outfile:
            # iterate headers
            if self.vartype == 'SNP':
                is_vartype = lambda x, y: len(x) == 1 and len(y) == 1
            else:
                is_vartype = lambda x, y: not(len(x) == 1 and len(y) == 1)

            filter_written = False
            for line in infile:
                if line.startswith("##"):
                    if 'FILTER' in line and not filter_written:
                        chunk.append('##FILTER=<ID=VEF_FILTERED,Description="VEF filtered">\n')
                        chunk.append('##INFO=<ID=VEF,Number=1,Type=Float,Description="Log Probability of being true variants according to VEF">\n')
                        filter_written = True
                    chunk.append(line)
                elif line.startswith("#"):
                    fields = line[1:].split()
                    chunk.append(line)
                    outfile.write(''.join(chunk))
                    chunk = []
                    break
            idx_FILTER = fields.index("FILTER")
            idx_REF = fields.index("REF")
            idx_ALT = fields.index("ALT")
            idx_INFO = fields.index("INFO")
            vcf_reader = csv.reader(infile, delimiter='\t')
            for num_row, row in enumerate(vcf_reader):
                # if is_vartype(row[idx_REF], row[idx_ALT]):
                # if num_row <= last_pass_index:
                    # if is_pass[num_row]:
                if self.predict_y[num_row]:
                    row[idx_FILTER] = "PASS"
                    row[idx_INFO] += (";VEF={:.4e}".format(self.predict_y_log_proba[num_row, 1]))
                else:
                    row[idx_FILTER] = "VEF_FILTERED"
                    row[idx_INFO] += (";VEF={:.4e}".format(self.predict_y_log_proba[num_row, 1]))
                # else:
                #     row[idx_FILTER] = "VEF_FILTERED"
                chunk.append(row)
                if num_row % chunk_size == 0 and num_row > 0:
                    outfile.write('\n'.join(['\t'.join(var) for var in chunk]) + '\n')
                    chunk = []
            outfile.write('\n'.join(['\t'.join(var) for var in chunk]))
        t1 = time.time()
        self.logger.info("Finish output filtered result, time elapsed {:.3f}s".format(t1 - t0))
        # print("Time elapsed {}s".format(t1 - t0))
