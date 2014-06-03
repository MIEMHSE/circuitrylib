#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'
__email__ = 'S.Sobko@profitware.ru'
__copyright__ = 'Copyright 2014, The Profitware Group'

from sympy.logic import *

from circuitry.devices import Device
from circuitry.devices.simple import DeviceNot


class DeviceAdd(Device):
    """Adder device"""
    mandatory_signals = ('strobe_signals', 'first_signals',
                         'second_signals', 'output_signals',)
    mandatory_signals_using_subs = ('strobe_signals',)
    truth_table_signals = ('strobe_signals', 'first_signals',
                           'second_signals', 'output_signals',)
    constraints = {
        'strobe_signals': {
            'min': 1,
            'max': 10
        },
        'first_signals': {
            'min': 1,
            'max': 5
        },
        'second_signals': {
            'min': 1,
            'max': 5
        },
        'output_signals': {
            'min': 1,
            'max': 7
        }
    }

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
        self.functions.append(self.strobe_signals_function & Xor(prev_p, current_p))  # Two's complement overflow
        self._generate_through_truth_table(signals_list=(self.first_signals, self.second_signals))


class DeviceInc(Device):
    """Increment device"""
    mandatory_signals = ('strobe_signals', 'data_signals', 'output_signals',)
    mandatory_signals_using_subs = ('strobe_signals',)
    truth_table_signals = ('strobe_signals', 'data_signals', 'output_signals',)
    constraints = {
        'strobe_signals': {
            'min': 1,
            'max': 10
        },
        'data_signals': {
            'min': 1,
            'max': 5
        },
        'output_signals': {
            'min': 1,
            'max': 7
        }
    }

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
            self.functions.append(self.strobe_signals_function & function.subs({'t0': 1}))
        self._generate_through_truth_table(signals_list=(self.data_signals,))


class DeviceDec(Device):
    """Decrement device"""
    mandatory_signals = ('strobe_signals', 'data_signals', 'output_signals',)
    mandatory_signals_using_subs = ('strobe_signals',)
    truth_table_signals = ('strobe_signals', 'data_signals', 'output_signals',)
    constraints = {
        'strobe_signals': {
            'min': 1,
            'max': 10
        },
        'data_signals': {
            'min': 1,
            'max': 5
        },
        'output_signals': {
            'min': 1,
            'max': 7
        }
    }

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
            self.functions.append(self.strobe_signals_function & function.subs(dec_subs))
        self._generate_through_truth_table(signals_list=(self.data_signals,))


class Device12Comp(DeviceInc):
    """Ones' complement to two's complement device"""

    def __init__(self, **kwargs):
        super(Device12Comp, self).__init__(**kwargs)
        for i in range(0, len(self.data_signals)):
            self.functions[i] = And(
                self.strobe_signals_function,
                Or(
                    And(self.data_signals[-1], self.functions[i]),
                    And(Not(self.data_signals[-1]), self.data_signals[i])
                )
            )
        self._generate_through_truth_table(signals_list=(self.data_signals,))


class Device21Comp(DeviceDec):
    """Two's complement to ones' complement device"""

    def __init__(self, **kwargs):
        super(Device21Comp, self).__init__(**kwargs)
        for i in range(0, len(self.data_signals)):
            self.functions[i] = And(
                self.strobe_signals_function,
                Or(
                    And(self.data_signals[-1], self.functions[i]),
                    And(Not(self.data_signals[-1]), self.data_signals[i])
                )
            )
        self._generate_through_truth_table(signals_list=(self.data_signals,))


class DeviceNeg(Device):
    """Negation for two's complement"""
    mandatory_signals = ('strobe_signals', 'data_signals', 'output_signals',)
    mandatory_signals_using_subs = ('strobe_signals',)
    truth_table_signals = ('strobe_signals', 'data_signals', 'output_signals',)
    constraints = {
        'strobe_signals': {
            'min': 1,
            'max': 10
        },
        'data_signals': {
            'min': 1,
            'max': 5
        },
        'output_signals': {
            'min': 1,
            'max': 5
        }
    }

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
                And(
                    self.strobe_signals_function,
                    Or(
                        And(self.data_signals[-1], device_inc.functions[i].subs(subs_dict)),  # Negative
                        And(Not(self.data_signals[-1]), device_not_dec.functions[i].subs(subs_dict))  # Positive
                    )
                )
            )
        self._generate_through_truth_table(signals_list=(self.data_signals,))
