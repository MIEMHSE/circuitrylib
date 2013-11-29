#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'
__email__ = 'S.Sobko@profitware.ru'
__copyright__ = 'Copyright 2013, The Profitware Group'

from PIL import Image, ImageDraw, ImageFont


class DefaultElectronicSymbol(object):
    _image = None
    _font = None
    _surface = None
    _device = None

    _options = {
        'background': 'white',
        'foreground': 'black',
        'fontname': 'sans-serif.ttf',
        'pins_interval_height': 15,
        'width': 200,
        'indent_x': 40,
        'indent_y': 10
    }

    @property
    def image(self):
        return self._image

    def __init__(self, **kwargs):
        # Here we may set width, height, device and other options
        self._options.update(kwargs)
        # Load device
        self._device = self._options['device']
        self._get_device_name()
        # Count pins, width and height if not specified, indents for DIP-like image
        self._get_pins_positions()
        # PIL manipulations
        self._image = Image.new('RGB', (self._options['width'], self._options['height']),
                                self._options['background'])
        self._load_font()
        self._surface = ImageDraw.Draw(self._image)
        # Draw package and pins
        self._draw_package()
        self._draw_pins()

    def _get_device_name(self):
        try:
            device_name = self._device.device_name
        except AttributeError:
            device_name = self._device.__class__.__name__[6:].upper()
        self._options['device_name'] = device_name

    def _get_pins_positions(self):
        self._options['input_signals'] = [self._device[_signals] for _signals in self._device.mandatory_signals
                                          if _signals != 'output_signals']
        self._options['output_signals'] = [self._device[_signals] for _signals in self._device.mandatory_signals
                                           if _signals == 'output_signals']
        _pins_count = max(sum(map(len, self._options['input_signals'])),
                          sum(map(len, self._options['output_signals'])))
        if not 'height' in self._options:
            self._options['height'] = \
                self._options['indent_y'] * 2 + self._options['pins_interval_height'] * _pins_count
        self._set_indents()
        self._options['pins_interval_height'] = \
            float(self._options['bottom_y'] - self._options['top_y']) / _pins_count
        self._options['pins_positions'] = \
            [self._options['top_y'] + (_i + 0.5) * self._options['pins_interval_height']
             for _i in xrange(0, _pins_count)]

    def _load_font(self):
        _font_loaded = False
        try:
            self._font = ImageFont.truetype(self._options['fontname'], 16)
            _font_loaded = True
        except ImportError:
            pass
        except IOError:
            pass
        if not _font_loaded:
            self._font = ImageFont.load_default()

    def _set_indents(self):
        self._options.update({'top_y': self._options['indent_y'],
                              'bottom_y': self._options['height'] - self._options['indent_y'],
                              'left_x': self._options['indent_x'],
                              'right_x': self._options['width'] - self._options['indent_x']})

    def _draw_package(self):
        _left_x, _top_y, _right_x, _bottom_y, _draw_color = \
            map(self._options.get, ['left_x', 'top_y', 'right_x', 'bottom_y', 'foreground'])
        self._surface.rectangle((_left_x, _top_y, _right_x, _bottom_y), None, _draw_color)
        _input_signals_verical_line_x = _left_x + int((_right_x - _left_x) / 3)
        _output_signals_verical_line_x = _right_x - int((_right_x - _left_x) / 3)

        self._options.update({
            'input_signals_vertical_line_x': _input_signals_verical_line_x,
            'output_signals_vertical_line_x': _output_signals_verical_line_x
        })

        self._surface.line((_input_signals_verical_line_x, _top_y,
                            _input_signals_verical_line_x, _bottom_y), _draw_color, 1)
        self._surface.line((_output_signals_verical_line_x, _top_y,
                            _output_signals_verical_line_x, _bottom_y), _draw_color, 1)
        self._draw_text(self._options['device_name'], 0,
                        _input_signals_verical_line_x, _output_signals_verical_line_x)

    def _draw_pins(self):
        _position_index = 0
        for _signals_slot in range(0, len(self._options['input_signals'])):
            for _signal in self._options['input_signals'][_signals_slot]:
                self._draw_text(str(_signal), _position_index,
                                self._options['left_x'],
                                self._options['input_signals_vertical_line_x'])
                self._draw_one_pin(_position_index, 0, self._options['left_x'])
                _position_index += 1
            _partition_y = self._options['pins_positions'][_position_index - 1] + \
                           self._options['pins_interval_height'] / 2
            self._surface.line((self._options['left_x'], _partition_y,
                                self._options['input_signals_vertical_line_x'], _partition_y),
                               self._options['foreground'], 1)
        _position_index = 0
        for _signals_slot in range(0, len(self._options['output_signals'])):
            for _signal in self._options['output_signals'][_signals_slot]:
                self._draw_text(str(_signal), _position_index,
                                self._options['output_signals_vertical_line_x'],
                                self._options['right_x'])
                self._draw_one_pin(_position_index, self._options['right_x'], self._options['width'])
                _position_index += 1
            pass

    def _draw_text(self, text, position_index, left_x, right_x):
        _text_dimension = self._font.getsize(text)
        _position_y = self._options['pins_positions'][position_index]
        _text_position = (right_x - (right_x - left_x) / 2 - _text_dimension[0] / 2,
                          _position_y - _text_dimension[1] / 2)
        self._surface.text(_text_position, text, self._options['foreground'], self._font)

    def _draw_one_pin(self, position_index, left_x, right_x):
        _position_y = self._options['pins_positions'][position_index]
        self._surface.line((left_x, _position_y, right_x, _position_y),
                           self._options['foreground'], 1)