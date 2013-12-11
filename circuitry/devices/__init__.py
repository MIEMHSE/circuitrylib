#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'
__email__ = 'S.Sobko@profitware.ru'
__copyright__ = 'Copyright 2013, The Profitware Group'

from sympy import symbols
from sympy.logic.boolalg import SOPform

from circuitry.exceptions import SignalsNotSpecified, SignalsSubsNotSpecified, SignalsMismatch, SignalsSubsMismatch


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

    def feed(self, **kwargs):
        signals = dict()
        # Iterate over kwargs finding signals
        for key, value in kwargs.iteritems():
            if key.endswith('_signals'):
                try:
                    assert key in self
                    if isinstance(value, list) or isinstance(value, tuple):
                        signals.update({key: tuple([_value for _value in value])})
                        assert len(signals[key]) == len(self[key])
                    else:
                        signals.update({key: value})
                except AssertionError:
                    if key in self:
                        key = self[key]
                    raise SignalsMismatch(key)
                except TypeError:
                    raise SignalsMismatch(self[key])
        # Check if all signal values except output_signals specified
        specified_set = set(signals)
        if self.mandatory_signals is not None:
            mandatory_set = set(self.mandatory_signals)
        else:
            mandatory_set = set()
        output_set = {'output_signals'}
        if specified_set & mandatory_set != mandatory_set ^ output_set:
            expected_set = mandatory_set ^ specified_set
            raise SignalsNotSpecified(tuple(expected_set))
        #
        # Get value of every signal slot
        #
        # There are three variants of signal handling:
        #
        # 1. signals[signal]=generator - DONE (generator returns tuple on every single step)
        # 2. signals[signal]=(1, 1, 1) - DONE
        # 3. signals[signal]=(1, 1, generator) - should generator return a tuple or one value on every single step?
        #
        for signal in signals:
            try:
                assert len(signals[signal]) == len(self[signal])
            except AssertionError:
                raise SignalsMismatch(self[signal])
            except TypeError:  # Generator function has no __len__
                pass

        for signal_output in self._signals_handler(signals):
            yield signal_output

    def _signals_handler(self, signals_values):
        raise StopIteration

    def _signals_handler_subs(self, signals_values):
        signals_subs = dict()
        for signals in signals_values:
            try:
                # signals[signal]=generator
                signals_subs.update(dict(zip(self[signals], next(signals_values[signals]))))
            except TypeError:
                # signals[signal]=(1, 1, 1)
                signals_subs.update(dict(zip(self[signals], signals_values[signals])))
        # signals[signal]=(1, 1, generator)
        # FIXME: For now we use single value generator. Should this remain?
        for k, v in signals_subs.iteritems():
            try:
                signals_subs.update({k: next(v)})
            except TypeError:
                pass
        return signals_subs

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