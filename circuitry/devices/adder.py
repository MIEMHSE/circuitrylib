#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'
__email__ = 'S.Sobko@profitware.ru'
__copyright__ = 'Copyright 2014, The Profitware Group'

from sympy.logic import *

from circuitry import generate_binary_lines_current, output_truth_table
from circuitry.devices import Device
from circuitry.devices.simple import DeviceNot


class DeviceAdd(Device):
    """Adder device"""
    mandatory_signals = ('strobe_signals', 'first_signals', 'second_signals', 'output_signals',)
    truth_table_signals = ('strobe_signals', 'first_signals', 'second_signals', 'output_signals',)

    def __init__(self, **kwargs):
        super(DeviceAdd, self).__init__(**kwargs)
        function_s = lambda vx, vy, vp: Xor(vx, vy, vp)
        function_p = lambda vx, vy, vp: Or(And(vx, vy), And(vx, vp), And(vy, vp))
        self.functions = list()
        current_p, prev_p = 0, 0
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
            prev_p = current_p
            current_p = function_p(x, y, current_p)
            self.functions.append(self.strobe_signals_function & current_s)
        self.functions.append(self.strobe_signals_function & current_p)  # Overflow
        self.functions.append(Xor(prev_p, current_p))  # Invalid state function for twos' complementary (overflow)
        self.truth_table = list()
        input_signals_len = len(self.first_signals) + len(self.second_signals)
        for bin_i in range(0, 2 ** input_signals_len):
            first_line, second_line = list(), list()
            value_index = 0
            for line_value in generate_binary_lines_current(input_signals_len, bin_i):
                if value_index < len(self.first_signals):
                    first_line.append(line_value)
                else:
                    second_line.append(line_value)
                value_index += 1
            first_line.reverse()
            second_line.reverse()
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


class DeviceInc(Device):
    """Increment device"""
    mandatory_signals = ('strobe_signals', 'data_signals', 'output_signals',)
    truth_table_signals = ('strobe_signals', 'data_signals', 'output_signals',)

    def __init__(self, **kwargs):
        super(DeviceInc, self).__init__(**kwargs)
        inc_dict = kwargs.copy()
        inc_dict.update({
            'first_signals': 't:1',
            'second_signals': kwargs['data_signals']
        })
        inc_adder = DeviceAdd(**inc_dict)
        self.functions = list()
        for function in inc_adder.functions[:len(self.output_signals)]:
            self.functions.append(function.subs({'t0': 1}))
        self.truth_table = list()
        for truth_table_line in inc_adder.truth_table:
            _, first_line, second_line, y_line = truth_table_line
            if first_line[0]:
                self.truth_table.append((self.strobe_signals_truth_table, second_line,
                                         y_line[:len(self.output_signals)]))


class DeviceDec(Device):
    """Decrement device"""
    mandatory_signals = ('strobe_signals', 'data_signals', 'output_signals',)
    truth_table_signals = ('strobe_signals', 'data_signals', 'output_signals',)

    def __init__(self, **kwargs):
        super(DeviceDec, self).__init__(**kwargs)
        dec_dict = kwargs.copy()
        dec_dict.update({
            'first_signals': 't:%d' % len(self.data_signals),
            'second_signals': kwargs['data_signals']
        })
        dec_adder = DeviceAdd(**dec_dict)
        self.functions = list()
        dec_subs = {'t%d' % i: 1 for i in range(0, len(self.data_signals))}
        for function in dec_adder.functions[:len(self.output_signals)]:
            self.functions.append(function.subs(dec_subs))
        self.truth_table = list()
        for truth_table_line in dec_adder.truth_table:
            _, first_line, second_line, y_line = truth_table_line
            if reduce(lambda x, y: x and y, first_line):
                self.truth_table.append((self.strobe_signals_truth_table, second_line,
                                         y_line[:len(self.output_signals)]))


class Device12Comp(DeviceInc):
    """Ones' complementary to twos' complementary device"""

    def __init__(self, **kwargs):
        super(Device12Comp, self).__init__(**kwargs)
        for i in range(0, len(self.data_signals)):
            self.functions[i] = Or(
                And(self.data_signals[-1], self.functions[i]),
                And(Not(self.data_signals[-1]), self.data_signals[i])
            )
        truth_table = list()
        for truth_table_line in self.truth_table:
            _, data_line, _ = truth_table_line
            line_subs = dict()
            for i in range(0, len(self.data_signals)):
                line_subs[str(self.data_signals[i])] = data_line[i]
            line_subs.update(self.strobe_signals_subs)
            y_line = list()
            for i in range(0, len(self.output_signals)):
                y_line.append(1 if self.functions[i].subs(line_subs) else 0)
            truth_table.append((self.strobe_signals_truth_table, data_line, y_line))
        self.truth_table = truth_table


class Device21Comp(DeviceDec):
    """Twos' complementary to ones' complementary device"""

    def __init__(self, **kwargs):
        super(Device21Comp, self).__init__(**kwargs)
        for i in range(0, len(self.data_signals)):
            self.functions[i] = Or(
                And(self.data_signals[-1], self.functions[i]),
                And(Not(self.data_signals[-1]), self.data_signals[i])
            )
        truth_table = list()
        for truth_table_line in self.truth_table:
            _, data_line, _ = truth_table_line
            line_subs = dict()
            for i in range(0, len(self.data_signals)):
                line_subs[str(self.data_signals[i])] = data_line[i]
            line_subs.update(self.strobe_signals_subs)
            y_line = list()
            for i in range(0, len(self.output_signals)):
                y_line.append(1 if self.functions[i].subs(line_subs) else 0)
            truth_table.append((self.strobe_signals_truth_table, data_line, y_line))
        self.truth_table = truth_table


class DeviceNeg(Device):
    """Negation for twos' complementary"""
    mandatory_signals = ('strobe_signals', 'data_signals', 'output_signals',)
    truth_table_signals = ('strobe_signals', 'data_signals', 'output_signals',)

    def __init__(self, **kwargs):
        super(DeviceNeg, self).__init__(**kwargs)
        not_inc_kwargs = kwargs.copy()
        not_inc_kwargs['data_signals'] = 'n' + not_inc_kwargs['data_signals'][1:]
        device_not_inc = DeviceNot(**not_inc_kwargs)
        inc_kwargs = kwargs.copy()
        inc_kwargs['data_signals'] = 'i' + inc_kwargs['data_signals'][1:]
        device_inc = DeviceInc(**inc_kwargs)
        dec_kwargs = kwargs.copy()
        dec_kwargs['data_signals'] = 'm' + dec_kwargs['data_signals'][1:]
        device_dec = DeviceDec(**dec_kwargs)
        not_dec_kwargs = kwargs.copy()
        not_dec_kwargs['data_signals'] = 'b' + not_dec_kwargs['data_signals'][1:]
        device_not_dec = DeviceNot(**not_dec_kwargs)
        self.functions = list()
        subs_dict = dict()
        for i in range(0, len(self.data_signals)):
            subs_dict[str(device_not_inc.data_signals[i])] = self.data_signals[i]
            subs_dict[str(device_inc.data_signals[i])] = device_not_inc.functions[i].subs(subs_dict)
            subs_dict[str(device_dec.data_signals[i])] = self.data_signals[i]
            subs_dict[str(device_not_dec.data_signals[i])] = device_dec.functions[i].subs(subs_dict)
            self.functions.append(
                Or(
                    And(self.data_signals[-1], device_inc.functions[i].subs(subs_dict)),  # Negative
                    And(Not(self.data_signals[-1]), device_not_dec.functions[i].subs(subs_dict))  # Positive
                )
            )
        truth_table = list()
        for truth_table_line in device_dec.truth_table:
            _, data_line, _ = truth_table_line
            line_subs = dict()
            for i in range(0, len(self.data_signals)):
                line_subs[str(self.data_signals[i])] = data_line[i]
            line_subs.update(self.strobe_signals_subs)
            y_line = list()
            for i in range(0, len(self.output_signals)):
                y_line.append(1 if self.functions[i].subs(line_subs) else 0)
            truth_table.append((self.strobe_signals_truth_table, data_line, y_line))
        self.truth_table = truth_table
