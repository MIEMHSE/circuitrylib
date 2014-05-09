#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'
__email__ = 'S.Sobko@profitware.ru'
__copyright__ = 'Copyright 2014, The Profitware Group'

from sympy.logic import *

from circuitry.devices import Device


class DeviceEq(Device):
    """Equality device"""
    mandatory_signals = ('strobe_signals', 'first_signals', 'second_signals', 'output_signals',)
    truth_table_signals = ('strobe_signals', 'first_signals', 'second_signals', 'output_signals',)

    def __init__(self, **kwargs):
        super(DeviceEq, self).__init__(**kwargs)
        functions = [Not(Xor(Ai, Bi)) for Ai, Bi in zip(self.first_signals, self.second_signals)]
        if len(self.output_signals) == 1:
            self.functions = [reduce(And, functions, True)]
        else:
            self.functions = functions
        self.functions = map(lambda Fi: And(self.strobe_signals_function, Fi), self.functions)
        self._generate_through_truth_table(signals_list=(self.first_signals, self.second_signals))


class DeviceCmp(DeviceEq):
    """Digital comparator device"""

    def __init__(self, **kwargs):
        super(DeviceCmp, self).__init__(**kwargs)
        input_signals_len = max(len(self.first_signals), len(self.second_signals))
        functions_eq = self.functions
        functions_eq_parts = [reduce(And, functions_eq[i:], True) for i in range(1, input_signals_len)] + [True]
        function_gt = reduce(Or, [
            And(Ai, Not(Bi), Xi) for Ai, Bi, Xi in zip(self.first_signals, self.second_signals, functions_eq_parts)
        ], False)
        function_lt = reduce(Or, [
            And(Not(Ai), Bi, Xi) for Ai, Bi, Xi in zip(self.first_signals, self.second_signals, functions_eq_parts)
        ], False)
        self.functions = map(lambda Fi: And(self.strobe_signals_function, Fi),
                             [function_lt, reduce(And, functions_eq, True), function_gt])
        self._generate_through_truth_table(signals_list=(self.first_signals, self.second_signals))