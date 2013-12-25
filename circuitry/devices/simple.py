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
    logic_function = None
    mandatory_signals = ('data_signals', 'output_signals',)

    def __init__(self, **kwargs):
        super(DeviceSimple, self).__init__(**kwargs)

    @property
    def function(self):
        if self.logic_function is None:
            raise LogicFunctionNotSpecified(self.__class__)
        return self.logic_function(*self.data_signals)


class DeviceNot(DeviceSimple):
    logic_function = Not


class DeviceAnd(DeviceSimple):
    logic_function = And


class DeviceOr(DeviceSimple):
    logic_function = Or


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


def create_simple_device_by_func_and_number_of_inputs(device_function_token, number_of_inputs):
    return create_simple_device_by_function(
        device_function_token(*[symbols(chr(char)) for char in range(ord('a'), ord('z'))[:number_of_inputs]]))