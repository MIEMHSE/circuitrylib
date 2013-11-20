#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'
__email__ = 'S.Sobko@profitware.ru'
__copyright__ = 'Copyright 2013, The Profitware Group'

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


class DeviceNand(DeviceSimple):
    logic_function = Nand


class DeviceNor(DeviceSimple):
    logic_function = Nor
