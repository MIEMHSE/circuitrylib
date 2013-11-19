__author__ = 'Sergey Sobko'
__email__ = 'quote2-developers@rbc.ru'


class CircuitException(Exception):
    pass


class SignalsNotSpecified(CircuitException):
    def __init__(self, signals):
        self.signals = signals

    def __str__(self):
        return repr(self.signals)


class LogicFunctionNotSpecified(CircuitException):
    def __init__(self, logic_class):
        self.logic_class = logic_class

    def __str__(self):
        return repr(self.logic_class)