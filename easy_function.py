#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple fuctions (file, time, numpy)
Last update: KzXuan, 2019.05.27
"""
import os
import json
import codecs as cs
from display_tool import dot


def file_in_dir(path, delete_start=['.']):
    """
    Get all files in path
    Parameters:
    * path [str]: search path
    * delete_start [list]: delete files that start with some symbols
    - file_list [list]: list of all the files
    """
    file_list = os.listdir(path)
    file_list = [ele for ele in file_list if ele[0] not in delete_start]
    return file_list


def load_list(file, desc=None, line_split=False, code='utf-8'):
    """
    Load a file to list
    * file [str]: load file/path
    * desc [str]: a description string
    * line_split [bool]: each line contains one element
    * code [str]: encoding
    - _list [list]: result list
    """
    if desc:
        dot.start("* Load {}".format(desc))
    _list = []
    with cs.open(file, 'r', code) as inobj:
        if line_split:
            for line in inobj:
                ele = json.loads(line)
                _list.append(ele)
        else:
            _list = json.load(inobj)
    if desc:
        dot.stop()
    return _list


def save_list(_list, file, desc=None, line_split=False, code='utf-8'):
    """
    Save a list
    * _list [list]: list for saving
    * file [str]: save file/path
    * desc [str]: a description string
    * line_split [bool]: each line contains one element
    * code [str]: encoding
    """
    if desc:
        dot.start("* Save {}".format(desc))
    with cs.open(file, 'w', code) as outobj:
        if line_split:
            for ele in _list:
                outobj.write(json.dumps(ele) + '\n')
        else:
            json.dump(_list, outobj)
    if desc:
        dot.stop()
    return 1


def load_dict(file, desc=None, line_split=False, code='utf-8'):
    """
    Load a file to dict
    * file [str]: load file/path
    * desc [str]: a description string
    * line_split [bool]: each line contains one element
    * code [str]: encoding
    - _dict [dict]: result dict
    """
    if desc:
        dot.start("* Load {}".format(desc))
    _dict = {}
    with cs.open(file, 'r', code) as inobj:
        if line_split:
            for line in inobj:
                key, value = line.split('\t', 1)
                value = json.loads(value)
                _dict[key] = value
        else:
            _dict = json.load(inobj)
    if desc:
        dot.stop()
    return _dict


def save_dict(_dict, file, desc=None, line_split=False, code='utf-8'):
    """
    Save a dict
    * _dict [dict]: dict for saving
    * file [str]: save file/path
    * desc [str]: a description string
    * line_split [bool]: each line contains one element
    * code [str]: encoding
    """
    if desc:
        dot.start("* Save {}".format(desc))
    with cs.open(file, 'w', code) as outobj:
        if line_split:
            for key, value in _dict.items():
                outobj.write(str(key) + '\t' + json.dumps(value) + '\n')
        else:
            json.dump(_dict, outobj)
    if desc:
        dot.stop()
    return 1


def time_difference(begin, end, form="%a %b %d %H:%M:%S %z %Y"):
    """
    Calculate the time difference between two tweets
    * begin [str]: time string
    * end [str]: time string
    * form [str]: time structure
    - seconds [int]: time difference in seconds
    """
    import datetime as dt
    atime = dt.datetime.strptime(begin, form)
    btime = dt.datetime.strptime(end, form)
    return (btime - atime).seconds


def time_str_stamp(str_time, form="%a %b %d %H:%M:%S %z %Y"):
    """
    Convert time string to stamp number
    * str_time [str]: time string
    * form [str]: time structure
    - time_stamp [int]: unix time stamp
    """
    import time
    time_array = time.strptime(str_time, form)
    time_stamp = int(time.mktime(time_array))
    return time_stamp


def one_hot(arr, n_class=0, padding=0):
    """
    Change labels to one-hot expression
    * arr [np.array]: numpy array
    * n_class [int]: number of class
    * padding [int]: padding size
    - oh [np.array]: numpy array with one-hot expression
    """
    import numpy as np
    if arr is None:
        return None
    if isinstance(arr, list):
        arr = np.array(arr)
    n_class = arr.max() + 1 if n_class == 0 else n_class
    assert n_class >= arr.max() + 1, ValueError("Value of 'n_class' is too small.")
    oh = np.zeros((arr.size, n_class), dtype=int)
    oh[np.arange(arr.size), arr] = 1
    if padding:
        oh = np.vstack((oh, np.zeros((padding, oh.shape[1]), dtype=int)))
    return oh


def remove_zero_rows(arr):
    """
    Remove rows with all zero from an matrix
    * arr [np.array]: matrix with size (-1, n_class)
    - result [np.array]: after removement
    - nonzero_row_indice [np.array]: index of nonzero rows
    """
    assert arr.ndim == 2, "Size error for 'array'."
    nonzero_row_indice, _ = arr.nonzero()
    nonzero_row_indice = np.unique(nonzero_row_indice)
    result = arr[nonzero_row_indice]
    return result, nonzero_row_indice
