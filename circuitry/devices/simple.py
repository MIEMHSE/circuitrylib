#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'
__email__ = 'S.Sobko@profitware.ru'
__copyright__ = 'Copyright 2013, The Profitware Group'

from sympy import symbols
from sympy.logic import *

from circuitry.exceptions import LogicFunctionNotSpecified
from circuitry.devices import Device


class DeviceSimple(Device):
    """NOOP device"""
    logic_function = None
    mandatory_signals = ('data_signals', 'output_signals',)
    constraints = {
        'data_signals': {
            'min': 1,
            'max': 10
        },
        'output_signals': {
            'min': 1,
            'max': 10
        }
    }

    def __init__(self, **kwargs):
        super(DeviceSimple, self).__init__(**kwargs)
        self._generate_through_truth_table(signals_list=(self.data_signals,))

    @property
    def functions(self):
        if not self.logic_function:
            return self.data_signals
        return [self.logic_function(*self.data_signals)]


class DeviceNot(DeviceSimple):
    """Logic NOT gate"""
    logic_function = Not
    constraints = {
        'data_signals': {
            'min': 1,
            'max': 10
        },
        'output_signals': {
            'min': 1,
            'max': 10
        }
    }

    @property
    def functions(self):
        return [self.logic_function(signal) for signal in self.data_signals]


class DeviceAnd(DeviceSimple):
    """Logic AND gate"""
    logic_function = And
    constraints = {
        'data_signals': {
            'min': 2,
            'max': 10
        },
        'output_signals': {
            'min': 1,
            'max': 1
        }
    }


class DeviceOr(DeviceSimple):
    """Logic OR gate"""
    logic_function = Or
    constraints = {
        'data_signals': {
            'min': 2,
            'max': 10
        },
        'output_signals': {
            'min': 1,
            'max': 1
        }
    }

def create_simple_device_by_function(device_function, is_topmost=False, save_signal_names=False):
    DeviceClass, _device = None, None
    device_class_dict = {
        'and': DeviceAnd,
        'or': DeviceOr,
        'not': DeviceNot
    }
    device_type = 'common'
    if is_topmost:
        device_type = 'output'
    _method = str(device_function.func).lower()
    if _method in device_class_dict:
        DeviceClass = device_class_dict[_method]
        if _method == 'not':
            if len(device_function.args) == 1 and device_function.args[0].is_Atom:
                device_type = 'input'
        if save_signal_names:
            _signal_names = ','.join(map(str, device_function.args))
        else:
            _signal_names = 'd:%s' % len(device_function.args)
        _device = DeviceClass(data_signals=_signal_names,
                              output_signals='y:1', output_signals_subs=dict(y0=1))
    return device_type, _device


def create_simple_device_by_func_and_number_of_inputs(device_function_token, number_of_inputs, dnum):
    rnd_pins = [symbols('random%s' % (num + number_of_inputs * dnum)) for num in range(0, number_of_inputs)]
    return create_simple_device_by_function(device_function_token(*rnd_pins), save_signal_names=True)
