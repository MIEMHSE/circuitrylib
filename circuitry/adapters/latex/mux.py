#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'
__email__ = 'S.Sobko@profitware.ru'
__copyright__ = 'Copyright 2013, The Profitware Group'

from circuitry.adapters.latex import TruthTableAdapter


class DeviceMuxTruthTableAdapter(TruthTableAdapter):
    @property
    def _truth_table(self):
        device = self._device
        truth_table = device.truth_table
        strobe_signals_add = list()
        for i in range(0, len(device.strobe_signals)):
            strobe_signals_anti_truth_table = ['x'] * len(device.strobe_signals)
            strobe_signals_anti_truth_table[i] = 1 - device.strobe_signals_truth_table[i]
            strobe_signals_add.append(tuple([strobe_signals_anti_truth_table] +
                                            [['x'] * len(device.address_signals)] +
                                            [[0] * len(device.data_signals)] +
                                            [[1 - _y for _y in device.output_signals_truth_table]]))
        return strobe_signals_add + truth_table

    def _latex_final_state_machine(self, current_signals_name, current_value):
        current_value = str(current_value)
        if current_signals_name == 'data_signals':
            if current_value == '0':
                return 'x'
            else:
                return '1/0'
        if current_signals_name == 'output_signals':
            if current_value == '1':
                return '1/0'
        return '%s' % current_value