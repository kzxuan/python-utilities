#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Predict data analysis
Last update: KzXuan, 2019.05.28
"""
import numpy as np
import pandas as pd
np.seterr(divide='ignore', invalid='ignore')


class prfacc(object):
    """
    Get evaluation metric P/R/F/Acc
    """
    @classmethod
    def analysis(cls, true, pred, one_hot=False, ndigits=4):
        """
        Analysis the predict by calculation
        * true [np.array/list]: true label size of (n_sample,) / (n_sample, n_class)
        * pred [np.array/list]: predict label size of (n_sample,) / (n_sample, n_class)
        * one_hot [bool]: (n_sample, n_class) input needs True
        * ndigits [int]: decimal number for float
        - results [dict]: dict of all the evaluation metric
        """
        cls.true = np.array(true) if isinstance(true, list) else true
        cls.pred = np.array(pred) if isinstance(pred, list) else pred

        if one_hot:
            assert cls.true.ndim == 2 and cls.pred.ndim == 2, "Dimension error."
            cls.true = np.argmax(cls.true, axis=1)
            cls.pred = np.argmax(cls.pred, axis=1)
        else:
            assert cls.true.ndim == 1 and cls.pred.ndim == 1, "Dimension error."
        assert cls.true.shape == cls.pred.shape, "Dimension error."

        cls.n_class = max(np.max(cls.true), np.max(cls.pred)) + 1
        col = ['C{}'.format(i) for i in range(cls.n_class)] + ['Mi', 'Ma']

        # all class statistic
        cls.true_class = np.array([np.sum(cls.true == i) for i in range(cls.n_class)])
        cls.pred_class = np.array([np.sum(cls.pred == i) for i in range(cls.n_class)])
        true_pred = true[np.argwhere((true == pred) == True).flatten()]
        cls.true_pred = np.array([np.sum(true_pred == i) for i in range(cls.n_class)])

        # add mean value for micro
        cls.true_class = np.append(cls.true_class, np.mean(cls.true_class))
        cls.pred_class = np.append(cls.pred_class, np.mean(cls.pred_class))
        cls.true_pred = np.append(cls.true_pred, np.mean(cls.true_pred))

        # calculate class and micro prf
        cls.precision = np.round(np.nan_to_num(cls.true_pred / cls.pred_class, 0), ndigits)
        cls.recall = np.round(np.nan_to_num(cls.true_pred / cls.true_class, 0), ndigits)
        cls.f1 = np.round(np.nan_to_num((2. * cls.precision * cls.recall) / (cls.precision + cls.recall), 0), ndigits)

        # add sum value
        cls.true_class = np.append(cls.true_class, np.sum(cls.true_class[:-1], dtype=int))
        cls.pred_class = np.append(cls.pred_class, np.sum(cls.pred_class[:-1], dtype=int))
        cls.true_pred = np.append(cls.true_pred, np.sum(cls.true_pred[:-1], dtype=int))

        # calculate accuracy
        cls.accuracy = round(cls.true_pred[-1] / cls.true_class[-1], ndigits)

        # calculate macro prf
        macro_p, macro_r = np.mean(cls.precision[:-1]), np.mean(cls.recall[:-1])
        cls.precision = np.append(cls.precision, round(macro_p, ndigits))
        cls.recall = np.append(cls.recall, round(macro_r, ndigits))
        cls.f1 = np.append(cls.f1, round(np.nan_to_num((2. * macro_p * macro_r) / (macro_p + macro_r), 0), ndigits))

        cls.results = {"Acc": cls.accuracy, "Correct": cls.true_pred[:-2].astype(int)}
        cls.results.update(**{"{}-P".format(col[i]): cls.precision[i] for i in range(len(col))})
        cls.results.update(**{"{}-R".format(col[i]): cls.recall[i] for i in range(len(col))})
        cls.results.update(**{"{}-F".format(col[i]): cls.f1[i] for i in range(len(col))})

        return cls.results

    @classmethod
    def tabular(cls, class_name=None):
        """
        Make table expression
        * class_name [list]: name of each class
        - table [pd.frame]: a pandas table of all the evaluation metric
        """
        assert hasattr(cls, "true"), "Need prfacc.analysis() first."
        class_name = class_name if class_name else list(range(cls.n_class))
        assert len(class_name) == cls.n_class, ValueError("Length error of 'class_name'.")
        class_name = class_name + ["micro/avg", "macro/sum"]
        accuracy = [''] * (cls.n_class + 1) + [str(cls.accuracy)]
        _tab = [cls.true_pred, cls.pred_class, cls.true_class, cls.precision, cls.recall, cls.f1, accuracy]

        index = ["correct", "predict", "label", "precision", "recall", "f1-score", "accuracy"]
        table = pd.DataFrame(_tab, index=index, columns=class_name)
        return table
