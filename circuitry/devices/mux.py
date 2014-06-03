#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'
__email__ = 'S.Sobko@profitware.ru'
__copyright__ = 'Copyright 2013, The Profitware Group'

from sympy.logic import *

from circuitry.devices import Device
from . import generate_binary_lines_current


class DeviceMux(Device):
    """Multiplexer device"""
    mandatory_signals = ('strobe_signals', 'address_signals',
                         'data_signals', 'output_signals',)
    mandatory_signals_using_subs = ('strobe_signals', 'output_signals',)
    truth_table_signals = ('strobe_signals', 'address_signals',
                           'data_signals', 'output_signals',)
    constraints = {
        'strobe_signals': {
            'min': 1,
            'max': 10
        },
        'address_signals': {
            'min': 1,
            'max': 5
        },
        'data_signals': {
            'min': 1,
            'max': 32
        },
        'output_signals': {
            'min': 1,
            'max': 1
        }
    }

    def __init__(self, **kwargs):
        super(DeviceMux, self).__init__(**kwargs)
        address_and_data_minterms = list()
        address_and_data_exludes = list()
        self.truth_table = list()
        for i in range(0, 2 ** len(self.address_signals)):
            address_line = list()
            for address_line_value in generate_binary_lines_current(len(self.address_signals), i):
                address_line.append(address_line_value)
            address_line.reverse()
            data_line = len(self.data_signals) * [0]
            if i < len(data_line):
                data_line[i] = 1
                y_line = self.output_signals_truth_table
                address_and_data_minterms.append(address_line + data_line)
            else:
                address_and_data_exludes.append(address_line + data_line)
                y_line = map(lambda _y: 1 - _y, self.output_signals_truth_table)
            self.truth_table.append((self.strobe_signals_truth_table, address_line, data_line, y_line))
        self.address_and_data_function = SOPform(self.address_signals + self.data_signals,
                                                 address_and_data_minterms, dontcares=address_and_data_exludes)
        self.functions = [self.strobe_signals_function & self.address_and_data_function]


class DeviceDemux(Device):
    """Demultiplexer device"""
    mandatory_signals = ('strobe_signals', 'address_signals',
                         'data_signals', 'output_signals',)
    mandatory_signals_using_subs = ('strobe_signals', 'data_signals',
                                    'output_signals')
    truth_table_signals = ('strobe_signals', 'address_signals',
                           'data_signals', 'output_signals',)
    constraints = {
        'strobe_signals': {
            'min': 1,
            'max': 10
        },
        'address_signals': {
            'min': 1,
            'max': 5
        },
        'data_signals': {
            'min': 1,
            'max': 1
        },
        'output_signals': {
            'min': 1,
            'max': 32
        }
    }

    def __init__(self, **kwargs):
        super(DeviceDemux, self).__init__(**kwargs)
        address_and_data_minterms = list()
        address_and_data_exludes = list()
        self.truth_table = list()
        self.functions = list()
        for i in range(0, 2 ** len(self.address_signals)):
            address_line = list()
            for address_line_value in generate_binary_lines_current(len(self.address_signals), i):
                address_line.append(address_line_value)
            address_line.reverse()
            data_line = len(self.output_signals) * [0]
            if i < len(data_line):
                data_line[i] = 1
                y_line = self.data_signals_truth_table
                address_and_data_minterms.append(address_line + data_line)
            else:
                address_and_data_exludes.append(address_line + data_line)
                y_line = map(lambda _y: 1 - _y, self.data_signals_truth_table)
            self.truth_table.append((self.strobe_signals_truth_table, address_line, y_line, data_line))
            if y_line[0] != 0:
                address_and_data_function = SOPform(self.address_signals + self.data_signals, [address_line + y_line])
                self.functions.append(self.strobe_signals_function & address_and_data_function)
