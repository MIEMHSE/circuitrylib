#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'
__email__ = 'S.Sobko@profitware.ru'
__copyright__ = 'Copyright 2013, The Profitware Group'


class CircuitException(Exception):
    pass


class SignalsNotSpecified(CircuitException):
    def __init__(self, signals):
        self.signals = signals

    def __str__(self):
        return repr(self.signals)


class SignalsSubsNotSpecified(CircuitException):
    def __init__(self, signals):
        self.signals = signals

    def __str__(self):
        return repr(self.signals)


class LogicFunctionNotSpecified(CircuitException):
    def __init__(self, logic_class):
        self.logic_class = logic_class

    def __str__(self):
        return repr(self.logic_class)
