#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'
__email__ = 'S.Sobko@profitware.ru'
__copyright__ = 'Copyright 2013, The Profitware Group'

from PIL import Image, ImageDraw, ImageFont

REPRESENTATION_RECTANGLE_INDENT_X = 40
REPRESENTATION_RECTANGLE_INDENT_Y = 10


def create_device_graphical_representation(device, width, height):
    # TODO: Output signals and full refactoring
    img = Image.new('RGB', (width, height), "white")

    draw_color = "black"
    try:
        draw_font = ImageFont.truetype("sans-serif.ttf", 16)
    except ImportError:
        draw_font = ImageFont.load_default()

    top_y = REPRESENTATION_RECTANGLE_INDENT_Y
    bottom_y = height - REPRESENTATION_RECTANGLE_INDENT_Y
    left_x = REPRESENTATION_RECTANGLE_INDENT_X
    right_x = width - REPRESENTATION_RECTANGLE_INDENT_X

    surface = ImageDraw.Draw(img)
    surface.rectangle((left_x, top_y, right_x, bottom_y), None, draw_color)

    input_signals_verical_line_x = left_x + int((right_x - left_x) / 3)
    output_signals_verical_line_x = right_x - int((right_x - left_x) / 3)

    surface.line((input_signals_verical_line_x, top_y, input_signals_verical_line_x, bottom_y), draw_color, 1)
    surface.line((output_signals_verical_line_x, top_y, output_signals_verical_line_x, bottom_y), draw_color, 1)

    input_signals = [device[_signals] for _signals in device.mandatory_signals if _signals != 'output_signals']
    input_signals_lens = map(len, input_signals)
    input_signal_height = float(bottom_y - top_y) / sum(input_signals_lens)

    input_signals_drawn_count = 0
    _current_y = top_y
    for i in range(0, len(input_signals)):
        for signal in input_signals[i]:
            _current_y = top_y + input_signals_drawn_count * input_signal_height
            _pin_y = _current_y + int(input_signal_height / 2)
            surface.line((0, _pin_y, left_x, _pin_y), draw_color, 1)
            signals_text = str(signal).upper()
            signals_text_dimension = draw_font.getsize(signals_text)
            signals_text_position = (input_signals_verical_line_x -
                                     (input_signals_verical_line_x - left_x) / 2 - signals_text_dimension[0] / 2,
                                     _pin_y - signals_text_dimension[1] / 2)
            surface.text(signals_text_position, signals_text, draw_color, draw_font)
            if input_signals_drawn_count == 0:
                try:
                    device_name = device.device_name
                except AttributeError:
                    device_name = device.__class__.__name__[6:].upper()
                device_name_text_dimension = draw_font.getsize(device_name)
                device_name_text_position = (output_signals_verical_line_x - (output_signals_verical_line_x -
                                                                              input_signals_verical_line_x) / 2 -
                                             device_name_text_dimension[0] / 2,
                                             _pin_y - device_name_text_dimension[1] / 2)
                surface.text(device_name_text_position, device_name, draw_color, draw_font)
            input_signals_drawn_count += 1
        if i < len(input_signals) - 1:
            _separator_y = _current_y + input_signal_height
            surface.line((left_x, _separator_y, input_signals_verical_line_x, _separator_y), draw_color, 1)

    return img