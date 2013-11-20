#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'
__email__ = 'S.Sobko@profitware.ru'
__copyright__ = 'Copyright 2013, The Profitware Group'

from sympy import symbols
from sympy.logic.boolalg import SOPform

from circuitry.exceptions import SignalsNotSpecified, SignalsSubsNotSpecified


class Device(dict):
    mandatory_signals = None
    mandatory_signals_using_subs = None

    def __init__(self, **kwargs):
        signals = dict()
        signals_subs = dict()
        # Iterate over kwargs finding signals and substitutions
        for key, value in kwargs.iteritems():
            if key.endswith('_signals') and isinstance(value, basestring):
                signals.update({key: symbols(value)})
            if key.endswith('_signals_subs') and isinstance(value, dict):
                signals_subs.update({key: value})
        # Find mandatory signals
        if self.mandatory_signals is not None:
            specified_set = set(signals)
            mandatory_set = set(self.mandatory_signals)
            if specified_set & mandatory_set != mandatory_set:
                excepted_set = mandatory_set ^ specified_set & mandatory_set
                raise SignalsNotSpecified(tuple(excepted_set))
        # Find mandatory substitutions
        specified_set = set(signals_subs)
        if self.mandatory_signals_using_subs is not None:
            mandatory_set = set(map(lambda _s: '%s_subs' % _s, self.mandatory_signals_using_subs))
            if specified_set & mandatory_set != mandatory_set:
                excepted_set = mandatory_set ^ specified_set & mandatory_set
                raise SignalsSubsNotSpecified(tuple(excepted_set))
        # Create truth tables and functions by substitutions
        for _subs_name in signals:
            if '%s_subs' % _subs_name in specified_set:
                kwargs.update({'%s_truth_table' % _subs_name:
                               [signals_subs['%s_subs' % _subs_name][str(_name)] for _name in signals[_subs_name]]})
                kwargs.update({'%s_function' % _subs_name:
                               SOPform(signals[_subs_name], [kwargs['%s_truth_table' % _subs_name]])})
        kwargs.update(signals)
        super(Device, self).__init__(**kwargs)

    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            return self.__getattribute__(item)