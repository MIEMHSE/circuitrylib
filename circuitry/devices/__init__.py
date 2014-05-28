#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'
__email__ = 'S.Sobko@profitware.ru'
__copyright__ = 'Copyright 2013, The Profitware Group'

from sympy import symbols
from sympy.logic.boolalg import SOPform

from circuitry.exceptions import SignalsNotSpecified, SignalsSubsNotSpecified, SignalsSubsMismatch


def generate_binary_lines_current(n_bin, i):
    for n in xrange(n_bin, 0, -1):
        if i - 2 ** (n - 1) < 0:
            yield 0
        else:
            i -= 2 ** (n - 1)
            yield 1


class Device(dict):
    mandatory_signals = None
    mandatory_signals_using_subs = None

    def __init__(self, **kwargs):
        signals = dict()
        signals_subs = dict()
        # Iterate over kwargs finding signals and substitutions
        for key, value in kwargs.iteritems():
            if key.endswith('_signals') and isinstance(value, basestring):
                signals.update({key: symbols(value)})
            if key.endswith('_signals_subs') and isinstance(value, dict):
                signals_subs.update({key: value})
        # Find mandatory signals
        if self.mandatory_signals is not None:
            specified_set = set(signals)
            mandatory_set = set(self.mandatory_signals)
            if specified_set & mandatory_set != mandatory_set:
                excepted_set = mandatory_set ^ specified_set
                raise SignalsNotSpecified(tuple(excepted_set))
        # Find mandatory substitutions
        specified_set = set(signals_subs)
        if self.mandatory_signals_using_subs is not None:
            mandatory_set = set(map(lambda _s: '%s_subs' % _s, self.mandatory_signals_using_subs))
            if specified_set & mandatory_set != mandatory_set:
                excepted_set = mandatory_set ^ specified_set
                raise SignalsSubsNotSpecified(tuple(excepted_set))
        # Create truth tables and functions by substitutions
        for _subs_name in signals:
            if '%s_subs' % _subs_name in specified_set:
                try:
                    kwargs.update({'%s_truth_table' % _subs_name:
                                   [signals_subs['%s_subs' % _subs_name][str(_name)] for _name in signals[_subs_name]]})
                    kwargs.update({'%s_function' % _subs_name:
                                   SOPform(signals[_subs_name], [kwargs['%s_truth_table' % _subs_name]])})
                except KeyError:
                    raise SignalsSubsMismatch(tuple(signals[_subs_name]))
        kwargs.update(signals)
        super(Device, self).__init__(**kwargs)

    # TODO: MyHDL integration

    @property
    def input_signals(self):
        signals_list = list()
        for i in self.mandatory_signals:
            if i != 'output_signals':
                signals_list += [self[i]]
        return signals_list

    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            return self.__getattribute__(item)

    def _generate_through_truth_table(self, signals_list=None):
        self.truth_table = list()
        if not signals_list:
            return
        strobe_signals = False
        if 'strobe_signals' in self.mandatory_signals:
            strobe_signals = True
        input_signals_len = sum([len(signals) for signals in signals_list])
        for bin_i in range(0, 2 ** input_signals_len):
            lines = [list() for _ in range(0, len(signals_list))]
            lines_index, value_index = 0, 0
            for line_value in generate_binary_lines_current(input_signals_len, bin_i):
                lines[lines_index].append(line_value)
                value_index += 1
                if value_index >= len(signals_list[lines_index]):
                    value_index = 0
                    lines_index += 1
            for line in lines:
                line.reverse()
            line_subs = dict()
            for signals_i in range(0, len(signals_list)):
                for i in range(0, len(signals_list[signals_i])):
                    line_subs[str(signals_list[signals_i][i])] = lines[signals_i][i]
            strobe_signals_truth_table = list()
            if strobe_signals:
                line_subs.update(self.strobe_signals_subs)
                strobe_signals_truth_table = [self.strobe_signals_truth_table]
            y_line = list()
            max_length = min(len(self.output_signals), len(self.functions))
            for i in range(0, max_length):
                y_line.append(1 if self.functions[i].subs(line_subs) else 0)
            self.truth_table.append(tuple(strobe_signals_truth_table + lines +
                                          [y_line[:max_length]]))