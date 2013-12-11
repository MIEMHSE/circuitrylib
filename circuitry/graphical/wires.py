#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'
__email__ = 'S.Sobko@profitware.ru'
__copyright__ = 'Copyright 2013, The Profitware Group'

from sympy.core.symbol import Symbol


class Wire(object):

    _options = None

    def __init__(self, **kwargs):
        self._options = {
            'pins_interval_height': 15,
        }

        self._options.update(kwargs)

    @property
    def signal(self):
        return self._options['signal']

    def __repr__(self):
        return repr(self._options)


class WiresPool(list):
    def index(self, value, start=None, stop=None):
        if isinstance(value, Symbol):
            _index = -1
            for _wire in self:
                _index += 1
                if value == _wire.signal:
                    return _index
            return list().index(value)
        else:
            return super(WiresPool, self).index(value, start, stop)