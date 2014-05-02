#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'
__email__ = 'S.Sobko@profitware.ru'
__copyright__ = 'Copyright 2014, The Profitware Group'

from sympy.logic import *

from circuitry import generate_binary_lines_current
from circuitry.devices import Device


class DeviceAdder(Device):
    """Adder device"""
    mandatory_signals = ('strobe_signals', 'first_signals', 'second_signals', 'output_signals',)
    truth_table_signals = ('strobe_signals', 'first_signals', 'second_signals', 'output_signals',)

    def __init__(self, **kwargs):
        super(DeviceAdder, self).__init__(**kwargs)
        function_s = lambda vx, vy, vp: Xor(vx, vy, vp)
        function_p = lambda vx, vy, vp: Or(And(vx, vy), And(vx, vp), And(vy, vp))
        self.functions = list()
        current_p = 0
        for i in range(0, max(len(self.first_signals), len(self.second_signals))):
            try:
                x = self.first_signals[i]
            except IndexError:
                x = 0
            try:
                y = self.second_signals[i]
            except IndexError:
                y = 0
            current_s = function_s(x, y, current_p)
            current_p = function_p(x, y, current_p)
            self.functions.append(self.strobe_signals_function & current_s)
        self.functions.append(self.strobe_signals_function & current_p)
        self.truth_table = list()
        input_signals_len = len(self.first_signals) + len(self.second_signals)
        for i in range(0, 2 ** input_signals_len):
            first_line, second_line = list(), list()
            value_index = 0
            for line_value in generate_binary_lines_current(input_signals_len, i):
                if value_index < len(self.first_signals):
                    first_line.append(line_value)
                else:
                    second_line.append(line_value)
                value_index += 1
            line_subs = dict()
            for i in range(0, len(self.first_signals)):
                line_subs[str(self.first_signals[i])] = first_line[i]
            for i in range(0, len(self.second_signals)):
                line_subs[str(self.second_signals[i])] = second_line[i]
            line_subs.update(self.strobe_signals_subs)
            y_line = list()
            for i in range(0, len(self.output_signals)):
                y_line.append(1 if self.functions[i].subs(line_subs) else 0)
            self.truth_table.append((self.strobe_signals_truth_table, first_line, second_line, y_line))