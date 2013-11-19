#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'
__email__ = 'S.Sobko@profitware.ru'
__copyright__ = 'Copyright 2013, The Profitware Group'

from sympy import symbols

from circuitry.exceptions import SignalsNotSpecified


class Device(dict):

    mandatory_signals = None

    def __init__(self, **kwargs):
        signals = dict()
        for key, value in kwargs.iteritems():
            if key.endswith('_signals') and isinstance(value, basestring):
                signals.update({key: symbols(value)})
        if self.mandatory_signals is not None:
            specified_set = set(signals)
            mandatory_set = set(self.mandatory_signals)
            if specified_set & mandatory_set != mandatory_set:
                excepted_set = mandatory_set ^ specified_set & mandatory_set
                raise SignalsNotSpecified(tuple(excepted_set))
        kwargs.update(signals)
        super(Device, self).__init__(**kwargs)

    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            return self.__getattribute__(item)