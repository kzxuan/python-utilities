#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Some tools for optimizing output
Last update: KzXuan, 2019.05.27
"""
import os
import sys
import tqdm
import time
import threading


class config():
    visible = 2


def sysprint(_str):
    """
    Print without '\n
    * _str [str]: string to output
    """
    sys.stdout.write(_str)
    sys.stdout.flush()


def seconds_str(seconds):
    """
    Convert seconds to time string
    * seconds [int]: number of seconds
    - _time [str]: time format string
    """
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return "{:02d}:{:02d}:{:02d}".format(int(h), int(m), int(s))
    else:
        return "{:02d}:{:02d}".format(int(m), int(s))


class timer(object):
    """
    Record the run time of the program
    """
    def __str__(self):
        return f"# {self.__class__} records run time. Use timer.start()/timer.stop()."

    @classmethod
    def start(cls, desc="* Start run ...", visible=1):
        """
        Record the start time
        * desc [str]: a description string
        """
        cls.visible = visible
        if cls.visible > config.visible:
            return
        cls.begin = time.time()
        if desc:
            print(desc)

    @classmethod
    def stop(cls, desc="- Run time"):
        """
        Record the stop time
        * desc [str]: a description string
        """
        if cls.visible > config.visible:
            return
        assert hasattr(cls, "begin"), "Need timer.start() first."
        cls.end = time.time()
        print(desc, seconds_str(cls.end - cls.begin))


class wait(object):
    """
    Base class for wait animation
    """
    def __init__(self, desc=None, visible=1):
        """
        Initialize
        * desc [str]: a description string
        """
        self.desc = desc
        self.visible = visible

    def __call__(self, func, *args, **kwargs):
        """
        Decorator function
        * func [func]: function
        """
        def wrapper(*args, **kwargs):
            self.start(self.desc, self.visible)
            func(*args, **kwargs)
            self.stop()
        return wrapper

    def __str__(self):
        return f"# {self.__class__} outputs waiting. Use slash.start()/slash.stop()."

    def start(self, desc, visible):
        pass

    def stop(self):
        pass


class slash(wait):
    """
    Print /-\| when the program is running
    """
    def __output(self):
        while self.flag:
            sysprint("\b/")
            time.sleep(0.1)
            sysprint("\b-")
            time.sleep(0.1)
            sysprint("\b\\")
            time.sleep(0.1)
            sysprint("\b|")
            time.sleep(0.1)

    @classmethod
    def start(cls, desc=None, visible=1):
        """
        Record the start
        * desc [str]: a description string
        """
        cls.visible = visible
        if cls.visible > config.visible:
            return
        cls.flag = 1
        if desc:
            sysprint(desc + "  ")
        cls.pr = threading.Thread(target=cls.__output, args=(cls, ))
        cls.pr.setDaemon(True)
        cls.pr.start()
        cls.begin = time.time()

    @classmethod
    def stop(cls):
        """
        Record the stop
        * desc [str]: a description string
        """
        if cls.visible > config.visible:
            return
        assert hasattr(cls, "begin"), "Need slash.start() first."
        cls.flag = 0
        cls.pr.join()
        cls.end = time.time()
        print("\b" + u"\u2713", seconds_str(cls.end - cls.begin))


class dot(wait):
    """
    Print ... when the program is running
    """
    def __output(self):
        while self.flag:
            if self.count == 6:
                sysprint('\b' * 6 + ' ' * 6 + '\b' * 6)
                self.count = 0
                time.sleep(0.5)
            else:
                sysprint(".")
                self.count += 1
                time.sleep(0.5)

    @classmethod
    def start(cls, desc=None, visible=1):
        """
        Record the start
        * desc [str]: a description string
        """
        cls.visible = visible
        if cls.visible > config.visible:
            return
        cls.flag, cls.count = 1, 0
        if desc:
            sysprint(desc + " ")
        cls.pr = threading.Thread(target=cls.__output, args=(cls, ))
        cls.pr.setDaemon(True)
        cls.pr.start()
        cls.begin = time.time()

    @classmethod
    def stop(cls):
        """
        Record the stop
        * desc [str]: a description string
        """
        if cls.visible > config.visible:
            return
        assert hasattr(cls, "begin"), "Need slash.start() first."
        cls.flag = 0
        cls.pr.join()
        cls.end = time.time()
        print("\b" * cls.count + u"\u2713", seconds_str(cls.end - cls.begin))


def bar(_list, desc=None, leave=True, visible=1):
    """
    Print progress bar and time in a loop
    * _list [int/list]: a list for loop
    * desc [str]: a description string
    * leave [bool]: leave the bar or not after loop
    """
    if visible > config.visible:
        return
    bar_format = "{l_bar}{bar}|[{elapsed}-{remaining}]"
    columns = int(os.popen('stty size', 'r').read().split()[1])
    ncols = columns // 2 if columns // 2 > 50 else 50

    if isinstance(_list, int):
        _list = list(range(_list))
    if isinstance(_list, dict):
        _list = list(_list.items())
    if not isinstance(_list, list):
        raise TypeError("Type error of '_list', want int/list, get {}.".format(type(_list)))

    for i in tqdm.tqdm(_list, desc=desc, leave=leave, ncols=ncols, ascii=True, bar_format=bar_format):
        yield i


class table(object):
    """
    Print table style
    """
    def __init__(self, col, place='^', sep='|', ntrunc=8, ndigits=4, visible=2):
        """
        Initialize
        * col [int/list]: number of columns or list of column names
        * place [str/list]: one alignment mark '^'/'<'/'>' or list of each col mark
        * sep [str]: separate mark like ' '/'|'/'*'
        * ntrunc [int]: maximun length allowed for int/float
        * ndigits [int]: decimal number for float
        """
        self.visible = visible
        if self.visible > config.visible:
            return None
        self._col(col)
        self._place(place)
        self._sep(sep)
        self.ntrunc = ntrunc
        self.ndigits = ndigits
        self.width = [0] * self.n_col
        self.cache = []
        self.falg = False
        print()
        self._header()

    def __str__(self):
        return f"# {self.__class__} prints table row-by-row."

    def _col(self, col):
        """
        Initialize column number or name
        * col [int/list]: number of columns or list of column names
        """
        if isinstance(col, list):
            self.col = col
            self.n_col = len(col)
        elif isinstance(col, int):
            self.col = None
            self.n_col = col
        else:
            raise TypeError("Type error of 'place', col int/list, get {}.".format(type(col)))

    def _place(self, place):
        """
        Initialize alignment mark
        * place [str/list]: one alignment mark '^'/'<'/'>' or list of each col mark
        """
        if isinstance(place, str):
            self.place = [place for i in range(self.n_col)]
        elif isinstance(place, list):
            if len(place) != self.n_col:
                raise ValueError("Length error of 'place'.")
            self.place = place
        else:
            raise TypeError("Type error of 'place', want str/list, get {}.".format(type(place)))

    def _sep(self, sep):
        """
        Initialize separate mark
        * sep [str]: separate mark like ' '/'|'/'*'
        """
        if sep != ' ':
            sep = ' ' + sep + ' '
        self.sep = [sep] * (self.n_col + 1)

    def _header(self):
        """
        Print header line if need
        """
        if self.col:
            self.row(self.col)

    def _str_row(self, value):
        """
        Convert a row to string
        * value [list]: list of column value
        """
        _str = []
        for ind, val in enumerate(value):
            if isinstance(val, float) and val >= 10 ** self.ntrunc:
                val = int(val)
            if isinstance(val, float):
                val = "{:.{}f}".format(val, self.ndigits)
            elif isinstance(val, int):
                _l = len(str(val))
                val = "{:.{}e}".format(val, self.ntrunc - 6) if _l > self.ntrunc else str(val)
            elif not isinstance(val, str):
                val = str(val)

            if len(val) > self.width[ind]:
                self.width[ind] = len(val)
                self.flag = True

            _str.append(val)
        return _str

    def _print_row(self, value):
        """
        Print a row
        * value [list]: list of column value
        """
        for ind, val in enumerate(value):
            sysprint(self.sep[ind])
            sysprint("{:{}{}}".format(val, self.place[ind], self.width[ind]))
        print(self.sep[-1])

    def _flash_cache(self):
        """
        Re-print all rows
        """
        sysprint('\x1b[{}A'.format(len(self.cache)))
        for _str in self.cache:
            self._print_row(_str)

    def row(self, values):
        """
        Process and print a row
        * values [list/dict]: list/dict of column value
        """
        if self.visible > config.visible:
            return
        if isinstance(values, list):
            assert len(values) == self.n_col, ValueError("Length error of the input row.")
            _str = self._str_row(values)
        elif isinstance(values, dict):
            assert self.col, TypeError("No column names for query.")
            n_values = []
            for cn in self.col:
                if cn in values.keys():
                    n_values.append(values[cn])
                else:
                    n_values.append('-')
            _str = self._str_row(n_values)
        else:
            raise TypeError("Type error of 'values', want list/dict, get {}.".format(type(values)))


        if self.flag:
            self._flash_cache()
        self._print_row(_str)
        self.cache.append(_str)
