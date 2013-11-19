#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'
__email__ = 'S.Sobko@profitware.ru'
__copyright__ = 'Copyright 2013, The Profitware Group'

from sympy.logic import *

from circuitry.devices import Device


class Mux(Device):
    def __init__(self, **kwargs):
        super(Mux, self).__init__(**kwargs)
        self._create_truth_table()

    def _create_truth_table(self):
        def _generate_binary_lines_current(n_bin, i):
            for n in xrange(n_bin, 0, -1):
                if i - 2 ** (n - 1) < 0:
                    yield 0
                else:
                    i -= 2 ** (n - 1)
                    yield 1
        strobe_formula = SOPform(self.strobe_signals,
                                 [[self.strobe_signals_subs[str(_name)] for _name in self.strobe_signals]])
        print strobe_formula
        address_and_data_minterms = list()
        address_and_data_exludes = list()
        for i in range(0, 2 ** len(self.address_signals)):
            address_line = list()
            for address_line_value in _generate_binary_lines_current(len(self.address_signals), i):
                address_line.append(address_line_value)
            data_line = len(self.data_signals) * [0]
            if i < len(data_line):
                data_line[i] = 1
                address_and_data_minterms.append(address_line + data_line)
            else:
                address_and_data_exludes.append(address_line + data_line)
        address_and_data_formula = SOPform(self.address_signals + self.data_signals,
                                           address_and_data_minterms, dontcares=address_and_data_exludes)
        print address_and_data_formula
        print self.address_signals

    def truth_table(self):
        return

    def formula(self):
        return