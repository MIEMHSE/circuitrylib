#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'
__email__ = 'S.Sobko@profitware.ru'
__copyright__ = 'Copyright 2014, The Profitware Group'

from circuitry.adapters import AbstractAdapter


class ConsoleTruthTableAdapter(AbstractAdapter):
    public_properties = ('console_table',)

    @property
    def _truth_table(self):
        return self._device.truth_table

    @property
    def console_table(self):
        truth_table = self._truth_table
        output_list = list()
        for truth_table_line in truth_table:
            for bin_line in truth_table_line:
                output_list.append(''.join(map(str, bin_line)[::-1]) + ' ')
            output_list.append('\n')
        return ''.join(output_list)