#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'
__email__ = 'S.Sobko@profitware.ru'
__copyright__ = 'Copyright 2013, The Profitware Group'

from PIL import Image, ImageDraw
from networkx import DiGraph

from circuitry.devices.simple import DeviceAnd, DeviceOr, DeviceNot
from circuitry.graphical import load_font
from circuitry.graphical.symbol import DefaultElectronicSymbol
from circuitry.graphical.wires import Wire, WiresPool


class DefaultSchematics(object):
    _image = None
    _font = None
    _surface = None
    _device = None

    _options = None
    _inputs = None
    _inputs_not = None

    _graph = None

    @property
    def image(self):
        self._draw_device()
        self._draw_inputs()
        return self._image

    @property
    def graph(self):
        # Populate graph
        self._walk_through_device_function(self._device.function)
        return self._graph

    def __init__(self, **kwargs):
        self._options = {
            'background': 'white',
            'foreground': 'black',
            'fontname': 'sans-serif.ttf',
            'pins_interval_height': 15,
            'width': 800,
            'height': 600,
            'indent_x': 40,
            'indent_y': 10
        }
        self._inputs = set()
        self._inputs_not = set()
        # Here we may set width, height, device and other options
        self._options.update(kwargs)
        # Create directed graph
        self._graph = DiGraph()
        # Load device
        self._device = self._options['device']
        # PIL manipulations
        self._image = Image.new('RGB', (self._options['width'], self._options['height']),
                                self._options['background'])
        self._font = load_font(self._options['fontname'])
        self._surface = ImageDraw.Draw(self._image)

    def _draw_simple_device(self, device_function_list, position_index, device_offset):
        _device_distance_height = self._options['height'] / (len(device_function_list) + 1) + device_offset
        _device_height = _device_distance_height
        for device_function in device_function_list:
            DeviceClass = None
            if str(device_function.func).lower() == 'and':
                DeviceClass = DeviceAnd
            if str(device_function.func).lower() == 'or':
                DeviceClass = DeviceOr
            if str(device_function.func).lower() == 'not' and len(device_function.args) == 1 and \
                    device_function.args[0].is_Atom:
                self._inputs_not |= {device_function}
            if DeviceClass is not None:
                _device = DeviceClass(data_signals='d:%s' % len(device_function.args),
                                      output_signals='y:1', output_signals_subs=dict(y0=1))
                _device_symbol = DefaultElectronicSymbol(device=_device)
                self._image.paste(_device_symbol.image,
                                  (self._options['width'] - _device_symbol._options['width'] * position_index,
                                   _device_height - _device_symbol._options['height'] / 2))
            _device_height += _device_distance_height
        pass

    def _walk_through_device_function(self, device_function, is_start=True):
        type = 'common'
        if is_start:
            type = 'output'
        DeviceClass = None
        if str(device_function.func).lower() == 'and':
            DeviceClass = DeviceAnd
        if str(device_function.func).lower() == 'or':
            DeviceClass = DeviceOr
        if str(device_function.func).lower() == 'not':
            DeviceClass = DeviceNot
            if device_function.args[0].is_Atom:
                type = 'input'
        if not str(device_function) in self._graph.nodes():
            if DeviceClass is not None:
                _device = DeviceClass(data_signals='d:%s' % len(device_function.args),
                                      output_signals='y:1', output_signals_subs=dict(y0=1))
                self._graph.add_node(str(device_function), device=_device, type=type)
                for subfunction in device_function.args:
                    self._walk_through_device_function(subfunction, is_start=False)
                    self._graph.add_edge(str(subfunction), str(device_function))
            else:
                self._graph.add_node(str(device_function), type='input')

    def _draw_device(self):
        pass

    def _draw_inputs(self):
        pass


class MultiplexerSchematics(DefaultSchematics):
    def _draw_device(self, function_list=None, position=1, _device_offset=None):
        if function_list is None:
            _args_list = [self._device.function]
        else:
            _args_list = function_list
        _device_offset = len(_args_list) * self._options['pins_interval_height']
        self._inputs |= set(filter(lambda x: x.is_Atom, _args_list))
        self._draw_simple_device(_args_list, position, _device_offset)
        _next_function_list = reduce(list.__add__, [list(_arg.args) for _arg in _args_list])
        if reduce(lambda x, y: x and y.is_Atom, _next_function_list):
            return
        self._draw_device(_next_function_list, position + 2, _device_offset)

    def _draw_inputs(self):
        # FIXME: Draw wires and connect devices to input bus
        wires_pool = WiresPool()
        for _signals_tuple in self._device.input_signals:
            for _signal in _signals_tuple:
                if _signal in self._inputs:
                    wires_pool += [Wire(signal=_signal)]
        inputs_not_list = list(self._inputs_not)
        for _signal in sorted(inputs_not_list, key=lambda rec: wires_pool.index(rec.args[0])):
            wires_pool += [Wire(signal=_signal)]
        _input_height = self._options['pins_interval_height']
        for i in range(0, len(wires_pool)):
            _current_y = (i + 1) * _input_height
            if wires_pool[i].signal.is_Atom:
                _offset_x = 30
            else:
                _offset_x = 60
                self._surface.line((_offset_x + i * 15, _current_y, _offset_x + i * 15,
                                    (wires_pool.index(wires_pool[i].signal.args[0]) + 1) * _input_height),
                                   self._options['foreground'], 1)
            self._surface.line((_offset_x, _current_y, self._options['width'], _current_y),
                               self._options['foreground'], 1)
            text = str(wires_pool[i].signal)
            _text_dimension = self._font.getsize(text)
            _text_position = (_offset_x / 2 - _text_dimension[0] / 2,
                              _current_y - _text_dimension[1] / 2)
            self._surface.text(_text_position, text, self._options['foreground'], self._font)
        #from pprint import pprint
        #pprint(wires_pool)
        #_input_height = 15
        #_inputs = [_input for _input in self._device if _input.endswith('_signals') and _input != 'output_signals']
        #print self._device.input_signals
        #print _inputs
        #for _position_input in range(1, len(self._inputs)):
        #    _current_y = _position_input * _input_height
        #    self._surface.line((30, _current_y, self._options['width'], _current_y), self._options['foreground'], 1)
