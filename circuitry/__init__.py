#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'
__email__ = 'S.Sobko@profitware.ru'
__copyright__ = 'Copyright 2013, The Profitware Group'


def generate_binary_lines_current(n_bin, i):
    for n in xrange(n_bin, 0, -1):
        if i - 2 ** (n - 1) < 0:
            yield 0
        else:
            i -= 2 ** (n - 1)
            yield 1