#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'
__email__ = 'S.Sobko@profitware.ru'
__copyright__ = 'Copyright 2013, The Profitware Group'

from sympy import symbols


class Device(dict):
    def __init__(self, **kwargs):
        signals = dict()
        for key, value in kwargs.iteritems():
            if key.endswith('_signals') and isinstance(value, basestring):
                signals.update({key: symbols(value)})
        kwargs.update(signals)
        super(Device, self).__init__(**kwargs)

    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            return self.__getattribute__(item)