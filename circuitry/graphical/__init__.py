#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'
__email__ = 'S.Sobko@profitware.ru'
__copyright__ = 'Copyright 2013, The Profitware Group'

from PIL import ImageFont


def load_font(font_name):
    _font = None
    _font_loaded = False
    try:
        _font = ImageFont.truetype(font_name, 16)
        _font_loaded = True
    except (ImportError, IOError):
        pass
    if not _font_loaded:
        _font = ImageFont.load_default()
    return _font
