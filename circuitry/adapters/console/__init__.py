#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'
__email__ = 'S.Sobko@profitware.ru'
__copyright__ = 'Copyright 2014, The Profitware Group'

from circuitry.adapters import AbstractAdapter


class ConsoleTruthTableAdapter(AbstractAdapter):
    public_properties = ('console_table',)
    default_method = lambda self: self.console_table

    @property
    def _truth_table(self):
        return self._device.truth_table

    def _get_string_line(self, bin_line):
        return ''.join(map(str, bin_line)[::-1]) + ' '

    @property
    def console_table(self):
        truth_table = self._truth_table
        output_list = list()
        for truth_table_line in truth_table:
            for bin_line in truth_table_line:
                output_list.append(self._get_string_line(bin_line))
            output_list.append('\n')
        return ''.join(output_list)


class TwosComplementConsoleTruthTableAdapter(ConsoleTruthTableAdapter):
    def default_method(self):
        min_len = len(self._device.output_signals)
        for signals_name in self._device.mandatory_signals:
            if signals_name not in ['output_signals', 'strobe_signals']:
                if len(self._device[signals_name]) < min_len:
                    min_len = len(self._device[signals_name])
        self._options['digits'] = min_len
        return self.console_table

    def _get_string_line(self, bin_line):
        start_pos = 0

        if 'digits' in self._options:
            max_num = 2 ** (self._options['digits'] - 1)
            start_pos = len(bin_line) - self._options['digits']
        else:
            max_num = 2 ** (len(bin_line) - 1)
        dec_max_len = len(str(max_num)) + 1
        bin_str = ''.join(map(str, bin_line)[::-1])
        dec_int, dec_int_two_complement = bin_str[0], bin_str[0]
        if len(bin_str) > 1:
            s_sign = (bin_str[start_pos] == '1') and '-' or ''
            dec_int = int(s_sign + '0b' + bin_str[start_pos:], base=2)
            if dec_int >= 0:
                dec_int_two_complement = dec_int
            else:
                dec_int_two_complement = -2 * max_num - dec_int
        return bin_str + (' (%s, %s)' % (dec_int, dec_int_two_complement)).ljust(dec_max_len * 2 + 7) + ' '